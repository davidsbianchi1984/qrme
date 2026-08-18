"""Somebody's matter, from the moment they say it to the moment it is settled.

:mod:`qrme.privileges` opens by saying what this agent is for: it is not a
life-wide companion — that is JIM's shape — it exists to **get a person's
matter resolved**, something wrong with the app, with their synthetic profiles,
or with the platform. That paragraph has been true about the intent and false
about the code, because there was nowhere for a matter to live.

    asked     can somebody get their issue looked at
    mattered  can they find out afterwards what happened to it

What existed was three things that each answer a different question and none
of them this one:

* :mod:`qrme.help` answers *how does this work* and **writes nothing** —
  deliberately, and that stays true here. A question answered is not an issue
  resolved, and a help box has no memory of yours between two screens.
* ``routers/feedback`` takes ideas and praise into a suggestion box. Nobody
  replies to a suggestion box, and nothing is supposed to.
* ``routers/problems`` collects what *broke*, content-free, in counters, from
  the clients themselves. It never knows whose failure it was and must not.

A matter is the missing one: a person said something is wrong, and this is the
record that says so, what was done about it, and how it ended.

## The free answer runs first, and nothing it says closes anything

:func:`raise_it` puts the person's own words to :func:`qrme.help.ask` before
anything else, because most of what arrives at a support door is a question
with a written answer — and an answer that costs nothing and arrives now beats
a queue. Same ladder :mod:`jim.noticed` walks in the sibling product, in the
same order and for the same reason: free and local first.

**The help box answers; it does not settle.** The first draft of this module
let a recognised question open the matter already settled, and the first thing
run through it was *"my card was charged twice on tuesday"* — which came back
settled, by help, on the strength of a keyword. That matching is right for
what it was built for: a help box offering a paragraph about a topic is useful
when it is approximately right and costs a person nothing when it is wrong.
The same guess disposing of a billing complaint costs them the complaint, and
nobody finds out, because a settled matter is in nobody's queue.

So a matter with an answer waiting on it stands at ``answered`` — *here is
something, is that it* — and never at ``settled``. Only a person moves it
there: the raiser saying that was it, or somebody here having answered them.
That holds whether the sentence came from the written table or from a model,
and the second is why the line has to exist at all — ``help.ask`` reaches a
model where one is configured, and a generated sentence about the product
disposing of a real issue is the same failure with worse odds.

## It is raisable by somebody who cannot sign in

The remit says *within the app and outside the app*, and the hardest case in
that sentence is the person whose matter **is** that they cannot get in. An
issue tracker that needs an account is closed to exactly the people whose
issue is the account.

So a matter may be raised with no principal at all, and what comes back is a
**claim** — one string, shown once, never stored. The row keeps its hash, the
way :mod:`qrme.escalation` keeps the waiver's. Reading an anonymous matter back
takes that claim and nothing else opens it: not being the operator, not knowing
the id, not guessing. A signed-in raiser is found by who they are and is never
issued one, because a second secret is a second thing to lose.

## Nothing here exercises a power

The roster in :mod:`qrme.privileges` is where the agent's powers live — going
to read up, asking strangers, briefing a real professional. A matter can
**name** that one of them was used on it, and it cannot use one. A support
record that could also spend the person's grants would be a second door onto
every power in that roster, and the roster's whole argument is that there is
one door per power and the person stands in it.

So no row was added to the roster for this round. The remit did not need a new
power; it needed somewhere for the powers there to be pointed.

## Reading the queue is narrower than writing to it

Anyone may raise a matter — that is the point of a support door. Reading
*everyone's* matters is behind :func:`qrme.auth.require_reviewer`, the gate
that already fails closed and already guards objection review. This queue is
not the failure map: those are counters with nobody in them, and this is what
people wrote in their own words about their own accounts.
"""

from __future__ import annotations

import hashlib
import secrets

from . import db, help as helpbox

#: What a matter can be about, in the words the ask used: *their issues with
#: their app, synthetic profiles or platform*. A closed set so every client
#: says it in the reader's own language and the server composes no prose.
CONCERNS = ("app", "profiles", "platform")

#: Where a matter stands. ``answered`` is *the help box had something* and is
#: waiting on the person to say whether that was it — deliberately not
#: ``settled``, and :func:`raise_it` says why.
STANDINGS = ("open", "answered", "with_a_person", "settled")

#: Who settled it. Empty until somebody does.
SETTLED_BY = ("help", "a_person", "the_person", "")

