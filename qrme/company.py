"""A digital company, built one employee at a time.

    asked     users start a digital company and fill positions with
              synthetic profiles trained for each — every department
              they can think of, any industry, then enter the business
              into the marketplace
    mattered  a company is not a batch job; it is a founder describing
              work, one role at a time, and signing what they described

## The interview is the training

Every hire begins as an interview the platform writes for the role. The
exemplar is the founder's own instrument — a role-mapping questionnaire
built years before this module for mapping transit personnel onto AI
assistants — and what generalises from it is not its questions but its
caliber: it asked a dispatcher about dispatch, in dispatch's own words.
So the model is shown the exemplar and writes an interview of that
caliber for THIS role in THIS industry, however many questions the role
needs. There is no fixed questionnaire, because there is no fixed job.

There is also no closed list. Industries, departments and titles are
whatever the founder types — the same rule the wearables catalogue
follows: suggestions are ink in a placeholder, never walls around it.

## What a signed interview becomes

The founder edits the drafted answers and signs. The signature is the
hire: a profile minted under the founder's own account, its persona
written from the interview, the interview itself filed into the
profile's source material (so every answer the employee ever gives can
ground on its own job description), connections wired to the colleagues
already hired, and a seat taken in the company's organization — the
existing department machinery, so a filled company coordinates the way
organizations already do.

## What an employee may not claim

A charter can carry duties whose performance is a licensed act or a
physical one. Those are marked `assists, does not perform` — the same
doctrine as the room-facing microphones: a refusal is a fact about the
product, and it is what keeps a marketplace of synthetic businesses
standing next to the AI marks and the VERIFIED plates.

## Oversight is ownership

Every employee belongs to the founder's account, so every owner control
that exists — the dials, the held replies, the memory shelf, the
transcript curation, the earnings ledger — applies to each employee
individually. The company is the folder that organises them; it grants
nothing new and hides nothing that exists.
"""

from __future__ import annotations

import json

from . import db, llm, organization
from .friends import befriend

MAX_HEADCOUNT = 50
MIN_HEADCOUNT = 1


class CompanyError(ValueError):
    """A founding or a hire that cannot stand."""


# A condensed cut of the exemplar — the founder's Houston Metro role-
# mapping questionnaire — shown to the model as the standard of caliber.
# Not a template: the model writes new questions in the role's own
# vocabulary, and this is only what "good" looks like.
EXEMPLAR = """\
Role overview: title, department, frontline/administrative/supervisory/
executive, supervises whom, the position in your own words.
Daily workflow: primary responsibilities and frequency; tools and
systems used; manual entries, reports, approvals handled; scheduling,
dispatch or inventory managed; incidents documented; the handoff and
escalation process when unavailable; recurring meetings and compliance.
Decision-making: which decisions are this role's own (routes, coverage,
approvals, budgets) and which are escalated, with a recent complex
decision and the data behind it.
Bottlenecks: the three most time-consuming weekly tasks; the redundant
or automatable ones; the pain points.
Manner: preferred interaction (voice, text, hybrid); whether a daily
activity summary is written."""

_TABLES = """
CREATE TABLE IF NOT EXISTS companies (
    id          TEXT PRIMARY KEY,
    owner_id    TEXT NOT NULL,
    org_id      TEXT NOT NULL,
    name        TEXT NOT NULL,
    industry    TEXT NOT NULL,
    headcount   INTEGER NOT NULL,
    shop_id     TEXT,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS company_seats (
    id          TEXT PRIMARY KEY,
    company_id  TEXT NOT NULL,
    title       TEXT NOT NULL,
    department  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open',   -- open | hired | retired
    interview   TEXT,                           -- drafted questions, JSON
    charter     TEXT,                           -- signed answers, JSON
    study       TEXT,                           -- the trade, in prose
    skills      TEXT,                           -- digital skills, JSON
    connections TEXT,                           -- who it must reach, JSON
    profile_id  TEXT,
    hired_at    TEXT
);
"""


