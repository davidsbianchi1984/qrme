"""The objection was upheld, the profile erased — and the clone still sold.

## The finding

`_terminate` is thorough about content. It walks fourteen tables, deletes the
sealed source items out of the vault, clears the handle and the beacon so the
profile "cannot be re-summoned", and leaves a tombstone. Its docstring is about
reachability, and on reachability it was right.

It says nothing about *capabilities* — the tokens other people already hold.
Termination retires the owner's token, and every owner-gated route on a
terminated profile answers 401. So the profile reads as closed from every door
an audit is likely to try.

`POST /profiles/{id}/license/acquire` is authorised by the **buyer's**
interactor token, which termination never touches. Driven end to end, against
a profile whose subject had objected and whose objection had been upheld:

    resolve   200   {"status": "upheld", "profile_status": "terminated"}
    acquire   201   the licence sells, the fee credits to the owner
    derive    201   a new profile, seeded from the erased persona,
                    owned by the buyer, with its own owner token

    asked     can the owner still act on a terminated profile
    mattered  can anyone still act on it

The same hole one status over: a profile **restricted pending review** — the
one whose subject is arguing in that moment that it should not exist — could be
bought and cloned throughout the review. `succeed_profile` already refuses to
hand a contested identity to a new owner, and `has_open_objection` exists in
this very module for that check. Succession hands over the profile; derivation
hands over a *copy* of it, permanently, to a stranger, and never asked.

## The count

Seven tables carry a `profile_id` together with a revocation flag or a live
token — a capability somebody else holds over this profile. **Termination
touched none of them.** Not the licence, not the skill grant, not the handoff
package, not the paired wrist, not the voice consent, not the contribution log.

## Scope

This round stops new capabilities being exercised and retires the standing
ones. A profile *already* derived under a licence bought while the source was
active is left alone: it is its buyer's profile, with its own owner and its own
provenance line, and tearing it down is a different decision from this one.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from qrme import db, voiceprint, wearables

from tests.test_capabilities import as_owner, make_profile


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
GOVERNANCE = REPO / "qrme" / "routers" / "governance.py"

#: Tables that carry a third party's capability over a profile and are **not**
#: retired by termination, each with the reason. A list with reasons rather
#: than silence: seven tables sat outside the teardown and looked like six
#: deliberate decisions and one oversight, when they were seven oversights.
EXEMPT = {
    "referrals":
        "not a capability over the profile. A referral is the *interactor's* "
        "medical session released to a named clinician under that person's "
        "own signature; the profile is the specialist that assembled it. Its "
        "token is already one-time and burns on redemption. Terminating the "
        "AI profile must not reach into somebody's care and pull back a "
        "summary their clinician is holding.",
}


# --- the generalisation -----------------------------------------------------

def _capability_tables() -> list[tuple[str, list[str]]]:
    """Every table scoped to a profile that also carries a revocation flag or a
    live token — read from the schema the product actually creates, not from a
    list in this file, so a table added next release is in scope by
    construction."""
    conn = db.connect()
    out = []
    for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall():
        cols = [c["name"] for c in conn.execute(
            f"PRAGMA table_info({row['name']})")]
        if "profile_id" not in cols:
            continue
        marks = [c for c in cols
                 if "revok" in c or c in ("token", "token_hash")]
        if marks:
            out.append((row["name"], marks))
    return sorted(out)


def _terminate_source() -> str:
    src = GOVERNANCE.read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "_terminate")
    return ast.get_source_segment(src, fn) or ""


def _tables_terminate_touches() -> set[str]:
    """The tables `_terminate` writes to, read out of its own string literals.

    Bare words are the teardown loop's entries; the rest are statements, so
    both the `DELETE FROM x` and `UPDATE x SET revoked=1` shapes are found.
    Reading the literals rather than the function name means a table moved
    from one shape to the other stays covered.
    """
    fn = ast.parse(_terminate_source()).body[0]
    found: set[str] = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        text = node.value
        if re.fullmatch(r"\w+", text):
            found.add(text)
            continue
        found.update(re.findall(r"(?:UPDATE|DELETE FROM|INSERT INTO)\s+(\w+)",
                                text))
    return found


def test_termination_retires_every_capability_somebody_else_holds(client):
    """The generalisation. Naming the licence — the one I found by hand —
    would have left the other five standing."""
    touched = _tables_terminate_touches()
    left = [f"{name} ({', '.join(marks)})"
            for name, marks in _capability_tables()
            if name not in touched and name not in EXEMPT]
    assert not left, (
        f"{len(left)} table(s) leave a capability live on a profile that has "
        "been terminated at its subject's request — termination revokes the "
        "owner's token and these are held by somebody else:\n    "
        + "\n    ".join(left))


def test_the_capability_scan_is_finding_tables(client):
    """A guard on the guard: a scan that stopped matching would report nothing
    left behind and pass on an empty set."""
    found = _capability_tables()
    assert len(found) >= 7, (
        f"only {len(found)} profile-scoped capability table(s) found — this "
        "schema has seven, and the check above is passing on almost nothing")


def test_every_exemption_still_names_a_real_table(client):
    """An exemption for a table that no longer exists is a paragraph standing
    in front of nothing."""
    live = {name for name, _ in _capability_tables()}
    stale = sorted(t for t in EXEMPT if t not in live)
    assert not stale, (
        "these exemptions name tables that are no longer profile-scoped "
        "capabilities — strike them:\n    " + "\n    ".join(stale))


# --- driven -----------------------------------------------------------------

def _buyer(client, birthdate="1990-01-01"):
    who = client.post("/interactors", json={
        "display_name": "Buyer", "birthdate": birthdate}).json()
    return who["id"], {"authorization": f"Bearer {who['token']}"}


def _offered(client, kind="clone"):
    """A profile offered for licence, and the owner's client left authorised."""
    p = make_profile(client, persona="A master sommelier's palate and lore.")
    as_owner(client, p)
    r = client.put(f"/profiles/{p['id']}/license",
                   json={"kind": kind, "price": 20})
    assert r.status_code == 200, r.text
    return p["id"]


