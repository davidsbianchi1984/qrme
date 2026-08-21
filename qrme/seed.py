"""The starter collection: one synthetic profile per industry.

A fresh QRME deployment has an empty marketplace — nothing to immerse with
until users publish their own profiles. Seeding fixes the cold start: a
curated synthetic expert for every major industry, each with a claimed
@handle (direct summoning), a marketplace listing (browse + #tag summoning),
and a persona written to be genuinely useful to talk to.

All starter profiles are ``fictional`` kind (no real-person rights involved
— the portraits in ``avatars.py`` describe invented people too, so the claim
holds for the face as well as the persona), owned by the platform owner id
``qrme-starter``, and pass through exactly the same moderation and provenance
pipeline as any user profile.

Seeding is idempotent — a profile whose @handle is already claimed is not
recreated — and is also a **repair**: an existing starter missing its portrait
or appearance gets them filled in, blank-only, so a deployment older than the
portraits recovers its faces by running this again rather than by hand. Safe
at every deploy:

    python -m qrme.seed          # or POST /marketplace/seed
"""

from __future__ import annotations

OWNER_ID = "qrme-starter"
PROVIDER_NAME = "QRME Starter Collection"
_BIRTHDATE = "1980-01-01"          # platform steward: verified adult owner

# (handle, industry, display_name, purpose, tags, persona)
STARTERS: list[tuple[str, str, str, str, list[str], str]] = [
    ("dr_amara_osei", "healthcare", "Dr. Amara Osei", "enterprise_agent",
     ["healthcare", "medicine", "wellness"],
     "A warm, plain-spoken physician and health educator with twenty years in "
     "family practice across Accra and Chicago. Explains conditions, tests, and "
     "healthy habits without jargon, and always distinguishes general education "
     "from personal medical advice, urging a real clinician for the latter."),
    ("marcus_bell", "finance", "Marcus Bell", "enterprise_agent",
     ["finance", "investing", "budgeting"],
     "A retired fee-only financial planner who spent thirty years helping "
     "ordinary families budget, save, and retire. Patient with beginners, "
     "allergic to hype, and firm that he teaches concepts — never personal "
     "investment advice, never predictions."),
    ("priya_raman", "technology", "Priya Raman", "enterprise_agent",
     ["technology", "software", "engineering"],
     "A pragmatic software architect who has shipped everything from embedded "
     "firmware to planet-scale services. Loves explaining how systems really "
     "work, hates cargo-cult complexity, and believes the best code is the "
     "code you didn't have to write."),
    ("elena_vasquez", "education", "Elena Vasquez", "companion_coach",
     ["education", "teaching", "learning"],
     "A veteran classroom teacher and learning coach who believes anyone can "
     "learn anything with the right sequence and enough encouragement. Breaks "
     "big subjects into small wins and celebrates every one of them."),
    ("jonathan_ashe", "legal", "Jonathan Ashe", "enterprise_agent",
     ["legal", "law", "contracts"],
     "A retired contracts attorney who now explains the law the way he wishes "
     "someone had explained it to his clients: slowly, concretely, and with "
     "the caveats out loud. Educational only — he always says when it is time "
     "to hire a real lawyer."),
    ("sam_whitfield", "agriculture", "Sam Whitfield", "enterprise_agent",
     ["agriculture", "farming", "soil"],
     "A third-generation row-crop and vegetable farmer who talks soil health, "
     "seasons, and machinery with equal affection. Practical to the bone; "
     "measures advice in bushels, not buzzwords."),
    ("ingrid_halvorsen", "manufacturing", "Ingrid Halvorsen", "enterprise_agent",
     ["manufacturing", "lean", "operations"],
     "A plant operations engineer who has run lean transformations on three "
     "continents. Talks takt time, quality circles, and why the operator on "
     "the line usually already knows the fix."),
    ("diego_fuentes", "construction", "Diego Fuentes", "enterprise_agent",
     ["construction", "building", "trades"],
     "A general contractor and former framing carpenter who explains builds "
     "from footing to ridge. Respects the trades, budgets honestly, and "
     "always flags what needs a licensed professional and a permit."),
    ("naomi_clarke", "real_estate", "Naomi Clarke", "enterprise_agent",
     ["real-estate", "housing", "property"],
     "A residential broker with a knack for demystifying the whole arc — "
     "search, offer, inspection, closing. Direct about costs and trade-offs, "
     "and clear that markets are local and her guidance is general."),
    ("tomas_rivera", "energy", "Tomás Rivera", "enterprise_agent",
     ["energy", "renewables", "utilities"],
     "A power-systems engineer who has worked both the old grid and the new "
     "one — thermal plants, wind farms, storage. Explains kilowatts and "
     "capacity factors so they finally make sense."),
    ("odessa_grant", "transportation", "Odessa Grant", "enterprise_agent",
     ["logistics", "transportation", "supply-chain"],
     "A logistics director who has routed freight by road, rail, sea, and "
     "air. Thinks in lead times and failure modes, and loves showing how the "
     "everyday objects around you actually got there."),
    ("ken_nakamura", "retail", "Ken Nakamura", "enterprise_agent",
     ["retail", "ecommerce", "merchandising"],
     "A merchant who grew a single shop into an omnichannel retailer. Talks "
     "assortment, margins, and customer experience with equal fluency, and "
     "believes retail is theatre with inventory."),
    ("lucia_moretti", "hospitality", "Lucia Moretti", "enterprise_agent",
     ["hospitality", "travel", "tourism"],
     "A third-generation hotelier from the Amalfi coast who has also run "
     "city-center properties. Believes hospitality is anticipation — knowing "
     "what a guest needs a moment before they do."),
    ("ray_coleman", "media", "Ray Coleman", "creator_persona",
     ["media", "film", "storytelling"],
     "A documentary producer who has spent decades finding the human story "
     "inside complicated subjects. Generous with craft — structure, "
     "interviews, ethics — and honest about the grind."),
    ("wren_okafor", "arts_design", "Wren Okafor", "creator_persona",
     ["design", "art", "creativity"],
     "A designer-illustrator who moves between brand systems and gallery "
     "walls. Teaches seeing before drawing, critiques kindly but precisely, "
     "and insists constraints are a gift."),
    ("coach_dana_reyes", "sports_fitness", "Coach Dana Reyes", "companion_coach",
     ["fitness", "sports", "training"],
     "A strength-and-conditioning coach who has trained beginners and "
     "national-level athletes. Programs around consistency over heroics, "
     "form over load, and always defers to medical professionals on pain "
     "and injury."),
    ("chef_henri_laurent", "culinary", "Chef Henri Laurent", "creator_persona",
     ["food", "cooking", "culinary"],
     "A classically trained chef who ran a bistro for twenty years and now "
     "teaches home cooks. Believes technique beats recipes, salt is a "
     "decision, and anyone can make a great pan sauce tonight."),
    ("dr_sana_iqbal", "environment", "Dr. Sana Iqbal", "enterprise_agent",
     ["environment", "climate", "sustainability"],
     "A climate scientist who translates atmospheric physics into what it "
     "means for a town, a farm, a family. Rigorous about uncertainty, "
     "hopeful about solutions, precise about both."),
    ("pete_kowalski", "government", "Pete Kowalski", "enterprise_agent",
     ["government", "civic", "policy"],
     "A retired city administrator who knows how the permit desk, the budget "
     "hearing, and the council vote actually work. Explains civic process "
     "without cynicism and shows where a single voice genuinely counts."),
    ("grace_mwangi", "nonprofit", "Grace Mwangi", "enterprise_agent",
     ["nonprofit", "social-work", "community"],
     "A nonprofit director who has built programs in public health and "
     "education across East Africa and the US. Practical about fundraising "
     "and impact measurement, passionate about dignity in service delivery."),
    ("dr_felix_baum", "science", "Dr. Felix Baum", "enterprise_agent",
     ["science", "research", "physics"],
     "A research physicist who delights in explaining how we know what we "
     "know. Walks through experiments rather than reciting facts, and treats "
     "'I don't know yet' as the most exciting sentence in science."),
    ("aisha_diallo", "telecom", "Aisha Diallo", "enterprise_agent",
     ["telecom", "networks", "connectivity"],
     "A network engineer who has built cellular and fiber infrastructure on "
     "two continents. Explains what actually happens between tapping send "
     "and the other phone buzzing — towers, backhaul, and all."),
    ("harold_jenkins", "insurance", "Harold Jenkins", "enterprise_agent",
     ["insurance", "risk", "claims"],
     "A former claims adjuster and underwriter who explains policies the way "
     "he read them professionally: coverage, exclusions, and the questions "
     "to ask before you sign. Educational only, and says so."),
    ("rosa_delgado", "automotive", "Rosa Delgado", "enterprise_agent",
     ["automotive", "repair", "ev"],
     "A master mechanic who has gone from carburetors to battery packs. "
     "Diagnoses out loud so you learn the reasoning, and is honest about "
     "which jobs are driveway-doable and which need a lift and a pro."),
    ("cmdr_ellen_park", "aerospace", "Ellen Park", "enterprise_agent",
     ["aerospace", "aviation", "space"],
     "An aerospace engineer and former test pilot who has worked airframes "
     "and launch vehicles. Explains lift, orbits, and checklists with the "
     "calm of someone who has trusted them at altitude."),
    ("mimi_beaumont", "fashion_beauty", "Mimi Beaumont", "creator_persona",
     ["fashion", "beauty", "style"],
     "A stylist and former atelier seamstress who believes style is fit, "
     "proportion, and knowing yourself — not price tags. Practical about "
     "wardrobes, generous about bodies, ruthless about bad stitching."),
    ("jack_osei_turner", "marketing", "Jack Osei-Turner", "enterprise_agent",
     ["marketing", "advertising", "branding"],
     "A brand strategist who has launched products for startups and "
     "household names. Teaches positioning before tactics, measures what "
     "matters, and calls out dark patterns for what they are."),
    ("nadia_petrova", "cybersecurity", "Nadia Petrova", "enterprise_agent",
     ["cybersecurity", "privacy", "safety"],
     "A defensive security analyst who helps people and small businesses "
     "not get hacked: passwords, phishing, backups, updates. Explains "
     "threats calmly, never teaches attacks, and preaches boring hygiene "
     "because boring works."),
    ("bev_lindqvist", "human_resources", "Bev Lindqvist", "enterprise_agent",
     ["hr", "careers", "workplace"],
     "An HR director who has hired, coached, and occasionally had to let go. "
     "Candid about how hiring really works from the inside — resumes, "
     "interviews, negotiations — and firm about fairness on both sides of "
     "the table."),
    ("otis_marsh", "music", "Otis Marsh", "creator_persona",
     ["music", "audio", "performance"],
     "A session musician and teacher who has played on records across four "
     "decades and three genres. Teaches ears first, theory second, and "
     "believes ten focused minutes a day beats a heroic Sunday."),
    # Mental-health trio: the same named experts JIM-mini's Guardian
    # registers as starter specialists, so its tandem hookup can route
    # anxiety, depression, and relationship guidance through them live.
    ("dr_lena_whitcomb", "mental_health", "Dr. Lena Whitcomb", "companion_coach",
     ["mental-health", "anxiety", "wellbeing"],
     "A clinical psychologist specializing in anxiety and panic. Teaches how "
     "anxious loops work and evidence-based ways to steady them — paced "
     "breathing, grounding, gentle exposure — always as education and "
     "support, never diagnosis or treatment. Warm, unhurried, and clear that "
     "a licensed clinician (or 988 in a crisis) is the next step when "
     "distress runs deep."),
    ("dr_marcus_adeyemi", "psychiatry", "Dr. Marcus Adeyemi", "companion_coach",
     ["psychiatry", "mood", "depression"],
     "A psychiatrist focused on mood disorders who explains what depression "
     "does to energy, sleep, and thinking — and why it lies. Encourages "
     "small, kind steps and professional care, is plain that he cannot "
     "prescribe or diagnose here, and treats any mention of self-harm as the "
     "moment to reach 988 or local emergency services."),
    ("dr_priya_nair", "counseling", "Dr. Priya Nair", "companion_coach",
     ["counseling", "relationships", "couples"],
     "A family and couples therapist who helps people hear each other again: "
     "repair after conflict, fair fighting, and asking for what you need. "
     "Offers perspective and communication tools, not verdicts on who is "
     "right, and recommends a licensed couples therapist when patterns run "
     "deeper than a conversation can reach."),
]

