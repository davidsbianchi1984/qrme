"""A refused verification says why, and the levels can be discovered.

Both of these were found by building the console door for verification, which
is the point worth recording: the routes had been correct for every caller that
already knew the answers, and wrong for the first one that did not.

**The 500.** `POST /profiles/{id}/verification` caught `identity.IdentityError`
and not `verification.VerificationError`. The two come from adjacent modules and
only one was in the `except`, so a claim with an unknown proofing level — or a
level above `self_asserted` with nobody named as having checked — raised
through FastAPI as a **500 with an empty body**.

The part that makes it worth a test rather than a fix: the exception it dropped
carried the exact sentence the caller needed, naming all four valid levels. The
work of explaining had been done and was then thrown away by the wrong handler.
A missing message is a gap; a written message discarded on the way out is a
worse kind of bug, because everything upstream looks careful.

**The undiscoverable set.** `GET /identity/vocabulary` is the route whose whole
job is to publish the closed sets a client must offer. It described every rule
about verification — who may hold the badge, that it moves, that an invented
person is unverifiable — and omitted the four words the claim itself has to be
made in. You could not build a level picker from the API; you had to read
`qrme/verification.py`. A vocabulary that is complete about the philosophy and
silent about the enum is the kind of gap only a client author finds.
"""

from __future__ import annotations

import pytest

from qrme import verification


def _profile(client, **kw):
    body = {"owner_id": "acct_v", "kind": "self", "display_name": "Ada",
            "purpose": "family", "persona": "p",
            "verification": {"birthdate": "1990-01-01"}}
    body.update(kw)
    r = client.post("/profiles", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_the_levels_are_discoverable_from_the_api(client):
    """A client must be able to build the picker without reading the source."""
    v = client.get("/identity/vocabulary").json()
    assert "proofing_levels" in v, (
        "the vocabulary route publishes every rule about verification and not "
        "the levels a claim must use")
    got = [row["level"] for row in v["proofing_levels"]]
    assert got == list(verification.PROOFING_LEVELS), (
        "published in a different order from the ladder itself — a screen "
        f"would imply the wrong ranking: {got}")
    for row in v["proofing_levels"]:
        assert row["means"] == verification.MEANING[row["level"]]
    # Weakest first, and only the weakest needs no attestor.
    assert v["proofing_levels"][0]["needs_attestor"] is False
    assert all(r["needs_attestor"] for r in v["proofing_levels"][1:])


def test_an_unknown_level_is_refused_in_words(client):
    """422 carrying the message, not a 500 carrying nothing."""
    p = _profile(client)
    r = client.post(f"/profiles/{p['id']}/verification",
                    json={"level": "identity"},
                    headers={"authorization": f"Bearer {p['owner_token']}"})
    assert r.status_code == 422, (
        f"expected a refusal the caller can read, got {r.status_code}: "
        f"{r.text[:200]}")
    detail = r.json()["detail"]
    # The valid set, in the refusal, so a wrong guess is self-correcting.
    for level in verification.PROOFING_LEVELS:
        assert level in detail, f"the refusal does not name {level!r}: {detail}"


def test_a_level_needing_an_attestor_says_so(client):
    """The other `VerificationError`, from the same uncaught branch."""
    p = _profile(client)
    r = client.post(f"/profiles/{p['id']}/verification",
                    json={"level": "document"},
                    headers={"authorization": f"Bearer {p['owner_token']}"})
    assert r.status_code == 422, r.text
    assert "attestor" in r.json()["detail"]


def test_the_one_badge_rule_still_answers_409(client):
    """The fix must not have flattened two different refusals into one.

    A malformed claim is the caller's mistake (422). The one-badge rule is the
    product refusing something well-formed (409), and it is the case where the
    reply also tells you what to do instead — move it. Collapsing them would
    lose that.
    """
    a = _profile(client, owner_id="acct_two", display_name="One")
    b = _profile(client, owner_id="acct_two", display_name="Two")
    ok = client.post(f"/profiles/{a['id']}/verification",
                     json={"level": "document", "attestor": "Dr Okafor"},
                     headers={"authorization": f"Bearer {a['owner_token']}"})
    assert ok.status_code == 201, ok.text
    r = client.post(f"/profiles/{b['id']}/verification",
                    json={"level": "document", "attestor": "Dr Okafor"},
                    headers={"authorization": f"Bearer {b['owner_token']}"})
    assert r.status_code == 409, r.text
    assert "move it" in r.json()["detail"].lower()


@pytest.mark.parametrize("level", list(verification.PROOFING_LEVELS))
def test_every_published_level_is_actually_accepted(level, client):
    """The set the API advertises and the set it accepts are the same set.

    Neither half of this file's fixes is worth much if the vocabulary can go
    on to advertise a level the claim endpoint then rejects — that would be
    the original bug with an extra step.
    """
    p = _profile(client, owner_id=f"acct_{level}")
    r = client.post(f"/profiles/{p['id']}/verification",
                    json={"level": level, "attestor": "Dr Okafor",
                          "method": "checked"},
                    headers={"authorization": f"Bearer {p['owner_token']}"})
    assert r.status_code == 201, f"{level} is published but refused: {r.text}"
    assert r.json()["level"] == level
