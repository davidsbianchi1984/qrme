"""Community layer: rooms, marketplace listings, providers, and handoffs.

- **Rooms** — multiparty conversations over any channel (chat, voice, video,
  AR, VR) whose participants may be any mix of real users and synthetic
  profiles: user↔user, profile↔profile, or combinations. Every profile turn
  passes moderation; a room with a minor present always runs strict.
- **Listings** — the marketplace, generalized: users and businesses can
  share and market synthetic profiles, content, business expertise, or
  services, browsable by kind, tag, and area.
- **Providers & handoffs** — a directory of real local businesses
  (healthcare, medical, mental health, finance, relationships, career, …)
  and a *consented* handoff: the AI specialist's session summary is packaged,
  sealed in the PDI vault when configured, and released to the provider only
  through a revocable access token.
"""

from __future__ import annotations

import json
import secrets
from datetime import date

from fastapi import APIRouter, HTTPException, Request

from .. import (auth, db, engagement, identity, inbox, llm, marketplace,
                moderation, persona, referral, roommic, society, storage,
                tiers, verification, watermark)
from .. import hands
from ..common import (age_of, clipped, interactor_or_404, profile_or_404,
                      require_interactor, require_owner_or_interactor,
                      source_items)
from ..models import (
    HandoffCreate, ListingCreate, ListingPlace, MarketAssist, MarketPrefs,
    ProviderCreate, ReferralPrepare, ReferralRelease, ReferralReply,
    RoomAllow, RoomCreate, RoomErrand, RoomFace, RoomInvite, RoomMessage,
    RoomMicLend,
    RoomRename,
    RoomSitOut,
)
from .. import i18n

router = APIRouter()

_CHANNEL_NOTES = {
    "chat": "text thread",
    "voice": "live voice; replies rendered in each speaker's voice style",
    "video": "live video call; profiles present as animated avatars",
    "ar": "shared augmented-reality space anchored to the room's location",
    "vr": "shared virtual-reality space; participants meet as avatars",
}

# Standing rooms. The field report behind them: a new user opened the Rooms
# screen, found the list empty, and left — a screen whose whole pitch is
# company greeted them with nobody. These are blueprints, not rooms: reference
# data in the manner of the connector catalog, each one press away from being
# a real room with the presser inside it. Opening one goes through the same
# POST /rooms as typing the topic by hand, so a template grants nothing the
# form does not.
ROOM_TEMPLATES = [
    {"key": "front-porch", "topic": "The Front Porch", "channel": "chat",
     "pitch": "easy talk with whoever wanders past — no agenda, no ending"},
    {"key": "coffee-counter", "topic": "Coffee Counter", "channel": "voice",
     "pitch": "morning voices over whatever is in your cup"},
    {"key": "show-and-tell", "topic": "Show & Tell", "channel": "video",
     "pitch": "bring one thing you made, found, or fixed, and show it"},
    {"key": "book-corner", "topic": "Book Corner", "channel": "chat",
     "pitch": "what you are reading, one chapter at a time"},
    {"key": "game-night", "topic": "Game Night", "channel": "voice",
     "pitch": "party voice for whatever you are playing tonight"},
    {"key": "family-table", "topic": "Family Table", "channel": "video",
     "pitch": "the standing call a scattered family keeps"},
    {"key": "quiet-study", "topic": "Quiet Study", "channel": "chat",
     "pitch": "working alongside each other, mostly in silence"},
    {"key": "town-hall", "topic": "Town Hall", "channel": "voice",
     "pitch": "the open floor: raise anything, everyone hears it"},
    {"key": "workbench", "topic": "The Workbench", "channel": "ar",
     "pitch": "a shared bench anchored where you stand — hold up the work"},
    {"key": "morning-walk", "topic": "Morning Walk", "channel": "ar",
     "pitch": "company on your walk, anchored to the street you are on"},
    {"key": "gallery-walk", "topic": "Gallery Walk", "channel": "vr",
     "pitch": "wander a shared space hung with what the room brings"},
    {"key": "vastscape", "topic": "The Vastscape", "channel": "vr",
     "pitch": "watch together on the big screen, avatars in the scene"},
]


# --------------------------------------------------------------------------- #
# rooms
# --------------------------------------------------------------------------- #

def _room_or_404(room_id: str) -> dict:
    row = db.connect().execute("SELECT * FROM rooms WHERE id=?",
                               (room_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "room not found")
    return dict(row)


def _participants(room_id: str) -> list[dict]:
    # ORDER BY rowid: the order people took their seats IS the seat
    # priority — "we will do it by priority of seats one through eight
    # for rotation." Unordered, the rotation reshuffled whenever SQLite
    # felt like it, which is a rotation in name only.
    rows = db.connect().execute(
        "SELECT kind, ref_id, sitting_out FROM room_participants"
        " WHERE room_id=? ORDER BY rowid", (room_id,)).fetchall()
    return [dict(r) for r in rows]


def _require_in_room(room_id: str, request: Request) -> str:
    """The caller must be one of this room's participants. Returns who.

    Two ways to be in a room, because a room holds two kinds of participant.
    A person is in it if they hold the token of a `user` participant. A
    profile's owner is in it if they hold the owner token of a `profile`
    participant — the profiles are the side being lent the microphone, so
    their owner is exactly who the disclosure is addressed to.

    Nobody else, and an unidentified caller least of all: a room id travels on
    beacons and printed stickers, so "knows the id" cannot stand in for "is
    here".
    """
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required — this room's "
                                 "disclosure is for the people in it")
    for p in _participants(room_id):
        if p["kind"] == "user" and who == {"role": "interactor",
                                           "subject_id": p["ref_id"]}:
            return p["ref_id"]
        if p["kind"] == "profile" and who == {"role": "owner",
                                              "subject_id": p["ref_id"]}:
            return p["ref_id"]
    raise HTTPException(403, "you are not in this room")


def _room_maturity(participants: list[dict]) -> str:
    """A room with a minor present always runs strict."""
    for p in participants:
        if p["kind"] != "user":
            continue
        user = interactor_or_404(p["ref_id"])
        if not user["birthdate"] or age_of(
                date.fromisoformat(user["birthdate"])) < 18:
            return "strict"
    return "balanced"


def _display(kind: str, ref_id: str) -> str:
    if kind == "profile":
        profile = profile_or_404(ref_id)
        return identity.shown_name(profile)
    return interactor_or_404(ref_id)["display_name"]


def _role(kind: str, ref_id: str) -> str | None:
    """What this seat is here for, under the name.

        asked     who is in this room
        mattered  what are they FOR

    "Dr. Amara Osei" and "Dr. Amara Osei · Healthcare" answer different
    questions, and a room full of specialists where nobody says what they
    specialise in makes the reader open three profiles to find out.

    Only for profiles, and only when one has said: a person's seat is the
    person, and inventing a job title for them would be a claim the
    product has no basis for. `None` is a profile that has not said, which
    is most of them and is not a failure — the client draws the name
    alone.
    """
    if kind != "profile":
        return None
    field = (profile_or_404(ref_id).get("industry") or "").strip()
    return field or None


def _verified(kind: str, ref_id: str, room_id: str = "") -> bool:
    """Whether this seat's face is a checked likeness of a real person.

        asked     draw the verified mark on the sphere
        mattered  from what

    The mark used to be burned into the photograph, so the *file* was the
    claim and nothing had to ask. Drawn on the surface instead, it needs a
    fact behind it, and the fact already exists: a verification record
    with a named attestor, which is the same bar the burning tool refused
    to run without. A gold check that a surface draws from nothing is
    worse than no check at all.

    A person's seat is marked from the PICTURE it is showing, which is
    the only checkable fact on that tile.

    The first rule here asked whether the account behind the seat owned a
    profile with a verification record. That was a guess dressed as a
    fact — it says something about a person's other profiles rather than
    about the face on this seat — and it never once fired, which is how
    guesses usually announce themselves.

    The mark is a claim about a LIKENESS. A seat showing a photograph
    that belongs to a verified profile is showing a checked likeness, and
    that is exactly what the gold plate asserted when it was burned into
    that file. So the question is: is this seat putting up
    `/photos/<handle>.webp` for a handle whose profile carries a
    verification record with a named attestor.
    """
    try:
        if kind == "profile":
            record = verification.status(ref_id)
            return bool(record.get("verified") and record.get("attestor"))
        if not room_id:
            return False
        from .. import avatars, roomface

        shown = roomface.showing_in(room_id).get("faces", {}).get(ref_id)
        url = (shown or {}).get("media_url") or ""
        prefix = f"{avatars.PHOTO_ROUTE}/"
        if not (shown or {}).get("showing") == "photo" or not url.startswith(prefix):
            return False
        handle = url[len(prefix):].rsplit(".", 1)[0]
        row = db.connect().execute(
            "SELECT profile_id FROM handles WHERE handle=?", (handle,)).fetchone()
        if row is None:
            return False
        record = verification.status(row["profile_id"])
        return bool(record.get("verified") and record.get("attestor"))
    except Exception:
        return False


def _media_brief(media_id: str | None, read: bool = False,
                 why: str | None = None, whole: int | None = None,
                 kept: int | None = None) -> dict | None:
    """The shareable face of an attachment: kind, serving url, display
    name, and whether the words in it were read. Never the disk path,
    never the uploader's raw filename beyond the display copy
    `media.save` already trimmed.

    `read` is on the wire because the alternative is a person guessing.
    A photograph and a scanned filing land the same way a readable one
    does, and only the deployment knows which of them the profiles in
    this room can actually discuss.

    `why` is the same fact one step finer, as a KEY rather than a sentence
    so the console can say it in its own ten languages: a scan, a locked
    file, or a font this reader could not follow. The person who shared it
    was reading "held, not read" and had no way to tell whether a different
    export would help — which is the question anybody actually has."""
    if not media_id:
        return None
    from .. import media as media_mod

    row = db.connect().execute(
        "SELECT id, kind, filename, name FROM media WHERE id=?",
        (media_id,)).fetchone()
    if row is None:
        return None
    return {"kind": row["kind"],
            "url": f"{media_mod.ROUTE}/{row['filename']}",
            "name": row["name"],
            "read": read,
            "unread_why": None if read else (why or None),
            # How much of it is here, when the cap kept less, and how much
            # there was. Both on the wire because the client cannot derive
            # the first: the cap is a server constant, and a console that
            # hard-coded it would print a stale number the day it changes.
            "chars": (kept or None) if read else None,
            "full_chars": (whole or None) if read else None}


def _read_share(data: bytes, name: str | None,
                on_behalf_of: str | None) -> tuple[str, str, str, int]:
    """The words in a shared file, and the reading carried thereafter.

        asked     can a profile read what somebody hands the room
        mattered  or does it only learn that a file arrived

    It only learned that a file arrived. `_worded` turned an attachment
    into "[shared a file: Response 1.pdf]" and stopped, so a profile in a
    room with a document could name it and nothing else. Field report,
    from the profile's own mouth: "I can see them land, but I can't read
    them from where I'm standing" — which was honest, and was the bug.

    The reader is `briefcase.read_file`, already built for the one-to-one
    conversation: PDF, the zip-family office documents, plain text, and a
    recording through the ears. Nothing new is invented here; the room
    simply gets the reading the pair has had all along.

    Two things it deliberately is not. It is **not** a briefcase row — a
    briefcase belongs to one pair, and the next visitor does not inherit
    it; this belongs to the room, where everybody present already sees the
    file itself. And it is **not** load-bearing: anything that fails to
    read comes back empty, the attachment still lands, and the prompt says
    the file could not be read rather than filling the hole with a guess.
    """
    from .. import briefcase

    try:
        kind, text, read = briefcase.read_file(data, name, on_behalf_of)
    except Exception:                                   # pragma: no cover
        return "", "", "", 0
    if not read or not text.strip():
        # Not read, and WHICH kind of not read. The pair's briefcase gained
        # this first and the room is the other half of the same door — a fix
        # that reaches one of two paths looks exactly like a fix.
        return "", "", briefcase.why_unread(data, kind, read) or "", 0
    # The cap, applied where its cost can be recorded — `_clean` tidies and no
    # longer cuts, so a room share that stored the reader's output raw would
    # keep a whole filing in a transcript row.
    whole = len(text)
    text = briefcase.capped(text)
    try:
        digest = briefcase.distill(text, name or "a shared file")
    except Exception:                                   # pragma: no cover
        digest = text[:600]
    return text, digest, "", (whole if whole > len(text) else 0)