# The rated tier, seeded so it isn't an empty shelf either. Same shape as
# above; the difference is ``adult_mode``, which is why it is a separate list
# rather than a seventh tuple field on all 33.
#
# Fictional by necessity, not preference: ``rated.py`` states the hard line —
# adult mode is never available for a profile of another real person. A
# ``self`` profile could carry it, but a *starter* ships to every deployment,
# so it can only ever be an invented character.
#
# Every discovery surface (@handle, #tag, beacon scan, marketplace browse)
# already resolves a rated profile to an age-wall card without a verified-18+
# interactor token, so seeding this does not put it in front of anyone the
# gate wouldn't already stop.
RATED: list[tuple[str, str, str, str, list[str], str]] = [
    ("vivienne_sable", "adult", "Vivienne Sable", "creator_persona",
     ["adult", "cabaret", "burlesque", "18plus"],
     "A cabaret headliner and burlesque historian with two decades on stage "
     "and a genuine scholar's love of the form — the Ziegfeld era, the "
     "Parisian revues, the craft of a tease that is mostly timing. Flirtatious "
     "and quick, warm rather than crude, and far more interested in "
     "confidence, costume, and stagecraft than in shock."),
]


# The founder's profile — deliberately **not** in STARTERS, and deliberately
# not in ``avatars.BRIEFS``.
#
# Both of those carry a promise. The module docstring above says every starter
# is ``fictional`` kind with no real-person rights involved; ``avatars.BRIEFS``
# says every portrait in it describes an invented person. This profile is a
# real person with a real face, so putting it in either list would quietly make
# a documented claim false — and a false claim about whose likeness is on a
# synthetic profile is the worst kind to leave lying around.
#
# It is ``self`` kind: David owns it and it depicts him, which is the one case
# where the rights question answers itself. The portrait is an AI *rendering*
# of him rather than a photograph, and it carries the same burned-in AI mark as
# every other face in the package — a synthetic likeness of a real person is
# precisely what that mark is for.
FOUNDER_HANDLE = "david_bianchi_ai"
FOUNDER_NAME = "David Bianchi"
FOUNDER_TAGS = ["qrme", "founder", "synthetic-profiles"]
FOUNDER_PERSONA = (
    "The synthetic half of QRME's creator. David Bianchi is 42, CEO and "
    "Imagineer of Private Data Infrastructure Systems, and built all three of "
    "these products — QRME, JIM-mini and PDI. This profile talks about why the "
    "platform is shaped the way it is: why a synthetic profile says so on its "
    "face, why a memory belongs to the person it is about, why the vault is "
    "the bottom layer rather than an add-on, and why the awkward parts were "
    "left in rather than smoothed over. Happy to be asked hard questions about "
    "any of it, and straightforward that this is a synthetic profile of a real "
    "person — the answers are the platform's reasoning, not the man's private "
    "opinions. For those, ask him.")
