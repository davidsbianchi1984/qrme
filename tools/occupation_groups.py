"""The tier between a title and its family.

    asked     which family is this job in
    mattered  what does *this* job do

`title_families.py` files 44,624 imported titles into sixteen families, and
a family is where their skills come from. Sixteen lists for forty-five
thousand jobs means a browse of the pool reads as sixteen jobs repeated,
and worse than repetitive it is often wrong: `Commercial Housekeeper` lands
in Hospitality, food & retail and inherits "stock rotation" and "till
reconciliation"; `Animal Caregiver` lands in Mental health & social care
and inherits "referral drafting" and "crisis services".

A **group** sits between the two. It is not a field — the families already
carry the fields — it is a *shape of work*, which is what the imported
titles actually vary by. Skilled trades alone holds 3,745 operators, 1,121
technicians, 490 mechanics and 335 installers, and those four do different
work at a keyboard however similar their trade.

## How a group is matched

Exactly as a family is, and deliberately so: ordered rules, first match
wins, a token is a whole word or a phrase, a token ending in `*` is a stem.
The two files are read side by side often enough that a second syntax would
be a tax. `title_families._pattern` is the shared matcher.

## What a group does not do

It does not re-file anything. A title keeps the family it was given, and a
group only decides which specifics lead. That matters for the mis-filed
rows above: `Commercial Housekeeper` stays in Hospitality where the search
index expects it, and stops claiming it reconciles a till.

It also never outranks a written role. The 529 roles hand-written in
`occupation_spec.py` say more about themselves than any rule can, so the
merge order is own, then group, then family — the same order `_lead_with`
already uses for a seat's own skills against its family's.

## Coverage

This file is not finished and is not meant to be finished in one sitting.
`tests/occupation_coverage.txt` records the share of the pool a group
reaches; the guard on it only lets that number rise.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from title_families import _pattern  # noqa: E402

#: (group, comma-separated tokens). Ordered; the first match wins, so the
#: narrow shapes come before the broad ones. A group whose rule can never
#: fire is a guard failure, not a dead line.
RULES: list[tuple[str, str]] = [
    # -- care of a person, before anything that merely contains "care" ----
    ("Clinical imaging",
     "radiolog*, radiograph*, sonograph*, ultrasound, mammograph*, "
     "imaging, x-ray, xray, ct tech*, mri, nuclear medicine"),

    ("Laboratory work",
     "laboratory, lab tech*, phlebotom*, histolog*, cytolog*, patholog*, "
     "specimen, assay*, microbiolog*, serolog*, toxicolog*"),

    ("Animal care",
     "veterinar*, animal, kennel*, groomer*, zookeep*, stable*, equine, "
     "livestock, pet, aquarium*, wildlife"),

    ("Personal care",
     "caregiver*, care aide*, care assistant*, care worker*, "
     "home health aide*, personal care*, nursing assistant*, orderly, "
     "carer*, companion*, home aide*"),

    ("Nursing",
     "nurse*, nursing, midwife*, midwives, midwifery"),

    # -- keeping a place ---------------------------------------------------
    ("Cleaning and housekeeping",
     "housekeep*, janitor*, custodian*, cleaner*, cleaning, "
     "maid, chambermaid*, laundr*, dry clean*, window washer*, "
     "sanitation worker*"),

    ("Grounds and premises",
     "groundskeep*, landscap*, gardener*, greenskeep*, caretaker*, "
     "porter, doorman, doorkeeper*, concierge*"),

    # -- the office ------------------------------------------------------
    #
    # Ordered narrowest first among themselves, because most of these
    # titles end in the same word. A payroll clerk, a file clerk and a
    # data entry clerk are three jobs, and "clerk" alone would make them
    # one — so Records and filing, which is the one keyed on the bare
    # word, comes last of the clerical rules.
    #
    # Claims sits above Inspection and testing below: "Claims Examiner"
    # matches `examiner*` there, and a claims examiner examines a claim,
    # not a casting.
    ("Claims and underwriting",
     "claims, claim*, adjuster*, underwrit*, loss assessor*, "
     "loss adjuster*"),

    ("Payroll and billing",
     "payroll*, billing, biller*, invoic*, accounts payable, "
     "accounts receivable, bookkeep*, bursar*, collections clerk*, "
     "credit clerk*"),

    ("Purchasing and procurement",
     "purchasing, procurement, buyer*, expediter*, expeditor*, sourcing"),

    ("Human resources",
     "human resources, recruiter*, recruitment, staffing, personnel, "
     "benefits clerk*, benefits administrator*"),

    ("Reception and front desk",
     "receptionist*, front desk, front office, switchboard*, "
     "telephone operator*, information clerk*"),

    ("Secretarial and executive support",
     "secretary*, secretarial, administrative assistant*, "
     "executive assistant*, office assistant*, personal assistant*, "
     "admin assistant*, office manager*"),

    ("Customer service and call handling",
     "customer service, customer support, customer care, call cent*, "
     "contact cent*, help desk, helpdesk, telemarket*, telephone sales, "
     "complaint*"),

    ("Scheduling and booking",
     "scheduler*, scheduling, appointment*, reservation*, timekeeper*, "
     "booking*"),

    ("Data entry and transcription",
     "data entry, keypunch*, typist*, stenograph*, transcription*, "
     "transcriptionist*, word processor*, coding clerk*, medical coder*, "
     "medical coding"),

    ("Records and filing",
     "records clerk*, file clerk*, filing, archivist*, registrar*, "
     "record*, clerk*"),

    # -- the shapes that fill the trades -----------------------------------
    ("Machine operation",
     "machine operator*, operator*, tender*, setter*, feeder*, "
     "machinist*, press*, lathe*, mill operator*, extruder*, "
     "molder*, moulder*, caster*, winder*, roller*"),

    ("Repair and service",
     "repairer*, repair*, mechanic*, servicer*, service tech*, "
     "fitter*, overhauler*, rebuilder*, refurbish*"),

    # `commissioning`, not `commission*`: the stem claimed thirty titles
    # and most were commissioners — Water, Tax, Insurance, Health — who
    # are public officials and do not commission anything.
    ("Installation and commissioning",
     "installer*, installation, erector*, rigger*, splicer*, "
     "commissioning, fitter-out, glazier*"),

    ("Assembly",
     "assembler*, assembly, fabricator*, bench worker*, "
     "solderer*, welder*, brazer*"),

    ("Inspection and testing",
     "inspector*, checker*, tester*, examiner*, grader*, sorter*, "
     "quality control, quality assur*, calibrat*, metrolog*"),

    ("Planned maintenance",
     "maintenance, maintainer*, lubricat*, greaser*, oiler*, "
     "millwright*, facilities tech*"),

    ("Materials handling",
     "loader*, unloader*, packer*, palletiz*, palletis*, "
     "warehouse*, stockroom*, picker*, forklift*, hoist*, "
     "material handler*, freight handler*"),

    ("Driving and delivery",
     "driver*, chauffeur*, courier*, delivery, dispatcher*, "
     "haulier*, trucker*, rider*"),

    # -- last of all -------------------------------------------------------
    #
    # A rank, not a shape. `title_families.py` puts Business, people &
    # operations last for the same reason: supervisor, manager and
    # director say where a role sits, not what it does, so they may only
    # decide a title nothing else claimed.
    #
    # Last is necessary and is not sufficient. `Nursing Supervisor` landed
    # here on the first run — not because the rule was too high but
    # because no rule above it covered nursing at all, and a rank is what
    # you get when nothing knows the work. The answer was the Nursing
    # group, not a lower placement. A title arriving here is worth reading
    # as a gap in the groups above.
    ("Supervision and management",
     "supervisor*, manager*, director*, coordinator*, superintendent*, "
     "foreman, forewoman, chief"),
]

#: What each group's members do at a keyboard, and who they must reach.
#: Written the way `occupation_spec.py` writes a role: the specifics of the
#: shape, never the field — the family still supplies the field.
SPECIFICS: dict[str, dict[str, list[str]]] = {
    "Clinical imaging": {
        "s": ["study protocol selection", "image report dictation",
              "prior study comparison", "dose record keeping",
              "urgent finding escalation"],
        "c": ["referring clinicians", "imaging technologists",
              "picture archive", "on-call radiologist"]},
    "Laboratory work": {
        "s": ["specimen logging", "chain of custody records",
              "result validation", "instrument calibration logs",
              "abnormal result flagging"],
        "c": ["requesting clinicians", "specimen couriers",
              "quality assurance", "reference laboratory"]},
    "Personal care": {
        "s": ["care plan following", "daily activity logging",
              "change of condition reporting", "medication prompt records",
              "family update writing"],
        "c": ["the person cared for", "family and next of kin",
              "supervising nurse", "care coordinator"]},
    "Animal care": {
        "s": ["animal record keeping", "feeding and treatment logs",
              "welfare observation notes", "vaccination scheduling",
              "owner update writing"],
        "c": ["owners", "veterinary surgeon", "welfare inspectors",
              "feed and supply merchants"]},
    "Nursing": {
        "s": ["care plan writing", "observation charting",
              "medication administration records", "handover writing",
              "deterioration escalation"],
        "c": ["patients and families", "the responsible doctor",
              "ward and shift lead", "pharmacy"]},
    "Cleaning and housekeeping": {
        "s": ["room and area checklists", "cleaning schedule keeping",
              "chemical safety records", "linen and supply counts",
              "damage and lost property reporting"],
        "c": ["residents and guests", "supervisors",
              "supply store", "maintenance desk"]},
    "Grounds and premises": {
        "s": ["site inspection notes", "seasonal work scheduling",
              "access and key records", "incident reporting",
              "contractor booking"],
        "c": ["occupants", "grounds contractors",
              "security desk", "utilities"]},
    "Claims and underwriting": {
        "s": ["claim intake and logging", "cover and eligibility checking",
              "evidence and document gathering", "settlement note writing",
              "decline and appeal correspondence"],
        "c": ["claimants", "loss adjusters",
              "underwriting desk", "legal and complaints"]},
    "Payroll and billing": {
        "s": ["timesheet collection", "invoice raising and matching",
              "payment run preparation", "arrears and query chasing",
              "reconciliation writing"],
        "c": ["employees and customers", "accounts department",
              "bank and payment provider", "auditors"]},
    "Purchasing and procurement": {
        "s": ["requisition handling", "quote comparison",
              "purchase order raising", "delivery chasing",
              "supplier record keeping"],
        "c": ["requesting departments", "suppliers",
              "goods-in", "accounts payable"]},
    "Human resources": {
        "s": ["vacancy and applicant tracking", "interview scheduling",
              "offer and contract drafting", "personnel file keeping",
              "absence and leave recording"],
        "c": ["candidates and staff", "hiring managers",
              "payroll", "occupational health"]},
    "Reception and front desk": {
        "s": ["visitor logging", "call routing and message taking",
              "appointment confirmation", "post and delivery handling",
              "enquiry triage"],
        "c": ["visitors and callers", "staff being asked for",
              "security desk", "facilities"]},
    "Secretarial and executive support": {
        "s": ["diary and travel arranging", "meeting paper preparation",
              "minute taking and actions", "correspondence drafting",
              "expense claim handling"],
        "c": ["the person supported", "other assistants",
              "meeting attendees", "finance office"]},
    "Customer service and call handling": {
        "s": ["enquiry logging", "case note writing and updating",
              "resolution and refund drafting", "escalation handling",
              "satisfaction follow-up"],
        "c": ["customers", "team leader",
              "specialist teams", "complaints handler"]},
    "Scheduling and booking": {
        "s": ["availability keeping", "booking and confirmation writing",
              "cancellation and waitlist handling", "reminder sending",
              "no-show recording"],
        "c": ["the people booked in", "the people booked for",
              "reception", "operations desk"]},
    "Data entry and transcription": {
        "s": ["source document keying", "audio and note transcription",
              "field validation and correction", "batch completion logging",
              "query and exception flagging"],
        "c": ["the authors of the source", "quality checker",
              "systems support", "records office"]},
    "Records and filing": {
        "s": ["record indexing", "retention schedule following",
              "retrieval request handling", "correction and amendment logging",
              "disposal authorisation"],
        "c": ["record requesters", "department owners",
              "compliance officer", "archive store"]},
    "Supervision and management": {
        "s": ["rota and cover planning", "objective and appraisal notes",
              "escalation handling", "budget and spend tracking",
              "incident and outcome reporting"],
        "c": ["the team", "senior management",
              "human resources", "the department's customers"]},
    "Machine operation": {
        "s": ["run sheet keeping", "batch and lot logging",
              "tolerance checking", "downtime reporting",
              "changeover records"],
        "c": ["shift supervisor", "maintenance",
              "quality control", "materials store"]},
    "Repair and service": {
        "s": ["fault diagnosis notes", "parts lookup and ordering",
              "service history keeping", "warranty claim drafting",
              "repair estimate writing"],
        "c": ["customers", "parts suppliers",
              "warranty administrator", "technical support"]},
    "Installation and commissioning": {
        "s": ["site survey notes", "measurement schedules",
              "commissioning sign-off", "handover pack writing",
              "variation recording"],
        "c": ["site contacts", "other trades",
              "building inspectors", "equipment suppliers"]},
    "Assembly": {
        "s": ["build sequence following", "part traceability records",
              "torque and joint logs", "rework recording",
              "first-off approval"],
        "c": ["line supervisor", "quality control",
              "component stores", "design engineer"]},
    "Inspection and testing": {
        "s": ["defect logging", "sampling records",
              "non-conformance reporting", "test result recording",
              "certificate issuing"],
        "c": ["production supervisor", "quality manager",
              "certifying body", "customers"]},
    "Planned maintenance": {
        "s": ["maintenance schedule keeping", "asset register updating",
              "permit-to-work handling", "spares stock tracking",
              "breakdown history writing"],
        "c": ["operations supervisor", "spares suppliers",
              "safety officer", "equipment manufacturers"]},
    "Materials handling": {
        "s": ["goods received recording", "stock location tracking",
              "pick list working", "damage and discrepancy reporting",
              "load manifest checking"],
        "c": ["drivers", "stock controller",
              "goods-in office", "carriers"]},
    "Driving and delivery": {
        "s": ["route and run sheet keeping", "delivery proof capture",
              "hours and rest logging", "vehicle defect reporting",
              "failed delivery reporting"],
        "c": ["dispatch", "recipients",
              "vehicle maintenance", "transport manager"]},
}

_COMPILED = [(name, _pattern(tokens)) for name, tokens in RULES]


def group_of(title: str) -> str | None:
    """The group this title belongs to, or None when nothing claims it."""
    for name, pattern in _COMPILED:
        if pattern.search(title):
            return name
    return None