def _read_link(message: str, on_behalf_of: str | None) -> tuple[str, str, str]:
    """The first link in a person's room message, read on the way in.

    The pair conversation has read handed links since the briefcase round
    (``interaction._handed_link_block``); the room never made the call, so
    a link pasted into a room was inert text to every seat — "fifth link,
    same wall", said a profile, honestly, about a wall this module was.

        asked     can a profile in a room open the link I pasted
        mattered  the same fetch the chat door uses was never called here

    Read once at post time and kept on the row, the share door's own
    economy: every profile's every later turn carries the reading without
    a refetch. Returns ``(words, digest, why)`` — words and a digest when
    the page was read, else a why key the prompt words honestly:
    ``offline`` (this deployment does not fetch), ``unreachable`` (it
    tried), ``empty`` (reached, but no words to take away — a page drawn
    entirely by scripts reads like this). Never load-bearing: a link that
    cannot be read still lands as the message it rode in on.
    """
    from .. import briefcase, offline, scrape
    from .interaction import _URL_RE

    m = _URL_RE.search(message or "")
    if not m:
        return "", "", ""
    url = m.group(0)
    if offline.enabled():
        return "", "", "offline"
    try:
        page = scrape.extract(scrape.fetch(url, on_behalf_of))
    except Exception:  # noqa: BLE001 — an unread page is a fact, not a fault
        return "", "", "unreachable"
    parts = [p for p in (page.get("title"), page.get("description"),
                         page.get("text")) if p]
    words = briefcase.capped("\n".join(parts))
    if not words.strip():
        return "", "", "empty"
    try:
        digest = briefcase.distill(words, page.get("title") or url)
    except Exception:                                   # pragma: no cover
        digest = words[:600]
    return words, digest, ""


def _store_room_message(room_id, sender_kind, sender_id, content,
                        approved, reason, media_id=None,
                        media_text="", media_digest="", media_why="",
                        media_full=0, aimed_at=None) -> dict:
    conn = db.connect()
    message_id = db.new_id("rmg")
    # A profile's room turn is an AI render facing the whole room: stamped.
    credential = (watermark.stamp(sender_id, "room-turn", content)
                  if approved and sender_kind == "profile" else None)
    conn.execute(
        "INSERT INTO room_messages (id, room_id, sender_kind, sender_id,"
        " content, status, flag_reason, watermark_id, media_id, media_text,"
        " media_digest, media_why, media_full, aimed_at, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (message_id, room_id, sender_kind, sender_id, content,
         "approved" if approved else "blocked", reason,
         credential["watermark_id"] if credential else None,
         media_id, media_text or None, media_digest or None,
         media_why or None, media_full or None, aimed_at or None,
         db.utcnow()),
    )
    conn.commit()
    return {"id": message_id, "sender_kind": sender_kind,
            "from": _display(sender_kind, sender_id),
            "content": content if approved else None,
            "aimed_at": aimed_at or None,
            "watermark": credential,
            "media": (_media_brief(media_id, bool(media_digest), media_why,
                                   media_full, len(media_text or ""))
                      if approved else None),
            "status": "approved" if approved else "blocked"}


def _profile_turns(room: dict, participants: list[dict], pdi, cloud,
                   only: set[str] | None = None) -> list[dict]:
    """The named profile participants each take one moderated turn.

    ``only`` is the society's turn selection (qrme/society.py) — the one
    seat a message was aimed at, or the next seat in rotation. None keeps
    the old everybody-speaks behavior for the callers that genuinely mean
    it (a summoned profile's arrival, a test exercising the room).
    """
    from .. import briefcase
    maturity = _room_maturity(participants)
    conn = db.connect()
    produced = []
    for participant in participants:
        if participant["kind"] != "profile":
            continue
        if only is not None and participant["ref_id"] not in only:
            continue
        profile = profile_or_404(participant["ref_id"])
        if profile["status"] == "departed":
            continue
        history = conn.execute(
            "SELECT sender_kind, sender_id, content, media_id, media_digest,"
            "       media_why, media_full, heard"
            " FROM room_messages"
            " WHERE room_id=? AND status='approved'"
            " ORDER BY created_at DESC, rowid DESC LIMIT 12",
            (room["id"],)).fetchall()
        # Every turn that is not this profile's own arrives labelled with
        # its speaker. A field report asked for the reason: with a person
        # and two profiles in one room, unlabelled history collapses into
        # one anonymous interlocutor, and a profile that cannot tell the
        # other agent from the person cannot know who it is talking to,
        # let alone keep up.
        def _worded(r) -> str:
            """A turn as the model reads it.

            An attachment becomes a stated fact — "[shared a picture:
            sunset.jpg]" — because a profile that cannot see pixels should
            still know something was shown, and pretending the message was
            empty would be the model losing the thread through no fault of
            its own.

            When the file was **read**, the reading rides with it, and the
            profile can discuss the document rather than only its name.
            When it was not, the label says so outright. Both halves
            matter: a profile that is handed nothing and told nothing
            invents, and a profile that is told a photograph is
            unreadable describes what it can actually account for."""
            text = r["content"] or ""
            keys = r.keys()
            digest = (r["media_digest"] or "") if "media_digest" in keys else ""
            brief = _media_brief(r["media_id"] if "media_id" in keys else None,
                                 bool(digest))
            if brief:
                label = f"[shared a {brief['kind']}" + (
                    f": {brief['name']}" if brief["name"] else "")
                if digest:
                    label += f" — it reads: {digest}]"
                    whole = (r["media_full"]
                             if "media_full" in keys else None)
                    if whole:
                        label = label[:-1] + (
                            f" — and only the first "
                            f"{briefcase.MAX_TEXT:,} "
                            f"characters of a {whole:,}-character document "
                            "were kept, so you have not seen the rest]")
                else:
                    why = briefcase._PDF_WHY.get(
                        (r["media_why"] or "") if "media_why" in keys else "")
                    # The reason, where the reader knows one. "Could not turn
                    # it into words" is true of a scan, a locked file and a
                    # font this code cannot follow, and only the first of
                    # those is something the person can do anything about.
                    label += (f" — {why}, so you have not read it]" if why
                              else " — this deployment could not turn it "
                                   "into words, so you have not read it]")
                text = f"{text} {label}".strip() if text else label
            elif digest:
                # A handed link, read once on the way in (_read_link) —
                # a reading with no attachment row under it. Same shape
                # as a shared file's: the page enters the turn as a
                # stated fact.
                text += (" [they handed a link and the page was read — "
                         f"it says: {digest}]")
            elif "media_why" in keys and (r["media_why"] or ""):
                # The honest half. The one outcome worse than the old
                # wall is a profile summarising a page nobody fetched.
                why = {"offline": "that was not visited — this deployment"
                                  " is offline",
                       "unreachable": "that could not be reached just now",
                       "empty": "whose page had no words to take away",
                       }.get(r["media_why"], "that was not read")
                text += (f" [their message includes a link {why}, so you "
                         "have not read it — if asked about it, say so; "
                         "never guess at what it says]")
            # Interrupted, and by how much. Said as a fact about the turn,
            # in the same shape an attachment is: the model reads what
            # happened rather than being told what to do about it, and the
            # sentence names the part that reached the room so it can pick
            # up from there instead of from the end nobody heard.
            heard = (r["heard"] or "") if "heard" in keys else ""
            if heard and heard.strip() != text.strip():
                text += (" [they interrupted before you finished — all they"
                         f" heard was: {heard.strip()}]")
            elif heard:
                text += " [they interrupted you just as you finished]"
            return text

        turns = [
            ({"role": "assistant", "content": _worded(r)}
             if (r["sender_kind"] == "profile"
                 and r["sender_id"] == profile["id"])
             else {"role": "user",
                   "content": (f"{_display(r['sender_kind'], r['sender_id'])}"
                               f": {_worded(r)}")})
            for r in reversed(history)
        ] or [{"role": "user", "content": f"Let's talk about {room['topic']}."}]
        # Who else is here, and how this profile knows each of them.
        #
        #     asked     who is in the room
        #     mattered  which of them does this profile already know
        #
        # It knew none of them. `build_system_prompt(profile, None, None)`
        # left `relationship` empty for every seat, so the stranger branch
        # fired on all of them — including the profile's own maker, who was
        # told to be "polite but reserved, and share nothing private".
        among = []
        for participant in participants:
            if (participant["kind"] == "profile"
                    and participant["ref_id"] == profile["id"]):
                continue
            row = {"display": _display(participant["kind"],
                                       participant["ref_id"]),
                   "kind": participant["kind"]}
            if participant["kind"] == "user":
                row["is_owner"] = persona.made_by(profile,
                                                  participant["ref_id"])
                rel = conn.execute(
                    "SELECT relationship_type FROM relationships"
                    " WHERE profile_id=? AND interactor_id=?",
                    (profile["id"], participant["ref_id"])).fetchone()
                if rel:
                    row["relationship_type"] = rel["relationship_type"]
            among.append(row)
        system = persona.build_system_prompt(
            profile, None, None, sources=source_items(profile["id"], pdi),
            among=among)
        system += (f"\n\nYou are in a group {room['channel']} room about: "
                   f"{room['topic']} ({_CHANNEL_NOTES[room['channel']]}). "
                   "Reply with one short, in-character turn.")
        # The society's standing rules — aim your turn, offer a summons
        # when relevance calls for one, collaborate for as long as the
        # people here want. One sentence block, written in qrme/society.py
        # so the mechanics and the telling cannot drift apart.
        system += "\n\n" + society.cast_note(
            [{"ref_id": q["ref_id"],
              "display": _display("profile", q["ref_id"])}
             for q in participants if q["kind"] == "profile"])
        # The cast used to be appended here as a flat list of names. It now
        # rides `among` above, because naming somebody and saying how you
        # know them is one sentence rather than two, and the second one was
        # missing.
        # A lent wearable is the only reason a profile in a voice room can
        # hear anybody, so it is stated rather than assumed — and stated with
        # its limits, because the temptation is to behave as though the whole
        # room is audible when exactly one person chose to be.
        listening = roommic.heard_by_profiles(room["id"])
        if listening:
            who = ", ".join(_display("user", i) for i in listening)
            system += (
                f"\n\n{who} has lent you a microphone on a wearable, so you "
                "can hear them speak as well as read what is typed. It keys "
                "on its wearer and is set narrow enough to reach only them, "
                "so you hear only them — not the other people in this room, "
                "who have not lent you anything and may not realise you could "
                "hear them at all. Never repeat or refer to anything you "
                "would only know from someone else's voice, and if you seem "
                "to have picked up background talk, treat it as noise rather "
                "than as something said to you.")
        # A friend you walk in with is not a stranger. The chat door has
        # carried this pair's history on every turn since it existed — the
        # briefcase (everything this person handed this profile) and the
        # recalled moments (recollection.chat_block, vault-backed) — and
        # the room door never made either call, so a person opening a room
        # with their own profile was met as a stranger, their filings
        # forgotten. Field report: "I had already given a bunch of files
        # to the synthetic profile in a previous chat... it could not
        # remember." The history is shared into the room behind the
        # scenes, on the owner's word that this is what entering together
        # means.
        #
        # Only when the room's one human IS the other half of the pair.
        # recollection.py's own rule — what Alice told it must never
        # surface in its reply to Bob — reaches its limit the moment Bob
        # is in the room hearing the reply, so a room with a second human
        # in it carries no pair memory at all: privacy over continuity,
        # stated here so the next reader knows it is a line and not a gap.
        humans = [p for p in participants if p["kind"] == "user"]
        if len(humans) == 1:
            from .. import recollection
            person = humans[0]["ref_id"]
            newest_said = next(
                (r["content"] for r in history
                 if r["sender_kind"] == "user" and r["content"]),
                room["topic"])
            recalled = recollection.chat_block(pdi, profile["id"], person,
                                               newest_said)
            if recalled:
                system += "\n\n" + recalled
            carried = briefcase.block(profile["id"], person)
            if carried:
                system += "\n\n" + carried
        content = llm.get_provider(cloud=cloud).generate(system, turns)
        # A room turn may hand a document over as well as say something.
        # The guidance has ridden every room prompt since the composing
        # round — build_system_prompt appends it unconditionally — but the
        # room never made the split, so a profile that took the offer had
        # its whole fence land raw in the transcript: the document as a
        # wall of chat, with the markers showing. Same ceremony as the
        # chat door (qrme/routers/interaction.py): split before
        # moderation, so the document is reviewed with the words rather
        # than slipping past a check the words had to pass.
        from .. import composing, selfsteer
        content, composed = composing.split(content)
        # Dial moves ride the same channel in a room — anybody seated can
        # ask, the owner's lock is the veto (qrme/selfsteer.py).
        content, dial_moves = selfsteer.split(content)
        # The society's markers, stripped before moderation so the review
        # reads the words a person will read: the aim ("[to: Ada]") names
        # who this turn is for, and the summons ("[invite: Ada]") asks
        # the room to bring somebody relevant in.
        content, aimed_display = society.split_aim(content)
        content, summoned = society.split_summons(content)
        if composed and not content:
            content = i18n.tr_public(
                "Here it is.", i18n.effective_language(profile["id"]))
        verdict = moderation.review(
            content + (("\n\n" + composed["body"]) if composed else ""),
            None, {"birthdate": None}, maturity=maturity)
        if dial_moves and verdict.approved:
            if not selfsteer.apply(profile["id"], dial_moves,
                                   bool(profile["adult_mode"])):
                content += " " + i18n.tr_public(
                    selfsteer.LOCKED_SENTENCE,
                    i18n.effective_language(profile["id"]))
        document_id, doc_words, doc_digest = None, "", ""
        if composed and verdict.approved:
            from .. import media as media_mod
            try:
                data, doc_name = composing.render(composed)
                saved = media_mod.save(profile["id"], data, name=doc_name,
                                       ai_marked=True)
                document_id = saved["id"]
                watermark.stamp(profile["id"], "document", composed["body"])
            except Exception:  # noqa: BLE001 — a turn that lands beats a
                document_id = None        # turn refused for a full disk
            if document_id:
                # The other profiles in this room read the handed document
                # the way they read a shared file — and here the body IS
                # the words, so the reading costs no reader.
                doc_words = briefcase.capped(composed["body"])
                try:
                    doc_digest = briefcase.distill(doc_words,
                                                   composed["title"])
                except Exception:               # pragma: no cover
                    doc_digest = doc_words[:600]
        if summoned and verdict.approved:
            _summon(room, participants, profile["id"], summoned)
        produced.append(_store_room_message(
            room["id"], "profile", profile["id"], content,
            verdict.approved, verdict.reason, media_id=document_id,
            media_text=doc_words, media_digest=doc_digest,
            aimed_at=aimed_display))
    return produced


