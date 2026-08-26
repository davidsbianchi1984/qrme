import { useEffect, useRef, useState } from "react";
import { isEcho, RECENT_TURNS } from "../echo";
import { api, getBase, type Avatar, type MicsHere, type RoomFaces,
         type RoomMsg } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { plainVoice, speakInPieces, type Speaking } from "../spoken";
import { useSession } from "../store";
import { putAway, whenPutAway } from "../away";
import { canRecord, meterWhileSpeaking, recordTurn, type Recording }
  from "../roomear";

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
  // `onerror` was missing from this type, which is why no caller wrote one.
  // A hand-written shape describes what the code is allowed to notice, and
  // this one quietly said failure was not among those things — so a refused
  // microphone had nowhere to be heard and fell through to `onend`, which
  // relit it. The type was the shape of the bug.
  onerror: ((e: { error?: string }) => void) | null;
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

/** Whether this browser has a recogniser at all.
 *
 *  Kept as its own fact because it is a real one, and because it is NOT the
 *  question the microphone button should be asking. On iOS this is true and
 *  the service refuses every time — a binding is not a door, which this
 *  console has learned in three separate places now. */
const hasRecogniser = typeof window !== "undefined"
  && Boolean((window as unknown as { SpeechRecognition?: unknown;
                                     webkitSpeechRecognition?: unknown })
      .SpeechRecognition
    || (window as unknown as { webkitSpeechRecognition?: unknown })
      .webkitSpeechRecognition);

/** Whether there is any way for this browser to hear you.
 *
 *      asked     does this browser have a recogniser
 *      mattered  can this person speak in the room
 *
 *  Two ears, and the button appears if either can stand. An iPhone has no
 *  usable recogniser and can record perfectly well, and it was being shown
 *  a room it could not talk in because the control asked the first question
 *  instead of the second. */
const canDictate = hasRecogniser || canRecord();

/** Why a shared file could not be read, in the reader's word for it, as a
 *  short clause in this person's language — see `whySays` in Briefcase.tsx
 *  for the same shape and the same reason. Branches with the key written out
 *  at each `tr`, because both a key table and a `${key}` template are
 *  invisible to the lookup scanner.
 *
 *  `null` for anything it does not recognise, so the line falls back to the
 *  plain wording rather than putting a missing-translation placeholder in
 *  the middle of somebody's conversation. */
