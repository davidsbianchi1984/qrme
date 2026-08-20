"""The weekly letter: a profile's week, written to its owner.

JIM's letter told a person what their own numbers meant; this is the
twin turned toward custody. An owner runs a synthetic profile that
talks to people, seals moments, studies topics and watches pages — and
the only way to know what kind of week it had was to open four screens.
The letter is the account rendered owed: composed **only from what the
week actually held** — a deterministic digest of the messages
exchanged, the moments sealed, the studies taken and what the watching
noticed — with no invented conversations and no editorializing. The
profile's own provider turns the digest into warm prose without adding
a single fact the digest doesn't carry (the voice that speaks all week
is the voice that reports on it, so the vault choice is honored here
too); when only the stub is standing, the digest itself is the letter,
plainly labeled. A week with nothing in it gets no letter — a letter
about an empty week would have to invent its contents.

    asked     what kind of week did the profile have
    mattered  an account rendered only on request is an account withheld
"""

from __future__ import annotations

import datetime as _dt

from . import db, llm, offline, research


class LetterError(Exception):
    pass


_PROSE_SYSTEM = (
    "You turn a factual digest of a profile's week into a short, warm "
    "letter addressed to the profile's owner. Use only the facts in the "
    "digest — never invent conversations, feelings, numbers or events "
    "the digest does not carry. No greeting-card filler; three or four "
    "honest sentences that tell the owner what their profile's week "
    "held. Answer with the letter only.")


def _week_window(now: str) -> tuple[str, str]:
    """The seven days ending now: (start_iso, start_date)."""
    end = _dt.datetime.fromisoformat(now)
    start = end - _dt.timedelta(days=7)
    return start.isoformat(), start.date().isoformat()


def _digest(profile_id: str, since: str) -> list[str]:
    """Plain-English lines for everything the week actually held — each
    line a fact from a table, none of them a judgement."""
    conn = db.connect()
    lines: list[str] = []

    row = conn.execute(
        "SELECT COUNT(*) AS n, COUNT(DISTINCT interactor_id) AS people"
        " FROM messages WHERE profile_id=? AND created_at>=?",
        (profile_id, since)).fetchone()
    if row["n"]:
        line = (f"{row['n']} message{'s' if row['n'] != 1 else ''}"
                f" with {row['people']}"
                f" {'people' if row['people'] != 1 else 'person'}")
        top = conn.execute(
            "SELECT i.display_name AS who, COUNT(*) AS n FROM messages m"
            " JOIN interactors i ON i.id=m.interactor_id"
            " WHERE m.profile_id=? AND m.created_at>=?"
            " GROUP BY m.interactor_id ORDER BY n DESC LIMIT 1",
            (profile_id, since)).fetchone()
        if top is not None and row["people"] > 1:
            line += f", most often with {top['who']}"
        lines.append(line)

    row = conn.execute(
        "SELECT COUNT(*) AS n FROM recollections WHERE profile_id=? AND"
        " created_at>=?", (profile_id, since)).fetchone()
    if row["n"]:
        lines.append(f"{row['n']} moment{'s' if row['n'] != 1 else ''}"
                     " sealed in the vault")

    studies = conn.execute(
        "SELECT topic FROM excursions WHERE profile_id=? AND created_at>=?"
        " ORDER BY created_at DESC", (profile_id, since)).fetchall()
    if studies:
        sample = "; ".join(s["topic"] for s in studies[:3])
        lines.append(f"{len(studies)}"
                     f" stud{'ies' if len(studies) != 1 else 'y'} taken,"
                     f" most recently: {sample}")

    # The asking: questions this profile put on the open board, and the
    # answers strangers left on them — the half of the studying that is
    # done by people, and as much a part of the week as the pages.
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM inquiries WHERE profile_id=? AND"
        " created_at>=?", (profile_id, since)).fetchone()
    if row["n"]:
        lines.append(f"{row['n']}"
                     f" question{'s' if row['n'] != 1 else ''}"
                     " asked on the open board")
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM inquiry_answers a JOIN inquiries q ON"
        " q.id=a.inquiry_id WHERE q.profile_id=? AND a.created_at>=?"
        " AND a.blocked=0", (profile_id, since)).fetchone()
    if row["n"]:
        lines.append(f"{row['n']}"
                     f" answer{'s' if row['n'] != 1 else ''} came back")
    return lines


