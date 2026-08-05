"""What leaves this deployment, and on what terms.

Two different kinds of leaving, kept apart because conflating them is how
somebody agrees to the wrong one:

* a **contribution** sends one anonymised exchange to the shared model — no
  ids, the persona name replaced, and a random ref so the item can be deleted
  at the gateway later without identifying anybody;
* a **licence** sends the profile itself: the right to consult it, or where
  the offer allows, to derive a whole new agent seeded from its persona and
  owned by the buyer.

## The preview is a dry run, and the screen has to say so

`preview_next` is computed whether or not the profile is opted in. That is
useful — it answers *what would this cost me* before you commit — but a
console that renders it under one heading either way tells an opted-out owner
their next conversation is on its way out. Recorded here as observed
behaviour, with the console's conditional heading pinned beside it.

## The bar moved from delivery to the till

A licence permitting derivatives used to sell to anybody. A fourteen-year-old
could buy one: 201, `can_derive: true`, and the fee credited to the seller at
sale time — then a 403 on the only thing the licence exists for. Somebody had
been paid for a thing the server would not hand over. The adult check now runs
at acquire, where the money moves.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _owner(client, account="acct_leave", contribute=True):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Dana",
        "purpose": "enterprise_agent", "persona": "precise",
        "cloud_contribution": contribute,
        "verification": {"birthdate": "1990-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    return p, head


def _person(client, name="Ana", birthdate="1990-05-05"):
    row = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate}).json()
    return row["id"], {"authorization": f"Bearer {row['token']}"}


# --- the shared model -------------------------------------------------------

def test_the_status_says_whether_anything_could_leave_at_all(client):
    """With no gateway configured nothing can be contributed however a
    profile is set, and the screen leads with that rather than showing an
    opt-in switch that does nothing."""
    s = client.get("/cloud/status").json()
    assert isinstance(s["cloud"], bool)
    assert s["fallback"] and s["contribution"]


def test_the_contribution_view_is_the_owners_alone(client):
    p, head = _owner(client, "acct_cv")
    uid, uhead = _person(client)
    assert client.get(f"/profiles/{p['id']}/cloud-contribution",
                      headers=uhead).status_code == 403
    assert client.get(f"/profiles/{p['id']}/cloud-contribution",
                      headers=head).status_code == 200


def test_the_preview_carries_no_names(client):
    """The whole claim of the feature, checked against the actual bytes
    rather than against the policy sentence next to them."""
    p, head = _owner(client, "acct_names")
    uid, uhead = _person(client)
    client.post(f"/profiles/{p['id']}/chat", headers=uhead,
                json={"interactor_id": uid, "message": "tell me about Dana"})
    view = client.get(f"/profiles/{p['id']}/cloud-contribution",
                      headers=head).json()
    blob = str(view["preview_next"])
    assert p["id"] not in blob and uid not in blob
    assert "Dana" not in blob, "the persona name survived into the preview"
    assert "PERSONA" in blob


def test_nothing_is_sent_to_produce_the_preview(client):
    """It is a dry run. Reading it twice must not put anything in the log."""
    p, head = _owner(client, "acct_dry")
    uid, uhead = _person(client)
    client.post(f"/profiles/{p['id']}/chat", headers=uhead,
                json={"interactor_id": uid, "message": "hello"})
    for _ in range(2):
        view = client.get(f"/profiles/{p['id']}/cloud-contribution",
                          headers=head).json()
    assert view["contributed"] == []


def test_the_preview_survives_opting_out(client):
    """Observed and recorded rather than changed. It answers *what would
    this cost me* before you commit, which is worth keeping — but it means
    an opted-out profile still shows an exchange, and a screen that did not
    say which is which would be raising a false alarm."""
    p, head = _owner(client, "acct_optout")
    uid, uhead = _person(client)
    client.post(f"/profiles/{p['id']}/chat", headers=uhead,
                json={"interactor_id": uid, "message": "hello"})
    client.post(f"/profiles/{p['id']}/cloud-contribution/revoke", headers=head)
    view = client.get(f"/profiles/{p['id']}/cloud-contribution",
                      headers=head).json()
    assert view["opted_in"] is False
    assert view["preview_next"] is not None


def test_the_screen_labels_the_preview_by_whether_it_is_opted_in():
    """Two headings over the same content, chosen by `opted_in`. Without
    this the console tells somebody who opted out that their next
    conversation is leaving."""
    src = _markup("app/src/screens/Leaving.tsx")
    assert "view.opted_in" in src
    # The heading moved into the l10n table, so the screen is asked for the
    # two lookups and the table is asked for the English. Matching the
    # sentence in the screen would now succeed off the key name alone —
    # `lvg.wouldleave.off` contains none of the words that matter.
    assert 'tr("lvg.wouldleave.on", lang)' in src
    assert 'tr("lvg.wouldleave.off", lang)' in src
    l10n = _markup("app/src/l10n.ts")
    assert "would leave if you turned this back on" in l10n
    assert "would leave on the next thumbs-up" in l10n


# --- taking it back ---------------------------------------------------------

def test_revoking_reports_the_two_things_it_did(client):
    p, head = _owner(client, "acct_revoke")
    r = client.post(f"/profiles/{p['id']}/cloud-contribution/revoke",
                    headers=head).json()
    assert r["opted_in"] is False
    assert "revoked" in r and "deleted_at_gateway" in r


def test_deleted_at_gateway_is_true_vacuously_when_nothing_ever_left(client):
    """A tick shown for this and for a gateway confirmation would be the
    wrong reassurance, so the console reads the count alongside it."""
    p, head = _owner(client, "acct_vacuous")
    r = client.post(f"/profiles/{p['id']}/cloud-contribution/revoke",
                    headers=head).json()
    assert r["revoked"] == 0
    assert r["deleted_at_gateway"] is True


def test_the_screen_tells_those_two_cases_apart():
    src = _markup("app/src/screens/Leaving.tsx")
    assert "revoked.revoked === 0" in src, (
        "one message covers both 'nothing ever left' and 'the gateway "
        "confirmed', which are different facts")


# --- licences ---------------------------------------------------------------

def _offer(client, p, head, **over):
    body = {"kind": "consult", "price": 250, "currency": "USD",
            "terms": "one engagement", "allow_derivatives": False}
    body.update(over)
    return client.put(f"/profiles/{p['id']}/license", headers=head, json=body)


def test_a_minor_cannot_buy_a_licence_they_could_not_use(client):
    """The defect this round found. It sold: 201, `can_derive: true`, and
    the fee credited to the seller — then a 403 on the only thing the
    licence is for."""
    p, head = _owner(client, "acct_till")
    _offer(client, p, head, kind="clone", allow_derivatives=True)
    _, minor = _person(client, "Teen", "2012-05-05")
    r = client.post(f"/profiles/{p['id']}/license/acquire", headers=minor)
    assert r.status_code == 403
    assert "verified-18+" in r.json()["detail"]


def test_a_consult_licence_still_sells_to_anybody(client):
    """The bar is on deriving, not on licensing. A consult licence buys time
    with a profile and creates no new owner, so tightening it would be a
    different decision than the one this fixes."""
    p, head = _owner(client, "acct_consult")
    _offer(client, p, head)
    _, minor = _person(client, "Teen", "2012-05-05")
    assert client.post(f"/profiles/{p['id']}/license/acquire",
                       headers=minor).status_code == 201


def test_deriving_from_a_consult_licence_is_refused_by_name(client):
    p, head = _owner(client, "acct_consultderive")
    _offer(client, p, head)
    _, buyer = _person(client, "Buyer")
    g = client.post(f"/profiles/{p['id']}/license/acquire",
                    headers=buyer).json()
    assert g["can_derive"] is False
    r = client.post(f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
                    headers=buyer)
    assert r.status_code == 403
    assert "consult only" in r.json()["detail"]


def test_the_screen_does_not_offer_a_button_that_would_be_refused():
    """`can_derive` comes back on the grant, so the console knows before it
    draws anything."""
    assert "grant.can_derive ?" in _markup("app/src/screens/Leaving.tsx")


def test_a_derived_agent_records_where_it_came_from(client):
    p, head = _owner(client, "acct_derive")
    _offer(client, p, head, kind="clone", allow_derivatives=True)
    _, buyer = _person(client, "Buyer")
    g = client.post(f"/profiles/{p['id']}/license/acquire",
                    headers=buyer).json()
    made = client.post(f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
                       headers=buyer).json()
    assert made["licensed_from"] == p["id"]
    assert made["derived_profile_id"] != p["id"]
    assert made["owner_token"], "the buyer has no way to own what they bought"


def test_one_agent_per_licence(client):
    """A licence was sold for one. The second attempt is a 409 rather than a
    second profile."""
    p, head = _owner(client, "acct_once")
    _offer(client, p, head, kind="clone", allow_derivatives=True)
    _, buyer = _person(client, "Buyer")
    g = client.post(f"/profiles/{p['id']}/license/acquire",
                    headers=buyer).json()
    path = f"/profiles/{p['id']}/license/{g['grant_id']}/derive"
    assert client.post(path, headers=buyer).status_code == 201
    assert client.post(path, headers=buyer).status_code == 409


def test_somebody_elses_licence_is_not_yours_to_derive_from(client):
    p, head = _owner(client, "acct_theirs2")
    _offer(client, p, head, kind="clone", allow_derivatives=True)
    _, buyer = _person(client, "Buyer")
    _, other = _person(client, "Other")
    g = client.post(f"/profiles/{p['id']}/license/acquire",
                    headers=buyer).json()
    r = client.post(f"/profiles/{p['id']}/license/{g['grant_id']}/derive",
                    headers=other)
    assert r.status_code == 403
    assert "another buyer" in r.json()["detail"]


def test_acquiring_a_licence_nobody_offered_is_a_404(client):
    p, head = _owner(client, "acct_nooffer")
    _, buyer = _person(client, "Buyer")
    assert client.post(f"/profiles/{p['id']}/license/acquire",
                       headers=buyer).status_code == 404


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _markup(rel: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", _src(rel), flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_exists():
    assert (REPO / "app/src/screens/Leaving.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.cloudStatus(", "api.contributionView(", "api.revokeContributions(",
    "api.acquireLicense(", "api.deriveAgent(",
])
def test_the_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Leaving.tsx")


def test_a_licence_is_bought_with_the_buyers_token():
    """Not the owner's. The console holds both, and picking the wrong one
    here is a 403 nobody can act on."""
    import sys

    sys.path.insert(0, str(REPO / "tests"))
    import clientpaths as cp

    src = _src("app/src/screens/Leaving.tsx")
    # Balanced, because `subject.trim()` closes a paren before the argument
    # list does and a naive slice stops there — reading only the callee and
    # concluding nothing about the token.
    start = src.index("api.acquireLicense(") + len("api.acquireLicense")
    call = cp._call_body(src, start)
    assert "buyerToken" in call
    assert "ownerToken" not in call
