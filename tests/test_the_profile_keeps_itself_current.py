"""The lookout: a page the vault keeps fresh, and the profile speaks from
(qrme/lookout.py).

JIM's lookout watches a page for a person; this is the twin with the
payoff turned toward conversation: the watched pages' current captures
ride the chat prompt, dated and capped, so a persona whose menu changed
this morning speaks this morning's menu. The resident does the watching
from inside the facility; QRME never does, and what leaves QRME is the
URL once, at planting.

    asked     can a profile stay current on a page
    mattered  who does the watching, and where the page lives
"""

from __future__ import annotations

import json

from qrme import db, lookout, privileges

from tests.test_the_profile_remembers_by_meaning import (BrokenVault,
                                                         FakeResidentVault,
                                                         _chat)


class StandingVault(FakeResidentVault):
    """A PDI with standing tasks, the way `lookout` sees one."""

    def __init__(self):
        super().__init__()
        self.standing: dict[str, dict] = {}
        self.cancelled: list[str] = []
        self.runs: dict[str, list] = {}
        self._n = 0

    def resident_stand(self, goal, steps, every_hours):
        self._n += 1
        tid = f"rtk_{self._n:04d}"
        self.standing[tid] = {
            "id": tid, "goal": goal, "status": "planned",
            "every_hours": every_hours,
            "next_run_at": "2999-01-01T00:00:00+00:00",
            "plan_steps": steps}
        return dict(self.standing[tid])

    def resident_cancel(self, task_id):
        if task_id in self.standing:
            del self.standing[task_id]
            self.cancelled.append(task_id)
            return True
        return False

    def resident_tasks(self):
        return [dict(t) for t in self.standing.values()]

    def resident_runs(self, task_id):
        return list(self.runs.get(task_id, []))


class OlderVault(StandingVault):
    """A PDI from before standing tasks: the client answers None."""

    def resident_stand(self, goal, steps, every_hours):
        return None


def _allow_study(profile_id):
    privileges.choose(profile_id, "study_the_web", True)


def _plant(client, profile_id, url="https://example.com/menu", every=24.0):
    r = client.post(f"/profiles/{profile_id}/lookout",
                    json={"url": url, "every_hours": every})
    assert r.status_code == 201, r.text
    return r.json()


def _seal_capture(vault, task_id, text,
                  fetched="2026-08-19T09:00:00+00:00",
                  url="https://example.com/menu"):
    vault.records[lookout.capture_key(task_id)] = json.dumps(
        {"url": url, "text": text, "fetched_at": fetched})


# -- planting ----------------------------------------------------------------

def test_planting_needs_the_study_privilege(client, profile_id):
    """`study_the_web` defaults on (the sanitiser and visits ledger carry
    that decision), so the refusal is proven by switching it off: an
    owner who said no to the web said no to the watching too."""
    client.app.state.pdi = StandingVault()
    privileges.choose(profile_id, "study_the_web", False)
    r = client.post(f"/profiles/{profile_id}/lookout",
                    json={"url": "https://example.com", "every_hours": 24})
    assert r.status_code == 403, r.text
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM lookouts").fetchone()["n"] == 0