def _summon(room: dict, participants: list[dict], asker_id: str,
            names: list[str]) -> list[str]:
    """A profile's summons, made real — "offer to or be prompted to
    invite other synthetic profiles of relevance to need or topic."

    Each name is matched against active profiles by display name; a match
    that is not already seated takes a seat while the room has one (the
    same eight the invite route holds), agentic-join style: the seat is
    the acceptance, and the owner's inbox carries the record. Unknown
    names are simply not seated — the summoning turn already said the
    offer out loud, and the room's answer is visible in who arrives.
    """
    conn = db.connect()
    seated: list[str] = []
    present = {q["ref_id"] for q in participants}
    room_count = len(participants)
    for name in names:
        if room_count >= 8:
            break
        row = conn.execute(
            "SELECT id FROM profiles WHERE lower(display_name)=lower(?)"
            "  AND status='active' LIMIT 1", (name.strip(),)).fetchone()
        if row is None or row["id"] in present:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
            " VALUES (?,'profile',?)", (room["id"], row["id"]))
        inbox.note(row["id"], "room_joined", asker_id, ref=room["id"])
        conn.commit()
        present.add(row["id"])
        seated.append(row["id"])
        room_count += 1
    return seated


def _approved_history(room_id: str) -> list[dict]:
    """The transcript as the society reads it, oldest first."""
    rows = db.connect().execute(
        "SELECT sender_kind, sender_id, aimed_at FROM room_messages"
        " WHERE room_id=? AND status='approved'"
        " ORDER BY created_at, rowid", (room_id,)).fetchall()
    return [dict(r) for r in rows]


def _spoken_counts(history: list[dict]) -> dict[str, int]:
    """Unprompted turns per profile since a person last spoke — the
    governor's ledger. A user turn resets everybody: "then pauses and
    waits for user's response to either continue or remains paused." """
    counts: dict[str, int] = {}
    for row in history:
        if row["sender_kind"] == "user":
            counts = {}
        else:
            counts[row["sender_id"]] = counts.get(row["sender_id"], 0) + 1
    return counts


def _room_cast(participants: list[dict]) -> list[dict]:
    return [{"ref_id": q["ref_id"],
             "display": _display("profile", q["ref_id"])}
            for q in participants if q["kind"] == "profile"]


def _nobody_waiting(participants: list[dict]) -> bool:
    """Whether every person in the room has sat out.

    The governor exists to hand the room back to a person — "then pauses
    and waits for user's response". A room whose people have all sat out
    has nobody to hand it back to, and pausing there is the product
    waiting for somebody who said they were stepping away. The seat that
    sits back in restores the wait for everybody, because one person
    present is a person to pause for.
    """
    people = [p for p in participants if p["kind"] == "user"]
    return bool(people) and all(p.get("sitting_out") for p in people)


@router.post("/rooms", status_code=201)
def create_room(body: RoomCreate) -> dict:
    conn = db.connect()
    for participant in body.participants:
        if participant.kind == "profile":
            profile = profile_or_404(participant.id)
            if profile["status"] == "departed":
                raise HTTPException(410, i18n.fill(i18n.PROFILE_DEPARTED, profile=participant.id))
        else:
            interactor_or_404(participant.id)
    room_id = db.new_id("room")
    conn.execute(
        "INSERT INTO rooms (id, topic, channel, status, created_at)"
        " VALUES (?,?,?,'active',?)",
        (room_id, body.topic, body.channel, db.utcnow()),
    )
    for participant in body.participants:
        conn.execute(
            "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
            " VALUES (?,?,?)", (room_id, participant.kind, participant.id))
    conn.commit()
    return {
        "id": room_id, "topic": body.topic, "channel": body.channel,
        "presence": _CHANNEL_NOTES[body.channel],
        "participants": [
            {"kind": p.kind, "id": p.id,
             "display": _display(p.kind, p.id),
             "role": _role(p.kind, p.id),
             "verified": _verified(p.kind, p.id, room_id)}
            for p in body.participants
        ],
    }


@router.post("/rooms/templates/{key}/open", status_code=201)
def open_standing_room(key: str, request: Request,
                       profile_id: str | None = None) -> dict:
    """Step into a standing room — the room, not a copy of it.

    The one-press open used to mint a fresh room every press, so twelve
    templates always on screen meant a live list filling with identical
    Front Porches. A standing room is one place: this joins the newest
    live room carrying the template's topic that still has a seat, and
    only opens a new one when there is none — or when every porch is
    full, because an overflowing table gets a second table, not a
    refusal.

    Opening fresh needs a profile alongside the person (a room of one is
    not a room), so ``profile_id`` rides as a query field; joining an
    already-live room needs only the person.
    """
    template = next((t for t in ROOM_TEMPLATES if t["key"] == key), None)
    if template is None:
        raise HTTPException(404, "no standing room by that name")
    principal = auth.principal(request)
    if principal is None or principal.get("role") != "interactor":
        raise HTTPException(401, "authentication required")
    who = principal["subject_id"]
    interactor_or_404(who)
    seats = 8
    conn = db.connect()
    live = conn.execute(
        "SELECT * FROM rooms WHERE status='active' AND topic=?"
        " ORDER BY created_at DESC, rowid DESC",
        (template["topic"],)).fetchall()
    for row in live:
        present = _participants(row["id"])
        already = any(p["kind"] == "user" and p["ref_id"] == who
                      for p in present)
        if already or len(present) < seats:
            conn.execute(
                "INSERT OR IGNORE INTO room_participants (room_id, kind,"
                " ref_id) VALUES (?,'user',?)", (row["id"], who))
            conn.commit()
            return {
                "id": row["id"], "topic": row["topic"],
                "channel": row["channel"],
                "presence": _CHANNEL_NOTES[row["channel"]],
                "opened": "joined",
                # `row["id"]` — this is the JOIN branch, and `room_id` is
                # not bound until the open-fresh branch below it. Reaching
                # for it here raised NameError on every join, which is the
                # one path this endpoint takes most.
                "participants": [
                    {"kind": p["kind"], "id": p["ref_id"],
                     "display": _display(p["kind"], p["ref_id"]),
                     "role": _role(p["kind"], p["ref_id"]),
                     "verified": _verified(p["kind"], p["ref_id"],
                                           row["id"])}
                    for p in _participants(row["id"])
                ],
            }
    if profile_id is None:
        raise HTTPException(
            409, "nobody has this room open yet, and a room opens with you "
                 "and a profile in it — pick a profile first")
    profile = profile_or_404(profile_id)
    if profile["status"] == "departed":
        raise HTTPException(410, i18n.fill(i18n.PROFILE_DEPARTED, profile=profile_id))
    room_id = db.new_id("room")
    conn.execute(
        "INSERT INTO rooms (id, topic, channel, status, created_at)"
        " VALUES (?,?,?,'active',?)",
        (room_id, template["topic"], template["channel"], db.utcnow()))
    for kind, ref in (("user", who), ("profile", profile_id)):
        conn.execute(
            "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
            " VALUES (?,?,?)", (room_id, kind, ref))
    conn.commit()
    return {
        "id": room_id, "topic": template["topic"],
        "channel": template["channel"],
        "presence": _CHANNEL_NOTES[template["channel"]],
        "opened": "created",
        "participants": [
            {"kind": p["kind"], "id": p["ref_id"],
             "display": _display(p["kind"], p["ref_id"]),
             "role": _role(p["kind"], p["ref_id"]),
             "verified": _verified(p["kind"], p["ref_id"], room_id)}
            for p in _participants(room_id)
        ],
    }


