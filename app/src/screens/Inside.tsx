import { useEffect, useRef, useState } from "react";
import { isEcho, RECENT_TURNS } from "../echo";
import { api, getBase, type Avatar, type MicsHere, type RoomFaces,
         type RoomMsg } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { speakInPieces } from "../spoken";
import { useSession } from "../store";

/**
 * Inside a room.
 *
 * `Rooms` opens one and lists what is live. It could not put you in it: the
 * console had no way to read a transcript, say anything, let the profiles
 * take a turn, or lend them a microphone. Six routes, four of them behind
 * `api.ts` bindings that no screen called — which is exactly what
 * `test_a_binding_is_not_a_door.py` was written to find, and building this
 * one found two defects worth more than the screen.
 *
 * ## Who may speak, and who may read
 *
 * `POST /rooms/{id}/messages` took the speaker from `sender_id` **in the
 * body**, and checked only that the id named a participant — never that the
 * caller was that person. Anybody holding a room id could put words in a
 * named participant's mouth: stored under their name, rendered `from: Ada`,
 * and answered by every profile in the room as though she had spoken.
 *
 * `GET /rooms/{id}/messages` asked for nothing at all, so the whole
 * conversation was readable by anyone who knew the id.
 *
 * A room id is not a secret — it rides in beacons and on printed QR
 * stickers, which is the point of them. That sentence was already written
 * down two routes away, on `GET /rooms/{id}/mic`, guarding the *narrower*
 * fact: who is wearing a live microphone was held to a standard the
 * conversation itself was not.
 *
 * ## The microphone is a disclosure, not a setting
 *
 * Lending one is shown to everybody in the room, because a microphone
 * somebody else cannot see is the thing this feature exists not to be. The
 * list is rendered whether or not you are the lender.
 *
 * ## The box is where you decide what people see of you
 *
 * The scene drew everybody in their own box and a box held one thing: two
 * initials and a name. Three controls live on your own box now — your camera,
 * a picture you upload, and the mask machinery `overlays` has owned since it
 * shipped and which was reachable only from a screen where you type a surface
 * name and a room id by hand.
 *
 * All three states are a box, at the same size, in the same place. A person
 * who has their camera off is still here, and a scene that shrinks or drops
 * them answers *who is talking* while losing *who is here*.
 *
 * **Only your own box carries controls.** Deciding what somebody else's box
 * shows is not something this product offers, and the route refuses it — but
 * a control that renders and then refuses is worse than one that is absent.
 */
// What a worn mask draws over your own preview, per catalogue kind. Your
// pixels never leave this device — the other seats show an on-air marker,
// not your stream — so the wearer's preview is the only place a mask can
// render at all, and until this map existed it rendered nowhere: the mask
// machinery recorded the disclosure and drew nothing, which read as broken.
//
// The glyph rides the box, not your facial landmarks. That is the honest
// budget of a beta with no face tracking, and the disclosure line stays the
// truth-bearing part. Three kinds are treatments of the video itself and
// carry a CSS class instead; `backdrop` would need segmentation this beta
// does not have, so it stays disclosure-only.
const MASK_GLYPHS: Record<string, string> = {
  mask: "\u{1F3AD}", half_mask: "\u{1F978}", character: "\u{1F9B9}",
  creature: "\u{1F98A}", puppet: "\u{1FA86}", avatar_2d: "\u{1F5BC}\uFE0F",
  avatar_3d: "\u{1F5FF}", helmet_hud: "\u{1FA96}", paint: "\u{1F3A8}",
  makeup: "\u{1F484}", hair: "\u{1F9D4}", headwear: "\u{1F3A9}",
  eyewear: "\u{1F576}\uFE0F", prosthetic: "\u{1F47A}",
  stylised: "\u{1F58C}\uFE0F",
};
const MASK_TREATMENTS: Record<string, string> = {
  obscured: " rs-obscured", silhouette: " rs-silhouette",
  touch_up: " rs-touchup",
};

/** The minimal face of the browser's recogniser — typed here because the
 *  DOM lib ships none, the same bargain the Agent screen struck. */
type SpeechRec = {
  lang: string; interimResults: boolean; continuous: boolean;
  onresult:
    ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void)
    | null;
  onend: (() => void) | null;
  start(): void; stop(): void;
};

/** How long a person's silence means they have finished saying it.
 *
 *  A field report, holding the send button: "while speaking, we should
 *  have like 4 to 5 seconds of silence will send instead of having to
 *  press this button."
 *
 *      asked     is the microphone open
 *      mattered  does anything happen when you stop talking
 *
 *  Deliberately longer than JIM's 2.5 seconds. That number ends a TURN in
 *  a two-way conversation, where cutting somebody off costs one
 *  interruption. This one commits a sentence to a ROOM with other people
 *  in it, where the same mistake sends half a thought to everybody — so
 *  it waits nearly twice as long, at the near end of the range the report
 *  asked for.
 */
const SILENCE_SENDS_MS = 5000;

/** Whether this browser ships a speech recogniser at all (iOS Safari does
 *  not). Module scope rather than a body const: the effect that opens the
 *  standing ear runs above where this used to be declared, and a `const`
 *  read before its line is a dead-zone crash rather than a false. */
/** A phone, rather than a narrow window on a computer. The held overlay
 *  exists because a phone in a full-screen room has no window edge, no tab
 *  strip and no back button — a desktop browser has all three, and a
 *  gesture invented to replace them there would be a gesture nobody needs
 *  and nobody would find. Coarse pointer is the honest test: it asks about
 *  the input, which is what the gesture is actually about. */
const onAPhone = typeof window !== "undefined"
  && typeof window.matchMedia === "function"
  && window.matchMedia("(pointer: coarse)").matches;

const canDictate = typeof window !== "undefined"
  && Boolean((window as unknown as { SpeechRecognition?: unknown;
                                     webkitSpeechRecognition?: unknown })
      .SpeechRecognition
    || (window as unknown as { webkitSpeechRecognition?: unknown })
      .webkitSpeechRecognition);

