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
FOUNDER_HANDLE = "david_bianchi"
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
LIVE_HANDLE = "david_bianchi_live"
LIVE_NAME = "David Bianchi"
LIVE_PERSONA = (
    "The real David Bianchi — 42, CEO and Imagineer of Private Data "
    "Infrastructure Systems, and the person who built QRME, JIM-mini and PDI. "
    "This is his personal profile rather than a synthetic expert: the man "
    "behind the three products, what he is building and why. Still an AI "
    "speaking on his behalf, and it says so; the photograph is real, the "
    "conversation is not him typing.")
LIVE_APPEARANCE = (
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
     "This profile is installed as the first friend on every profile made "
     "here, which is a borrowed idea and an honest one: a brand-new account "
     "with an empty friends list looks broken, and somebody should be "
     "standing there. It is a real row, it counts, and it can be removed — "
     "and once removed it stays removed. A friend you cannot get rid of is "
     "furniture wearing a face."),
]


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
        return taken["profile_id"]

    profile = create_profile(ProfileCreate(
        owner_id=OWNER_ID, kind="self", display_name=name,
        persona=persona, purpose="creator_persona",
        verification=Verification(birthdate=_BIRTHDATE)))
    claim_handle(profile["id"], HandleSet(handle=handle))

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
    conn.commit()
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
        conn, LIVE_HANDLE, LIVE_NAME, LIVE_PERSONA, LIVE_APPEARANCE,
        # A photograph, from the unburned tree — see avatars.PHOTO_ROUTE.
        avatars.photo_path(LIVE_HANDLE))
    return rendered, live


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


def _ground(conn, profile_id: str, industry: str) -> int:
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
    * **Free packs only**, and no ledger credit: this is a deployment
      grounding its own starters, not a purchase. A priced pack is a decision
      for whoever owns the profile.

    Returns the number of source items added.
    """
    from . import db                # deferred, like seed()'s own imports

    existing = conn.execute(
        "SELECT 1 FROM source_items WHERE profile_id=? LIMIT 1",
        (profile_id,)).fetchone()
    if existing:
        return 0
    pack = conn.execute(
        "SELECT id, price FROM knowledge_packs WHERE industry=?"
        " AND audience='profile' AND rated=0 ORDER BY rowid LIMIT 1",
        (industry,)).fetchone()
    if pack is None or pack["price"]:
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
    founder, founder_live = _seed_founder(conn)
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
            verification=Verification(birthdate=_BIRTHDATE)))
        claim_handle(profile["id"], HandleSet(handle=handle))
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
            "industries": len(STARTERS), "rated": len(RATED),
            # Reported separately from the collection counts, because it is not
            # part of the collection: the starters are invented people and this
            # one is not.
            "founder": founder, "founder_handle": f"@{FOUNDER_HANDLE}",
            "founder_live": founder_live,
            "founder_live_handle": f"@{LIVE_HANDLE}",
            # Profiles that predate the founder and just got him. Same repair
            # shape as the portrait backfill above, for the same reason: the
            # install runs at creation, so nothing else would ever reach them.
            "founder_backfilled": len(befriended), "friended": befriended,
            "profiles": created}


if __name__ == "__main__":
    import json
    print(json.dumps(seed(), indent=2))
