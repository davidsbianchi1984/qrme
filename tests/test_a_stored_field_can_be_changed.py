"""A field somebody stored is a field somebody can change.

Requirement, from the field: "if users modify the synthetic profiles in
any way, the return visit will render those modifications."

Storage was never the problem — `profiles` rows are durable and
`profile_out` reads them fresh. Doors were. `ProfileUpdate` exposed ten
fields against thirty columns, and a column with no door cannot be
modified, so "renders on return" was vacuous for every one of them.

    asked     is the change kept
    mattered  was there a way to make it in the first place

## What this found

`kind`, `base_age` and `adult_mode` had **no update site anywhere in the
codebase** — set once at creation, never again. `kind` is the one that
bit: it defaults to `"fictional"`, only the onboarding flow sets
`"self"`, and it decides `avatars.likeness().real_person`. So a digital
twin built any other way was permanently recorded as an invented
character whose portrait depicts nobody, and every surface checking that
record refused to draw it as a person's face.

## The shape of this guard

Every column is one of four things, and the guard makes the codebase say
which: settable on PATCH, holder of a dedicated door, system-owned, or
written down in `profile_columns_doorless.txt` with a reason. A new column
that is none of the four fails, which is the point — the next `kind`
should be caught the week it lands rather than a year later.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.test_capabilities import (as_interactor, make_interactor,  # noqa: F401
                                     make_profile, pdi_pair)

ROOT = Path(__file__).resolve().parents[1]
DB = (ROOT / "qrme/db.py").read_text(encoding="utf-8")
MODELS = (ROOT / "qrme/models.py").read_text(encoding="utf-8")
RECORD = ROOT / "tests/profile_columns_doorless.txt"

# The system owns these; nobody edits them, and a door would be a defect.
SYSTEM_OWNED = {
    "id", "owner_id", "created_at", "status", "forgot_at",
    "terms_accepted_at", "terms_version", "licensed_from",
    # Written by the kind transition rather than set directly — a rights
    # claim is a consequence of what the profile IS, not a free-text field.
    "consent_basis", "consent_attestor",
}

# A door of their own, rather than a field on PATCH /profiles/{id}: the
# column, the file that holds that door, and the shape to look for in it.
#
# `sources` is the odd one and is written down as odd rather than tidied
# away: the COLUMN is set once at creation and never updated, because the
# live material lives in the `source_items` table behind
# POST /profiles/{id}/sources. The door is real; it just does not write
# this column, and a guard that pretended otherwise would be checking the
# wrong thing.
OWN_DOOR = {
    "anonymous": ("qrme/identity.py", r"SET anonymous="),
    "sources": ("qrme/routers/profiles.py",
                r'@router\.post\("/profiles/\{profile_id\}/sources"'),
    "avatar": ("qrme/avatars.py", r"SET avatar="),
    "watermark_design": ("qrme/watermark.py", r"SET watermark_design="),
    "unlisted": ("qrme/friends.py", r"SET unlisted="),
    "demographics": ("qrme/routers/steering.py", r"SET demographics="),
}


def _profile_columns() -> list[str]:
    block = DB[DB.index("CREATE TABLE IF NOT EXISTS profiles ("):]
    block = block[:block.index("\n);")]
    out = []
    for line in block.splitlines()[1:]:
        line = line.strip()
        if not line or line.startswith("--"):
            continue
        name = line.split()[0]
        if name.upper() in ("PRIMARY", "FOREIGN", "UNIQUE", "CHECK"):
            continue
        out.append(name)
    return out


def _patchable() -> set[str]:
    block = MODELS[MODELS.index("class ProfileUpdate"):]
    block = block[:block.index("class ProfileOut")]
    return set(re.findall(r"^    (\w+):", block, re.M))


def _recorded() -> dict[str, str]:
    rows = {}
    for line in RECORD.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, _, reason = line.partition("  ")
        rows[name.strip()] = reason.strip()
    return rows


def test_every_column_is_one_of_the_four():
    """Settable, own door, system-owned, or written down with a reason."""
    unexplained = [
        c for c in _profile_columns()
        if c not in _patchable() and c not in SYSTEM_OWNED
        and c not in OWN_DOOR and c not in _recorded()]
    assert not unexplained, (
        "profile columns nobody can change and nobody accounted for: "
        + ", ".join(unexplained)
        + " — give each a door, or a line in "
          "tests/profile_columns_doorless.txt saying why not")


def test_the_record_only_shrinks():
    assert len(_recorded()) <= 1, (
        "a column arrived on the doorless record — this list is a ratchet "
        "and only comes down")


def test_every_recorded_column_says_why():
    for name, reason in _recorded().items():
        assert len(reason) > 40, (
            f"{name} is recorded as doorless with no real reason")


def test_the_own_door_modules_still_hold_those_doors():
    """A dedicated door that moved or was deleted would leave the column
    doorless while this guard kept passing."""
    for column, (where, shape) in OWN_DOOR.items():
        src = (ROOT / where).read_text(encoding="utf-8")
        assert re.search(shape, src), (
            f"{column} is credited to {where}, which no longer holds its door")


# -- the kind door, which is what all of this was about -----------------------

def _kind_of(profile_id: str) -> str:
    from qrme import db
    return db.connect().execute(
        "SELECT kind FROM profiles WHERE id=?", (profile_id,)).fetchone()["kind"]


def test_an_owner_can_say_this_one_is_me(client):
    # The helper defaults to kind="self"; the case worth testing starts
    # where a profile made outside the onboarding flow starts.
    dana = make_profile(client, kind="fictional")
    r = client.patch(f"/profiles/{dana['id']}", json={"kind": "self"},
                     headers={"authorization": f"Bearer {dana['owner_token']}"})
    assert r.status_code == 200, r.text
    assert _kind_of(dana["id"]) == "self"


def test_saying_it_is_me_makes_the_likeness_record_true(client):
    """The whole reason this mattered: `likeness().real_person` is read by
    every surface that decides whether a portrait may be drawn as a
    person's face."""
    from qrme import avatars

    dana = make_profile(client, kind="fictional")
    assert avatars.likeness(dana["id"])["real_person"] is False
    client.patch(f"/profiles/{dana['id']}", json={"kind": "self"},
                 headers={"authorization": f"Bearer {dana['owner_token']}"})
    said = avatars.likeness(dana["id"])
    assert said["real_person"] is True
    assert said["basis"], "a real likeness with no recorded basis"
    assert said["attestor"], "a real likeness nobody attested to"