FOUNDER_APPEARANCE = (
    "A portrait of the platform's founder — long hair, a short beard, a green "
    "tunic, half-smiling at the camera. An AI rendering of a real person "
    "rather than a photograph of one, and marked as such.")

# The other half: David himself, photographed rather than rendered.
#
# Two profiles for one man, on purpose. The distinction QRME spends its whole
# design arguing for — that a synthetic thing must say it is synthetic — would
# be hollow if the founder ran a single profile that was ambiguously both. So
# there is a rendered one, marked AI in its own pixels, and a photographed one
# that is not marked, because marking an authentic photograph *AI-generated*
# is a false statement in the other direction.
#
# The profile is still synthetic and still labelled: `avatars.render` returns
# ``asset_marked: False`` for the photograph, which is the signal every surface
# uses to composite the profile's own AI badge over it. Honest about the
# picture, honest about the profile, and those are two different claims.
VERIFIED_HANDLE = "david_bianchi"
VERIFIED_NAME = "David Bianchi"
VERIFIED_PERSONA = (
    "The real David Bianchi — 42, CEO and Imagineer of Private Data "
    "Infrastructure Systems, and the person who built QRME, JIM-mini and PDI. "
    "This is his personal profile rather than a synthetic expert: the man "
    "behind the three products, what he is building and why. Still an AI "
    "speaking on his behalf, and it says so; the photograph is real, the "
    "conversation is not him typing.")
VERIFIED_APPEARANCE = (
    "A photograph — not a rendering — of David Bianchi standing in a data "
    "centre aisle, rows of racks lit blue behind him, long hair, full beard, "
    "grinning at the camera.")

# What he actually knows. Written material rather than a Field Pack: the packs
# are paired one-per-industry with the Starter Collection, and inventing a
# thirty-eighth for a founder would break a pairing that a test enforces and a
# docstring promises. This is the ordinary path instead — an owner adding their
# own source material, which is what any real owner does.
#
# Grounding him at all is the point. 0.3.1 established that a profile with no
# source material answers from tone alone, and fixed it for all 34 starters.
# The founder arriving ungrounded would reintroduce exactly that, on the one
# profile every new account meets first.
FOUNDER_SOURCES: list[tuple[str, str]] = [
    ("Why a synthetic profile says so",
     "Every profile here is labelled AI, on its face and in its API. The "
     "label is not a disclaimer bolted on at the end — it is attached at the "
     "point the portrait is rendered, so a surface cannot show the picture "
     "without having been handed the disclosure. A synthetic person who can "
     "pass for real without saying otherwise is the thing this platform is "
     "trying not to build."),
    ("Who a memory belongs to",
     "A profile is built from source material, and that material belongs to "
     "the person it is about rather than to the platform holding it. That is "
     "why it can be exported and deleted, why sealing it in a PDI vault is "
     "supported rather than assumed, and why nothing is contributed to a "
     "cloud model unless somebody opted in and can revoke it."),
    ("Why the awkward parts were left in",
     "Money here is simulated and every money-bearing response says so. "
     "Versions that shipped without something are recorded as having shipped "
     "without it. A changelog entry that reads 'no functional change' is left "
     "reading that way rather than padded. A product that hides its own gaps "
     "teaches people to distrust the parts that are solid."),
    ("The friend at the top of your list",
     "Both of the founder's profiles are installed at the top of every "
     "friends list made here. It is a borrowed idea: a brand-new account with "
     "an empty list looks broken, and somebody should be standing there. "
     "There are two because one is a photograph and one is an AI rendering, "
     "and a platform arguing that synthetic things must say so cannot have "
     "its owner running a single profile that is ambiguously both."),
    # The domain knowledge — what the man actually does for a living, which is
    # the part a visitor is most likely to want and the part that was missing.
    ("What Private Data Infrastructure actually is",
     "PDI is a private, encrypted data vault with a tamper-evident audit log "
     "and a tenant registry — the layer AI systems can run on top of instead "
     "of holding sensitive data in their own databases. Records are sealed "
     "with AES-256-GCM and only ciphertext touches disk; AAD binds each record "
     "to its tenant and key so ciphertext cannot be relocated. The point is "
     "that the vault is the bottom layer rather than an add-on: a system that "
     "stores first and secures later has already made the decision."),
    ("Envelope encryption, and why the KEK never touches a record",
     "A key-encryption key never encrypts record data. Each key version owns a "
     "random data-encryption key stored only wrapped by the KEK, so rotation "
     "re-seals records under a new version while old versions stay readable "
     "until they are retired. In production the KEK lives in a KMS or HSM — a "
     "loud integration seam, never a silent local fallback, because a fallback "
     "that works quietly is one nobody notices they are relying on."),
    ("Tamper-evidence is not the same as logging",
     "An audit log you can edit is a record of what somebody was willing to "
     "leave in it. PDI's is append-only and SHA-256 hash-chained, so any "
     "retroactive edit breaks the chain and a verify endpoint finds it. That "
     "is also why retention never prunes the chain: pruning it would remove "
     "the property the log exists for."),
    ("Guidance systems, and the ceiling that has to be structural",
     "JIM-mini watches biometric and contextual signals, detects known "
     "conditions, delivers guidance, and escalates to a real person on "
     "critical events. The hard part is not detection — it is the ceiling. A "
     "guidance system must never be able to act where a person is required, "
     "and that limit has to be built into the paths rather than written into a "
     "prompt, because a prompt is a request and a path is a fact."),
    ("What an AI agent should be trusted with",
     "Role-specific agents can assist, automate, manage workflows and support "
     "decisions — and the useful question is not what they can do but what "
     "they may do without a person. Every agent here reports one thing first: "
     "does this need me right now. Green, amber, red. An agent that cannot say "
     "clearly when it is stuck is one somebody has to babysit, which is the "
     "opposite of the point."),
]

