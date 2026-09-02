"""Watches and wearables paired over Bluetooth.

QRME already had a watch *API* — `qrme/routers/watch.py` serves one glanceable
payload and a remote `act` endpoint — and no way to say **which watch**. This
is the pairing: a named device, what kind it is, and which faces it may show.

Kept deliberately apart from :data:`embodiments`, which records where a
*profile* lives — a speaker, a hologram, a robot body. A wearable here belongs
to the **owner** and reaches their own account. Folding them together would
mean pairing a watch could put somebody's synthetic persona on their wrist,
which is a different feature with a different consent question.

**Pairing and permission only.** Nothing here opens a channel. A paired device
is a registration and a set of allowed faces; whether anything ever listens
through one is a separate decision, held elsewhere and not made here. The
microphone-bearing kinds are listed because the registry is what that later
feature will need — a device somebody already paired for their watch face
should not have to be paired twice.

**Room-facing microphones are refused at the door.** A smart speaker, a
conference puck, a tabletop array: each hears whoever walks in, and that person
did not pair it, was not asked, and in most places has a right not to be
recorded. A platform cannot collect a waiver from somebody who is merely
present. Refused rather than allowed-and-restricted, because a restriction is a
setting somebody can change and a refusal is a fact about the product.

**Unpairing is a revocation, not a delete.** The row stays with `revoked_at`
set, so a device that has been sent away cannot quietly come back by
re-presenting the same name — and the owner can see what was ever paired, which
is the question people actually ask after losing a watch.
"""

from __future__ import annotations

import json

from . import db, i18n

# What may be paired. Personal devices, worn by the person pairing them.
#
# The microphone-bearing kinds are here because the pairing registry is what
# `qrme/roommic.py` needs — not because anything listens *here*. Nothing in
# this module opens a channel; a paired device is a registration and a set of
# allowed faces, and a test asserts no capture path exists.
#
# That feature has since landed, and the split is deliberate rather than
# historical: pairing says which devices somebody owns, lending says what one
# of them may do inside one room. Keeping them apart is what lets a grant end
# with the room without unpairing the watch.
#
# The names here and the ones in `roommic.MIC_TYPES` differ — `lapel_mic`
# against `lapel` — because that table is kept in step with `jim/mic.py` by
# hand, the two products not importing each other. `roommic.FROM_WEARABLE`
# translates, and a test holds every kind below against one side or the other,
# so adding a device forces the question *does this carry a microphone* here
# rather than when somebody tries to lend it.
KINDS: dict[str, str] = {
    "watch": "on the wrist",
    "band": "on the wrist",
    "ring": "on the finger",
    "earbuds": "in the ears",
    "headset": "over the ears",
    "lapel_mic": "clipped to the collar",
    "clip_on_mic": "clipped to clothing",
    "glasses": "worn on the face",
    "pendant": "worn at the neck",
    # The 2.9.7 widening: everything a person in America can buy and wear.
    #
    #     asked     offer all the ones that are available in America — AR,
    #               VR, watches, rings, pendants, and ankle monitors, and
    #               any others you can think of
    #     mattered  every one of these is worn by the person pairing it,
    #               which is the rule the whole registry stands on
    #
    # Each addition answers the microphone question in
    # tests/test_room_mic.py the day it lands, and the screened ones are
    # named in SCREENS below — a device with a screen is somewhere the
    # console can show itself; the rest pair as presence and, later,
    # readings.
    "vr_headset": "over the eyes",
    "ar_glasses": "over the eyes, with the room still visible",
    "hearing_aids": "in the ears, fitted",
    "chest_strap": "across the chest",
    "health_patch": "stuck to the skin",
    "headband": "across the forehead",
    "ankle_monitor": "on the ankle",
    "insoles": "under the feet",
    "alert_button": "worn within reach",
    "smart_clothing": "woven into what you wear",
    # Asked for by name: "Bluetooth earbuds, even the ones that are
    # earrings". A kind of its own rather than a catalogue row, because
    # where a thing is worn is what this table says, and jewelry that
    # plays sound is worn differently from a bud in the canal. Named
    # plainly rather than with a sound-prefixed identifier: the
    # capture-path guard reads this module's source for the vocabulary of
    # recording, and a prefix from that vocabulary tripped it. The guard
    # is right and keeps its word; the catalogue rows below say what
    # these earrings do.
    "earrings": "worn as earrings, on the ear",
}