def test_becoming_fictional_clears_the_rights_claim(client):
    """An invented character has no rights holder. Leaving a real person's
    attestation on one is a false claim sitting on the row."""
    from qrme import db

    dana = make_profile(client)
    head = {"authorization": f"Bearer {dana['owner_token']}"}
    client.patch(f"/profiles/{dana['id']}", json={"kind": "self"}, headers=head)
    client.patch(f"/profiles/{dana['id']}", json={"kind": "fictional"},
                 headers=head)
    row = db.connect().execute(
        "SELECT consent_basis, consent_attestor FROM profiles WHERE id=?",
        (dana["id"],)).fetchone()
    assert not row["consent_basis"]
    assert not row["consent_attestor"]


def test_another_real_person_still_needs_a_consent_record(client):
    dana = make_profile(client)
    head = {"authorization": f"Bearer {dana['owner_token']}"}
    r = client.patch(f"/profiles/{dana['id']}",
                     json={"kind": "other_person"}, headers=head)
    assert r.status_code == 422, r.text
    ok = client.patch(f"/profiles/{dana['id']}", headers=head,
                      json={"kind": "other_person",
                            "consent": {"basis": "subject_consent",
                                        "attestor": "Ada Lovelace"}})
    assert ok.status_code == 200, ok.text


def test_a_hybrid_is_still_born_not_typed(client):
    dana = make_profile(client)
    r = client.patch(f"/profiles/{dana['id']}", json={"kind": "hybrid"},
                     headers={"authorization": f"Bearer {dana['owner_token']}"})
    assert r.status_code == 422
    assert "composite" in r.json()["detail"]


def test_a_stranger_cannot_change_what_a_profile_is(client):
    dana = make_profile(client, kind="fictional")
    other = make_profile(client)
    r = client.patch(f"/profiles/{dana['id']}", json={"kind": "self"},
                     headers={"authorization":
                              f"Bearer {other['owner_token']}"})
    assert r.status_code in (401, 403)
    assert _kind_of(dana["id"]) == "fictional"


def test_the_change_survives_the_return_visit(client):
    """The requirement in one test: modify it, come back, read it."""
    dana = make_profile(client)
    head = {"authorization": f"Bearer {dana['owner_token']}"}
    client.patch(f"/profiles/{dana['id']}", headers=head,
                 json={"kind": "self", "appearance": "silver hair, denim",
                       "base_age": 41})
    seen = client.get(f"/profiles/{dana['id']}", headers=head).json()
    assert seen["kind"] == "self"
    from qrme import db
    row = db.connect().execute(
        "SELECT appearance, base_age FROM profiles WHERE id=?",
        (dana["id"],)).fetchone()
    assert row["appearance"] == "silver hair, denim"
    assert row["base_age"] == 41


# -- adult mode: shown, and shut ---------------------------------------------

IDENTITY = (ROOT / "app/src/screens/Identity.tsx").read_text(encoding="utf-8")


def test_the_rated_setting_is_on_screen():
    """Shown, because a setting nobody can see is a setting nobody can
    audit — an owner who cannot tell what their own profile is set to
    cannot check it."""
    assert "idn.rated" in IDENTITY, (
        "adult mode is invisible as well as unchangeable")
    assert "idn.rated.on" in IDENTITY and "idn.rated.off" in IDENTITY, (
        "the screen shows the setting exists without saying which way it "
        "is set")


def test_the_rated_control_is_shut():
    """And shut, because every guard on it lives at creation. Shown and
    shut is a deliberate pair, not an unfinished one."""
    block = IDENTITY[IDENTITY.index('<h3>{tr("idn.rated"'):]
    block = block[:block.index("</div>")]
    assert "disabled" in block and "readOnly" in block, (
        "the adult-mode control can be operated")
    assert "onChange" not in block, (
        "the adult-mode control is wired to something")
    assert "idn.rated.why" in block, (
        "the control is shut and does not say why, which reads as a bug "
        "rather than a decision")


def test_the_reason_names_all_three_checks():
    """A refusal that says 'not here' teaches nothing. The copy names what
    is actually being protected."""
    row = (ROOT / "app/src/l10n.ts").read_text(encoding="utf-8")
    row = row[row.index('"idn.rated.why"'):]
    row = row[:row.index("},")]
    said = re.search(r'en: "([^"]+)"', row).group(1).lower()
    assert "verified adult" in said
    assert "another real person" in said
    assert "plan" in said


def test_no_field_stands_behind_the_shut_control():
    """The half that matters. A visible-but-disabled control with a live
    PATCH field behind it is worse than no control at all."""
    assert "adult_mode" not in _patchable(), (
        "adult_mode became settable on PATCH — the checks that live in "
        "create_profile would be routed around")
    assert "adult_mode" in _recorded(), (
        "adult_mode left the doorless record without gaining a door")