#: What has been done to a matter. Closed, for the same reason as ``CONCERNS``
#: — and every step here is *recorded* by whoever did it through that thing's
#: own door. None of them is performed from this module.
STEPS = ("asked_help", "read_up", "asked_strangers", "briefed_a_person",
         "handed_to_a_person", "not_the_answer", "answered")


class MatterError(Exception):
    """A matter cannot be found, or the caller has no business with it."""


class NoSuchMatter(MatterError):
    pass


def _hash(claim: str) -> str:
    return hashlib.sha256(claim.encode("utf-8")).hexdigest()


def _row(matter_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM matters WHERE id=?", (matter_id,)).fetchone()
    if row is None:
        raise NoSuchMatter(matter_id)
    return dict(row)


def _step(matter_id: str, step: str, note: str = "") -> None:
    conn = db.connect()
    conn.execute(
        "INSERT INTO matter_steps (id, matter_id, step, note, stepped_at)"
        " VALUES (?,?,?,?,?)",
        (db.new_id("mst"), matter_id, step, note, db.utcnow()))
    conn.commit()


def _steps(matter_id: str) -> list[dict]:
    return [{"did": r["step"], "note": r["note"], "stepped_at":
             r["stepped_at"]}
            for r in db.connect().execute(
                "SELECT step, note, stepped_at FROM matter_steps"
                " WHERE matter_id=? ORDER BY stepped_at, rowid",
                (matter_id,)).fetchall()]


def _seen(row: dict) -> dict:
    """One shape, whether it was settled or not.

    Every key is present on both, because a payload that grows fields only
    when something happened hands four shells ``undefined`` on the case they
    meet most.
    """
    return {"id": row["id"], "concern": row["concerns"], "trouble": row["trouble"],
            "standing": row["standing"], "settled_by": row["settled_by"],
            "answer": row["answer"], "raised_at": row["raised_at"],
            "settled_at": row["settled_at"], "anonymous":
            row["raised_by"] == "anonymous", "trail": _steps(row["id"])}


def raise_it(trouble: str, concerns: str, raised_by: str = "anonymous") -> dict:
    """Somebody says something is wrong. Offer an answer now if there is one.

    Returns the matter, and — only for a raiser with no account — a ``claim``
    that will not be shown again. The caller is responsible for putting it in
    front of them once and not storing it either.
    """
    trouble = (trouble or "").strip()
    if not trouble:
        raise MatterError("nothing was said")
    if concerns not in CONCERNS:
        raise MatterError(concerns)

    # The free answer, before the record exists, so the matter is born
    # carrying whatever the help box had rather than being opened and amended
    # a line later.
    heard = helpbox.ask(trouble)
    recognised = bool(heard.get("recognised")) and not heard.get("refused")

    matter_id = db.new_id("mtr")
    claim = "" if raised_by != "anonymous" else secrets.token_urlsafe(24)
    conn = db.connect()
    conn.execute(
        "INSERT INTO matters (id, raised_by, claim, concerns, trouble,"
        " standing, settled_by, answer, raised_at, settled_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (matter_id, raised_by, _hash(claim) if claim else "", concerns,
         trouble, "answered" if recognised else "open", "",
         heard["answer"] if recognised else "", db.utcnow(), None))
    conn.commit()
    _step(matter_id, "asked_help",
          "the help box had an answer for this" if recognised
          else "the help box did not have this one")

    seen = _seen(_row(matter_id))
    # What help said when it did *not* recognise the question: a model's
    # sentence, or the fallback naming what this box covers. Offered rather
    # than filed — `offered` is not `answer`, and `answer` is only ever the
    # one somebody is being asked to accept.
    seen["offered"] = "" if recognised else heard["answer"]
    seen["claim"] = claim
    return seen


def read(matter_id: str, raised_by: str = "anonymous",
         claim: str = "") -> dict:
    """The matter, for the person whose matter it is.

    An anonymous one opens with the claim and with nothing else. Knowing the
    id is not enough and was never meant to be: ids travel in logs, in
    screenshots and in support threads, and what is behind this one is what
    somebody wrote about their own account.
    """
    row = _row(matter_id)
    if row["raised_by"] != "anonymous":
        if raised_by != row["raised_by"]:
            raise NoSuchMatter(matter_id)
    else:
        if not claim or not secrets.compare_digest(_hash(claim),
                                                   row["claim"]):
            raise NoSuchMatter(matter_id)
    return _seen(row)