function fileWhy(key: string | null | undefined, lang: string): string | null {
  if (key === "scanned") return tr("ins.file.why.scanned", lang);
  if (key === "locked") return tr("ins.file.why.locked", lang);
  if (key === "unmapped") return tr("ins.file.why.unmapped", lang);
  return null;
}

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
  // Why the device's voice is standing in for a profile's, when it is —
  // the server's own refusal sentence, shown beside the transcript. The
  // room used to fall back (or worse, fall silent) with no reason on
  // screen anywhere.
  const [earNote, setEarNote] = useState<string | null>(null);
  const [hearAll, setHearAll] = useState(
    () => localStorage.getItem("qrme.room.hear") !== "0");
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
  const nowSaying = useRef<Speaking | null>(null);
  /** Which TURN is in the air — the message id, not the speaker's. An
   *  interruption is about the sentence being said, and a profile can say
   *  several in a row. */
  const sayingMsg = useRef<string | null>(null);
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
  // Put away, not switched off. That comment above says the recogniser dies
  // at "a tab blur" and the standing ear restarts — which was true, and was
  // the bug: it restarted into a page the browser had stopped running, over
  // and over, while the mic button stayed lit and the line still read that
  // the room was being heard. A person talking into that gets no hint that
  // nothing is arriving.
  //
  //     asked     does the room stop hearing when the tab sleeps
  //     mattered  does the light go out with it
  //
  // So the ear comes down and says so, and it stands back up on return
  // because the decision behind it never changed.
  const dozing = useRef(false);
  /** A recording in flight, where this console records rather than relying
   *  on a recogniser the browser may not really have. */
  const taping = useRef<Recording | null>(null);
  /** Set once this platform has refused its own recogniser, so the next
   *  press does not spend another round trip discovering it again. */
  const recorderOnly = useRef(false);
  const [dozed, setDozed] = useState(false);
  // Why the ear died, when it did.
  //
  //     asked     is the microphone on
  //     mattered  can it hear you
  //
  // Field report from an iPhone, with the strip's mic lit gold: "the audio
  // on the mobile version isn't working in the chat room. I can mute the mic
  // and unmute the mic, and I can tap into the text bar, but it's not
  // picking up my voice."
  //
  // `startTalking` set `onresult` and `onend` and had NO `onerror` at all.
  // On iOS the `webkitSpeechRecognition` constructor exists — so `canDictate`
  // is true and the button renders — and the service then refuses. The
  // refusal fell through to `onend`, which read `wantTalking` as still true
  // and stood another recogniser, which was refused, forever. A lit
  // microphone that cannot hear is worse than no microphone, because the
  // person keeps talking to it.
  //
  // The sibling screen already carries this fix and the comment explaining
  // it. This room never got it.
  const [earFault, setEarFault] = useState<string | null>(null);
  /** Until when the ear disbelieves itself.
   *
   *  Field report, from Windows this time and after the text guard had
   *  already shipped: "the voice that's coming from my speaker, that is the
   *  synthetic profile talking to me, is being picked up on my microphone as
   *  a prompt."
   *
   *      asked     did the room hear something
   *      mattered  was it somebody in it
   *
   *  `isEcho` compares what was heard against what the room just said and
   *  needs 70% of the words to line up. That catches a clean echo. It does
   *  not catch a misheard one — the microphone hears the speaker through the
   *  room, the recogniser guesses at it, and a guess about a sentence is not
   *  70% the same sentence. So the mangled version cleared the guard and was
   *  sent as though somebody had said it.
   *
   *  The certain test is not what the words were, it is when they arrived: a
   *  microphone open while this room's own voice is in the air has nothing
   *  to offer. `speaking` says exactly that and was sitting right here
   *  unread. The tail covers the speaker still decaying and the recogniser
   *  delivering a result it formed a moment ago. */
  const ECHO_TAIL_MS = 900;
  const disbelieveUntil = useRef(0);

  /** The room started saying something out loud.
   *
   *  Called by EVERY path that puts a voice in this room, which is the
   *  whole point of it existing. There were two — the 🔊 toggle that reads
   *  the backlog, and the 🔊 on each line — and the first release of this
   *  guard set the flag inside the first one only. So a person using the
   *  per-line button had no time gate AND no `roomSaid` window, which means
   *  both echo nets were blind at once and the profile's own speech walked
   *  into the room as a prompt. Reported from a Windows handheld, where the
   *  recogniser works perfectly and heard the speaker beautifully.
   *
   *      asked     is the room speaking
   *      mattered  which button started it
   *
   *  The answer must not depend on the second question. A comment two
   *  screens up already said "the per-turn 🔊 is still on every line" — the
   *  code named the other speaker and the fix gated one of them.
   */
  /** Somebody spoke up while the room was talking, loudly enough that a
   *  speaker across the table would not have. Believed for exactly one
   *  turn: interrupting is a thing you do, not a state you enter. */
  const barged = useRef(false);
  const closeMeter = useRef<(() => void) | null>(null);

  function roomSpeaks(said: string) {
    speaking.current = true;
    // The meter runs only while the voice is in the air, and ONLY for
    // somebody whose own microphone is already standing.
    //
    //     asked     can we tell an interruption from an echo
    //     mattered  whose microphone are we opening to find out
    //
    // The first version asked the first question and not the second: it
    // opened a stream whenever the room spoke, so a person who had never
    // pressed the microphone — reading a room with the voices on — got a
    // recording light they did not ask for. That is worse than the problem
    // it solves. `wantTalking` is the person having already said yes to
    // this room hearing them; metering under that decision adds nothing
    // they have not already allowed, and metering without it is the
    // product taking a liberty.
    //
    // Nobody listening in silence loses anything: they were not talking, so
    // there is no interruption to recognise.
    if (wantTalking.current && !closeMeter.current) {
      barged.current = false;
      void meterWhileSpeaking(() => {
        barged.current = true;
        // Barging in IS a turn. Believing the words and letting the profile
        // keep talking over them is half an interruption, which is the
        // half nobody asked for.
        nowSaying.current?.stop();
      })
        .then((close) => {
          // The voice may have finished while the microphone was opening.
          if (speaking.current) closeMeter.current = close; else close();
        });
    }
    // Remembered before it plays, not after: the microphone is open the
    // whole time this voice is in the air, so the words have to be in the
    // window before they can come back through it.
    roomSaid.current = [...roomSaid.current, said].slice(-RECENT_TURNS);
  }

  /** And stopped. The tail covers the speaker still decaying and the
   *  recogniser delivering a result it formed a moment ago. */
  /** The person has taken the turn. The speaker stops; the words stay.
   *
   *      asked     did the person say something
   *      mattered  is the profile still talking over it
   *
   *  Sending IS the interruption. Somebody who spoke on purpose, or typed
   *  and pressed send while a profile was mid-answer, has said as plainly
   *  as it can be said that they want this one to stop — usually because it
   *  is heading somewhere they are trying to head off. Waiting for the
   *  paragraph to finish delivers the correction after the thing it was
   *  meant to prevent.
   *
   *  What stops is the AUDIO and only the audio. `stop()` pauses the
   *  element, so the voice ends on the word it is on rather than at the end
   *  of the sentence or the queue. The reply itself is untouched: the
   *  transcript comes from the room's own record, so the full text stays on
   *  screen to be read, scrolled back to and answered. Cutting a voice off
   *  is not deleting what it said.
   */
  /** What the last interruption cut off: which turn, and how much of it
   *  reached the room. Spent on the next thing said, because it describes
   *  that one turn and not the conversation. */
  const cutOff = useRef<{ id: string; heard: string } | null>(null);

  function personTakesTheTurn() {
    // The QUEUE first, not just the sentence.
    //
    //     asked     did the voice in the air stop
    //     mattered  did the next one start
    //
    // `stop()` pauses the piece being played, which resolves `s.done`, which
    // lets the backlog loop move straight on to the following message and
    // begin speaking that. So an interruption ended one sentence and bought
    // the next paragraph — reported exactly that way: "it won't stop, you
    // have to wait for a paragraph or two to finish."
    //
    // `earRun` is the loop's own break, and it was only ever bumped when
    // somebody left the room. A person interrupting is the same fact:
    // whatever was queued is not what they want to hear now.
    earRun.current++;
    // Read before the stop: `heard()` reports the pieces that actually
    // played, and stopping is what makes that number final.
    const said = nowSaying.current?.heard() || "";
    const was = sayingMsg.current;
    if (was && said) cutOff.current = { id: was, heard: said };
    sayingMsg.current = null;
    nowSaying.current?.stop();
    nowSaying.current = null;
    setVoicing(null);
    roomFellQuiet();
  }

  function roomFellQuiet() {
    speaking.current = false;
    disbelieveUntil.current = Date.now() + ECHO_TAIL_MS;
    closeMeter.current?.();
    closeMeter.current = null;
  }
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
  // Your friends list, in the room, because a text box asking for a profile
  // id is a door with the key filed off.
  //
  //     asked     can you ask somebody into the room
  //     mattered  can you ask somebody whose id you do not know
  //
  // Field report: "my friends list should appear and be able to choose from
  // the friends list to add other friends and profiles to the chat." The
  // invite has worked all along — host asks, the guest's owner accepts —
  // and the only way to name the guest was to type `prf_3735f90003ba`,
  // which nobody has and nothing on screen showed. The list is the same
  // rows the Friends screen draws, read from the same door.
  const [myFriends, setMyFriends] = useState<
    { profile_id: string; display_name: string;
      avatar?: string | null; handle?: string | null }[] | null>(null);
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
  // Going in is a press, not a consequence of knowing an id.
  //
  //     asked     do you have a room id
  //     mattered  have you gone in
  //
  // `inRoom` was `Boolean(open)`, so the moment a room id existed — typed,
  // remembered, or handed in by another screen — this component joined the
  // room and drew the faces. Field report, from a phone: "it shouldn't
  // even be shown yet. I don't think it should dive straight into the
  // room." Having somebody's address is not the same as being in their
  // house, and the frames arriving before the press made the button that
  // follows them look like it had already been pressed.
  const [entered, setEntered] = useState(false);
  // Who is coming, picked before the door opens.
  //
  //     asked     can you invite somebody
  //     mattered  can you decide who is coming BEFORE you walk in
  //
  // `POST /rooms/{id}/invite` requires the inviter to already be in the
  // room, and deliberately: "inviting somebody somewhere you are not is
  // how a room id becomes a way to send mail." That rule is not worth
  // loosening for an ordering preference, so the picks are gathered here
  // and sent the moment the join lands. From the outside it is choosing
  // your guests before you go in; underneath, you are in the room by the
  // time a single invite leaves.
  const [guestList, setGuestList] = useState<string[]>([]);
  const inRoom = entered && Boolean(open);
  // Read by the strip, which is built long before the cards that used
  // to be the only reader. Declared with `inRoom` for that reason —
  // this is the third dead-zone crash on this screen from a const
  // sitting below its first use.
  const lentByMe = mics?.microphones_lent.some((m) => m.interactor_id === me);
  // The room's name, read off the join answer and editable in place.
  const [roomName, setRoomName] = useState("");
  async function saveName() {
    const want = roomName.trim();
    if (!want || !token || busy) return;
    await act(async () => {
      await api.renameRoom(open, me, want, token);
      setNote(tr("ins.roomname.saved", lang));
    })();
  }

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
      .then((r) => {
        setSeats(r.participants);
        setChannel(r.channel);
        // The name, so the box shows what the room is called rather than
        // an empty field somebody has to guess the current value of.
        setRoomName(r.topic || "");
      })
      .catch(() => setSeats([]));
    // What is in the seats, and who is wearing what — one call, because a
    // second one would draw a frame with a face and no disclosure on it.
    api.roomFaces(open, token).then(setScene).catch(() => setScene(null));
  }
  // Loads when you go IN, not when an id appears. The dependency was
  // `[open, token]`, which is exactly the dive this screen was reported
  // for — and it also meant every keystroke in the id box tried to join a
  // half-typed room.
  useEffect(() => { if (entered) load(); }, [entered, open, token]);

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
      localStorage.removeItem("qrme.room.hear");
      // Everything already said stays said: the toggle speaks what comes
      // next, not the scrollback.
      heardUpTo.current = transcript.length > 0
        ? transcript[transcript.length - 1].id : null;
    } else {
      // "0" is the remembered mute; hearing is the default a fresh
      // browser arrives with, after the field report that said, in one
      // word, what a silent room reads as: broken.
      localStorage.setItem("qrme.room.hear", "0");
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
    const run = earRun.current;
    void (async () => {
      try {
        for (const m of fresh) {
          if (run !== earRun.current) break;
          // Piece by piece: a long turn starts being heard at its first
          // sentence. A first piece the platform refuses now REJECTS
          // rather than resolving as a reply that was heard.
          let s: Speaking;
          try {
            s = await speakInPieces(
              m.sender_id as string, m.content || "", token);
          } catch (e) {
            // No binding, no engine key, or the platform refused. The
            // room used to go silently deaf on exactly this — the whole
            // backlog abandoned on the first profile without a voice, and
            // "no audio in the rooms" reported three times with nothing
            // on screen to say why. The device's voice stands in per
            // turn, and the reason is a line beside the transcript.
            const why = (e as { message?: string })?.message;
            if (why) setEarNote(why);
            roomSpeaks(m.content || "");
            setVoicing({ kind: "profile", id: m.sender_id as string });
            await plainVoice(m.content || "", lang);
            setVoicing(null);
            roomFellQuiet();
            continue;
          }
          roomSpeaks(m.content || "");
          nowSaying.current = s;
          sayingMsg.current = m.id;
          if (run !== earRun.current) { s.stop(); break; }
          // The light follows the voice: while a backlog is being read,
          // the transcript's last line is not who is speaking.
          setVoicing({ kind: "profile", id: m.sender_id as string });
          await s.done;
        }
      } catch { /* a voice that cannot be fetched leaves the text standing */ }
      nowSaying.current = null;
      setVoicing(null);
      roomFellQuiet();
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
    // The barge-in meter is a microphone too. Leaving a room with one open
    // is the light nobody asked to leave on.
    closeMeter.current?.();
    closeMeter.current = null;
  }, [open]);

  // The room, put away. Both microphones go down — the standing ear and
  // dictation — and only the standing ear comes back, because it was a
  // decision and dictation was a press. Whatever the ear had already heard
  // is sent before it goes: a person who finished a sentence and then
  // switched tabs meant to say it, which is the same bargain the button's
  // own stop makes.
  useEffect(() => whenPutAway(
    () => {
      dictation.current?.stop();
      dictation.current = null;
      setDictating(false);
      if (!wantTalking.current || dozing.current) return;
      dozing.current = true;
      setDozed(true);
      if (silence.current !== null) {
        window.clearTimeout(silence.current);
        silence.current = null;
      }
      sendPending();
      talkRec.current?.stop();
      talkRec.current = null;
      setTalking(false);
    },
    () => {
      if (!dozing.current) return;
      dozing.current = false;
      setDozed(false);
      if (wantTalking.current) startTalking();
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []);

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
  /** Send what was heard.
   *
   *  `barged` says the words came from the recorded ear, which has an
   *  analyser in front of it and already decided: a peak that cleared
   *  `BARGE_PEAK` while the room was speaking is a person leaning into the
   *  microphone, not a speaker across the table. The time gate exists
   *  because the recogniser has no analyser and cannot tell those apart;
   *  applying it to an ear that CAN tell would throw away the interruption
   *  it just correctly recognised.
   *
   *      asked     was that the room's own voice
   *      mattered  which ear is being asked
   */
  function sendPending(fromEar = false) {
    const said = pending.current.trim();
    pending.current = "";
    setDraft("");
    if (!said || !token) return;
    // Two nets, and this is the second one. The first is time — nothing
    // heard while the room was speaking got this far. This one catches a
    // clean echo that arrived after the tail, and it stays because the two
    // fail in different directions: a text match misses a mangled echo, and
    // a clock misses a late one.
    // Three ways to be believed: the recorded ear already ruled (`fromEar`),
    // the meter heard somebody lean in, or the room was not speaking.
    const interrupted = barged.current;
    barged.current = false;
    if (!fromEar && !interrupted
        && (speaking.current || Date.now() < disbelieveUntil.current)) return;
    if (isEcho(said, roomSaid.current.join(" "))) {
      // The room hearing itself. Dropped silently and the ear stays
      // open — announcing it would be the product apologising for a
      // microphone the person never pressed.
      return;
    }
    // Past both nets, so these are somebody's own words rather than the
    // room's — which makes them a turn, and a turn stops the voice that
    // was still finishing the last one.
    personTakesTheTurn();
    // Past both nets, so these are somebody's own words and not the room's
    // — which makes them a turn, and a turn stops the voice still finishing
    // the last one.
    personTakesTheTurn();
    // Past both nets, so these are somebody's own words and not the room's
    // — which makes them a turn, and a turn stops the voice that is still
    // finishing the last one.
    personTakesTheTurn();
    // `act` is deliberately not used: it flips `busy`, which would grey
    // out the room under somebody mid-conversation.
    const cut = cutOff.current;
    cutOff.current = null;
    api.sayInRoom(open, me, said, token, cut || undefined)
      .then(load).catch(setError);
  }

  /** The recorded ear, standing.
   *
   *  One turn at a time: open the microphone, wait for the silence that
   *  means the sentence is over, post the audio, put the words in. Then do
   *  it again, because the person's decision has not changed — the same
   *  contract the recogniser's `onend` has, with a mechanism that does not
   *  depend on what speech service the browser ships.
   *
   *  Every failure ends the loop rather than feeding it. A microphone that
   *  keeps reopening into a refusal is the defect this room has already had
   *  twice, once per ear.
   */
  async function standRecordedEar() {
    if (!token || taping.current) return;
    while (wantTalking.current && !dozing.current) {
      let turn: Recording;
      try {
        turn = await recordTurn(open, me, token,
                                () => speaking.current, undefined);
      } catch {
        // The microphone itself was refused. Nothing to retry into.
        setEarFault(tr("ins.ear.blocked", lang));
        wantTalking.current = false;
        setTalking(false);
        return;
      }
      taping.current = turn;
      setTalking(true);
      let said = "";
      try {
        said = await turn.done;
      } catch (e) {
        const why = (e as Error).message || "";
        // Quiet is not a failure: a turn nobody spoke into simply opens
        // the microphone again, which is what a standing ear is for.
        if (why !== "nothing was heard in that"
            && why !== "nothing was recorded") {
          // Everything else is the door refusing — most often a deployment
          // with no transcriber, which is a sentence its owner can act on
          // and no amount of pressing will change.
          setError(e);
          wantTalking.current = false;
          taping.current = null;
          setTalking(false);
          return;
        }
      }
      taping.current = null;
      if (said) {
        pending.current = said;
        setDraft(said);
        // `true`: the analyser already ruled on this one.
        sendPending(true);
      }
    }
    setTalking(false);
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
    if (talkRec.current || taping.current) return;
    wantTalking.current = true;
    if (putAway()) {
      dozing.current = true;
      setDozed(true);
      setTalking(false);
      return;
    }
    // No recogniser, or one this platform has already refused: record and
    // send instead. Chosen by what works rather than by hope — on iOS the
    // constructor exists and the service always refuses, so "is there a
    // constructor" was never the question worth asking.
    if (!SR || recorderOnly.current) {
      if (!canRecord()) {
        setEarFault(tr("ins.ear.platform", lang));
        wantTalking.current = false;
        setTalking(false);
        return;
      }
      setEarFault(null);
      void standRecordedEar();
      return;
    }
    // One microphone: dictation and the standing ear cannot both hold it.
    dictation.current?.stop();
    dictation.current = null;
    setDictating(false);
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
      // Gated here rather than only at the send, so the room's own words
      // never reach the draft box either — watching the profile type its
      // last sentence into your composer is the same bug with a worse view.
      //
      // But NOT past somebody interrupting. This gate is why barge-in could
      // not work on a browser with a recogniser: it dropped everything heard
      // while the room spoke, at the ear, so the words never reached the
      // send and the meter's verdict had nothing left to be applied to. A
      // person talking over a profile got silence twice — the voice did not
      // stop, and what they said was thrown away.
      //
      //     asked     is the room speaking
      //     mattered  is somebody speaking over it on purpose
      //
      // `barged` is the meter's answer to the second question, and it is the
      // only thing that can tell an interruption from an echo on this path.
      if (!barged.current
          && (speaking.current || Date.now() < disbelieveUntil.current)) return;
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
    // The three a person can act on, each named, and the fourth that names
    // itself as a dead end. `no-speech` and `aborted` are the ordinary end of
    // a quiet stretch and the restart below is the right answer to them.
    let fatal = false;
    rec.onerror = (e: { error?: string }) => {
      const code = e.error || "";
      if (code === "not-allowed") {
        fatal = true; setEarFault(tr("ins.ear.blocked", lang));
      } else if (code === "service-not-allowed" && canRecord()) {
        // The platform refusing its own recogniser — iOS, every time. There
        // is a second ear, so this is a fork in the road rather than a dead
        // end, and the person is told nothing because nothing was lost.
        recorderOnly.current = true;
        fatal = true;
      } else if (code === "service-not-allowed") {
        // The platform refusing, rather than the person. No setting on the
        // phone changes it and no number of presses will either, so the
        // sentence says that instead of sending somebody to a switch.
        fatal = true; setEarFault(tr("ins.ear.platform", lang));
      } else if (code === "audio-capture") {
        fatal = true; setEarFault(tr("ins.ear.nomic", lang));
      } else if (code === "network") {
        fatal = true; setEarFault(tr("ins.ear.unreachable", lang));
      }
    };
    rec.onend = () => {
      talkRec.current = null;
      if (dozing.current) return;
      // A fault relighting cannot fix ends the ear rather than feeding the
      // loop. `wantTalking` goes with it: leaving the decision standing
      // would have the next press restart straight back into the refusal.
      if (fatal) {
        // A fault with somewhere to go hands the ear over; one without
        // ends it. Either way the loop never restarts into the refusal.
        if (recorderOnly.current && wantTalking.current) {
          void standRecordedEar();
          return;
        }
        wantTalking.current = false;
        setTalking(false);
        return;
      }
      if (wantTalking.current) { startTalking(); return; }
      setTalking(false);
    };
    rec.start();
    talkRec.current = { stop: () => rec.stop() };
    setEarFault(null);
    setTalking(true);
  }

  function stopTalking() {
    wantTalking.current = false;
    dozing.current = false;
    setDozed(false);
    // Whichever ear is standing. `stop` on a recording ends the turn and
    // sends what it already has, the same bargain the recogniser's stop
    // makes with a finished sentence.
    taping.current?.stop();
    taping.current = null;
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
    personTakesTheTurn();
    const cut = cutOff.current;
    cutOff.current = null;
    await act(async () => {
      await api.sayInRoom(open, me, text, token, cut || undefined);
    })();
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
          {m.media.read
            // A prefix, said as one — the same fact the profiles are told,
            // on the line the person who shared it is reading.
            ? (m.media.full_chars
                ? fill(tr("ins.file.part", lang), {
                    chars: (m.media.chars || 0).toLocaleString(),
                    whole: m.media.full_chars.toLocaleString() })
                : tr("ins.file.read", lang))
            : (fileWhy(m.media.unread_why, lang)
                ? tr("ins.file.unread", lang) + " — "
                  + fileWhy(m.media.unread_why, lang)
                : tr("ins.file.unread", lang))}
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
         * while it listens, and five seconds of silence sends.
         *
         * One glyph, two states — lit and dim — rather than a slashed
         * speaker for the idle case. The slash read as "sound is muted"
         * on a button that actually means "press to talk", and the owner
         * asked for it gone by name. The lit/dim treatment was already
         * the design; the slash was never carrying information. */}
        {canDictate && (
          <button className={"rs-round mic" + (talking ? " live" : "")}
                  aria-pressed={talking}
                  aria-label={talking ? tr("ins.mute", lang)
                                      : tr("ins.unmute", lang)}
                  title={talking ? tr("ins.mute", lang)
                                 : tr("ins.unmute", lang)}
                  onClick={flipTalking}>🎙</button>
        )}
        <button className="rs-round invite" disabled={busy || !token}
                aria-label={tr("ins.ask.title", lang)}
                title={tr("ins.ask.title", lang)}
                onClick={() => setAsking(true)}>👤+</button>
        {/* Lending the profiles your microphone — a sixth control, beside
         * the handover it sits next to in meaning: both hand something of
         * yours to somebody else. It had a whole card explaining itself,
         * which is the right amount of words and the wrong place for
         * them; the sentence stays as the button's title, where somebody
         * reaching for it will actually meet it.
         *
         * Two states, not one, because lending and taking back are
         * different acts and a toggle that says "microphone" for both
         * tells you nothing about which way it is pointing. */}
        <button className={"rs-round lend" + (lentByMe ? " live" : "")}
                disabled={busy || !token || !me || !open}
                aria-pressed={lentByMe}
                aria-label={lentByMe ? tr("ins.takeback", lang)
                                     : tr("ins.lendmic", lang)}
                title={tr("ins.micpitch", lang)}
                onClick={act(async () => {
                  if (lentByMe) {
                    await api.takeBackMicInRoom(open, me, token);
                  } else {
                    await api.lendMicInRoom(open, me, token);
                  }
                }, lentByMe ? tr("ins.takenback", lang)
                            : tr("ins.lent", lang))}>
          {lentByMe ? "🎧" : "🎚"}
        </button>
        {/* Letting the profiles talk without you saying anything. The one
         * control on the card below that was NOT a duplicate, so it moved
         * here rather than out of the product — deleting the only door to
         * a capability is a different act from removing a second copy of
         * one. Sending a message already makes them reply; this is for
         * when you want to hear them without adding a line. */}
        <button className="rs-round talkers" disabled={busy || !token || !open}
                aria-label={tr("ins.letthemtalk", lang)}
                title={tr("ins.letthemtalk", lang)}
                onClick={act(async () => {
                  await api.advanceRoom(open, token);
                })}>💬</button>
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
        {/* A fault outranks everything else this line can say. An ear that
            reports "hearing you" over a microphone the platform refused is
            the line lying in the one direction that costs somebody their
            words — they keep talking. */}
        {earFault
          ? earFault
          : voicing
          ? fill(tr("ins.voice.speaking", lang),
                 { who: seats.find((s) => isTalking(s))?.display
                        || tr("ins.voice.someone", lang) })
          : dozed ? tr("ins.voice.asleep", lang)
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

  /** Read the list when the panel opens, not on every room render.
   *
   *  A failure here leaves `mine` as an empty list rather than an error:
   *  the id box below still works, and a friends list that would not load
   *  is not a reason to refuse the invite that does. */
  useEffect(() => {
    if (!asking || myFriends !== null || !session.profileId) return;
    api.friends(session.profileId)
      .then((r) => setMyFriends(r.friends))
      .catch(() => setMyFriends([]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [asking, session.profileId]);

  async function askIn(who?: string) {
    const guest = (who ?? guestId).trim();
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

            {/* The list first, because it is the answer for everybody who
                does not already know an id — which is everybody. Anyone
                already seated is shown and not pressable: a row that
                re-invites somebody sitting in the room is a press that
                cannot mean anything. */}
            {myFriends !== null && myFriends.length > 0 && (
              <>
                <p className="rh-note">{tr("ins.ask.yours", lang)}</p>
                <div className="rh-list">
                  {myFriends.map((f) => {
                    const seated = seats.some((s) => s.id === f.profile_id);
                    return (
                      <button key={f.profile_id} className="rh-friend"
                              disabled={busy || !token || seated}
                              onClick={() => {
                                setAsking(false); void askIn(f.profile_id);
                              }}>
                        {f.avatar ? (
                          <img className="friend-photo"
                               src={getBase() + f.avatar} alt="" />
                        ) : (
                          <span className="friend-photo friend-initials"
                                aria-hidden="true">
                            {f.display_name.split(/\s+/)
                              .map((w) => w[0]).join("").slice(0, 2)}
                          </span>
                        )}
                        <span className="rh-friend-name">{f.display_name}</span>
                        {seated && (
                          <span className="muted small">
                            {tr("ins.ask.here", lang)}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </>
            )}
            {myFriends !== null && myFriends.length === 0 && (
              <p className="rh-note">{tr("ins.ask.nofriends", lang)}</p>
            )}

            {/* Still here, and deliberately second: an id from somewhere
                else is a real way in, and the list not covering it is not a
                reason to take the box away. */}
            <p className="rh-note">{tr("ins.ask.orid", lang)}</p>
            <input value={guestId}
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
        // The way out, as an X. Asked for in those words — "you were just
        // supposed to incorporate an X to close and go back to the
        // previous window" — and an X is what a person looks for at the
        // corner of something they are inside of. The word is still there
        // for anybody reading the screen rather than seeing it.
        <button className="room-out" aria-label={tr("ins.leave", lang)}
                title={tr("ins.leave", lang)}
                onClick={() => { setEntered(false); onLeave(); }}>
          ✕
        </button>
      )}
      {!inRoom && <h2>{tr("ins.title", lang)}</h2>}
      {!inRoom && <p className="muted small">{tr("ins.pitch", lang)}</p>}

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {/* One card, two jobs, decided by whether you are in a room yet.
       *
       *     asked     which room do you want
       *     mattered  and once you are in it, what is it called
       *
       * Outside: the id box and Go in, as before. Inside: the same place
       * becomes the room's NAME and the button becomes Save — which is
       * where a person already is when they notice the name is wrong.
       * Field request: "that's a good place to edit your room name while
       * you're already in, and the button that says Go in — I just need to
       * say Save and it'll save the name." */}
      <div className="card">
        <h3>{inRoom ? tr("ins.roomname", lang) : tr("ins.whichroom", lang)}</h3>
        <div className="row">
          {inRoom ? (
            <input value={roomName}
                   onChange={(e) => setRoomName(e.target.value)}
                   onKeyDown={(e) => { if (e.key === "Enter") void saveName(); }}
                   placeholder={tr("ins.roomname.ph", lang)}
                   style={{ flex: 1 }} />
          ) : (
            <input value={roomId} onChange={(e) => setRoomId(e.target.value)}
                   placeholder={tr("ins.roomid.ph", lang)} style={{ flex: 1 }} />
          )}
          {inRoom ? (
            <button disabled={busy || !token || !roomName.trim()}
                    onClick={() => void saveName()}>
              {tr("ins.roomname.save", lang)}
            </button>
          ) : (
            <button disabled={busy || !open || !token} onClick={act(async () => {
              setEntered(true);
              load();
              // The join is what makes the invites legal, so they go after
              // it and never before. One failure does not take the others
              // down: an id that is not a profile is that guest's problem,
              // not the room's.
              for (const guest of guestList) {
                try { await api.inviteToRoom(open, guest, token); }
                catch { /* said in the note below, not thrown away */ }
              }
              if (guestList.length) {
                // `fill` returns nodes for rendering; a note is a string.
                setNote(tr("ins.ask.queued.sent", lang)
                          .replace("{count}", String(guestList.length)));
                setGuestList([]);
              }
            })}>
              {tr("ins.goin", lang)}
            </button>
          )}
        </div>
        {!token && (
          <p className="muted small">{tr("ins.signinperson", lang)}</p>
        )}
      </div>

      {/* Who is coming, chosen on the way in rather than after arriving.
       *
       * Only before you enter: once you are inside, the strip's 👤+ is the
       * invite and a second copy would be the duplication two other cards
       * were just removed for. */}
      {!inRoom && (
        <div className="card">
          <h3>{tr("ins.ask.title", lang)}</h3>
          <p className="muted small">{tr("ins.ask.pitch", lang)}</p>
          <div className="row">
            <input value={guestId} style={{ flex: 1 }}
                   placeholder={tr("ins.ask.ph", lang)}
                   onChange={(e) => setGuestId(e.target.value)}
                   onKeyDown={(e) => {
                     if (e.key !== "Enter") return;
                     const g = guestId.trim();
                     if (!g || guestList.includes(g)) return;
                     setGuestList((l) => [...l, g]);
                     setGuestId("");
                   }} />
            <button disabled={!guestId.trim()
                              || guestList.includes(guestId.trim())}
                    onClick={() => {
                      setGuestList((l) => [...l, guestId.trim()]);
                      setGuestId("");
                    }}>
              {tr("ins.ask.add", lang)}
            </button>
          </div>
          {/* The list, with a way off it. A queue you cannot correct is a
              queue that sends the typo. */}
          {guestList.map((g) => (
            <p className="small" key={g}>
              <code>{g}</code>{" "}
              <button className="chip"
                      aria-label={tr("ins.ask.drop", lang)}
                      onClick={() => setGuestList(
                        (l) => l.filter((x) => x !== g))}>✕</button>
            </p>
          ))}
          {guestList.length > 0 && (
            <p className="muted small">
              {fill(tr("ins.ask.queued", lang),
                    { count: String(guestList.length) })}
            </p>
          )}
        </div>
      )}

      {inRoom && seats.length > 0 && (
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
                    {/* There is deliberately no "my own picture" button
                        here any more. It sat beside "put a picture up"
                        doing what read as the same thing, and the owner
                        asked for it gone by name: the circle DEFAULTS to
                        the person's own picture — the seat falls through
                        to it whenever nothing is put up for this room —
                        and the picture itself is set once, on the
                        Identity screen, not per room. Two buttons for one
                        visible outcome is a menu, and the menu problem is
                        the one this product keeps choosing not to have. */}
                    {/* Taking your own picture down. Offered only when
                        there is one, and separate from the room's own
                        "back to a name in a box" — that clears what you
                        are showing HERE, this clears who you are in every
                        room, and conflating them would take a face off
                        four rooms when somebody meant one. */}
                    {ownPic(me) && (
                      <button className="chip" disabled={busy}
                              onClick={act(async () => {
                                await api.clearOwnPicture(me, token);
                                load();
                              })}>
                        {tr("ins.face.mineoff", lang)}
                      </button>
                    )}
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
                    {/* "Just my name" used to sit here — taken out on
                        request, and it took something with it that the
                        request did not ask for. That chip only changed
                        what was DISPLAYED, and the way back to a name in
                        a box is still the camera control. But it was also
                        the only caller of the one route that takes an
                        uploaded picture or background back OFF the server,
                        so removing it left somebody who put up a
                        background they regret with no way down.
                        This is the taking-down half, kept and narrowed:
                        offered only when there is something up to take
                        down, which the display toggle never checked. */}
                    {(face?.media_url || face?.background_url) && (
                      <button className="chip" disabled={busy}
                              onClick={act(async () => {
                                await api.clearRoomFace(open, me, token);
                                load();
                              })}>
                        {tr("ins.face.hereoff", lang)}
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
          </div>
          {/* A SIBLING of the scene, not a child of it.
           *
           *     asked     where does the strip sit
           *     mattered  can it ever sit on top of the faces
           *
           * It used to live inside `.room-scene`, absolutely positioned,
           * with the stage reserving a hardcoded 104px underneath. That
           * number was right the day it was written and wrong the moment
           * the transcript grew to four scrolling rows — reported three
           * times, each time as the bar "resting on top of the frames".
           *
           * A reserved constant is a guess about somebody else's height.
           * As a sibling it takes the space it actually needs and the
           * scene shrinks by exactly that much, so the two cannot overlap
           * whatever either of them grows into later. */}
          {spokenRoom ? voiceBar : chatStrip}
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

      {inRoom && (
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
            {earNote && (
              <div className="voice-note" role="status">
                <span>🔇 {earNote}</span>
                <button type="button" aria-label="×"
                        onClick={() => setEarNote(null)}>×</button>
              </div>
            )}
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
                            // Announced before a note of it plays, and
                            // through the same door the backlog uses. This
                            // button put the profile's voice in the room
                            // with neither echo net watching.
                            roomSpeaks(m.content || "");
                            speakInPieces(id, m.content || "", token)
                              .then((s) => {
                                nowSaying.current = s;
                                sayingMsg.current = m.id;
                                setVoicing({ kind: "profile", id });
                                return s.done;
                              })
                              .then(() => { setVoicing(null); roomFellQuiet(); })
                              .catch((e) => {
                                setVoicing(null);
                                // Quiet again even when the voice failed:
                                // a flag left standing would deafen the
                                // room until it was reloaded.
                                roomFellQuiet();
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
            {/* The compose row that used to sit here is gone.
             *
             *     asked     can you say something
             *     mattered  is there more than one place to say it
             *
             * A paperclip, a dictation mic, a type box and a send —
             * every one of them already in the strip that rides the room
             * itself, so this card offered a second, worse copy of the
             * same conversation. Field report: "I thought we had gotten
             * rid of this series of buttons and secondary text bar... we
             * can get rid of all those."
             *
             * The one control here that was NOT a duplicate — letting the
             * profiles talk without you saying anything — moved into the
             * strip rather than out of the product, because deleting the
             * only door to a capability is a different act from removing
             * a second copy of one. This card is the record now, and a
             * record is for reading. */}
            {/* The file picker stays: the strip's own attach button
                clicks it, so it is this row's one surviving job. */}
            <input ref={sharePick} type="file" style={{ display: "none" }}
                   accept="image/*,video/*,.pdf,.docx,.xlsx,.pptx,.zip,.txt"
                   onChange={(e) => {
                     const f = e.target.files?.[0];
                     e.target.value = "";
                     if (f) void shareFile(f);
                   }} />
            <p className="muted small">{tr("ins.watermarked", lang)}</p>
          </div>

          {/* Two cards left this screen here.
           *
           *     asked     is the control on screen
           *     mattered  is it on screen TWICE
           *
           * "Ask somebody into the room" repeated the strip's 👤+, and
           * "Lend them my microphone" is now a control in the strip beside
           * the handover arrow. A second copy of a button is not more
           * discoverable, it is one more thing to read past — and the
           * strip is where a person's hand already is. The doors both
           * cards opened are unchanged; only these copies of them are
           * gone. */}
        </>
      )}
    </div>
  );
}
