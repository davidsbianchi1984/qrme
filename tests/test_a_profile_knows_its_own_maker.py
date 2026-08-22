"""A profile knows its own maker.

Field report, after signing out and back in on another device:

    "Both profiles chatting with the AI synthetic profile that I built
     doesn't understand. I'm Bianchi, the verified profile that created
     its profile."

    asked     who is this profile talking to
    mattered  is it the person who made it

## The finding

`profiles.owner_id` has been in the schema since the first migration and
reached **no prompt in this codebase**. The word "owner" appeared in
`persona.py` only in comments about owner-set *language* and owner
*sliders*. Nothing computed whether the person speaking was the owner —
a one-line comparison of `interactors.account_id` against
`profiles.owner_id`, available on every surface and used on none.

And it was worse than absent. `build_system_prompt` ends its relationship
block with an `else`:

    "You do not know this person; treat them as a stranger — be polite but
     reserved, and share nothing private."

In a room, `relationship` was **always** None — `_profile_turns` called
`build_system_prompt(profile, None, None, ...)` — so that line fired for
every seat at the table, and a profile was actively instructed to be
reserved with the account that made it.

## The line this must not cross

Recognition is knowledge, not authority. Being the maker means the profile
knows you and speaks to you as the person who built it; it does not widen
what it may do without asking. Money, credentials and anything reaching
outside the conversation stay ask-first for the owner exactly as for a
stranger, and `_OWNER_NOTE` says so in the prompt rather than leaving it
to be inferred.

## Not the sign-in

Cross-device identity was already sound: `accounts.interactor_for` is
idempotent per account and hands back the same interactor row every time,
so the Android sign-in was the same person to the profile all along.
"""

from __future__ import annotations

from pathlib import Path

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)

ROOT = Path(__file__).resolve().parents[1]
PERSONA = (ROOT / "qrme/persona.py").read_text(encoding="utf-8")
COMMUNITY = (ROOT / "qrme/routers/community.py").read_text(encoding="utf-8")


def _profile_row(profile_id: str) -> dict:
    from qrme import db
    return dict(db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)).fetchone())


def test_the_owner_is_recognised(client):
    from qrme import accounts, persona

    dana = make_profile(client)
    profile = _profile_row(dana["id"])
    mine = accounts.interactor_for(profile["owner_id"], "David")
    assert persona.made_by(profile, mine["id"]) is True


def test_somebody_else_is_not(client):
    from qrme import persona

    dana = make_profile(client)
    stranger = make_interactor(client, "Nosy")
    assert persona.made_by(_profile_row(dana["id"]), stranger) is False


def test_an_accountless_visitor_is_nobodys_owner(client):
    """A stranger scanning a beacon has no account — a first-class case in
    this schema — and must never match by accident."""
    from qrme import persona

    dana = make_profile(client)
    visitor = make_interactor(client, "Passerby")
    assert persona.made_by(_profile_row(dana["id"]), visitor) is False
    assert persona.made_by(_profile_row(dana["id"]), None) is False


def test_the_maker_is_not_called_a_stranger(client):
    """The defect, in one assertion."""
    from qrme import accounts, persona

    dana = make_profile(client)
    profile = _profile_row(dana["id"])
    mine = accounts.interactor_for(profile["owner_id"], "David")
    said = persona.build_system_prompt(profile, None, None,
                                       viewer_id=mine["id"])
    assert "treat them as a stranger" not in said
    assert "the account that made you" in said


def test_a_stranger_still_is_one(client):
    """The reserve is right for people the profile does not know. Fixing
    the owner case must not open the profile to everybody."""
    from qrme import persona

    dana = make_profile(client)
    stranger = make_interactor(client, "Nosy")
    said = persona.build_system_prompt(_profile_row(dana["id"]), None, None,
                                       viewer_id=stranger)
    assert "treat them as a stranger" in said


def test_knowing_the_maker_grants_no_authority(client):
    """Recognition is knowledge, not permission. An owner who is recognised
    is still asked before money moves or a credential is used."""
    from qrme import accounts, persona

    dana = make_profile(client)
    profile = _profile_row(dana["id"])
    mine = accounts.interactor_for(profile["owner_id"], "David")
    said = persona.build_system_prompt(profile, None, None,
                                       viewer_id=mine["id"])
    assert "not what you may DO" in said
    assert "spends money" in said and "credential" in said


def test_a_room_names_how_the_profile_knows_each_seat(client):
    """`among` replaced a flat list of names. Naming somebody and saying
    how you know them is one sentence; the second half was missing."""
    from qrme import accounts, persona

    dana = make_profile(client)
    profile = _profile_row(dana["id"])
    mine = accounts.interactor_for(profile["owner_id"], "David")
    said = persona.build_system_prompt(
        profile, None, None,
        among=[{"display": "David", "kind": "user", "is_owner": True},
               {"display": "Nosy", "kind": "user"},
               {"display": "Ada", "kind": "profile"}])
    assert "your owner, the account that made you" in said
    assert "a person you do not know" in said
    assert "another synthetic profile" in said
    assert "the account that made you" in said
    assert mine["id"] not in said, "an internal id leaked into the prompt"


def test_a_room_does_not_call_everybody_a_stranger(client):
    """The singular stranger line has no referent when four people are
    present, and it fired on all of them."""
    from qrme import persona

    dana = make_profile(client)
    said = persona.build_system_prompt(
        _profile_row(dana["id"]), None, None,
        among=[{"display": "Ada", "kind": "profile"}])
    assert "treat them as a stranger" not in said


def test_the_room_path_actually_passes_the_cast():
    """A helper nobody calls is a helper that fixes nothing."""
    turns = COMMUNITY[COMMUNITY.index("def _profile_turns"):]
    turns = turns[:turns.index("\n@router")]
    assert "among=among" in turns
    assert "persona.made_by(" in turns, (
        "the room builds a cast without asking which of them made this "
        "profile — the one thing the field report was about")


def test_the_one_to_one_path_passes_the_viewer():
    src = (ROOT / "qrme/routers/interaction.py").read_text(encoding="utf-8")
    assert "viewer_id=body.interactor_id" in src, (
        "a profile meeting its maker in a private chat is still told to "
        "treat them as a stranger")


def test_the_comparison_is_account_against_owner():
    """An interactor id is a different kind of thing from an owner id and
    would never match — the comparison has to go through the account."""
    fn = PERSONA[PERSONA.index("def made_by"):]
    fn = fn[:fn.index("\n_OWNER_NOTE")]
    assert "account_id" in fn
    assert 'row["account_id"] == profile["owner_id"]' in fn