def mine(raised_by: str) -> list[dict]:
    """Everything this person raised, newest first.

    Anonymous matters are unreachable here by construction rather than by a
    filter somebody could delete: they are keyed by a claim nobody holds a
    copy of, so there is no caller this could return them to.
    """
    if raised_by == "anonymous":
        return []
    return [_seen(dict(r)) for r in db.connect().execute(
        "SELECT * FROM matters WHERE raised_by=?"
        " ORDER BY raised_at DESC, rowid DESC", (raised_by,)).fetchall()]


def queue(standing: str = "") -> list[dict]:
    """Everything not settled, oldest first. For whoever is answering them.

    The default is *unsettled* rather than ``open``, and that is a correction
    rather than a preference. With ``open`` as the default the queue came back
    empty on a database holding two unanswered matters, because the help box
    finds something to say about nearly anything and both had gone straight to
    ``answered``. A support queue whose default view is empty while people are
    waiting is worse than no queue: it reports *nothing to do* to the person
    whose job is the doing.

    Pass a standing to narrow it. ``settled`` is the one thing the default
    leaves out, because that is the only standing where nobody is waiting.
    """
    if standing and standing not in STANDINGS:
        raise MatterError(standing)
    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM matters WHERE standing=? ORDER BY raised_at, rowid",
        (standing,)).fetchall() if standing else conn.execute(
        "SELECT * FROM matters WHERE standing<>'settled'"
        " ORDER BY raised_at, rowid").fetchall()
    return [_seen(dict(r)) for r in rows]


def not_it(matter_id: str) -> dict:
    """The raiser says the answer waiting on it was not the answer.

    Without this the person who got an irrelevant paragraph could only wait
    for somebody here to notice. Saying so is one press, it puts the matter
    back to ``open``, and the step stays on the record — a matter that was
    answered wrongly once is a different thing from one nobody ever answered,
    and the queue should be able to tell.
    """
    row = _row(matter_id)
    if row["standing"] != "answered":
        raise MatterError("there is no answer waiting on this")
    conn = db.connect()
    conn.execute("UPDATE matters SET standing='open', answer='' WHERE id=?",
                 (matter_id,))
    conn.commit()
    _step(matter_id, "not_the_answer", "")
    return _seen(_row(matter_id))


def took_it(matter_id: str) -> dict:
    """A person has picked this up. Said out loud so the raiser can see it.

    Somebody waiting on a support queue is mostly waiting to find out whether
    anybody is there. This is the smallest true thing that answers that, and
    it is a step rather than a message because a step is dated.
    """
    row = _row(matter_id)
    if row["standing"] == "settled":
        raise MatterError("already settled")
    conn = db.connect()
    conn.execute("UPDATE matters SET standing='with_a_person' WHERE id=?",
                 (matter_id,))
    conn.commit()
    _step(matter_id, "handed_to_a_person", "")
    return _seen(_row(matter_id))


def used(matter_id: str, step: str, note: str = "") -> dict:
    """Record that one of the roster's powers was exercised on this matter.

    Recorded, not exercised. The power runs behind its own door in
    :mod:`qrme.privileges`; this writes down that it ran, so the matter reads
    afterwards as an account of what was tried rather than a status that
    changed for reasons nobody kept.
    """
    _row(matter_id)
    if step not in STEPS:
        raise MatterError(step)
    _step(matter_id, step, note)
    return _seen(_row(matter_id))


def settle(matter_id: str, answer: str, by: str) -> dict:
    """Somebody settled it, and the answer is what settled it.

    ``by`` says which somebody. ``the_person`` is the raiser closing their own
    — the answer waiting on it was the answer, or they worked it out, or it
    stopped mattering — and that is a different fact from a person here having
    answered them, so it is stored rather than flattened into *closed*.

    ``help`` is a permitted value that nothing sets on its own: it records
    that the sentence the help box offered is what did it, which is worth
    being able to count and is not worth letting a keyword decide.
    """
    row = _row(matter_id)
    if by not in SETTLED_BY or not by:
        raise MatterError(by)
    if row["standing"] == "settled":
        raise MatterError("already settled")
    answer = (answer or "").strip()
    if not answer:
        raise MatterError("an answer is required to settle a matter")
    conn = db.connect()
    conn.execute(
        "UPDATE matters SET standing='settled', settled_by=?, answer=?,"
        " settled_at=? WHERE id=?", (by, answer, db.utcnow(), matter_id))
    conn.commit()
    _step(matter_id, "answered", "")
    return _seen(_row(matter_id))