export function Inside({ onPlans, start = "", onLeave }: {
  onPlans: () => void;
  /** A room id handed in by the Rooms screen's join — the field is
   *  prefilled so the person lands in the room they just entered. */
  start?: string;
  /** Step back out. Required once a room owns the window: the sidebar
   *  that used to be the way out is hidden while somebody is standing in
   *  a room, and a full-screen place with no door is a trap. */
  onLeave?: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.interactorId || "";
  const token = session.interactorToken || "";

  const [roomId, setRoomId] = useState(start);
  const [transcript, setTranscript] = useState<RoomMsg[]>([]);
  const [mics, setMics] = useState<MicsHere | null>(null);
  const [seats, setSeats] = useState<
    { kind: string; id: string; display: string }[]>([]);
  const [draft, setDraft] = useState("");
  const [scene, setScene] = useState<RoomFaces | null>(null);
  // The room's own channel, read off the join answer. `chat`, `voice` and
  // `video` present flat; `ar` and `vr` are the two the homepage sells as
  // *places*, and until this state existed the screen rendered them as the
  // same flat grid — the channel was a badge on the way in and nothing
  // inside. The scene card offers a stage for both now.
  const [channel, setChannel] = useState("");
  // The immersive stage. Entered by a press and left by one — never on the
  // room's behalf, because going fullscreen and turning sensors on are
  // decisions a person makes, not properties a room has.
  const [immersed, setImmersed] = useState(false);
  // VR look direction: degrees of yaw, driven by dragging the stage. The
  // seats sit on a turntable this angle turns.
  const [yaw, setYaw] = useState(0);
  const dragFrom = useRef<{ x: number; yaw: number } | null>(null);
  // AR passthrough — the device's world-facing camera as the stage floor.
  // Deliberately separate from the room-face camera machinery: this stream
  // renders your surroundings to you and only you, shares no fact with the
  // room, and stops the moment you step out.
  const pass = useRef<HTMLVideoElement>(null);
  const passStream = useRef<MediaStream | null>(null);
  const [passDenied, setPassDenied] = useState(false);
  const [masks, setMasks] = useState<
    { kind: string; covers_face: boolean; means: string }[]>([]);
  // The synthetic seats' portraits. `GET /profiles/{id}/avatar` is the one
  // shape every surface reads — 2-D, 3-D, VR, AR — and it carries the AI
  // badge and the likeness record with the picture, so this screen cannot
  // show the face without having been handed the disclosure. Until this map
  // existed a profile seat drew two initials while the platform held a whole
  // portrait for it, which read as "my agent has no avatar".
  const [aiFaces, setAiFaces] = useState<Record<string, Avatar>>({});
  // My own profile's portrait, for my own seat.
  //
  // A person's seat drew initials while the platform held their picture —
  // the same defect the note above describes for profile seats, never
  // fixed for the other half. Field report, looking at a room holding both
  // of his: "I don't know why both profile photos don't show up, one says
  // You with a Y on it. It should be my image that I have on my profile."
  //
  //     asked     does this seat belong to a profile
  //     mattered  is there a face for whoever is in it
  //
  // Portraits belong to profiles here, not to people, so a person's seat
  // has nothing of its own to fetch. Their own profile's is the honest
  // stand-in — with a rule attached, below.
  const [myFace, setMyFace] = useState<Avatar | null>(null);
  const picker = useRef<HTMLInputElement>(null);
  // Which of the device's cameras. "user" is the selfie side; flipping asks
  // for the other and the effect below re-acquires the stream.
  const [facing, setFacing] = useState<"user" | "environment">("user");
  // Whether the controls are shown over a live full-bleed camera. A camera
  // that fills its box leaves nowhere for buttons to live politely, so they
  // hide — and a double-tap or a long press brings them back. Both gestures,
  // because neither is discoverable and two chances beat one.
  const [reveal, setReveal] = useState(false);
  // Three pickers, three different destinations: the room's photo, the
  // person's own picture, and the background behind them.
  const mePicker = useRef<HTMLInputElement | null>(null);
  const bgPicker = useRef<HTMLInputElement | null>(null);
  const hold = useRef<number | null>(null);
  // The local preview. Rendering is the device's, exactly as `overlays` says —
  // what the backend holds is the fact that a camera is on, which is what
  // lets everybody else's client draw the same scene.
  const mine = useRef<HTMLVideoElement>(null);
  const stream = useRef<MediaStream | null>(null);

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Hear the room without pressing anything. A field report on the 🔊
  // press-per-turn: "you should be able to hear the audio anyways without
  // having to press the button". The toggle is still a press — the one
  // gesture the autoplay rules want — and after it, every profile turn
  // that ARRIVES speaks in its bound voice. Turns already on screen stay
  // silent (switching this on is not a request to re-hear the backlog),
  // one turn plays at a time, and the choice is this browser's to keep.
  const [hearAll, setHearAll] = useState(
    () => localStorage.getItem("qrme.room.hear") === "1");
  const heardUpTo = useRef<string | null>(null);
  const speaking = useRef(false);
  // Whose turn is being read aloud RIGHT NOW — an identity (kind + id),
  // for the talking light. Null when no voice is playing.
  const [voicing, setVoicing] = useState<{ kind: string; id: string } | null>(
    null);
  // The ear's live handle and run counter. Switching rooms or leaving
  // the screen bumps the run and stops the playing turn — without this,
  // the queue kept reading the OLD room's turns under the new one (or
  // under no screen at all), because the loop's handle was a local.
  const nowSaying = useRef<{ stop: () => void } | null>(null);
  const earRun = useRef(0);
  // Dictation: speech types into the box and sends nothing — the send
  // stays a decision. Only offered where the browser ships a recogniser
  // (iOS Safari does not), the same bargain the Agent screen struck.
  const [dictating, setDictating] = useState(false);
  const dictation = useRef<{ stop: () => void } | null>(null);
  // Talking INTO a voice room: the same recogniser, but what it hears is
  // said in the room rather than typed into a box. The two cannot run at
  // once — one microphone, one destination.
  const [talking, setTalking] = useState(false);
  const talkRec = useRef<{ stop: () => void } | null>(null);
  // The standing ear's own state. `wantTalking` is the person's decision,
  // held apart from `talking` because the browser's recogniser ends itself
  // on its own schedule — a quiet minute, a tab blur — and a standing ear
  // that died at the platform's convenience would put the press right back
  // where a field report just took it from.
  const wantTalking = useRef(false);
  // What is being heard, before it is sent. It rides in the draft box on
  // purpose: a person talking to a room needs to see that they are being
  // heard, and a microphone with no visible output is one people repeat
  // themselves into.
  const pending = useRef("");
  const silence = useRef<number | null>(null);
  // What the room has recently said out loud, for the echo guard. Kept as
  // turns rather than one string so the window stays honest as it rolls.
  const roomSaid = useRef<string[]>([]);
  // Asking another synthetic profile into the room. The invite is consent-
  // shaped on the wire — host asks, the profile's owner accepts — and for a
  // profile this person owns, the console holds both tokens, so one press
  // does the whole round trip and the guest is simply seated.
  const [guestId, setGuestId] = useState("");
  // Whether the guest-invite form is showing. The strip's person-plus is a
  // shortcut to a form that already exists further down this page rather
  // than a second way to do the same thing — one invite, one door, one
  // place the refusal lands.
  const [asking, setAsking] = useState(false);
  const askCard = useRef<HTMLDivElement>(null);
  // The held overlay — screen 104. Press and hold, or double tap, anywhere
  // in the room and three options come up over it; tap anywhere else and
  // they go away again.
  //
  //     asked     how do you get out of a full-screen room on a phone
  //     mattered  is there anything to press, and can you find it twice
  //
  // Deliberately **phone only**. A computer is landscape already and has a
  // window edge, a tab bar and a back button; putting a held overlay there
  // would be inventing a gesture to solve a problem that screen does not
  // have. The field report said so in one line — "that's for mobile
  // because computer will be landscape anyways".
  const [held, setHeld] = useState(false);
  const holdRoom = useRef<number | null>(null);
  // Sharing into the room: whatever is typed in the box rides along as
  // the caption, so "look at this" and the picture arrive as one turn.
  const sharePick = useRef<HTMLInputElement>(null);

  const open = roomId.trim();
  // Whether a room is open, and therefore whether this screen is a PLACE
  // rather than a page. Declared beside `open` because effects far above
  // the render read it — a `const` read before its line is a dead-zone
  // crash, not a false.
  const inRoom = Boolean(open);

  // A voice room is a voice room. Field report, holding a `voice` room up
  // against what it drew: "this is supposed to be audio chat only — we
  // need to get rid of the type bar and the transparent chat text and go
  // back to hearing the voices." The channel was chosen on the way in and
  // then ignored: every room wore the chat furniture and hearing was an
  // opt-in press, so the one room whose whole pitch is sound arrived
  // silent with a keyboard in front of it.
  //
  //     asked     what kind of room is this
  //     mattered  the room's own answer, or the same furniture everywhere
  const spokenRoom = channel === "voice";

  function load() {
    if (!open || !token) return;
    api.roomMessages(open, token).then(setTranscript).catch(setError);
    api.micsInRoom(open, token).then(setMics).catch(() => setMics(null));
    // The seats. Joining twice is being there once, so the join door
    // doubles as the who-is-here read — and going in renders a scene
    // rather than leaving you on the same form, which a field report
    // described as "it just stayed here in the same menu".
    api.joinRoom(open, token)
      .then((r) => { setSeats(r.participants); setChannel(r.channel); })
      .catch(() => setSeats([]));
    // What is in the seats, and who is wearing what — one call, because a
    // second one would draw a frame with a face and no disclosure on it.
    api.roomFaces(open, token).then(setScene).catch(() => setScene(null));
  }
  useEffect(load, [open, token]);

  // The transcript box follows the newest line, unless you have scrolled
  // up to read — then it stays where you put it, and follows again once
  // you come back to the bottom. Without the second half, reading an
  // older turn is impossible in a room that is still talking: every poll
  // would yank you back down.
  const chatLog = useRef<HTMLDivElement | null>(null);
  const pinned = useRef(true);
  function watchScroll() {
    const box = chatLog.current;
    if (!box) return;
    pinned.current =
      box.scrollHeight - box.scrollTop - box.clientHeight < 24;
  }
  useEffect(() => {
    const box = chatLog.current;
    if (box && pinned.current) box.scrollTop = box.scrollHeight;
  }, [transcript]);

  // The room keeps itself current. Without this, the transcript refreshed
  // only on mount or after the viewer's own action — another person's
  // turn, a profile still writing its reply to somebody else, a shared
  // picture: none of it arrived until you did something. A room you have
  // to poke to hear is not a room. The sender's own turn also lands here
  // while the profiles are still thinking, because the server stores it
  // before it starts generating replies. Quiet on failure on purpose: a
  // poll that can paint an error banner every four seconds is a nag, and
  // the next action's own error handling still says what is wrong.
  useEffect(() => {
    if (!open || !token) return;
    const tick = window.setInterval(() => {
      api.roomMessages(open, token).then(setTranscript)
        .catch(() => { /* the next poll, or the next action, will say */ });
    }, 4000);
    return () => window.clearInterval(tick);
  }, [open, token]);

  useEffect(() => {
    api.overlayCatalogue().then((c) => setMasks(c.kinds)).catch(() => setMasks([]));
  }, []);

  useEffect(() => {
    const mine = session.profileId;
    if (!mine || !token || myFace) return;
    api.avatar(mine, token).then(setMyFace).catch(() => setMyFace(null));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session.profileId, token]);

  useEffect(() => {
    for (const seat of seats) {
      if (seat.kind === "user" || aiFaces[seat.id]) continue;
      api.avatar(seat.id, token)
        .then((a) => setAiFaces((m) => ({ ...m, [seat.id]: a })))
        .catch(() => undefined);
    }
    // aiFaces deliberately not a dep: it is the cache this effect fills.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seats, token]);

  const showing = scene?.faces[me]?.showing || "voice";

  // The camera itself. Held in a ref rather than state because a MediaStream
  // is a live handle, not a value to re-render on — and stopping every track
  // is the only thing that puts the device's own light out.
  useEffect(() => {
    let dropped = false;
    if (showing === "camera") {
      // A flip re-runs this effect, so the old side is stopped before the
      // new one is asked for — two live tracks is two camera lights.
      stream.current?.getTracks().forEach((t) => t.stop());
      stream.current = null;
      navigator.mediaDevices?.getUserMedia(
        // `ideal` rather than `exact`: a laptop has no back camera, and a
        // hard constraint there turns the flip button into an error dialog.
        { video: { facingMode: { ideal: facing } } })
        .then((s) => {
          if (dropped) { s.getTracks().forEach((t) => t.stop()); return; }
          stream.current = s;
          if (mine.current) mine.current.srcObject = s;
        })
        .catch((e) => setError(e));
    }
    if (showing !== "camera") {
      stream.current?.getTracks().forEach((t) => t.stop());
      stream.current = null;
      if (mine.current) mine.current.srcObject = null;
      setReveal(false);
    }
    return () => { dropped = true; };
  }, [showing, facing]);

  // Leaving the screen with a camera still running is how an indicator light
  // stays on in somebody's room after they have gone.
  useEffect(() => () => {
    stream.current?.getTracks().forEach((t) => t.stop());
    stream.current = null;
  }, []);

  // The AR passthrough, alive exactly while the stage is. The refusal path
  // matters as much as the grant: a denied camera downgrades the stage to
  // the flat backdrop and says so, rather than presenting a black room as
  // though that were the feature.
  useEffect(() => {
    if (!(immersed && channel === "ar")) {
      passStream.current?.getTracks().forEach((t) => t.stop());
      passStream.current = null;
      if (pass.current) pass.current.srcObject = null;
      return;
    }
    let gone = false;
    setPassDenied(false);
    navigator.mediaDevices?.getUserMedia(
      { video: { facingMode: { ideal: "environment" } } })
      .then((s) => {
        if (gone) { s.getTracks().forEach((t) => t.stop()); return; }
        passStream.current = s;
        if (pass.current) pass.current.srcObject = s;
      })
      .catch(() => setPassDenied(true));
    return () => {
      gone = true;
      passStream.current?.getTracks().forEach((t) => t.stop());
      passStream.current = null;
    };
  }, [immersed, channel]);

  /** What a seat shows at stage size: the photo somebody chose, a
   *  profile's own portrait with its AI mark, or the initials — the same
   *  resolution order the flat tiles use, because the stage is a way of
   *  standing in the room, not a different room. */
  const stageFace = (s: { kind: string; id: string; display: string }) => {
    const face = scene?.faces[s.id];
    if (face?.showing === "photo" && face.media_url) {
      return <img className="rs-photo" src={face.media_url} alt={s.display} />;
    }
    // My own seat, wearing my own profile's picture.
    //
    // Only a real photograph, and the two flags decide it rather than a
    // guess: `likeness.real_person` says the portrait is of an actual
    // person and `asset_marked` says whether it carries the AI mark. A
    // generated portrait stays off a human seat — a synthetic image
    // passing unmarked as somebody's face is the one thing this codebase
    // refuses to build, and the mark belongs to the profile seat where it
    // is already drawn.
    if (s.kind === "user" && s.id === me && myFace?.asset
        && !myFace.asset_marked
        && myFace.likeness?.real_person) {
      return <img className="rs-photo" alt={s.display}
                  src={(myFace.asset as string).startsWith("http")
                         ? (myFace.asset as string)
                         : getBase() + myFace.asset} />;
    }
    if (s.kind !== "user" && aiFaces[s.id]?.asset
        && !aiFaces[s.id]?.placeholder) {
      return <img className="rs-photo" alt={s.display}
                  src={(aiFaces[s.id].asset as string).startsWith("http")
                         ? (aiFaces[s.id].asset as string)
                         : getBase() + aiFaces[s.id].asset} />;
    }
    if (face?.showing === "camera") {
      return <span className="rs-face rs-oncam"
                   title={tr("ins.face.theirs", lang)}>
        {tr("ins.face.camicon", lang)}
      </span>;
    }
    return <span className="rs-face">
      {(s.display || "?").split(/\s+/).map((w) => w[0]).join("").slice(0, 2)}
    </span>;
  };

  // Whose square is lit: the voice actually being HEARD first, the last
  // voice in the transcript otherwise — matched by WHO, never by name. It
  // used to compare display names, and a field report caught the failure
  // that invites: a person in a room with their own synthetic twin shares
  // a name with it, so the profile's square lit while the person spoke.
  // sender_kind + sender_id is an identity; "David Bianchi" is two
  // participants. And when the room's ear reads a backlog of turns aloud
  // one by one, the transcript's last line is not who is speaking — the
  // light follows the voice, or three queued turns all light the wrong
  // square until the reading catches up.
  const lastSaid = transcript.length > 0
    ? transcript[transcript.length - 1] : null;
  const isTalking = (s: { kind: string; id: string }) =>
    voicing !== null
      ? (voicing.kind === "user") === (s.kind === "user")
        && voicing.id === s.id
      : lastSaid !== null
        && (lastSaid.sender_kind === "user") === (s.kind === "user")
        && lastSaid.sender_id === s.id;

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { setError(e); } finally { setBusy(false); }
  };

  function flipHearAll() {
    const v = !hearAll;
    setHearAll(v);
    if (v) {
      localStorage.setItem("qrme.room.hear", "1");
      // Everything already said stays said: the toggle speaks what comes
      // next, not the scrollback.
      heardUpTo.current = transcript.length > 0
        ? transcript[transcript.length - 1].id : null;
    } else {
      localStorage.removeItem("qrme.room.hear");
    }
  }

  // Speak the profile turns that arrived since the last look, one at a
  // time. `speaking` is the queue's lock: a reload mid-playback must not
  // start a second voice over the first.
  useEffect(() => {
    if (!hearAll || speaking.current || transcript.length === 0) return;
    const start = heardUpTo.current === null ? 0
      : transcript.findIndex((m) => m.id === heardUpTo.current) + 1;
    const fresh = transcript.slice(Math.max(start, 0))
      .filter((m) => m.sender_kind === "profile" && m.sender_id && m.content);
    heardUpTo.current = transcript[transcript.length - 1].id;
    if (fresh.length === 0) return;
    speaking.current = true;
    const run = earRun.current;
    void (async () => {
      try {
        for (const m of fresh) {
          if (run !== earRun.current) break;
          // Piece by piece: a long turn starts being heard at its first
          // sentence. A rejected play (autoplay withheld after all) ends
          // quietly — the per-turn 🔊 is still on every line.
          const s = await speakInPieces(
            m.sender_id as string, m.content || "", token);
          // Remembered before it plays, not after: the microphone is open
          // the whole time this voice is in the air, so the words have to
          // be in the window before they can come back through it.
          roomSaid.current = [...roomSaid.current, m.content || ""]
            .slice(-RECENT_TURNS);
          nowSaying.current = s;
          if (run !== earRun.current) { s.stop(); break; }
          // The light follows the voice: while a backlog is being read,
          // the transcript's last line is not who is speaking.
          setVoicing({ kind: "profile", id: m.sender_id as string });
          await s.done;
        }
      } catch { /* a voice that cannot be fetched leaves the text standing */ }
      nowSaying.current = null;
      setVoicing(null);
      speaking.current = false;
    })();
    // heardUpTo/speaking are refs on purpose: the transcript is the signal.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [transcript, hearAll, token]);

  // Switching rooms — or leaving the screen, which runs the same cleanup
  // — silences the old room's queue and its dictation. Without this, the
  // ear kept reading the previous room's turns into the new one, and
  // navigating away left the voice talking with no screen behind it.
  useEffect(() => () => {
    earRun.current++;
    nowSaying.current?.stop();
    nowSaying.current = null;
    dictation.current?.stop();
    dictation.current = null;
    // `wantTalking` first: `onend` restarts the ear while it is true, so
    // stopping the recogniser without clearing the decision would spawn a
    // fresh one into a room nobody is standing in any more.
    wantTalking.current = false;
    if (silence.current !== null) {
      window.clearTimeout(silence.current);
      silence.current = null;
    }
    pending.current = "";
    roomSaid.current = [];
    talkRec.current?.stop();
    talkRec.current = null;
  }, [open]);

  // A voice room arrives speaking. Going in is itself the press the
  // autoplay rules want — the same gesture the 🔊 toggle was standing in
  // for — so nothing else has to be tapped before the room is audible.
  // The toggle stays, now as the way to SILENCE a voice room rather than
  // the way to start it, and a chat room's remembered choice is untouched.
  useEffect(() => {
    if (spokenRoom) setHearAll(true);
  }, [spokenRoom, open]);

  // ...and arrives listening. The other half of the same field report:
  // "everything seems to be working fine as long as users are in the
  // room. They shouldn't have to press the microphone button."
  //
  //     asked     can you talk in this room
  //     mattered  do you have to ask permission to start
  //
  // Being in a voice room IS the intent to speak in it — the press was
  // the room asking a question it had already been answered. So the ear
  // opens on the way in, and the control below becomes the MUTE.
  //
  // Only in a spoken room: a chat room's microphone stays a decision,
  // because there the medium is typing and an ear opening itself would
  // be the product taking a liberty nobody asked for.
  useEffect(() => {
    if (!spokenRoom || !canDictate) return;
    startTalking();
    // `open` in the deps so moving between voice rooms re-opens the ear
    // in the new one; the teardown above has already closed the old.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [spokenRoom, open, canDictate]);

  // The strip's person-plus. Outside a room the invite form is a card on
  // the page and scrolling to it is right; inside one the page is a place
  // and the card is below the fold, so scrolling to it looked exactly like
  // a button that does nothing.
  //
  //     asked     did the button fire
  //     mattered  did anything happen where the person was looking
  //
  // Field report on the deployed room: "the add friend or synthetic
  // profile button is not working". It was working. It scrolled a
  // full-screen room to a form nobody could see move.
  useEffect(() => {
    if (!asking || inRoom) return;
    askCard.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    const t = window.setTimeout(() => setAsking(false), 1600);
    return () => window.clearTimeout(t);
  }, [asking, inRoom]);

  // What the room has to say, said IN the room. `note` renders as a card
  // near the top of the page, which in a full-screen room is somewhere
  // nobody is looking — the same reason the share arrow read as broken:
  // it copied the room and announced it off-screen.
  useEffect(() => {
    if (!note || !inRoom) return;
    const t = window.setTimeout(() => setNote(null), 3200);
    return () => window.clearTimeout(t);
  }, [note, inRoom]);

  /** Turn the room sideways.
   *
   *  Orientation can only be locked from fullscreen — that is the
   *  platform's rule, not a preference — so the press does both. This is
   *  the one place in this screen that asks for fullscreen, and it is a
   *  press that says the word: a person tapping "Landscape" has asked for
   *  exactly this.
   *
   *  It fails on iOS, which does not implement the lock at all. Said out
   *  loud rather than swallowed: a button that does nothing and reports
   *  nothing is the thing people press four times before giving up.
   */
  async function goSideways() {
    const el = document.documentElement as HTMLElement & {
      webkitRequestFullscreen?: () => Promise<void>;
    };
    const orient = screen.orientation as ScreenOrientation & {
      lock?: (o: string) => Promise<void>;
    };
    try {
      if (!document.fullscreenElement) {
        await (el.requestFullscreen?.() ?? el.webkitRequestFullscreen?.());
      }
      if (!orient?.lock) throw new Error("no lock");
      await orient.lock("landscape");
    } catch {
      setNote(tr("ins.held.turnfail", lang));
    }
  }

  /** Send what has been heard, and clear the box.
   *
   *  The echo guard stands here rather than at `onresult`: a person's
   *  sentence and the room's own voice can land in the same pending
   *  buffer, and the thing worth checking is what is about to be SAID in
   *  the room, not each fragment on its way in. */
  function sendPending() {
    const said = pending.current.trim();
    pending.current = "";
    setDraft("");
    if (!said || !token) return;
    if (isEcho(said, roomSaid.current.join(" "))) {
      // The room hearing itself. Dropped silently and the ear stays
      // open — announcing it would be the product apologising for a
      // microphone the person never pressed.
      return;
    }
    // `act` is deliberately not used: it flips `busy`, which would grey
    // out the room under somebody mid-conversation.
    api.sayInRoom(open, me, said, token).then(load).catch(setError);
  }

  /** Start the standing ear.
   *
   *  Separate from the toggle so entering a voice room can open it
   *  without pretending somebody pressed something.
   */
  function startTalking() {
    const w = window as unknown as {
      SpeechRecognition?: new () => SpeechRec;
      webkitSpeechRecognition?: new () => SpeechRec;
    };
    const SR = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!SR || talkRec.current) return;
    // One microphone: dictation and the standing ear cannot both hold it.
    dictation.current?.stop();
    dictation.current = null;
    setDictating(false);
    wantTalking.current = true;
    const rec = new SR();
    rec.lang = navigator.language || "en";
    rec.interimResults = false;
    rec.continuous = true;
    let seen = 0;
    rec.onresult = (e) => {
      const parts: string[] = [];
      for (let i = seen; i < e.results.length; i++) {
        parts.push(e.results[i][0].transcript);
      }
      seen = e.results.length;
      const heard = parts.join(" ").trim();
      if (!heard) return;
      pending.current = (pending.current ? pending.current + " " : "") + heard;
      // Shown as it is heard. The box is the feedback that the room is
      // listening; without it an open microphone is indistinguishable
      // from a broken one.
      setDraft(pending.current);
      if (silence.current !== null) window.clearTimeout(silence.current);
      silence.current = window.setTimeout(sendPending, SILENCE_SENDS_MS);
    };
    // The browser ends recognition on its own — a quiet stretch, a
    // backgrounded tab. A standing ear restarts, because the person's
    // decision has not changed; only the platform's patience has.
    rec.onend = () => {
      talkRec.current = null;
      if (wantTalking.current) { startTalking(); return; }
      setTalking(false);
    };
    rec.start();
    talkRec.current = { stop: () => rec.stop() };
    setTalking(true);
  }

  function stopTalking() {
    wantTalking.current = false;
    if (silence.current !== null) {
      window.clearTimeout(silence.current);
      silence.current = null;
    }
    // Anything already heard is sent rather than binned: a person who
    // finished a sentence and reached for the button meant to say it.
    sendPending();
    talkRec.current?.stop();
    talkRec.current = null;
    setTalking(false);
  }

  /** The control is now a mute, not a trigger. */
  function flipTalking() {
    if (talking) stopTalking(); else startTalking();
  }

  function flipDictation() {
    if (dictating) {
      dictation.current?.stop();
      dictation.current = null;
      setDictating(false);
      return;
    }
    const w = window as unknown as {
      SpeechRecognition?: new () => SpeechRec;
      webkitSpeechRecognition?: new () => SpeechRec;
    };
    const SR = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!SR) return;
    const rec = new SR();
    rec.lang = navigator.language || "en";
    rec.interimResults = false;
    rec.continuous = true;
    let seen = 0;
    rec.onresult = (e) => {
      const parts: string[] = [];
      for (let i = seen; i < e.results.length; i++) {
        parts.push(e.results[i][0].transcript);
      }
      seen = e.results.length;
      const text = parts.join(" ").trim();
      if (text) setDraft((d) => (d ? d + " " : "") + text);
    };
    rec.onend = () => { dictation.current = null; setDictating(false); };
    rec.start();
    dictation.current = { stop: () => rec.stop() };
    setDictating(true);
  }

  async function sendDraft() {
    if (!draft.trim() || !token || busy) return;
    const text = draft;
    setDraft("");
    await act(async () => { await api.sayInRoom(open, me, text, token); })();
  }

  async function shareFile(file: File) {
    if (!token) return;
    const caption = draft.trim() || undefined;
    setDraft("");
    await act(async () => {
      await api.shareInRoom(open, me, file, token, caption);
    })();
  }

  /** A person's own picture, absolute — theirs, and the same in every room
   *  they walk into. Sparse by design: a person who has not put one up has
   *  no entry, and the seat falls through to their initials. */
  function ownPic(interactorId: string): string | null {
    const url = scene?.pictures?.[interactorId];
    if (!url) return null;
    return url.startsWith("http") ? url : getBase() + url;
  }

  /** What a shared attachment looks like in the transcript: the picture
   *  itself, the video playable, anything else a plain link that says its
   *  name — never an iframe, never markup from the file. */
  function attachment(m: RoomMsg) {
    if (!m.media) return null;
    const src = getBase() + m.media.url;
    if (m.media.kind === "image") {
      return <img className="rm-media" src={src}
                  alt={m.media.name || tr("ins.share", lang)} />;
    }
    if (m.media.kind === "video") {
      return <video className="rm-media" src={src} controls playsInline />;
    }
    // A document says whether the room could read it.
    //
    //     asked     did the file arrive
    //     mattered  can the profiles in here discuss it
    //
    // Field report, in the profile's own words: "I can see them land, but
    // I can't read them from where I'm standing". It was right, and the
    // person sharing had no way to know that before they asked. So the
    // answer is on the attachment itself, before the question is put.
    return (
      <span className="rm-fileline">
        <a className="rm-file" href={src} target="_blank" rel="noreferrer">
          📎 {m.media.name || m.media.url.split("/").pop()}
        </a>
        <span className={"rm-read" + (m.media.read ? " yes" : "")}>
          {m.media.read ? tr("ins.file.read", lang)
                        : tr("ins.file.unread", lang)}
        </span>
      </span>
    );
  }

  // The transparent chat, exactly as the gallery drew it (screens 96–98,
  // 105): the last few turns as translucent lines riding the scene, and
  // the Type… pill under them — so the conversation with the profiles and
  // the people here runs ON the room, not in a card below it. The full
  // transcript, the hear-the-room toggle and the per-turn voices keep
  // their card; this is the same conversation worn differently.
  const chatStrip = (
    <div className="rs-chatstrip">
      {/* Four rows of back-and-forth, and the rest above them.
       *
       *     asked     what happens to a line once it is not the newest
       *     mattered  is it gone, or is it above you
       *
       * It used to be gone: the strip drew `transcript.slice(-3)`, so the
       * fourth-newest turn left the DOM, and a line longer than the strip
       * was cut off mid-sentence by an ellipsis with nowhere to go. Field
       * report: "when it goes past the first line as it's talking it just
       * doesn't keep scrolling... I want at least three or four rows of
       * back-and-forth text but I want them to start vanishing on the
       * fifth, users can scroll up and down if they want to see it".
       *
       * So the last thirty turns are all here, in a box four rows tall
       * that scrolls. Vanishing above the fold and vanishing out of the
       * record are different things, and only the first one was wanted.
       * A long line wraps now instead of being clipped. */}
      <div className="rs-chatlog" ref={chatLog} onScroll={watchScroll}>
        {transcript.slice(-30).map((m) => (
          <p key={m.id} className="rs-chatline">
            <strong>{m.from}</strong> {m.content}
            {/* The real attachment, not a filename in an emoji. The strip
                printed `📎 name` as text, so in a full-screen room a
                shared picture was a word and a shared document was a word
                you could not open. Same renderer as the card below. */}
            {attachment(m)}
          </p>
        ))}
      </div>
      <div className="rs-chatpill">
        <button className="rs-chatbtn" disabled={busy || !token}
                aria-label={tr("ins.share", lang)}
                title={tr("ins.share", lang)}
                onClick={() => sharePick.current?.click()}>📎</button>
        {canDictate && (
          <button className="rs-chatbtn" disabled={busy}
                  aria-pressed={dictating}
                  aria-label={tr("ins.dictate", lang)}
                  onClick={flipDictation}>🎤</button>
        )}
        <input value={draft} placeholder={tr("ins.type.ph", lang)}
               onChange={(e) => setDraft(e.target.value)}
               onKeyDown={(e) => { if (e.key === "Enter") void sendDraft(); }} />
        <button className="rs-chatbtn" disabled={busy || !token || !draft.trim()}
                aria-label={tr("ins.sayit", lang)}
                onClick={() => void sendDraft()}>➤</button>
      </div>
      {/* The round controls screen 103 draws along the bottom.
       *
       *      asked     which buttons does the drawing have
       *      mattered  which of them can actually do anything
       *
       *  Five, and every one of them now has a door. The drawing's fifth
       *  was a heart, and the field report threw it out on the way past:
       *  "who all is gonna like the chat, just the people in the chat" —
       *  which is exactly right. A like is for an audience that is not in
       *  the room, and everybody here is. The slot became the files
       *  button, which is a thing people in a room actually do.
       *
       *  So: a link, a file, the microphone, an invitation, and the way to
       *  hand somebody the room. Nothing here lights up without changing
       *  something somebody else can see. */}
      <div className="rs-strip">
        <button className="rs-round link" disabled={busy || !token}
                aria-label={tr("ins.link", lang)}
                title={tr("ins.link", lang)}
                onClick={() => {
                  const url = window.prompt(tr("ins.link.ask", lang)) || "";
                  const clean = url.trim();
                  if (clean) setDraft((d) => (d ? d + " " : "") + clean);
                }}>🔗</button>
        <button className="rs-round files" disabled={busy || !token}
                aria-label={tr("ins.files", lang)}
                title={tr("ins.files", lang)}
                onClick={() => sharePick.current?.click()}>📎</button>
        {/* The microphone, in every room.
         *
         * It was offered only in voice rooms, on the reasoning that a chat
         * room's medium is typing and an ear opening itself there would be
         * a liberty nobody asked for. The first half of that still holds —
         * nothing opens on its own here — but the second half was wrong:
         * a person PRESSING a microphone has asked for it, in any room.
         *
         *     asked     should a chat room start listening by itself
         *     mattered  may somebody in one choose to talk
         *
         * Field report, from a chat room: "it should stay illuminated if
         * it stays on when you just click that and it's illuminated you
         * should be able to just speak". So: press to open, it stays lit
         * while it listens, and five seconds of silence sends. */}
        {canDictate && (
          <button className={"rs-round mic" + (talking ? " live" : "")}
                  aria-pressed={talking}
                  aria-label={talking ? tr("ins.mute", lang)
                                      : tr("ins.unmute", lang)}
                  title={talking ? tr("ins.mute", lang)
                                 : tr("ins.unmute", lang)}
                  onClick={flipTalking}>{talking ? "🎙" : "🔇"}</button>
        )}
        <button className="rs-round invite" disabled={busy || !token}
                aria-label={tr("ins.ask.title", lang)}
                title={tr("ins.ask.title", lang)}
                onClick={() => setAsking(true)}>👤+</button>
        <button className="rs-round share" disabled={!open}
                aria-label={tr("ins.handover", lang)}
                title={tr("ins.handover", lang)}
                onClick={() => {
                  // The room itself, handed to somebody who is not in it.
                  // The id is what the join screen takes, so the id is what
                  // goes on the clipboard — a URL would be this console's
                  // address, which is not necessarily theirs.
                  void navigator.clipboard?.writeText(open)
                    .then(() => setNote(tr("ins.handover.done", lang)))
                    .catch(() => setNote(open));
                }}>↗</button>
      </div>
    </div>
  );

  // What a voice room wears instead: no lines of text riding the scene,
  // no Type… pill — one control that listens, and a line saying whether
  // anybody is speaking. The transcript still exists (a room keeps its
  // record, and a person who cannot hear needs to read it); it lives in
  // the card below, where the reading is deliberate rather than pasted
  // over a room somebody came here to listen to.
  const voiceBar = (
    <div className="rs-voicebar">
      <div className="rs-voicenow">
        {voicing
          ? fill(tr("ins.voice.speaking", lang),
                 { who: seats.find((s) => isTalking(s))?.display
                        || tr("ins.voice.someone", lang) })
          : talking ? tr("ins.voice.hearing", lang)
                    : tr("ins.voice.quiet", lang)}
      </div>
      {canDictate ? (
        <button className={"rs-talk" + (talking ? " live" : "")}
                aria-pressed={talking}
                aria-label={talking ? tr("ins.voice.stop", lang)
                                    : tr("ins.voice.talk", lang)}
                onClick={flipTalking}>
          🎙 {talking ? tr("ins.voice.stop", lang)
                      : tr("ins.voice.talk", lang)}
        </button>
      ) : (
        // No recogniser here (iOS Safari ships none). A voice room with no
        // way in is a locked door: the typed pill comes back, and the line
        // says why it is the one being offered.
        <>
          <p className="rs-voicenote">{tr("ins.voice.notalk", lang)}</p>
          <div className="rs-chatpill">
            <input value={draft} placeholder={tr("ins.type.ph", lang)}
                   onChange={(e) => setDraft(e.target.value)}
                   onKeyDown={(e) => {
                     if (e.key === "Enter") void sendDraft();
                   }} />
            <button className="rs-chatbtn"
                    disabled={busy || !token || !draft.trim()}
                    aria-label={tr("ins.sayit", lang)}
                    onClick={() => void sendDraft()}>➤</button>
          </div>
        </>
      )}
    </div>
  );

  async function askIn() {
    const guest = guestId.trim();
    if (!guest || !token) return;
    setError(null); setNote(null); setBusy(true);
    try {
      await api.inviteToRoom(open, guest, token);
      // The invite stands either way. The acceptance is the guest's own
      // owner token saying yes — held here exactly when the guest is this
      // person's profile. Anybody else's profile keeps its owner's choice:
      // the refusal below downgrades the note, never the invite.
      if (session.ownerToken) {
        try {
          await api.acceptRoomInvite(open, guest, session.ownerToken);
          setNote(tr("ins.ask.seated", lang));
          setGuestId("");
          load();
          return;
        } catch { /* not this person's profile — the invite is the news */ }
      }
      setNote(tr("ins.ask.sent", lang));
      setGuestId("");
    } catch (e) { setError(e); } finally { setBusy(false); }
  }

  const lentByMe = mics?.microphones_lent.some((m) => m.interactor_id === me);

  // A room is a place, not a page.
  //
  // Field report, twice, the second time with the gallery's own screen 105
  // held up beside a screenshot: "when you enter a room, you should leave
  // the homepage and enter a full-blown screen like this second photo not
  // like the first one" — and later, "the chat becomes the full screen
  // instead of in a little blue box".
  //
  //     asked     is the room on screen
  //     mattered  is the room the screen
  //
  // Both were true of the console and neither was the point. `.screen` is
  // capped at 720px and sits in a padded column beside the sidebar, which
  // is right for every settings page in this product and wrong for the one
  // surface that is somewhere you ARE. Once you are in a room, the room is
  // the whole window: the faces fill it, the sidebar steps out of the way,
  // and the composer is the slim strip along the bottom that screen 105
  // draws rather than the middle of the page.
  //
  // The title and the pitch go with it. They are shelf copy — what this
  // screen is for, read by somebody deciding whether to open it — and a
  // person already standing in the room has decided.
  return (
    <div className={"screen" + (inRoom ? " room-place" : "")}>
      {inRoom && onAPhone && (
        // The gestures. Both, because neither is discoverable and two
        // chances beat one — the same reasoning the camera controls on
        // this screen already use, and the same pair screen 104 names.
        <div className="room-gestures"
             onDoubleClick={() => setHeld(true)}
             onTouchStart={() => {
               holdRoom.current = window.setTimeout(() => setHeld(true), 550);
             }}
             onTouchEnd={() => {
               if (holdRoom.current !== null) {
                 window.clearTimeout(holdRoom.current);
                 holdRoom.current = null;
               }
             }}
             onTouchMove={() => {
               // A drag is a scroll, not a press. Without this, reading the
               // transcript brings the overlay up under your thumb.
               if (holdRoom.current !== null) {
                 window.clearTimeout(holdRoom.current);
                 holdRoom.current = null;
               }
             }} />
      )}
      {inRoom && note && (
        // Said in the room, because the room is where the person is. The
        // page's own note card is still there for the roomless case; this
        // is the same sentence delivered somewhere it can be read.
        <p className="room-said" role="status">{note}</p>
      )}
      {inRoom && asking && (
        // The invitation, in the room. Outside one it is a card on the
        // page and scrolling to it is right; here the page IS the room, so
        // the form comes to the person rather than the person going to the
        // form. Same door, same refusal, same single place a failure lands
        // — only the furniture moved.
        <div className="room-scrim" onClick={() => setAsking(false)}>
          <div className="rh-panel" onClick={(e) => e.stopPropagation()}>
            <p className="rh-title">{tr("ins.ask.title", lang)}</p>
            <p className="rh-note">{tr("ins.ask.pitch", lang)}</p>
            <input value={guestId} autoFocus
                   placeholder={tr("ins.ask.ph", lang)}
                   onChange={(e) => setGuestId(e.target.value)}
                   style={{ width: "100%" }} />
            <button className="primary"
                    disabled={busy || !token || !guestId.trim()}
                    onClick={() => { setAsking(false); void askIn(); }}>
              {tr("ins.ask.send", lang)}
            </button>
          </div>
        </div>
      )}
      {held && (
        // Tap anywhere else to go back — the scrim IS the way out, which is
        // why it is the element that carries the handler rather than a
        // fourth button that would need explaining.
        <div className="room-held" onClick={() => setHeld(false)}>
          <p className="rh-title">{tr("ins.held.title", lang)}</p>
          <div className="rh-row" onClick={(e) => e.stopPropagation()}>
            <button className="rh-opt help"
                    onClick={() => { setHeld(false); setNote(tr("ins.held.helptext", lang)); }}>
              <span className="rh-glyph">?</span>
              {tr("ins.held.help", lang)}
            </button>
            <button className="rh-opt turn"
                    onClick={() => { setHeld(false); void goSideways(); }}>
              <span className="rh-glyph">⟳</span>
              {tr("ins.held.landscape", lang)}
            </button>
            <button className="rh-opt back"
                    onClick={() => { setHeld(false); onLeave?.(); }}>
              <span className="rh-glyph">↩</span>
              {tr("ins.held.back", lang)}
            </button>
          </div>
          <p className="rh-note">{tr("ins.held.tapaway", lang)}</p>
        </div>
      )}
      {inRoom && onLeave && (
        // The way out. The sidebar is hidden while a room owns the window,
        // so this is the only door — which is why it is drawn before
        // anything else in the frame rather than tucked under the fold
        // with the room's other controls.
        <button className="room-out" onClick={onLeave}>
          {tr("ins.leave", lang)}
        </button>
      )}
      {!inRoom && <h2>{tr("ins.title", lang)}</h2>}
      {!inRoom && <p className="muted small">{tr("ins.pitch", lang)}</p>}

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("ins.whichroom", lang)}</h3>
        <div className="row">
          <input value={roomId} onChange={(e) => setRoomId(e.target.value)}
                 placeholder={tr("ins.roomid.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !open || !token} onClick={act(async () => {
            load();
          })}>
            {tr("ins.goin", lang)}
          </button>
        </div>
        {!token && (
          <p className="muted small">{tr("ins.signinperson", lang)}</p>
        )}
      </div>

      {open && seats.length > 0 && (
        // The scene: everyone in the room in their own square, and the
        // square of whoever spoke last wears the light. The transcript
        // stays below — the scene is where you are, the transcript is
        // what was said.
        <div className={"card" + (inRoom ? " room-stage" : "")}>
          {/* In a room the faces ARE the screen, so the heading goes: it
              labels a section on a page, and there is no page left to be a
              section of. Outside a room — the same component, no room open
              — it still says what it is. */}
          {!inRoom && <h3>{tr("ins.scene", lang)}</h3>}
          <div className="room-scene">
            {seats.map((s) => {
              const face = scene?.faces[s.id];
              const isMe = s.kind === "user" && s.id === me;
              // What is BEHIND this person, which is a different object
              // from what stands in FOR them: `photo` replaces the person,
              // a background sits under whatever the seat is showing and
              // leaves them on top of it.
              const behind = face?.background_url
                ? (face.background_url.startsWith("http")
                     ? face.background_url : getBase() + face.background_url)
                : null;
              const wearing = scene?.wearing.find(
                (w) => w.interactor_id === s.id);
              const camLive = isMe && face?.showing === "camera";
              // A put-up picture behaves like the camera: full-bleed in
              // the tile, controls hidden behind the same double-tap or
              // hold. A field report put a photo up and met a small circle
              // with the buttons still showing — the picture is the face
              // now, and the face fills the frame the way the camera does.
              const picShown = face?.showing === "photo" && !!face.media_url;
              const picLive = isMe && picShown;
              const faceLive = camLive || picLive;
              return (
              <div key={s.id}
                   className={"rs-tile" + (isTalking(s) ? " talking" : "")
                              + (camLive || picShown ? " rs-camtile" : "")}
                   /* The gesture that opens your own seat's options, and it
                    * has to work on an EMPTY seat.
                    *
                    *     asked     can you get at your seat's controls
                    *     mattered  can you get at them when there is nothing
                    *               in the seat yet
                    *
                    * It was gated on `faceLive` — a camera or a picture
                    * ALREADY showing — so the one state where you need the
                    * options was the one state where the handler was
                    * `undefined` and the tap did nothing. Field report:
                    * "it's not letting me double tap to open up the windows
                    * to add a photo as my background or turn on my camera."
                    *
                    * Own seat, always. Somebody else's seat has no controls
                    * of yours on it, and never did. */
                   onDoubleClick={isMe
                     ? () => setReveal((v) => !v) : undefined}
                   onPointerDown={isMe ? () => {
                     hold.current = window.setTimeout(
                       () => setReveal((v) => !v), 550);
                   } : undefined}
                   onPointerUp={isMe ? () => {
                     if (hold.current) window.clearTimeout(hold.current);
                     hold.current = null;
                   } : undefined}
                   onPointerLeave={isMe ? () => {
                     if (hold.current) window.clearTimeout(hold.current);
                     hold.current = null;
                   } : undefined}>
                {/* What is behind the person, drawn first so everything
                    else sits on top of it. Never on a seat showing a live
                    camera: cutting somebody out of their own video frame
                    needs real segmentation, and a background pasted behind
                    an uncut frame is just a picture nobody can see. */}
                {behind && face?.showing !== "camera" && (
                  <img className="rs-behind" src={behind} alt=""
                       aria-hidden="true" />
                )}
                {/* What is in the box. A camera, a picture, or the initials —
                    and the box is the same size in all three, because the
                    quiet person is as present as the talking one. */}
                {s.kind === "user" && !face?.showing && ownPic(s.id) ? (
                  // The person's OWN picture — theirs, not a profile's.
                  //
                  //     asked     can a person show a face
                  //     mattered  whose face is it
                  //
                  // This used to borrow the portrait of the profile bound
                  // to the session, gated on `likeness.real_person`, which
                  // is false for any profile whose kind is "fictional" —
                  // and kind DEFAULTS to fictional. So the gate refused,
                  // the seat drew initials, and the borrowed picture
                  // appeared on the synthetic seat beside it instead:
                  // "one says You with a Y on it, it should be my image".
                  //
                  // A person's face belongs to the person. It comes from
                  // the room's own `pictures` map, so it is drawn for
                  // EVERY human seat rather than only for your own, and it
                  // fills the frame the way the camera and the put-up
                  // photo do — "the pictures they upload will fill the
                  // whole frame".
                  <img className="rs-photo rs-fullbleed" alt={s.display}
                       src={ownPic(s.id) as string} />
                ) : isMe && face?.showing === "camera" ? (
                  <>
                    <video ref={mine}
                           className={"rs-live rs-fullbleed"
                             + (wearing
                                ? MASK_TREATMENTS[wearing.kind] || "" : "")}
                           autoPlay playsInline muted
                           aria-label={tr("ins.face.yourcamera", lang)} />
                    {wearing && MASK_GLYPHS[wearing.kind] && (
                      <span className="rs-mask" aria-hidden="true">
                        {MASK_GLYPHS[wearing.kind]}
                      </span>
                    )}
                    {!reveal && (
                      <span className="rs-hint">
                        {tr("ins.face.hint", lang)}
                      </span>
                    )}
                  </>
                ) : face?.showing === "camera" ? (
                  // Somebody else's camera. The fact is shared; the pixels
                  // are not — this product carries no stream between clients,
                  // and drawing a fake frame here would be the one lie the
                  // whole scene is built to avoid.
                  <span className="rs-face rs-oncam"
                        title={tr("ins.face.theirs", lang)}>
                    {tr("ins.face.camicon", lang)}
                  </span>
                ) : face?.showing === "photo" && face.media_url ? (
                  // Full-bleed like the camera, for every seat: a face is a
                  // face whether pixels stream or stand still. On your own
                  // tile the controls hide behind the same double-tap the
                  // camera taught, and the hint says so.
                  <>
                    <img className="rs-photo rs-fullbleed"
                         src={face.media_url} alt={s.display} />
                    {picLive && !reveal && (
                      <span className="rs-hint">
                        {tr("ins.face.hint", lang)}
                      </span>
                    )}
                  </>
                ) : s.kind !== "user" && aiFaces[s.id]?.asset
                    && !aiFaces[s.id]?.placeholder ? (
                  // The profile's own portrait, in the same circle a person's
                  // photo uses. The AI mark on this tile is the disclosure the
                  // avatar route insists travels with the picture.
                  <img className="rs-photo" alt={s.display}
                       src={(aiFaces[s.id].asset as string).startsWith("http")
                              ? (aiFaces[s.id].asset as string)
                              : getBase() + aiFaces[s.id].asset} />
                ) : (
                  <span className="rs-face">
                    {(s.display || "?").split(/\s+/)
                      .map((w) => w[0]).join("").slice(0, 2)}
                  </span>
                )}
                <span className="rs-name">{s.display}</span>
                {/* The mark, top left, on the synthetic seats and no others —
                    the way the screen this is drawn from does it, and the way
                    the rest of the platform does it.

                    It replaces a caption underneath that read `person` against
                    a field the backend spells `user`, so the ternary never
                    matched and every human in the room was labelled a profile
                    — on the one screen where telling the two apart is the
                    entire point. The word is kept as the title so it is still
                    readable, and so the person's own word is still spoken to
                    a screen reader. */}
                {s.kind === "user" ? (
                  <span className="sr-only">{tr("ins.seat.person", lang)}</span>
                ) : (
                  <span className="rs-ai" title={tr("ins.seat.profile", lang)}>
                    {tr("ins.seat.aimark", lang)}
                  </span>
                )}
                {/* The two corner marks screen 103 draws, and only where
                    this deployment actually knows the fact.

                        asked     whose camera and microphone are on
                        mattered  which of those does anybody here know

                    **Camera, top left, for everybody.** `showing` is a real
                    per-seat field — voice, photo or camera — so a seat with
                    a live camera can be marked truthfully on anyone's tile.

                    **Microphone, top right, on your own seat only.** There
                    is no per-seat mute in this product: `microphones_lent`
                    is a *borrowed wearable*, which is a different fact and
                    not its opposite. Drawing a red slash on somebody else's
                    tile would be a badge for something nobody tracks — the
                    same defect as a roster row printing a permission as a
                    sensor. Your own is real, because the standing ear on
                    this screen is the thing being reported. Until the
                    server learns the rest, the other tiles stay honest by
                    staying blank. */}
                {face?.showing === "camera" && (
                  <span className="rs-mark rs-oncamera"
                        title={tr("ins.mark.camera", lang)}>
                    <span className="sr-only">
                      {tr("ins.mark.camera", lang)}
                    </span>
                  </span>
                )}
                {isMe && !talking && (
                  <span className="rs-mark rs-micoff"
                        title={tr("ins.mark.micoff", lang)}>
                    <span className="sr-only">
                      {tr("ins.mark.micoff", lang)}
                    </span>
                  </span>
                )}
                {/* The mask disclosure, on the face it is about. It rides with
                    the scene rather than sitting in a settings screen nobody
                    opens — the sentence is addressed to the other people. */}
                {wearing && (
                  <span className="muted small rs-worn">
                    {wearing.disclosure}
                  </span>
                )}
                {isMe && (!faceLive || reveal) && (
                  <div className="rs-controls">
                    <button className="chip" disabled={busy}
                            aria-pressed={face?.showing === "camera"}
                            onClick={act(async () => {
                              await api.setRoomFace(
                                open, me,
                                face?.showing === "camera" ? "voice" : "camera",
                                token);
                            })}>
                      {face?.showing === "camera"
                        ? tr("ins.face.cameraoff", lang)
                        : tr("ins.face.cameraon", lang)}
                    </button>
                    {camLive && (
                      <button className="chip" disabled={busy}
                              onClick={() => setFacing(
                                (f) => f === "user" ? "environment" : "user")}>
                        {tr("ins.face.flip", lang)}
                      </button>
                    )}
                    <button className="chip" disabled={busy}
                            onClick={() => picker.current?.click()}>
                      {tr("ins.face.photo", lang)}
                    </button>
                    <input ref={picker} type="file" accept="image/*"
                           style={{ display: "none" }}
                           onChange={(e) => {
                             const file = e.target.files?.[0];
                             e.target.value = "";
                             if (file) {
                               act(async () => {
                                 await api.uploadRoomFace(open, me, file, token);
                               })();
                             }
                           }} />
                    {/* Your own picture — the PERSON's, not this room's.
                        Two pictures, two buttons, and the difference is
                        which one follows you out of here: the one above is
                        what you are showing in THIS room, this is who you
                        are in all of them. */}
                    <button className="chip" disabled={busy}
                            onClick={() => mePicker.current?.click()}>
                      {tr("ins.face.mine", lang)}
                    </button>
                    <input ref={mePicker} type="file" accept="image/*"
                           style={{ display: "none" }}
                           onChange={(e) => {
                             const file = e.target.files?.[0];
                             e.target.value = "";
                             if (file) {
                               act(async () => {
                                 await api.setOwnPicture(me, file, token);
                                 load();
                               })();
                             }
                           }} />
                    {/* The background — behind you rather than instead of
                        you. Its own button because `photo` REPLACES the
                        person: somebody who wanted a room behind them and
                        pressed the only picture button available replaced
                        themselves with it. */}
                    <button className="chip" disabled={busy}
                            onClick={() => bgPicker.current?.click()}>
                      {tr("ins.face.background", lang)}
                    </button>
                    <input ref={bgPicker} type="file" accept="image/*"
                           style={{ display: "none" }}
                           onChange={(e) => {
                             const file = e.target.files?.[0];
                             e.target.value = "";
                             if (file) {
                               act(async () => {
                                 await api.uploadRoomBackground(
                                   open, me, file, token);
                                 load();
                               })();
                             }
                           }} />
                    {/* Off, back to a name in a box — which is still a box.
                        Offered only when there is something to take down. */}
                    {face && face.showing !== "voice" && (
                      <button className="chip" disabled={busy}
                              onClick={act(async () => {
                                await api.clearRoomFace(open, me, token);
                              })}>
                        {tr("ins.face.plain", lang)}
                      </button>
                    )}
                    {/* The masks. Two records, not one: taking a mask off and
                        turning a camera off are different actions, so this
                        sits beside the three above rather than among them. */}
                    <select className="chip" disabled={busy}
                            value={wearing?.kind || ""}
                            onChange={(e) => {
                              const kind = e.target.value;
                              act(async () => {
                                if (!kind) {
                                  await api.takeOffOverlay("room", open, me,
                                                           token);
                                  return;
                                }
                                const said = masks.find((m) => m.kind === kind);
                                await api.wearOverlay("room", open, {
                                  interactor_id: me, kind,
                                  title: said?.means || kind,
                                }, token);
                              })();
                            }}>
                      <option value="">{tr("ins.face.nomask", lang)}</option>
                      {masks.map((m) => (
                        <option key={m.kind} value={m.kind}>{m.means}</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
              );
            })}
            {/* The conversation, worn on the room itself — the gallery's
                design (screens 96–98, 105) the flat card below never
                delivered until a field report held the mockups up next
                to the live screen. A voice room wears the talk control
                in its place: text pasted over a room somebody came here
                to LISTEN to is the wrong furniture, not less of it. */}
            {spokenRoom ? voiceBar : chatStrip}
          </div>
          {/* "nobody here has turned a camera on" — true, and said to
              somebody looking at a room full of faces who can see that for
              themselves. Kept on the wire, where other readers use it;
              taken off the room, where it is furniture. */}
          {scene && !inRoom && (
            <p className="muted small">{scene.note}</p>
          )}
          {/* The way into the stage, offered only in the rooms whose whole
              pitch is being a place. Flat rooms stay flat; nothing here
              turns a chat room into a headset demand. */}
          {(channel === "ar" || channel === "vr") && (
            <button disabled={busy} onClick={() => {
              setYaw(0); setImmersed(true);
            }}>
              {channel === "ar" ? tr("ins.stage.ar", lang)
                                : tr("ins.stage.vr", lang)}
            </button>
          )}
        </div>
      )}

      {immersed && (channel === "ar" || channel === "vr") && (
        // The stage: the same room, stood in. AR draws the seats over this
        // device's own passthrough; VR draws them around a turntable the
        // drag turns. Both are rendered here and only here — no pixels of
        // yours and no room of anybody else's crosses the wire for this.
        <div className={"room-stage" + (channel === "vr" ? " vr" : "")}
             role="dialog" aria-label={tr("ins.stage.title", lang)}
             onPointerDown={(e) => {
               dragFrom.current = { x: e.clientX, yaw };
             }}
             onPointerMove={(e) => {
               if (dragFrom.current == null) return;
               // A third of a degree per pixel: a full swipe across a phone
               // turns about 120° — enough to look around the circle without
               // a flick spinning the room.
               setYaw(dragFrom.current.yaw
                 + (e.clientX - dragFrom.current.x) / 3);
             }}
             onPointerUp={() => { dragFrom.current = null; }}
             onPointerLeave={() => { dragFrom.current = null; }}>
          {channel === "ar" && !passDenied && (
            <video ref={pass} className="stage-pass" autoPlay playsInline muted
                   aria-label={tr("ins.stage.passlabel", lang)} />
          )}
          {channel === "ar" && passDenied && (
            <p className="stage-note">{tr("ins.stage.denied", lang)}</p>
          )}
          {channel === "vr" && (
            <div className="stage-floor" aria-hidden="true" />
          )}
          {channel === "vr" ? (
            <div className="stage-turn">
              {seats.map((s, i) => {
                // The circle: seats spaced evenly, each card counter-rotated
                // so it faces the viewer from wherever the turntable stops —
                // a billboard, which is what a face is for.
                const a = (360 / Math.max(seats.length, 1)) * i;
                return (
                  <div key={s.id} className="stage-anchor"
                       style={{ transform:
                         `rotateY(${a + yaw}deg) translateZ(-280px)` }}>
                    <div className={"stage-seat"
                                    + (isTalking(s) ? " talking" : "")}
                         style={{ transform: `rotateY(${-(a + yaw)}deg)` }}>
                      {stageFace(s)}
                      <span className="rs-name">{s.display}</span>
                      {s.kind !== "user" && (
                        <span className="rs-ai"
                              title={tr("ins.seat.profile", lang)}>
                          {tr("ins.seat.aimark", lang)}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            seats.map((s, i) => {
              // Anchored over the passthrough deterministically: the same
              // room shows everyone the same arrangement, because the seat
              // index — not a random draw — decides where a face floats.
              const n = Math.max(seats.length, 1);
              const left = 10 + (i * 80) / n + (i % 2) * 6;
              const top = 24 + ((i * 29) % 42);
              return (
                <div key={s.id}
                     className={"stage-seat ar"
                                + (isTalking(s) ? " talking" : "")}
                     style={{ left: `${left}%`, top: `${top}%` }}>
                  {stageFace(s)}
                  <span className="rs-name">{s.display}</span>
                  {s.kind !== "user" && (
                    <span className="rs-ai" title={tr("ins.seat.profile", lang)}>
                      {tr("ins.seat.aimark", lang)}
                    </span>
                  )}
                </div>
              );
            })
          )}
          {/* The conversation rides the stage, so stepping in is not
              stepping out of it — the same strip the flat scene wears,
              which for a voice room is the talk control. */}
          {spokenRoom ? voiceBar : chatStrip}
          <p className="stage-note">
            {channel === "ar" ? tr("ins.stage.arnote", lang)
                              : tr("ins.stage.vrnote", lang)}
          </p>
          <button className="stage-leave"
                  onClick={() => setImmersed(false)}>
            {tr("ins.stage.leave", lang)}
          </button>
        </div>
      )}

      {open && (
        <>
          <div className="card">
            <h3>
              {tr("ins.whatsaid", lang)}{" "}
              <button className={"chip" + (hearAll ? " primary" : "")}
                      onClick={flipHearAll}
                      title={hearAll ? tr("ins.hear.off", lang)
                                     : tr("ins.hear.on", lang)}
                      aria-pressed={hearAll}>
                🔊 {hearAll ? tr("ins.hear.off", lang)
                            : tr("ins.hear.on", lang)}
              </button>
            </h3>
            {transcript.length === 0 && (
              <p className="muted small">{tr("ins.nothingyet", lang)}</p>
            )}
            {transcript.map((m) => (
              <p className="small" key={m.id}>
                <strong>{m.from}</strong>: {m.content}
                {attachment(m)}
                {/* A profile turn can be heard in the voice its owner bound.
                    A press, never autoplay: the phone's rule and the room's
                    are the same — sound starts on a gesture. */}
                {m.sender_kind === "profile" && m.sender_id && (
                  <button className="chip" disabled={busy}
                          aria-label={tr("ins.hear", lang)}
                          onClick={() => {
                            const id = m.sender_id as string;
                            speakInPieces(id, m.content || "", token)
                              .then((s) => {
                                nowSaying.current = s;
                                setVoicing({ kind: "profile", id });
                                return s.done;
                              })
                              .then(() => setVoicing(null))
                              .catch((e) => {
                                setVoicing(null);
                                setError(e);
                              });
                          }}>
                    🔊
                  </button>
                )}
                {/* A profile's turn is always watermarked and a person's
                    never is, so the mark is the honest way to tell which
                    kind of speaker this was — not the name. */}
                {m.watermark?.display?.line && (
                  <span className="muted small">
                    {" "}· {m.watermark.display.line}
                  </span>
                )}
              </p>
            ))}
            <div className="row">
              {/* One picker for both composers — the pill on the scene and
                  this row share it, and whatever is typed rides along as
                  the caption. Never rendered as its own control: a bare
                  file input beside a styled row reads as somebody else's
                  form. */}
              <input ref={sharePick} type="file" style={{ display: "none" }}
                     accept="image/*,video/*,.pdf,.docx,.xlsx,.pptx,.zip,.txt"
                     onChange={(e) => {
                       const f = e.target.files?.[0];
                       e.target.value = "";
                       if (f) void shareFile(f);
                     }} />
              <button className="chip" disabled={busy || !token}
                      aria-label={tr("ins.share", lang)}
                      title={tr("ins.share", lang)}
                      onClick={() => sharePick.current?.click()}>
                📎
              </button>
              {/* A voice room keeps its record and loses its keyboard: the
                  typed box, the dictation mic that fills it and the send
                  all belong to a room people write in. Sharing a picture
                  and letting the profiles talk are not typing, so they
                  stay. The way in is the talk control on the room itself.
                  Where the browser ships no recogniser, `voiceBar` puts a
                  typed pill back with a line saying why. */}
              {!spokenRoom && (
              <input value={draft} onChange={(e) => setDraft(e.target.value)}
                     placeholder={tr("ins.say.ph", lang)} style={{ flex: 1 }}
                     onKeyDown={(e) => {
                       if (e.key === "Enter" && draft.trim() && !busy && token) {
                         void act(async () => {
                           const text = draft;
                           setDraft("");
                           await api.sayInRoom(open, me, text, token);
                         })();
                       }
                     }} />
              )}
              {/* Dictation: speech types into the box. The send below stays
                  a decision — a room has other people in it. Absent where
                  the browser ships no recogniser, not disabled: a dead
                  control is a broken promise drawn as a button. */}
              {canDictate && !spokenRoom && (
                <button className={"chip" + (dictating ? " primary" : "")}
                        disabled={busy}
                        aria-pressed={dictating}
                        aria-label={tr("ins.dictate", lang)}
                        title={tr("ins.dictate", lang)}
                        onClick={flipDictation}>
                  🎤
                </button>
              )}
              {/* A send is a small thing now — "the button could be a lot
                  smaller if it's only gonna be a send" — and Enter sends
                  too. The name survives in the label for a screen reader. */}
              {!spokenRoom && (
              <button className="chip"
                      disabled={busy || !token || !draft.trim()}
                      aria-label={tr("ins.sayit", lang)}
                      title={tr("ins.sayit", lang)}
                      onClick={act(async () => {
                        const text = draft;
                        setDraft("");
                        await api.sayInRoom(open, me, text, token);
                      })}>
                ➤
              </button>
              )}
              <button disabled={busy || !token}
                      onClick={act(async () => {
                        await api.advanceRoom(open, token);
                      })}>
                {tr("ins.letthemtalk", lang)}
              </button>
            </div>
            <p className="muted small">{tr("ins.watermarked", lang)}</p>
          </div>

          <div className="card">
            <h3>{tr("ins.microphones", lang)}</h3>
            {mics && <p className="muted small">{mics.note}</p>}
            {mics?.microphones_lent.map((m) => (
              <p className="small" key={m.interactor_id}>
                {fill(tr("ins.micline", lang), {
                  who: <code>{m.interactor_id}</code>, device: m.device,
                  hears: m.hears, when: m.since,
                })}
              </p>
            ))}
            <div className="row">
              {!lentByMe ? (
                <button disabled={busy || !token || !me}
                        onClick={act(async () => {
                          await api.lendMicInRoom(open, me, token);
                        }, tr("ins.lent", lang))}>
                  {tr("ins.lendmic", lang)}
                </button>
              ) : (
                <button disabled={busy || !token}
                        onClick={act(async () => {
                          await api.takeBackMicInRoom(open, me, token);
                        }, tr("ins.takenback", lang))}>
                  {tr("ins.takeback", lang)}
                </button>
              )}
            </div>
            <p className="muted small">{tr("ins.micpitch", lang)}</p>
          </div>

          <div className={"card" + (asking ? " asked-for" : "")}
               ref={askCard}>
            <h3>{tr("ins.ask.title", lang)}</h3>
            <p className="muted small">{tr("ins.ask.pitch", lang)}</p>
            <div className="row">
              <input value={guestId} style={{ flex: 1 }}
                     placeholder={tr("ins.ask.ph", lang)}
                     onChange={(e) => setGuestId(e.target.value)} />
              <button disabled={busy || !token || !guestId.trim()}
                      onClick={() => void askIn()}>
                {tr("ins.ask.go", lang)}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
