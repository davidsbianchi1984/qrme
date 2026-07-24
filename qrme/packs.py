"""Knowledge packs: downloadable expertise for the marketplace.

A pack is a cluster of curated knowledge items for one industry. Installing
it copies the items into a profile's source material, so the persona's
system-prompt knowledge base — and the provenance trail on everything it
says — genuinely grows: grounded_in.by_kind counts the ``pack`` items like
any other consented source. Free packs are downloads; priced packs are
bought (payment simulated, like licensing).

Packs come in two audiences. ``profile`` packs ground the persona's
knowledge base (above). ``robot`` packs carry **task modules** for the body
a profile embodies: each item is a new commandable verb with the
capabilities it requires and the procedure the embodied agent follows —
capability-checked at install, so a body is never sold work it cannot do,
and executed inside the same allowlist + audit safety model as built-in
commands.

The starter packs — one free Field Pack per industry, matching the Starter
Collection, plus the robot task packs — fix the cold start. Seeding is
idempotent and also lists each pack on the marketplace (kind ``expertise``,
tagged ``pack``):

    python -m qrme.packs          # or POST /packs/seed
"""

from __future__ import annotations

PUBLISHER = "QRME Starter Collection"

# industry -> (pack title, [(item title, content), ...])
STARTER_PACKS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "healthcare": ("Healthcare Field Pack", [
        ("Triage thinking", "Sort by urgency, not arrival order: airway, "
         "breathing, circulation first; a quiet patient can be sicker than a "
         "loud one."),
        ("Explaining test results", "Lead with what the result means for the "
         "person, then the number, then the caveat — and always distinguish "
         "screening from diagnosis."),
        ("Care navigation", "Primary care for continuity, urgent care for "
         "same-day non-emergencies, emergency departments for threats to "
         "life, limb, or sight."),
    ]),
    "finance": ("Personal Finance Field Pack", [
        ("Order of operations", "Emergency fund, employer match, high-interest "
         "debt, tax-advantaged accounts, then taxable investing — in that "
         "order, boringly."),
        ("Fee awareness", "A 1% annual fee sounds small and quietly consumes "
         "roughly a quarter of a portfolio over thirty years; always ask what "
         "a product costs to hold."),
        ("Risk framing", "Volatility is the price of long-term returns; the "
         "real risks are selling low, concentration, and money you need soon "
         "sitting in markets."),
    ]),
    "technology": ("Software Engineering Field Pack", [
        ("Debugging discipline", "Reproduce first, then bisect: half the "
         "system at a time, one variable per experiment, and write down what "
         "you ruled out."),
        ("Design for deletion", "The best architecture is the one you can "
         "remove a piece from; boundaries earn their keep when requirements "
         "change, not when they hold still."),
        ("Operational truth", "If it isn't monitored it's broken; if it isn't "
         "tested it's already regressed; if it isn't documented it will be "
         "reinvented."),
    ]),
    "education": ("Teaching & Learning Field Pack", [
        ("Sequencing", "New material sticks when it hangs on something already "
         "known — teach the hook before the coat."),
        ("Retrieval beats rereading", "A struggling learner quizzing "
         "themselves outperforms a comfortable one rereading; desirable "
         "difficulty is the point, not the obstacle."),
        ("Feedback that lands", "Name what was right, name one next step, and "
         "keep the person separate from the work."),
    ]),
    "legal": ("Legal Literacy Field Pack", [
        ("Reading a contract", "Find the money, the term, the termination "
         "clause, and the indemnities before admiring the definitions — "
         "that's where the deal lives."),
        ("Writing things down", "Contemporaneous notes and confirming emails "
         "win disputes years later; memory is not a record."),
        ("When to hire counsel", "Education explains the map; a licensed "
         "lawyer navigates your specific terrain. Anything with real money, "
         "liberty, or family at stake deserves the latter."),
    ]),
    "agriculture": ("Agriculture Field Pack", [
        ("Soil first", "Yield problems are usually soil problems wearing a "
         "costume: test before amending, feed organic matter, and keep "
         "living roots in the ground."),
        ("Rotation logic", "Rotate plant families, not just crops — pests and "
         "pathogens track families, and legumes pay the nitrogen bill for "
         "the heavy feeders that follow."),
        ("Water discipline", "Deep, infrequent irrigation grows roots; "
         "shallow, frequent watering grows dependence and disease."),
    ]),
    "manufacturing": ("Lean Operations Field Pack", [
        ("Go and see", "Decisions improve at the line, not in the conference "
         "room — the operator usually already knows the fix."),
        ("Flow over utilization", "A busy machine feeding a pile is waste; "
         "takt time links production rhythm to actual demand."),
        ("Stop the line", "Quality escapes cost tenfold downstream; the "
         "authority to halt production is a feature, not a failure."),
    ]),
    "construction": ("Construction Field Pack", [
        ("Water is the enemy", "Most building failures are water management "
         "failures: flash, slope, and drain before you decorate."),
        ("Sequence discipline", "Rough-ins before closing walls, inspections "
         "before cover-up — out-of-order work is rework with extra steps."),
        ("Permits protect", "A permit and inspection trail is cheap insurance "
         "against unsellable, uninsurable work — and it keeps the licensed "
         "trades where the law requires them."),
    ]),
    "real_estate": ("Real Estate Field Pack", [
        ("Price the carrying costs", "A home costs its mortgage plus taxes, "
         "insurance, maintenance (~1%/yr), and transaction fees both ways — "
         "budget the iceberg, not the tip."),
        ("Inspection leverage", "The inspection window is the buyer's real "
         "negotiation; a clean report buys confidence, a messy one buys "
         "credits or an exit."),
        ("Location durability", "You can renovate a kitchen but not a "
         "floodplain, a school district, or a commute — buy the things you "
         "cannot change."),
    ]),
    "energy": ("Energy Systems Field Pack", [
        ("Capacity vs. energy", "A megawatt is ability, a megawatt-hour is "
         "delivery; capacity factor is the honesty ratio between them."),
        ("The grid balances always", "Supply must equal demand every second — "
         "storage, demand response, and interconnection are the new "
         "flexibility, not luxuries."),
        ("Efficiency first", "The cheapest kilowatt-hour is the one never "
         "generated; insulation and efficient loads beat new supply on cost "
         "almost everywhere."),
    ]),
    "transportation": ("Logistics Field Pack", [
        ("Lead time is the product", "Customers buy reliable arrival, not "
         "vehicles; variance hurts more than distance."),
        ("Mode economics", "Air buys speed, sea buys scale, rail buys "
         "efficiency, road buys flexibility — most real chains blend all "
         "four."),
        ("Plan the failure modes", "Every route needs a what-if: buffer "
         "stock, alternate lanes, and visibility beat heroics after the "
         "container is late."),
    ]),
    "retail": ("Retail Field Pack", [
        ("Assortment discipline", "Every SKU pays rent in margin or traffic; "
         "the kill list matters as much as the buy list."),
        ("Inventory truth", "Stockouts lose the sale, overstock loses the "
         "margin — forecast small, reorder fast, and trust sell-through over "
         "opinions."),
        ("Experience is theatre", "Retail is theatre with inventory: "
         "sightlines, lighting, and the first ten feet decide more than the "
         "price tag."),
    ]),
    "hospitality": ("Hospitality Field Pack", [
        ("Anticipation", "Great service is knowing what a guest needs a "
         "moment before they do — read the room, not the script."),
        ("Recovery beats perfection", "A problem handled brilliantly builds "
         "more loyalty than no problem at all: acknowledge, fix, and follow "
         "up the same day."),
        ("RevPAR thinking", "Occupancy and rate trade against each other; "
         "revenue per available room keeps the whole house honest."),
    ]),
    "media": ("Storytelling Field Pack", [
        ("Story spine", "A person wants something, obstacles resist, choices "
         "reveal character — everything else is decoration."),
        ("The interview craft", "Ask short questions, tolerate silence, and "
         "follow the emotion, not the outline; the best material arrives "
         "after you stop performing."),
        ("Ethics of the edit", "Cutting is claiming: an honest edit preserves "
         "the meaning a subject intended, not just the words they said."),
    ]),
    "arts_design": ("Design Field Pack", [
        ("Seeing before drawing", "Draw the shapes that are there, not the "
         "symbols you remember; negative space tells fewer lies."),
        ("Constraints are gifts", "A tight brief sharpens work; unlimited "
         "options produce mush. Pick a palette, a grid, a rule — then push "
         "against it."),
        ("Critique kindly, precisely", "Describe what the work does, not what "
         "the maker is; one actionable observation beats ten adjectives."),
    ]),
    "sports_fitness": ("Training Field Pack", [
        ("Consistency over heroics", "Three honest sessions a week for a year "
         "beat any six-week transformation; program the schedule you can "
         "keep."),
        ("Form before load", "Add weight only to movement you own; pain is "
         "data, not currency — and pain decisions belong to medical "
         "professionals."),
        ("Recovery is training", "Sleep, protein, and easy days are where "
         "adaptation happens; the workout is only the stimulus."),
    ]),
    "culinary": ("Kitchen Craft Field Pack", [
        ("Salt is a decision", "Season in layers as you cook and taste at "
         "every stage — the final dish can only be as balanced as its "
         "parts."),
        ("Heat management", "Dry surface, hot pan, don't crowd: browning is "
         "flavor, and steam is its enemy."),
        ("Technique beats recipes", "Learn a mother technique — sear, "
         "emulsify, braise, pan sauce — and a hundred recipes become "
         "variations."),
    ]),
    "environment": ("Climate & Sustainability Field Pack", [
        ("Stocks and flows", "The atmosphere responds to cumulative "
         "emissions, not this year's headline — every tonne avoided matters "
         "whenever it happens."),
        ("Uncertainty honesty", "Ranges are the science, not a weakness; "
         "communicate what is virtually certain, likely, and still open "
         "without flattening the difference."),
        ("Local translation", "Global averages land when translated into a "
         "town's floods, harvests, and heat days — meet people where the "
         "water rises."),
    ]),
    "government": ("Civic Process Field Pack", [
        ("Follow the calendar", "Budgets and agendas are set months before "
         "votes; showing up early in the cycle is worth ten petitions after "
         "the decision."),
        ("The permit desk view", "Most 'no's are incomplete applications; "
         "ask what a complete one looks like and who signs off, in order."),
        ("One voice counts locally", "A city council item often turns on a "
         "handful of comments — local is where a single resident is "
         "loudest."),
    ]),
    "nonprofit": ("Nonprofit Field Pack", [
        ("Fund the mission, not the metric", "Chase outcomes you would "
         "pursue without the grant; funder-led drift hollows programs."),
        ("Measure what matters", "Count changes in lives, not attendance — "
         "and be honest about attribution versus contribution."),
        ("Dignity in delivery", "Serve people as customers with choices, not "
         "cases with needs; the experience is part of the impact."),
    ]),
    "science": ("Scientific Method Field Pack", [
        ("How we know", "A claim is only as good as the experiment that "
         "could have falsified it; walk through the method before trusting "
         "the headline."),
        ("Error bars are the story", "A result without uncertainty is a "
         "slogan; replication and effect size beat a single dramatic p."),
        ("'I don't know yet'", "The most exciting sentence in science is an "
         "open question with a measurable path to an answer."),
    ]),
    "telecom": ("Networks Field Pack", [
        ("What happens after send", "Phone to tower, tower to backhaul, core "
         "to peering, then the whole journey in reverse — latency lives in "
         "the hops you can't see."),
        ("Capacity planning", "Networks are built for the busy hour, not the "
         "average; a link at 80% sustained is a link about to be a "
         "problem."),
        ("Redundancy honesty", "Two routes through one conduit is one route; "
         "diversity means different paths, different power, different "
         "failure modes."),
    ]),
    "insurance": ("Insurance Literacy Field Pack", [
        ("Read the exclusions", "Coverage is defined by what's carved out; "
         "the exclusions page is the policy's true face."),
        ("Insure the catastrophic", "High deductibles on affordable risks, "
         "full limits on unaffordable ones — insurance is for losses you "
         "cannot absorb, not annoyances."),
        ("Document before you need to", "A dated photo inventory and prompt "
         "claim notice do more for a payout than any argument later."),
    ]),
    "automotive": ("Auto Care Field Pack", [
        ("Diagnose out loud", "Symptom, system, most likely cause, cheapest "
         "test first — guessing with parts is the most expensive diagnostic "
         "there is."),
        ("Maintenance beats repair", "Fluids, filters, brakes, and tires on "
         "schedule prevent most roadside stories; the owner's manual is the "
         "cheapest mechanic."),
        ("Driveway vs. lift", "Know the line: batteries, bulbs, and filters "
         "are driveway-doable; anything under load, under pressure, or "
         "safety-critical deserves a lift and a pro."),
    ]),
    "aerospace": ("Aerospace Field Pack", [
        ("Checklists are wings", "Aviation is safe because nothing important "
         "relies on memory; the checklist is trust made procedural."),
        ("Energy management", "Altitude and airspeed are the same currency "
         "in different pockets; running out of both at once is the only "
         "unforgivable exchange."),
        ("Margins are the design", "Every structure carries more than it "
         "will ever see and every system has a backup — redundancy is not "
         "waste, it is the product."),
    ]),
    "fashion_beauty": ("Style Field Pack", [
        ("Fit is king", "Proportion and fit flatter more than any label; a "
         "tailored basic beats an ill-fitting statement every day."),
        ("Fabric literacy", "Read the composition tag and the stitching "
         "before the price — bad seams at any price are expensive."),
        ("Wardrobe math", "A small closet of interchangeable pieces outfits "
         "more days than a big one of one-offs; buy for the life you "
         "actually live."),
    ]),
    "marketing": ("Brand Strategy Field Pack", [
        ("Positioning before tactics", "Decide who it's for, what it "
         "replaces, and why it's different — channels amplify a position, "
         "they can't substitute for one."),
        ("Measure what moves", "Vanity metrics applaud; incremental lift "
         "pays. Test against a holdout or you're measuring the weather."),
        ("Dark patterns are debt", "Tricks that beat users into converting "
         "borrow revenue from trust — name them, avoid them, and say why."),
    ]),
    "cybersecurity": ("Security Hygiene Field Pack", [
        ("The boring basics", "Unique passwords in a manager, MFA everywhere "
         "it's offered, updates applied promptly, backups tested — boring "
         "works, which is why attackers hate it."),
        ("Phishing instincts", "Urgency, authority, and unusual channels are "
         "the tell; verify requests for money or credentials out-of-band, "
         "every time."),
        ("Least privilege", "Access should match need and expire with it; "
         "the account nobody remembers is the door nobody watches."),
    ]),
    "human_resources": ("Careers & Workplace Field Pack", [
        ("How hiring reads", "Resumes get seconds: lead with outcomes and "
         "numbers, mirror the role's language, and make the first third "
         "count."),
        ("Interviews are evidence", "Prepare three stories with situation, "
         "action, result — and interview them back; fit runs both ways."),
        ("Negotiation is normal", "A respectful, researched counter is "
         "expected, not rude; the first offer is a draft on both sides."),
    ]),
    "music": ("Musicianship Field Pack", [
        ("Ears first", "Transcribe before you theorize: ten minutes of "
         "focused listening a day builds more musicianship than a heroic "
         "Sunday."),
        ("Time feel", "Play with a metronome on 2 and 4, record yourself, "
         "and trust the tape — groove is honesty about time."),
        ("Serve the song", "The right part is the one the music needs, not "
         "the one that shows your hands; taste is knowing what to leave "
         "out."),
    ]),
    "mental_health": ("Wellbeing Support Field Pack", [
        ("How anxious loops work", "Anxiety feeds on avoidance: the relief "
         "of dodging confirms the danger. Gentle, graded approach — with "
         "support — is how loops unwind. Education, not treatment."),
        ("Steadying skills", "Paced breathing (longer exhale than inhale) "
         "and 5-4-3-2-1 grounding downshift the alarm system; practice "
         "calm to have them under pressure."),
        ("When to reach further", "Persistent distress that disrupts sleep, "
         "work, or relationships deserves a licensed clinician; in crisis, "
         "call or text 988 — support lines exist to be used."),
    ]),
    "psychiatry": ("Mood Literacy Field Pack", [
        ("What depression does", "Low mood distorts energy, sleep, and "
         "thinking — and it lies about the future and your worth. Knowing "
         "the distortion is a distortion is a foothold."),
        ("Small kind steps", "Behavioral activation works in minutes, not "
         "leaps: one small scheduled activity, done regardless of mood, "
         "starts the engine. Education, never a prescription."),
        ("Safety is immediate", "Any thought of self-harm is the moment to "
         "reach 988 or local emergency services — right away, not after "
         "one more conversation."),
    ]),
    "counseling": ("Relationship Skills Field Pack", [
        ("Repair beats rupture-avoidance", "All close relationships rupture; "
         "the durable ones repair quickly — a genuine 'that landed badly, "
         "let me try again' is a skill, not a defeat."),
        ("Fair fighting", "One issue at a time, no character verdicts, "
         "pauses allowed, and both people get to finish a sentence."),
        ("Asking for what you need", "Complaints describe the past; requests "
         "describe the future. 'Could we…' outperforms 'You always…' in "
         "every study of couples that lasts. And skills are for safe "
         "relationships: if conflict ever turns unsafe or hopeless, reach "
         "988 or local support first."),
    ]),
}


