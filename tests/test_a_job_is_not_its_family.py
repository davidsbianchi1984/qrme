"""A position says what it does, not what field it is in.

The pool holds 45,153 positions. 529 were written by hand; the rest came
in as titles from published taxonomies and take their skills from one of
sixteen families. Sixteen lists for forty-five thousand jobs is not a
detail of the data — it is what a founder reads on the screen:

    Commercial Housekeeper   order taking, stock rotation, till
                             reconciliation, allergen awareness
    Animal Caregiver         case note writing, risk flagging, referral
                             drafting, crisis services
    Attending Radiologist    patient history intake, clinical note
                             writing, triage by severity

    asked     which family is this job in
    mattered  what does *this* job do

A **group** is the tier between the two — the shape of the work rather
than the field, because shape is what the imported titles vary by. One
family, Skilled trades, holds 3,745 operators, 1,121 technicians, 490
mechanics and 335 installers, and those do different work at a keyboard
whatever they are working on.

## What this guard holds

That every group is reachable and furnished, that the shipped pool was
built from the rules as they stand, that the narrow rule wins over the
broad one, that a group never speaks over a role somebody wrote by hand,
and that coverage only rises.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from qrme import occupations

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from occupation_groups import RULES, SPECIFICS, group_of  # noqa: E402

DATA = json.loads((ROOT / "qrme/data/occupations.json").read_text(encoding="utf-8"))
RECORD = Path(__file__).with_name("occupation_coverage.txt")


def _recorded() -> tuple[int, int]:
    for line in RECORD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"COVERED\s+(\d+)\s+of\s+(\d+)", line.strip())
        if m:
            return int(m.group(1)), int(m.group(2))
    raise AssertionError(f"{RECORD.name} records no COVERED line")


def test_every_group_is_furnished_and_every_furnishing_is_reachable():
    """A group with no skills has nothing to add; specifics no rule
    reaches are a paragraph nobody will ever read."""
    named = [name for name, _ in RULES]
    assert len(named) == len(set(named)), "a group is declared twice"
    assert set(named) == set(SPECIFICS), (
        "RULES and SPECIFICS disagree: "
        f"{sorted(set(named) ^ set(SPECIFICS))}")
    for name, spec in SPECIFICS.items():
        assert spec["s"] and spec["c"], f"{name} names no skills or nobody"


def test_no_rule_is_dead():
    """A rule that claims nothing is a rule that was never right.

    Ordered rules make this easy to get wrong: a narrow group placed after
    a broad one matches nothing at all and looks fine in the file.
    """
    claimed = {r.get("g") for r in DATA["positions"]}
    dead = [name for name, _ in RULES if name not in claimed]
    assert not dead, (
        f"{len(dead)} group(s) claim no position in the shipped pool — "
        "either the rule is wrong or a broader rule above it gets there "
        f"first: {dead}")


def test_the_shipped_pool_was_built_from_these_rules():
    """The data and the rules cannot drift apart.

    Editing the rules without rebuilding leaves a pool that disagrees with
    the file describing it, and every reader believes the file.
    """
    wrong = [(r["t"], r.get("g"), group_of(r["t"]))
             for r in DATA["positions"]
             if not r.get("w") and r.get("g") != group_of(r["t"])]
    assert not wrong, (
        f"{len(wrong)} position(s) carry a group the rules no longer give "
        "them. Rebuild: python3 tools/build_occupations.py\n    "
        + "\n    ".join(f"{t}: shipped {had!r}, rules say {now!r}"
                        for t, had, now in wrong[:10]))


def test_the_narrow_rule_wins():
    """`Animal Caregiver` is an animal job whose title contains the word
    every human-care rule is keyed on. It read as Personal care — case
    notes, referral drafting, crisis services — until Animal care was
    ordered above it. Order is the whole mechanism, so it is tested.
    """
    assert group_of("Animal Caregiver") == "Animal care"
    assert group_of("Caregiver") == "Personal care"
    assert group_of("Pet Groomer") == "Animal care"
    assert group_of("Nursing Assistant") == "Personal care"


def test_a_rank_is_the_last_thing_a_title_is_read_as():
    """Supervision and management may only claim what nothing else did.

    It is a rank, not a shape, and a rank is what a title gets when
    nothing knows the work. `Nursing Supervisor` landed there on the
    first run — 23 nursing titles did — which was a gap in the groups
    above it rather than a placement error. A title reaching the rank
    rule is worth reading as a missing group, so the pairs below are
    pinned: the work wins, and the rank picks up what is genuinely only
    a rank.
    """
    assert group_of("Nursing Supervisor") == "Nursing"
    assert group_of("Nursing Assistant") == "Personal care"
    assert group_of("Veterinary nurse") == "Animal care"
    assert group_of("Machine Shop Supervisor") == "Supervision and management"
    assert RULES[-1][0] == "Supervision and management", (
        "the rank rule must stay last, or it takes titles a real group "
        "would have described")


def test_a_stem_does_not_swallow_a_different_word():
    """`commission*` claimed the commissioners.

    Thirty titles — Water Commissioner, Tax Commissioner, Insurance
    Commissioner, Health Commissioner — read as installation and
    commissioning because a stem was written where a word was meant.
    They are public officials and commission nothing.
    """
    assert group_of("Commissioning Engineer") == "Installation and commissioning"
    for official in ("Water Commissioner", "Tax Commissioner",
                     "Insurance Commissioner", "Health Commissioner"):
        assert group_of(official) != "Installation and commissioning", official


def test_the_clerical_rules_run_narrowest_first():
    """Eleven office titles end in the same word. `clerk*` is the bare
    one, so Records and filing is last of them; put it anywhere else and
    a payroll clerk, a file clerk and a data entry clerk are one job."""
    assert group_of("Payroll Clerk") == "Payroll and billing"
    assert group_of("Data Entry Clerk") == "Data entry and transcription"
    assert group_of("File Clerk") == "Records and filing"
    assert group_of("Claims Examiner") == "Claims and underwriting"
    assert group_of("Quality Control Inspector") == "Inspection and testing"


def test_instruction_is_read_before_its_subject():
    """Teaching is first of every rule.

    `Nursing Instructor` read as nursing and `Radiology Instructor` as
    imaging, because the care groups sit high and both titles name the
    subject being taught. Whoever it is about, instructing is the work:
    lesson plans and reports to parents, not observation charts.

    Training and coaching deliberately did not move with it.
    """
    assert group_of("Nursing Instructor") == "Teaching and instruction"
    assert group_of("Radiology Instructor") == "Teaching and instruction"
    assert group_of("Auto Mechanics Teacher") == "Teaching and instruction"
    assert group_of("Animal Trainer") == "Animal care"
    assert RULES[0][0] == "Teaching and instruction"


def test_the_operator_sense_of_engineer_stays_with_the_trades():
    """`engineer` is two words in these lists.

    A civil engineer designs; a locomotive engineer drives a train and a
    stationary engineer minds a boiler. The Engineering rule sits below
    the trades for exactly this, and the three operator senses are named
    on the groups that should hold them rather than left to placement.
    """
    assert group_of("Civil Engineer") == "Engineering"
    assert group_of("Software Engineer") == "Software and data"
    assert group_of("Locomotive Engineer") == "Driving and delivery"
    assert group_of("Stationary Engineer") == "Machine operation"
    assert group_of("Maintenance Engineer") == "Planned maintenance"


def test_a_coach_is_also_a_vehicle():
    """`coach*` is a token in no rule.

    As a stem it made every coach driver a trainer. Training and coaching
    names the human senses instead, and the vehicle keeps its driver.
    """
    assert group_of("Coach Driver") == "Driving and delivery"
    assert group_of("Life Coach") == "Training and coaching"
    # A token, not a substring: `life coach*` and `sports coach*` are the
    # human senses and are meant to be there. It is the bare stem that
    # swallows the vehicle.
    bare = [name for name, tokens in RULES
            if "coach*" in {tok.strip() for tok in tokens.split(",")}]
    assert not bare, f"a bare coach stem is back in {bare}; it takes the drivers"


def test_the_words_that_live_inside_machines():
    """Driving stays below Machine operation, and this is the cost.

    Lifting it above fixes four coach and bus operators and breaks six
    others, because `driver` and `delivery` appear inside the names of
    machines. The six are pinned so the trade cannot be made by accident
    later; the four are recorded as known-wrong in the coverage file.
    """
    assert group_of("Electric Screw Driver Operator") == "Machine operation"
    assert group_of("Delivery Table Feeder") == "Machine operation"
    assert group_of("Delivery Table Operator") == "Machine operation"
    assert group_of("Driver License Examiner") == "Inspection and testing"


def test_a_hairspring_is_a_watch_part():
    """The salon is written in phrases and never as a `hair*` stem.

    48 titles in the pool start a word with "hair" and the watchmaking
    ones outnumber the salon ones: Hairspring Inspector, Hairspring
    Truing Inspector, Balance and Hairspring Assembler. `Hair Boiler` is
    a rendering job. A stem would have taken all of them.
    """
    assert group_of("Hairspring Inspector") == "Inspection and testing"
    assert group_of("Balance and Hairspring Assembler") == "Assembly"
    assert group_of("Hair and Makeup Artist") == "Hairdressing and beauty"
    assert not any("hair*" in {tok.strip() for tok in tokens.split(",")}
                   for _, tokens in RULES), "a bare hair stem takes the watchmakers"


def test_a_cat_is_a_catalogue():
    """Animal care knows `dog` and not `cat`.

    Three letters, and the stem that would have been symmetrical takes
    every catalogue clerk with it. The animals it cannot name this way
    are worth less than the clerks it would cost.
    """
    assert group_of("Dog Walker") == "Animal care"
    assert group_of("Poultry Farmer") == "Animal care"
    assert group_of("Catalog Clerk") == "Records and filing"
    assert not any(tok.strip() in ("cat", "cat*")
                   for _, tokens in RULES for tok in tokens.split(","))


def test_the_process_shapes_sit_under_the_machine():
    """A title that is only a process and a material is what these are for.

    They sit below every other rule. "Bone Cutter" has nothing but the
    process; "Cutting Machine Operator" is being operated, and the run
    sheet is the work, so Machine operation keeps it.
    """
    assert group_of("Bone Cutter") == "Cutting and shaping"
    assert group_of("Abrasive Mixer") == "Mixing and batching"
    assert group_of("Cutting Machine Operator") == "Machine operation"


def test_a_rank_that_says_nothing_is_not_a_group():
    """Coverage is the ratchet's measure, not its goal.

    `technician`, `specialist`, `worker`, `assistant` and `associate` are
    the largest words left unclaimed, and grouping them would raise the
    number while making the answers worse: a group leads the merged row,
    so a Physician Assistant given "task list working" would lose the
    clinical phrases it has now.
    """
    empty = ("technician*", "specialist*", "worker*", "assistant*",
             "associate*", "consultant*", "professional*")
    named = {tok.strip() for _, tokens in RULES for tok in tokens.split(",")}
    assert not named & set(empty), (
        f"a rank that says nothing became a group: {sorted(named & set(empty))}")
    # A physician assistant is a clinician, and Clinical practice claims
    # it on `physician*` — the word that says the work, not the one that
    # says the rank. What must never happen is the row landing somewhere
    # on the strength of "assistant".
    assert group_of("Physician Assistant") == "Clinical practice"
    assert group_of("Executive Assistant") == "Secretarial and executive support"
    assert group_of("Research Assistant") == "Analysis and research"


def test_a_stem_is_checked_against_the_pool_before_it_is_written():
    """Four stems that looked obvious and were measured wrong.

    `tax*` takes the taxi drivers and the taxidermists. `fire*` takes
    the kiln firers. `server` takes the people who administer machines.
    `logger*` takes seven oil-well loggers for every four who fell trees.
    None is a token; the phrases that mean the job are.
    """
    assert group_of("Taxi Driver") == "Driving and delivery"
    assert group_of("Taxidermist") is None
    assert group_of("Kiln Firer") is None
    assert group_of("Server Administrator") is None
    assert group_of("Mud Logger") is None
    assert group_of("Firefighter") == "Fire and rescue"
    assert group_of("Tax Preparer") == "Finance and accounting"
    bare = {tok.strip() for _, tokens in RULES for tok in tokens.split(",")}
    assert not bare & {"tax*", "fire*", "server", "server*", "logger*"}


def test_the_field_shapes_sit_between_the_office_and_the_trades():
    """A legal secretary is a secretary; a deckhand is at sea.

    Below the office so `clerk` and `secretary` keep their titles, above
    the trades and the process shapes so a farm hand is on a farm and a
    deckhand is on a deck before either is a hand.
    """
    assert group_of("Legal Secretary") == "Secretarial and executive support"
    assert group_of("Tax Clerk") == "Records and filing"
    assert group_of("Farm Hand") == "Farming and growing"
    assert group_of("Deckhand") == "Marine and fishing"
    assert group_of("Deck Builder") == "Building and construction"


def test_a_group_never_speaks_over_a_written_role():
    """The 529 hand-written roles say more about themselves than a rule
    keyed on one word in a title ever can, so they take no group."""
    spoken_over = [r["t"] for r in DATA["positions"] if r.get("w") and r.get("g")]
    assert not spoken_over, spoken_over[:10]


def test_the_specific_half_leads_the_shared_half():
    """A group's skills come before its family's in the merged row.

    This is the same defect the family tier already had once: Radiologist
    carried its own specifics and showed six generic health-care skills,
    because the shared half led. A tier that lands behind the generic one
    is a tier nobody sees.
    """
    row = occupations.find("Commercial Housekeeper")
    assert row and row.get("group") == "Cleaning and housekeeping"
    lead = row["skills"][:len(SPECIFICS["Cleaning and housekeeping"]["s"])]
    assert lead == SPECIFICS["Cleaning and housekeeping"]["s"], lead
    assert "till reconciliation" not in lead


def test_a_phrase_two_tiers_share_is_shown_once():
    """`certificate issuing` is Skilled trades' and Inspection and
    testing's alike. Shown twice it reads as a bug in the app."""
    for row in occupations._pool():
        for field in ("skills", "connections"):
            assert len(row[field]) == len(set(row[field])), (
                f"{row['title']} repeats a {field[:-1]}: {row[field]}")


def test_coverage_only_rises():
    """The pool is too big to finish in one sitting; it can still be
    stopped from going backwards."""
    covered = sum(1 for r in DATA["positions"] if r.get("g"))
    total = len(DATA["positions"])
    was, was_of = _recorded()
    assert total >= was_of, (
        f"the pool shrank from {was_of} to {total} positions")
    assert covered >= was, (
        f"group coverage fell from {was} to {covered} of {total} "
        f"positions. If that is deliberate, say why under RAISED in "
        f"{RECORD.name} and record\n    COVERED  {covered}  of  {total}")
    if covered > was:
        raise AssertionError(
            f"coverage rose from {was} to {covered} of {total} "
            f"({100 * covered / total:.1f}%) — record it in "
            f"{RECORD.name}:\n    COVERED  {covered}  of  {total}")