#: Columns added after the table first shipped. A database founded
#: before them is still a database, so they are added when missing
#: rather than the schema being versioned for three text fields.
_LATER = ("study", "skills", "connections")


def _ensure(conn) -> None:
    conn.executescript(_TABLES)
    held = {r[1] for r in conn.execute("PRAGMA table_info(company_seats)")}
    for column in _LATER:
        if column not in held:
            conn.execute(
                f"ALTER TABLE company_seats ADD COLUMN {column} TEXT")


def found(owner_id: str, name: str, industry: str, headcount: int) -> dict:
    """Found a company: a named folder, an organization behind it, and
    `headcount` seats waiting to be described. Positions come later and
    freely — founding fixes only the size of the ambition."""
    name = (name or "").strip()
    industry = (industry or "").strip()
    if not name:
        raise CompanyError("a company needs a name")
    if not industry:
        raise CompanyError(
            "a company needs an industry — any industry, in your words")
    if not (MIN_HEADCOUNT <= headcount <= MAX_HEADCOUNT):
        raise CompanyError(
            f"headcount is between {MIN_HEADCOUNT} and {MAX_HEADCOUNT}")
    org = organization.create(owner_id, name)
    conn = db.connect()
    _ensure(conn)
    row = {
        "id": db.new_id("co"), "owner_id": owner_id, "org_id": org["id"],
        "name": name, "industry": industry, "headcount": headcount,
        "shop_id": None, "created_at": db.utcnow(),
    }
    conn.execute(
        "INSERT INTO companies (id, owner_id, org_id, name, industry,"
        " headcount, shop_id, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (row["id"], owner_id, org["id"], name, industry, headcount,
         None, row["created_at"]))
    conn.commit()
    return row


def get(company_id: str) -> dict | None:
    conn = db.connect()
    _ensure(conn)
    cur = conn.execute("SELECT * FROM companies WHERE id=?", (company_id,))
    r = cur.fetchone()
    return dict(r) if r else None


def list_for(owner_id: str) -> list[dict]:
    conn = db.connect()
    _ensure(conn)
    return [dict(r) for r in conn.execute(
        "SELECT * FROM companies WHERE owner_id=? ORDER BY created_at",
        (owner_id,))]


def seats(company_id: str) -> list[dict]:
    conn = db.connect()
    _ensure(conn)
    out = []
    for r in conn.execute(
            "SELECT * FROM company_seats WHERE company_id=? ORDER BY rowid",
            (company_id,)):
        row = dict(r)
        for field in ("interview", "charter", "skills", "connections"):
            row[field] = json.loads(row[field]) if row[field] else None
        out.append(row)
    return out


def add_seat(company: dict, title: str, department: str) -> dict:
    """One open position. Title and department are the founder's words —
    any job on Earth is a job here, and the count of seats never exceeds
    the headcount the founding declared."""
    title = (title or "").strip()
    department = (department or "").strip()
    if not title or not department:
        raise CompanyError("a seat needs a title and a department")
    conn = db.connect()
    _ensure(conn)
    standing = conn.execute(
        "SELECT COUNT(*) FROM company_seats WHERE company_id=?"
        " AND status != 'retired'", (company["id"],)).fetchone()[0]
    if standing >= company["headcount"]:
        raise CompanyError(
            f"the company was founded for {company['headcount']} — retire a "
            "seat or found larger")
    row = {"id": db.new_id("seat"), "company_id": company["id"],
           "title": title, "department": department, "status": "open"}
    conn.execute(
        "INSERT INTO company_seats (id, company_id, title, department,"
        " status) VALUES (?,?,?,?, 'open')",
        (row["id"], company["id"], title, department))
    conn.commit()
    return row


def _seat(company: dict, seat_id: str) -> dict:
    conn = db.connect()
    _ensure(conn)
    r = conn.execute(
        "SELECT * FROM company_seats WHERE id=? AND company_id=?",
        (seat_id, company["id"])).fetchone()
    if r is None:
        raise CompanyError("no such seat in this company")
    return dict(r)