def test_a_lookout_is_one_standing_appointment_and_one_ledger_row(client,
                                                                  profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    out = _plant(client, profile_id)
    assert out["planted"] is True and out["next_run_at"]
    task = vault.standing[out["task_id"]]
    assert task["every_hours"] == 24.0
    assert task["plan_steps"] == [{"tool": "fetch.url",
                                   "args": {"url": "https://example.com/menu"}}]
    row = db.connect().execute(
        "SELECT * FROM lookouts WHERE profile_id=?",
        (profile_id,)).fetchone()
    assert row["task_id"] == out["task_id"]


def test_planting_is_honest_at_every_edge(client, profile_id):
    _allow_study(profile_id)
    client.app.state.pdi = None
    r = client.post(f"/profiles/{profile_id}/lookout",
                    json={"url": "https://example.com", "every_hours": 24})
    assert r.status_code == 422 and "no vault" in r.text
    client.app.state.pdi = OlderVault()
    r = client.post(f"/profiles/{profile_id}/lookout",
                    json={"url": "https://example.com", "every_hours": 24})
    assert r.status_code == 422 and "standing tasks" in r.text
    client.app.state.pdi = StandingVault()
    r = client.post(f"/profiles/{profile_id}/lookout",
                    json={"url": "ftp://example.com", "every_hours": 24})
    assert r.status_code == 422, r.text
    r = client.post(f"/profiles/{profile_id}/lookout",
                    json={"url": "https://example.com", "every_hours": 0.01})
    assert r.status_code == 422 and "quarter-hour" in r.text
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM lookouts").fetchone()["n"] == 0


# -- the list and the capture ------------------------------------------------

def test_the_list_carries_what_the_vault_says(client, profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    out = client.get(f"/profiles/{profile_id}/lookout").json()
    assert out["readable"] is True
    assert [w["status"] for w in out["lookouts"]] == ["planned"]
    client.app.state.pdi = BrokenVault()
    out = client.get(f"/profiles/{profile_id}/lookout").json()
    assert out["readable"] is False
    assert out["lookouts"][0]["id"] == planted["id"]
    assert out["lookouts"][0]["status"] is None


def test_the_capture_reads_back_from_the_seal(client, profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    _seal_capture(vault, planted["task_id"], "today's menu words")
    out = client.get(f"/profiles/{profile_id}/lookout/{planted['id']}"
                     "/page").json()
    assert out["readable"] is True
    assert out["text"] == "today's menu words"
    assert out["chars"] == len("today's menu words")
    missing = client.get(f"/profiles/{profile_id}/lookout/lkt_no/page")
    assert missing.status_code == 404


# -- the payoff: the profile answers from the capture ------------------------

def test_the_profile_answers_from_the_current_capture(client, profile_id,
                                                      interactor_id,
                                                      monkeypatch):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    _seal_capture(vault, planted["task_id"],
                  "Today's special is the lemon tart")
    seen = {}
    orig = lookout.prompt_block

    def spy(pid, pdi=None):
        out = orig(pid, pdi)
        seen["block"] = out
        return out

    monkeypatch.setattr(lookout, "prompt_block", spy)
    answered = _chat(client, profile_id, interactor_id,
                     "what is the special today")
    assert answered["profile_message"]["content"]
    assert "lemon tart" in seen["block"]
    assert "captured 2026-08-19" in seen["block"], (
        "a capture must ride the prompt wearing its date")


def test_an_unreadable_tandem_contributes_nothing_not_a_failure(client,
                                                                profile_id,
                                                                interactor_id):
    client.app.state.pdi = StandingVault()
    _allow_study(profile_id)
    _plant(client, profile_id)
    client.app.state.pdi = BrokenVault()
    answered = _chat(client, profile_id, interactor_id, "hello there")
    assert answered["profile_message"]["content"]
    assert lookout.prompt_block(profile_id, BrokenVault()) is None


def test_a_capture_rides_as_a_digest_not_an_archive(client, profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    _seal_capture(vault, planted["task_id"], "x" * (lookout.PROMPT_CAP * 5))
    block = lookout.prompt_block(profile_id, vault)
    assert block is not None
    assert len(block) < lookout.PROMPT_CAP * 2


# -- the drop and erasure ----------------------------------------------------

def test_dropping_stops_the_watching_the_whole_way(client, profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    _seal_capture(vault, planted["task_id"], "words")
    r = client.delete(f"/profiles/{profile_id}/lookout/{planted['id']}")
    assert r.status_code == 200, r.text
    assert r.json() == {"removed": True, "id": planted["id"]}
    assert vault.cancelled == [planted["task_id"]]
    assert lookout.capture_key(planted["task_id"]) not in vault.records
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM lookouts").fetchone()["n"] == 0


def test_a_down_tandem_keeps_the_row_on_the_list(client, profile_id):
    client.app.state.pdi = StandingVault()
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    client.app.state.pdi = BrokenVault()
    r = client.delete(f"/profiles/{profile_id}/lookout/{planted['id']}")
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["removed"] is False and "OSError" in out["why"]
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM lookouts").fetchone()["n"] == 1


def test_erasure_cancels_every_appointment_and_unseals_every_capture(client,
                                                                     profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    a = _plant(client, profile_id, url="https://example.com/a")
    b = _plant(client, profile_id, url="https://example.com/b", every=1.0)
    for planted in (a, b):
        _seal_capture(vault, planted["task_id"], "words")
    gone = client.delete(f"/profiles/{profile_id}?mode=erase")
    assert gone.status_code == 200, gone.text
    assert vault.standing == {}, "an appointment survived erasure"
    assert not any(k.startswith("resident/") for k in vault.records), (
        "a capture survived erasure")
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM lookouts WHERE profile_id=?",
        (profile_id,)).fetchone()["n"] == 0


# -- the change date rides everywhere the capture shows ----------------------

def test_the_list_and_the_page_say_when_the_page_changed(client, profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    vault.records[lookout.capture_key(planted["task_id"])] = json.dumps(
        {"url": "https://example.com/menu", "text": "words",
         "fetched_at": "2026-08-19T09:00:00+00:00",
         "changed_at": "2026-08-18T07:00:00+00:00"})
    row = client.get(f"/profiles/{profile_id}/lookout").json()["lookouts"][0]
    assert row["changed_at"] == "2026-08-18T07:00:00+00:00"
    got = client.get(f"/profiles/{profile_id}/lookout/{planted['id']}"
                     "/page").json()
    assert got["changed_at"] == "2026-08-18T07:00:00+00:00"
    block = lookout.prompt_block(profile_id, vault)
    assert "last changed 2026-08-18" in block


def test_a_capture_before_fingerprints_says_nothing_not_now(client,
                                                            profile_id):
    """A seal from before PDI carried change history has no changed_at;
    the list answers None rather than inventing a date."""
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    _seal_capture(vault, planted["task_id"], "words")
    row = client.get(f"/profiles/{profile_id}/lookout").json()["lookouts"][0]
    assert row["changed_at"] is None
    got = client.get(f"/profiles/{profile_id}/lookout/{planted['id']}"
                     "/page").json()
    assert got["readable"] is True and got["changed_at"] is None
    assert "last changed" not in lookout.prompt_block(profile_id, vault)


# -- the trouble line: why the watching last failed --------------------------

def test_the_list_says_why_the_watching_last_failed(client, profile_id):
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    vault.runs[planted["task_id"]] = [
        {"id": "rrun_2", "ran_at": "2026-08-19T10:00:00+00:00",
         "status": "failed", "note": "ResidentError: the wire is down"},
        {"id": "rrun_1", "ran_at": "2026-08-19T09:00:00+00:00",
         "status": "done", "note": "fetched 12 chars"},
    ]
    row = client.get(f"/profiles/{profile_id}/lookout").json()["lookouts"][0]
    assert row["trouble"] == "ResidentError: the wire is down"


def test_a_recovered_lookout_carries_no_stale_trouble(client, profile_id):
    """Only the *latest* round speaks: a lookout that failed yesterday
    and ran clean this morning is not in trouble."""
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    planted = _plant(client, profile_id)
    vault.runs[planted["task_id"]] = [
        {"id": "rrun_2", "ran_at": "2026-08-19T10:00:00+00:00",
         "status": "done", "note": "fetched 12 chars, sealed (unchanged)"},
        {"id": "rrun_1", "ran_at": "2026-08-19T09:00:00+00:00",
         "status": "failed", "note": "ResidentError: the wire is down"},
    ]
    row = client.get(f"/profiles/{profile_id}/lookout").json()["lookouts"][0]
    assert row["trouble"] is None


def test_an_older_vault_without_the_ledger_says_nothing(client, profile_id):
    class NoLedgerVault(StandingVault):
        resident_runs = None

    vault = NoLedgerVault()
    client.app.state.pdi = vault
    _allow_study(profile_id)
    _plant(client, profile_id)
    row = client.get(f"/profiles/{profile_id}/lookout").json()["lookouts"][0]
    assert row["trouble"] is None