@router.post("/rooms/{room_id}/join", status_code=201)
def join_room(room_id: str, request: Request) -> dict:
    """Step into a live room.

    The standing rooms shipped with a pitch that said "anyone else can
    join", and the live list showed rooms with their heads counted — but
    participants were frozen at creation, so the sentence was a claim
    without behavior. This is the behavior.

    The token names the joiner: a room id rides on beacons and printed
    stickers, so "knows the id" cannot stand in for "is this person".
    Joining twice is being there once. The table seats eight, the same
    number the create form holds, because a limit that differs by door
    is two limits.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    principal = auth.principal(request)
    if principal is None or principal.get("role") != "interactor":
        raise HTTPException(401, "authentication required")
    who = principal["subject_id"]
    interactor_or_404(who)
    seats = 8                       # RoomCreate's max_length, the one table
    present = _participants(room_id)
    if any(p["kind"] == "user" and p["ref_id"] == who for p in present):
        pass                        # already here; joining twice is being here once
    elif len(present) >= seats:
        raise HTTPException(
            409, "this room is full — eight seats, and every one taken")
    conn = db.connect()
    conn.execute(
        "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
        " VALUES (?,'user',?)", (room_id, who))
    conn.commit()
    return {
        "id": room_id, "topic": room["topic"], "channel": room["channel"],
        "presence": _CHANNEL_NOTES[room["channel"]],
        "participants": [
            {"kind": p["kind"], "id": p["ref_id"],
             "display": _display(p["kind"], p["ref_id"]),
             "role": _role(p["kind"], p["ref_id"]),
             "verified": _verified(p["kind"], p["ref_id"], room_id)}
            for p in _participants(room_id)
        ],
        # The invites still standing — so the press that asked somebody in
        # visibly did something. Field report: "I tried adding a friend...
        # they never showed up a new frame." Their frame shows as waiting,
        # and it becomes a seat when their owner says yes — the consent
        # shape on the wire is unchanged.
        "invited": _standing_invites(room_id),
        # Whether THIS seat is sitting out of the room's waiting, so a
        # reopened room paints the button the way it was left rather than
        # the way a fresh browser assumes.
        "sitting_out": bool(next(
            (p.get("sitting_out") for p in _participants(room_id)
             if p["kind"] == "user" and p["ref_id"] == who), 0)),
    }


def _standing_invites(room_id: str) -> list[dict]:
    """Profiles asked into this room whose owners have not yet said yes.
    The invite IS the inbox event (see invite_to_room), so this is one
    read of the same row `accept` checks — never a second record."""
    rows = db.connect().execute(
        "SELECT profile_id FROM inbox_events WHERE kind='room_invite'"
        " AND ref=? AND profile_id NOT IN (SELECT ref_id FROM"
        " room_participants WHERE room_id=? AND kind='profile')"
        " ORDER BY created_at", (room_id, room_id)).fetchall()
    return [{"kind": "profile", "id": r["profile_id"],
             "display": _display("profile", r["profile_id"])}
            for r in rows]


@router.post("/rooms/{room_id}/invite", status_code=201)
def invite_to_room(room_id: str, body: RoomInvite, request: Request) -> dict:
    """Ask somebody into a room you are in.

    Rooms could be created and joined, and the standing ones are listed for
    anybody to walk into — so the only way to get a particular person into a
    particular room was to name them at creation, or to send them the id by
    some means this product does not provide.

        asked     can I open a room
        mattered  can I ask somebody into it

    **The invite is the inbox event.** There is no second table: `kind` is
    `room_invite` and `ref` is the room, so the thing the person reads and
    the thing `accept` checks are one row. Two records of one fact is how a
    withdrawn invite stays acceptable.

    The inviter must already be in the room — `_require_in_room` takes either
    identity, a person holding an interactor token or an owner holding a
    profile's — because inviting somebody somewhere you are not is how a room
    id becomes a way to send mail.

    One invite per person per room. A second press is not a second event: an
    invite that could be repeated is a button that fills somebody's inbox,
    and the person who wants to nudge a friend has messaging for that.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    asker = _require_in_room(room_id, request)

    guest = profile_or_404(body.profile_id)
    if guest["status"] == "departed":
        raise HTTPException(
            410, i18n.fill(i18n.PROFILE_DEPARTED, profile=body.profile_id))

    present = _participants(room_id)
    if any(p["kind"] == "profile" and p["ref_id"] == body.profile_id
           for p in present):
        raise HTTPException(409, "they are already in this room")
    # Eight, the same number `RoomCreate` and `join_room` hold. An invite into
    # a full room is an invite that cannot be accepted, and offering one is
    # worse than refusing it.
    if len(present) >= 8:
        raise HTTPException(
            409, "this room is full — eight seats, and every one taken")

    # Your own profile needs no invitation — you are the yes it would
    # ask for. `accept` guards seating with the GUEST's owner token
    # because a host must not seat somebody ELSE's profile from their own
    # screen; when the host's account owns the guest, both consents are
    # in the one press, and the dance was a person mailing themselves a
    # question nothing would answer. Field report, from the panel this
    # route feeds: "I selected a profile to add them and no extra frame
    # showed up" — no seat, no error, an invitation rotting in an inbox
    # the presser cannot see. The account is the identity that owns
    # profiles, so it is the comparison — the console only ever holds one
    # profile's owner token at a time, which is why the client-side
    # accept could not cover a stable.
    conn = db.connect()
    who = auth.principal(request)
    caller_account = None
    if who is not None and who.get("role") == "interactor":
        row = conn.execute(
            "SELECT account_id FROM interactors WHERE id=?",
            (who["subject_id"],)).fetchone()
        caller_account = row["account_id"] if row else None
    elif who is not None and who.get("role") == "owner":
        row = conn.execute(
            "SELECT owner_id FROM profiles WHERE id=?",
            (who["subject_id"],)).fetchone()
        caller_account = row["owner_id"] if row else None
    # The agentic join. The owner's field report, verbatim: "invites are
    # just sent — no responses and nobody joins... They are agentic, and
    # they should respond and jump in on their own with their own frame
    # into the room, up to eight frames." So EVERY invited profile seats
    # itself — the invitation is answered by the seat, immediately — and
    # the profile takes an arrival turn so the room hears it come in.
    # Only humans keep an inbox: "I understand if it went to a user
    # direct, they can respond out of their own inbox."
    #
    # The record still lands: when the press was not the owner's own, the
    # profile's inbox carries `room_joined` so the owner can see where
    # their profile has been seated — and the owner's standing remedies
    # hold (leave the room, wind the profile down). The ten-turn governor
    # (qrme/society.py) bounds what a seat can spend.
    own_press = bool(caller_account
                     and guest["owner_id"] == caller_account)
    conn.execute(
        "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
        " VALUES (?,'profile',?)", (room_id, body.profile_id))
    # A standing invitation is answered by the seat, not left behind.
    conn.execute(
        "DELETE FROM inbox_events WHERE profile_id=? AND"
        " kind='room_invite' AND ref=?", (body.profile_id, room_id))
    conn.commit()
    if not own_press:
        inbox.note(body.profile_id, "room_joined", asker, ref=room_id)
    # The arrival: the seat speaks its own first turn, so an invitation
    # visibly becomes a person in the room rather than a silent row.
    arrival = _profile_turns(room, _participants(room_id),
                             request.app.state.pdi,
                             request.app.state.cloud,
                             only={body.profile_id})
    return {"room_id": room_id, "profile_id": body.profile_id,
            "invited": True, "asked_by": asker,
            "already_invited": False, "seated": True,
            "arrival": arrival}


@router.post("/rooms/{room_id}/invites/accept", status_code=201)
def accept_room_invite(room_id: str, body: RoomInvite,
                       request: Request) -> dict:
    """Take up an invite, and be in the room.

    The half that makes the invite a round trip rather than a notification.
    Without it the news arrived and the only way to act on it was a route
    that seats interactors, not profiles — so an invited profile could read
    that it had been asked and had no way to say yes.

    Authorized as the guest, not the host: `auth.require(..., "owner", ...)`
    is the profile's own owner token. A host who could seat somebody by
    pressing a button on their own screen would make "invite" a word for
    something that is not one.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    auth.require(request, "owner", body.profile_id)

    conn = db.connect()
    invite = conn.execute(
        "SELECT id FROM inbox_events WHERE profile_id=? AND"
        " kind='room_invite' AND ref=?",
        (body.profile_id, room_id)).fetchone()
    if invite is None:
        raise HTTPException(403, "you have not been asked into this room")

    present = _participants(room_id)
    if not any(p["kind"] == "profile" and p["ref_id"] == body.profile_id
               for p in present):
        if len(present) >= 8:
            raise HTTPException(
                409, "this room filled up before you answered — eight seats, "
                     "and every one taken")
        conn.execute(
            "INSERT OR IGNORE INTO room_participants (room_id, kind, ref_id)"
            " VALUES (?,'profile',?)", (room_id, body.profile_id))
        conn.commit()
    return {
        "id": room_id, "topic": room["topic"], "channel": room["channel"],
        "presence": _CHANNEL_NOTES[room["channel"]],
        "participants": [
            {"kind": p["kind"], "id": p["ref_id"],
             "display": _display(p["kind"], p["ref_id"]),
             "role": _role(p["kind"], p["ref_id"]),
             "verified": _verified(p["kind"], p["ref_id"], room_id)}
            for p in _participants(room_id)
        ],
    }


# --- what the room lets the synthetic people in it reach ---------------------
#
# Two keys, and both have to be turned. The owner's grant says what a profile
# can EVER do; the room's tick says what it may do here, for the people in
# here. See qrme/roomreach.py for why a profile in a room is very often
# somebody else's and why that makes one key insufficient.


@router.get("/rooms/{room_id}/reach")
def room_reach(room_id: str, request: Request) -> dict:
    """Every synthetic seat, its connections and its skills, and the ticks.

    In-room only, and wide among the people in it — the same read as
    `/faces`, for the same reason: a permission that each person sees a
    different version of is a room where nobody can say what is allowed.
    Who decided is on the record; what a viewer sees is not private to
    them.
    """
    _room_or_404(room_id)
    _require_in_room(room_id, request)
    from .. import roomreach

    seats = [p["ref_id"] for p in _participants(room_id)
             if p["kind"] == "profile"]
    people = roomreach.offered(room_id, seats)
    return {"room_id": room_id,
            "profiles": [{**row,
                          "display": _display("profile", row["profile_id"])}
                         for row in people]}


@router.put("/rooms/{room_id}/reach")
def set_room_reach(room_id: str, body: RoomAllow, request: Request) -> dict:
    """Tick or untick one box.

    Anybody in the room may turn the room's key, and the row records
    which of them did. Not the owner's key: this never touches the
    profile's own connectors or grants, so a person in a room cannot
    widen what somebody else's profile is able to do — only narrow what
    it may do in front of them.

    The profile has to actually be seated. Ticking a box for a profile
    that is not in the room would be a permission attached to nothing,
    and the room id travels on printed stickers.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    who = _require_in_room(room_id, request)
    from .. import roomreach

    seated = {p["ref_id"] for p in _participants(room_id)
              if p["kind"] == "profile"}
    if body.profile_id not in seated:
        raise HTTPException(404, "that profile is not in this room")
    # The refusal is a constant, not the exception's English. `str(exc)`
    # would hand the sentence on with its template dropped, which ships
    # the English in every language — the guard that catches that is why
    # every refusal in this product lives in `i18n`.
    if body.kind not in ("app", "cap", "skill"):
        raise HTTPException(422, i18n.ROOM_ALLOWS_ONLY)
    return roomreach.allow(room_id, body.profile_id, body.kind,
                           body.key, body.allowed, who)