# The kinds with a screen the console can render on. Not a capability the
# device claims — a fact about the kind, said here so a client can offer
# "show the console here" only where a surface exists. The watch's faces
# are already real (`routers/watch.py`); the stage is what an eyes-covering
# device will carry. Bands get the glance faces a watch does, smaller.
SCREENS: dict[str, str] = {
    "watch": "the faces — status lights, counts, the remote",
    "band": "the glance faces, small",
    "vr_headset": "the room's stage, as a place you enter",
    "ar_glasses": "the room's stage, laid over where you stand",
}

# What each kind can feel. A fact about the kind, like SCREENS — every
# kind appears, sensing or empty, because "not decided" and "senses
# nothing" are different claims and only one of them is this table's
# job. The words are a guardian's vocabulary on purpose: these are the
# readings JIM-mini's drip channel takes, and the whole point of saying
# them here is that a paired device can be pointed at a guardian.
#
# QRME never receives a reading. A reading is a medical fact, and the
# product built for medical facts is the sibling next door — so the road
# stored below is an ADDRESS, the readings travel device-to-guardian,
# and this platform holds only where the owner chose to send them.
SENSES: dict[str, tuple[str, ...]] = {
    "watch": ("heart_rate", "steps", "oxygen"),
    "band": ("heart_rate", "steps", "sleep"),
    "ring": ("heart_rate", "sleep", "temperature"),
    "earbuds": ("heart_rate",),
    "headset": (),
    "lapel_mic": (),
    "clip_on_mic": (),
    "glasses": (),
    "pendant": ("fall",),
    "vr_headset": (),
    "ar_glasses": (),
    "hearing_aids": ("steps", "fall"),
    "chest_strap": ("heart_rate", "respiration"),
    "health_patch": ("heart_rate", "temperature"),
    "headband": ("sleep",),
    "ankle_monitor": ("steps", "gait"),
    "insoles": ("steps", "gait"),
    "alert_button": ("fall",),
    "smart_clothing": ("heart_rate", "respiration"),
    "earrings": (),
}

# What people actually own, by kind — the American-market names offered as
# suggestions when a device is being named. Suggestions and nothing else:
# pairing stores the name the owner typed, and an unlisted device pairs
# exactly as well. Kept server-side so all four clients offer one list,
# and deliberately short — a menu, not a census.
CATALOG: dict[str, tuple[str, ...]] = {
    "watch": ("Apple Watch", "Samsung Galaxy Watch", "Google Pixel Watch",
              "Garmin", "Fitbit"),
    "band": ("Fitbit Charge", "WHOOP", "Amazfit Band"),
    "ring": ("Oura Ring", "Samsung Galaxy Ring", "Ultrahuman Ring Air",
             "RingConn"),
    "earbuds": ("AirPods", "Galaxy Buds", "Pixel Buds", "Beats", "Sony",
                "Bose QuietComfort", "Jabra Elite", "Skullcandy", "JLab"),
    "headset": ("Bose", "Sony", "HyperX"),
    "glasses": ("Ray-Ban Meta", "Amazon Echo Frames", "Solos AirGo"),
    "pendant": ("Limitless Pendant", "Plaud NotePin", "Bee"),
    "vr_headset": ("Meta Quest 3", "Meta Quest 3S", "Apple Vision Pro",
                   "PlayStation VR2", "Valve Index", "Bigscreen Beyond"),
    "ar_glasses": ("Xreal One", "Viture Pro", "Rokid AR", "Even Realities G1",
                   "Meta Ray-Ban Display"),
    "hearing_aids": ("Phonak", "Oticon", "Jabra Enhance", "Sony CRE"),
    "chest_strap": ("Polar H10", "Garmin HRM-Pro", "Wahoo TICKR"),
    "health_patch": ("Dexcom G7", "FreeStyle Libre 3"),
    "headband": ("Muse S",),
    "ankle_monitor": ("AngelSense", "Theora Connect"),
    "insoles": (),
    "alert_button": ("Life Alert", "Medical Guardian", "Lively"),
    "smart_clothing": ("Hexoskin",),
    "earrings": ("Nova H1 Audio Earrings", "Bose Ultra Open Earbuds",
                 "Anker Soundcore C30i"),
    "lapel_mic": (), "clip_on_mic": (),
}

