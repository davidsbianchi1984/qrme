"""Offline mode said whether anything left. Nothing said who kept watching.

`qrme/offline.py` is the one function in the package that sees every outbound
host before it is reached — `test_nothing_leaves_the_host.py` holds every
socket site to consulting it — and it answered one question and forgot the
host. So a deployment could prove a given excursion was sanitized and could
not say that the same far end had now watched this household leave fourteen
times.

    asked     did anything leave the host
    mattered  who has watched us leave, and how often

A scrubber covers the first request. It does not cover the fifteenth being
read against the previous fourteen — same address, same rhythm, same set of
interests — which is a subject even when every field in every one of them was
stripped.

## What the guards here are for

Three of them are about what the ledger must *not* hold or hand over, because
a tool built to measure correlation is a tool that would be very good at
correlating people:

* the **path** never enters it — in the scrape case the path is the subject's
  handle, so a ledger keeping it is a second copy of the private thing in a
  table nobody thinks of as private;
* the **deployment-wide** view carries no profile at any depth, or it becomes
  a way for one owner to read what another owner's agent reads;
* an owner's own view is scoped like everything else that is theirs.

One is about the lever: a stand-down that is enforced at the route rather than
at the socket is one that every other caller of the fetcher walks past. The
test drives the fetcher directly, below every route, and expects the refusal
there.

And one is structural: a new outbound path either says whose errand it is or
is written down in `visits.UNATTRIBUTED` with a reason somebody read.
"""

import ast
import inspect
from pathlib import Path

import pytest

from qrme import offline, scrape, visits

REPO = Path(__file__).resolve().parent.parent


def _visit(profile_id=None, host="forum.example.com", what="the profile-page fetch"):
    visits.record(host, what, profile_id)


# --------------------------------------------------------------------------
# The thing itself.
# --------------------------------------------------------------------------

def test_a_far_host_is_counted_and_a_local_one_is_not(client, profile_id):
    """The ledger is about the far end. The loopback daemon and the on-prem
    vault are on this side of the wire and are not watching anybody, so
    recording them would be noise in the one place noise is expensive."""
    offline.allow("https://forum.example.com/threads/42",
                  "the profile-page fetch", profile_id)
    offline.allow("http://127.0.0.1:11434/api/tags",
                  "the local model daemon", profile_id)

    rows = client.get(f"/profiles/{profile_id}/visits").json()
    hosts = [r["host"] for r in rows]
    assert "forum.example.com" in hosts
    assert not any(h.startswith("127.") for h in hosts)


def test_the_path_never_enters_the_ledger(client, profile_id):
    """The line this whole feature turns on. `/@grandpa-joe` is the subject's
    handle; a ledger holding it would be a second copy of the private thing,
    sitting somewhere nobody audits."""
    offline.allow("https://social.example.com/@grandpa-joe",
                  "the profile-page fetch", profile_id)
    body = client.get(f"/profiles/{profile_id}/visits").text
    assert "grandpa-joe" not in body
    assert "social.example.com" in body


def test_going_back_is_what_the_row_reports(client, profile_id):
    """Not *you visited this* — *this one has seen you enough times to know
    you*. One row per host with a count, never one row per visit: a list of
    individual times is the movement log this feature exists to warn about."""
    for _ in range(visits.PERSISTENT_AFTER):
        offline.allow("https://forum.example.com/threads/42",
                      "the profile-page fetch", profile_id)
    row = next(r for r in client.get(f"/profiles/{profile_id}/visits").json()
               if r["host"] == "forum.example.com")
    assert row["times"] == visits.PERSISTENT_AFTER
    assert row["persistent"] is True
    assert row["first_seen"] and row["last_seen"]
    assert row["reasons"] == ["the profile-page fetch"]


def test_one_visit_is_not_yet_a_pattern(client, profile_id):
    offline.allow("https://once.example.com/x", "the profile-page fetch",
                  profile_id)
    row = next(r for r in client.get(f"/profiles/{profile_id}/visits").json()
               if r["host"] == "once.example.com")
    assert row["times"] == 1
    assert row["persistent"] is False