def study_role(company: dict, seat_id: str, cloud=None) -> str:
    """The platform studies the trade before it writes the interview.

        asked     the platform goes online with the info given and
                  researches the occupation, its skills, the connections
                  needed, and the knowledge of its profession
        mattered  an interview written from model memory is a guess
                  about a job; a study is the job looked at

    The brief goes through `research.gather`, which owns the whole
    posture already: sanitized before it leaves, refused nothing while
    offline but answered by the local deterministic provider instead,
    and `llm.answered_by()` records who did the studying. The findings
    are stored on the seat, ground the interview, and — on hire — file
    into the employee's source material as the trade's own knowledge,
    so the hire arrives knowing its profession and every reply can
    ground on it.
    """
    from . import research
    seat = _seat(company, seat_id)
    brief = (
        f"The occupation: {seat['title']}, in the {seat['department']} "
        f"department of a small {company['industry']} business in the "
        "United States. Describe, concretely and in the trade's own "
        "vocabulary: what this role does day to day and how often; the "
        "skills a competent one carries; the tools of the trade; what it "
        "decides alone and what it escalates, and to whom; who it works "
        "with inside and outside the business; and the working knowledge "
        "of the profession a good one holds.")
    findings = research.gather(brief, cloud=cloud)
    conn = db.connect()
    _ensure(conn)
    conn.execute("UPDATE company_seats SET study=? WHERE id=?",
                 (findings, seat["id"]))
    conn.commit()
    return findings


#: How many of each the study may contribute. The card is read on a
#: phone, and a list long enough to scroll is a list nobody edits — which
#: is the whole point of putting it in front of the founder.
_MAX_FOUND_SKILLS = 8
_MAX_FOUND_CONNECTIONS = 6


def _tidy(items, cap: int) -> list[str]:
    """Short noun phrases, deduped case-blind, in the order given.

    A model asked for a list returns some of it as sentences, some
    capitalised, and some twice. None of those is a reason to throw the
    answer away — they are a reason to read it carefully.
    """
    out: list[str] = []
    seen: set[str] = set()
    for raw in items if isinstance(items, list) else ():
        text = " ".join(str(raw).strip().split())
        # A trailing full stop means it was written as a sentence; a long
        # one *is* a sentence, and a sentence is not a skill.
        text = text.rstrip(".").strip()
        if not text or len(text) > 60:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= cap:
            break
    return out


def _lead_with(found: list[str], pooled: list[str]) -> list[str]:
    """This job's own first, its family's behind, nothing said twice."""
    seen = {t.lower() for t in found}
    return found + [p for p in pooled if p.lower() not in seen]


def role_specifics(seat: dict, findings: str, cloud=None
                   ) -> tuple[list[str], list[str]]:
    """What *this* job needs, read out of the study that was just fetched.

        asked     skills and connections tailored to every profile, for
                  what they need for their particular job
        mattered  516 of 45,153 rows carry skills of their own; the rest
                  inherit their family's, so a browse of the whole table
                  read as sixteen jobs repeated

    The carried pool is exhaustive in titles and coarse in detail — that
    is the bargain that keeps it at 4.2 MB. The study is the opposite: it
    is about one job and it is prose. This turns that prose into the two
    lists the seat actually stores, so a radiologist's seat carries
    "prior study comparison" because the study said so and not because
    somebody wrote that row out by hand.

    It returns two empty lists rather than raising. Nothing reachable,
    a refusal, a shape that will not parse — every one of those leaves
    the pool's own answer standing, which is what was on screen before
    this existed and is still a true answer about the family.

    Entries stay records and coordination rather than acts. The charter
    every hire signs ends "duties that are licensed or physical acts are
    assisted, never performed", and a skill list reading "administers
    medication" would contradict the document the same profile carries.
    """
    if not findings or not findings.strip():
        return [], []
    system = (
        "You read a study of one occupation and extract two lists for a "
        "builder of synthetic employees. Answer ONLY as a JSON object "
        'with keys "skills" and "connections".\n\n'
        '"skills": what a competent one does with information in this '
        "job specifically — a record kept, a note written, a schedule "
        "made, a check reported, a document read. Never a licensed or "
        "physical act: this employee assists with those, it does not "
        "perform them. Never a generic office skill that would be true "
        "of any job.\n"
        '"connections": who and what this job must reach — the people, '
        "the departments, the outside bodies, the systems.\n\n"
        "Each entry is a short lowercase noun phrase of two to four "
        f"words, not a sentence. At most {_MAX_FOUND_SKILLS} skills and "
        f"{_MAX_FOUND_CONNECTIONS} connections. Fewer is better than "
        "padding: return only what this study actually supports.")
    ask = (f"Role: {seat['title']}\nDepartment: {seat['department']}\n\n"
           "THE STUDY:\n" + findings[:4000])
    try:
        raw = llm.get_provider(cloud=cloud).generate(
            system, [{"role": "user", "content": ask}])
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end <= start:
            return [], []
        parsed = json.loads(raw[start:end + 1])
        if not isinstance(parsed, dict):
            return [], []
        return (_tidy(parsed.get("skills"), _MAX_FOUND_SKILLS),
                _tidy(parsed.get("connections"), _MAX_FOUND_CONNECTIONS))
    except Exception:  # noqa: BLE001 — the pool's answer still stands
        return [], []