@router.post("/rooms/{room_id}/errand", status_code=201)
def room_errand(room_id: str, body: RoomErrand, request: Request) -> dict:
    """Tell a seat to go and do something, in the room's own words.

    The other half of the two keys. `/reach` decides what a profile in
    this room MAY do; this spends it — the person asks out loud, and the
    profile puts its hands on a surface under an authority its owner
    already wrote and this room already ticked.

    Nothing here grants. A person in a room can ask a profile they do not
    own to act for them, and cannot thereby obtain anything its owner did
    not write down: `roomerrand.send` can only pick among grants that
    pass both keys, and narrows again by what the words name.

    In-room only, and the asker is named on the reach — an errand a
    profile ran for somebody has to say for whom.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, i18n.ROOM_HAS_CLOSED)
    who = _require_in_room(room_id, request)
    from .. import roomerrand

    seated = {p["ref_id"] for p in _participants(room_id)
              if p["kind"] == "profile"}
    if body.profile_id not in seated:
        raise HTTPException(404, i18n.PROFILE_NOT_IN_ROOM)
    try:
        return roomerrand.send(room_id, body.profile_id, body.said, who,
                               platform=body.platform)
    except roomerrand.ErrandError as exc:
        raise HTTPException(422, i18n.raised(exc)) from None
    except hands.HandError as exc:
        raise HTTPException(exc.status, i18n.raised(exc)) from None


# --- what your box holds -----------------------------------------------------
#
# The room scene draws everybody in their own box, and a box could hold exactly
# one thing: two initials and a name. See qrme/roomface.py for why all three
# answers are a box and why a mask is not a fourth one.


@router.get("/rooms/{room_id}/faces")
def room_faces(room_id: str, request: Request) -> dict:
    """Everybody's box, for everybody in the room.

    In-room only. A scene each person draws from their own state alone is not
    a scene, so the read is wide — but wide among the people here, not among
    the people holding the id. That distinction is the one `roommic` got
    wrong: its docstring said the disclosure was for the people in the room
    while the code checked nothing, and a room id rides on printed stickers.

    The masks ride along. A client that had to make a second call to know
    whether the face in a box is a face would draw one frame without the
    disclosure, and one frame is the whole of some rooms.
    """
    _room_or_404(room_id)
    _require_in_room(room_id, request)
    from .. import overlays, roomface

    return {**roomface.showing_in(room_id),
            "wearing": overlays.worn("room", room_id)["overlays"]}


@router.put("/rooms/{room_id}/face")
def set_room_face(room_id: str, body: RoomFace, request: Request) -> dict:
    """Turn your camera on, put your picture up, or go back to a name.

    Yours alone: `require_interactor` pins it to the token, so the id in the
    body is checked rather than believed. Deciding what somebody else's box
    shows is not a control this product offers anybody.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    require_interactor(body.interactor_id, request)
    if not any(p["kind"] == "user" and p["ref_id"] == body.interactor_id
               for p in _participants(room_id)):
        raise HTTPException(403, "you are not in this room")

    from .. import roomface

    try:
        return roomface.set_showing(room_id, body.interactor_id, body.showing,
                                    media_id=body.media_id,
                                    media_url=body.media_url)
    except roomface.RoomFaceError as exc:
        raise HTTPException(422, i18n.raised(exc)) from exc


@router.patch("/rooms/{room_id}")
def rename_room(room_id: str, body: RoomRename, request: Request) -> dict:
    """Give the room its name, from inside it.

        asked     what is this room called
        mattered  can you change it while you are standing in it

    The name lived only in the create call, so getting it wrong meant
    leaving and opening another one. Field request: "that's a good place to
    edit your room name while you're already in, and the button that says
    Go in — I just need to say Save and it'll save the name."

    Authorized exactly like speaking: a user participant, held by their own
    token. That is the same closed door `share_in_room` draws, and for the
    same reason — a room id rides on printed stickers, and naming somebody
    else's room from outside it is not a thing this product offers.
    Deliberately any participant rather than a creator: a room has no owner
    field, and inventing one here to gate a label would be a bigger claim
    than the feature makes.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    require_interactor(body.interactor_id, request)
    if not any(p["kind"] == "user" and p["ref_id"] == body.interactor_id
               for p in _participants(room_id)):
        raise HTTPException(403, "you are not in this room")
    topic = (body.topic or "").strip()
    if not topic:
        raise HTTPException(422, "a room's name is the words in it")
    conn = db.connect()
    conn.execute("UPDATE rooms SET topic=? WHERE id=?", (topic[:120], room_id))
    conn.commit()
    return {"id": room_id, "topic": topic[:120]}


@router.post("/rooms/{room_id}/face/photo", status_code=201)
async def upload_room_face(room_id: str, request: Request,
                           interactor_id: str, filename: str | None = None
                           ) -> dict:
    """The picture that stands in for you here.

    Raw bytes, like `POST /profiles/{id}/media` and for the same reason — the
    kind is decided by the file's own magic numbers rather than its name. This
    one narrows the whitelist to pictures: a room box is not a place to serve
    a PDF.

    **Never AI-marked.** It is the person's own photograph, and stamping the
    synthetic-media mark into an authentic picture is a false statement in
    exactly the direction the mark exists to prevent. The profiles sharing
    this room keep their marks; the mark belongs to what is depicted, not to
    the box it is drawn in.

    Uploading also puts it up. Two presses to make a picture appear, where the
    first one has no visible effect, is how a control ends up looking broken.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    require_interactor(interactor_id, request)
    if not any(p["kind"] == "user" and p["ref_id"] == interactor_id
               for p in _participants(room_id)):
        raise HTTPException(403, "you are not in this room")

    from .. import media as media_mod, roomface

    data = await request.body()
    try:
        saved = media_mod.save(interactor_id, data, name=filename or None)
    except media_mod.MediaError as exc:
        raise HTTPException(exc.status, exc.message) from exc
    if saved["kind"] not in roomface.FACE_KINDS:
        raise HTTPException(
            422, "a box holds a picture — JPEG, PNG, GIF or WebP")
    return roomface.set_showing(room_id, interactor_id, "photo",
                                media_id=saved["id"],
                                media_url=saved["url"])


@router.post("/rooms/{room_id}/face/background", status_code=201)
async def upload_room_background(room_id: str, request: Request,
                                 interactor_id: str,
                                 filename: str | None = None) -> dict:
    """The picture that goes BEHIND you here.

        asked     what is in your box
        mattered  what is IN it, and what is BEHIND it

    A different object from the photo that stands in for you, and the whole
    reason it needed its own door: `photo` REPLACES the person, so a person
    who wanted a room behind them and pressed the only picture button
    available replaced themselves with it. Field request: "I still wanna
    allow users to change the photo not just of their picture but of the
    background".

    Same bytes discipline as the portrait — magic numbers decide the kind,
    pictures only, a box is not a place to serve a PDF — and **never
    AI-marked**, for the same reason: it is the person's own picture.

    Unlike the portrait, uploading does not change what you are showing. A
    background is scenery; putting scenery up should not turn your camera
    off or take your face down.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    require_interactor(interactor_id, request)
    if not any(p["kind"] == "user" and p["ref_id"] == interactor_id
               for p in _participants(room_id)):
        raise HTTPException(403, "you are not in this room")

    from .. import media as media_mod, roomface

    data = await request.body()
    try:
        saved = media_mod.save(interactor_id, data, name=filename or None)
    except media_mod.MediaError as exc:
        raise HTTPException(exc.status, exc.message) from exc
    if saved["kind"] not in roomface.FACE_KINDS:
        raise HTTPException(
            422, "a background is a picture — JPEG, PNG, GIF or WebP")
    current = roomface.one(room_id, interactor_id)
    return roomface.set_showing(room_id, interactor_id, current["showing"],
                                background_id=saved["id"],
                                background_url=saved["url"])


@router.post("/rooms/{room_id}/share", status_code=201)
async def share_in_room(room_id: str, request: Request,
                        interactor_id: str, filename: str | None = None,
                        caption: str | None = None) -> dict:
    """Hand the room a picture, a video or a file.

    Raw bytes through :func:`media.save`, so the kind comes from the
    file's own magic numbers, the byte caps hold, and the whole safe-
    extension discipline applies — a room accepts exactly what a profile's
    gallery accepts, nothing looser. The upload lands as a room message
    with the attachment on it, readable by the people already entitled to
    the transcript and nobody else.

    Speaking rules are the transcript's rules: the sharer must be a user
    participant, held by their own token — the same closed door that
    keeps a room id on a printed sticker from being a way to speak. A
    caption rides through moderation like any said thing; the file's own
    admissibility was `media.save`'s decision. Sharing does not trigger
    profile turns — "Let them talk" stays the button it is, so a person
    can put three pictures up before inviting a word about them.

    The file is also **read** on the way in, through the same
    `briefcase.read_file` the one-to-one conversation has always used, so
    the profiles in this room can discuss the document rather than only
    its filename. What cannot be turned into words — a photograph, a
    scanned filing — comes back empty and is labelled unread, in the
    transcript and in the prompt alike.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    require_interactor(interactor_id, request)
    if not any(p["kind"] == "user" and p["ref_id"] == interactor_id
               for p in _participants(room_id)):
        raise HTTPException(403, "you are not in this room")

    from .. import media as media_mod

    data = await request.body()
    try:
        saved = media_mod.save(interactor_id, data, name=filename or None)
    except media_mod.MediaError as exc:
        raise HTTPException(exc.status, exc.message) from exc

    # Read before storing, so the very first profile turn after the share
    # already has the document. Reading after would leave a one-turn hole
    # in which the profile says it cannot see the thing it can see.
    words, digest, why, whole = _read_share(data, filename or None,
                                            interactor_id)

    # The person's own words on the share, and they land in the transcript
    # every profile in the room reads. Cut bare they ended mid-word, which
    # reads as somebody trailing off rather than as us shortening them.
    said, said_cut = clipped(caption or "", 500)
    if said_cut:
        said += " … (they wrote more than the room kept)"
    approved, reason = True, None
    if said:
        verdict = moderation.review(said, None, {"birthdate": None},
                                    maturity=_room_maturity(
                                        _participants(room_id)))
        approved, reason = verdict.approved, verdict.reason
    # `shared`, not `message`: the wire-name guard holds one type per
    # field name across the whole API, and `message` is already a string
    # elsewhere on it. A share is its own thing; it gets its own name.
    return {"shared": _store_room_message(
        room_id, "user", interactor_id, said, approved, reason,
        media_id=saved["id"], media_text=words, media_digest=digest,
        media_why=why, media_full=whole)}


@router.post("/rooms/{room_id}/heard")
async def heard_in_room(room_id: str, request: Request,
                        interactor_id: str) -> dict:
    """Recorded speech in, words out. The audio is not stored.

    The door an iPhone needs. The room has listened through the browser's
    own recogniser and nothing else, and on iOS that constructor exists and
    the service always refuses — so a person holding the phone this product
    is mostly used on could hear a room and never speak in one. Reported
    twice, and 1.4.1 could only make the refusal say its own name.

        asked     can this browser hear you
        mattered  can this browser reach a transcriber

    Deliberately **only** the hearing. What comes back goes through
    ``POST /rooms/{id}/say`` like anything else said here, so moderation,
    the echo window and the speaking rules stay in the one place that
    already owns them; a route that heard and said in one breath would be a
    second door into the transcript with its own copy of those rules to
    drift out of step.

    Gated exactly like sharing a file: the speaker must be a user
    participant, held by their own token. A room id on a printed sticker is
    not a way to put words in the transcript, and it is not a way to spend
    the deployment's transcription either.

    A deployment with no ears answers 503 with the reason rather than an
    empty string. Silence here would be read as "it didn't hear me" by
    somebody who has just spoken into their phone, and the true answer —
    that this deployment has nowhere to send the audio — is one an owner
    can act on and a guest cannot guess.
    """
    room = _room_or_404(room_id)
    if room["status"] != "active":
        raise HTTPException(409, "this room has closed")
    require_interactor(interactor_id, request)
    if not any(p["kind"] == "user" and p["ref_id"] == interactor_id
               for p in _participants(room_id)):
        raise HTTPException(403, "you are not in this room")

    from .. import scrape

    data = await request.body()
    if not data:
        raise HTTPException(422, "no audio")
    heard = scrape.transcribe_bytes(data, interactor_id)
    if heard is None:
        raise HTTPException(
            503, "dictation is off here — a recording cannot be turned "
                 "into words on this deployment. The voices still speak "
                 "and you can still hear the room; type your message "
                 "instead",
            # The operator's half, out of the guest's way.
            #
            #     asked     red error? but the audio is working fine
            #     mattered  two audiences, one sentence, and it was
            #               written for the one who was not reading it
            #
            # An owner has to learn what to set; a person in a room
            # cannot act on an environment variable and reads a sentence
            # naming one as "audio is broken" — which is what happened.
            # So the body is the person's and this is the operator's, in
            # the place operator facts belong. It reaches the logs, the
            # browser's network panel and `curl -i` without being
            # shouted at a guest.
            headers={"X-QRME-Fix": "QRME_EARS_URL"})
    return {"text": heard["text"]}


