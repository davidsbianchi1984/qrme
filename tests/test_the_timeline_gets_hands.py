"""Raise — grow your own. Round two: the timeline gets hands.

docs/raise.md, build-order step three — the three time controls. Watch:
every Album entry lands on a day of the life's own calendar. Rewind:
a visit steps back to a lived day as read-only presence (the character
speaks as they were, teaching waits for the present), and a branch
copies the record into a second life raised differently — the original
never overwritten. Fast-forward: simulated days lived from the record
alone, growth at a discount, saved questions waiting when you return.
The sealed timeline (the full trail) refuses both rewinds: that door
is lived forward only.
"""

from __future__ import annotations

from pathlib import Path

from qrme import raising

REPO = Path(__file__).resolve().parents[1]
ENGINE = (REPO / "qrme" / "raising.py").read_text()
RAISE_TSX = (REPO / "app" / "src" / "screens" / "Raise.tsx").read_text()


def _begin(client, name="Pip", stage="child", preset="sandbox"):
    r = client.post("/raise", json={
        "owner_id": "acct_guardian", "display_name": name,
        "stage": stage, "preset": preset,
        "temperament": {"warm_reserved": -40},
        "verification": {"birthdate": "1984-05-01"},
        "terms_consent": True})
    assert r.status_code == 201, r.text
    out = r.json()
    return out["profile_id"], {"authorization":
                               f"Bearer {out['owner_token']}"}, out


# -- watch: the calendar ------------------------------------------------------

def test_a_life_begins_on_day_one_and_entries_carry_their_day(client):
    pid, head, out = _begin(client)
    assert out["character"]["sim_day"] == 1
    assert out["character"]["visiting_day"] is None
    client.post(f"/raise/{pid}/teach", headers=head,
                json={"teaching": "word", "what": "butterfly"})
    album = client.get(f"/raise/{pid}/album", headers=head).json()
    assert all(e["sim_day"] == 1 for e in album["entries"])


# -- fast-forward -------------------------------------------------------------

def test_fast_forward_lives_days_from_the_record_alone(client):
    pid, head, _ = _begin(client)
    client.post(f"/raise/{pid}/teach", headers=head,
                json={"teaching": "word", "what": "butterfly"})
    r = client.post(f"/raise/{pid}/forward", headers=head,
                    json={"days": 9})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["character"]["sim_day"] == 10
    # Testimony, not invention: every away entry is grounded in what
    # was actually taught — nothing is learned that nobody taught.
    for e in out["while_away"]:
        assert "butterfly" in e["note"] or "missed you" in e["note"]
    # And they save questions for you — come back to someone who
    # missed you.
    assert any(e["kind"] == "saved_question" for e in out["while_away"])


def test_an_untaught_life_waits_honestly(client):
    pid, head, _ = _begin(client)
    out = client.post(f"/raise/{pid}/forward", headers=head,
                      json={"days": 2}).json()
    assert all("waited for you" in e["note"] for e in out["while_away"])


def test_away_growth_is_discounted_and_the_album_keeps_highlights(client):
    """The balance rule: away time develops them slower than guardian
    time, and a long stretch writes highlights, not a diary."""
    pid, head, _ = _begin(client, stage="embryo")
    before = client.get(f"/raise/{pid}", headers=head).json()
    out = client.post(f"/raise/{pid}/forward", headers=head,
                      json={"days": 20}).json()
    # 20 days at the 1-per-2 discount: 10 points — half of what twenty
    # guardian words would have earned.
    assert (out["character"]["growth_points"]
            == before["growth_points"] + 10)
    assert len(out["while_away"]) <= 10
    # Days accrued still open doors: earned points are earned points.
    out = client.post(f"/raise/{pid}/forward", headers=head,
                      json={"days": 20}).json()
    assert out["stage_door"] is not None
    assert out["character"]["stage"] == "child"


def test_the_forward_cap_holds_everywhere_but_the_sandbox(client):
    pid, head, _ = _begin(client, preset="storybook")
    r = client.post(f"/raise/{pid}/forward", headers=head,
                    json={"days": 31})
    assert r.status_code == 422
    assert "thirty days" in r.json()["detail"]
    # The sandbox door has no cap — "unlimited fast-forward" is its
    # whole posture — and the Album still keeps only the highlights.
    pid2, head2, _ = _begin(client, name="Zip")
    out = client.post(f"/raise/{pid2}/forward", headers=head2,
                      json={"days": 200})
    assert out.status_code == 200
    assert out.json()["character"]["sim_day"] == 201
    assert len(out.json()["while_away"]) <= 10


# -- rewind as presence -------------------------------------------------------

def test_a_visit_rewinds_the_voice_to_the_lived_day(client):
    pid, head, _ = _begin(client)
    client.post(f"/raise/{pid}/teach", headers=head,
                json={"teaching": "word", "what": "butterfly"})
    client.post(f"/raise/{pid}/forward", headers=head, json={"days": 5})
    client.post(f"/raise/{pid}/teach", headers=head,
                json={"teaching": "word", "what": "telescope"})
    r = client.post(f"/raise/{pid}/visit", headers=head,
                    json={"sim_day": 1})
    assert r.status_code == 200, r.text
    assert r.json()["visiting_day"] == 1
    block = raising.prompt_block(pid)
    # The character speaks as they were: day one's knowledge, and the
    # visit said out loud — nothing past the visited day exists yet.
    assert "day 1 of your life" in block
    assert "butterfly" in block
    assert "telescope" not in block