def study_seat(company: dict, seat_id: str, cloud=None) -> dict:
    """Download what this seat has to know, and hand it back to be read.

        asked     does the platform know the trade
        mattered  does the *founder* get to see what it knows before
                  signing somebody into the job

    `study_role` already went online and stored the prose. It ran inside
    `draft_interview`, silently, so the knowledge existed and nobody was
    ever shown it: the founder pressed one button and got questions,
    with no way to check whether the platform had understood the job at
    all before hiring against its understanding.

    This is that step made a step. It carries two halves that arrive
    differently. The working knowledge is the fetched half, and once
    fetched it is stored on the seat — which is what makes the hire
    offline from then on.

    The skills and the connections are themselves two halves. The pool
    the app carries answers for the *family*, and answers instantly with
    nothing reachable; `role_specifics` reads the study that was just
    fetched and answers for *this job*. The second leads and the first
    fills in behind, so the card is specific where the study was and
    never empty where it was not.

    `found` says whether the pool recognised the title. A seat the pool
    has never heard of is not an error and not a lesser seat: it studies
    the same way, it just starts from an empty list rather than a
    filled one.
    """
    from . import occupations
    seat = _seat(company, seat_id)
    known = occupations.find(seat["title"])
    if known is None:
        hits = occupations.search(seat["title"], limit=1)
        known = hits[0] if hits else None
    pooled_skills = list(known["skills"]) if known else []
    pooled_connections = list(known["connections"]) if known else []
    knowledge = study_role(company, seat_id, cloud=cloud)
    # What the study found about *this* job leads; the pool's answer,
    # which is true of the family, fills in behind it. Both halves are on
    # the card and both are editable, because the founder is the one who
    # knows which of them is right about their own store.
    found_skills, found_connections = role_specifics(
        seat, knowledge, cloud=cloud)
    skills = _lead_with(found_skills, pooled_skills)
    connections = _lead_with(found_connections, pooled_connections)
    conn = db.connect()
    _ensure(conn)
    conn.execute(
        "UPDATE company_seats SET skills=?, connections=? WHERE id=?",
        (json.dumps(skills), json.dumps(connections), seat["id"]))
    conn.commit()
    return {"seat_id": seat["id"], "title": seat["title"],
            "known_as": known["title"] if known else None,
            "family": known["family"] if known else None,
            "found": known is not None,
            "skills": skills, "connections": connections,
            # How many of the lists came from this job's own study rather
            # than its family. A founder reading a card of six generic
            # skills has no way to tell whether the study contributed
            # nothing or was never asked, and those are different.
            "tailored": len(found_skills) + len(found_connections),
            "knowledge": knowledge, "studied_by": _who_studied()}