def _object(client, pid) -> str:
    r = client.post("/objections", json={
        "profile_id": pid, "objector_ref": "ref", "reason": "that is me"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _uphold(client, pid) -> None:
    obj = _object(client, pid)
    r = client.post(f"/objections/{obj}/resolve",
                    json={"outcome": "uphold", "rationale": "verified"})
    assert r.status_code == 200 and r.json()["profile_status"] == "terminated"


def test_a_terminated_profile_does_not_sell_a_licence(client):
    """The defect, driven. Before this round: 201, and the fee credited."""
    pid = _offered(client)
    _uphold(client, pid)
    _, hdr = _buyer(client)
    r = client.post(f"/profiles/{pid}/license/acquire", headers=hdr)
    assert r.status_code == 410, (
        f"expected 410 at the till on a terminated profile, got "
        f"{r.status_code} — 201 is the defect this round is about; a 404 means "
        "only the shop window came down, and the till is still open to any "
        "profile whose offer was never torn down (a departed one, say)")


def test_a_terminated_profile_is_not_cloned(client):
    """The consequence rather than the status code: the licence bought while
    the profile was live does not survive its termination either, so the sale
    that already happened cannot be cashed in afterwards."""
    pid = _offered(client)
    _, hdr = _buyer(client)
    grant = client.post(f"/profiles/{pid}/license/acquire", headers=hdr).json()
    assert grant["can_derive"] is True
    _uphold(client, pid)
    r = client.post(f"/profiles/{pid}/license/{grant['grant_id']}/derive",
                    headers=hdr)
    assert r.status_code in (403, 410), (
        f"a new profile was minted from a terminated one's persona "
        f"({r.status_code}), owned by the buyer, with its own owner token")


def test_a_licence_bought_before_the_objection_is_not_cashed_in_during_it(client):
    """The case only the gate at `derive` can catch, and it was missing.

    Removing that gate left all of this file green: the terminated path is
    stopped a second time by the grant revocation, and the contested path is
    stopped earlier at `acquire`. Neither reaches `derive` — so nothing
    exercised it, which is how the seven ungated routes looked fine in the
    round before this one.

    Here the licence was bought while the profile was active, so no revocation
    has happened and there is nothing left to buy. The buyer walks up with a
    valid grant in the middle of the review and mints a clone of the person who
    is contesting it.

        asked     was the licence still good
        mattered  was the profile still somebody's to license
    """
    pid = _offered(client)
    _, hdr = _buyer(client)
    grant = client.post(f"/profiles/{pid}/license/acquire", headers=hdr).json()
    _object(client, pid)                       # restricted, review open
    r = client.post(f"/profiles/{pid}/license/{grant['grant_id']}/derive",
                    headers=hdr)
    assert r.status_code == 403, (
        f"a clone was minted from a contested profile mid-review "
        f"({r.status_code})")
    assert "objection" in r.json()["detail"], (
        "refused, but for the wrong reason — this must be the objection, not "
        "the licence terms")


def test_the_standing_offer_goes_down_with_the_profile(client):
    """The shop window, independently of the gate at the till."""
    pid = _offered(client)
    _uphold(client, pid)
    left = db.connect().execute(
        "SELECT 1 FROM license_offers WHERE profile_id=?", (pid,)).fetchone()
    assert left is None, "a terminated profile is still offered for licence"


def test_a_contested_profile_is_not_bought_while_it_is_contested(client):
    """The subject is arguing this profile should not exist. It was for sale
    throughout the review."""
    pid = _offered(client)
    _object(client, pid)
    _, hdr = _buyer(client)
    r = client.post(f"/profiles/{pid}/license/acquire", headers=hdr)
    assert r.status_code == 403, r.text
    assert "objection" in r.json()["detail"]


def test_a_departed_profile_is_not_put_up_for_sale(client):
    """Sunset leaves the living owner their token, so the owner gate did not
    close this one — a memorial could be listed after the fact."""
    p = make_profile(client)
    as_owner(client, p)
    assert client.post(f"/profiles/{p['id']}/sunset").status_code == 200
    r = client.put(f"/profiles/{p['id']}/license",
                   json={"kind": "clone", "price": 20})
    assert r.status_code == 410, (
        f"a memorial was listed for licence ({r.status_code})")


def test_an_active_profile_still_sells_and_derives(client):
    """The gate refuses three statuses and must not touch the fourth."""
    pid = _offered(client)
    _, hdr = _buyer(client)
    grant = client.post(f"/profiles/{pid}/license/acquire", headers=hdr).json()
    r = client.post(f"/profiles/{pid}/license/{grant['grant_id']}/derive",
                    headers=hdr)
    assert r.status_code == 201, r.text
    assert r.json()["licensed_from"] == pid


def test_the_other_capabilities_are_retired_too(client):
    """Not only the one that was found by hand: a paired device and a voice
    consent are capabilities over the same profile, and both outlived it."""
    p = make_profile(client)
    as_owner(client, p)
    pid = p["id"]
    # Through the product's own entry points, so the rows are shaped the way
    # the product shapes them.
    wearables.pair(pid, "Wrist", "watch")
    voiceprint.consent(pid, own_voice=True, sources=None,
                       note="the owner's own voice")
    conn = db.connect()
    _uphold(client, pid)
    live = conn.execute(
        "SELECT (SELECT COUNT(*) FROM wearables WHERE profile_id=? AND"
        " revoked_at IS NULL) AS w,"
        " (SELECT COUNT(*) FROM voice_consents WHERE profile_id=? AND"
        " revoked_at IS NULL) AS v", (pid, pid)).fetchone()
    assert (live["w"], live["v"]) == (0, 0), (
        f"after termination {live['w']} device(s) are still paired and "
        f"{live['v']} voice consent(s) still stand")