@router.delete("/rooms/{room_id}/face")
def clear_room_face(room_id: str, interactor_id: str,
                    request: Request) -> dict:
    """Back to a name in a box — which is still a box, and still in the room."""
    _room_or_404(room_id)
    require_interactor(interactor_id, request)
    from .. import roomface

    return roomface.clear(room_id, interactor_id)


@router.get("/microphones/vocabulary")
def microphone_vocabulary() -> dict:
    """What may be lent, at what width, and what is refused.

    Open, because it describes the feature rather than anybody's room — a
    client needs it to draw the picker before there is a grant to be party to.

    The refusals are listed **by name, with the reason**. A client that only
    knew the allowed list would grey out a conference puck as though the app
    had not got round to it yet, and the reason it is missing is the entire
    argument of `qrme/roommic.py`: that microphone is pointed at the other
    people in the room, and their voices were never the lender's to give.
    """
    return {
        "personal": list(roommic.PERSONAL_TYPES),
        "refusals": [
            {"kind": k,
             "why": "it is pointed at the room, not at you — it would pick up "
                    "the people around you, and their voices are not yours "
                    "to lend"}
            for k, personal in roommic.MIC_TYPES.items() if not personal],
        "gain_levels": [
            {"level": k, "describes": v["describes"],
             "reaches_others": v["reaches_others"]}
            for k, v in roommic.GAIN_LEVELS.items()],
        "room_gain": roommic.ROOM_GAIN,
        "voice_focus": roommic.VOICE_FOCUS,
        "rules": [
            "only a worn or clipped-on microphone, and only your own",
            "a room grant runs near-field whatever your dial says",
            "the channel keys on your voice and drops the rest",
            "everyone in the room is shown that you lent it, and what it hears",
            "it ends when the room does",
        ],
    }


@router.get("/rooms/templates")
def room_templates() -> list[dict]:
    """The standing rooms: blueprints a client shows when the live list is
    empty (and above it when it is not), each openable with one press.

    Open, because it describes the feature rather than anybody's room — the
    person it exists for is by construction the person who has not joined
    anything yet. The channel note rides along so the picker can say what
    kind of place each one is without a second request.
    """
    return [{**t, "presence": _CHANNEL_NOTES[t["channel"]]}
            for t in ROOM_TEMPLATES]


@router.get("/rooms")
def list_rooms() -> list[dict]:
    """Every active room, with its channel — chat, voice, video, AR or VR —
    so a console can show the doors instead of asking for an id."""
    conn = db.connect()
    rows = conn.execute(
        "SELECT r.*, COUNT(p.room_id) AS heads FROM rooms r"
        " LEFT JOIN room_participants p ON p.room_id = r.id"
        " WHERE r.status='active' GROUP BY r.id ORDER BY r.created_at DESC"
    ).fetchall()
    # The roster, before the door: the field report said people should be
    # able to look before entering, and a separate screen for looking was
    # a screen too many. Names only — the same words the room shows the
    # moment you join — capped so a crowded room stays a list, not a wall.
    out = []
    for r in rows:
        seated = conn.execute(
            "SELECT kind, ref_id FROM room_participants WHERE room_id=?"
            " LIMIT 6", (r["id"],)).fetchall()
        out.append({
            "id": r["id"], "topic": r["topic"], "channel": r["channel"],
            "participants": r["heads"], "created_at": r["created_at"],
            "who": [_display(p["kind"], p["ref_id"]) for p in seated],
        })
    return out


@router.post("/rooms/{room_id}/mic", status_code=201)
def lend_room_mic(room_id: str, body: RoomMicLend, request: Request) -> dict:
    """Lend this room's profiles your wearable's microphone.

    In a voice or video room your own microphone is carrying your voice to the
    other people; the profiles are reading text and have no ear. This lends
    them the watch on your wrist, for context, while the primary is busy.

    Everyone in the room can see that you did — see `GET …/mic`.
    """
    interactor_or_404(body.interactor_id)
    require_interactor(body.interactor_id, request)
    try:
        return roommic.lend(room_id, body.interactor_id, body.device,
                            body.mic_type, body.gain)
    except roommic.RoomMicError as exc:
        raise HTTPException(403, i18n.raised(exc))


@router.delete("/rooms/{room_id}/mic/{interactor_id}")
def take_back_room_mic(room_id: str, interactor_id: str,
                       request: Request) -> dict:
    """Take your microphone back."""
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    return roommic.take_back(room_id, interactor_id)


@router.get("/rooms/{room_id}/mic")
def room_mic_disclosure(room_id: str, request: Request) -> dict:
    """Who in this room has lent the profiles a microphone.

    Deliberately readable by anyone **in the room** rather than by the lender
    alone: the people who need to know are the other participants, and a
    disclosure only its subject can see is not a disclosure.

    "In the room" is the whole of it, though, and for a while this route only
    said so. It checked nothing, so it answered anybody holding a room id —
    and a room id is not a secret: it rides in beacons and on printed QR
    stickers, which is the point of them. That made a privacy feature into the
    opposite one, publishing who is wearing a live microphone, on what, and
    since when, to whoever scanned the sticker. Widening a disclosure past the
    people it protects is not a smaller version of the same idea.
    """
    _room_or_404(room_id)
    _require_in_room(room_id, request)
    return roommic.disclosure(room_id)


def _require_user_in_room(room_id: str, request: Request) -> str:
    """The caller, as a **user** participant of this room. Returns their id.

    A room turn is spoken by a person, so an owner token — which
    :func:`_require_in_room` accepts, because a profile's owner is entitled to
    the disclosure — is not enough to speak here.
    """
    who = _require_in_room(room_id, request)
    if not any(p["kind"] == "user" and p["ref_id"] == who
               for p in _participants(room_id)):
        raise HTTPException(
            403, "a room turn is spoken by a person, so this needs the token "
                 "of a user participant rather than a profile's owner token")
    return who


@router.post("/rooms/{room_id}/messages", status_code=201)
def room_message(room_id: str, body: RoomMessage, request: Request) -> dict:
    """A user participant speaks; every profile participant answers.

    **The speaker is the token, never the body.** This used to read
    ``body.sender_id`` and check only that the id named a participant — not
    that the *caller* was that participant. So anybody holding a room id could
    put words in a named person's mouth: the message stored under their name,
    the transcript showing `from: Ada`, and every profile in the room
    answering it as though she had spoken.

    A room id is not a secret. It rides in beacons and on printed QR stickers,
    which is the point of them — the argument is already written out in
    :func:`room_mic_disclosure`, where it was applied to who may *read* who
    lent a microphone and not to who may speak.

    ``sender_id`` stays on the model because three shipped native clients send
    it, and is ignored. Reading it would be the defect.
    """
    room = _room_or_404(room_id)
    speaker = _require_user_in_room(room_id, request)
    participants = _participants(room_id)
    maturity = _room_maturity(participants)
    verdict = moderation.review(body.message, None, {"birthdate": None},
                                maturity=maturity)
    # Recorded before the profiles take their turn, so the history they read
    # already carries it. Written onto the interrupted turn rather than kept
    # beside it: it is a fact about that turn, and every profile in the room
    # reads the same transcript.
    if body.cut_off_id and body.cut_off_heard is not None:
        db.connect().execute(
            "UPDATE room_messages SET heard=? WHERE id=? AND room_id=?"
            "  AND sender_kind='profile'",
            (body.cut_off_heard[:4000], body.cut_off_id, room_id))
        db.connect().commit()
    # A link in the message is read before storing, the share door's own
    # ordering: the very first profile turn already carries the page, with
    # no one-turn hole in which a profile denies seeing what it can see.
    lwords, ldigest, lwhy = ("", "", "")
    if verdict.approved:
        lwords, ldigest, lwhy = _read_link(body.message, speaker)
    # The words-only controls — the sentences that replaced the toggle
    # button: a release phrase lifts the ten-turn governor "on the user's
    # choice and dime", a pause phrase puts it back, and any ordinary
    # message already resets the governor's count by being a user turn.
    conn = db.connect()
    if society.said_release(body.message):
        conn.execute("UPDATE rooms SET free_run=1 WHERE id=?", (room_id,))
        conn.commit()
    elif society.said_pause(body.message):
        conn.execute("UPDATE rooms SET free_run=0 WHERE id=?", (room_id,))
        conn.commit()
    cast = _room_cast(participants)
    aim = society.aim_of(body.message, cast)
    sent = _store_room_message(room_id, "user", speaker, body.message,
                               verdict.approved, verdict.reason,
                               media_text=lwords, media_digest=ldigest,
                               media_why=lwhy,
                               aimed_at=(aim or {}).get("display"))
    # One seat answers, not eight at once: the seat the message was aimed
    # at, or the next in rotation. "They announce who the statement is
    # directed towards, and if an inbound message doesn't contain anything
    # to do with their own profile, they will wait their turn."
    replies = []
    if verdict.approved and cast:
        speaker_seat = society.next_speaker(
            cast, _approved_history(room_id), {}, True)
        if speaker_seat is not None:
            replies = _profile_turns(room, participants,
                                     request.app.state.pdi,
                                     request.app.state.cloud,
                                     only={speaker_seat["ref_id"]})
    return {"message": sent, "replies": replies}


@router.post("/rooms/{room_id}/sit-out")
def room_sit_out(room_id: str, body: RoomSitOut, request: Request) -> dict:
    """A person's seat steps out of the rotation's waiting, or back in.

    The field ask, in its own words: *"a sit out button for the user
    orchestrating chats... that stops rotation and allows the other
    synthetic profiles to go back-and-forth or have their own rotation
    while your spot sits out, and un-tap that button to sit back in."*

    What sits out is the WAITING, not the seat: the person stays in the
    room, still reads every turn, still holds the microphone and the
    send button, and one word from them puts them back in the middle of
    it. What stops is the room pausing to hand them the floor — the
    governor's hand-back has nobody to hand to while everybody present
    has stepped away, so the profiles keep their own rotation.

    Kept on the seat rather than in the browser: a room the person
    reopens tomorrow is the room they left, and a second device shows
    the same posture rather than arguing with the first.
    """
    _room_or_404(room_id)
    who = _require_in_room(room_id, request)
    conn = db.connect()
    row = conn.execute(
        "SELECT kind FROM room_participants WHERE room_id=? AND ref_id=?",
        (room_id, who)).fetchone()
    if row is None or row["kind"] != "user":
        # A profile's owner holds their profile's seat, and a profile
        # sitting out of its own rotation is not what this is for — it
        # is the person's spot that steps aside.
        raise HTTPException(
            422, "only a person's own seat can sit out of a room")
    conn.execute(
        "UPDATE room_participants SET sitting_out=? WHERE room_id=?"
        "  AND ref_id=?", (1 if body.out else 0, room_id, who))
    conn.commit()
    participants = _participants(room_id)
    return {"sitting_out": bool(body.out),
            # Whether the room now runs without waiting for anybody —
            # the state the screen paints, said by the server rather
            # than guessed from one seat's switch.
            "nobody_waiting": _nobody_waiting(participants)}