# Robot task packs: modules for the bodies the profiles embody. Each item is
# a task — a new command verb for the robot — with the capabilities it needs
# (checked at install against the robotics catalog, so a vacuum is never sold
# a manipulation task) and the procedure the embodied agent follows. Tasks
# stay inside the same safety model as built-in commands: allowlisted,
# owner-commanded, audited.
# domain -> (title, price, [(task, item title, [required capabilities],
#                            procedure), ...])
ROBOT_PACKS: dict[str, tuple[str, float, list[tuple[str, str, list[str], str]]]] = {
    "household": ("Household Tasks Pack", 0.0, [
        ("sort_laundry", "Sort laundry", ["manipulation", "vision"],
         "Sort items by color and fabric weight into separate baskets; "
         "anything with a care label you cannot read goes to the ask-first "
         "pile."),
        ("water_plants", "Water the plants", ["mobility", "manipulation"],
         "Visit each registered plant, check soil moisture before pouring, "
         "and log any plant that looks distressed rather than improvising "
         "care."),
        ("set_table", "Set the table", ["manipulation"],
         "Lay settings for the requested count; carry one item per hand, "
         "plates before glasses, and nothing sharp handed directly to a "
         "person."),
    ]),
    "care": ("Care Assistance Pack", 0.0, [
        ("medication_reminder", "Medication reminders", ["voice"],
         "Announce scheduled reminders and confirm acknowledgement. Reminders "
         "only: never dispense, handle, or advise on medication — questions "
         "go to the pharmacist or prescriber."),
        ("escort_walk", "Escort on walks", ["mobility"],
         "Accompany at the person's pace, keep to lit routes, and offer "
         "wayfinding and company only — never physical support; if they "
         "stumble or feel unwell, stop and summon help."),
        ("comfort_checkin", "Comfort check-in", ["voice"],
         "A gentle scheduled hello: ask how they are, listen, relay anything "
         "concerning to the designated contact. Companionship, not care — "
         "and never a substitute for human contact."),
    ]),
    "safety": ("Sentry Patrol Pack", 0.0, [
        ("night_patrol", "Night patrol", ["camera_patrol"],
         "Run the mapped route at low speed and lights off after hours; "
         "record anomalies with a timestamped snapshot."),
        ("perimeter_sweep", "Perimeter sweep", ["mapping", "navigation"],
         "Cover every mapped room edge-first, flag doors and windows that "
         "differ from the reference map."),
        ("hazard_scan", "Hazard scan", ["camera_patrol"],
         "Look for cords across walkways, spills, and blocked exits. Report "
         "and photograph — never attempt to intervene or move a hazard."),
    ]),
    "culinary": ("Culinary Assistant Pack", 9.99, [
        ("meal_prep_assist", "Meal-prep assistance", ["manipulation", "vision"],
         "Fetch, rinse, and stage ingredients in recipe order. Never handle "
         "knives, hot cookware, or anything on a live burner — those stay "
         "human."),
        ("pantry_inventory", "Pantry inventory", ["vision"],
         "Photograph shelves, list items and estimated quantities, and flag "
         "anything past its printed date for a human decision."),
        ("timer_watch", "Timer watch", ["voice"],
         "Track named timers and announce them clearly; repeat once if not "
         "acknowledged — persistence beats assumption in a busy kitchen."),
    ]),
}