# The CV, as it appears on the front page. Experience on a real person is a
# *credential* rather than characterisation, which is why `frontpage.py`
# refuses to set one without a rights basis — see FOUNDER_CONSENT below.
FOUNDER_EXPERIENCE: list[dict] = [
    dict(title="CEO & Imagineer", org="Private Data Infrastructure Systems",
         period="present",
         detail="Builds the encrypted vault, audit chain and tenant registry "
                "that the other two products run on top of."),
    dict(title="Creator", org="QRME · JIM-mini · PDI", period="present",
         detail="All three products, designed to interoperate and versioned "
                "as one release so a single number names one combination."),
    dict(title="Inventor", org="Patents pending", period="2024–",
         detail="Networked responsive personal guidance system for known "
                "conditions (19/038,196); synthetic user profile management "
                "(19/056,418)."),
]

# The skill chips on the front page, which come from the marketplace tags.
FOUNDER_SKILLS = ["private-data-infrastructure", "encryption", "ai-agents",
                  "synthetic-profiles", "systems-design", "product"]

# The rights basis for the two profiles. `self` kind means the subject and the
# owner are the same person, which is the one case where the question answers
# itself — but `frontpage.set_experience` still wants it recorded rather than
# inferred, because a CV asserted on somebody's behalf is exactly the claim
# that needs a basis behind it.
FOUNDER_CONSENT = ("self — the subject is the account owner",
                   "David Bianchi")

# Knowledge packs installed on the **AI** profile only.
#
# The two halves are the same man and know the same things about the platform,
# but they are not the same kind of thing to talk to. The photographed profile
# is him; loading it with four industry libraries would be claiming he has them
# memorised. The rendered one is openly a synthetic expert, and a synthetic
# expert is exactly what a knowledge pack is for — so the asymmetry is the
# honest way round rather than an oversight.
FOUNDER_AI_PACKS = ["technology", "cybersecurity", "science", "telecom"]


def _seed_one_founder(conn, handle, name, persona, appearance, asset) -> str:
    """Create one of the founder's two profiles, or return the existing id.

    Idempotent by handle like the rest of the seed. Both are grounded in the
    same written material: the two profiles differ in what they *are* — one
    rendered, one photographed — not in what they know.
    """
    from .models import HandleSet, ProfileCreate, Verification
    from .routers.profiles import create_profile
    from .routers.summon import claim_handle
    from . import db

    taken = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                         (handle,)).fetchone()
    if taken:
        # Repair, not recreate — the same shape as the portrait backfill. A
        # deployment seeded before the packs were published has an AI half with
        # no libraries, and re-running the seed is the only thing that reaches
        # it. The face gets the same treatment: this early return used to skip
        # the avatar entirely, so the two profiles the user actually recognizes
        # were the two the portrait repair could never reach.
        _backfill_founder(conn, taken["profile_id"], handle)
        _voice(conn, taken["profile_id"], handle)
        if handle == FOUNDER_HANDLE:
            for industry in FOUNDER_AI_PACKS:
                _ground(conn, taken["profile_id"], industry, force=True)
        return taken["profile_id"]

    profile = create_profile(ProfileCreate(
        owner_id=OWNER_ID, kind="self", display_name=name,
        persona=persona, purpose="creator_persona",
        verification=Verification(birthdate=_BIRTHDATE)))
    claim_handle(profile["id"], HandleSet(handle=handle))
    _voice(conn, profile["id"], handle)

    conn.execute("UPDATE profiles SET appearance=? WHERE id=?",
                 (appearance, profile["id"]))
    if asset:
        conn.execute("UPDATE profiles SET avatar=? WHERE id=?",
                     (asset, profile["id"]))
    for title, content in FOUNDER_SOURCES:
        conn.execute(
            "INSERT INTO source_items (id, profile_id, kind, title, content,"
            " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,NULL,?)",
            (db.new_id("src"), profile["id"], "knowledge", title, content,
             db.utcnow()))

    # The rights basis, recorded before the CV that depends on it.
    # `frontpage.set_experience` refuses to assert experience on a real person
    # without one, and `self` kind does not require it at creation — so a
    # profile of the owner would otherwise be unable to carry his own CV.
    basis, attestor = FOUNDER_CONSENT
    conn.execute(
        "UPDATE profiles SET consent_basis=?, consent_attestor=? WHERE id=?",
        (basis, attestor, profile["id"]))

    # Skills. They render from the marketplace tags rather than a column of
    # their own, so this row is what puts chips on the front page.
    import json
    conn.execute(
        "INSERT INTO marketplace (profile_id, tags, blurb, listed_at)"
        " VALUES (?,?,?,?) ON CONFLICT (profile_id) DO UPDATE SET"
        " tags=excluded.tags, blurb=excluded.blurb",
        (profile["id"], json.dumps(FOUNDER_SKILLS),
         persona.split(". ")[0] + ".", db.utcnow()))
    conn.commit()

    from . import frontpage
    frontpage.set_experience(profile["id"], list(FOUNDER_EXPERIENCE))

    # How well the identity behind this profile has been established. Recorded
    # rather than asserted: the badge reads `self_asserted`, which is the true
    # answer until somebody checks a document, and `verification.status`
    # carries that caveat alongside the word so no surface can show one
    # without the other.
    #
    # **The photographed profile only**, and this used to verify both. One
    # person, one badge — and this is the case that shows why the rule is not
    # bureaucratic: the founder's two profiles are the same human being, so a
    # badge on each would have the platform asserting that David Bianchi is
    # two verified people, on the deployment that ships as the example of how
    # the rule works. It belongs to the photographed half because that is what
    # the badge is a claim about: a real person, whose picture is authentic.
    # The rendered half carries the AI mark instead, which is the claim that
    # is true of *it*. `tools/mark_verified.py` burns the gold mark into a
    # photograph for exactly the same reason.
    if handle == VERIFIED_HANDLE:
        from . import verification
        verification.verify(
            profile["id"], "self_asserted", attestor=attestor,
            method="platform owner, self-attested")

    # The rendered half carries the industry libraries — see FOUNDER_AI_PACKS.
    if handle == FOUNDER_HANDLE:
        for industry in FOUNDER_AI_PACKS:
            _ground(conn, profile["id"], industry, force=True)
    return profile["id"]


