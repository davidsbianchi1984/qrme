import { useEffect, useRef, useState } from "react";
import { api, type AgentTurn, type WebSearchAnswer,
         uploadMedia } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { speakInPieces, type Speaking } from "../spoken";
import { useSession } from "../store";

/**
 * The Agent — the collaborator, with its own front door.
 *
 * The agent that can rebuild your page and write your widgets has existed
 * since the Studio shipped, and the only way to reach it was to open the
 * widget workshop first. So the person who wanted to say *make my page say
 * what I actually do* had to go somewhere about code to find it.
 *
 *     asked     can an agent edit this person's app
 *     mattered  can the person find the agent
 *
 * ## It says what it can touch before it is asked to touch anything
 *
 * `authoring.TOOLS` is a written list and the backend renders it into
 * sentences a person can read rather than tool names a developer would. That
 * roster is on this screen and open by default, because an agent whose reach
 * you discover by watching what it does is one you have to supervise instead
 * of instruct.
 *
 * ## The boundary is drawn on the screen, not learned by being refused
 *
 * The list was eleven rows when this tab shipped — the page, the homepage,
 * the friends list and the widgets — against a screen implying a
 * collaborator for the whole app. A surface that implies a general assistant
 * and then refuses two thirds of what is asked of it teaches people to stop
 * asking, so the roster now covers the profile itself, what it knows, what
 * it shows the world, the wall, the switches, the work and the numbers.
 *
 * What is still out is out for a reason `qrme/authoring.py` states in full:
 * nothing that spends money, ends a profile, claims an identity, settles an
 * objection, moves something in the physical world, or reaches another
 * person's rows. The count is not written here — the screen renders the
 * live list, so a row added in the backend appears without anybody
 * remembering to edit this paragraph.
 */
/** The rail, in the order somebody reaches for them: what it makes, where
 *  that goes, who sees it, and what it is connected to.
 *
 *  A tab id and an icon, and nothing else — the words come from `nav.<id>`,
 *  which is the row the navigation itself reads. A `label` field here would
 *  be a second name for one screen and the way a chip ends up saying one
 *  thing and opening another. */
/** The strip above the composer: things the agent *does*, not places the
 *  menu already goes. A field report put it exactly: the sliders were menu
 *  tabs — twenty destinations the navigation and the + menu carry anyway —
 *  and a launcher pretending to be a toolbar teaches nobody what the agent
 *  is for. Six actions now, each wired to the strongest machinery this
 *  product has today:
 *
 *  - `video` and `image` fill the box with a structured brief (image after
 *    an upload, so the brief carries the real reference). The agent answers
 *    from its roster — and where the engine is not built yet it says so,
 *    which beats a chip that navigates somewhere unrelated;
 *  - `voicemode` toggles spoken replies (and dictation where the browser
 *    has it — iOS Safari does not, so the toggle never depends on it);
 *  - `docs` hands a file to the same upload door media uses and fills the
 *    box with a reading ask;
 *  - `customize` and `widget` fill the box for the two things the roster
 *    is best at: the page and a small tool.
 */
const ACTIONS: { key: string; icon: string }[] = [
  { key: "video", icon: "\u{1F3AC}" },
  { key: "image", icon: "\u{1F5BC}\uFE0F" },
  { key: "voicemode", icon: "\u{1F399}\uFE0F" },
  { key: "docs", icon: "\u{1F4C4}" },
  { key: "customize", icon: "\u{1F3A8}" },
  { key: "widget", icon: "\u{1F9E9}" },
];

/** The composer's `+`. Five entries, each opening a screen that exists.
 *
 *  The shape asked for was Camera, Photos, Files and Plugins, and all of them
 *  have somewhere real to land here: the camera is what is live in a place,
 *  photos are what the wall takes, files are the source material a profile
 *  answers from, and the plug-ins are the outside services it connects to.
 *  Nothing in this menu is a placeholder — a control that opens nothing is
 *  the thing this estate keeps finding and removing.
 *
 *  Plug-ins pointed at `remainder` when this menu shipped, because the
 *  storefront did not exist yet and the miscellany screen was the nearest
 *  true thing. It exists now. */
const PLUS: { id: string; icon: string }[] = [
  { id: "live", icon: "📷" },
  { id: "wall", icon: "🖼" },
  { id: "workshop", icon: "📎" },
  { id: "plugins", icon: "🔌" },
  { id: "assist", icon: "✏️" },
];