def _who_studied() -> str | None:
    """Who answered the study, by name — the same record the letters'
    author line reads, so a founder can tell a real study from the local
    fallback standing in for one."""
    answered = llm.answered_by()
    return answered[0] if answered else None


def keep_study(company: dict, seat_id: str, skills: list[str],
               connections: list[str]) -> dict:
    """The founder's edits to what the study found.

    Review means being able to change it. A skill the pool suggested and
    this business does not want comes off; one it never thought of goes
    on. Nothing here hires anybody — that is still the signature.
    """
    seat = _seat(company, seat_id)
    clean_s = [s.strip() for s in skills if s and s.strip()][:60]
    clean_c = [c.strip() for c in connections if c and c.strip()][:60]
    conn = db.connect()
    _ensure(conn)
    conn.execute(
        "UPDATE company_seats SET skills=?, connections=? WHERE id=?",
        (json.dumps(clean_s), json.dumps(clean_c), seat["id"]))
    conn.commit()
    return {"seat_id": seat["id"], "skills": clean_s,
            "connections": clean_c}


def draft_interview(company: dict, seat_id: str, cloud=None) -> list[dict]:
    """The platform writes the interview for this seat — questions in the
    role's own vocabulary with suggested answers, at the exemplar's
    caliber. No model reachable is said plainly, and a small role-blind
    core is offered instead: a degraded interview that admits it is one
    beats a hidden failure wearing a good one's clothes."""
    seat = _seat(company, seat_id)
    findings = study_role(company, seat_id, cloud=cloud)
    system = (
        "You compose role interviews for a builder of synthetic employees. "
        "Shown below is the caliber expected — an exemplar's outline. Write "
        "8 to 14 questions for the role given, each in the role's own "
        "vocabulary, each with a plausible suggested answer for a small "
        "business of this industry. The first question is always the "
        "employee's full name (suggest one). Include at least one question "
        "about what this role decides alone versus escalates, and one about "
        "its handoff when unavailable. If any duty of this role is a "
        "licensed or physical act, add a question acknowledging it will be "
        "assisted, not performed. Answer ONLY as a JSON array of objects "
        'with keys "question" and "suggested".\n\nEXEMPLAR OUTLINE:\n'
        + EXEMPLAR)
    ask = (f"Industry: {company['industry']}\nCompany: {company['name']}\n"
           f"Department: {seat['department']}\nRole: {seat['title']}\n\n"
           "WHAT THE PLATFORM'S OWN STUDY OF THIS TRADE FOUND — ground "
           "every question in it:\n" + findings[:4000])
    questions: list[dict] | None = None
    try:
        raw = llm.get_provider(cloud=cloud).generate(
            system, [{"role": "user", "content": ask}])
        start, end = raw.find("["), raw.rfind("]")
        if start >= 0 and end > start:
            parsed = json.loads(raw[start:end + 1])
            if (isinstance(parsed, list) and parsed
                    and all(isinstance(q, dict) and q.get("question")
                            for q in parsed)):
                questions = [{"question": str(q["question"]),
                              "suggested": str(q.get("suggested", ""))}
                             for q in parsed[:20]]
    except Exception:
        questions = None
    if questions is None:
        questions = [
            {"question": "Full name of this employee:", "suggested": ""},
            {"question": f"Describe the {seat['title']} position in your "
                         "own words:", "suggested": ""},
            {"question": "Primary daily responsibilities and how often:",
             "suggested": ""},
            {"question": "What this role decides alone, and what it "
                         "escalates — and to whom:", "suggested": ""},
            {"question": "Its handoff when unavailable:", "suggested": ""},
            {"question": "Preferred manner: voice, text, or both:",
             "suggested": "both"},
        ]
    conn = db.connect()
    conn.execute("UPDATE company_seats SET interview=? WHERE id=?",
                 (json.dumps(questions), seat["id"]))
    conn.commit()
    return questions


