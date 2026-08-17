"""What the agent may do, chosen one at a time.

The product grew powers faster than it grew a place to see them. A profile can
go and study the open web, put a question to strangers, package a history for a
professional, run a job over vaulted material, and reach emergency services —
and a person who wanted to know *what can this thing actually do on my behalf*
had to read a changelog.

    asked     can the agent do this
    mattered  did the person decide it could, knowing what it costs

## What this agent is for, and what it is not

The agent here is not a life-wide companion that sits beside somebody all day
— that is JIM's shape, and JIM's rounds. This one exists to **get a person's
matter resolved**: something wrong with the app, with their synthetic profiles,
or with the platform, and increasingly matters that start there and end
somewhere outside it. Every row below is a power that serves *that* — going to
read up, asking somebody who knows, handing the matter to a real professional,
doing the job under a grant, and, when nothing else will do, reaching emergency
services.

It matters for what does *not* belong here. A row is added when this agent
needs it to finish somebody's matter, not because a sibling product has one.

## Three tables, three different questions

The word *capability* is already spoken for twice in this product, and neither
of those is this:

* :data:`qrme.tiers.CAPABILITIES` is **what the plan pays for**. It answers
  *is this account entitled to the feature at all*, and the refusal is a price.
* :data:`qrme.social.FEATURES` is **what the page shows** — ``messaging`` and
  ``homepage``, both defaulting *on*. Turning one off is a restriction a person
  applies to their own page.
* This module is **what the person has let the agent do**. It defaults *off*,
  granting one costs access to something, and the refusal is not a price — it
  is *nobody said yes to this*.

One table with a per-row default would hold all three, and that is exactly the
failure this module is shaped to prevent: it would let somebody add *watch my
screen* beside *homepage* with ``True`` in the same column and nothing to
notice. So they stay apart, and the rule that makes this one different is
enforced rather than remembered — see :func:`_defaults_are_honest` and the
guard that reads it.

## Three things every row says, in the person's words

**may_do** — what they are letting it do. Not a feature name; the sentence
they would use for it afterwards. It is drawn from the product's own closed
vocabulary, so it is translated wherever it is shown or refused with. Named
that way on the wire rather than ``asks``, which already means something else
there: the confirmation an agent stopped to ask for, which is an object rather
than a sentence. One name, one type.

**holds** — what it keeps, and that is the half a roster usually omits.
"Summarise your meetings" and "summarise your meetings, and keep the recording"
are different agreements, and only one of them is what the code does.

**touches_others** — whether exercising it reaches somebody who never chose it.
The other side of a call, a professional receiving a file, the stranger on a
board. It is a field rather than a paragraph because it has to be checkable:
anything true here can never default on, whatever else is true about it.

## The rule that is enforced rather than intended

A power that reaches people who did not choose it, or that keeps material
without a written reason, **is off until somebody turns it on**. Convenience
defaults are how a product ends up recording a room that did not agree to be
recorded, and the argument for one always sounds reasonable at the time.

## Nothing here is a label on an empty box

Every row names a power this product actually has, wired to the code that
exercises it through :func:`require`. A roster row for something unbuilt is a
dead control — the person says yes, and yes does nothing. New powers arrive
here in the round that builds them, not before.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import db, i18n


@dataclass(frozen=True)
class Privilege:
    """One thing the agent may be allowed to do."""

    name: str
    may_do: str                     # what the person is agreeing to
    holds: str = ""                 # what it keeps; empty means nothing
    needs: tuple[str, ...] = ()     # what access it requires
    touches_others: bool = False    # does exercising it reach somebody else
    default: bool = False
    why: str = ""                   # why the default is what it is


#: Every power the agent has, and what each one costs. Adding a row is a
#: decision made here, beside the defaults, rather than a string that quietly
#: becomes load-bearing somewhere else.
PRIVILEGES: dict[str, Privilege] = {p.name: p for p in (
    Privilege(
        "study_the_web",
        may_do="go and read up on something it does not know",
        holds="what it learned, as a knowledge source on the profile",
        needs=("the open web",),
        # The far end sees a request. It does not see the person, and the
        # visits ledger is what keeps that answerable over time.
        touches_others=False,
        default=True,
        why="the excursion sanitiser strips the owner's own terms before "
            "anything leaves and the visits ledger records where it went; "
            "this shipped before the roster existed, and switching it off "
            "under profiles already relying on it would be a change made to "
            "them rather than by them"),
    Privilege(
        "ask_people",
        may_do="put a question to strangers who can answer it",
        holds="answers the owner accepts, as a knowledge source",
        needs=("the open board",),
        # Whoever answers chose to answer. They are not captured by it.
        touches_others=False,
        default=False,
        why="a question on a public board is the owner's words in public, "
            "scrubbed but still theirs, and that is a decision rather than a "
            "setting"),
    Privilege(
        "brief_a_professional",
        may_do="catch a real person up on a matter before they step in",
        holds="nothing new — it sends what a grant already allows",
        needs=("a revocable grant", "somebody in your people"),
        touches_others=True,
        default=False,
        why="it puts a person's material in front of a third party; the grant "
            "decides what and the person decides who, and neither of those is "
            "a default"),
    Privilege(
        "reach_emergency_services",
        may_do="reach emergency services when it cannot resolve something",
        holds="the matter, and whether a call connected",
        needs=("a signed waiver",),
        touches_others=True,
        default=False,
        why="it can cost the person money and can put a stranger in a "
            "vehicle; the waiver is signed ahead and the last hop is sealed "
            "through the beta"),
    Privilege(
        "run_jobs",
        may_do="do a multi-step job over material the owner has granted it",
        holds="the job's finished output, watermarked",
        needs=("a revocable grant",),
        touches_others=False,
        default=False,
        why="autonomous work over vaulted material is the thing a person most "
            "wants to have said yes to explicitly"),
)}


class NotChosen(RuntimeError):
    """Refused: nobody has given this profile's agent this privilege.

    Raised rather than returned, for the reason :class:`qrme.offline.LeftTheHost`
    gives — a caller that could ignore the answer is a caller that will.
    """


def _defaults_are_honest() -> list[str]:
    """Rows whose default contradicts what they cost.

    Read by a guard rather than asserted at import, so the failure arrives with
    a test name that says what went wrong instead of a stack trace on a server
    that will not start. Anything that reaches people who did not choose it, or
    that keeps material with no written reason, is off until somebody turns it
    on.
    """
    return sorted(
        p.name for p in PRIVILEGES.values()
        if p.default and (p.touches_others or (p.holds and not p.why)))


def roster(profile_id: str) -> list[dict]:
    """Every privilege, what it costs, and whether this profile has it.

    The whole list every time, including the ones that are off. A roster that
    hides what has not been chosen is a roster nobody can choose from — and
    the visitor side of this route is the answer to *what can this profile
    actually do for me*, which was previously only discoverable mid-sentence.
    """
    on = {r["privilege"]: bool(r["chosen"]) for r in db.connect().execute(
        "SELECT privilege, chosen FROM chosen_privileges WHERE profile_id=?",
        (profile_id,)).fetchall()}
    return [{"name": p.name, "may_do": p.may_do, "holds": p.holds,
             "needs": list(p.needs), "touches_others": p.touches_others,
             "chosen": on.get(p.name, p.default), "by_default": p.default,
             "why": p.why}
            for p in PRIVILEGES.values()]


def chosen(profile_id: str, name: str) -> bool:
    """Whether this profile has this privilege, decision or default."""
    row = db.connect().execute(
        "SELECT chosen FROM chosen_privileges WHERE profile_id=?"
        " AND privilege=?", (profile_id, name)).fetchone()
    if row is not None:
        return bool(row["chosen"])
    privilege = PRIVILEGES.get(name)
    return bool(privilege and privilege.default)


def choose(profile_id: str, name: str, on: bool) -> list[dict]:
    """Say yes or no to one privilege, and get the whole roster back.

    A decision is written down even when it agrees with the default, so *never
    asked* and *considered and left alone* stay different states — the second
    is the one that survives a change of default.
    """
    if name not in PRIVILEGES:
        raise NotChosen(i18n.fill(i18n.MUST_BE_ONE_OF, field="privilege",
                                  choices=",".join(sorted(PRIVILEGES))))
    conn = db.connect()
    conn.execute(
        "INSERT INTO chosen_privileges (profile_id, privilege, chosen,"
        " decided_at) VALUES (?,?,?,?) ON CONFLICT (profile_id, privilege)"
        " DO UPDATE SET chosen=excluded.chosen, decided_at=excluded.decided_at",
        (profile_id, name, 1 if on else 0, db.utcnow()))
    conn.commit()
    return roster(profile_id)


def require(profile_id: str, name: str) -> None:
    """The chokepoint. Refuse unless this profile has been given this.

    One function, so a privilege cannot be exercised by a path that forgot to
    ask — the argument :func:`qrme.offline.allow` makes for sitting on every
    socket and :func:`qrme.tasks.scoped_items` makes for reading every grant.

    The refusal names the thing rather than the row, because *turn it on* is
    only actionable if the person knows which one, and because a token like
    ``run_jobs`` in a Portuguese sentence is the mixed refusal `i18n.Term`
    exists to prevent.
    """
    if chosen(profile_id, name):
        return
    privilege = PRIVILEGES.get(name)
    doing = privilege.may_do if privilege else name
    raise NotChosen(i18n.fill(i18n.PRIVILEGE_NOT_GIVEN, doing=i18n.Term(doing)))