/** Three openings for somebody who has the screen and not the sentence —
 *  and each one *does* its thing rather than describing it. Create opens
 *  the picker and the send button publishes; Search runs a real web search
 *  through the keyless door (`/profiles/{id}/search`), which is the one of
 *  the three that works on a deployment with no model configured; Write
 *  fills the box and hands the sentence to the agent, whose strongest
 *  tools are exactly the writing ones. */
const OPENERS: { key: string; icon: string }[] = [
  { key: "agent.open.create", icon: "🎬" },
  { key: "agent.open.search", icon: "🔎" },
  { key: "agent.open.write", icon: "✍\uFE0F" },
];

/** The browser's own recogniser, where there is one. iOS Safari has none,
 *  which is why every path that reaches for this has a keyboard answer. */
type SR = { new(): {
  continuous: boolean; interimResults: boolean; lang: string;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>
                             & { isFinal: boolean }> }) => void) | null;
  onerror: ((e: { error?: string }) => void) | null;
  onend: (() => void) | null; start: () => void; stop: () => void;
} };

function recogniserOf(): SR | undefined {
  const w = window as unknown as {
    SpeechRecognition?: SR; webkitSpeechRecognition?: SR };
  return w.SpeechRecognition || w.webkitSpeechRecognition;
}

/** A conversation nobody has spoken into for two minutes bows out on its
 *  own — the same number JIM's rooms settled on, for the same reason:
 *  long enough to think or step away, short enough that an empty room
 *  does not hold the microphone open all afternoon. */
const CONVERSATION_IDLE_MS = 120_000;

/** A voice waveform, drawn rather than found: no emoji reads as one, and
 *  the button it sits on is the door to the orb. */
function WaveIcon() {
  const bars: [number, number, number][] = [
    [1, 6, 4], [4, 3, 10], [7, 1, 14], [10, 4, 8], [13, 6, 4]];
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
      {bars.map(([x, y, h]) => (
        <rect key={x} x={x} y={y} width="2" height={h} rx="1"
              fill="currentColor" />
      ))}
    </svg>
  );
}