def test_a_visit_is_presence_not_raising(client):
    """Read-only the whole way: teaching refuses, and a chat turn earns
    nothing — a past that accrued growth would not be the past."""
    pid, head, _ = _begin(client)
    client.post(f"/raise/{pid}/forward", headers=head, json={"days": 3})
    client.post(f"/raise/{pid}/visit", headers=head, json={"sim_day": 2})
    r = client.post(f"/raise/{pid}/teach", headers=head,
                    json={"teaching": "word", "what": "nope"})
    assert r.status_code == 422
    assert "teaching happens in the present" in r.json()["detail"]
    raising.turn_taken(pid)
    who = client.get(f"/raise/{pid}", headers=head).json()
    assert who["milestones"]["turns_together"] == 0


def test_coming_back_restores_the_present(client):
    pid, head, _ = _begin(client)
    client.post(f"/raise/{pid}/forward", headers=head, json={"days": 3})
    client.post(f"/raise/{pid}/visit", headers=head, json={"sim_day": 1})
    r = client.post(f"/raise/{pid}/visit", headers=head,
                    json={"sim_day": None})
    assert r.json()["visiting_day"] is None
    r = client.post(f"/raise/{pid}/teach", headers=head,
                    json={"teaching": "word", "what": "home"})
    assert r.status_code == 201, r.text


def test_a_visit_reaches_only_lived_days(client):
    pid, head, _ = _begin(client)
    r = client.post(f"/raise/{pid}/visit", headers=head,
                    json={"sim_day": 7})
    assert r.status_code == 422
    assert "a day this life has lived" in r.json()["detail"]


def test_the_sealed_timeline_is_lived_forward_only(client):
    """The full trail's whole posture: tombstones await, and no rewind
    softens them — visits and branches both refuse."""
    pid, head, _ = _begin(client, stage="adult", preset="full_trail")
    client.post(f"/raise/{pid}/forward", headers=head, json={"days": 3})
    r = client.post(f"/raise/{pid}/visit", headers=head,
                    json={"sim_day": 1})
    assert r.status_code == 422
    assert "sealed" in r.json()["detail"]
    r = client.post(f"/raise/{pid}/branch", headers=head,
                    json={"sim_day": 1, "display_name": "Echo"})
    assert r.status_code == 422


# -- rewind as a second life --------------------------------------------------

def test_a_branch_copies_the_days_and_never_touches_the_original(client):
    pid, head, _ = _begin(client)
    client.post(f"/raise/{pid}/teach", headers=head,
                json={"teaching": "word", "what": "butterfly"})
    client.post(f"/raise/{pid}/forward", headers=head, json={"days": 5})
    client.post(f"/raise/{pid}/teach", headers=head,
                json={"teaching": "word", "what": "telescope"})
    original = client.get(f"/raise/{pid}/album", headers=head).json()
    r = client.post(f"/raise/{pid}/branch", headers=head,
                    json={"sim_day": 3, "display_name": "Pip-Else"})
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["character"]["branch_of"] == pid
    assert out["character"]["sim_day"] == 3
    # The copy re-derives itself from the copied record alone: day-one
    # butterfly came along, day-six telescope did not, turns start over.
    assert out["character"]["milestones"]["words_taught"] == 1
    assert out["character"]["milestones"]["turns_together"] == 0
    bhead = {"authorization": f"Bearer {out['owner_token']}"}
    balbum = client.get(f"/raise/{out['profile_id']}/album",
                        headers=bhead).json()
    notes = " ".join(e["note"] for e in balbum["entries"])
    assert "butterfly" in notes and "telescope" not in notes
    assert balbum["entries"][-1]["kind"] == "branched"
    # "The original life is never overwritten" — its record byte-same.
    after = client.get(f"/raise/{pid}/album", headers=head).json()
    assert after == original


def test_branching_needs_the_unlocked_time_controls(client):
    pid, head, _ = _begin(client, preset="storybook")
    r = client.post(f"/raise/{pid}/branch", headers=head,
                    json={"sim_day": 1, "display_name": "Nope"})
    assert r.status_code == 422
    assert "unlocked time controls" in r.json()["detail"]
    # And a refused branch leaves no orphan profile — the creation
    # door's no-orphan discipline, kept by the branch door too.
    from qrme import db
    count = db.connect().execute(
        "SELECT COUNT(*) c FROM profiles WHERE display_name='Nope'"
    ).fetchone()["c"]
    assert count == 0


def test_a_childhood_day_branched_is_a_childhood_raised(client):
    """The law rides the branch: enter a childhood day and the second
    life is family forever, whichever way the original's door pointed —
    and it runs strict at the profile row like any childhood."""
    from qrme import db
    pid, head, _ = _begin(client, stage="child")
    client.post(f"/raise/{pid}/forward", headers=head, json={"days": 2})
    r = client.post(f"/raise/{pid}/branch", headers=head,
                    json={"sim_day": 1, "display_name": "Little"})
    made = r.json()["character"]
    assert made["started_stage"] == "child"
    assert raising.may_be_romantic(r.json()["profile_id"]) is False
    row = db.connect().execute(
        "SELECT maturity FROM profiles WHERE id=?",
        (r.json()["profile_id"],)).fetchone()
    assert row["maturity"] == "strict"


# -- the record stays append-only ---------------------------------------------

def test_the_time_controls_never_edit_the_record():
    """Round one's vault discipline survives round two: visits write
    nothing, branches only INSERT copies, and there is still no UPDATE
    or DELETE on growth_record anywhere in the engine."""
    assert "UPDATE growth_record" not in ENGINE
    assert "DELETE FROM growth_record" not in ENGINE


# -- the screen ---------------------------------------------------------------

def test_the_time_bar_stands_on_the_raise_screen():
    for needle in ("raise.time", "raise.visit.go", "raise.return",
                   "raise.forward.go", "raise.branch.go", "raise.away",
                   "raiseVisit", "raiseForward", "raiseBranch",
                   "visiting_day"):
        assert needle in RAISE_TSX, f"the Raise screen lost {needle}"
