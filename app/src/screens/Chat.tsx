import { useEffect, useRef, useState } from "react";
import { fill, t as tr, visitorLang } from "../l10n";
import { api, getBase, type Avatar, type Briefing, type DialerPosture,
         type Escalated, type MyPerson } from "../api";
import { Briefcase } from "../Briefcase";
import { Refusal } from "../Refusal";
import { openTheEar, plainVoice, speakInPieces } from "../spoken";
import { TalkRail } from "../TalkRail";
import { Waveform } from "../Waveform";
import { presenceOf, presenceKey, animatedIn } from "../presence";
import { useSession } from "../store";
import { putAway, whenPutAway } from "../away";
import { canRecord, recordAsked, type Recording } from "../roomear";
import { startWalking } from "../walk";

interface Doc { id: string; name: string | null; url: string;
                ai_marked: boolean }
interface Msg { who: "you" | "assistant"; text: string; note?: string;
                /** A document this turn handed over (qrme/composing.py) —
                 *  the card, never the body. */
                doc?: Doc | null;
                /** Set when the model the owner chose did not answer and
                 *  the local fallback wrote this instead. */
                degradedFrom?: string | null }

/** The designation, over the face it is the designation of.
 *
 * `Avatar.watermark` carries `line` and the type calls it "always displayed,
 * by the product's own rule". This surface showed the face at its largest,
 * talking, and displayed it nowhere — the one screen where a synthetic
 * person is most convincing was the one not saying so.
 *
 *     asked     does the avatar carry a watermark
 *     mattered  does the screen showing the avatar display it
 *
 * Rendered from the server's own line rather than a literal here, so a
 * designation an owner customised reads the same on this screen as on every
 * other, and a deployment that changes the mark changes it once.
 */
function TalkMark({ avatar }: { avatar: Avatar }) {
  const line = avatar.watermark?.line;
  if (!line) return null;
  return <span className="talk-wm">{line}</span>;
}

/** What the engine's error codes mean to somebody looking at the screen.
 *
 * `not-allowed` is not a sentence, and a person who has just been refused a
 * microphone is not the person to hand a spec term to. Anything unrecognised
 * falls through to the general line, which still says the ear closed rather
 * than pretending it drifted shut.
 *
 * Written as a branch per key rather than a lookup table, and that is not
 * style. A table holds its keys as data, so `tr(TABLE[x])` never shows the
 * scanner a literal — the guard that finds strings translated into ten
 * languages and read by nobody reported all four of these, correctly. It was
 * the second time in one round: `chat.talk.stop` and `chat.talk.again` had
 * just been fixed for being assembled the same way, and the repair for them
 * reintroduced it one shape along.
 *
 *     asked     is the key used
 *     mattered  can anything tell that it is used
 */
function earTroubleLine(why: string, lang: ReturnType<typeof visitorLang>): string {
  if (why === "not-allowed" || why === "service-not-allowed") {
    return tr("chat.talk.trouble.blocked", lang);
  }
  if (why === "audio-capture" || why === "start-refused") {
    return tr("chat.talk.trouble.nomic", lang);
  }
  if (why === "network") return tr("chat.talk.trouble.network", lang);
  return tr("chat.talk.trouble", lang);
}

