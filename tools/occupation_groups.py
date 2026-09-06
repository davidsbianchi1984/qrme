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

## What is deliberately not a group

`technician` (1,352 unclaimed titles), `specialist` (1,206), `worker`
(917), `assistant` (331), `associate` (207) and `consultant` (278) are
the largest words left, and none of them becomes a group. They say where
somebody sits, not what they do, and a group leads the merged row — so a
`Physician Assistant` given "task list working" would read worse than a
`Physician Assistant` given Health care's clinical phrases, while the
coverage number went up.

`Supervision and management` is the one rank that is a group, and it
earns it by being last: it decides only what nothing else claimed, and a
title reaching it is read as a gap in the rules above. A rank rule placed
where it can outrank real work is not coverage, it is noise with a
percentage attached.

Coverage is the ratchet's measure, not its goal. It exists to stop the
catalogue sliding backwards, and it is worth less than a right answer.

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
    # -- instruction, before the subject being instructed ------------------
    #
    # First of every rule. "Nursing Instructor" read as nursing and
    # "Radiology Instructor" as imaging, because the care groups sit high
    # and both titles name their subject. Whoever the instruction is
    # about, instructing is the work: lesson plans, marking and reports
    # to parents, not observation charts.
    #
    # Training and coaching does not come with it. It stays below Animal
    # care, because an animal trainer trains animals.
    ("Teaching and instruction",
     "teacher*, teaching, instructor*, professor*, lecturer*, tutor*, "
     "faculty, educator*, headteacher*, principal of, schoolmaster*, "
     "schoolmistress*"),

    # -- care of a person, before anything that merely contains "care" ----
    ("Clinical imaging",
     "radiolog*, radiograph*, sonograph*, ultrasound, mammograph*, "
     "imaging, x-ray, xray, ct tech*, mri, nuclear medicine"),

    ("Laboratory work",
     "laboratory, lab tech*, phlebotom*, histolog*, cytolog*, patholog*, "
     "specimen, assay*, microbiolog*, serolog*, toxicolog*"),

    ("Animal care",
     "veterinar*, animal, kennel*, groomer*, zookeep*, stable*, equine, "
     "livestock, pet, aquarium*, wildlife, dog, dogs, canine*, "
     "feline*, puppy, kitten*, poultry, apiar*, beekeep*"),

    ("Personal care",
     "caregiver*, care aide*, care assistant*, care worker*, "
     "home health aide*, personal care*, nursing assistant*, orderly, "
     "carer*, companion*, home aide*"),

    ("Nursing",
     "nurse*, nursing, midwife*, midwives, midwifery"),

    ("Hairdressing and beauty",
     "hairdress*, hairstylist*, hair stylist*, barber*, beautician*, "
     "cosmetolog*, manicur*, pedicur*, nail technician*, esthetic*, "
     "aesthetic*, waxing, lash technician*, "
     "hair assistant*, hair worker*, hair specialist*, hair artist*, "
     "hair stylist*, shampooer*, makeup artist*, make-up artist*"),

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
     "loss adjuster*, insurance producer*, insurance agent*, "
     "insurance sales*"),

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
     "record, records, recordkeep*, clerk*"),

    # -- the rest of the fields --------------------------------------------
    #
    # Above the fields block so a train conductor is not an orchestra's,
    # and a sales assistant is on a shop floor before Sales gets the
    # word. Every stem here was probed first: `well*` is not a token
    # because of the wellness coaches, `gas*` because of the gas
    # fitters, `stock*` because of the stockbrokers, `shop*` because it
    # takes the machine shop supervisors, `child*` because it takes the
    # child psychologists from Therapy, `electric*` because an
    # electrician is a trade. Transport says `train conductor*` by
    # phrase and leaves `conductor*` to the orchestras.
    ("Energy and extraction",
     "oil well*, gas well*, well driller*, well logger*, wellhead*, "
     "oilfield*, oil field*, oil rig*, drilling rig*, rig hand*, "
     "roughneck*, roustabout*, derrickman*, derrickhand*, toolpusher*, "
     "petroleum*, refinery*, pipeline*, natural gas*, gas plant*, "
     "miner, miners, mining machine*, mining operator*, "
     "mining engineer*, surface mining*, underground mining*, "
     "coal mining*, mine worker*, mining captain*, mining production*, "
     "gas producer*, mud logger*, quarry*, colliery*, lineman, linemen, "
     "linesman, linesmen, lineworker*, line worker*, power plant*, "
     "power station*, substation*, meter reader*, solar*, "
     "wind turbine*, nuclear*, hydroelectric*, geothermal*"),

    ("Science",
     "chemist*, physicist*, biolog*, geolog*, meteorolog*, astronom*, "
     "ecolog*, geoscien*, hydrolog*, oceanograph*, botanist*, "
     "zoolog*, microbiolog*, biochem*, environmental scientist*, "
     "seismolog*, metallurg*"),

    ("Public administration",
     "civil servant*, public servant*, councillor*, council officer*, "
     "government*, planning officer*, compliance officer*, licensing*, "
     "environmental health officer*, building inspector*, "
     "health inspector*, customs officer*, immigration officer*, "
     "border force*, border patrol*, revenue officer*, "
     "benefits officer*, housing officer*, ombudsman*, regulator*, "
     "town planner*, urban planner*, elections*, electoral*, "
     "clerk of the*, city clerk*, county clerk*"),

    ("Retail and shop floor",
     "cashier*, retail*, shop assistant*, shopkeeper*, shop floor*, "
     "checkout*, merchandis*, florist*, grocer*, store clerk*, "
     "store associate*, store assistant*, sales assistant*, "
     "sales associate*, salesclerk*, sales clerk*, shelf stacker*, "
     "till operator*"),

    ("Transport operations",
     "train conductor*, bus conductor*, railway*, railroad*, "
     "signaller*, signalman*, signalmen, station master*, "
     "stationmaster*, transit*, fleet*, logistics, freight*, "
     "customs broker*, import*, export*, forwarder*, "
     "traffic controller*, traffic officer*, traffic warden*, "
     "parking*"),

    ("Media and communications",
     "broadcast*, producer*, presenter*, announcer*, newscaster*, "
     "camera operator*, cameraman*, camerawoman*, sound engineer*, "
     "sound technician*, lighting technician*, publicist*, "
     "public relations, communications officer*, "
     "communications manager*, marketing*, advertis*, social media, "
     "press officer*, media"),

    ("IT operations",
     "network*, systems administrator*, system administrator*, "
     "it support*, it technician*, cyber*, infrastructure engineer*, "
     "devops*, cloud*, database*, sysadmin*, webmaster*, "
     "computer operator*, computer technician*, it manager*"),

    ("Childcare and community",
     "childcare*, child care*, childminder*, nanny*, nannies, "
     "au pair*, playworker*, daycare*, day care*, nursery assistant*, "
     "youth worker*, social worker*, community worker*, "
     "community support*, welfare officer*, family support*, "
     "foster*, care coordinator*, support worker*, outreach*"),

    ("Sport and fitness",
     "athlete*, fitness*, gym*, personal trainer*, referee*, umpire*, "
     "jockey*, golf*, swim*, footballer*, cricketer*, sportsman*, "
     "sportswoman*, sports*, boxer*, wrestler*, cyclist*"),

    # -- the fields with a shape of their own ------------------------------
    #
    # Below the office, so a legal secretary is a secretary and a tax
    # clerk is a clerk; above the professions and the trades, so a
    # deckhand is at sea and a farm hand is on a farm before either is a
    # hand. Stems are checked against the pool, not guessed: `tax*` is
    # not here because it takes the taxi drivers and the taxidermists,
    # `fire*` because a kiln firer is not a firefighter, `server` because
    # half the servers administer machines.
    ("Fire and rescue",
     "firefighter*, fire fighter*, fireman, firemen, fire officer*, "
     "fire chief*, fire captain*, rescue, paramedic*, ambulance, "
     "lifeguard*, emergency medical"),

    ("Security and policing",
     "security, police, constable*, sheriff*, detective*, patrol*, "
     "correctional, corrections, prison, warden*, bailiff*, "
     "crossing guard*, security guard*, bodyguard*, investigator*"),

    ("Clinical practice",
     "physician*, doctor*, surgeon*, dentist*, dental*, pharmac*, "
     "optometr*, podiatr*, chiropract*, anesthesiolog*, anaesthe*, "
     "orthodont*, paediatric*, pediatric*, psychiatr*, physiotherap*, "
     "clinician*, medical officer*, general practitioner*"),

    ("Aviation",
     "pilot*, aircraft*, flight*, aviation, air traffic*, cabin crew*, "
     "air steward*, aircrew*, airline*, aerodrome*, airport*"),

    ("Marine and fishing",
     "deckhand*, deck officer*, deck cadet*, seaman*, seafarer*, "
     "sailor*, mariner*, boatswain*, skipper*, fisherman*, fisher*, "
     "shipmaster*, harbour master*, harbor master*, coxswain*, "
     "able seaman*, ship's*, marine engineer*, dock worker*, docker*, "
     "stevedore*, longshore*"),

    ("Farming and growing",
     "farm*, grower*, harvest*, crop*, orchard*, vineyard*, ranch*, "
     "agricultur*, horticultur*, nursery worker*, forester*, forestry, "
     "arborist*, tree surgeon*, gardener*, greenhouse*, "
     "shepherd*, herdsman*, dairy*"),

    ("Cooking and food preparation",
     "cook, cooks, chef*, baker*, butcher*, pastry*, kitchen*, "
     "caterer*, catering, barista*, bartender*, sommelier*, "
     "line cook*, prep cook*, sous chef*, fishmonger*, confectioner*"),

    ("Front of house",
     "waiter*, waitress*, waitstaff*, food server*, banquet server*, "
     "hostess*, busser*, busboy*, room attendant*, wine steward*, "
     "maitre d*, restaurant host*, bar staff*, barback*"),

    ("Legal practice",
     "lawyer*, attorney*, solicitor*, barrister*, paralegal*, legal, "
     "notary*, judge*, magistrate*, conveyanc*, litigation, "
     "legal executive*, law clerk*"),

    ("Finance and accounting",
     "accountant*, accounting, auditor*, audit, actuar*, banker*, "
     "teller*, loan*, mortgage*, tax advisor*, tax adviser*, "
     "tax preparer*, tax examiner*, tax consultant*, taxation, "
     "treasur*, financial*, finance*, credit analyst*, investment*"),

    ("Performing arts",
     "musician*, singer*, vocalist*, actor*, actress*, dancer*, "
     "performer*, entertainer*, composer*, conductor*, choreograph*, "
     "comedian*, magician*, drummer*, guitarist*, pianist*, dj"),

    ("Visual arts and photography",
     "artist*, photograph*, sculptor*, printmaker*, ceramicist*, "
     "cartoonist*, muralist*, videograph*, cinematograph*"),

    ("Clergy and ministry",
     "clergy*, priest*, pastor*, chaplain*, rabbi*, imam*, "
     "minister of religion*, vicar*, deacon*, reverend*, monk*, nun, "
     "religious"),

    # -- work whose shape is what it produces -----------------------------
    #
    # Above the trades, because a teacher of a trade teaches: "Auto
    # Mechanics Teacher" is an instructor, not a mechanic, and the trade
    # rules below would have taken it.
    #
    # `coach*` is deliberately not a token. A coach is also a vehicle, and
    # the stem would have made every coach driver a trainer.
    ("Training and coaching",
     "trainer*, coaching, life coach*, executive coach*, sports coach*, "
     "wellness coach*, health coach*, "
     "apprenticeship*, instructional design*"),

    ("Therapy and counselling",
     "therapist*, therapy, counselor*, counsellor*, counseling, "
     "counselling, psychotherap*, analyst of behaviour"),

    ("Software and data",
     "software engineer*, programmer*, software develop*, web develop*, "
     "application develop*, data scientist*, data engineer*, "
     "machine learning, database administrator*, systems analyst*"),

    ("Analysis and research",
     "analyst*, analysis, researcher*, research assistant*, "
     "research associate*, scientist*, statistician*, economist*"),

    ("Design",
     "designer*, design, draughtsman*, draftsman*, drafter*, "
     "illustrator*, animator*"),

    ("Writing and editing",
     "writer*, editor*, journalist*, copywriter*, reporter*, "
     "proofreader*, translator*, interpreter*"),

    ("Sales and accounts",
     "sales, salesperson*, salesman*, saleswoman*, account executive*, "
     "account manager*, business development, canvasser*, broker*, "
     "market maker*"),

    # -- the shapes that fill the trades -----------------------------------
    # `stationary engineer` and `operating engineer` are machine minders,
    # not engineers in the professional sense. Named here so the
    # Engineering group below the trades never sees them.
    ("Machine operation",
     "stationary engineer*, operating engineer*, boiler engineer*, "
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
     "commissioning, fitter-out, glazier*, electrician*, plumber*, "
     "pipefitter*, steamfitter*, hvac*"),

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

    # This rule stays below Machine operation even though `operator*`
    # there takes the four coach and bus operators off it. Lifting it
    # above was tried and measured: it fixed those four and broke six —
    # `Electric Screw Driver Operator`, `Delivery Table Feeder` and
    # `Delivery Table Operator` became drivers, `Driver License Examiner`
    # stopped being an inspection, and an `Advance Seal Delivery System
    # Maintainer` stopped doing maintenance. `driver` and `delivery` are
    # words that appear inside machines. A net loss of two is not worth
    # taking, so the four are a known wrong answer rather than a hidden
    # one.
    # A locomotive engineer drives the train.
    ("Driving and delivery",
     "locomotive engineer*, train engineer*, "
     "motor coach operator*, coach operator*, bus operator*, "
     "driver*, chauffeur*, courier*, delivery, dispatcher*, "
     "haulier*, trucker*, rider*"),

    # -- what the hands are doing ------------------------------------------
    #
    # Below every rule above, on purpose. These claim the titles that are
    # only a process and a material — "Bone Cutter", "Sole Trimmer",
    # "Abrasive Mixer" — which is what `title_families.by_shape` files
    # into Skilled trades on the strength of a word ending alone, and
    # 9,769 of them are still sitting there. A "Cutting Machine Operator"
    # is claimed by Machine operation above and stays there: it is being
    # operated, and the run sheet is the work.
    ("Cutting and shaping",
     "cutter*, cutting, trimmer*, trimming, sawyer*, shearer*, "
     "grinder*, grinding, borer*, driller*, turner*, planer*, "
     "slitter*, slicer*, chopper*"),

    ("Finishing and coating",
     "finisher*, finishing, painter*, painting, polisher*, plater*, "
     "plating, coater*, coating, varnisher*, lacquerer*, buffer*, "
     "sandblaster*, galvaniz*, galvanis*, enameler*, enameller*"),

    ("Mixing and batching",
     "mixer*, mixing, blender*, blending, batch*, compounder*, "
     "dyer*, dyeing, brewer*, distiller*, refiner*"),

    ("Making and craft",
     "maker*, craftsman*, craftswoman*, crafter*, carver*, weaver*, "
     "potter*, tailor*, seamstress*, cobbler*, upholsterer*, "
     "bookbinder*, engraver*, jeweler*, jeweller*"),

    ("Building and construction",
     "builder*, bricklayer*, mason*, carpenter*, joiner*, roofer*, "
     "plasterer*, paver*, concreter*, scaffolder*, demolition"),

    ("Labouring and helping",
     "labourer*, laborer*, helper*, handyman*, handyperson*, "
     "yard hand*, deck hand*, farm hand*, general hand*"),

    # -- the ambiguous one -------------------------------------------------
    #
    # Below the trades, and alone among the professional shapes in being
    # so. "Engineer" carries an operator sense all through these
    # taxonomies — maintenance engineer, stationary engineer, locomotive
    # engineer — and those are the job the trade rules above describe. Put
    # this rule up with Design and Software and a maintenance engineer
    # stops doing maintenance.
    ("Engineering",
     "engineer*, engineering"),

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
    "Hairdressing and beauty": {
        "s": ["consultation and patch test records", "appointment card keeping",
              "colour and formula recording", "product and stock use logging",
              "aftercare advice writing"],
        "c": ["clients", "product suppliers",
              "salon manager", "the next stylist"]},
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
    "Energy and extraction": {
        "s": ["shift and tour reporting", "permit-to-work handling",
              "well and plant log keeping", "gas test and reading records",
              "incident and near-miss reporting"],
        "c": ["control room", "site supervisor",
              "safety officer", "maintenance and contractors"]},
    "Science": {
        "s": ["method and protocol writing", "sample and observation logging",
              "data analysis and plotting", "result validation",
              "report and paper drafting"],
        "c": ["principal investigator", "laboratory and field teams",
              "peer reviewers", "funding and regulatory bodies"]},
    "Public administration": {
        "s": ["case and application processing", "decision letter drafting",
              "statutory record keeping", "consultation summarising",
              "committee report writing"],
        "c": ["members of the public", "elected members",
              "legal services", "other departments and agencies"]},
    "Retail and shop floor": {
        "s": ["till and payment handling", "stock count and replenishment",
              "price and promotion checking", "returns and exchange handling",
              "customer query answering"],
        "c": ["customers", "store manager",
              "stockroom", "head office"]},
    "Transport operations": {
        "s": ["timetable and roster following", "movement and manifest records",
              "delay and incident logging", "customs and consignment paperwork",
              "safety check recording"],
        "c": ["control and dispatch", "drivers and crews",
              "customers and consignees", "regulators and customs"]},
    "Media and communications": {
        "s": ["running order and brief keeping", "content scheduling",
              "release and statement drafting", "coverage and reach tracking",
              "rights and clearance records"],
        "c": ["editors and producers", "clients or the organisation",
              "press and platforms", "talent and contributors"]},
    "IT operations": {
        "s": ["ticket and incident handling", "change and patch records",
              "monitoring and alert response", "access and account management",
              "runbook and documentation keeping"],
        "c": ["the people supported", "on-call engineers",
              "vendors and suppliers", "security team"]},
    "Childcare and community": {
        "s": ["daily record and observation writing", "care and support plans",
              "safeguarding and incident recording", "family communication",
              "referral and signposting"],
        "c": ["children and families", "safeguarding lead",
              "schools and agencies", "supervising practitioner"]},
    "Sport and fitness": {
        "s": ["programme and session planning", "attendance and progress records",
              "fixture and result recording", "injury and incident logging",
              "equipment and facility checks"],
        "c": ["participants and members", "club or centre manager",
              "governing body", "medical and physio support"]},
    "Fire and rescue": {
        "s": ["incident log keeping", "equipment check records",
              "patient handover writing", "hazard and risk noting",
              "post-incident reporting"],
        "c": ["control room", "hospital emergency department",
              "police", "station officer"]},
    "Security and policing": {
        "s": ["incident and occurrence logging", "statement taking",
              "evidence and exhibit recording", "patrol and check records",
              "report writing for the file"],
        "c": ["control room", "supervising officer",
              "the public and complainants", "courts and prosecutors"]},
    "Clinical practice": {
        "s": ["consultation note writing", "prescription and order writing",
              "referral letter drafting", "result review and actioning",
              "consent and safeguarding records"],
        "c": ["patients", "nursing and allied staff",
              "specialists and referrals", "pharmacy and laboratory"]},
    "Aviation": {
        "s": ["flight plan and log keeping", "weather and notice checking",
              "checklist and defect recording", "manifest and load records",
              "occurrence reporting"],
        "c": ["air traffic control", "operations and dispatch",
              "engineering", "crew and passengers"]},
    "Marine and fishing": {
        "s": ["log book keeping", "watch and weather records",
              "catch and cargo recording", "safety drill records",
              "port and customs paperwork"],
        "c": ["the master or skipper", "harbour and port authority",
              "coastguard", "buyers and agents ashore"]},
    "Farming and growing": {
        "s": ["field and crop records", "stock and movement records",
              "input and treatment logging", "yield and sales recording",
              "compliance and inspection paperwork"],
        "c": ["merchants and buyers", "veterinary and agronomy advisers",
              "inspectors", "contractors and seasonal labour"]},
    "Cooking and food preparation": {
        "s": ["prep list and par level keeping", "recipe and portion following",
              "temperature and hygiene logs", "allergen record keeping",
              "stock and waste recording"],
        "c": ["head chef", "front of house",
              "suppliers", "environmental health"]},
    "Front of house": {
        "s": ["table and booking management", "order taking and relaying",
              "bill and payment handling", "allergen and dietary noting",
              "complaint and comment recording"],
        "c": ["guests", "kitchen",
              "shift manager", "reservations"]},
    "Legal practice": {
        "s": ["matter and file opening", "document drafting and review",
              "deadline and court date keeping", "attendance note writing",
              "time recording and billing"],
        "c": ["clients", "courts and tribunals",
              "opposing representatives", "supervising solicitor"]},
    "Finance and accounting": {
        "s": ["ledger and journal posting", "reconciliation writing",
              "return and filing preparation", "variance and review notes",
              "audit evidence gathering"],
        "c": ["clients or budget holders", "the bank",
              "auditors and regulators", "the finance team"]},
    "Performing arts": {
        "s": ["rehearsal and call sheet keeping", "repertoire and set lists",
              "booking and contract records", "rider and technical notes",
              "royalty and rights tracking"],
        "c": ["agent or manager", "venues and promoters",
              "other performers", "audiences"]},
    "Visual arts and photography": {
        "s": ["brief and shot list keeping", "edit and proof handling",
              "licensing and usage records", "portfolio and archive keeping",
              "invoice and delivery notes"],
        "c": ["clients and commissioners", "galleries and publishers",
              "printers and labs", "subjects and models"]},
    "Clergy and ministry": {
        "s": ["service and sermon preparation", "pastoral visit records",
              "register keeping", "safeguarding records",
              "correspondence with the congregation"],
        "c": ["the congregation", "denominational authority",
              "families in the parish", "community organisations"]},
    "Teaching and instruction": {
        "s": ["lesson planning", "progress recording",
              "assessment and marking", "report writing to parents",
              "resource preparation"],
        "c": ["learners", "parents and guardians",
              "head of department", "examination board"]},
    "Training and coaching": {
        "s": ["training needs noting", "session material writing",
              "attendance and completion records", "feedback summarising",
              "competency sign-off"],
        "c": ["the people trained", "their managers",
              "awarding body", "learning and development"]},
    "Therapy and counselling": {
        "s": ["session note writing", "goal and plan setting",
              "consent and confidentiality records", "outcome measuring",
              "onward referral drafting"],
        "c": ["clients", "referrers",
              "clinical supervisor", "safeguarding lead"]},
    "Software and data": {
        "s": ["change and ticket writing", "code and query review notes",
              "release and rollback records", "incident write-ups",
              "documentation keeping"],
        "c": ["product owner", "other engineers",
              "operations on call", "the people who use it"]},
    "Analysis and research": {
        "s": ["question and method framing", "data gathering and cleaning",
              "finding write-ups", "assumption and limit stating",
              "source citation"],
        "c": ["the people who asked", "data owners",
              "peer reviewers", "publication or reporting line"]},
    "Design": {
        "s": ["brief taking", "concept and option presenting",
              "specification and drawing issue", "revision recording",
              "handover to production"],
        "c": ["clients and stakeholders", "makers and manufacturers",
              "reviewers and approvers", "suppliers"]},
    "Writing and editing": {
        "s": ["commission and brief handling", "draft and revision keeping",
              "fact and source checking", "style guide following",
              "publication scheduling"],
        "c": ["commissioning editor", "sources and contributors",
              "subeditors and proofreaders", "readers"]},
    "Sales and accounts": {
        "s": ["lead and pipeline recording", "quote and proposal writing",
              "objection and follow-up notes", "order and contract raising",
              "account review writing"],
        "c": ["prospects and customers", "sales manager",
              "delivery or fulfilment team", "credit control"]},
    "Cutting and shaping": {
        "s": ["cut list working", "measurement and marking records",
              "offcut and yield recording", "blade and tool change logs",
              "dimension checking"],
        "c": ["the person who set the job", "materials store",
              "quality checker", "the next operation"]},
    "Finishing and coating": {
        "s": ["surface preparation records", "coat and cure logging",
              "colour and batch matching", "defect and rework noting",
              "material safety records"],
        "c": ["the person who set the job", "paint and coating suppliers",
              "quality checker", "safety officer"]},
    "Mixing and batching": {
        "s": ["recipe and formulation following", "batch weight recording",
              "sample retention logging", "yield and loss recording",
              "contamination and allergen records"],
        "c": ["the person who set the batch", "ingredient suppliers",
              "laboratory", "production planner"]},
    "Making and craft": {
        "s": ["order and specification taking", "pattern and template keeping",
              "material and cost estimating", "work-in-progress recording",
              "repair and alteration notes"],
        "c": ["customers", "material merchants",
              "other makers", "the person who commissioned it"]},
    "Building and construction": {
        "s": ["setting-out records", "material take-off and ordering",
              "daywork and variation sheets", "inspection hold points",
              "site diary keeping"],
        "c": ["site manager", "other trades",
              "building inspector", "builders merchants"]},
    "Labouring and helping": {
        "s": ["task list working", "material moving records",
              "timesheet keeping", "hazard and near-miss reporting",
              "tool and equipment sign-out"],
        "c": ["the person being helped", "site or shift supervisor",
              "stores", "safety officer"]},
    "Engineering": {
        "s": ["requirement and specification writing", "calculation recording",
              "drawing and revision control", "test and inspection reports",
              "as-built and handover documentation"],
        "c": ["the client or project manager", "other disciplines",
              "approving authority", "contractors and suppliers"]},
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