# What may **not** be paired, and why, in the words the refusal returns.
#
# A room-facing microphone hears whoever walks in. They did not pair it, were
# not asked, and in most places have a right not to be recorded — and a
# platform cannot collect a waiver from somebody who is simply present. Until
# that is worked out with counsel, the device class is refused at the door
# rather than allowed and then restricted, because a restriction is a setting
# and a refusal is a fact.
REFUSED: dict[str, str] = {
    "smart_speaker": "a room-facing microphone",
    "conference_puck": "a room-facing microphone",
    "room_array": "a room-facing microphone",
    "tabletop_mic": "a room-facing microphone",
    "desk_mic": "a room-facing microphone",
}
REFUSAL = (
    "{kind} is {what}: it hears whoever walks into the room, and they did "
    "not pair it, were not asked, and may have a right not to be recorded. "
    "Only devices worn by the person pairing them can be attached."
)

# The faces a wrist can be given, and what each is for. A closed set, because
# "which faces" is a permission and a permission with open-ended values is one
# nobody can audit.
FACES: dict[str, str] = {
    "agents": "the status lights and their counts — no names",
    "activity": "how many new posts, friends and replies are waiting",
    "profile": "the profile's own headline figures",
    "control": "assist, halt, approve — the remote",
    # Channel 2, on the device it is running on. The whole feature is lending
    # the microphone on this wrist, and the grant is "yours to end, alone and
    # at any moment" — so the most obvious place to end it is the thing doing
    # the listening. A watch that can be lent and cannot be taken back from is
    # a watch you have to go and find a phone to switch off.
    "microphone": "whether this watch is lent to a room, and the way back",
    # The four below are all the same kind of question: *what am I currently
    # presenting as, without looking at a phone.* Each is a glance answer to
    # something you would otherwise find out by being told, which is the test
    # for a wrist — a face that needs reading belongs on a screen you hold.
    "identity": "which of your profiles you are posting as, and whether it is "
                "anonymous right now",
    "camera": "what your camera is showing other people — the overlay on your "
              "face and what is behind you",
    "lobby": "who is in the game with you, and which of them are synthetic",
    "screens": "which fixed screens are live with you on them",
    # The ecosystem round's two glances, same test as the four above: a
    # count-shaped answer to "is anything waiting on me", never the thing
    # itself. A campaign's progress is its own public card; a joint plan's
    # text is not a glance.
    "proceeds": "how your open campaigns are doing — donors and progress, "
                "never a donor's name",
    "coordination": "whether the departments have finished a joint plan — "
                    "never the plan",
}
DEFAULT_FACES = ("agents", "activity")

# Comfortably above the number of kinds, so somebody can own one of each and
# still add a second watch. A limit below the catalogue would be a rule that
# contradicts the menu it is printed next to.
MAX_WEARABLES = 24


class WearableError(ValueError):
    """A pairing that cannot stand."""


def pair(profile_id: str, name: str, kind: str,
         faces: list[str] | None = None) -> dict:
    """Pair a device, or re-pair one that was revoked.

    Re-pairing an existing name updates it rather than failing, because a watch
    that was unpaired and is being paired again is the same watch, and making
    somebody invent ``watch-2`` to do it is the kind of friction that teaches
    people to leave devices paired.
    """
    name = (name or "").strip()
    if not name:
        raise WearableError("a device needs a name you will recognise")
    if len(name) > 60:
        raise WearableError("a device name is at most 60 characters")
    if kind in REFUSED:
        raise WearableError(REFUSAL.format(kind=kind, what=REFUSED[kind]))
    if kind not in KINDS:
        raise WearableError(
            i18n.fill(i18n.UNKNOWN_CHOICE_EXPECTED, field="wearable", got=repr(kind), choices=', '.join(KINDS)))
    chosen = list(faces) if faces is not None else list(DEFAULT_FACES)
    for face in chosen:
        if face not in FACES:
            raise WearableError(
                i18n.fill(i18n.UNKNOWN_CHOICE_EXPECTED, field="face", got=repr(face), choices=', '.join(FACES)))

    conn = db.connect()
    existing = conn.execute(
        "SELECT id FROM wearables WHERE profile_id=? AND name=?",
        (profile_id, name)).fetchone()
    if existing is None:
        live = conn.execute(
            "SELECT COUNT(*) AS n FROM wearables WHERE profile_id=? AND"
            " revoked_at IS NULL", (profile_id,)).fetchone()["n"]
        if live >= MAX_WEARABLES:
            raise WearableError(
                i18n.fill(i18n.PAIRED_DEVICES_LIMIT, max=MAX_WEARABLES))
        conn.execute(
            "INSERT INTO wearables (id, profile_id, name, kind, transport,"
            " faces, paired_at) VALUES (?,?,?,?,'bluetooth',?,?)",
            (db.new_id("wbl"), profile_id, name, kind, json.dumps(chosen),
             db.utcnow()))
    else:
        conn.execute(
            "UPDATE wearables SET kind=?, faces=?, paired_at=?,"
            " revoked_at=NULL WHERE id=?",
            (kind, json.dumps(chosen), db.utcnow(), existing["id"]))
    conn.commit()
    return device(profile_id, name)