export function Chat({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  // Bringing somebody real into it. `people` is yours-first for the area
  // asked about; `brief` is the whole file, read before anybody is
  // contacted, so declining is still free.
  const [realOpen, setRealOpen] = useState(false);
  const [realArea, setRealArea] = useState("");
  const [people, setPeople] = useState<MyPerson[]>([]);
  const [matter, setMatter] = useState("");
  const [grantToken, setGrantToken] = useState("");
  const [brief, setBrief] = useState<Briefing | null>(null);
  // Shown up front rather than produced mid-conversation: a person should
  // know what this profile can do before anything goes wrong.
  const [dialer, setDialer] = useState<DialerPosture | null>(null);
  const [escalated, setEscalated] = useState<Escalated | null>(null);
  const [said, setSaid] = useState("");
  // `signature_id`, not `envelope_id` — the ceremony returns the signature
  // and that is what arming checks. Same shape the referral form uses.
  const [waiverSig, setWaiverSig] = useState("");
  const lang = visitorLang();
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  // Where you are (spec clause 1): optional context the reply adapts to.
  // Off until opened, empty until filled — nothing is inferred or collected.
  const [whereOpen, setWhereOpen] = useState(false);
  const [location, setLocation] = useState("");
  const [conditions, setConditions] = useState("");
  const [activity, setActivity] = useState("");
  // Spec clauses 2/12: how the profile should work this turn. Empty means
  // "read my prompt and decide", which is what the backend does on its own.
  const [role, setRole] = useState("");
  const [rehearsal, setRehearsal] = useState<{ id: string; scenario: string } | null>(null);
  const [rhScenario, setRhScenario] = useState("");
  const [rhOpen, setRhOpen] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  // The reply mid-play, so leaving the screen can stop it. Navigating
  // away used to leave the bound voice talking with no screen behind it.
  const saying = useRef<{ stop: () => void } | null>(null);
  useEffect(() => () => {
    saying.current?.stop();
    saying.current = null;
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    // Leaving the screen closes the microphone too. This teardown stopped the
    // voice and left the ear open — put-away had its own handler and unmount
    // did not, so navigating away kept a browser tab's recording indicator
    // lit on a screen that was no longer there.
    earTurn.current += 1;
    wantsEar.current = false;
    talkRec.current?.stop();
    talkRec.current = null;
  }, []);
  // Voice: replies read aloud by the device's own engine, and a microphone
  // that fills the composer. Both feature-detected — the mic button simply
  // does not render on a browser without SpeechRecognition, because a
  // control that cannot work is worse than no control.
  // On by default — a profile with a voice is expected to be heard, and
  // the first field report on this screen was one word: silence. The mute
  // is this browser's to keep.
  const [speakOn, setSpeakOn] = useState(
    () => localStorage.getItem("qrme.chat.speak") !== "0");
  // The bound voice mid-utterance — `speechSynthesis.speaking` cannot see
  // an <audio> element, so the face needs its own word for it.
  const [voicing, setVoicing] = useState(false);
  // TS's DOM lib does not ship SpeechRecognition types; the constructor is
  // feature-detected and driven through the three members every engine has.
  const Recognition: (new () => any) | undefined =
    (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;
  const [listening, setListening] = useState(false);
  // The live recogniser, so the page being put away can put it down. It had
  // no handle at all: the overlay relied on `onend` firing to drop the
  // light, and a frozen tab is exactly the case where `onend` never comes —
  // so the caption said the profile was listening to a microphone the
  // browser had already stopped.
  const talkRec = useRef<{ stop: () => void } | null>(null);
  // Whether the person still wants the ear open. A ref, not state: `onend`
  // fires from the engine outside React's render, and reading `listening`
  // there would read the value from the render that installed the handler.
  const wantsEar = useRef(false);
  // Which opening of the ear is the live one. Every recognizer closes over
  // its own turn number and does nothing unless it is still that turn.
  //
  //     asked     did this session end
  //     mattered  is this session still the one on screen
  //
  // `wantsEar` is one ref and every recognizer's handlers write to it, so a
  // late event from a superseded session was turning off the ear that had
  // just replaced it — a race that reads exactly like the engine refusing.
  const earTurn = useRef(0);
  /** The composer's dictation, held apart from the overlay's ear: they are
   *  two microphones with two destinations and must not share a handle. */
  const dictRec = useRef<{ stop: () => void } | null>(null);
  const [dictating, setDictating] = useState(false);
  // The recording bar's level history — real readings off a real analyser,
  // newest at the right, the way a voice memo draws itself. An empty array
  // when no analyser could open; the bar then shows its resting dots and
  // the recording still works.
  const [dictLevels, setDictLevels] = useState<number[]>([]);
  const dictMeter = useRef<{ stop: () => void } | null>(null);
  const dictBefore = useRef("");
  // Which dictation is the live one — the overlay's `earTurn`, for the bar.
  // The recorded fallback's words arrive only after the recording stops, so
  // ⏹ must let them land while ✕ must not; a retired turn is how ✕ says so.
  const dictTurn = useRef(0);
  const inputRef = useRef<HTMLInputElement | null>(null);
  // Why the ear closed, when it closed for a reason rather than a silence.
  // A caption that only ever falls back to "tap to talk" cannot tell a
  // refused microphone from a bug, and the person watching it has no way to
  // find out — which is how the first repair of this screen shipped on an
  // assumption with nothing able to contradict it.
  const [earTrouble, setEarTrouble] = useState<string | null>(null);
  // Why the robot voice is standing in, when it is. The fallback used to be
  // silent about its reason — a field report heard "a female robot voice"
  // and could only guess at keys and bindings. The server's refusal names
  // it (no voice bound, no engine key, ceiling), already in the reader's
  // language; showing that sentence turns the guess into a fact.
  const [voiceNote, setVoiceNote] = useState<string | null>(null);
  // The talk surface: a full listening overlay in the sibling product's
  // shape — except this product's speaker has a face. The profile's avatar
  // is what you look at while it listens and answers; the abstract orb only
  // appears when the profile has no portrait yet.
  const [talking, setTalking] = useState(false);
  const [talkAvatar, setTalkAvatar] = useState<Avatar | null>(null);
  /** The name as the product requires it to be shown.
   *
   * `watermark.design()` on the server builds `AI · {name}` and forces the
   * designation in front even of a label an owner customised — "the AI
   * designation is invariant". The console was rendering `display_name`
   * straight, which walks around that rule entirely: the header of a
   * conversation with a synthetic profile read "Chat with David Bianchi"
   * and said nothing about what it was.
   *
   *     asked     does the profile carry a designation
   *     mattered  does the screen naming it use one
   *
   * Falls back to the bare name only where no watermark has loaded yet, so
   * a slow request shows a name rather than an empty header — and never the
   * reverse, which would be the designation arriving after somebody had
   * already read the name without it.
   */
  const shownName = talkAvatar?.watermark?.label
    || session.profile?.display_name;
  const [heard, setHeard] = useState("");
  // Handing your own profile something to read, and changing the face it
  // wears. Both shipped with a door on somebody *else's* homepage and none
  // here — so a person could give a starter they had just met a document,
  // and could not give one to the profile built from their own life.
  const [bcOpen, setBcOpen] = useState(false);
  // The composer's +. Five tools lived as full-size buttons in the bar and
  // the text box paid for it — the field report could not even see it. The
  // mic, the box and Send stay; everything else folds here.
  const [plusOpen, setPlusOpen] = useState(false);
  const [talkPlus, setTalkPlus] = useState(false);
  // The camera. A photograph goes into the briefcase rather than into a
  // route of its own — the briefcase is already the place material handed to
  // a profile lives, already says plainly that this deployment cannot see a
  // picture, and already scopes what you hand over to the two of you.
  const camRef = useRef<HTMLInputElement | null>(null);
  // The camera carries `capture`, which is what makes a phone open the lens.
  // These three deliberately do not: a picture already taken, a video, and
  // anything else are chosen from the device. All four land in the same
  // place — `shoot` imports whatever it is given.
  const libRef = useRef<HTMLInputElement | null>(null);
  const vidRef = useRef<HTMLInputElement | null>(null);
  const docRef = useRef<HTMLInputElement | null>(null);
  const [shooting, setShooting] = useState(false);
  const shoot = (file: File) => {
    if (!session.profileId || !session.interactorId) return;
    setShooting(true);
    api.importFile(session.profileId, session.interactorId, file,
                   tr("chat.camera.note", lang))
      .then(() => setBcOpen(true))   // land where it went, not nowhere
      .catch(setError)
      .finally(() => setShooting(false));
  };

  // What the conversation is doing, decided once. Before this the surface
  // had `listening` and used it for the pulse, the caption, and nothing
  // else — a profile that was thinking, speaking, or had just failed looked
  // identical to one sitting idle. `presence.ts` was written for this and
  // then nothing imported it, which is a module with no door.
  const presence = presenceOf({
    listening,
    awaiting: busy,
    // Two mouths, one face: the device recogniser reports through
    // `speechSynthesis.speaking`, the bound voice through `voicing`.
    speaking: (speakOn && !!window.speechSynthesis?.speaking) || voicing,
    working: shooting,
    failed: !!error,
  });

  // The conversation follows itself. The previous version scrolled from
  // `finally` inside a requestAnimationFrame, which can fire before React
  // commits the reply bubble — it measured yesterday's scrollHeight and the
  // newest message sat below the fold until the reader dragged it up. An
  // effect runs after the commit, so it sees the bubble it is scrolling to;
  // keying on busy too means the thinking indicator is followed as well.
  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [msgs, busy]);

  // Loaded on mount so the talk overlay opens with the face (or torso)
  // already in hand instead of flashing the placeholder.
  useEffect(() => {
    if (!session.profileId) return;
    api.avatar(session.profileId, session.ownerToken || "")
      .then(setTalkAvatar).catch(() => setTalkAvatar(null));
  }, [session.profileId, session.ownerToken]);

  async function speakAloud(text: string) {
    // The profile's own bound voice first — the person made it, bound it,
    // and this is the screen where the profile talks back; hearing the
    // browser's robot here was the binding not reaching the conversation.
    // The device's voice stands in when there is no binding, no engine, or
    // the reply outruns the synthesis ceiling.
    const token = session.ownerToken || session.interactorToken;
    if (session.profileId && token) {
      try {
        // Piece by piece: the first sentence plays while the rest is
        // still being synthesised — the talking face lights when the
        // first word is heard, not when the whole reply is rendered.
        const s = await speakInPieces(session.profileId, text, token);
        saying.current = s;
        setVoicing(true);
        void s.done.then(() => {
          if (saying.current === s) saying.current = null;
          setVoicing(false);
        });
        return;
      } catch (e) {
        // The device's voice stands in — and says why, on screen. A
        // rejection carries the server's own sentence when the door
        // refused (no binding, no engine key), and the platform's when
        // playback was refused; either way the person hearing the robot
        // now reads the reason instead of guessing at keys.
        setVoicing(false);
        const why = (e as { message?: string })?.message;
        if (why) setVoiceNote(why);
      }
    }
    if (!("speechSynthesis" in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang;
    window.speechSynthesis.speak(u);
  }

  // The watermark is needed by the header, not only by the talk overlay, so
  // it is fetched when the conversation opens. A designation that arrives
  // only once somebody presses the microphone is a designation most readers
  // never see.
  useEffect(() => {
    if (!session.profileId) return;
    api.avatar(session.profileId, session.ownerToken || "")
      .then(setTalkAvatar).catch(() => setTalkAvatar(null));
  }, [session.profileId]);

  function openTalk() {
    setTalking(true);
    setHeard("");
    talkListen();
  }

  // Listen → send → speak the reply → listen again, until closed. The
  // transcript is shown while it is being heard, so the surface never
  // swallows words silently.
  function talkListen() {
    if (!Recognition || putAway()) return;
    // The playback grant is taken here, inside the press, so the reply's
    // bound voice can play on platforms that gate audio behind a gesture.
    openTheEar();
    // An ear that is already open must not be opened again. Chrome allows
    // one recognition at a time, and starting a second aborts the first —
    // whose `aborted` then arrived and closed the one that had just opened.
    // Pressing the button while it was listening did exactly this.
    if (talkRec.current) return;
    const mine = ++earTurn.current;
    const live = () => mine === earTurn.current;
    setEarTrouble(null);
    const rec = new Recognition();
    rec.lang = lang;
    // `continuous` defaults to **false**, and that was the whole defect: the
    // engine is specified to stop after the first utterance, so the ear shut
    // itself about a second in and the caption fell back to "tap to talk"
    // while somebody was still speaking. The room's dictation has set it
    // since it was written; this screen was a worse copy of a listener that
    // already worked here.
    rec.continuous = true;
    // Words appear as they are said rather than only when a phrase settles,
    // so the surface never looks deaf while it is hearing.
    rec.interimResults = true;
    let settled = "";
    let seen = 0;
    rec.onresult = (e: any) => {
      // A continuous session hands back a growing list. Reading
      // `results[0][0]` took the first phrase and only ever the first, so a
      // second sentence replaced nothing and was lost.
      let live = "";
      for (let i = seen; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) {
          const said = String(r[0].transcript).trim();
          if (said) settled += (settled ? " " : "") + said;
          seen = i + 1;
        } else {
          live += r[0].transcript;
        }
      }
      const text = (settled + (live ? " " + live : "")).trim();
      setHeard(text);
      setInput(text);
    };
    rec.onend = () => {
      if (!live()) return;
      talkRec.current = null;
      // Chrome ends the session on its own silence timeout even when
      // continuous, so an ear meant to stay open has to be reopened. Only
      // while the person still wants it and the screen has not been put
      // away — a press is not a thing to replay on somebody's behalf.
      if (wantsEar.current && !putAway()) { talkListen(); return; }
      wantsEar.current = false;
      setListening(false);
    };
    rec.onerror = (e: any) => {
      if (!live()) return;
      const why = String(e?.error || "");
      // Neither of these is a fault. `no-speech` is a quiet room, and
      // `aborted` is what the engine reports when a session is superseded
      // or stopped on purpose — treating it as fatal is what made the ear
      // close a fifth of a second after it opened.
      if ((why === "no-speech" || why === "aborted")
          && wantsEar.current && !putAway()) return;
      // The faults this console can route around. `network` is the
      // recogniser's speech service unreachable — the handheld's report.
      // `service-not-allowed` and `not-allowed` are iPhones refusing
      // Apple's own recogniser while the microphone permission reads
      // Allow — the field report was a person staring at Safari's own
      // settings saying Allow while this screen told them to go allow it.
      // The recorded ear answers all three, and it is self-correcting: if
      // the person truly blocked the microphone, the recording fails at
      // getUserMedia and says so honestly.
      if ((why === "network" || why === "service-not-allowed"
           || why === "not-allowed")
          && canRecord() && session.interactorId) {
        talkRec.current = null;
        void talkRecord(settled);
        return;
      }
      // Anything else closes the ear, and says so. Falling silently back to
      // "tap to talk" left the person and the next person to read this
      // screen with the same nothing to go on.
      wantsEar.current = false;
      talkRec.current = null;
      setListening(false);
      if (why && why !== "aborted") setEarTrouble(why);
    };
    talkRec.current = { stop: () => rec.stop() };
    wantsEar.current = true;
    setListening(true);
    // `start()` throws where the engine refuses outright — no microphone
    // bound, or a session the browser will not grant. Unhandled, the ear
    // was left reading as open over a recognizer that never began.
    try {
      rec.start();
    } catch {
      wantsEar.current = false;
      talkRec.current = null;
      setListening(false);
      setEarTrouble("start-refused");
    }
  }

  /** The overlay's recorded ear: the browser's recogniser exists but cannot
   *  reach its speech service, so this console records the turn itself and
   *  the deployment's ears transcribe it (`/interactors/{id}/heard`).
   *  Silence ends a turn exactly as the room's ear decided it should, the
   *  transcript grows across turns the way the recogniser's did, and every
   *  existing stop — ✕, put-away, unmount — still works, because the
   *  recording sits behind the same `talkRec` handle.
   *
   *      asked     can this browser reach a transcriber
   *      mattered  does the conversation still happen when it cannot */
  async function talkRecord(prior: string) {
    if (putAway() || !session.interactorId) return;
    const mine = ++earTurn.current;
    const live = () => mine === earTurn.current;
    setEarTrouble(null);
    wantsEar.current = true;
    setListening(true);
    let recording: Recording;
    try {
      recording = await recordAsked(
        session.interactorId, session.interactorToken || "");
    } catch {
      if (!live()) return;
      wantsEar.current = false;
      setListening(false);
      setEarTrouble("start-refused");
      return;
    }
    if (!live()) { recording.stop(); return; }
    talkRec.current = { stop: () => recording.stop() };
    try {
      const said = await recording.done;
      if (!live()) return;
      talkRec.current = null;
      const text = (prior ? prior + " " : "") + said;
      setHeard(text);
      setInput(text);
      if (wantsEar.current && !putAway()) { void talkRecord(text); return; }
      setListening(false);
    } catch (e) {
      if (!live()) return;
      talkRec.current = null;
      // "nothing was heard in that" is a quiet stretch, not a fault —
      // listen again, the recogniser's own posture for `no-speech`.
      if (wantsEar.current && !putAway()
          && String((e as Error)?.message || "").startsWith("nothing")) {
        void talkRecord(prior);
        return;
      }
      wantsEar.current = false;
      setListening(false);
      setEarTrouble(String((e as Error)?.message || "trouble"));
    }
  }

  /** The microphone beside the composer: speech into the text bar, and
   *  nothing else.
   *
   * It used to open the talk overlay, which meant the two voice controls on
   * this screen did the same thing and neither did dictation — there was no
   * way to speak a message and then edit it before sending. They are
   * different jobs: this one fills a field somebody is looking at, the wave
   * beside Send hands the whole conversation over to voice.
   *
   *     asked     does the microphone open
   *     mattered  where do the words it hears go
   */
  /** A real meter behind the recording bar. Its own stream beside the
   *  recogniser's — refusal is harmless: the bars rest and the words
   *  still arrive, the same posture the room's ear takes. */
  async function startDictMeter() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const w = window as unknown as {
        AudioContext?: typeof AudioContext;
        webkitAudioContext?: typeof AudioContext;
      };
      const Ctx = w.AudioContext ?? w.webkitAudioContext;
      if (!Ctx) { stream.getTracks().forEach((t) => t.stop()); return; }
      const ctx = new Ctx();
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 1024;
      ctx.createMediaStreamSource(stream).connect(analyser);
      const wave = new Uint8Array(analyser.fftSize);
      const tick = window.setInterval(() => {
        analyser.getByteTimeDomainData(wave);
        let peak = 0;
        for (let i = 0; i < wave.length; i++) {
          const dev = Math.abs(wave[i] - 128);
          if (dev > peak) peak = dev;
        }
        const level = Math.min(1, peak / 40);
        setDictLevels((l) => [...l.slice(-46), level]);
      }, 90);
      dictMeter.current = {
        stop: () => {
          window.clearInterval(tick);
          stream.getTracks().forEach((t) => t.stop());
          void ctx.close().catch(() => {});
        },
      };
    } catch { /* no meter is not no recording */ }
  }

  function stopDictMeter() {
    dictMeter.current?.stop();
    dictMeter.current = null;
  }

  /** The ✕ on the recording bar: close the ear and put the field back the
   *  way it was — a cancelled recording leaves no words behind. */
  function dictCancel() {
    // Retire the turn before the stop: a recorded fallback's words arrive
    // only after the recording ends, and a cancelled bar must not have
    // them land in the field it just restored.
    dictTurn.current += 1;
    const rec = dictRec.current;
    dictRec.current = null;
    setDictating(false);
    stopDictMeter();
    rec?.stop();
    setInput(dictBefore.current);
  }

  function dictate() {
    if (!Recognition) return;
    openTheEar();
    if (dictRec.current) { dictStop(); return; }
    // A fresh press is a fresh turn: words from any earlier recording that
    // is still resolving belong to it, not to this one.
    dictTurn.current += 1;
    // Deliberately no focus() here: on a touch device focusing the input
    // summons the on-screen keyboard, and the person asked to speak, not to
    // type. The bar shows the recording; the keyboard comes only from a
    // tap into the field itself.
    const rec = new Recognition();
    rec.lang = lang;
    rec.continuous = true;
    rec.interimResults = true;
    const before = input;
    dictBefore.current = input;
    setDictLevels([]);
    void startDictMeter();
    let settled = "";
    let seen = 0;
    const handle = { stop: () => rec.stop() };
    rec.onresult = (e: any) => {
      if (dictRec.current !== handle) return;
      let live = "";
      for (let i = seen; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) {
          const said = String(r[0].transcript).trim();
          if (said) settled += (settled ? " " : "") + said;
          seen = i + 1;
        } else {
          live += r[0].transcript;
        }
      }
      const heardNow = (settled + (live ? " " + live : "")).trim();
      setInput((before ? before + " " : "") + heardNow);
    };
    rec.onend = () => {
      dictRec.current = null; setDictating(false); stopDictMeter();
    };
    rec.onerror = (e: any) => {
      const why = String(e?.error || "");
      if (why === "no-speech" || why === "aborted") return;
      // Same route-around as the overlay's, and for the same three codes:
      // an unreachable speech service — or an iPhone refusing its own
      // recogniser under `not-allowed`/`service-not-allowed` while the
      // microphone permission reads Allow — hands the bar to the recorded
      // ear. The meter restarts inside it, fed by the recording's own
      // analyser.
      if ((why === "network" || why === "service-not-allowed"
           || why === "not-allowed")
          && canRecord() && session.interactorId) {
        stopDictMeter();
        void dictRecord();
        return;
      }
      dictRec.current = null;
      setDictating(false);
      setEarTrouble(why || "start-refused");
    };
    dictRec.current = handle;
    setDictating(true);
    try {
      rec.start();
    } catch {
      dictRec.current = null;
      setDictating(false);
      setEarTrouble("start-refused");
    }
  }

  function dictStop() {
    const rec = dictRec.current;
    dictRec.current = null;
    setDictating(false);
    stopDictMeter();
    rec?.stop();
  }

  /** The recording bar over the deployment's ears — dictation's version of
   *  the overlay's fallback. The bar looks and works exactly as it did:
   *  the meter draws from the recording's own analyser, ⏹ (or 2.5s of
   *  silence) ends the recording and the words land in the field, and ✕
   *  cancels clean. The words arrive only after the recording stops, which
   *  is why ⏹ leaves the turn standing and ✕ retires it. */
  async function dictRecord() {
    if (!session.interactorId) return;
    const mine = ++dictTurn.current;
    const before = dictBefore.current;
    setDictLevels([]);
    let recording: Recording;
    try {
      recording = await recordAsked(
        session.interactorId, session.interactorToken || "",
        (level) => setDictLevels((l) => [...l.slice(-46), level]));
    } catch {
      dictRec.current = null;
      setDictating(false);
      setEarTrouble("start-refused");
      return;
    }
    if (mine !== dictTurn.current) { recording.stop(); return; }
    dictRec.current = { stop: () => recording.stop() };
    setDictating(true);
    try {
      const said = await recording.done;
      if (mine !== dictTurn.current) return;
      dictRec.current = null;
      setDictating(false);
      setInput((before ? before + " " : "") + said);
    } catch (e) {
      if (mine !== dictTurn.current) return;
      dictRec.current = null;
      setDictating(false);
      // A recording nobody spoke into leaves the field alone, quietly —
      // the recogniser's own posture for `no-speech`.
      if (!String((e as Error)?.message || "").startsWith("nothing")) {
        setEarTrouble(String((e as Error)?.message || "trouble"));
      }
    }
  }

  /** The caption says "tap to talk", so the face and the caption are the
   * tap targets — not only the buttons under them. */
  function tapTalk() {
    if (!listening && !busy) talkListen();
  }

  /** Close the ear because the person asked, not because it timed out. */
  function talkStop() {
    // Retire the turn first: the `aborted` this stop provokes then belongs
    // to a session nobody is listening to, and cannot reopen or report.
    earTurn.current += 1;
    wantsEar.current = false;
    const rec = talkRec.current;
    talkRec.current = null;
    setListening(false);
    setEarTrouble(null);
    rec?.stop();
  }

  // Put away mid-listen: the microphone goes down and the caption with it.
  // Nothing stands back up here — this overlay listens one turn at a time,
  // started by a press, and a press is not a thing to replay on somebody's
  // behalf when they come back.
  useEffect(() => whenPutAway(() => {
    earTurn.current += 1;
    wantsEar.current = false;
    talkRec.current?.stop();
    talkRec.current = null;
    setListening(false);
  }), []);

  async function send() {
    const message = input.trim();
    if (!message || !session.profileId || !session.interactorId) return;
    // Send is the press the spoken reply will ride on.
    if (speakOn || talking) openTheEar();
    setInput("");
    setError(null);
    setMsgs((m) => [...m, { who: "you", text: message }]);
    setBusy(true);
    const environment =
      whereOpen && (location.trim() || conditions.trim() || activity.trim())
        ? {
            ...(location.trim() && { location: location.trim() }),
            ...(conditions.trim() && { conditions: conditions.trim() }),
            ...(activity.trim() && { activity: activity.trim() }),
            local_time: new Date().toTimeString().slice(0, 5),
          }
        : undefined;
    // An open rehearsal room takes the turn: the reply comes back marked
    // for what it is, and nothing lands in the remembered conversation.
    if (rehearsal) {
      try {
        const turn = await api.rehearse(
          session.profileId, rehearsal.id, message);
        setMsgs((m) => [...m, {
          who: "assistant", text: turn.reply,
          note: "🎭 " + rehearsal.scenario }]);
      } catch (e) { setError(e); }
      finally { setBusy(false); }
      return;
    }
    try {
      const reply = await api.chat(session.profileId, {
        interactor_id: session.interactorId,
        message,
        environment,
        // Spec clauses 2/12: ask the profile to work as an advisor,
        // collaborator or operator. Left on "read the prompt" the profile
        // decides for itself and the reply says which it chose.
        role: role || undefined,
      });
      const pm = reply.profile_message;
      const rc = reply.role_context;
      // Takes the sentence, not the key. Passing the key would put the
      // literal after `put(` instead of after `tr(`, where the dead-key
      // guard looks — four live keys would have read as dead.
      const put = (line: string, values: Record<string, string>) =>
        Object.entries(values).reduce(
          (out, [k, v]) => out.replace(`{${k}}`, v), line);
      const note = reply.handoff?.state
        ? put(tr("chat.handoff", lang), { state: reply.handoff.state })
        : pm.status !== "approved"
          ? pm.flag_reason
            ? put(tr("chat.moderated.why", lang),
                  { status: pm.status, why: pm.flag_reason })
            : put(tr("chat.moderated", lang), { status: pm.status })
          : rc
            ? put(tr("chat.workedas", lang), { role: rc.role, how: rc.how })
            : reply.environment
              ? tr("chat.adapted", lang)
              : undefined;
      const text = pm.status === "approved"
        ? pm.content
        : tr("chat.held", lang);
      // Who actually wrote it. Canned fallback text presented as the chosen
      // model is a lie the reader has no way to detect from the words alone —
      // the sibling product's Coach screen has said so in amber for releases.
      const degradedFrom = reply.provenance?.degraded_from ?? null;
      // What the turn handed over, if it handed anything over.
      const doc = (pm as { document?: Doc | null }).document ?? null;
      setMsgs((m) => [...m, { who: "assistant", text, note, degradedFrom,
                              doc }]);
      if ((speakOn || talking) && pm.status === "approved") speakAloud(text);
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="screen chat">
      <header className="screen-head chat-head">
        {/* The face belongs beside the name — the same portrait the talk
            overlay stands at full height, at header scale. Decorative here:
            the h2 already says who this is, so a reader hears it once. */}
        {talkAvatar?.asset && !talkAvatar.placeholder && (
          <img className="chat-head-face"
               src={talkAvatar.asset.startsWith("http")
                      ? talkAvatar.asset
                      : getBase() + talkAvatar.asset}
               alt="" aria-hidden="true" />
        )}
        <div className="chat-head-words">
          <h2>
            {fill(tr("chat.with", lang), { name: shownName })}
          </h2>
          <span className="muted small">{tr("chat.pitch", lang)}</span>
        </div>
      </header>

      {/* role=log + aria-live: a screen reader is told when the reply
          arrives, instead of the conversation advancing silently. */}
      {/* The presence bubbles and the receding-grid backdrop stood here
          for one release and came back out on a field report: the names
          and portraits floated over the words people were trying to
          read. Presence rendering belongs to the rooms and the
          vastscape, where there is a scene to stand in — a text thread
          is its own scene. */}
      <div className="messages" role="log" aria-live="polite"
           ref={listRef}>
        {msgs.length === 0 && (
          <div className="muted center">
            {fill(tr("chat.sayhello", lang), { name: shownName })}
          </div>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={"bubble " + m.who}>
            {m.text}
            {/* A document, as a card you can open and keep — the whole
              * point of the round: "how am I supposed to receive it and
              * how does it render on the screen?" The AI mark rides on it
              * because a composed document is synthetic media, which is
              * the mirror of a person's own photograph never being
              * marked. */}
            {m.doc && (
              <a className="bubble-doc" href={getBase() + m.doc.url}
                 target="_blank" rel="noreferrer" download={m.doc.name ?? true}>
                <span className="bubble-doc-icon" aria-hidden="true">📄</span>
                <span className="bubble-doc-name">
                  {m.doc.name || tr("chat.doc", lang)}
                </span>
                {m.doc.ai_marked && (
                  <span className="bubble-doc-ai">{tr("chat.doc.ai", lang)}</span>
                )}
              </a>
            )}
            {m.note && <div className="bubble-note">{m.note}</div>}
            {m.degradedFrom && (
              <div className="degraded">
                ⚠ {tr("chat.degraded.head", lang)}{" "}
                {m.degradedFrom} {tr("chat.degraded.tail", lang)}
              </div>
            )}
          </div>
        ))}
        {busy && <div className="bubble assistant thinking">…</div>}
      </div>

      <Refusal error={error} onPlans={onPlans} variant="inline" />

      {/* Spec clauses 2/12 — advisor counsels, collaborator co-creates,
          operator executes. "Let it read my prompt" is the honest default:
          the profile infers from the wording and the reply says which. */}
      <label className="role-pick">{tr("chat.rolepick", lang)}
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="">{tr("chat.role.read", lang)}</option>
          <option value="advisor">{tr("chat.role.advisor", lang)}</option>
          <option value="collaborator">{tr("chat.role.collaborator", lang)}</option>
          <option value="operator">{tr("chat.role.operator", lang)}</option>
        </select>
      </label>

      {/* Both doors still exist and neither is on the screen by default.
          They are the escalation to emergency services and the handoff to a
          real person: safety paths, and safety paths are not a thing to
          delete for room. Folded into one line instead, closed until asked
          for — which is what "make them smaller or put them somewhere else"
          leaves standing.

              asked     is the chat screen clear
              mattered  are the doors still there */}
      <details className="chat-doors">
        <summary className="muted small">{tr("chat.doors", lang)}</summary>
      {/* --- what this profile can do, before anything goes wrong ------- */}
      <div className="card">
        <h3>{tr("esc.hdr", lang)}</h3>
        <p className="muted small">{tr("esc.pitch", lang)}</p>
        {!dialer
          ? <button className="ghost" onClick={() => {
              api.dialerPosture(session.interactorId || "",
                                session.interactorToken || "")
                .then(setDialer).catch(setError);
            }}>{tr("esc.show", lang)}</button>
          : (<>
              {/* The words, readable before anybody signs anything. */}
              <p className="small">{dialer.waiver}</p>
              <p className="muted small">
                {dialer.armed ? tr("esc.armed", lang) : tr("esc.notarmed", lang)}
              </p>
              {/* Said now, not discovered at the worst moment. */}
              {dialer.sealed && (
                <p className="small">
                  {fill(tr("esc.sealed", lang), { number: dialer.call_yourself })}
                </p>
              )}
              {!dialer.armed && (
                <>
                  <input value={waiverSig}
                         placeholder={tr("esc.sig.ph", lang)}
                         onChange={(e) => setWaiverSig(e.target.value)} />
                  <button className="ghost" disabled={!waiverSig} onClick={() => {
                    setError(null);
                    api.armDialer(session.interactorId || "", waiverSig,
                                  session.interactorToken || "")
                      .then(setDialer).catch(setError);
                  }}>{tr("esc.arm", lang)}</button>
                </>
              )}
              <button className="ghost" disabled={!matter} onClick={() => {
                setError(null);
                api.cannotResolve(session.profileId || "",
                                  { interactor_id: session.interactorId || "",
                                    matter },
                                  session.interactorToken || "")
                  .then(setEscalated).catch(setError);
              }}>{tr("esc.raise", lang)}</button>
              {escalated && (
                <button onClick={() => {
                  setError(null); setSaid("");
                  api.dialEmergency(escalated.id, session.interactorId || "",
                                    session.interactorToken || "")
                    .then(() => setSaid(tr("esc.placed", lang)))
                    .catch(setError);
                }}>{tr("esc.press", lang)}</button>
              )}
              <button className="ghost" onClick={() => {
                api.myEscalations(session.interactorId || "",
                                  session.interactorToken || "")
                  .then((rows) => setSaid(rows.length === 0
                    ? tr("esc.none", lang)
                    : rows.map((r) => `${r.matter} · ` + (r.placed
                        ? tr("esc.was.placed", lang)
                        : tr("esc.was.not", lang))).join("\n")))
                  .catch(setError);
              }}>{tr("esc.past", lang)}</button>
              {said && <p className="small">{said}</p>}
            </>)}
      </div>

      {/* --- bringing somebody real into it ---------------------------- */}
      <div className="card">
        <h3>{tr("real.hdr", lang)}</h3>
        <p className="muted small">{tr("real.pitch", lang)}</p>
        {!realOpen
          ? <button className="ghost" onClick={() => {
              setRealOpen(true);
              // Yours first, before any area is typed: that is what keeping
              // them was for.
              api.myPeople(session.interactorId || "",
                           session.interactorToken || "")
                .then(setPeople).catch(() => setPeople([]));
            }}>
              {tr("real.open", lang)}
            </button>
          : (<>
              <input value={realArea} placeholder={tr("real.area.ph", lang)}
                     onChange={(e) => setRealArea(e.target.value)} />
              <button disabled={!realArea} onClick={() => {
                setError(null);
                api.peopleForArea(session.interactorId || "", realArea,
                                  session.interactorToken || "")
                  .then(setPeople).catch(setError);
              }}>{tr("real.find", lang)}</button>
              {people.map((p) => (
                <div key={p.provider_id}>
                  <p className="small">
                    <b>{p.name}</b>{" · "}{p.area}
                    {p.location ? ` · ${p.location}` : ""}
                    {" · "}
                    {/* Yours and found-for-you are different claims. */}
                    {p.yours ? tr("real.yours", lang) : tr("real.found", lang)}
                    {p.preferred ? ` · ${tr("real.first", lang)}` : ""}
                  </p>
                  {p.yours
                    ? (<>
                        {!p.preferred && (
                          <button className="ghost" onClick={() => {
                            api.preferPerson(session.interactorId || "",
                                             p.provider_id,
                                             session.interactorToken || "")
                              .then(() => setPeople([])).catch(setError);
                          }}>{tr("real.prefer", lang)}</button>
                        )}
                        <button className="ghost" onClick={() => {
                          api.dropPerson(session.interactorId || "",
                                         p.provider_id,
                                         session.interactorToken || "")
                            .then(() => setPeople([])).catch(setError);
                        }}>{tr("real.drop", lang)}</button>
                      </>)
                    : <button className="ghost" onClick={() => {
                        api.keepPerson(session.interactorId || "",
                                       { provider_id: p.provider_id },
                                       session.interactorToken || "")
                          .then(() => setPeople([])).catch(setError);
                      }}>{tr("real.keep", lang)}</button>}
                </div>
              ))}
              <input value={matter} placeholder={tr("real.matter.ph", lang)}
                     onChange={(e) => setMatter(e.target.value)} />
              <input value={grantToken} type="password"
                     placeholder={tr("real.grant.ph", lang)}
                     onChange={(e) => setGrantToken(e.target.value)} />
              {people.filter((p) => p.yours).map((p) => (
                <button key={p.provider_id} className="ghost"
                        disabled={!matter || !grantToken}
                        onClick={() => {
                          setError(null); setBrief(null);
                          api.previewBriefing({
                            interactor_id: session.interactorId || "",
                            profile_id: session.profileId || "",
                            provider_id: p.provider_id, matter,
                            grant_token: grantToken,
                          }, session.interactorToken || "")
                            .then(setBrief).catch(setError);
                        }}>
                  {fill(tr("real.preview", lang), { name: p.name })}
                </button>
              ))}
              {brief && (
                <div>
                  {/* Read before anybody is contacted, counted out loud. */}
                  <p className="small">{brief.reads}</p>
                  {brief.package.attachments.map((a, i) => (
                    <p className="muted small" key={i}>
                      {a.kind} · {a.title}
                      {a.sealed ? ` · ${tr("real.sealed", lang)}` : ""}
                    </p>
                  ))}
                </div>
              )}
            </>)}
      </div>
      </details>


      {whereOpen && (
        <div className="row" style={{ padding: "4px 0" }}>
          <label>{tr("chat.where", lang)}<input value={location}
                             placeholder={tr("chat.where.ph", lang)}
                             onChange={(e) => setLocation(e.target.value)} /></label>
          <label>{tr("chat.conditions", lang)}<input value={conditions}
                                  placeholder={tr("chat.conditions.ph", lang)}
                                  onChange={(e) => setConditions(e.target.value)} /></label>
          <label>{tr("chat.doing", lang)}<input value={activity}
                             placeholder={tr("chat.doing.ph", lang)}
                             onChange={(e) => setActivity(e.target.value)} /></label>
        </div>
      )}

      {talking && (
        <div className="talk-overlay" role="dialog"
             aria-label={tr("chat.talk", lang)}>
          <button className="talk-close" onClick={() => {
            setTalking(false); window.speechSynthesis?.cancel();
          }}>×</button>
          {/* The torso form stands at full figure where there is one; the
              circular face is next; the orb is only for a profile with no
              portrait at all. */}
          {talkAvatar?.torso ? (
            <div className={"talk-torso-wrap talk-tap"
                            + (animatedIn(presence) ? " listening" : "")}
                 onClick={tapTalk}>
              <img className={"talk-torso"
                              + (animatedIn(presence) ? " listening" : "")}
                   src={talkAvatar.torso.startsWith("http")
                          ? talkAvatar.torso
                          : getBase() + talkAvatar.torso}
                   alt={session.profile?.display_name || ""} />
              <TalkMark avatar={talkAvatar} />
            </div>
          ) : talkAvatar?.asset ? (
            /* The face, or the empty frame — `render()` decides which, and
               `placeholder` only says how to caption it. This branch used to
               fall through to an abstract orb whenever the asset was a
               placeholder, which made every portrait-less profile look
               identical to every other and looked like a thing rather than
               like something to fill. */
            <div className={"talk-face talk-tap"
                            + (animatedIn(presence) ? " listening" : "")
                            + (talkAvatar.placeholder ? " empty" : "")}
                 onClick={tapTalk}>
              <img src={talkAvatar.asset.startsWith("http")
                          ? talkAvatar.asset
                          : getBase() + talkAvatar.asset}
                   alt={session.profile?.display_name || ""} />
              <TalkMark avatar={talkAvatar} />
            </div>
          ) : null}
          <div className="talk-name">{shownName}</div>
          {/* Seven states rather than two, and the strip below reads from the
              same decision — so the caption and the bars cannot disagree
              about what is happening. */}
          <div className="talk-state muted small" onClick={tapTalk}>
            {(earTrouble && earTroubleLine(earTrouble, lang))
              || tr(presenceKey(presence), lang)}
          </div>
          <Waveform presence={presence} lang={lang} />
          {heard && <div className="talk-heard">{heard}</div>}
          {talkAvatar && (!talkAvatar.asset || talkAvatar.placeholder) && (
            <div className="muted small">{tr("chat.talk.noface", lang)}</div>
          )}
          <div className="row talk-actions" style={{ justifyContent: "center" }}>
            {/* One control, both directions. While it was only "Speak
                again" there was no way to close an ear that had opened, and
                no way to tell from the button that it was open. */}
            {/* The share menu opens leftward of the talk control rather than
                past the send button, which is where the row ran out of room
                on a phone. */}
            <button className="agent-plusbtn" aria-label={tr("agent.plus", lang)}
                    aria-expanded={talkPlus}
                    onClick={() => setTalkPlus((o) => !o)}>+</button>
            <button className={listening ? "" : "primary"}
                    onClick={listening ? talkStop : talkListen}>
              {listening ? tr("chat.talk.stop", lang) : tr("chat.talk.again", lang)}
            </button>
            <button className="primary" disabled={busy || !input.trim()}
                    onClick={() => { setHeard(""); send(); }}>
              {tr("chat.send", lang)}
            </button>
          </div>
          {talkPlus && (
            <div className="agent-plus talk-plus" role="menu">
              <button role="menuitem"
                      disabled={!session.profileId || !session.interactorId}
                      onClick={() => { setTalkPlus(false); libRef.current?.click(); }}>
                🖼️ {tr("chat.share.photo", lang)}
              </button>
              <button role="menuitem"
                      disabled={!session.profileId || !session.interactorId}
                      onClick={() => { setTalkPlus(false); vidRef.current?.click(); }}>
                🎬 {tr("chat.share.video", lang)}
              </button>
              <button role="menuitem"
                      disabled={!session.profileId || !session.interactorId}
                      onClick={() => { setTalkPlus(false); camRef.current?.click(); }}>
                📷 {tr("chat.camera", lang)}
              </button>
              <button role="menuitem"
                      disabled={!session.profileId || !session.interactorId}
                      onClick={() => { setTalkPlus(false); docRef.current?.click(); }}>
                📄 {tr("chat.share.file", lang)}
              </button>
            </div>
          )}
          {/* Who they are, what they hold about you, what you are to each
              other, and how they behave — beside the face rather than three
              screens away from it. */}
          {session.profileId && (
            <TalkRail profileId={session.profileId}
                      interactorId={session.interactorId || null}
                      lang={lang}
                      ownerToken={session.ownerToken || null}
                      interactorToken={session.interactorToken || null}
                      onError={setError} />
          )}
        </div>
      )}

      {/* Rehearsal: practice the hard conversation — the transcript lives
          only in the room, and closing the room wipes it. While a room is
          open, turns go there instead of the remembered conversation. */}
      {rhOpen && (
        <div className="card">
          <h3>{tr("cht.rh", lang)}</h3>
          <p className="muted small">{tr("cht.rh.pitch", lang)}</p>
          {rehearsal ? (
            <div className="row">
              <span className="muted small" style={{ flex: 1 }}>
                🎭 {rehearsal.scenario}
              </span>
              <button className="danger" onClick={async () => {
                if (!session.profileId) return;
                try {
                  await api.closeRehearsal(session.profileId, rehearsal.id);
                } catch { /* the room may already be gone */ }
                setRehearsal(null);
              }}>{tr("cht.rh.close", lang)}</button>
            </div>
          ) : (
            <div className="row">
              <input value={rhScenario}
                     placeholder={tr("cht.rh.scenario.ph", lang)}
                     onChange={(e) => setRhScenario(e.target.value)}
                     style={{ flex: 1 }} />
              <button className="primary"
                      disabled={busy || !rhScenario.trim()}
                      onClick={async () => {
                        if (!session.profileId || !session.interactorId) return;
                        try {
                          const room = await api.openRehearsal(
                            session.profileId, session.interactorId,
                            rhScenario.trim());
                          setRehearsal({ id: room.id, scenario: room.scenario });
                          setRhScenario("");
                        } catch (e) { setError(e); }
                      }}>{tr("cht.rh.open", lang)}</button>
            </div>
          )}
        </div>
      )}

      {bcOpen && session.profileId && session.interactorId && (
        <div className="card">
          <Briefcase profileId={session.profileId}
                     interactorId={session.interactorId}
                     name={session.profile?.display_name || ""}
                     onError={setError} />
        </div>
      )}

      {voiceNote && (
        <div className="voice-note" role="status">
          <span>🔇 {voiceNote}</span>
          <button type="button" aria-label="×"
                  onClick={() => setVoiceNote(null)}>×</button>
        </div>
      )}
      <div className="composer">
        {plusOpen && (
          <div className="agent-plus composer-plus" role="menu">
            <button role="menuitem"
                    onClick={() => { setPlusOpen(false); setBcOpen((o) => !o); }}>
              📎 {tr("prf.bc.heading", lang)}{bcOpen ? " ✓" : ""}
            </button>
            <button role="menuitem"
                    disabled={!session.profileId || !session.interactorId}
                    onClick={() => { setPlusOpen(false); camRef.current?.click(); }}>
              📷 {tr("chat.camera", lang)}
            </button>
            <button role="menuitem"
                    onClick={() => { setPlusOpen(false); setRhOpen((o) => !o); }}>
              🎭 {tr("cht.rh", lang)}{rhOpen || rehearsal ? " ✓" : ""}
            </button>
            <button role="menuitem"
                    onClick={() => { setPlusOpen(false); setWhereOpen((w) => !w); }}>
              📍 {tr("chat.wheretitle", lang)}{whereOpen ? " ✓" : ""}
            </button>
            <button role="menuitem" aria-pressed={speakOn}
                    onClick={() => {
                      setPlusOpen(false);
                      setSpeakOn((v) => {
                        if (v) localStorage.setItem("qrme.chat.speak", "0");
                        else localStorage.removeItem("qrme.chat.speak");
                        return !v;
                      });
                    }}>
              {speakOn ? "🔊" : "🔇"} {tr("chat.speak", lang)}{speakOn ? " ✓" : ""}
            </button>
          </div>
        )}
        <button className="agent-plusbtn" aria-label={tr("agent.plus", lang)}
                aria-expanded={plusOpen}
                onClick={() => setPlusOpen(!plusOpen)}>+</button>
        {/* The camera. `capture="environment"` is what makes a phone open the
            lens rather than the picker — without it this is the paperclip
            again with a different glyph, which is how a camera button ends up
            shipping that never took a photograph. On a desktop browser the
            attribute is ignored and the file chooser opens, which is the
            honest fallback rather than a control that does nothing. */}
        <input ref={libRef} type="file" accept="image/*"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0];
                 e.target.value = "";
                 if (f) shoot(f);
               }} />
        <input ref={vidRef} type="file" accept="video/*"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0];
                 e.target.value = "";
                 if (f) shoot(f);
               }} />
        <input ref={docRef} type="file"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0];
                 e.target.value = "";
                 if (f) shoot(f);
               }} />
        <input ref={camRef} type="file" accept="image/*" capture="environment"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0];
                 e.target.value = "";
                 if (f) shoot(f);
               }} />
        {/* Two microphones, two destinations. This one fills the bar. */}
        {Recognition && (
          <button title={tr("chat.mic", lang)}
                  aria-label={tr("chat.mic", lang)}
                  className={dictating ? "primary" : ""}
                  onClick={dictating ? dictStop : dictate}>🎤</button>
        )}
        {dictating ? (
          /* The bar is the recording, drawn like a voice memo draws
             itself: discard on the left, the levels the analyser actually
             read in the middle, keep on the right. No live input, so the
             on-screen keyboard stays down; the words land in the field
             when the ✓ closes the ear, and only a tap into the field
             summons a keyboard. */
          <div className="chat-recbar" role="group"
               aria-label={tr("chat.rec.live", lang)}>
            <button type="button" className="rec-x"
                    aria-label={tr("chat.rec.cancel", lang)}
                    onClick={dictCancel}>×</button>
            <div className="rec-strip" aria-hidden="true">
              {dictLevels.length === 0 && (
                <span className="rec-bar" style={{ height: "4px" }} />
              )}
              {dictLevels.map((v, i) => (
                <span key={i} className="rec-bar"
                      style={{ height: `${4 + Math.round(v * 18)}px` }} />
              ))}
            </div>
            <button type="button" className="rec-ok"
                    aria-label={tr("chat.rec.stop", lang)}
                    title={tr("chat.rec.stop", lang)}
                    onClick={dictStop}>
              <span className="rec-stopsq" aria-hidden="true" />
            </button>
          </div>
        ) : (
          <input
            ref={inputRef}
            value={input}
            placeholder={tr("chat.type.ph", lang)}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
        )}
        {/* An arrow, not the word: on a phone the spelt-out Send was
            width the input needed more. The name stays for the screen
            reader and the tooltip. */}
        <button className="primary chat-send" onClick={send} disabled={busy}
                aria-label={tr("chat.send", lang)}
                title={tr("chat.send", lang)}>↑</button>
        {/* And this one hands the whole conversation over to voice. It sits
            after Send because it leaves the text surface rather than
            contributing to it — the microphone belongs to the bar, the wave
            belongs to the conversation. */}
        {Recognition && (
          <button title={tr("chat.audio", lang)}
                  aria-label={tr("chat.audio", lang)}
                  className="chat-wave"
                  onClick={openTalk}>🎙️</button>
        )}
        {/* Take it with you. The only control in this console that hands an
            ear to something outliving the screen — so it is a press, it is
            labelled, and the strip it hands to says it is listening. */}
        {Recognition && session.profileId && session.interactorId && (
          <button title={tr("chat.walk", lang)}
                  aria-label={tr("chat.walk", lang)}
                  className="chat-walkbtn"
                  onClick={() => {
                    setTalking(false);
                    window.speechSynthesis?.cancel();
                    const pid = session.profileId || "";
                    const iid = session.interactorId || "";
                    const itok = session.interactorToken || "";
                    // The same token the screen's own voice uses: the
                    // owner's when this is their profile, the interactor's
                    // otherwise. Captured here rather than read inside the
                    // callback, so the walk keeps the identity it started
                    // with even if the session moves on.
                    const vtok = session.ownerToken || itok;
                    startWalking({
                      shownName: shownName || "",
                      lang,
                      // How it hears out there. The browser's recogniser
                      // is ended when the page is put away; a recording is
                      // not, so the strip records and posts the bytes. Only
                      // when this person holds their own token — an ear is
                      // spent on the deployment's transcription, and a
                      // stranger's id is not a way to spend it.
                      ...(iid && itok ? {
                        hears: (audio: Blob) => api.heard(iid, audio, itok),
                      } : {}),
                      // The voice somebody chose, not the browser's own.
                      // The strip shipped with `SpeechSynthesisUtterance`
                      // while this screen had `speakInPieces` two hundred
                      // lines up — a field report heard the robot and
                      // reasonably blamed the voice key, when nothing was
                      // broken except that the strip never asked.
                      //
                      //     asked     did the reply get spoken
                      //     mattered  in whose voice
                      say: async (text: string) => {
                        try {
                          const s = await speakInPieces(pid, text, vtok);
                          await s.done;
                        } catch (e) {
                          // The device's own voice stands in. A rejection
                          // here is no binding, no engine, or a platform
                          // that refused to play — and to a listener all
                          // three are the same event: nothing was said.
                          // The reason lands on the screen's note, so the
                          // robot never stands in unexplained.
                          const why = (e as { message?: string })?.message;
                          if (why) setVoiceNote(why);
                          await plainVoice(text, lang);
                        }
                      },
                      take: async (message) => {
                        const r = await api.chat(pid, {
                          interactor_id: iid, message });
                        // `degraded_from` is the honest half: a profile
                        // whose key expired reads as the model it was set
                        // to unless something says otherwise, and out on
                        // the strip there is no banner to notice.
                        // On the reply, not on the message: the record of
                        // who wrote it belongs to the turn.
                        const prov = r.provenance;
                        return {
                          text: r.profile_message?.content || "",
                          offline: Boolean(prov?.degraded_from)
                                   || prov?.generated_by === "stub",
                        };
                      },
                    });
                  }}>🚶</button>
        )}
      </div>
    </div>
  );
}
