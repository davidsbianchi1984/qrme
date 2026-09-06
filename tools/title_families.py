"""File an imported occupation title into one of the pool's families.

The three lists under ``tools/data`` are titles and nothing else. A title
on its own is not a pool row: a row has to say what a synthetic worker
would *do* with a keyboard and who it would have to reach, and those come
from the family. So every imported title has to land in one.

Two things about the token format are load-bearing, both learned the hard
way on the first pass. A token may contain spaces and is then matched as a
phrase — the first version split every rule on whitespace, so "case
manager" became "case" or "manager" and filed 221 titles, most of them
managers of something else entirely, under mental health. And a token
matches a whole word unless it ends in ``*``, which makes it a stem —
"engine*" was meant for "search engine" and instead swallowed every
Engineer in the list.

Rules are ordered and the first match wins, so the specific families come
before the general ones. ``Business, people & operations`` is last on
purpose: manager, supervisor and clerk say what a role's shape is, not
what field it is in, so they only decide a title nothing else claimed.
``UNPLACED`` is not a silent bucket — the build fails on it, because a
title filed nowhere would ship as a row with no skills at all.
"""
from __future__ import annotations

import re

UNPLACED = "?"

#: (family, comma-separated tokens). A token is matched as a whole word or
#: phrase; a token ending in "*" is a stem and matches any word starting
#: with it.
RULES: list[tuple[str, str]] = [
    ("Creator economy & online media",
     "influencer*, creator*, youtuber*, tiktoker*, instagram, twitch, "
     "onlyfans, fansly, manyvids, chaturbate, stripchat, streamer*, "
     "streaming, podcast*, webcam*, cam girl, cam boy, adult, erotic*, "
     "fetish, pornograph*, nude, burlesque, stripper, domme, submissive, "
     "bdsm, asmr, cosplay, meme, reels, shorts, short-form, viral, "
     "monetization, monetisation, social media, online personality, "
     "virtual influencer, age verification, sex toy, sex educator, "
     "live commerce, digital sex educator, digital content, "
     "content strategist"),

    ("Health care",
     "nurse*, nursing, physician*, surgeon*, surgical, surgery, doctor, "
     "medical, medicine, clinical, dentist*, dental, dentistry, "
     "orthodontist*, prosthodontist*, endodontist*, periodontist*, "
     "hygienist*, pharmacist*, pharmacy, pharmaceutical*, radiolog*, "
     "radiograph*, radiologic, sonograph*, anesthesiolog*, anaesthesiolog*, "
     "anesthetist*, anaesthetist*, cardiolog*, cardiovascular, dermatolog*, "
     "neurolog*, neurodiagnostic, oncolog*, pathologist*, pathology, "
     "pediatric*, paediatric*, psychiatrist*, psychiatric, obstetric*, "
     "gynecolog*, gynaecolog*, ophthalmolog*, optometrist*, optician*, "
     "orthoptist*, podiatrist*, chiropractor*, midwife, midwives, "
     "midwifery, paramedic*, ambulance, physiotherap*, physical therapist*, "
     "occupational therapist*, respiratory therapist*, recreational "
     "therapist*, radiation therapist*, therapist*, therapy, dietitian*, "
     "dietician*, nutritionist*, audiologist*, speech-language, "
     "phlebotomist*, epidemiolog*, immunolog*, allergist*, endocrinolog*, "
     "gastroenterolog*, hematolog*, haematolog*, nephrolog*, urolog*, "
     "rheumatolog*, orthopedic, orthopaedic, orthotist*, prosthetic*, "
     "prosthetist*, perfusionist*, acupuncturist*, naturopath*, "
     "veterinar*, hospice, patient, health, healthcare, clinic, clinics, "
     "hospital, exercise physiolog*, athletic trainer*, coroner*, "
     "embalmer*, funeral, cytotechnologist*, cytogenetic, histotechnolog*, "
     "histolog*, magnetic resonance, diagnostic medical, orderlies, "
     "orderly, dialysis, genetic counselor*, genetic counsellor*, "
     "biostatistician*, neuropsycholog*, otolaryngolog*, otorhinolaryngolog*, "
     "physiatrist*, intensivist*, hospitalist*, resident, residents, intern, "
     "interns, clinician*, prescriptionist*, acupressurist*, rolfer*, "
     "encephalograph*, accessioner*, sonologist*, anatomist*, "
     "osteopath*, chiroprax*, midwif*, doula*, nurse-midwife, apothecary, "
     "apothecaries, extern*, bioanalyst*, biotechnician*, cytotechnician*, "
     "histotechnician*, diagnostician*, geriatrician*, neurosurgeon*, "
     "naprapath*, psychoanalyst*, paraoptometric*, polysomnograph*, "
     "emt, emt-p, emt-i, hydrotechnician*"),

    ("Mental health & social care",
     "psycholog*, counselor*, counsellor*, counselling, counseling, "
     "psychotherap*, social worker*, social work, social service*, "
     "caseworker*, case manager*, substance abuse, addiction, "
     "behavioral disorder*, behavioural disorder*, marriage and family, "
     "probation, parole, rehabilitation counselor*, child care, childcare, "
     "child, family, and school, residential advisor*, personal care aide*, "
     "home health aide*, home-based personal care, caregiver*, "
     "community health worker*, crisis, nannies, nanny, "
     "health care assistant*, teachers aide*, teaching assistant*, "
     # Care by its ordinary English names, which the taxonomies do not
     # use and workers do. Without these the generic shapes downstream
     # take them: "Home Care Attendant" matched `attendant*` and was
     # filed under hospitality, so a home carer browsed with "till
     # reconciliation" and "allergen awareness" as their first skills;
     # "Care Worker" and "Care Assistant" fell to `worker*` and
     # `assistant*` and landed in business operations. `carer*` is a
     # stem and does not reach "career" — that is c-a-r-e-e-r.
     "care worker*, care assistant*, care attendant*, care aide*, "
     "carer*, home care, homecare, care home, live-in care, "
     "domiciliary care, support worker*, elder care, eldercare, "
     "senior care, respite care"),

    ("Education & research",
     "teacher*, teaching, professor*, lecturer*, instructor*, tutor*, "
     "educator*, education, educational, school principal*, dean, "
     "curriculum, librarian*, library, archivist*, curator*, museum, "
     "historian*, anthropolog*, archeolog*, archaeolog*, sociolog*, "
     "philosopher*, political scientist*, linguist*, scientist*, "
     "researcher*, research, physicist*, astronomer*, chemist*, "
     "geologist*, geophysicist*, geoscientist*, geographer*, biologist*, "
     "botanist*, zoologist*, microbiolog*, biochemist*, meteorolog*, "
     "hydrolog*, oceanograph*, postsecondary, kindergarten, preschool, "
     "special needs, education methods, higher education, "
     "mathematician*, actuar*, statistician*, economist*, "
     "mathematical science, survey researcher*, geneticist*, "
     "statistical, mathematical, learning experience, instructional design*, "
     "learning ecosystem, forest school, graduate fellow*, graduate student*, "
     "montessori, paraprofessional*, vice principal*, housefellow*, "
     "protohistorian*, metaphysician*, econometrician*, biomathematician*, "
     "biometrician*, geometrician*, psychometrician*, ballistician*, "
     "cryptanalyst*, nanotechnician*, geotechnician*, microarchitect*"),

    ("Law & public administration",
     "lawyer*, attorney*, solicitor*, barrister*, judge*, judicial, "
     "magistrate*, paralegal*, legal, law clerk*, arbitrator*, mediator*, "
     "conciliator*, adjudicator*, hearing officer*, court, title examiner*, "
     "licensing, government official*, legislator*, policy, compliance, "
     "regulatory, customs, immigration, border, tax examiner*, revenue, "
     "eligibility interviewer*, notary, notaries, ombudsman, "
     "senior government, traditional chief*, special-interest, "
     "clergy, religious, chaplain*, social benefits, alderman, aldermen, "
     "councilman, councilmen, councilwoman, councilwomen, comptroller*, "
     "bondsman, bondsmen, rector*, officiant*, advocate*, activist*, "
     "admeasurer*, abstractor*, abstract searcher*, deputy*, marshal*, "
     "bishop*, monk, monks, nun, nuns, priest*, curate*, deacon*, imam*, "
     "rabbi*, reverend*, vicar*, sacristan*, sexton*, mohel*, shochet*, "
     "shohet*, missionary, missionaries, postulant*, novice*, infirmarian*, "
     "attache*, consul*, delegate*, politician*, councilperson*, "
     "commandant*, register in chancery, register of, tipstaff, bursar*, "
     "conferee*, liaison*, sanitarian*, provost*, scribe*, prefect*"),

    ("Finance, accounting & insurance",
     "accountant*, accounting, auditor*, auditing, bookkeep*, payroll, "
     "financial, finance, budget analyst*, credit, loan, loans, mortgage, "
     "insurance, underwriter*, claims, adjuster*, appraiser*, appraisers "
     "of, assessor*, tax preparer*, tax, treasurer*, investment, "
     "securities, broker*, teller*, tellers, billing, collections, "
     "debt-collector*, pawnbroker*, bookmaker*, croupier*, gambling, "
     "gaming, valuer*, cost estimator*, fundraiser*, fundraising, "
     "money-lender*, account collector*"),

    ("Software & IT",
     "software, developer*, programmer*, programming, computer, "
     "information security, cybersecurity, penetration tester*, database*, "
     "network*, systems administrator*, systems analyst*, web, webmaster*, "
     "information technology, help desk, helpdesk, devops, data scientist*, "
     "data engineer*, data warehousing, machine learning, artificial "
     "intelligence, blockchain, cloud, applications, informatics, "
     "bioinformatic*, telecommunication*, telecom, quality assurance "
     "analyst*, search engine, digital forensic*, geospatial, "
     "user support, business intelligence, document management"),

    ("Engineering & built environment",
     "engineer*, engineering, architect*, architectural, drafter*, "
     "drafting, draughtsperson*, surveyor*, surveying, cartograph*, "
     "geodetic, urban planner*, town and traffic, regional planner*, "
     "landscape, industrial designer*, product designer*, garment "
     "designer*, mechatronic*, robotic*, nanotechnolog*, photonic*, "
     "materials, civil, structural, geotechnical, construction manager*"),

    ("Energy, utilities & resources",
     "power plant*, power distributor*, nuclear, reactor, power-line, "
     "power line, utilities, utility, water treatment, wastewater, "
     "gas, oil, petroleum, drilling, mining, miner*, mine, quarry, "
     "extraction, refinery, refining, pipeline, solar, wind, "
     "photovoltaic, hydroelectric, energy, fuel cell, biofuel*, biomass, "
     "geothermal, incinerator, recycling, refuse, hazardous materials, "
     "substation, powerhouse, stationary engineer*, wellhead, derrick, "
     "roustabout*, rock splitter*, roof bolter*, earth driller*"),

    ("Agriculture, environment & animals",
     "farmer*, farm, farming, ranch, rancher*, agricultur*, crop*, "
     "livestock, animal*, aquacultur*, fisher*, fishery, fishing, "
     "hunter*, trapper*, forest, forestry, logging, logger*, timber, "
     "faller*, nursery, greenhouse, groundskeeping, landscaping, "
     "horticultur*, gardener*, market gardener*, pest control, "
     "conservation, environmental, wildlife, park naturalist*, soil, "
     "plant scientist*, breeder*, subsistence, veterinary assistant*, "
     "tree trimmer*, logging equipment, forester*, log grader*, scaler*, "
     "pesticide, vegetation, sprayer*, applicator*, permaculture, apiarist*, "
     "apiary, beekeep*, mycolog*, forag*, herbalist*, mushroom, dog, cat, "
     "pet, pets, kennel*, aquarium, picker*, viner*, snapper*, snipper*, "
     "floricultur*, silvicultur*, avicultur*, apicultur*, viticultur*, "
     "lumberjack*, lumberman, lumbermen, woodsman, woodsmen, axman, axmen, "
     "roguer*, weed*, orchard*, vineyard*, harvest*, thresher*, "
     "shepherd*, herder*, milker*, shearer*, stockman, stockmen, cowboy*, "
     "vaquero*, jackaroo*, barn, corral, zanjero*, "
     "hatchery, tier, tiers, transplanter*, cultivator*"),

    ("Public safety, defence & security",
     "police, detective*, sheriff*, deputy, constable*, firefighter*, "
     "fire fighter*, fire-fighter*, fire inspector*, firefighting, "
     "correctional, corrections, prison, bailiff*, security, "
     "surveillance, armed forces, military, soldier*, commissioned, "
     "non-commissioned, infantry, artillery, armored, armoured, "
     "ordnance, special forces, air crew, missile, "
     "emergency management, lifeguard*, animal control, other ranks, "
     "protective service*, guard, guards, telecommunicator*, public safety, "
     "cop, cops, watchman, watchmen, patroller*, gunner*, crewmember*, "
     "lieutenant*, sergeant*, corporal*, captain, sentry, sentries, "
     "custodian*, redcap*, red cap, bodyguard*, watchguard*, mercenary, "
     "mercenaries, navy seal*, spy, spies, reconnaissance, expeditionary, "
     "multi-national, combat"),

    ("Transport & logistics",
     "driver*, pilot*, copilot*, flight, aircraft, airline*, air traffic, "
     "aviation, airfield, sailor*, seaman, deckhand*, mate, mates, ship*, "
     "boat*, vessel*, marine, motorboat*, locomotive, railroad, rail, "
     "yard, subway, streetcar, conductor*, bus, taxi, chauffeur*, "
     "delivery, courier*, truck*, freight, cargo, shipping, receiving, "
     "warehouse, logistic*, supply, distribution, dispatcher*, "
     "traffic technician*, stock clerk*, material mover*, packer*, "
     "packaging, stower*, baggage, porter*, parking, crane, hoist, "
     "forklift, transportation, postal, mail carrier*, messenger*, "
     "travel attendant*, travel steward*, transport, passenger*, "
     "postmaster*, stocker*, order filler*"),

    ("Hospitality, food & retail",
     "chef*, cook*, baker*, bakers, butcher*, waiter*, waitress*, server*, "
     "bartender*, barista*, host, hostess, restaurant*, kitchen, food, "
     "beverage*, catering, dishwasher*, hotel*, motel*, lodging, "
     "housekeeping, maid*, janitor*, cleaner*, cleaning, "
     "bellhop*, usher*, retail, sales, salesperson*, cashier*, "
     "merchandis*, buyer*, purchasing, counter, rental, demonstrator*, "
     "promoter*, telemarketer*, vendor*, barber*, hairdresser*, "
     "hairstylist*, cosmetolog*, manicurist*, pedicurist*, skincare, "
     "esthetician*, spa, massage, fitness, personal trainer*, "
     "recreation, amusement, tour guide*, travel guide*, travel agent*, "
     "travel consultant*, flight attendant*, shampooer*, slaughter*, "
     "meat, poultry, fish, dairy, confectionery, pastry, brewing, "
     "distilling, winemaker*, sommelier*, laundry, dry-cleaning, "
     "presser*, personal service*, other personal, conference and event, "
     "meeting, convention, concierge*, merchant*, attendant*, athlete*, "
     "sports, umpire*, referee*, coach*, scout*, preserver*, tobacco, "
     "cheesemaker*, cheese, mixologist*, mixology, bar back, barback*, "
     "barkeep*, barmaid*, bellperson*, bellstaff, busboy*, carhop*, "
     "curb hop, skate hop, chambermaid*, housemaid*, houseperson*, "
     "doorperson*, concessionaire*, restaurateur*, scullion*, stewardess*, "
     "valet*, sky cap, skycap*, caddie*, caddy, caddies, expo, bobarista*, "
     "fountain jerk, cosmetician*, aesthetician*, esthetician*, masseur*, "
     "masseuse*, chaperon*, companion*, governess*, matron*, laundress*, "
     "bootblack*, shoeblack*, docent*, page, pages, banquet"),

    ("Media, creative & communications",
     "writer*, writers, author*, editor*, journalist*, reporter*, "
     "correspondent*, broadcast*, announcer*, producer*, director of "
     "photography, camera, cinematograph*, photograph*, videograph*, "
     "film, video, audio, sound, lighting, stage, set designer*, "
     "graphic, multimedia, animator*, illustrator*, artist*, artistic, "
     "sculptor*, craft, musician*, singer*, composer*, dancer*, "
     "choreographer*, actor*, actress*, performer*, entertainer*, "
     "talent, public relations, advertising, marketing, "
     "communications, copywriter*, translator*, interpreter*, "
     "proofread*, publisher*, publishing, disc jockey*, radio, "
     "television, media, poet*, lyricist*, agents and business managers, "
     "creative, cultural, museum technician*, designer*, designers, "
     "costume*, projectionist*, motion picture, exhibit, muralist*, mural, "
     "reviewer*, typeface*, font, fonts, glyph*, emoji, foley, "
     "accompanist*, pianist*, violinist*, cellist*, guitarist*, organist*, "
     "harpist*, flautist*, drummer*, instrumentalist*, vocalist*, "
     "cartoonist*, caricaturist*, acrobat*, aerialist*, juggler*, "
     "magician*, prestidigitator*, clown*, mime, puppeteer*, ventriloquist*, "
     "circus, stunt*, extra, extras, role player*, storyteller*, "
     "double bass, piano, banjo, fiddler*, bugler*, trumpeter*, ballerina*, "
     "bandperson*, comedian*, comic, comics, critic*, emcee*, maestro*, "
     "mascot*, medium, mediums, clairvoyant*, grip, grips, cyberathlete*, "
     "equestrian*, jockey, jockeys, shill*, freak*"),

    ("Skilled trades",
     "plumber*, pipefitter*, pipe fitter*, steamfitter*, electrician*, "
     "carpenter*, joiner*, mason*, bricklayer*, brickmason*, blockmason*, "
     "stonemason*, roofer*, glazier*, plasterer*, drywall, tiler*, "
     "tile setter*, floor layer*, painter*, paperhanger*, welder*, "
     "welding, solderer*, brazer*, sheet metal, boilermaker*, "
     "millwright*, machinist*, toolmaker*, tool and die, blacksmith*, "
     "locksmith*, mechanic*, repairer*, technician*, technologist*, "
     "installer*, maintenance, hvac, refrigeration, insulation, "
     "upholster*, cabinetmaker*, cabinet-maker*, woodwork*, wood, "
     "carpet, sawing, shoemaker*, cobbler*, tailor*, seamstress*, "
     "sewing, weaver*, potter*, jeweler*, jeweller*, jewellery, "
     "watch repairer*, musical instrument*, sign writer*, engraver*, "
     "etcher*, furrier*, tanner*, pelt, handicraft, basket, loom, "
     "fabricator*, assembler*, rigger*, scaffold*, ironworker*, "
     "reinforcing, elevator, escalator, operator*, tender*, tenders, "
     "setter*, grinder*, polisher*, moulder*, molder*, caster*, "
     "extruding, forming, pressing, cutting, punching, milling, lathe, "
     "feeder*, offbearer*, heat treating, plating, coating, spraying, "
     "dipping, furnace, kiln, print*, press, bindery, prepress, "
     "pre-press, typesetter*, photographic process*, tire builder*, "
     "commercial diver*, underwater diver*, fence erector*, "
     "segmental paver*, model maker*, patternmaker*, pattern-maker*, "
     "finisher*, splitter*, carver*, fitter*, servicer*, crushing, "
     "helpers, helper, structural metal, building frame, "
     "building structure, precision instrument*, laborer*, labourer*, "
     "sweeper*, pipelayer*, foundry, coremaker*, mold*, cutter*, "
     "trimmer*, sewer*, weigher*, measurer*, checker*, sampler*, "
     "process controller*, plant controller*, service attendant*"),

    ("Business, people & operations",
     "manager*, management, managing director*, director*, executive*, "
     "officer*, chief, president, supervisor*, administrator*, "
     "administrative, assistant*, secretary, secretaries, receptionist*, "
     "reception, clerk*, clerical, office, human resource*, personnel, "
     "recruiter*, recruiting, training, development specialist*, "
     "specialist*, coordinator*, planner*, analyst*, consultant*, "
     "consulting, operations, project, program, procurement, contract*, "
     "logistician*, business, entrepreneur*, franchise, owner, "
     "proprietor*, representative*, account*, customer service, "
     "call center*, call centre*, contact centre*, data entry, "
     "typist*, word processor*, switchboard, interviewer*, "
     "statistical assistant*, enquiry, inspector*, worker*, workers, "
     "occupations, models, model, agent*, agents, facilitator*, "
     "organiser*, organizer*, culture builder, mutual aid"),
]


