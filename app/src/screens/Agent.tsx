import { useEffect, useState } from "react";
import { api, type AgentTurn } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
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
const RAIL: { id: string; icon: string }[] = [
  { id: "studio", icon: "🛠" },
  { id: "corner", icon: "🏠" },
  { id: "wall", icon: "🧱" },
  { id: "workshop", icon: "🧩" },
  { id: "assist", icon: "🛠" },
  { id: "market", icon: "🏷" },
  { id: "shop", icon: "🛒" },
  { id: "discover", icon: "🛍" },
  { id: "rooms", icon: "🎧" },
  { id: "live", icon: "🎥" },
  { id: "presence", icon: "🖼" },
  { id: "beacons", icon: "🔳" },
  { id: "voice", icon: "🎙" },
  { id: "identity", icon: "🪪" },
  { id: "memory", icon: "🔒" },
  { id: "simulate", icon: "🔮" },
  { id: "campaigns", icon: "🎗" },
  { id: "selling", icon: "💰" },
  { id: "remainder", icon: "🧩" },
];

/** The composer's `+`. Four entries, each opening a screen that exists.
 *
 *  The shape asked for was Camera, Photos, Files and Plugins, and all four
 *  have somewhere real to land here: the camera is what is live in a place,
 *  photos are what the wall takes, files are the source material a profile
 *  answers from, and the plug-ins are the outside services it connects to.
 *  Nothing in this menu is a placeholder — a control that opens nothing is
 *  the thing this estate keeps finding and removing. */
const PLUS: { id: string; icon: string }[] = [
  { id: "live", icon: "📷" },
  { id: "wall", icon: "🖼" },
  { id: "workshop", icon: "📎" },
  { id: "remainder", icon: "🔌" },
];

/** Three openings for somebody who has the screen and not the sentence.
 *  They fill the box rather than sending it: what the agent does is still
 *  something a person presses. */
const OPENERS: { key: string; icon: string }[] = [
  { key: "agent.try.page", icon: "🎨" },
  { key: "agent.try.widget", icon: "🛠" },
  { key: "agent.try.post", icon: "🧱" },
];

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

  async function send() {
    if (!session.profileId || !session.ownerToken) return;
    const said = ask;
    setAsking(true); setError(null);
    try {
      const turn = await api.authoringTurn(
        session.profileId, said, talk, session.ownerToken);
      setDid(turn);
      setAsks(turn.asks);
      setTalk([...talk, { role: "user", content: said },
               { role: "assistant", content: turn.reply }]);
      setAsk("");
      // What it may have changed is somebody's own page, so the roster is
      // re-read rather than assumed — a tool that stopped being available
      // mid-conversation should stop being offered.
      api.studioAgent().then(setReach).catch(() => undefined);
    } catch (e) { setError(e); }
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
      {talk.length === 0 && (
        <div className="agent-openers">
          {OPENERS.map((o) => (
            <button key={o.key} className="agent-opener"
                    onClick={() => setAsk(tr(o.key, lang))}>
              <span aria-hidden="true">{o.icon}</span> {tr(o.key, lang)}
            </button>
          ))}
        </div>
      )}

      {/* The rail: every tool and connection this agent works alongside, as a
          launcher for screens that already exist. Each chip is a tab id, and
          its words come from the same `nav.<id>` row the navigation uses —
          the destination named once, so a chip cannot end up labelled for one
          screen and opening another. */}
      <div className="agent-rail">
        {RAIL.map((c) => (
          <button key={c.id} className="agent-chip" onClick={() => go(c.id)}>
            <span aria-hidden="true">{c.icon}</span> {tr(`nav.${c.id}`, lang)}
          </button>
        ))}
      </div>

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
        <div className="agent-pill">
          <button className="agent-plusbtn" aria-label={tr("agent.plus", lang)}
                  aria-expanded={plus} onClick={() => setPlus(!plus)}>+</button>
          <input value={ask} placeholder={tr("agent.ask.ph", lang)}
                 onChange={(e) => setAsk(e.target.value)}
                 onKeyDown={(e) => { if (e.key === "Enter") send(); }} />
          {talk.length > 0 && (
            <button className="agent-forget" aria-label={tr("studio.ask.forget", lang)}
                    onClick={() => { setTalk([]); setDid(null); setAsks(null); }}>
              ⟲
            </button>
          )}
          <button className="agent-mic" aria-label={tr("nav.voice", lang)}
                  onClick={() => go("voice")}>🎙</button>
          <button className="agent-voice" aria-label={tr("nav.rooms", lang)}
                  onClick={() => go("rooms")}>🎧</button>
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
