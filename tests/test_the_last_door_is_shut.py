"""A real dialer, an explicit press, and a door that will not open in beta.

A synthetic profile can hand a matter to somebody real. Some matters do not
wait for a butcher or a broker, and the honest end of that ladder is emergency
services — which is the most dangerous control this product could grow.

    asked     can the profile hand this to a professional
    mattered  what happens when it cannot, and nobody has time

So it is built as the smallest thing that can be true: the press is explicit,
the waiver is signed ahead in calm conditions, and the last hop **refuses**
while the deployment is sealed.

## What makes this different from a button wired to nothing

A mock that returns success is worse than no feature: it is a person believing
help is coming. The path here is real and is stopped at the point the call
would leave, and every answer says plainly that no call was placed and gives
the number to dial.

That is the rule the beacon-alarm round settled — *an alarm that says help was
called has to have called it* — kept by never making the claim.

## What the guards hold

* the seal is read at the moment of the call, so shutting it needs no restart;
* **no argument, plan, profile setting or request field opens it** — only the
  deployment's own environment variable, and a structural check refuses any
  parameter that could;
* the refusal never claims a call was placed, and always carries the number;
* `placed` is set by a call that connected and by nothing else;
* the press refuses without a signed waiver, and the waiver must be signed
  over *these* words rather than any valid signature the account holds.
"""

import inspect

import pytest

from qrme import escalation


def _unresolved(client, profile_id, interactor_id, head,
                matter="the chest pain is getting worse"):
    # The owner's half of it. Reaching emergency services is off until the
    # profile's owner puts it on the roster (qrme/privileges.py); the waiver
    # below is the *other* person's half, and neither stands in for the other.
    # It rides here so these tests stay about the door rather than the roster —
    # which has its own file, including the case where this is missing.
    client.post(f"/profiles/{profile_id}/privileges/reach_emergency_services",
                json={"on": True})
    r = client.post(f"/profiles/{profile_id}/unresolved",
                    json={"interactor_id": interactor_id, "matter": matter},
                    headers=head)
    assert r.status_code == 201, r.text
    return r.json()


def _arm(interactor_id):
    """Arm it without the signing ceremony, which has its own tests.

    Straight to the store: these tests are about the door, and routing every
    one of them through WebAuthn would be testing the signature stack twice
    and the seal once.
    """
    from qrme import db, signatures
    conn = db.connect()
    conn.execute(
        "INSERT OR REPLACE INTO dial_waivers (interactor_id, signature_id,"
        " waiver, waiver_sha256, signed_at) VALUES (?,?,?,?,?)",
        (interactor_id, "sig_test", escalation.WAIVER,
         signatures.sha256_hex(escalation.WAIVER), db.utcnow()))
    conn.commit()


# --------------------------------------------------------------------------
# Cannot resolve, and what is offered.
# --------------------------------------------------------------------------

def test_reaching_the_limit_is_written_down(client, profile_id,
                                            interactor_id, interactor_head):
    """Not a sentence in a chat turn: a record, so what was offered and what
    happened next are answerable by somebody who was not there."""
    row = _unresolved(client, profile_id, interactor_id, interactor_head)
    assert row["matter"] == "the chest pain is getting worse"
    assert row["placed"] is False
    assert row["dialed_at"] is None

    mine = client.get(f"/interactors/{interactor_id}/unresolved",
                      headers=interactor_head).json()
    assert [r["id"] for r in mine] == [row["id"]]


def test_an_escalation_with_no_subject_is_refused(client, profile_id,
                                                  interactor_id,
                                                  interactor_head):
    r = client.post(f"/profiles/{profile_id}/unresolved",
                    json={"interactor_id": interactor_id, "matter": "  "},
                    headers=interactor_head)
    assert r.status_code == 422, r.text


# --------------------------------------------------------------------------
# The waiver, signed ahead.
# --------------------------------------------------------------------------

def test_the_words_are_readable_before_anybody_signs(client, interactor_id,
                                                     interactor_head):
    """A person deciding whether to arm it should be able to read what arming
    means, and should learn *now* that this deployment is sealed rather than
    discovering it at the worst moment."""
    out = client.get(f"/interactors/{interactor_id}/dialer",
                     headers=interactor_head).json()
    assert out["armed"] is False
    assert "charged to me" in out["waiver"]
    assert out["sealed"] is True
    assert out["call_yourself"]