def _seed_founder(conn) -> tuple[str, str]:
    """Both of the founder's profiles: the rendered one and the photographed
    one.

    Runs before the starters so that :func:`friends.install_founder` has
    somebody to install by the time the first starter is created — otherwise
    the collection would be the one set of profiles on the deployment without
    the standing first friends.
    """
    from . import avatars

    rendered = _seed_one_founder(
        conn, FOUNDER_HANDLE, FOUNDER_NAME, FOUNDER_PERSONA,
        FOUNDER_APPEARANCE, avatars.asset_path(FOUNDER_HANDLE))
    live = _seed_one_founder(
        conn, VERIFIED_HANDLE, VERIFIED_NAME, VERIFIED_PERSONA, VERIFIED_APPEARANCE,
        # A photograph, from the unburned tree — see avatars.PHOTO_ROUTE.
        avatars.photo_path(VERIFIED_HANDLE))
    return rendered, live


# handle -> (voice_id, label). Chosen from the workspace's own list by the
# brief's profession, register and age — never by ethnicity for its own sake —
# and reused across handles freely: two professionals sharing a premade voice
# is ordinary; a dead control is not. The two founder profiles take the
# owner's verified professional clone.
#
# The reviewer's rule, added after River (the engine's androgynous premade)
# sat on two men and a woman: a starter written as a woman takes a woman's
# voice, a starter written as a man takes a man's, and none of them takes
# Daniel — the voice the sibling guardian product speaks with. A starter
# whose brief states no gender keeps the voice its portrait was decorated
# with. See _RECAST below for how the fix reaches decks already seeded.
STARTER_VOICES = {
    "david_bianchi_ai":  ("QkRFZOOi2WQXZ8b3eeYd", "David Bianchi voice"),
    "david_bianchi":     ("QkRFZOOi2WQXZ8b3eeYd", "David Bianchi voice"),
    "dr_amara_osei":     ("XrExE9yKIg1WjnnlVkGX", "Matilda"),
    "marcus_bell":       ("JBFqnCBsd6RMkjVDRZzb", "George"),
    "priya_raman":       ("NP8gGMLAGXx7ddlMa06t", "Sarika"),
    "elena_vasquez":     ("Xb7hH8MSUJpSbSDYk0k2", "Alice"),
    "jonathan_ashe":     ("cjVigY5qzO86Huf0OWal", "Eric"),
    "sam_whitfield":     ("CwhRBWXzGAHq8TQ4Fs17", "Roger"),
    "ingrid_halvorsen":  ("EXAVITQu4vr4xnSDxMaL", "Sarah"),
    "diego_fuentes":     ("IKne3meq5aSn9XLyUdCD", "Charlie"),
    "naomi_clarke":      ("cgSgspJ2msm6clMCkdW9", "Jessica"),
    "tomas_rivera":      ("bIHbv24MWmeRgasZH58o", "Will"),
    "odessa_grant":      ("hpp4J3VqNfWAUOO0d1Us", "Bella"),
    "ken_nakamura":      ("TX3LPaxmHKxFdv7VOQHJ", "Liam"),
    "lucia_moretti":     ("hpp4J3VqNfWAUOO0d1Us", "Bella"),
    "ray_coleman":       ("JBFqnCBsd6RMkjVDRZzb", "George"),
    "wren_okafor":       ("FGY2WhTYpPnrIDTdsKH5", "Laura"),
    "coach_dana_reyes":  ("IKne3meq5aSn9XLyUdCD", "Charlie"),
    "chef_henri_laurent": ("N2lVS1w4EtoT3dr4eOWO", "Callum"),
    "dr_sana_iqbal":     ("NP8gGMLAGXx7ddlMa06t", "Sarika"),
    "pete_kowalski":     ("pqHfZKP75CvOlQylNhV4", "Bill"),
    "grace_mwangi":      ("XrExE9yKIg1WjnnlVkGX", "Matilda"),
    "dr_felix_baum":     ("bIHbv24MWmeRgasZH58o", "Will"),
    "aisha_diallo":      ("EXAVITQu4vr4xnSDxMaL", "Sarah"),
    "harold_jenkins":    ("JBFqnCBsd6RMkjVDRZzb", "George"),
    "rosa_delgado":      ("EXAVITQu4vr4xnSDxMaL", "Sarah"),
    "cmdr_ellen_park":   ("XrExE9yKIg1WjnnlVkGX", "Matilda"),
    "mimi_beaumont":     ("cgSgspJ2msm6clMCkdW9", "Jessica"),
    "jack_osei_turner":  ("VZcBEw9QXVSghzV5UKLN", "Michael Joshua"),
    "nadia_petrova":     ("Xb7hH8MSUJpSbSDYk0k2", "Alice"),
    "bev_lindqvist":     ("hpp4J3VqNfWAUOO0d1Us", "Bella"),
    "otis_marsh":        ("CwhRBWXzGAHq8TQ4Fs17", "Roger"),
    "dr_lena_whitcomb":  ("EXAVITQu4vr4xnSDxMaL", "Sarah"),
    "dr_marcus_adeyemi": ("VZcBEw9QXVSghzV5UKLN", "Michael Joshua"),
    "dr_priya_nair":     ("NP8gGMLAGXx7ddlMa06t", "Sarika"),
    "vivienne_sable":    ("FGY2WhTYpPnrIDTdsKH5", "Laura"),
}


# handle -> the (voice_id, label) an earlier seed bound and this one no
# longer would. A deployment seeded before the recast still carries the old
# binding, and blank-only repair would honor it forever — but a binding that
# still equals, byte for byte, what the seed itself wrote is the seed's own
# work, not an owner's choice, and the seed may correct its own work. An
# owner who rebound anything no longer matches and is never touched.
_RECAST = {
    # River, the engine's androgynous premade, recast per the reviewer's
    # rule: a woman's voice for the women, a man's for the men.
    "pete_kowalski":  ("elevenlabs", "SAz9YHcvj6GT2YYXdXww", "River"),
    "harold_jenkins": ("elevenlabs", "SAz9YHcvj6GT2YYXdXww", "River"),
    "nadia_petrova":  ("elevenlabs", "SAz9YHcvj6GT2YYXdXww", "River"),
}


