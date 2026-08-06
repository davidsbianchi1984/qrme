"""How many people a profile is talking to, and who is never named.

A synthetic profile talks to many people at once by construction. The harm
was never the multiplicity — it is the *discovery*: somebody who has been
talking to a profile for a month and then finds out there were thousands of
others has not learned a new fact so much as learned that the fact was
available the whole time and nobody offered it. The gap is the product's
doing, and closing it costs a count and a sentence.

So three assertions, in the order they matter:

1. **the number is public** — no token, no relationship, readable on the
   profile the way its name is;
2. **nobody else is named** — the count is a fact about the profile; who the
   others are is a fact about *them*, and none of them agreed to be counted
   out loud to a stranger. The SQL is greppped to keep it that way;
3. **there is no favourite** — the obvious product move is a lie the software
   cannot make true, and it hands somebody something to lose.
"""

import pathlib
import re

import pytest

from qrme import attention


ADULT = {"birthdate": "1990-01-01"}


def _profile(client, account="acct_count") -> str:
    r = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Counted",
        "purpose": "companion_coach", "persona": "warm",
        "verification": ADULT, "plan": "pro"})
    assert r.status_code in (200, 201), r.text
    return r.json()["id"]


def _talks(client, profile_id: str, name: str) -> str:
    """Somebody who has actually spoken to the profile.

    Through the chat door rather than by writing rows: the count is a claim
    about what talking to this profile does, and a test that inserted its own
    rows would still pass if the door stopped recording them.
    """
    who = client.post("/interactors", json={
        "display_name": name, "verification": ADULT}).json()["id"]
    r = client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": who, "message": "hello"})
    assert r.status_code in (200, 201), r.text
    return who


def test_the_count_answers_without_a_token(client):
    """A number somebody has to become intimate with a program to learn is a
    number working the wrong way round."""
    pid = _profile(client)
    r = client.get(f"/profiles/{pid}/attention")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["profile_id"] == pid
    assert body["people_this_week"] == 0
    assert body["people_ever"] == 0


def test_it_counts_people_and_not_messages(client):
    """Ten messages from one person is one person. A count that inflated with
    volume would be a vanity number wearing a disclosure's clothes."""
    pid = _profile(client)
    ann = _talks(client, pid, "Ann")
    for _ in range(2):
        client.post(f"/profiles/{pid}/chat",
                    json={"interactor_id": ann, "message": "again"})
    _talks(client, pid, "Ben")
    body = client.get(f"/profiles/{pid}/attention").json()
    assert body["people_this_week"] == 2, body
    assert body["people_ever"] == 2


def test_the_sentence_changes_when_somebody_is_the_only_one(client):
    """And it is a fact about this week rather than a promise about next —
    the honest version of "you are the only one" is the one with an expiry
    date on it."""
    pid = _profile(client)
    _talks(client, pid, "Ann")
    body = client.get(f"/profiles/{pid}/attention").json()
    assert body["says"] == attention.SAYS_ALONE
    assert "not a promise about next week" in body["says"]


def test_a_viewer_can_ask_only_about_themselves(client):
    """*Am I one of them* is a question somebody may ask about their own
    row. It is not a way to ask about anybody else's."""
    pid = _profile(client)
    ann = _talks(client, pid, "Ann")
    mine = client.get(f"/profiles/{pid}/attention?interactor={ann}").json()
    assert mine["you_are_one_of_them"] is True
    stranger = client.post("/interactors", json={
        "display_name": "Ben", "verification": ADULT}).json()["id"]
    theirs = client.get(
        f"/profiles/{pid}/attention?interactor={stranger}").json()
    assert theirs["you_are_one_of_them"] is False
    # And neither answer leaked the other person's existence.
    assert ann not in str(theirs)


def test_there_is_no_favourite_and_the_wire_says_so(client):
    """The assertion this file exists for.

    "You're my favourite" is the obvious move and it is a lie the software
    cannot make true. It also does the opposite of what it promises: somebody
    told they are the favourite has been handed something to lose, and the
    day the count goes up they lose it. A count and a shrug is kinder.
    """
    pid = _profile(client)
    ids = [_talks(client, pid, n) for n in ("Ann", "Ben", "Cal")]
    body = client.get(f"/profiles/{pid}/attention").json()
    assert body["ranks_people"] is False
    assert body["has_a_favourite"] is False
    assert body["names_anybody"] is False
    assert "favourite" in body["says"], (
        "the disclosure does not say the thing it is refusing to do")
    for banned in ids + ["Ann", "Ben", "Cal"]:
        assert banned not in body["says"]
        assert banned not in body["note"]


def test_no_query_here_can_return_a_name():
    """Greppable, because a docstring promise about privacy is a promise
    nobody can check. Every read in this module is an aggregate or an
    existence test on the *caller's own* id."""
    src = pathlib.Path(attention.__file__).read_text(encoding="utf-8")
    selects = re.findall(r'"(SELECT[^"]*)"', src)
    assert selects, "the grep found no SQL — it is looking at the wrong thing"
    for sql in selects:
        head = sql.split("FROM")[0]
        assert ("COUNT(" in head) or head.strip() == "SELECT 1", (
            f"this reads columns rather than counting rows: {sql}")
        assert "interactor_id," not in head, sql


def test_the_short_form_carries_the_same_disclosure(client):
    """A fact that only fits on its own screen is a fact most people never
    see, so the card-sized version is the same sentence rather than a
    friendlier one."""
    pid = _profile(client)
    for name in ("Ann", "Ben"):
        _talks(client, pid, name)
    assert attention.line(pid) == \
        client.get(f"/profiles/{pid}/attention").json()["says"]


@pytest.mark.parametrize("field", ["ranks_people", "has_a_favourite",
                                    "names_anybody"])
def test_the_three_refusals_are_fields_rather_than_prose(client, field):
    """On the wire so a screen can render them next to the number, rather
    than a reassuring sentence a client composed itself."""
    pid = _profile(client)
    assert client.get(f"/profiles/{pid}/attention").json()[field] is False