def hire(company: dict, seat_id: str, answers: list[dict]) -> dict:
    """Sign the interview and the signature is the hire.

    The charter (question/answer pairs, the founder's edits included) is
    stored on the seat, written into the persona, and filed into the
    profile's source material so every reply can ground on the job it
    was hired to do. Colleagues already hired become connections, and
    the seat joins its department in the company's organization."""
    seat = _seat(company, seat_id)
    if seat["status"] == "hired":
        raise CompanyError("this seat is already filled — retire it first")
    kept = [{"question": str(a.get("question", "")).strip(),
             "answer": str(a.get("answer", "")).strip()}
            for a in answers
            if str(a.get("question", "")).strip()
            and str(a.get("answer", "")).strip()]
    if len(kept) < 3:
        raise CompanyError(
            "an interview this thin cannot train a position — answer at "
            "least the name, the duties and the authority")
    name = kept[0]["answer"][:60]

    from .models import ProfileCreate, Verification
    from .routers.profiles import create_profile
    from .seed import _BIRTHDATE

    lines = [f"{name} — {seat['title']}, {seat['department']} department, "
             f"{company['name']} ({company['industry']}).",
             "Hired by interview; the signed charter below is the job.", ""]
    lines += [f"Q: {qa['question']}\nA: {qa['answer']}" for qa in kept[1:]]
    lines += ["", "Duties that are licensed or physical acts are assisted, "
                  "never performed."]
    profile = create_profile(ProfileCreate(
        owner_id=company["owner_id"], kind="fictional", display_name=name,
        persona="\n".join(lines), purpose="creator_persona",
        verification=Verification(birthdate=_BIRTHDATE)))

    conn = db.connect()
    # The job, on the profile itself rather than only inside the charter it
    # was hired on. Every surface that draws a face draws the line under
    # the name from these two columns, and a hire whose title lives only in
    # a source item is a hire every one of those surfaces has to call
    # untitled.
    # "Head baker" alone leaves a reader asking where — the same question
    # the owner asked of a bare "Founder". The seat's title and the company
    # it is a seat AT go on one line, because that is how a person says it.
    conn.execute("UPDATE profiles SET job_title=?, industry=? WHERE id=?",
                 (f"{seat['title']}, {company['name']}",
                  company["industry"], profile["id"]))
    conn.execute(
        "INSERT INTO source_items (id, profile_id, kind, title, content,"
        " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,NULL,?)",
        (db.new_id("src"), profile["id"], "knowledge",
         f"The position: {seat['title']} ({company['name']})",
         json.dumps(kept, indent=1), db.utcnow()))
    if seat.get("study"):
        # The trade's own knowledge, filed beside the job description —
        # the hire arrives knowing its profession, provenance-counted
        # like every grounding already is.
        conn.execute(
            "INSERT INTO source_items (id, profile_id, kind, title, content,"
            " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,NULL,?)",
            (db.new_id("src"), profile["id"], "knowledge",
             f"The trade: {seat['title']}", seat["study"], db.utcnow()))

    # The colleagues: everyone already hired is a connection, because a
    # company whose employees are strangers to each other is an org chart,
    # not a staff.
    for other in seats(company["id"]):
        if other["status"] == "hired" and other["profile_id"]:
            try:
                befriend(profile["id"], other["profile_id"])
            except Exception:
                pass  # a duplicate link is not a failed hire

    org = organization.get(company["org_id"])
    if org is not None:
        try:
            organization.add_department(
                org, seat["department"], seat["title"],
                dict(conn.execute("SELECT * FROM profiles WHERE id=?",
                                  (profile["id"],)).fetchone()), None)
        except organization.OrganizationError:
            pass  # a full org is an org problem, not a lost employee

    conn.execute(
        "UPDATE company_seats SET status='hired', charter=?, profile_id=?,"
        " hired_at=? WHERE id=?",
        (json.dumps(kept), profile["id"], db.utcnow(), seat["id"]))
    conn.commit()
    return {"seat_id": seat["id"], "profile_id": profile["id"],
            "display_name": name}