def _watching_lines(profile_id: str, since: str, pdi) -> list[str]:
    """What the lookouts noticed this week — a changed page is a real
    event the owner asked to be told about, and a failing watch is a
    fact they should not have to open a task window to learn. No vault,
    or an unreached one, contributes nothing — the letter never fails
    for its least essential paragraph."""
    if pdi is None:
        return []
    from . import lookout as lookout_mod
    rows = db.connect().execute(
        "SELECT * FROM lookouts WHERE profile_id=? ORDER BY created_at,"
        " rowid", (profile_id,)).fetchall()
    lines: list[str] = []
    for r in rows:
        sealed = lookout_mod._capture(pdi, r["task_id"])
        changed = (sealed or {}).get("changed_at")
        if changed and changed >= since:
            lines.append(f"watched page {r['url']} changed on {changed[:10]}")
        if lookout_mod._trouble(pdi, r["task_id"]):
            lines.append(f"the watch on {r['url']} has been failing")
    return lines


def _week_names(profile_id: str, since: str) -> list[str]:
    """The people this week's digest may name — sanitize extras, the way
    the inquiry path passes its own. `research._private_terms` knows the
    profile's standing relationships; the digest also names whoever it
    merely messaged with this week, and those names must not leave
    either."""
    return [r["who"] for r in db.connect().execute(
        "SELECT DISTINCT i.display_name AS who FROM messages m"
        " JOIN interactors i ON i.id=m.interactor_id"
        " WHERE m.profile_id=? AND m.created_at>=?", (profile_id, since))]


def compose(profile_id: str, cloud=None, pdi=None) -> dict:
    """Write this week's letter from what the week actually held."""
    now = db.utcnow()
    since, week_start = _week_window(now)
    lines = _digest(profile_id, since) + _watching_lines(profile_id, since,
                                                         pdi)
    if not lines:
        raise LetterError("an empty week writes no letter")

    digest = "\n".join("- " + l for l in lines)
    body, described_by = digest, "digest"
    provider = llm.provider_for_profile(profile_id, cloud=cloud)
    # The letter is not the looser door. The study path sanitizes what
    # leaves and writes down that it left; the letter — carrying the
    # week's names, watched pages and counts — reached the same network
    # models with neither. Now a voice that would leave the host gets
    # the *sanitized* digest (the owner's own letter keeps the real
    # one), and `left_host` says what happened, in the excursions' own
    # word. The vault's voice and the local ones see the full digest —
    # nothing leaves, and the prose is better for it.
    choice = llm.resolve_choice(llm.get_choice(profile_id))
    # The vault's wire to PDI is the facility's own (`network: True` in
    # the registry, honestly — a socket opens), but the excursions set
    # the meaning of `left_host` and it means *left the facility*: the
    # vault branch is explicitly not-leaving there, so it is here.
    left_host = (choice != "vault" and not offline.enabled()
                 and llm.is_network(choice))
    outbound, redactions = (
        research.sanitize(profile_id, digest,
                          _week_names(profile_id, since))
        if left_host else (digest, 0))
    try:
        prose = (provider.generate(
            _PROSE_SYSTEM,
            [{"role": "user", "content": outbound}]) or "").strip()
    except Exception:  # noqa: BLE001 — a down provider never costs the letter
        prose = ""
    # The prose is the letter only when a real model wrote it: the stub,
    # or a degrade the FallbackProvider recorded, keeps the digest as the
    # body — plainly labeled rather than dressed up.
    inner = getattr(provider, "_primary", provider)
    who = llm.answered_by()
    spoke_locally = isinstance(inner, llm.StubProvider) or (
        who is not None and who[0] == llm.LOCAL_FALLBACK)
    if prose and not spoke_locally:
        body, described_by = prose, "model"

    conn = db.connect()
    letter_id = db.new_id("let")
    conn.execute(
        "INSERT INTO letters (id, profile_id, week_start, body,"
        " described_by, digest, left_host, redactions, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (letter_id, profile_id, week_start, body, described_by, digest,
         int(left_host), redactions, now))
    conn.commit()
    return {"id": letter_id, "week_start": week_start, "body": body,
            "described_by": described_by, "digest": lines,
            "left_host": left_host, "redactions": redactions}


def shelf(profile_id: str, limit: int = 12) -> list[dict]:
    """Past weekly letters, newest first, each carrying the digest the
    words were made from."""
    rows = db.connect().execute(
        "SELECT * FROM letters WHERE profile_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (profile_id, limit)).fetchall()
    return [{"id": r["id"], "week_start": r["week_start"], "body": r["body"],
             "described_by": r["described_by"],
             "digest": r["digest"].split("\n"),
             "left_host": bool(r["left_host"]),
             "redactions": r["redactions"],
             "created_at": r["created_at"]} for r in rows]