# --------------------------------------------------------------------------
# The lever, and where it is enforced.
# --------------------------------------------------------------------------

def test_a_stand_down_refuses_at_the_socket_not_at_the_route(client, profile_id):
    """Driven below every route, deliberately. A refusal that lived in the
    route above the fetcher would be one the chat path, the briefcase and any
    caller added tomorrow walk straight past."""
    assert client.post(f"/profiles/{profile_id}/visits/stand-down",
                       json={"host": "forum.example.com"}).status_code == 201

    with pytest.raises(offline.StoodDown):
        scrape.fetch("https://forum.example.com/threads/42", profile_id)

    # And the refusal names the host and the way back, rather than explaining
    # a setting this person never touched.
    with pytest.raises(offline.StoodDown) as caught:
        offline.allow("https://forum.example.com/x", "the profile-page fetch",
                      profile_id)
    assert "forum.example.com" in str(caught.value)
    assert "stand-down" in str(caught.value)


def test_a_stand_down_is_one_profiles_decision(client, profile_id):
    """It binds the profile that made it and nobody else. A host one household
    stops visiting is not a host the deployment stops visiting."""
    client.post(f"/profiles/{profile_id}/visits/stand-down",
                json={"host": "forum.example.com"})
    # Another profile's errand — here, none at all — is untouched.
    offline.allow("https://forum.example.com/x", "the profile-page fetch")


def test_lifting_it_starts_again_and_keeps_the_record(client, profile_id):
    offline.allow("https://forum.example.com/x", "the profile-page fetch",
                  profile_id)
    client.post(f"/profiles/{profile_id}/visits/stand-down",
                json={"host": "forum.example.com"})
    assert client.post(f"/profiles/{profile_id}/visits/lift",
                       json={"host": "forum.example.com"}).status_code == 200
    offline.allow("https://forum.example.com/y", "the profile-page fetch",
                  profile_id)
    row = next(r for r in client.get(f"/profiles/{profile_id}/visits").json()
               if r["host"] == "forum.example.com")
    # Lifting is not unremembering the visits that led to the decision.
    assert row["times"] == 2
    assert row["stood_down"] is False


def test_a_whole_url_is_accepted_where_a_host_is_meant(client, profile_id):
    """The thing a person has in their hand is the address they were shown."""
    client.post(f"/profiles/{profile_id}/visits/stand-down",
                json={"host": "https://forum.example.com/threads/42"})
    assert visits.stood_down(profile_id, "forum.example.com") is True


# --------------------------------------------------------------------------
# What each reader may see.
# --------------------------------------------------------------------------

def test_an_owner_reads_their_own_hosts_and_not_anybody_elses(
        client, profile_id):
    offline.allow("https://forum.example.com/x", "the profile-page fetch",
                  profile_id)
    r = client.get(f"/profiles/{profile_id}/visits",
                   headers={"authorization": "Bearer not-the-owner"})
    assert r.status_code in (401, 403), r.text


def test_the_deployment_wide_view_names_no_profile(client, profile_id):
    """The view that shows real correlation exposure — one address, several
    households, one far end seeing all of it — must not itself be the way one
    owner learns what another owner's agent reads."""
    offline.allow("https://forum.example.com/x", "the profile-page fetch",
                  profile_id)
    r = client.get("/visits/across")
    assert r.status_code == 200, r.text
    assert "forum.example.com" in r.text
    assert profile_id not in r.text
    for row in r.json():
        assert "profile_id" not in row
        assert "stood_down" not in row       # a stand-down belongs to somebody


def test_the_deployment_wide_view_is_the_operators(client, profile_id,
                                                   monkeypatch):
    monkeypatch.setenv("QRME_PROBLEMS_KEY", "sekret")
    # No bearer at all is a different answer from the wrong one, and the
    # profile owner's own token is the wrong one here — the deployment-wide
    # view is not something being an owner buys.
    assert client.get("/visits/across",
                      headers={"authorization": ""}).status_code == 401
    assert client.get("/visits/across").status_code == 403
    assert client.get("/visits/across",
                      headers={"authorization": "Bearer wrong"}).status_code == 403
    assert client.get("/visits/across",
                      headers={"authorization": "Bearer sekret"}).status_code == 200