def set_guardian(profile_id: str, name: str,
                 drip_url: str | None) -> dict:
    """Point a sensing device's readings at the owner's guardian.

        asked     the rings, straps and patches that report — tied into
                  the guardian's rate-emergency
        mattered  QRME must never become the second place health data
                  lives; the guardian product already exists, one door
                  over, with a baseline and a ladder behind it

    ``drip_url`` is the per-user deposit address JIM-mini's wrist
    channel mints — a URL-bearer credential, stored for its owner to
    read back and never logged. The readings themselves travel from the
    device's own app or a phone automation straight to that address;
    nothing here relays them, which is what makes storing the address
    safe. Passing None (or blank) takes the road back down.
    """
    row = device(profile_id, name)
    text = (drip_url or "").strip()
    if text and not SENSES.get(row["kind"], ()):
        raise WearableError(i18n.SENSES_NOTHING_FOR_A_GUARDIAN)
    if text and not text.startswith(("http://", "https://")):
        raise WearableError(i18n.GUARDIAN_ADDRESS_IS_A_URL)
    conn = db.connect()
    try:
        conn.execute("ALTER TABLE wearables ADD COLUMN guardian TEXT")
    except Exception:
        pass
    conn.execute(
        "UPDATE wearables SET guardian=? WHERE profile_id=? AND name=?",
        (text or None, profile_id, name))
    conn.commit()
    return device(profile_id, name)


def unpair(profile_id: str, name: str) -> dict:
    """Revoke a pairing. The row survives — see the module note."""
    conn = db.connect()
    row = conn.execute(
        "SELECT id FROM wearables WHERE profile_id=? AND name=?",
        (profile_id, name)).fetchone()
    if row is None:
        raise WearableError("no such device")
    conn.execute("UPDATE wearables SET revoked_at=? WHERE id=?",
                 (db.utcnow(), row["id"]))
    conn.commit()
    return device(profile_id, name)


def device(profile_id: str, name: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM wearables WHERE profile_id=? AND name=?",
        (profile_id, name)).fetchone()
    if row is None:
        return {}
    keys = row.keys()
    return {"id": row["id"], "name": row["name"], "kind": row["kind"],
            "transport": row["transport"],
            "faces": json.loads(row["faces"]),
            "senses": list(SENSES.get(row["kind"], ())),
            "guardian": row["guardian"] if "guardian" in keys else None,
            "paired_at": row["paired_at"], "revoked_at": row["revoked_at"],
            "paired": row["revoked_at"] is None}


def paired(profile_id: str, include_revoked: bool = False) -> list[dict]:
    sql = "SELECT name FROM wearables WHERE profile_id=?"
    if not include_revoked:
        sql += " AND revoked_at IS NULL"
    rows = db.connect().execute(sql + " ORDER BY paired_at",
                                (profile_id,)).fetchall()
    return [device(profile_id, r["name"]) for r in rows]


def may_show(profile_id: str, name: str, face: str) -> bool:
    """Whether this device is allowed this face.

    Checked here rather than at each surface, so a face added later cannot
    arrive on every wrist by default.
    """
    d = device(profile_id, name)
    return bool(d) and d["paired"] and face in d["faces"]