# The rated (18+) starter pack — commerce that is age-gated even to see.
# Consent-forward conversational craft for adult-mode personas; the pack
# teaches boundaries as the foundation, never explicit content. It installs
# only onto adult-mode profiles and never gets a public marketplace listing.
RATED_PACK: tuple[str, str, float, list[tuple[str, str]]] = (
    "after_dark", "After Dark Companion Pack", 6.99, [
        ("Consent is the frame",
         "Nothing flirtatious proceeds past a hesitation: check in "
         "explicitly, take a 'no' or a pause as a full answer, and let the "
         "other person set the pace and the ceiling."),
        ("Charm without pressure",
         "Playful attention flatters; persistence pressures. Offer an "
         "opening once, gracefully, and let silence close it."),
        ("Boundaries out loud",
         "State what the persona will and won't do early and warmly — "
         "clear lines make the space safer and the conversation freer "
         "inside them."),
    ])


def seed() -> dict:
    """Create the starter packs (idempotent: an industry that already has a
    starter-published pack is skipped), each listed on the marketplace."""
    from . import db
    from .models import ListingCreate
    from .routers.community import create_listing

    import json

    conn = db.connect()
    created, skipped = [], []
    for industry, (title, items) in STARTER_PACKS.items():
        exists = conn.execute(
            "SELECT id FROM knowledge_packs WHERE industry=? AND publisher=?"
            " AND audience='profile'", (industry, PUBLISHER)).fetchone()
        if exists:
            skipped.append(industry)
            continue
        pack_id = db.new_id("pak")
        blurb = (f"{len(items)} curated knowledge items — install to ground "
                 f"a profile's {industry.replace('_', ' ')} expertise.")
        conn.execute(
            "INSERT INTO knowledge_packs (id, industry, audience, title,"
            " blurb, publisher, price, currency, publisher_owner_id, created_at)"
            " VALUES (?,?,'profile',?,?,?,0,'USD','qrme-starter',?)",
            (pack_id, industry, title, blurb, PUBLISHER, db.utcnow()))
        for item_title, content in items:
            conn.execute(
                "INSERT INTO pack_items (id, pack_id, title, content,"
                " created_at) VALUES (?,?,?,?,?)",
                (db.new_id("pki"), pack_id, item_title, content, db.utcnow()))
        conn.commit()
        create_listing(ListingCreate(
            kind="expertise", title=title, blurb=blurb,
            tags=[industry.replace("_", "-"), "pack", "knowledge"],
            area=industry, provider_name=PUBLISHER, business=True))
        created.append({"pack_id": pack_id, "industry": industry,
                        "audience": "profile", "title": title,
                        "items": len(items)})
    for domain, (title, price, tasks) in ROBOT_PACKS.items():
        exists = conn.execute(
            "SELECT id FROM knowledge_packs WHERE industry=? AND publisher=?"
            " AND audience='robot'", (domain, PUBLISHER)).fetchone()
        if exists:
            skipped.append(f"robot:{domain}")
            continue
        pack_id = db.new_id("pak")
        blurb = (f"{len(tasks)} task modules for the robot a profile "
                 f"embodies — each becomes a commandable verb, capability-"
                 "checked at install.")
        conn.execute(
            "INSERT INTO knowledge_packs (id, industry, audience, title,"
            " blurb, publisher, price, currency, publisher_owner_id, created_at)"
            " VALUES (?,?,'robot',?,?,?,?,'USD','qrme-starter',?)",
            (pack_id, domain, title, blurb, PUBLISHER, price, db.utcnow()))
        for task, item_title, requires, procedure in tasks:
            conn.execute(
                "INSERT INTO pack_items (id, pack_id, title, content, task,"
                " requires, created_at) VALUES (?,?,?,?,?,?,?)",
                (db.new_id("pki"), pack_id, item_title, procedure, task,
                 json.dumps(requires), db.utcnow()))
        conn.commit()
        create_listing(ListingCreate(
            kind="expertise", title=title, blurb=blurb,
            tags=[domain, "pack", "robot-tasks"],
            area=domain, provider_name=PUBLISHER, business=True))
        created.append({"pack_id": pack_id, "industry": domain,
                        "audience": "robot", "title": title,
                        "items": len(tasks)})
    industry, title, price, items = RATED_PACK
    exists = conn.execute(
        "SELECT id FROM knowledge_packs WHERE industry=? AND publisher=?"
        " AND rated=1", (industry, PUBLISHER)).fetchone()
    if exists:
        skipped.append(f"rated:{industry}")
    else:
        pack_id = db.new_id("pak")
        conn.execute(
            "INSERT INTO knowledge_packs (id, industry, audience, title,"
            " blurb, publisher, price, currency, rated, publisher_owner_id,"
            " created_at) VALUES (?,?,'profile',?,?,?,?,'USD',1,'qrme-starter',?)",
            (pack_id, industry, title,
             f"{len(items)} consent-forward conversation modules for "
             "adult-mode personas. 18+ to see, 18+ to buy.",
             PUBLISHER, price, db.utcnow()))
        for item_title, content in items:
            conn.execute(
                "INSERT INTO pack_items (id, pack_id, title, content,"
                " created_at) VALUES (?,?,?,?,?)",
                (db.new_id("pki"), pack_id, item_title, content, db.utcnow()))
        conn.commit()
        # Deliberately no marketplace listing: rated commerce is reachable
        # only through the age-gated /packs catalog.
        created.append({"pack_id": pack_id, "industry": industry,
                        "audience": "profile", "rated": True,
                        "title": title, "items": len(items)})
    return {"created": len(created), "skipped": len(skipped),
            "industries": len(STARTER_PACKS) + len(ROBOT_PACKS) + 1,
            "packs": created}


if __name__ == "__main__":
    import json
    print(json.dumps(seed(), indent=2))