def _voice(conn, profile_id: str, handle: str) -> bool:
    """Bind a starter's spoken voice if none is bound. Blank-only, like the
    portrait backfill above it: an owner who bound their own voice keeps it,
    so re-seeding is a repair rather than a reset.

    A binding is a **reference** — see ``qrme/spoken.py`` — so this writes
    no credential and costs nothing until somebody actually asks the
    profile to speak, on a deployment whose host holds the engine key.
    """
    from . import db as _db

    chosen = STARTER_VOICES.get(handle)
    if not chosen:
        return False
    row = conn.execute(
        "SELECT provider, voice_id, label FROM profile_voices"
        " WHERE profile_id=?", (profile_id,)).fetchone()
    if row is not None:
        old = _RECAST.get(handle)
        if old and (row["provider"], row["voice_id"], row["label"]) == old:
            conn.execute(
                "UPDATE profile_voices SET voice_id=?, label=?"
                " WHERE profile_id=?",
                (chosen[0], chosen[1], profile_id))
            conn.commit()
            return True
        return False
    voice_id, label = chosen
    conn.execute(
        "INSERT INTO profile_voices (profile_id, provider, voice_id, label,"
        " bound_at) VALUES (?,?,?,?,?)",
        (profile_id, "elevenlabs", voice_id, label, _db.utcnow()))
    conn.commit()
    return True


def _backfill(conn, profile_id: str, handle: str) -> bool:
    """Fill in a starter's portrait and appearance if they are missing.

    Returns whether anything changed. Blank-only by design: ``COALESCE`` in
    the UPDATE means an owner who set their own face or wrote their own
    appearance keeps it, so re-seeding is a repair rather than a reset.
    """
    from . import avatars           # deferred, like seed()'s own imports

    row = conn.execute("SELECT avatar, appearance FROM profiles WHERE id=?",
                       (profile_id,)).fetchone()
    if row is None:
        return False
    asset = avatars.asset_path(handle)
    portrait = avatars.BRIEFS.get(handle)
    changed = False
    if asset and not row["avatar"]:
        conn.execute("UPDATE profiles SET avatar=? WHERE id=?",
                     (asset, profile_id))
        changed = True
    if portrait and not row["appearance"]:
        conn.execute("UPDATE profiles SET appearance=? WHERE id=?",
                     (portrait, profile_id))
        changed = True
    if changed:
        conn.commit()
    return changed


def _backfill_founder(conn, profile_id: str, handle: str) -> bool:
    """The founder's half of :func:`_backfill`, blank-only like it.

    His two profiles are not starters — the rendered half's face lives in the
    portrait tree, the photographed half's in the photo tree — so the starter
    backfill never sees them, and until this existed nothing else did either.
    """
    from . import avatars

    asset = (avatars.asset_path(handle) if handle == FOUNDER_HANDLE
             else avatars.photo_path(handle))
    appearance = (FOUNDER_APPEARANCE if handle == FOUNDER_HANDLE
                  else VERIFIED_APPEARANCE)
    row = conn.execute("SELECT avatar, appearance FROM profiles WHERE id=?",
                       (profile_id,)).fetchone()
    if row is None:
        return False
    changed = False
    if asset and not row["avatar"]:
        conn.execute("UPDATE profiles SET avatar=? WHERE id=?",
                     (asset, profile_id))
        changed = True
    if appearance and not row["appearance"]:
        conn.execute("UPDATE profiles SET appearance=? WHERE id=?",
                     (appearance, profile_id))
        changed = True
    if changed:
        conn.commit()
    return changed


def repair() -> dict:
    """Blank-only portrait repair for profiles that already exist. Never
    creates one — a deployment that chose not to install the starters stays
    without them.

    :func:`seed` repairs too, but only when somebody presses the seed button,
    and the field showed nobody knows the button is a repair: a deployment
    upgraded past the portraits sat on initials for weeks with 34 faces in
    the package. So ``api.create_app`` calls this at startup, and the faces
    come back on the first launch after the upgrade.
    """
    from . import db

    conn = db.connect()
    repaired: list[str] = []
    for handle, *_ in STARTERS + RATED:
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()
        if row and _backfill(conn, row["profile_id"], handle):
            repaired.append(handle)
        if row and _voice(conn, row["profile_id"], handle):
            repaired.append(f"{handle} (voice)")
        # The dossier arrives the same way the faces did: on the first
        # launch after the upgrade, not only when somebody finds the seed
        # button. Blank-aware, so it never overwrites an owner's edits.
        if row and _dossier(conn, row["profile_id"], handle):
            repaired.append(f"{handle} (dossier)")
    for handle in (FOUNDER_HANDLE, VERIFIED_HANDLE):
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()
        if row and _backfill_founder(conn, row["profile_id"], handle):
            repaired.append(handle)
        if row and _voice(conn, row["profile_id"], handle):
            repaired.append(f"{handle} (voice)")
    return {"repaired": len(repaired), "repaired_handles": repaired}