def plan_company(company: dict, description: str, cloud=None) -> list[dict]:
    """Predict the roster a fully functioning business of this kind
    needs, from the founder's own words about what the store is meant
    to be. Suggestions, never walls: nothing here opens a seat — the
    founder taps the ones they want, and typing their own stays exactly
    as good."""
    from . import research
    description = (description or "").strip() or company["industry"]
    findings = research.gather(
        f"A small {company['industry']} business in the United States, "
        f"described by its founder as: {description}. What staff does a "
        "fully functioning one carry? For each role: its title, its "
        "department, and one line on why this business needs it.",
        cloud=cloud)
    raw = llm.get_provider(cloud=cloud).generate(
        "From the study below, answer ONLY as a JSON array of objects "
        'with keys "title", "department" and "why" — every role a fully '
        "functioning business of this kind carries, most essential "
        "first, at most the company's headcount of "
        f"{company['headcount']}.\n\nTHE STUDY:\n" + findings[:4000],
        [{"role": "user", "content": description}])
    import json as _json
    start, end = raw.find("["), raw.rfind("]")
    if start >= 0 and end > start:
        try:
            parsed = _json.loads(raw[start:end + 1])
            rows = [{"title": str(r.get("title", "")).strip()[:80],
                     "department": str(r.get("department", "")).strip()[:80],
                     "why": str(r.get("why", "")).strip()[:200]}
                    for r in parsed if isinstance(r, dict)]
            rows = [r for r in rows if r["title"] and r["department"]]
            if rows:
                return [_with_pool(r) for r in rows[:company["headcount"]]]
        except Exception:
            pass
    return _from_pool(company, description)


def _with_pool(row: dict) -> dict:
    """Attach what the pool knows about a role the model named.

    A suggested seat used to arrive as three strings and nothing else, so
    the founder chose a title without being told what the job would need.
    If the pool carries the role, its digital skills and connections come
    with it; if not, the row is unchanged and `study_seat` fills them in.
    """
    from . import occupations
    known = occupations.find(row["title"])
    if not known:
        found = occupations.search(row["title"], limit=1)
        known = found[0] if found else None
    if known:
        row = dict(row, skills=known["skills"],
                   connections=known["connections"], known_as=known["title"])
    return row


def _from_pool(company: dict, description: str) -> list[dict]:
    """The roster the app can answer with on its own.

    This is where "Industry lead / Front desk / Bookkeeper" used to be.
    Those three were what a founder saw whenever the study did not parse
    — most often on a deployment with no model to ask — and three canned
    strings are not a roster. The pool answers the same question offline,
    from the trade and the founder's own words, and the seats come with
    their skills and connections already on them.

    The headcount caps what a company may *open*, so it caps this list;
    it does not cap `occupations.for_trade`, which is a menu and is meant
    to show the roles the founder had not thought of.
    """
    from . import occupations
    rows = [
        {"title": row["title"], "department": row["family"],
         "why": "carried by a working " + company["industry"],
         "skills": row["skills"], "connections": row["connections"],
         "known_as": row["title"]}
        for row in occupations.for_trade(
            company["industry"], limit=company["headcount"],
            described=description)
    ]
    if rows:
        return rows
    # Only reachable with no pool file at all, and still better than a
    # blank screen: the trade itself, the front, and the books.
    return [
        {"title": company["industry"].title() + " lead",
         "department": "The trade",
         "why": "somebody has to do the thing the sign says"},
        {"title": "Front desk", "department": "Front of house",
         "why": "somebody answers whoever walks in"},
        {"title": "Bookkeeper", "department": "Back office",
         "why": "somebody counts what came in and went out"},
    ][:company["headcount"]]