def test_the_press_refuses_without_a_signed_waiver(client, profile_id,
                                                   interactor_id,
                                                   interactor_head):
    row = _unresolved(client, profile_id, interactor_id, interactor_head)
    r = client.post(f"/escalations/{row['id']}/dial",
                    params={"interactor_id": interactor_id},
                    headers=interactor_head)
    assert r.status_code == 403, r.text
    assert "waiver" in r.text


def test_a_signature_over_other_words_does_not_arm_it():
    """Any valid assertion the account holds would otherwise do — the binding
    argument `referral.release` makes, for a louder reason."""
    src = inspect.getsource(escalation.arm)
    assert "document_sha256" in src
    assert "WAIVER" in src


# --------------------------------------------------------------------------
# The press, and the door at the end of it.
# --------------------------------------------------------------------------

def test_the_press_is_refused_at_the_last_hop_and_says_so(
        client, profile_id, interactor_id, interactor_head):
    """The whole point. Armed, pressed, and stopped — with no claim that help
    is coming and with the number to dial beside it."""
    _arm(interactor_id)
    row = _unresolved(client, profile_id, interactor_id, interactor_head)
    r = client.post(f"/escalations/{row['id']}/dial",
                    params={"interactor_id": interactor_id},
                    headers=interactor_head)
    assert r.status_code == 503, r.text
    body = r.text.lower()
    assert "no call was placed" in body
    assert "yourself" in body

    # And the record agrees with the sentence.
    after = client.get(f"/interactors/{interactor_id}/unresolved",
                       headers=interactor_head).json()[0]
    assert after["placed"] is False
    assert after["dialed_at"], "the attempt itself is recorded"


def test_the_refusal_never_claims_help_is_coming():
    """The beacon-alarm round settled it: an alarm that says help was called
    has to have called it. This one keeps that by never making the claim."""
    with pytest.raises(escalation.Sealed) as caught:
        escalation._place("999")
    said = str(caught.value).lower()
    assert "no call was placed" in said
    for lie in ("help is on the way", "calling", "we have called",
                "emergency services have been contacted"):
        assert lie not in said


def test_the_press_belongs_to_the_person_who_raised_it(
        client, profile_id, interactor_id, interactor_head):
    _arm(interactor_id)
    row = _unresolved(client, profile_id, interactor_id, interactor_head)
    with pytest.raises(escalation.NotArmed):
        escalation.dial(row["id"], "usr_somebody_else")


# --------------------------------------------------------------------------
# The seal itself.
# --------------------------------------------------------------------------

def test_the_seal_is_read_at_the_call_not_at_import(monkeypatch):
    """A deployment that has to restart to shut this is a deployment that will
    leave it open."""
    assert escalation.sealed() is True
    monkeypatch.setenv("QRME_DIALER_ARMED", "1")
    assert escalation.sealed() is False
    monkeypatch.delenv("QRME_DIALER_ARMED")
    assert escalation.sealed() is True


def test_unsealing_without_a_carrier_still_places_no_call(monkeypatch):
    """The honest middle state. A deployment that opens the switch and has
    configured nothing must not be told a call went out."""
    monkeypatch.setenv("QRME_DIALER_ARMED", "1")
    with pytest.raises(escalation.Sealed) as caught:
        escalation._place("999")
    assert "no call was placed" in str(caught.value).lower()


def test_nothing_but_the_deployment_can_open_the_seal():
    """No parameter, plan, profile setting or request field.

    Crude on purpose: any argument at all on `sealed()` fails this, because
    the argument for adding one always sounds reasonable — a test that needs
    it open, a plan tier that should bypass it, a debug flag that shipped.
    """
    assert list(inspect.signature(escalation.sealed).parameters) == []
    assert list(inspect.signature(escalation._place).parameters) == ["number"]
    body = inspect.getsource(escalation._place)
    assert "sealed()" in body, "the last hop must consult the seal itself"


def test_the_route_does_not_second_guess_the_seal():
    """Enforced at the last hop, not in the route above it — a refusal that
    lived in the router is a refusal a second caller walks past."""
    from qrme.routers import escalation as routes
    src = inspect.getsource(routes)
    assert "QRME_DIALER_ARMED" not in src
    assert "Sealed" in src, "the route translates the refusal rather than "\
                            "deciding it"


def test_placed_is_set_by_a_connected_call_and_nothing_else():
    """The one column somebody would read to answer *did help get called*."""
    src = inspect.getsource(escalation)
    assert "placed=1" not in src.replace(" ", "")
    assert "SET dialed_at" in src, "the attempt is recorded; the outcome is not"
