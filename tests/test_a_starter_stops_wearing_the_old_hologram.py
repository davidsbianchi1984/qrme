"""A starter wearing a face this deployment minted gets its portrait back.

    asked     why is this starter still a blue character
    mattered  is this face OURS to replace

`_backfill` fills a BLANK — `COALESCE` — which is right for the case it
was written for and cannot reach this one. A deployment seeded before
the photographs shipped minted cyan holograms for itself (`avatars.STYLE`
is that prompt) and then kept them forever, because a face that is
already set is never a blank again. Reported twice from the field: "some
of the starter packs are still blue characters", and a seat in a room
that was "one of the old hologram ones".

The danger in fixing it is obvious and is what most of these guard: a
starter can be claimed, and an owner who chose their own picture must
keep it. So the rule is narrow on purpose — a face is replaced only when
the deployment demonstrably put it there, and an unaccountable face is
left alone. One odd-looking seat is a smaller cost than destroying
somebody's chosen picture.
"""

from __future__ import annotations

import pytest

from qrme import avatars, db, seed


HANDLE = "dr_amara_osei"


@pytest.fixture()
def wearing(tmp_path, monkeypatch):
    """A starter profile with whatever face the test wants to put on it."""
    monkeypatch.setenv("QRME_DB", str(tmp_path / "reface.db"))
    db.reset()
    conn = db.connect()
    conn.execute(
        "INSERT INTO profiles (id, owner_id, kind, display_name, persona,"
        " status, created_at)"
        " VALUES ('p_star','o1','fictional','Amara','A cardiologist.',"
        "'active',?)", (db.utcnow(),))
    conn.commit()

    def put(asset, registry=None):
        conn.execute("UPDATE profiles SET avatar=? WHERE id='p_star'",
                     (asset,))
        if registry is not None:
            owner, source = registry
            conn.execute(
                "INSERT INTO avatar_registry (id, owner_account_id, source,"
                " provider, asset, rights, status, created_at)"
                " VALUES ('reg1',?,?,'internal',?,'{}','active',?)",
                (owner, source, asset, db.utcnow()))
        conn.commit()
        return conn

    yield put, conn
    db.reset()


def face_now(conn):
    return conn.execute(
        "SELECT avatar FROM profiles WHERE id='p_star'").fetchone()["avatar"]


def test_a_face_the_box_minted_for_itself_is_replaced(wearing):
    put, conn = wearing
    put("/media/holo-amara.webp", registry=(None, "seeded"))
    assert seed._restore_face(conn, "p_star", HANDLE) is True
    assert face_now(conn) == avatars.asset_path(HANDLE)


def test_a_prompted_face_with_no_owner_is_also_ours(wearing):
    put, conn = wearing
    put("/media/holo-amara.webp", registry=(None, "prompted"))
    assert seed._restore_face(conn, "p_star", HANDLE) is True


def test_a_portrait_path_with_no_registry_row_is_left_alone(wearing):
    """The rule that a first draft got wrong.

    Treating any `/portraits/` path with no file behind it as ours-by-route
    read a path and inferred intent, and
    `test_backfill_never_overwrites_what_an_owner_set` broke on it — that
    guard sets exactly this and expects it kept. A hunch is not evidence,
    and this is the one function here where a wrong guess destroys
    something somebody chose.
    """
    put, conn = wearing
    put(f"{avatars.ASSET_ROUTE}/mine.webp")
    assert seed._restore_face(conn, "p_star", HANDLE) is False
    assert face_now(conn) == f"{avatars.ASSET_ROUTE}/mine.webp"


def test_an_uploaded_face_is_left_alone(wearing):
    """The one that matters. Somebody chose this."""
    put, conn = wearing
    put("/media/my-own-photo.webp", registry=("acct_7", "uploaded"))
    assert seed._restore_face(conn, "p_star", HANDLE) is False
    assert face_now(conn) == "/media/my-own-photo.webp"


def test_a_curated_pick_is_left_alone(wearing):
    put, conn = wearing
    put("/media/from-the-shelf.webp", registry=(None, "curated_library"))
    assert seed._restore_face(conn, "p_star", HANDLE) is False


def test_a_seeded_face_with_an_OWNER_is_left_alone(wearing):
    """An owner account on the row means somebody claimed it, whatever the
    source says about how it was made."""
    put, conn = wearing
    put("/media/claimed.webp", registry=("acct_7", "seeded"))
    assert seed._restore_face(conn, "p_star", HANDLE) is False


def test_a_face_with_no_provenance_at_all_is_left_alone(wearing):
    """Silence is the right answer for a face this cannot account for."""
    put, conn = wearing
    put("/media/who-knows.webp")
    assert seed._restore_face(conn, "p_star", HANDLE) is False


def test_a_live_portrait_path_is_not_stale(wearing):
    """The file is right there. Nothing to repair."""
    put, conn = wearing
    put(avatars.asset_path(HANDLE))
    assert seed._restore_face(conn, "p_star", HANDLE) is False


def test_a_blank_face_is_the_other_functions_job(wearing):
    """`_backfill` fills blanks; this one replaces wrong ones. Two jobs,
    and neither should quietly do the other's."""
    put, conn = wearing
    put(None)
    assert seed._restore_face(conn, "p_star", HANDLE) is False


def test_a_starter_with_no_shipped_portrait_is_never_touched(wearing):
    put, conn = wearing
    put("/media/holo.webp", registry=(None, "seeded"))
    assert seed._restore_face(conn, "p_star", "nobody_ships_this") is False


def test_the_shipped_collection_is_photographs_not_holograms():
    """The repository's own side of the report. A hologram on a live box
    is deployed DATA — every file here is a warm photograph, which is why
    the repair belongs in the seed and not in the asset tree."""
    from PIL import Image
    for handle in ("dr_amara_osei", "marcus_bell", "aisha_diallo"):
        path = avatars.portraits_dir() / f"{handle}.webp"
        im = Image.open(path).convert("RGB").resize((32, 32))
        at = im.load()
        px = [at[x, y] for y in range(32) for x in range(32)]
        red = sum(p[0] for p in px) / len(px)
        blue = sum(p[2] for p in px) / len(px)
        assert blue - red < 12, f"{handle} reads as a cyan render"


def test_the_restore_runs_at_startup_not_only_on_the_button(client):
    """The mistake this file was one step away from repeating.

    `repair()`'s own docstring records it: a repair that only runs when
    somebody presses the seed button is a repair nobody runs, and a
    deployment sat on initials for weeks because of that. Wiring the
    restore into `seed()` alone would have left every hologram waiting
    for a press by an operator who does not know the button is a repair.
    """
    from qrme import seed as seeding

    seeding.seed()
    conn = db.connect()
    row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                       (HANDLE,)).fetchone()
    conn.execute("UPDATE profiles SET avatar='/media/old-hologram.webp'"
                 " WHERE id=?", (row["profile_id"],))
    conn.execute(
        "INSERT INTO avatar_registry (id, owner_account_id, source, provider,"
        " asset, rights, status, created_at)"
        " VALUES ('reg_holo',NULL,'prompted','internal',"
        "'/media/old-hologram.webp','{}','active',?)", (db.utcnow(),))
    conn.commit()

    out = seeding.repair()
    assert f"{HANDLE} (face)" in out["repaired_handles"]
    now = conn.execute("SELECT avatar FROM profiles WHERE id=?",
                       (row["profile_id"],)).fetchone()["avatar"]
    assert now == avatars.asset_path(HANDLE)