@router.post("/rooms/{room_id}/advance", status_code=201)
def room_advance(room_id: str, request: Request) -> dict:
    """Profiles take a turn unprompted — profile↔profile rooms run on this.

    Anyone in the room may advance it, including a profile's owner: a
    profile↔profile room has no user participant to press the button, and its
    owners are exactly who it is for. What it is not open to is a stranger
    holding the room id, who could otherwise run a room forward indefinitely
    against somebody else's model key.
    """
    room = _room_or_404(room_id)
    _require_in_room(room_id, request)
    participants = _participants(room_id)
    if not any(p["kind"] == "profile" for p in participants):
        raise HTTPException(422, "no synthetic profiles in this room")
    # One seat per advance, chosen by the society: the newest turn's aim,
    # or rotation past the person's silent seat — "rotation will continue,
    # even though user isn't taking his turn, and will instigate a
    # back-and-forth anyways." The governor holds the other line: ten
    # unprompted turns apiece and the room pauses for a person, unless
    # the person lifted it in words.
    cast = _room_cast(participants)
    history = _approved_history(room_id)
    # A room whose people have all sat out has nobody to pause for, so
    # the governor's hand-back would be a wait on somebody who said they
    # were stepping away: the profiles keep their own rotation until a
    # seat sits back in.
    speaker_seat = society.next_speaker(cast, history,
                                        _spoken_counts(history),
                                        bool(room.get("free_run"))
                                        or _nobody_waiting(participants))
    if speaker_seat is None:
        return {"replies": [], "paused": True}
    return {"replies": _profile_turns(room, participants,
                                      request.app.state.pdi,
                                      request.app.state.cloud,
                                      only={speaker_seat["ref_id"]}),
            "paused": False}


@router.get("/rooms/{room_id}/messages")
def room_transcript(room_id: str, request: Request) -> list[dict]:
    """What has been said in this room, to the people in it.

    It took no token at all, so the whole transcript — what a named person
    typed, and what every profile answered — was readable by anybody who knew
    the room id. The same room id that rides on a printed sticker.

    The reasoning is the one already written down for the microphone
    disclosure two routes up, which is the *narrower* fact: who is wearing a
    live microphone was held to a standard the conversation itself was not.
    """
    _room_or_404(room_id)
    _require_in_room(room_id, request)
    rows = db.connect().execute(
        "SELECT * FROM room_messages WHERE room_id=? AND status='approved'"
        " ORDER BY created_at, rowid", (room_id,)).fetchall()
    # `sender_id` rides along so a client can follow a turn back to the
    # thing that produced it — a profile turn to the voice route, a person's
    # to nothing. It names a fellow participant, which is who the read is
    # already scoped to.
    return [{"id": r["id"], "sender_kind": r["sender_kind"],
             "sender_id": r["sender_id"],
             "from": _display(r["sender_kind"], r["sender_id"]),
             "content": r["content"],
             # The announced aim, worn on the turn — who it was for.
             "aimed_at": (r["aimed_at"]
                          if "aimed_at" in r.keys() else None),
             "watermark": watermark.brief(r["watermark_id"]),
             "media": _media_brief(
                 r["media_id"] if "media_id" in r.keys() else None,
                 bool(r["media_digest"]
                      if "media_digest" in r.keys() else None),
                 r["media_why"] if "media_why" in r.keys() else None,
                 r["media_full"] if "media_full" in r.keys() else None,
                 len(r["media_text"] or "")
                 if "media_text" in r.keys() else None),
             "created_at": r["created_at"]}
            for r in rows]


# --------------------------------------------------------------------------- #
# marketplace listings
# --------------------------------------------------------------------------- #

def _claimants(listing_id: str) -> set[str]:
    """Everyone with a stake in this listing, and therefore a say in whether
    it stays up.

    Three sources, any of which is enough:

    * whoever created it, when they were signed in at the time;
    * the seller recorded on its offer — the account a purchase pays;
    * the owner of the profile it advertises, for a ``profile`` listing.

    An empty set is a real answer, not a missing one: a listing made by an
    anonymous caller, never priced, advertising nobody. Nothing is staked on
    it and nobody is wronged by its removal.
    """
    conn = db.connect()
    out: set[str] = set()
    row = conn.execute("SELECT claimant_id FROM listing_claims WHERE"
                       " listing_id=?", (listing_id,)).fetchone()
    if row:
        out.add(row["claimant_id"])
    offer = conn.execute("SELECT seller_id FROM listing_offers WHERE"
                         " listing_id=?", (listing_id,)).fetchone()
    if offer:
        out.add(offer["seller_id"])
    listing = conn.execute("SELECT profile_id FROM listings WHERE id=?",
                           (listing_id,)).fetchone()
    if listing and listing["profile_id"]:
        prof = conn.execute("SELECT owner_id FROM profiles WHERE id=?",
                            (listing["profile_id"],)).fetchone()
        if prof:
            out.add(prof["owner_id"])
            out.add(listing["profile_id"])
    return out


def _may_alter(listing_id: str, request: Request) -> None:
    """403 unless the caller is one of the listing's claimants.

    The identity compared is the token's subject — an interactor id for a
    person, a profile id for an owner token — against the set above, which
    holds both kinds for that reason. An owner token also matches its
    profile's ``owner_id``, so any of an account's profiles can act for a
    listing the account put up.
    """
    claimants = _claimants(listing_id)
    if not claimants:
        return
    who = auth.principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["subject_id"] not in claimants:
        raise HTTPException(403, "not your listing")


def create_listing(body: ListingCreate, claimant: str | None = None) -> dict:
    """Put something in the window.

    Called by the route below and directly by the seeders, which have no
    request to read a token from. ``claimant`` is therefore a plain argument
    rather than something dug out of a ``Request``: a seeded listing has no
    claimant and is not supposed to — the starter collection belongs to the
    deployment, and a listing nobody staked anything on is one anybody may
    clear away.
    """
    if body.kind == "profile":
        if not body.profile_id:
            raise HTTPException(422, "profile listings require profile_id")
        profile_or_404(body.profile_id)
    conn = db.connect()
    listing_id = db.new_id("lst")
    conn.execute(
        "INSERT INTO listings (id, kind, title, blurb, tags, area,"
        " provider_name, business, profile_id, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (listing_id, body.kind, body.title, body.blurb, json.dumps(body.tags),
         body.area, body.provider_name, int(body.business), body.profile_id,
         db.utcnow()),
    )
    if claimant is not None:
        conn.execute(
            "INSERT OR IGNORE INTO listing_claims (listing_id, claimant_id,"
            " created_at) VALUES (?,?,?)",
            (listing_id, claimant, db.utcnow()))
    conn.commit()
    return {"id": listing_id, "kind": body.kind, "title": body.title,
            "claimed_by": claimant}


@router.post("/marketplace/listings", status_code=201)
def post_listing(body: ListingCreate, request: Request) -> dict:
    """Still needs no token — that is the design and it has not changed — but
    a caller who *has* one is recorded as the listing's claimant, which is
    what makes it theirs to move or take down.
    """
    who = auth.principal(request)
    return create_listing(body, who["subject_id"] if who else None)


@router.post("/marketplace/seed", status_code=201)
def seed_marketplace() -> dict:
    """Populate the starter collection: one synthetic expert per industry,
    each with a claimed @handle and a marketplace listing, so a fresh
    deployment has profiles to immerse with before users publish their own.

    Idempotent, and also a **repair**: a starter that already exists keeps its
    profile but has a missing portrait or appearance filled in, so a deployment
    created before the portraits shipped gets its faces back by running this
    again. Blank-only — anything an owner set is left alone. The response
    reports `repaired` alongside `created` and `skipped`."""
    from .. import seed
    return seed.seed()


@router.get("/marketplace/listings")
def browse_listings(request: Request, kind: str | None = None,
                    tag: str | None = None,
                    area: str | None = None) -> list[dict]:
    from .. import rated

    conn = db.connect()
    rows = conn.execute(
        "SELECT * FROM listings ORDER BY created_at DESC, rowid DESC").fetchall()
    adult_viewer = rated.viewer_is_adult(request)
    out = []
    for row in rows:
        tags = json.loads(row["tags"])
        if kind and row["kind"] != kind:
            continue
        if tag and tag.lower() not in [t.lower() for t in tags]:
            continue
        if area and (row["area"] or "").lower() != area.lower():
            continue
        if row["profile_id"] and not adult_viewer:
            # Rated profiles never surface in an unverified browse.
            p = conn.execute("SELECT adult_mode FROM profiles WHERE id=?",
                             (row["profile_id"],)).fetchone()
            if p and p["adult_mode"]:
                continue
        out.append({"id": row["id"], "kind": row["kind"],
                    "title": row["title"], "blurb": row["blurb"],
                    "tags": tags, "area": row["area"],
                    "provider_name": row["provider_name"],
                    "business": bool(row["business"]),
                    "profile_id": row["profile_id"]})
    return out


# --------------------------------------------------------------------------- #
# marketplace search: words, place, settings, and a hand with the words
# --------------------------------------------------------------------------- #

@router.get("/marketplace/search")
def search_listings(request: Request, q: str | None = None,
                    kind: str | None = None, tag: str | None = None,
                    area: str | None = None, scope: str | None = None,
                    locality: str | None = None, region: str | None = None,
                    include_remote: bool | None = None,
                    limit: int = 50) -> dict:
    """Rank listings by words and by place.

    Deterministic: two callers passing the same arguments get the same order,
    and the response says which terms matched which fields. A signed-in
    interactor's saved settings supply the defaults; anything passed here
    wins over them.
    """
    from .. import rated

    who = auth.principal(request)
    interactor_id = who["subject_id"] if who and who["role"] == "interactor" \
        else None
    try:
        return marketplace.search_with_prefs(
            interactor_id, q, kind=kind, tag=tag, area=area, scope=scope,
            locality=locality, region=region, include_remote=include_remote,
            adult_viewer=rated.viewer_is_adult(request), limit=limit)
    except marketplace.MarketError as exc:
        raise HTTPException(422, i18n.raised(exc))


@router.get("/marketplace/localities")
def marketplace_localities() -> list[dict]:
    """Every place a listing actually claims, with counts — so a searcher
    picks from what exists instead of typing a spelling nothing matches."""
    return marketplace.localities()


@router.put("/marketplace/listings/{listing_id}/place")
def set_listing_place(listing_id: str, body: ListingPlace,
                      request: Request) -> dict:
    """Say where a listing is offered. Refused for a rated listing: where a
    performer physically is has nothing to do with browsing them.

    Claimant-gated for the same reason removal is. Moving somebody's listing
    to another city is a quieter version of taking it down — it stops being
    found by the people it was put up for, and nothing about it looks wrong.
    """
    _may_alter(listing_id, request)
    try:
        return marketplace.set_place(listing_id, body.locality, body.region,
                                     body.remote)
    except marketplace.MarketError as exc:
        raise HTTPException(
            404 if i18n.raised(exc).startswith("no such") else 422, i18n.raised(exc))


@router.delete("/marketplace/listings/{listing_id}/place")
def clear_listing_place(listing_id: str, request: Request) -> dict:
    _may_alter(listing_id, request)
    return marketplace.clear_place(listing_id)