def _pattern(tokens: str) -> re.Pattern:
    parts = []
    for tok in (t.strip() for t in tokens.split(",")):
        if not tok:
            continue
        if tok.endswith("*"):
            parts.append(re.escape(tok[:-1]) + r"\w*")
        else:
            parts.append(re.escape(tok))
    return re.compile(r"\b(?:%s)\b" % "|".join(parts), re.I)


_COMPILED = [(fam, _pattern(tokens)) for fam, tokens in RULES]


#: Agent-noun endings. A title that is only somebody who *does* a thing —
#: "Abrasive Mixer", "Acetylene Burner", "Bone Puller", "Sole Skiver" — is
#: a maker or a handler, and the taxonomy's forty thousand reported titles
#: are full of them. This is the last resort, applied only after the words
#: and the nearest known occupation have both had their say, and the build
#: prints how many landed here so it never becomes an invisible bucket.
_SHAPES = ("er", "or", "man", "men", "ist", "smith", "wright", "hand",
           "monger", "eer", "layer", "maker", "keeper")


def by_shape(title: str) -> str | None:
    """Skilled trades, when the title's shape is all there is to go on."""
    words = title.replace("-", " ").split()
    if not words:
        return None
    last = words[-1].lower().rstrip("s")
    if any(last.endswith(shape) for shape in _SHAPES):
        return "Skilled trades"
    return None


def family_of(title: str) -> str:
    """The family this title belongs to, or UNPLACED."""
    for fam, pattern in _COMPILED:
        if pattern.search(title):
            return fam
    return UNPLACED