export function Agent({ onPlans, go }: {
  onPlans: () => void;
  /** Open one of the console's existing screens. Ids are `App.tsx`'s tabs;
   *  typed as a string here so this screen does not need the union — the
   *  rail is a list of destinations, not a second definition of them. */
  go: (id: string) => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();

  const [reach, setReach] = useState<
    { can_touch: string[]; available: boolean } | null>(null);
  const [showsReach, setShowsReach] = useState(true);
  const [ask, setAsk] = useState("");
  const [asking, setAsking] = useState(false);
  // The conversation is this screen's, and it is not written down anywhere:
  // leaving the tab is the whole of forgetting it, the same bargain the
  // Studio's own agent makes.
  const [talk, setTalk] = useState<{ role: string; content: string }[]>([]);
  // Voice mode: the reply is spoken. Dictation rides along only where the
  // browser has SpeechRecognition — iOS Safari does not, and a toggle that
  // depended on it would be a dead control on the phone this was asked from.
  const [voiceMode, setVoiceMode] = useState(false);
  // Dictation is the *other* microphone: it types into the box and sends
  // nothing. Separate from the orb on purpose — one press was asked to mean
  // one thing.
  const [dictating, setDictating] = useState(false);
  const [micHint, setMicHint] = useState(false);
  // Why the ear died, when it did. The recogniser had no onerror at all,
  // so a refused microphone or an unreachable speech service fell through
  // to onend — which relit "listening" over a dead microphone, forever.
  // A field report watched exactly that orb. The fault is a sentence now,
  // and a fatal error stops the relight loop instead of feeding it.
  const [earFault, setEarFault] = useState<string | null>(null);
  // "Search the Internet": the composer becomes a search box, the answer is
  // rows with links, and none of it needs a model.
  const [searchMode, setSearchMode] = useState(false);
  const [finds, setFinds] = useState<WebSearchAnswer | null>(null);
  // A picked picture or video, uploaded and waiting for its words. The send
  // button publishes it — the caption is required by the wall's own door,
  // which is the door doing the asking, not this screen.
  const [pending, setPending] = useState<{ id: string; name: string } | null>(
    null);
  const docPicker = useRef<HTMLInputElement>(null);
  const imgPicker = useRef<HTMLInputElement>(null);
  const mediaPicker = useRef<HTMLInputElement>(null);
  const dictation = useRef<{ stop: () => void } | null>(null);
  const askBox = useRef<HTMLInputElement>(null);
  // The browser's own recogniser, where there is one. Held in a ref — it is
  // a live handle like the room camera's MediaStream, not a value to render
  // on. iOS Safari has none: there, voice mode is the orb, spoken replies,
  // and the keyboard's own dictation key into a focused box.
  const recogniser = useRef<{ stop: () => void } | null>(null);
  // The callbacks' view of voice mode. The recogniser's own `onend` and the
  // utterance's `onend` outlive the render that made them, and reading the
  // state there reads a snapshot; these refs read now.
  const voiceOn = useRef(false);
  const lastHeard = useRef(0);
  // A turn in flight — model plus spoken reply. The recogniser also ends
  // when a final result is sent, and that end must not relight the mic
  // over the agent's own voice; the reply's end does the relighting.
  const turning = useRef(false);
  // The reply being spoken, for the orb's label: an orb that says
  // "listening" while the agent talks is the orb lying twice a turn.
  const [saying, setSaying] = useState(false);
  // The bound-voice reply mid-play, so closing the orb can stop it — the
  // same live-handle bargain the recogniser ref makes. A Speaking handle
  // rather than one audio element, because the reply is spoken piece by
  // piece and pausing only the playing piece would let the next one start.
  const playing = useRef<Speaking | null>(null);
  const [did, setDid] = useState<AgentTurn | null>(null);
  const [error, setError] = useState<unknown>(null);
  // What it stopped to ask about. Held here rather than inside `did`, because
  // dropping the question must not also drop the record of what it did before
  // it got there.
  const [asks, setAsks] = useState<AgentTurn["asks"]>(null);
  const [pressing, setPressing] = useState(false);
  const [plus, setPlus] = useState(false);

  useEffect(() => {
    api.studioAgent().then(setReach).catch(() => setReach(null));
  }, []);

  function stopVoice() {
    // The ref goes first: stopping the recogniser fires its `onend`, and
    // an `onend` that still reads voice-on would relight what was just
    // put out.
    voiceOn.current = false;
    recogniser.current?.stop();
    recogniser.current = null;
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    playing.current?.stop();
    playing.current = null;
    setSaying(false);
    setVoiceMode(false);
  }

  // Leaving the screen ends the conversation. There was no unmount
  // teardown at all: navigating away mid-reply left a headless loop —
  // the voice kept talking, and the relight-after-reply contract kept
  // re-opening the recogniser under a screen that no longer exists. The
  // dictation recogniser is stopped too; stopVoice never owned it.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => () => {
    stopVoice();
    dictation.current?.stop();
    dictation.current = null;
  }, []);

  /** Say the reply out loud — the profile's own bound voice first (the
   *  deployment's engine, the watermark riding in the header), the
   *  device's voice standing in when there is no binding, no engine key,
   *  or the reply outruns the synthesis ceiling. One relight contract
   *  either way: when the speaking ends, the mic opens again and the
   *  idle clock restarts. Before this, a profile whose owner had made
   *  and bound a real voice still answered the orb in the browser's
   *  robot — the one surface where the voice mattered most. */
  async function speakReply(reply: string) {
    const done = () => {
      playing.current = null;
      setSaying(false);
      turning.current = false;
      if (voiceOn.current && !recogniser.current) startVoice();
    };
    if (session.profileId && session.ownerToken) {
      try {
        // Piece by piece: the first sentence plays while the rest is
        // still being synthesised, so the wait before the orb answers no
        // longer grows with the length of the answer. `stop()` (the orb
        // being closed mid-sentence) resolves `done` like playing out.
        const s = await speakInPieces(
          session.profileId, reply, session.ownerToken);
        playing.current = s;
        void s.done.then(done);
        return;
      } catch { /* the device's own voice stands in */ }
    }
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const spoken = new SpeechSynthesisUtterance(reply);
      spoken.onend = done;
      spoken.onerror = done;
      window.speechSynthesis.speak(spoken);
    } else {
      done();
    }
  }

  /** `fresh` marks a start that resets the idle clock — the person opening
   *  the orb, or the mic relighting after a spoken reply. The relight after
   *  a *silent* end passes false, so quiet cannot keep itself alive. */
  function startVoice(fresh = true) {
    voiceOn.current = true;
    if (fresh) lastHeard.current = Date.now();
    setVoiceMode(true);
    const Rec = recogniserOf();
    if (!Rec) {
      // No recogniser (iOS Safari). The orb still runs: the box takes the
      // keyboard's dictation key, and the reply comes back spoken.
      askBox.current?.focus();
      return;
    }
    const r = new Rec();
    r.continuous = false;
    r.interimResults = true;
    r.lang = lang;
    r.onresult = (e) => {
      const last = e.results[e.results.length - 1];
      const words = last[0]?.transcript || "";
      setAsk(words);
      if ((last as { isFinal: boolean }).isFinal && words.trim()) {
        lastHeard.current = Date.now();
        turning.current = true;
        void sendSaid(words);
      }
    };
    let fatal = false;
    r.onerror = (e: { error?: string }) => {
      // The three causes a person can act on, each named. Everything else
      // (`no-speech`, `aborted`) is the ordinary end of a quiet stretch
      // and the relight in onend is the right answer.
      const code = e.error || "";
      if (code === "not-allowed" || code === "service-not-allowed") {
        fatal = true;
        setEarFault(tr("agent.ear.blocked", lang));
      } else if (code === "audio-capture") {
        fatal = true;
        setEarFault(tr("agent.ear.nomic", lang));
      } else if (code === "network") {
        fatal = true;
        setEarFault(tr("agent.ear.unreachable", lang));
      }
    };
    r.onend = () => {
      recogniser.current = null;
      // A silent stretch ends the browser's recogniser on its own, and
      // the orb used to keep saying "listening" over a dead microphone.
      // Relight it — unless the ear just failed for a reason relighting
      // cannot fix (the fault line says which), a turn is mid-flight
      // (the reply's own end relights), the person closed the orb, or
      // nothing has been heard for two minutes, in which case the
      // conversation bows out quietly: leaving a room empty is not an
      // error.
      if (fatal) return;
      if (!voiceOn.current || turning.current) return;
      if (Date.now() - lastHeard.current >= CONVERSATION_IDLE_MS) {
        stopVoice();
        return;
      }
      startVoice(false);
    };
    recogniser.current = r;
    setEarFault(null);
    r.start();
  }

  function stopDictation() {
    dictation.current?.stop();
    dictation.current = null;
    setDictating(false);
  }

  function startDictation() {
    const Rec = recogniserOf();
    if (!Rec) {
      // iOS Safari has no recogniser. The honest version of this button
      // there is the keyboard's own dictation key, and a hint that says so
      // beats a control that silently does nothing.
      askBox.current?.focus();
      setMicHint(true);
      window.setTimeout(() => setMicHint(false), 6000);
      return;
    }
    const r = new Rec();
    r.continuous = true;
    r.interimResults = true;
    r.lang = lang;
    const base = ask.trim() ? ask.trim() + " " : "";
    r.onresult = (e) => {
      let finals = "", interim = "";
      for (let i = 0; i < e.results.length; i++) {
        const words = e.results[i][0]?.transcript || "";
        if ((e.results[i] as { isFinal: boolean }).isFinal) finals += words;
        else interim += words;
      }
      setAsk(base + finals + interim);
    };
    r.onerror = (e: { error?: string }) => {
      const code = e.error || "";
      if (code === "not-allowed" || code === "service-not-allowed") {
        setEarFault(tr("agent.ear.blocked", lang));
      } else if (code === "audio-capture") {
        setEarFault(tr("agent.ear.nomic", lang));
      } else if (code === "network") {
        setEarFault(tr("agent.ear.unreachable", lang));
      }
    };
    r.onend = () => { dictation.current = null; setDictating(false); };
    dictation.current = r;
    setEarFault(null);
    setDictating(true);
    r.start();
  }

  async function doSearch(qWhat: string) {
    if (!session.profileId || !session.ownerToken) return;
    const q = qWhat.trim();
    if (!q) return;
    setAsking(true); setError(null);
    try {
      setFinds(await api.webSearch(session.profileId, q, session.ownerToken));
      setAsk("");
    } catch (e) { setError(e); }
    finally { setAsking(false); }
  }

  async function postIt() {
    if (!session.profileId || !session.ownerToken || !pending) return;
    setAsking(true); setError(null);
    try {
      await api.publishPost(session.profileId,
        { body: ask, media_ids: [pending.id] }, session.ownerToken);
      setTalk([...talk, { role: "user", content: ask },
               { role: "assistant", content: tr("agent.open.created", lang) }]);
      setPending(null); setAsk("");
    } catch (e) { setError(e); }
    finally { setAsking(false); }
  }

  async function send() {
    if (searchMode) return doSearch(ask);
    if (pending) return postIt();
    return sendSaid(ask);
  }

  async function sendSaid(saidWhat: string) {
    if (!session.profileId || !session.ownerToken) return;
    const said = saidWhat;
    setAsking(true); setError(null);
    try {
      const turn = await api.authoringTurn(
        session.profileId, said, talk, session.ownerToken);
      setDid(turn);
      setAsks(turn.asks);
      setTalk([...talk, { role: "user", content: said },
               { role: "assistant", content: turn.reply }]);
      setAsk("");
      // Voice mode says the reply out loud, with the device's own voice —
      // the same fallback the chat screen uses, for the same reason: it
      // works offline and costs nothing.
      // The next turn: when the reply finishes, the mic relights — a
      // conversation, not a dictation box with extra steps — and the
      // idle clock restarts, so a long answer never eats into the
      // person's two minutes.
      if (voiceMode) {
        setSaying(true);
        void speakReply(turn.reply);
      } else {
        turning.current = false;
      }
      // What it may have changed is somebody's own page, so the roster is
      // re-read rather than assumed — a tool that stopped being available
      // mid-conversation should stop being offered.
      api.studioAgent().then(setReach).catch(() => undefined);
    } catch (e) {
      setError(e);
      // A failed turn must not strand the orb with a dead microphone:
      // the conversation stands, the error shows, the mic relights.
      turning.current = false;
      if (voiceOn.current && !recogniser.current) startVoice(false);
    }
    finally { setAsking(false); }
  }

  /** The press. The arguments go back exactly as the turn handed them over —
   *  rebuilding them here would make the sentence on the screen a summary of
   *  what happens rather than the thing being agreed to. */
  async function doIt() {
    if (!session.profileId || !session.ownerToken || !asks) return;
    setPressing(true); setError(null);
    try {
      const done = await api.authoringAct(
        session.profileId, { tool: asks.tool, arguments: asks.arguments },
        session.ownerToken);
      setDid({ reply: "", acted: [{ tool: done.tool, answered: done.answered,
                                    said: done.says }],
               stopped: null, said: null, asks: null });
      setAsks(null);
    } catch (e) { setError(e); }
    finally { setPressing(false); }
  }

  if (!session.profileId) {
    return (
      <div className="screen">
        <header className="screen-head"><h2>{tr("agent.title", lang)}</h2></header>
        <div className="card"><p className="muted center">
          {tr("agent.signin", lang)}
        </p></div>
      </div>
    );
  }

  return (
    <div className="agentscreen">
      {/* The conversation, and nothing above it. The mark used to sit here at
          full width and it is the *tab's* picture — a poster inside the room
          it is the door to, pushing the composer off the first screen. It is
          in the nav and nowhere else now. */}
      <div className="agent-body">
        <Refusal error={error} onPlans={onPlans} variant="inline" />

        {talk.length === 0 && !did && (
          <p className="muted small center agent-pitch">
            {tr("agent.pitch", lang)}
          </p>
        )}

        {talk.map((turn, i) => (
          <p key={i} className={turn.role === "user"
            ? "agent-said" : "muted small agent-heard"}>{turn.content}</p>
        ))}

        {did && did.said && <p className="muted small">{did.said}</p>}
        {did && did.acted.length > 0 && (
          <ul className="muted small">
            {did.acted.map((step, i) => (
              <li key={i}>
                {step.said ?? fill(tr("studio.step", lang), {
                  tool: step.tool, code: String(step.answered ?? 0) })}
              </li>
            ))}
          </ul>
        )}

        {/* It stopped and asked. The roster's own sentence, the arguments it
            chose, and two answers. */}
        {asks && (
          <div className="card asks">
            <p className="small">
              {fill(tr("agent.asks", lang), { does: asks.says })}
            </p>
            {Object.keys(asks.arguments).length > 0 && (
              <ul className="muted small">
                {Object.entries(asks.arguments).map(([field, value]) => (
                  <li key={field}>{field}: {String(value)}</li>
                ))}
              </ul>
            )}
            <div className="row">
              <button className="primary" disabled={pressing} onClick={doIt}>
                {pressing ? tr("agent.asks.doing", lang)
                          : tr("agent.asks.doit", lang)}
              </button>
              <button disabled={pressing} onClick={() => setAsks(null)}>
                {tr("agent.asks.no", lang)}
              </button>
            </div>
          </div>
        )}

        {showsReach && reach && (
          <div className="card">
            <div className="row">
              <strong style={{ flex: 1 }}>{tr("agent.ask.title", lang)}</strong>
              <button onClick={() => setShowsReach(false)}>
                {tr("studio.reach.hide", lang)}
              </button>
            </div>
            <p className="muted small">{tr("agent.ask.sub", lang)}</p>
            <ul className="muted small">
              {reach.can_touch.map((line) => <li key={line}>{line}</li>)}
            </ul>
          </div>
        )}
        {reach && !reach.available && (
          <p className="muted small">{tr("studio.ask.nomodel", lang)}</p>
        )}
      </div>

      {/* Three openings, for the person who has the screen and not the
          sentence. Each one fills the box rather than sending — what it does
          is still theirs to press. */}
      {finds && (
        <div className="card agent-found">
          <div className="row">
            <strong style={{ flex: 1 }}>{finds.q}</strong>
            <button aria-label={tr("agent.search.done", lang)}
                    onClick={() => { setFinds(null); setSearchMode(false); }}>
              ✕
            </button>
          </div>
          {finds.pages.length === 0 && (
            <p className="muted small">{tr("agent.search.none", lang)}</p>
          )}
          <ul className="agent-links">
            {finds.pages.map((row) => (
              <li key={row.url}>
                <a href={row.url} target="_blank" rel="noreferrer">
                  {row.title || row.url}
                </a>
                {row.note && <p className="muted small">{row.note}</p>}
              </li>
            ))}
          </ul>
          <a className="small" href={finds.more_url} target="_blank"
             rel="noreferrer">
            {tr("agent.search.more", lang)}
          </a>
        </div>
      )}

      {talk.length === 0 && !finds && (
        <div className="agent-openers">
          {OPENERS.map((o) => (
            <button key={o.key} className="agent-opener"
                    aria-pressed={o.key === "agent.open.search"
                                  ? searchMode : undefined}
                    onClick={() => {
                      if (o.key === "agent.open.create") {
                        mediaPicker.current?.click();
                      } else if (o.key === "agent.open.search") {
                        setSearchMode(!searchMode);
                        askBox.current?.focus();
                      } else {
                        setSearchMode(false);
                        setAsk(tr("agent.open.write.ask", lang));
                        askBox.current?.focus();
                      }
                    }}>
              <span aria-hidden="true">{o.icon}</span> {tr(o.key, lang)}
            </button>
          ))}
        </div>
      )}

      {/* The action strip. These do things; the places live in the menu. */}
      <div className="agent-rail">
        {ACTIONS.map((c) => (
          <button key={c.key} className="agent-chip"
                  aria-pressed={c.key === "voicemode" ? voiceMode : undefined}
                  onClick={() => {
                    if (c.key === "voicemode") {
                      if (voiceMode) stopVoice(); else startVoice();
                    } else if (c.key === "docs") {
                      docPicker.current?.click();
                    } else if (c.key === "image") {
                      imgPicker.current?.click();
                    } else {
                      setAsk(tr(`agent.act.${c.key}.ask`, lang));
                    }
                  }}>
            {c.key === "voicemode"
              ? <WaveIcon />
              : <span aria-hidden="true">{c.icon}</span>}
            {" "}{tr(`agent.act.${c.key}`, lang)}
            {c.key === "voicemode" && voiceMode ? " \u2713" : ""}
          </button>
        ))}
        <input ref={docPicker} type="file"
               accept=".pdf,.txt,.md,.doc,.docx,text/*,application/pdf"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0]; e.target.value = "";
                 if (!f || !session.profileId || !session.ownerToken) return;
                 uploadMedia(session.profileId, f, session.ownerToken)
                   .then((up) => setAsk(
                     tr("agent.act.docs.ask", lang) + " " + (up.id || f.name)))
                   .catch(setError);
               }} />
        <input ref={mediaPicker} type="file" accept="image/*,video/*"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0]; e.target.value = "";
                 if (!f || !session.profileId || !session.ownerToken) return;
                 setAsking(true);
                 uploadMedia(session.profileId, f, session.ownerToken)
                   .then((up) => { setPending({ id: up.id, name: f.name });
                                   askBox.current?.focus(); })
                   .catch(setError)
                   .finally(() => setAsking(false));
               }} />
        <input ref={imgPicker} type="file" accept="image/*"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0]; e.target.value = "";
                 if (!f || !session.profileId || !session.ownerToken) return;
                 uploadMedia(session.profileId, f, session.ownerToken)
                   .then((up) => setAsk(
                     tr("agent.act.image.ask", lang) + " " + (up.id || f.name)))
                   .catch(setError);
               }} />
      </div>

      {/* The orb: voice mode, visibly running. Tap it to stop. It relights
          the recogniser for the next turn where the browser has one; where
          it does not (iOS Safari) the orb is the state and the keyboard's
          dictation key is the microphone. */}
      {voiceMode && (
        <button className="agent-orb" onClick={stopVoice}
                aria-label={tr("agent.orb.stop", lang)}>
          <span className="agent-orb-ball" aria-hidden="true" />
          <span className="small">
            {/* A fault outranks "listening": an orb that says it hears
                over a microphone the browser refused is the lie the
                fault line exists to end. */}
            {asking ? tr("agent.orb.thinking", lang)
                    : saying ? tr("agent.orb.speaking", lang)
                    : earFault ?? tr("agent.orb.listening", lang)}
          </span>
        </button>
      )}

      <div className="agent-bar">
        {plus && (
          <div className="agent-plus" role="menu">
            {PLUS.map((p) => (
              <button key={p.id} role="menuitem"
                      onClick={() => { setPlus(false); go(p.id); }}>
                {p.icon} {tr(`nav.${p.id}`, lang)}
              </button>
            ))}
            <button role="menuitem"
                    onClick={() => { setPlus(false); setShowsReach(true); }}>
              ✦ {tr("agent.ask.title", lang)}
            </button>
          </div>
        )}
        {pending && (
          <div className="agent-pending">
            <span className="small">🖼 {pending.name}</span>
            <button aria-label={tr("agent.open.drop", lang)}
                    onClick={() => setPending(null)}>✕</button>
          </div>
        )}
        {micHint && (
          <p className="muted small agent-michint">
            {tr("agent.mic.keyboard", lang)}
          </p>
        )}
        {earFault && !voiceMode && (
          // The dictation mic's failures land here — the orb is not open
          // to carry them, and a 🎤 that dies silently reads as broken.
          <p className="muted small agent-michint">{earFault}</p>
        )}
        <div className="agent-pill">
          <button className="agent-plusbtn" aria-label={tr("agent.plus", lang)}
                  aria-expanded={plus} onClick={() => setPlus(!plus)}>+</button>
          <input ref={askBox} value={ask}
                 placeholder={pending ? tr("agent.open.caption", lang)
                              : searchMode ? tr("agent.search.ph", lang)
                              : tr("agent.ask.ph", lang)}
                 onChange={(e) => setAsk(e.target.value)}
                 onKeyDown={(e) => { if (e.key === "Enter") send(); }} />
          {talk.length > 0 && (
            <button className="agent-forget" aria-label={tr("studio.ask.forget", lang)}
                    onClick={() => { setTalk([]); setDid(null); setAsks(null); }}>
              ⟲
            </button>
          )}
          {/* Two buttons, two meanings, told apart on purpose: the mic
              *records into the box* — a take you stop when you are done —
              and the waveform beside it opens the orb. The mic used to be
              a navigator, then it was the orb; both were the same defect,
              a control doing something other than what its icon says. */}
          <button className={"agent-mic" + (dictating ? " rec" : "")}
                  aria-pressed={dictating}
                  aria-label={dictating ? tr("agent.mic.stop", lang)
                                        : tr("agent.mic.dictate", lang)}
                  onClick={() => (dictating ? stopDictation()
                                            : startDictation())}>
            {dictating ? "⏹" : "🎙"}
          </button>
          <button className="agent-wave" aria-pressed={voiceMode}
                  aria-label={tr("agent.orb.open", lang)}
                  onClick={() => (voiceMode ? stopVoice() : startVoice())}>
            <WaveIcon />
          </button>
          <button className="agent-send"
                  disabled={asking || !session.ownerToken || !ask.trim()}
                  onClick={send}>
            {asking ? tr("studio.ask.working", lang) : tr("studio.ask.go", lang)}
          </button>
        </div>
      </div>
    </div>
  );
}