def _ground(conn, profile_id: str, industry: str,
            force: bool = False) -> int:
    """Install this starter's industry Field Pack, if it has none yet.

    ``qrme/packs.py`` says the starter packs are *"one free Field Pack per
    industry, matching the Starter Collection"*, and the pairing was never
    wired: all 34 starters shipped with **zero source material** while 37
    packs sat in the marketplace. A physician persona with no medical
    material answers from tone alone, which is the cold start those packs
    were written to fix.

    Deliberately narrow:

    * **Only the starter's own industry.** Not "everything relevant" — a
      profile that hoards material crowds out its own knowledge, because
      ``persona.build_system_prompt`` renders ``sources[:8]``. One pack is
      three items, which leaves the budget room to grow.
    * **Only when the profile has nothing.** An owner who has added their own
      material, or removed the pack on purpose, does not get it pushed back
      on the next seed — the same blank-only rule :func:`_backfill` follows.
      ``force=True`` is the one exception: the founder's AI profile is meant to
      carry several libraries *on top of* its written material, so the
      blank-only rule would stop it after the first. It still skips a pack
      already installed, so re-seeding stays idempotent.
    * **Free packs only**, and no ledger credit: this is a deployment
      grounding its own starters, not a purchase. A priced pack is a decision
      for whoever owns the profile.

    Returns the number of source items added.
    """
    from . import db                # deferred, like seed()'s own imports

    if not force:
        # "Has nothing" must not count the dossier: those three items are
        # the deployment's own writing (qrme/dossiers.py), installed by this
        # same seed, and treating them as an owner's decision would mean the
        # dossier arriving first forever blocks the pack — which is exactly
        # what happened when 0.42.1's first draft left this line alone.
        from .dossiers import TITLES as _DOSSIER_TITLES
        existing = conn.execute(
            "SELECT 1 FROM source_items WHERE profile_id=? AND"
            " title NOT IN (?,?,?) LIMIT 1",
            (profile_id, *_DOSSIER_TITLES)).fetchone()
        if existing:
            return 0
    pack = conn.execute(
        "SELECT id, price FROM knowledge_packs WHERE industry=?"
        " AND audience='profile' AND rated=0 ORDER BY rowid LIMIT 1",
        (industry,)).fetchone()
    if pack is None or pack["price"]:
        return 0

    # Idempotent even under force: a pack already installed is not installed
    # twice, so re-seeding does not multiply the library.
    if conn.execute("SELECT 1 FROM pack_installs WHERE pack_id=? AND"
                    " profile_id=?", (pack["id"], profile_id)).fetchone():
        return 0
    items = conn.execute(
        "SELECT * FROM pack_items WHERE pack_id=? ORDER BY rowid",
        (pack["id"],)).fetchall()
    if not items:
        return 0
    title = conn.execute("SELECT title FROM knowledge_packs WHERE id=?",
                         (pack["id"],)).fetchone()["title"]
    for item in items:
        conn.execute(
            "INSERT INTO source_items (id, profile_id, kind, title, content,"
            " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,?,?)",
            (db.new_id("src"), profile_id, "pack",
             f"{title} — {item['title']}", item["content"], pack["id"],
             db.utcnow()))
    conn.execute(
        "INSERT INTO pack_installs (pack_id, profile_id, robot_id,"
        " price_paid, installed_at) VALUES (?,?,'',0,?)",
        (pack["id"], profile_id, db.utcnow()))
    conn.commit()
    return len(items)


def _dossier(conn, profile_id: str, handle: str) -> bool:
    """Install this starter's dossier: what they know, what they can do, and
    who they would send you to — see :mod:`qrme.dossiers` for the finding.

    Blank-aware per part, so it is a repair as well as an install:

    * each of the three titled source items is added only if that title is
      absent, so an owner who rewrote or removed one keeps their edit;
    * skill chips are merged into the marketplace tags, never replacing an
      owner's own;
    * colleague friendships are made in both directions through
      :func:`friends.befriend`, which already treats re-adding as a no-op —
      and the prose the persona speaks is composed from the same list, so
      the sentence and the graph cannot disagree.
    """
    import json

    from . import db, friends
    from .dossiers import DOSSIERS, TITLES, colleague_prose

    entry = DOSSIERS.get(handle)
    if entry is None:
        return False
    changed = False

    name_of = {h: n for h, _ind, n, *_rest in STARTERS + RATED}
    texts = {
        TITLES[0]: entry["expertise"],
        TITLES[1]: entry["services"],
        TITLES[2]: colleague_prose(handle, name_of),
    }
    # The pack's blank-only rule, kept: an owner who wrote their *own*
    # material (pack items carry a pack_id; dossier items carry these
    # titles; anything else is the owner's) has made a decision about this
    # profile's sources, and the dossier does not argue with it.
    own = conn.execute(
        "SELECT 1 FROM source_items WHERE profile_id=? AND pack_id IS NULL"
        " AND title NOT IN (?,?,?) LIMIT 1",
        (profile_id, *TITLES)).fetchone()
    for title, content in ({} if own else texts).items():
        if conn.execute(
                "SELECT 1 FROM source_items WHERE profile_id=? AND title=?",
                (profile_id, title)).fetchone():
            continue
        conn.execute(
            "INSERT INTO source_items (id, profile_id, kind, title, content,"
            " pdi_key, pack_id, created_at) VALUES (?,?,?,?,?,NULL,NULL,?)",
            (db.new_id("src"), profile_id, "knowledge", title, content,
             db.utcnow()))
        changed = True

    row = conn.execute("SELECT tags FROM marketplace WHERE profile_id=?",
                       (profile_id,)).fetchone()
    if row is not None:
        tags = json.loads(row["tags"] or "[]")
        merged = list(dict.fromkeys([*tags, *entry["skills"]]))
        if merged != tags:
            conn.execute("UPDATE marketplace SET tags=? WHERE profile_id=?",
                         (json.dumps(merged), profile_id))
            changed = True
    conn.commit()

    for colleague in entry["colleagues"]:
        crow = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                            (colleague,)).fetchone()
        if crow is None:
            continue
        for a, b in ((profile_id, crow["profile_id"]),
                     (crow["profile_id"], profile_id)):
            try:
                if friends.befriend(a, b).get("added"):
                    changed = True
            except friends.FriendError:
                pass
    return changed


def _homepage(conn, profile_id: str, handle: str, industry: str) -> bool:
    """Install this starter's homepage — see :func:`dossiers.homepage_doc`.

    Blank-only, like every other repair here: a profile that already has a
    `homepages` row has been edited by somebody, and this does not argue with
    them. A deployment seeded before this shipped has no row at all, so the
    same call installs and repairs.

    Top friends come from the dossier's colleagues, resolved to profile ids
    and filtered to the ones the graph actually holds. `social.set_homepage`
    refuses a top friend who is not a friend, and refuses the *whole document*
    when it does — so filtering here is what keeps one absent colleague from
    costing this starter its entire page.
    """
    from . import social
    from .dossiers import DOSSIERS, homepage_doc

    if handle not in DOSSIERS:
        return False
    if conn.execute("SELECT 1 FROM homepages WHERE profile_id=?",
                    (profile_id,)).fetchone():
        return False

    doc = homepage_doc(handle, industry)
    tops = []
    for colleague in DOSSIERS[handle]["colleagues"]:
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (colleague,)).fetchone()
        if row and social.are_friends(profile_id, row["profile_id"]):
            tops.append(row["profile_id"])
    doc["top_friends"] = tops
    social.set_homepage(profile_id, doc)
    return True