# --------------------------------------------------------------------------
# The horizon.
# --------------------------------------------------------------------------

def test_old_detail_stops_existing(client, profile_id):
    """A log of when a household's agent goes online is the thing this module
    warns about. Keeping one forever in order to write the warning would be
    indefensible, so past the horizon only the fact survives."""
    from qrme import db
    conn = db.connect()
    for i in range(4):
        conn.execute(
            "INSERT INTO outbound_visits (id, profile_id, host, what, at)"
            " VALUES (?,?,?,?,?)",
            (f"vst_old{i}", profile_id, "forum.example.com",
             "the profile-page fetch", "2019-01-0%d T00:00:00+00:00" % (i + 1)))
    conn.commit()

    assert visits.fold_old() >= 3
    rows = [r for r in visits.for_profile(profile_id)
            if r["host"] == "forum.example.com"]
    # The host, and that it was reached, survive. The beat of it does not.
    assert rows and rows[0]["times"] == 1


# --------------------------------------------------------------------------
# And structurally, so it stays true after the next edit.
# --------------------------------------------------------------------------

def test_the_witness_sits_in_the_function_every_socket_already_passes():
    """`offline.allow` is the chokepoint the sibling guard already enforces.
    Recording anywhere else would be recording somewhere a new caller can miss.
    """
    src = inspect.getsource(offline.allow)
    assert "_witness" in src
    assert "_witness" in inspect.getsource(offline.allow_host)
    witness = inspect.getsource(offline._witness)
    assert "is_local" in witness, (
        "the ledger must skip local hosts — the loopback daemon is not "
        "watching anybody, and recording it is noise where noise is expensive")
    assert "stood_down" in witness, (
        "the stand-down is enforced here or it is enforced nowhere a second "
        "caller inherits")


def test_recording_can_never_be_why_a_fetch_fails():
    """A courtesy to the person reading later is not allowed to become an
    outage. Every failure inside `record` is swallowed on purpose."""
    body = ast.parse(inspect.getsource(visits.record))
    handlers = [n for n in ast.walk(body) if isinstance(n, ast.ExceptHandler)]
    assert handlers, "record() must not be able to raise into a caller"


def test_every_outbound_path_names_a_profile_or_is_written_down():
    """A new way out of the host either says whose errand it is, or is
    recorded in `visits.UNATTRIBUTED` with a reason. The middle case — a
    socket that could name a profile and does not — is the one that makes the
    ledger quietly useless and the stand-down quietly dead.
    """
    unattributed = set(visits.UNATTRIBUTED)
    loose = []
    for path in sorted((REPO / "qrme").rglob("*.py")):
        if path.name == "offline.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in ("allow", "allow_host")
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "offline"):
                continue
            what = node.args[1] if len(node.args) > 1 else None
            named = (isinstance(what, ast.Constant)
                     and what.value in unattributed)
            attributed = len(node.args) > 2 or node.keywords
            if not (named or attributed):
                where = getattr(what, "value", "<not a literal>")
                loose.append(f"{path.name}:{node.lineno}: {where!r}")
    assert not loose, (
        f"{len(loose)} outbound path(s) name no profile and are not recorded "
        "in visits.UNATTRIBUTED:\n    " + "\n    ".join(loose)
        + "\n  Pass the profile the errand belongs to, or write down why "
          "there is not one.")


def test_the_written_down_ones_still_exist():
    """A list of exemptions that has drifted from the code is worse than
    none — it makes the guard a statement about a dict rather than about the
    package."""
    reasons = set(visits.UNATTRIBUTED)
    found = set()
    for path in sorted((REPO / "qrme").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for reason in reasons:
            if f'"{reason}"' in text:
                found.add(reason)
    stale = sorted(reasons - found)
    assert not stale, (
        "recorded exemption(s) name an errand nothing does any more — strike "
        "them from visits.UNATTRIBUTED:\n    " + "\n    ".join(stale))