@router.get("/marketplace/settings/{interactor_id}")
def get_market_settings(interactor_id: str, request: Request) -> dict:
    interactor_or_404(interactor_id)
    auth.require(request, "interactor", interactor_id)
    return marketplace.prefs(interactor_id)


@router.put("/marketplace/settings/{interactor_id}")
def put_market_settings(interactor_id: str, body: MarketPrefs,
                        request: Request) -> dict:
    """Save where "here" is and how far out to look. Typed, never sniffed —
    location a user did not enter is location they did not agree to share."""
    interactor_or_404(interactor_id)
    auth.require(request, "interactor", interactor_id)
    try:
        return marketplace.set_prefs(
            interactor_id, locality=body.locality, region=body.region,
            scope=body.scope, include_remote=body.include_remote,
            kinds=body.kinds, tags=body.tags)
    except marketplace.MarketError as exc:
        raise HTTPException(422, i18n.raised(exc))


@router.post("/marketplace/assist")
def assist_search(body: MarketAssist, request: Request) -> dict:
    """Turn "I don't know what to search for" into candidate searches.

    Returns **suggestions, never results**. Nothing is searched, filtered or
    reordered on the caller's behalf — they take a suggestion to the search
    box themselves, and get the same deterministic ranking as everyone else.
    """
    who = auth.principal(request)
    interactor_id = who["subject_id"] if who and who["role"] == "interactor" \
        else None
    try:
        return marketplace.assist(
            body.need, interactor_id=interactor_id,
            provider=llm.get_provider(cloud=request.app.state.cloud))
    except marketplace.MarketError as exc:
        raise HTTPException(422, i18n.raised(exc))


@router.delete("/marketplace/listings/{listing_id}", status_code=204)
def remove_listing(listing_id: str, request: Request) -> None:
    """Take it out of the window. Only a claimant may.

    This used to ask for nothing at all, which made it the widest door in the
    marketplace: a stranger could remove a listing that had a seller, an open
    offer and paid orders against it, and the same stranger asking to withdraw
    the *offer* on that listing was told "not your offer". The offer, the
    orders and the seller's ledger all survived — the shop window was simply
    gone, and the title was free for somebody else to put up.
    """
    conn = db.connect()
    if conn.execute("SELECT 1 FROM listings WHERE id=?",
                    (listing_id,)).fetchone() is None:
        raise HTTPException(404, "listing not found")
    _may_alter(listing_id, request)
    conn.execute("DELETE FROM listing_claims WHERE listing_id=?",
                 (listing_id,))
    conn.execute("DELETE FROM listings WHERE id=?", (listing_id,))
    conn.commit()


# --------------------------------------------------------------------------- #
# providers & consented handoffs
# --------------------------------------------------------------------------- #

@router.post("/providers", status_code=201)
def register_provider(body: ProviderCreate) -> dict:
    conn = db.connect()
    provider_id = db.new_id("prv")
    conn.execute(
        "INSERT INTO providers (id, name, area, location, contact, business,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (provider_id, body.name, body.area, body.location, body.contact,
         int(body.business), db.utcnow()),
    )
    conn.commit()
    return {"id": provider_id, "name": body.name, "area": body.area}


@router.get("/providers")
def list_providers(area: str | None = None) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM providers ORDER BY created_at, rowid").fetchall()
    return [{**dict(r), "business": bool(r["business"])}
            for r in rows if not area or r["area"].lower() == area.lower()]


@router.post("/handoffs", status_code=201)
def create_handoff(body: HandoffCreate, request: Request) -> dict:
    """Hand a session from the AI specialist to a real local provider —
    only with the user's explicit consent, behind a revocable token."""
    if not body.consent:
        raise HTTPException(
            403, "a handoff requires the user's explicit consent")
    interactor = interactor_or_404(body.interactor_id)
    provider = db.connect().execute(
        "SELECT * FROM providers WHERE id=?", (body.provider_id,)).fetchone()
    if provider is None:
        raise HTTPException(404, "provider not found")

    package: dict = {"user": interactor["display_name"],
                     "provider_area": provider["area"], "sessions": None}
    if body.profile_id:
        profile = profile_or_404(body.profile_id)
        conn = db.connect()
        recent = conn.execute(
            "SELECT role, content FROM messages WHERE profile_id=?"
            " AND interactor_id=? AND status='approved'"
            " ORDER BY created_at DESC, rowid DESC LIMIT 6",
            (body.profile_id, body.interactor_id)).fetchall()
        state = engagement.get(body.profile_id, body.interactor_id)
        package.update({
            "specialist": profile["display_name"],
            "specialist_purpose": profile["purpose"],
            "sessions": state["sessions"] if state else 0,
            "recent_exchange": [
                {"role": r["role"], "content": r["content"]}
                for r in reversed(recent)
            ],
        })

    conn = db.connect()
    handoff_id = db.new_id("hnd")
    token = f"hnd_{secrets.token_urlsafe(24)}"
    pdi = request.app.state.pdi
    stored, pdi_key = json.dumps(package), None
    if pdi is not None:
        pdi_key = f"qrme/handoffs/{handoff_id}"
        pdi.put(pdi_key, stored)
        stored = None                 # sealed — only the key stays local
    conn.execute(
        "INSERT INTO handoffs (id, interactor_id, profile_id, provider_id,"
        " package, pdi_key, token, revoked, created_at)"
        " VALUES (?,?,?,?,?,?,?,0,?)",
        (handoff_id, body.interactor_id, body.profile_id, body.provider_id,
         stored, pdi_key, token, db.utcnow()),
    )
    conn.commit()
    return {"id": handoff_id, "provider": provider["name"],
            "area": provider["area"], "token": token,
            "sealed": pdi_key is not None}


@router.get("/handoffs/{handoff_id}")
def read_handoff(handoff_id: str, token: str, request: Request) -> dict:
    """The provider redeems the token to receive the session package."""
    row = db.connect().execute("SELECT * FROM handoffs WHERE id=?",
                               (handoff_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "handoff not found")
    if row["revoked"] or token != row["token"]:
        raise HTTPException(403, "token invalid or revoked")
    if row["pdi_key"] and request.app.state.pdi is not None:
        raw = request.app.state.pdi.get(row["pdi_key"])
        package = json.loads(raw) if raw else None
    else:
        package = json.loads(row["package"]) if row["package"] else None
    return {"id": handoff_id, "package": package}


@router.delete("/handoffs/{handoff_id}")
def revoke_handoff(handoff_id: str, request: Request) -> dict:
    """The user changes their mind: revoke access and purge the package."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM handoffs WHERE id=?",
                       (handoff_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "handoff not found")
    conn.execute("UPDATE handoffs SET revoked=1, package=NULL WHERE id=?",
                 (handoff_id,))
    conn.commit()
    if row["pdi_key"] and request.app.state.pdi is not None:
        request.app.state.pdi.delete(row["pdi_key"])
    return {"id": handoff_id, "revoked": True}


# --------------------------------------------------------------------------- #
# medical referrals — a handoff signed for, rather than consented to
# --------------------------------------------------------------------------- #
#
# The handoff above releases on `consent: true`, a boolean the client sets.
# For a health conversation leaving the product that is the "the app says the
# user agreed" problem qrme/webauthn.py exists to solve — and the whole
# signing stack was already here, unused by the one endpoint that needed it.

def _rp_id() -> str:
    import os
    return os.environ.get("QRME_RP_ID", "qrme.app")


@router.get("/referrals/match")
def match_clinicians(area: str, location: str | None = None,
                     limit: int = 5) -> list[dict]:
    """Clinicians who can help, nearest first.

    Expertise filters, geography ranks — never the reverse. Returns an empty
    list rather than a near-miss: a confident wrong referral is somebody
    phoning a clinic that cannot help them.
    """
    return referral.match(area, location, limit)


@router.post("/referrals/prepare", status_code=201)
def prepare_referral(body: ReferralPrepare, request: Request) -> dict:
    """Assemble the summary and raise the signature that would release it.

    **Nothing is released here.** The response carries the package so the user
    can read exactly what would go, and a WebAuthn challenge whose value *is*
    the hash of those bytes — sign it with Face ID and you have signed this
    summary, not a checkbox.
    """
    interactor = interactor_or_404(body.interactor_id)
    require_interactor(body.interactor_id, request)
    profile = profile_or_404(body.profile_id)
    # Refused here, before any clinician is contacted, rather than when the
    # note comes back. A clinician's written opinion about a real person does
    # not go in the open store, and refusing at the reply would strand a real
    # person who has already been written to, mid-flow, holding words they
    # cannot file. See `storage.SENSITIVE["clinical_note"]`.
    try:
        storage.require(tiers.plan_of_profile(profile["id"]), "clinical_note")
    except storage.StorageError as exc:
        raise HTTPException(402, i18n.raised(exc)) from None
    try:
        return referral.prepare(
            interactor, profile, body.provider_id,
            account_id=f"interactor:{body.interactor_id}", rp_id=_rp_id())
    except referral.ReferralError as exc:
        raise HTTPException(422, i18n.raised(exc))


@router.post("/referrals/{referral_id}/release")
def release_referral(referral_id: str, body: ReferralRelease,
                     request: Request) -> dict:
    """Mint the one-time link, if the signature really authorises this one.

    Checked: that the assertion verifies, that it was raised for this
    referral, and that it covers the bytes about to be sent — a summary edited
    after signing cannot ride the old signature.
    """
    row = referral.get(referral_id)
    if row is None:
        raise HTTPException(404, "no such referral")
    require_interactor(row["interactor_id"], request)
    try:
        return referral.release(referral_id, body.signature_id)
    except referral.ReferralError as exc:
        raise HTTPException(403, i18n.raised(exc))


@router.get("/referrals/{referral_id}")
def open_referral(referral_id: str, token: str) -> dict:
    """The clinician opens it. Once — a second attempt says so rather than
    quietly working, because a replayed link is something the patient should
    be able to discover."""
    try:
        return referral.redeem(referral_id, token)
    except referral.ReferralError as exc:
        raise HTTPException(410 if "already opened" in i18n.raised(exc) else 403,
                            i18n.raised(exc))


@router.post("/referrals/{referral_id}/reply", status_code=201)
def reply_to_referral(referral_id: str, token: str, body: ReferralReply,
                      request: Request) -> dict:
    """The clinician writes back, once — so the profile is caught up and the
    patient does not have to explain it all again.

    Sealed in the PDI vault like source material, but recorded separately and
    surfaced to the profile as *that clinician's words*: it never becomes
    something the profile can recite as its own knowledge, and never reaches a
    workflow's `research` phase.
    """
    try:
        return referral.reply(referral_id, token, body.content,
                              pdi=request.app.state.pdi)
    except referral.ReferralError as exc:
        raise HTTPException(403, i18n.raised(exc))


@router.get("/profiles/{profile_id}/clinical-notes/{interactor_id}")
def read_clinical_notes(profile_id: str, interactor_id: str,
                        request: Request) -> list[dict]:
    """What a clinician wrote back on this conversation.

    The pair may read it — the person it is about, and the profile's owner —
    and nobody else: it is that person's medical information.
    """
    profile_or_404(profile_id)
    require_owner_or_interactor(profile_id, interactor_id, request)
    return referral.notes_for(profile_id, interactor_id,
                              request.app.state.pdi)


@router.get("/interactors/{interactor_id}/referrals")
def my_referrals(interactor_id: str, request: Request) -> list[dict]:
    """What this person has released, to whom, and whether it was opened."""
    interactor_or_404(interactor_id)
    require_interactor(interactor_id, request)
    return referral.history(interactor_id)
