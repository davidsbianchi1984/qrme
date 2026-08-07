"""The other half of the multiplicity disclosure, pointed at the person.

`attention.py` tells somebody how many people a profile is talking to. It is
the honest half of a fact that would otherwise be discovered by accident. This
is the same fact from the other end and nobody was reporting it: a person can
spend months here in conversation that is entirely synthetic, and **the
platform is the only party in a position to see that**.

    asked     does a profile disclose how divided its attention is
    mattered  does anybody tell the person how one-sided theirs has been

## What this file is mostly about

The feature is thirty lines of counting. Nearly everything below is about the
four things it must never turn into, because each of them is what a product
with a growth target would build instead:

* **a diagnosis** — deciding somebody is lonely and telling them so;
* **a notification** — watching the logs and then messaging about what they say;
* **a signal about a user, readable by somebody else** — a profile owner
  learning which of their visitors have nobody else;
* **a transcript with a referral stapled to it** — handing a *health* product
  the content of somebody's private evenings under the banner of helping.

Each has a test here, and each test would fail on the version of this feature
that a metrics review would ask for.
"""

from __future__ import annotations

from qrme import solitude
from tests.test_capabilities import auth_header, make_profile


def _interactor(client, name="Vis"):
    r = client.post("/interactors", json={"display_name": name,
                                          "birthdate": "1990-01-01"})
    assert r.status_code in (200, 201), r.text
    return r.json()["id"]


def _talk_to_profile(client, times=1):
    """Real turns through the real route, so the count is of what the product
    actually recorded rather than of rows this test wrote itself."""
    owner = make_profile(client, display_name="A Profile")
    who = _interactor(client)
    for i in range(times):
        client.post(f"/profiles/{owner['id']}/chat",
                    json={"interactor_id": who, "message": f"hello {i}"},
                    headers=auth_header(owner))
    return who, owner


# --- the count itself -------------------------------------------------------

def test_a_quiet_account_is_told_it_is_too_early_to_say(client):
    """Two turns is not a shape. Offering a door on that evidence is the
    software being presumptuous about somebody it has barely met."""
    who, _ = _talk_to_profile(client, times=2)
    body = client.get(f"/interactors/{who}/solitude").json()
    assert body["enough_to_say"] is False, body
    assert "offer" not in body, body


def test_an_account_that_only_talked_to_profiles_is_offered_the_door(client):
    who, _ = _talk_to_profile(client, times=solitude.MIN_TURNS)
    body = client.get(f"/interactors/{who}/solitude").json()
    assert body["enough_to_say"] is True, body
    assert body["share_synthetic"] == 1.0, body
    assert body["offer"]["state"] == "available", body
    assert body["offer"]["what"] == "jim-mini", body


def test_the_counts_are_of_this_persons_own_turns(client):
    """Not of the profile's replies. A chatty profile answering three times per
    message would otherwise move a number that is supposed to describe a
    person's own week."""
    who, _ = _talk_to_profile(client, times=solitude.MIN_TURNS)
    body = client.get(f"/interactors/{who}/solitude").json()
    assert body["turns"]["to_profiles"] == solitude.MIN_TURNS, body


# --- the four things it must not become -------------------------------------

def test_nothing_in_the_answer_diagnoses_the_reader(client):
    """The word is not there, and neither is any of its family.

    This product cannot know. Somebody with a full life may talk to a profile
    every evening for reasons entirely their own. A count is a fact and is
    what the software is entitled to say; *"you seem lonely"* is a verdict it
    has no standing to reach and no way to check.
    """
    who, _ = _talk_to_profile(client, times=solitude.MIN_TURNS)
    said = str(client.get(f"/interactors/{who}/solitude").json()).lower()
    for verdict in ("lonely", "loneliness", "isolated", "isolation",
                    "withdrawn", "depress", "at risk", "concern"):
        assert verdict not in said, (
            f"the answer says {verdict!r} — this reports a count and does not "
            f"reach a conclusion about the person reading it")


