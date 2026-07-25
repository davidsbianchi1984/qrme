"""The Cloud Model Gateway server.

The client side of this contract has been tested against fakes for a while;
what was missing was the thing the fakes stood in for. The tests that matter
here are the ones about *refusing*: an open gateway, an identity leak in a
contribution, and an intake that isn't configured. Serving inference is the
easy half.
"""

import pytest
from fastapi.testclient import TestClient

from cloudgw import screening
from cloudgw.api import create_app
from cloudgw.model import StubProvider
from cloudgw.store import NoVault, PDIVault


class FakeVault:
    configured = True

    def __init__(self):
        self.items = {}

    def describe(self):
        return {"configured": True, "kind": "fake"}

    def put(self, source, ref, payload):
        # Mirrors PDI's real ContributionIn: `payload` is an object.
        assert isinstance(payload, dict), "PDI takes an object, not a string"
        self.items[ref] = payload
        return True

    def delete(self, refs):
        return sum(bool(self.items.pop(r, None)) for r in refs)


@pytest.fixture()
def vault():
    return FakeVault()


@pytest.fixture()
def client(vault):
    return TestClient(create_app(provider=StubProvider(), vault=vault))


def _exchange(**over):
    body = {"ref": "ctb_a1b2c3d4", "source": "qrme", "kind": "rated_exchange",
            "quality": "positive", "purpose": "companion_coach",
            "exchange": [{"role": "user", "content": "how do I make a roux?"},
                         {"role": "assistant", "content": "equal parts fat and flour"}]}
    body.update(over)
    return body


# -- the contract ----------------------------------------------------------