def fill_seat(company: dict, seat_id: str, profile_id: str) -> dict:
    """Bring your own hire: an existing profile — the founder's, or a
    hybrid they blended — takes the seat. Same-account only, the rule
    the organization's own staffing keeps, and the seat's obligations
    do not change: colleagues connect, the department seats them, and
    the file says brought rather than interviewed."""
    seat = _seat(company, seat_id)
    if seat["status"] == "hired":
        raise CompanyError("this seat is already filled — retire it first")
    conn = db.connect()
    prof = conn.execute("SELECT * FROM profiles WHERE id=?",
                        (profile_id,)).fetchone()
    if prof is None or prof["owner_id"] != company["owner_id"]:
        raise CompanyError(
            "a seat takes a profile this company's founder holds")
    for other in seats(company["id"]):
        if other["status"] == "hired" and other["profile_id"]:
            try:
                befriend(profile_id, other["profile_id"])
            except Exception:
                pass
    org = organization.get(company["org_id"])
    if org is not None:
        try:
            organization.add_department(
                org, seat["department"], seat["title"], dict(prof), None)
        except organization.OrganizationError:
            pass
    conn.execute(
        "UPDATE company_seats SET status='hired', profile_id=?, hired_at=?"
        " WHERE id=?", (profile_id, db.utcnow(), seat["id"]))
    conn.commit()
    return {"seat_id": seat["id"], "profile_id": profile_id,
            "display_name": prof["display_name"], "brought": True}


def retire(company: dict, seat_id: str) -> dict:
    """The seat opens again; the profile stays the founder's to keep,
    repurpose or delete through the owner doors that already exist —
    retiring a seat is a staffing decision, not a deletion."""
    seat = _seat(company, seat_id)
    conn = db.connect()
    conn.execute("UPDATE company_seats SET status='retired' WHERE id=?",
                 (seat["id"],))
    conn.commit()
    return {"seat_id": seat["id"], "status": "retired"}


def publish(company: dict, tagline: str | None = None) -> dict:
    """Open for business: the company enters the marketplace inside the
    app.

        asked     users can enter their business into the digital
                  marketplace QRME offers
        mattered  a company that works only for its founder is a
                  rehearsal; the marketplace is the audience

    The storefront rides the shop rails that already exist — one shop,
    anchored on the first hire (the front desk), named for the company,
    tagged with its industry so Discover files it where people browse.
    Each department with hired staff becomes a service offering whose
    blurb names who answers, at no listed price: what a company charges
    is the founder's later decision on the offering, not a founding
    fee invented here. Publishing twice is an edit, like the shop rail
    it stands on; closing the storefront is `unpublish`, and the company
    keeps working privately either way.
    """
    from . import shops
    hired = [s for s in seats(company["id"])
             if s["status"] == "hired" and s["profile_id"]]
    if not hired:
        raise CompanyError("a company with nobody hired cannot open for "
                           "business")
    front = hired[0]["profile_id"]
    shop = shops.open_shop(front, company["name"],
                           tagline or company["industry"],
                           company["industry"][:60])
    standing = {o["title"] for o in shop.get("offerings", [])}
    by_dept: dict[str, list[str]] = {}
    for s in hired:
        who = (s["charter"] or [{}])[0].get("answer", s["title"])             if isinstance(s["charter"], list) else s["title"]
        by_dept.setdefault(s["department"], []).append(who)
    for dept, names in by_dept.items():
        if dept in standing:
            continue
        shops.add_offering(shop["id"], "service", dept,
                           "Ask for " + ", ".join(names[:3]), 0.0)
    conn = db.connect()
    conn.execute("UPDATE companies SET shop_id=? WHERE id=?",
                 (shop["id"], company["id"]))
    conn.commit()
    return shops.shop(shop["id"])


def unpublish(company: dict) -> dict:
    """The storefront comes down; the company keeps working. A status
    flip on the shop rail — listings only show what is open — so
    republishing later is the same edit it always was."""
    if not company.get("shop_id"):
        raise CompanyError("this company is not in the marketplace")
    conn = db.connect()
    conn.execute("UPDATE shops SET status='closed' WHERE id=?",
                 (company["shop_id"],))
    conn.execute("UPDATE companies SET shop_id=NULL WHERE id=?",
                 (company["id"],))
    conn.commit()
    return {"company_id": company["id"], "storefront": "closed"}