def test_reading_it_is_a_pull_and_never_arrives_on_its_own(client):
    """A product that watched somebody's conversations and then messaged them
    about it would be performing the surveillance the count exists to
    disclose. Talking a great deal to profiles must put nothing in the inbox.
    """
    who, _ = _talk_to_profile(client, times=solitude.MIN_TURNS)
    inbox = client.get(f"/interactors/{who}/inbox")
    if inbox.status_code == 200:
        blob = str(inbox.json()).lower()
        assert "solitude" not in blob and "jim-mini" not in blob, (
            "the count reached the inbox — it is a pull and nothing else")


def test_no_route_lets_anybody_else_read_this_about_a_person(client):
    """The count is a fact about one person's own use of the software. The
    moment a second party can read it, it stops being a disclosure and becomes
    a tool for exactly what it was written to disclose — a profile owner
    learning which of their visitors have nobody else to talk to.
    """
    from qrme.api import create_app
    paths = [p for p in create_app().openapi()["paths"] if "solitude" in p]
    assert paths, "the routes vanished and this test proved nothing"
    for p in paths:
        assert p.startswith("/interactors/{interactor_id}/solitude"), (
            f"{p} reaches the count from somewhere that is not the person's "
            f"own account")


def test_the_referral_carries_no_word_anybody_wrote(client):
    """The bridge is counts and a window.

    JIM-mini is a health guardian. A referral from here that carried
    conversation content would be handing a medical product the transcript of
    somebody's private evenings under the banner of helping them — which is
    the precise trade this ecosystem exists to refuse.
    """
    secret = "the-thing-i-only-said-here"
    owner = make_profile(client, display_name="A Profile")
    who = _interactor(client)
    for i in range(solitude.MIN_TURNS):
        client.post(f"/profiles/{owner['id']}/chat",
                    json={"interactor_id": who, "message": secret},
                    headers=auth_header(owner))

    r = client.post(f"/interactors/{who}/solitude/handoff",
                    json={"accept": True})
    assert r.status_code == 200, r.text
    ref = r.json()["referral"]
    blob = str(ref)
    assert secret not in blob, "the referral carries what was written"
    assert owner["id"] not in blob, "the referral names the profile"
    assert owner["display_name"] not in blob, "the referral names the profile"
    assert set(ref) == {"ref", "window_days", "turns", "issued_at", "product"}, ref


# --- consent ----------------------------------------------------------------

def test_declining_is_recorded_and_the_offer_does_not_come_back(client):
    """The more important half. An offer somebody declined that reappears next
    month is the product overriding an answer it already got, and the second
    asking is worse than the first."""
    who, _ = _talk_to_profile(client, times=solitude.MIN_TURNS)
    assert client.get(f"/interactors/{who}/solitude"
                      ).json()["offer"]["state"] == "available"

    client.post(f"/interactors/{who}/solitude/handoff", json={"accept": False})
    again = client.get(f"/interactors/{who}/solitude").json()
    assert again["offer"]["state"] == "declined", again
    assert "accept_at" not in again["offer"], again


def test_declining_issues_no_referral(client):
    who, _ = _talk_to_profile(client, times=solitude.MIN_TURNS)
    client.post(f"/interactors/{who}/solitude/handoff", json={"accept": False})
    assert client.get(f"/interactors/{who}/solitude/referral"
                      ).status_code == 404


def test_the_person_can_read_the_referral_before_it_travels(client):
    """A referral somebody cannot look at before it moves is a referral they
    did not really consent to."""
    who, _ = _talk_to_profile(client, times=solitude.MIN_TURNS)
    client.post(f"/interactors/{who}/solitude/handoff", json={"accept": True})
    r = client.get(f"/interactors/{who}/solitude/referral")
    assert r.status_code == 200, r.text
    assert r.json()["product"] == "jim-mini"


def test_consent_has_no_default(client):
    """An empty POST is not an acceptance. A body whose `accept` defaulted to
    true would turn a mis-fired button into a consent nobody typed."""
    who, _ = _talk_to_profile(client, times=solitude.MIN_TURNS)
    assert client.post(f"/interactors/{who}/solitude/handoff",
                       json={}).status_code == 422


def test_a_handoff_with_nothing_behind_it_is_refused(client):
    """Accepting a door that was never offered still must not mint a referral
    built on four turns."""
    who, _ = _talk_to_profile(client, times=2)
    r = client.post(f"/interactors/{who}/solitude/handoff",
                    json={"accept": True})
    assert r.status_code == 409, r.text