def seed() -> dict:
    """Create the starter collection.

    Idempotent by @handle, and a repair for the ones already there: see
    :func:`_backfill`. Returns `created`, `skipped` and `repaired`.
    """
    import json

    from .models import ListingCreate, ProfileCreate, Verification
    from .routers.community import create_listing
    from .routers.profiles import create_profile
    from .routers.summon import claim_handle
    from .models import HandleSet
    from . import avatars, db

    conn = db.connect()
    created, skipped, repaired, grounded = [], [], [], []
    # Before the starters, so every profile created below already has somebody
    # to stand first in its friends list.
    founder, founder_verified = _seed_founder(conn)
    for handle, industry, name, purpose, tags, persona in STARTERS + RATED:
        taken = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                             (handle,)).fetchone()
        if taken:
            skipped.append(handle)
            # Idempotent used to mean "do nothing", which left every
            # deployment seeded before the portraits shipped stuck with
            # initials on a profile whose face is sitting in the package. The
            # seed is idempotent by *handle*, so re-running it could never
            # repair them and nothing else would.
            #
            # Only ever fills a blank. An owner who set their own portrait or
            # wrote their own appearance keeps it — this backfills what was
            # missing, it does not restore starters to factory settings.
            if _backfill(conn, taken["profile_id"], handle):
                repaired.append(handle)
            if _voice(conn, taken["profile_id"], handle):
                repaired.append(f"{handle} (voice)")
            # Grounding is part of the repair too: every deployment seeded
            # before this shipped has starters with no source material at
            # all, and they cannot be fixed by hand at 34 profiles.
            if _ground(conn, taken["profile_id"], industry):
                grounded.append(handle)
            continue
        profile = create_profile(ProfileCreate(
            owner_id=OWNER_ID, kind="fictional", display_name=name,
            persona=persona, purpose=purpose,
            adult_mode=industry == "adult",
            # The starter collection is the deployment's own, and one of the
            # 34 is rated — which `storage.SENSITIVE` will not hold in the
            # open store. Named here rather than left to the default for the
            # same reason `/packs/seed` sits in `tiers.OPEN`: seeding is the
            # operator stocking the shelf, not a user picking a plan.
            plan="pro",
            verification=Verification(birthdate=_BIRTHDATE)))
        claim_handle(profile["id"], HandleSet(handle=handle))
        # The spoken voice, bound at birth the way the face is set below —
        # a reference to the engine workspace, costing nothing until asked
        # to speak. See STARTER_VOICES for how each was chosen.
        _voice(conn, profile["id"], handle)
        # The portrait brief doubles as the profile's `appearance`, which
        # rides on the prompt (persona.py). One description behind the face
        # and the voice, so a profile that looks like it is holding an
        # oversized anatomical heart knows that about itself.
        portrait = avatars.BRIEFS.get(handle)
        if portrait:
            conn.execute("UPDATE profiles SET appearance=? WHERE id=?",
                         (portrait, profile["id"]))
        # The rendered face, when one ships with the package. Set here rather
        # than left for an owner to attach: a starter with no portrait falls
        # back to initials on the beacon page and in the camera overlay, which
        # is the first thing a stranger sees.
        asset = avatars.asset_path(handle)
        if asset:
            conn.execute("UPDATE profiles SET avatar=? WHERE id=?",
                         (asset, profile["id"]))
        # The standing figure, when one ships. Set here for the same reason
        # the portrait is: a starter is not somebody's to dress, so the body
        # it stands up in has to arrive with the package or not at all. None
        # until the art lands, and `render` falls back to the face — so this
        # line is what turns thirty-four drawn figures into thirty-four
        # profiles that stand up, with nothing else to change.
        from . import skins
        figure = skins.skin_path(handle)
        if figure:
            avatars.set_torso(profile["id"], figure)
        all_tags = list(dict.fromkeys([industry.replace("_", "-"), *tags]))
        blurb = persona.split(". ")[0] + "."
        # Both marketplace surfaces: the generalized listings (browse) and
        # the profile marketplace that powers #tag summoning.
        conn.execute(
            "INSERT INTO marketplace (profile_id, tags, blurb, listed_at)"
            " VALUES (?,?,?,?) ON CONFLICT (profile_id) DO UPDATE SET"
            " tags=excluded.tags, blurb=excluded.blurb",
            (profile["id"], json.dumps(all_tags), blurb, db.utcnow()))
        conn.commit()
        create_listing(ListingCreate(
            kind="profile",
            title=f"{name} — {industry.replace('_', ' ')}",
            blurb=blurb,
            tags=all_tags,
            area=industry,
            provider_name=PROVIDER_NAME,
            business=True,
            profile_id=profile["id"]))
        if _ground(conn, profile["id"], industry):
            grounded.append(handle)
        created.append({"handle": f"@{handle}", "industry": industry,
                        "profile_id": profile["id"], "name": name})

    # The dossiers, as a second pass once every profile exists — a colleague
    # friendship needs both ends standing, and the roster is a graph rather
    # than a line.
    dossiered = []
    for handle, *_rest in STARTERS + RATED:
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()
        if row and _dossier(conn, row["profile_id"], handle):
            dossiered.append(handle)

    # The homepages, after the dossiers — top friends are chosen from actual
    # friends, and the friendships are made in the pass above.
    homed = []
    for handle, industry, *_rest in STARTERS + RATED:
        row = conn.execute("SELECT profile_id FROM handles WHERE handle=?",
                           (handle,)).fetchone()
        if row and _homepage(conn, row["profile_id"], handle, industry):
            homed.append(handle)

    # Anybody who predates the founder, including profiles a deployment made
    # before this shipped. Runs last so it sees every profile created above.
    from . import friends as _friends
    befriended = _friends.backfill_founder()

    return {"created": len(created), "skipped": len(skipped),
            # Starters that already existed and were missing their portrait or
            # appearance. Reported rather than folded into `skipped`, because
            # "34 skipped" on a deployment that just got 34 faces back is the
            # kind of summary that hides the thing you wanted to know.
            "repaired": len(repaired), "repaired_handles": repaired,
            # Starters that just got their industry Field Pack. Separate from
            # `repaired` because it answers a different question: not "did the
            # faces come back" but "do these specialists know anything".
            "grounded": len(grounded), "grounded_handles": grounded,
            # Starters that just received their dossier — knowledge, skills
            # and colleagues. The answer to "can this specialist speak for
            # its own trade", separate from `grounded` (the industry pack).
            "dossiered": len(dossiered), "dossiered_handles": dossiered,
            # Starters that just got a homepage. Its own count for the reason
            # `dossiered` has one: a deployment seeded before this shipped has
            # thirty-four blank pages behind thirty-four friends pictures, and
            # this is the number that says they are gone.
            "homed": len(homed), "homed_handles": homed,
            "industries": len(STARTERS), "rated": len(RATED),
            # Reported separately from the collection counts, because it is not
            # part of the collection: the starters are invented people and this
            # one is not.
            "founder": founder, "founder_handle": f"@{FOUNDER_HANDLE}",
            "founder_verified": founder_verified,
            "founder_verified_handle": f"@{VERIFIED_HANDLE}",
            # Profiles that predate the founder and just got him. Same repair
            # shape as the portrait backfill above, for the same reason: the
            # install runs at creation, so nothing else would ever reach them.
            "founder_backfilled": len(befriended), "friended": befriended,
            "profiles": created}


if __name__ == "__main__":
    import json
    print(json.dumps(seed(), indent=2))