def test_generate_returns_content_and_the_model_that_answered(client):
    r = client.post("/v1/generate", json={
        "system": "be helpful", "messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 200
    assert "hi" in r.json()["content"]
    assert r.json()["model"] == "stub"


def test_model_info_names_the_real_model(client):
    """Clients show users which model is answering, so a gateway serving a
    stub must not describe itself as a hosted tier."""
    body = client.get("/v1/model").json()
    assert body["model"] == "stub" and body["tier"] == "stub"


def test_empty_messages_are_refused(client):
    assert client.post("/v1/generate", json={"messages": []}).status_code == 422


def test_upstream_failure_is_a_503_the_client_can_fall_back_from(vault):
    """The client falls back locally on any failure, so this is a routine
    outcome — but it must be reported, not disguised as an empty answer."""
    class Broken(StubProvider):
        def generate(self, system, messages):
            raise RuntimeError("model timeout")

    c = TestClient(create_app(provider=Broken(), vault=vault))
    r = c.post("/v1/generate", json={"messages": [{"role": "user", "content": "x"}]})
    assert r.status_code == 503
    assert "model timeout" in r.json()["detail"]


def test_a_contribution_is_accepted_and_attributed(client, vault):
    r = client.post("/v1/contributions", json=_exchange())
    assert r.status_code == 202
    stored = vault.items["ctb_a1b2c3d4"]
    # Attribution is which *deployment* sent it, never who it came from.
    assert stored["contributed_by"] == "local-dev"
    assert stored["kind"] == "rated_exchange"


def test_revocation_deletes_by_ref_without_identifying_anyone(client, vault):
    client.post("/v1/contributions", json=_exchange())
    r = client.post("/v1/contributions/revoke", json={"refs": ["ctb_a1b2c3d4"]})
    assert r.json() == {"requested": 1, "deleted": 1}
    assert vault.items == {}


# -- the intake refuses rather than sanitizes ------------------------------

@pytest.mark.parametrize("payload,fragment", [
    (_exchange(profile_id="prf_deadbeef01"), "profile_id"),
    (_exchange(display_name="Ada Lovelace"), "display_name"),
    (_exchange(exchange=[{"role": "user", "content": "I'm at ada@example.com"}]),
     "email"),
    (_exchange(exchange=[{"role": "user", "content": "see prf_deadbeef01"}]),
     "product id"),
    (_exchange(source="somewhere-else"), "unknown source"),
    (_exchange(kind="raw_memory"), "unknown contribution kind"),
])
def test_identity_leaks_are_refused_not_stripped(client, vault, payload, fragment):
    """A gateway that quietly sanitized would hide the client bug that caused
    the leak. 422 tells the contributing deployment its build is leaking."""
    r = client.post("/v1/contributions", json=payload)
    assert r.status_code == 422
    assert fragment in r.json()["detail"]
    assert vault.items == {}


def test_nested_identity_is_caught_too(client):
    """A nested exchange is exactly where an id hides."""
    r = client.post("/v1/contributions", json=_exchange(
        exchange=[{"role": "user", "content": "hi", "interactor_id": "itr_1"}]))
    assert r.status_code == 422
    assert "interactor_id" in r.json()["detail"]


def test_a_contribution_without_a_ref_is_refused(client):
    """No ref means no way to revoke it later without deanonymizing the
    contributor — so it must not be stored at all."""
    body = _exchange()
    del body["ref"]
    r = client.post("/v1/contributions", json=body)
    assert r.status_code == 422 and "revoke" in r.json()["detail"]


def test_the_refs_own_id_shape_is_allowed(client, vault):
    """The contribution's own ref is random and carries no identity — the
    screen must not reject the very field that makes revocation possible."""
    assert client.post("/v1/contributions",
                       json=_exchange(ref="ctb_0011223344")).status_code == 202
    assert "ctb_0011223344" in vault.items


def test_jim_guidance_outcomes_pass(client):
    """The other product's real payload shape, so the screen doesn't only fit
    QRME's."""
    r = client.post("/v1/contributions", json={
        "ref": "ctb_99887766", "source": "jim-mini", "kind": "guidance_outcome",
        "condition": "anxiety", "severity": "moderate", "rating": "up"})
    assert r.status_code == 202


# -- refusing to store badly ------------------------------------------------

def test_without_a_vault_contributions_are_refused_and_inference_still_works():
    """Never storing beats storing unencrypted and unauditable — and the half
    that needs no vault keeps working."""
    c = TestClient(create_app(provider=StubProvider(), vault=NoVault()))
    r = c.post("/v1/contributions", json=_exchange())
    assert r.status_code == 503
    assert "unencrypted" in r.json()["detail"]
    assert c.post("/v1/generate",
                  json={"messages": [{"role": "user", "content": "x"}]}
                  ).status_code == 200


def test_health_admits_when_there_is_no_intake():
    c = TestClient(create_app(provider=StubProvider(), vault=NoVault()))
    assert c.get("/health").json()["intake"]["configured"] is False


# -- auth fails closed off-machine -----------------------------------------

def test_no_tokens_configured_is_localhost_only(client, monkeypatch):
    """Same posture as PDI's admin surface: open admin on a routable address
    is somebody else's model bill."""
    monkeypatch.delenv("CLOUDGW_TOKENS", raising=False)
    # TestClient presents the in-process sentinel host, so this is allowed...
    assert client.get("/v1/model").status_code == 200

    # ...and a real network peer is not.
    from cloudgw import api
    from fastapi import HTTPException

    class Peer:
        client = type("C", (), {"host": "203.0.113.9"})()

    with pytest.raises(HTTPException) as exc:
        api._caller(Peer(), authorization="")
    assert exc.value.status_code == 503


def test_a_configured_token_is_required_and_attributed(vault, monkeypatch):
    monkeypatch.setenv("CLOUDGW_TOKENS", "acme:tok-acme,globex:tok-globex")
    c = TestClient(create_app(provider=StubProvider(), vault=vault))

    assert c.get("/v1/model").status_code == 401
    assert c.get("/v1/model", headers={"authorization": "Bearer wrong"}
                 ).status_code == 403
    assert c.get("/v1/model", headers={"authorization": "Bearer tok-acme"}
                 ).status_code == 200

    c.post("/v1/contributions", json=_exchange(),
           headers={"authorization": "Bearer tok-globex"})
    assert vault.items["ctb_a1b2c3d4"]["contributed_by"] == "globex"


# -- the PDI wire ----------------------------------------------------------

def test_the_vault_speaks_pdis_real_contribution_contract(vault):
    """The gateway is an ordinary PDI tenant — no privileges the contract
    doesn't give everyone."""
    calls = []

    class FakePDI:
        def post(self, path, json=None, headers=None):
            calls.append(("POST", path, json, headers))
            return type("R", (), {"status_code": 201})()

        def delete(self, path, headers=None):
            calls.append(("DELETE", path, None, headers))
            return type("R", (), {"status_code": 200})()

    v = PDIVault("http://pdi:8100", "pdi_tok", client=FakePDI())
    v.put("qrme", "ctb_1", {"a": 1})
    assert calls[0][1] == "/contributions"
    assert calls[0][2]["ref"] == "ctb_1"
    assert calls[0][3]["authorization"] == "Bearer pdi_tok"

    assert v.delete(["ctb_1", "ctb_2"]) == 2
    assert calls[1][1] == "/contributions/ctb_1"


def test_a_vault_write_failure_is_not_reported_as_success(vault):
    """Answering 202 while the write failed would lose contributions
    silently, and the contributor would log them as delivered."""
    class Failing:
        def post(self, path, json=None, headers=None):
            return type("R", (), {"status_code": 500})()

    v = PDIVault("http://pdi:8100", "t", client=Failing())
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        v.put("qrme", "ctb_1", {})
    assert exc.value.status_code == 502


def test_the_launcher_runs_and_says_what_it_is_configured_for(capsys, monkeypatch):
    """Nothing else imports ``__main__``, so without this a syntax error in
    it ships green — which is exactly what happened while writing it.

    The banner matters on its own: an operator who thinks they are serving a
    hosted model from a stub, or collecting into a vault that isn't there,
    should find out at boot rather than from a quiet corpus much later.
    """
    import unittest.mock as mock

    from cloudgw import __main__ as launcher

    for var in ("ANTHROPIC_API_KEY", "CLOUDGW_PDI_URL", "CLOUDGW_TOKENS"):
        monkeypatch.delenv(var, raising=False)
    with mock.patch("uvicorn.run") as run:
        assert launcher.main([]) == 0
    assert run.call_args.args[0] == "cloudgw.api:app"

    out = capsys.readouterr().out
    assert "serving the stub, not a hosted model" in out
    assert "contributions will be refused" in out
    assert "closed to everyone else" in out


def test_screening_is_usable_on_its_own():
    """It is the piece an operator would want to run over an existing corpus,
    so it stands alone rather than only inside a route."""
    screening.screen(_exchange())
    with pytest.raises(screening.Rejected):
        screening.screen(_exchange(owner_id="own_1"))
