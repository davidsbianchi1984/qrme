import { fill, t as tr, type Lang } from "./l10n";
import type { AgentTurn } from "./api";

/**
 * The agent conversation, in one place.
 *
 * This markup was written inside `Studio.tsx`, where the agent that can edit
 * your page and build your widgets was reachable only by somebody already
 * editing a widget. Giving it its own tab meant a second surface needing the
 * same textarea, the same two buttons, the same turn list and the same
 * rendering of what it actually did — and fifty duplicated lines of JSX in a
 * repository whose suite fails over a binding nobody calls would be the wrong
 * answer to that.
 *
 * So the render moved and the state did not. Each screen keeps its own
 * `talk`, its own `send`, and its own idea of what happens afterwards —
 * Studio re-reads the widget it was editing, Agent re-reads the roster — and
 * hands the pieces here. A shared component that also owned the conversation
 * would make two screens share one history, which is not what either wants.
 *
 * ## What it did is under what it said
 *
 * An agent that describes an edit in prose is asking to be believed. The
 * steps are the part that can be checked, so they are rendered as a list
 * under the reply rather than folded into it, and a refused step keeps its
 * own sentence instead of being dropped — a tool that declined is a fact
 * about the turn, and hiding it leaves a person wondering why nothing
 * changed.
 */
export function AgentTalk({
  lang, ask, setAsk, asking, canSend, onSend, talk, did, onForget,
  reach, showsReach, onToggleReach, unavailable, words,
}: {
  lang: Lang;
  ask: string;
  setAsk: (v: string) => void;
  asking: boolean;
  /** The screen's own answer to "is there anybody to ask, and anything to
   *  ask with" — Studio wants an owner token, Agent wants a profile. */
  canSend: boolean;
  onSend: () => void;
  talk: { role: string; content: string }[];
  did: AgentTurn | null;
  onForget: () => void;
  /** What the agent may touch, in its own words, from the backend. */
  reach: string[] | null;
  showsReach: boolean;
  onToggleReach: () => void;
  /** True when no model is configured — said plainly rather than left for
   *  somebody to discover by pressing a button that answers nothing. */
  unavailable: boolean;
  /** Each screen's own three sentences, already translated: Studio asks about
   *  a widget, Agent asks about the app.
   *
   *  Words rather than a key prefix, and that is not a style choice. The
   *  first version took `labels="agent.ask"` and built the lookups here as
   *  `tr(`${labels}.title`, lang)`. Every one of them rendered — and
   *  `test_no_key_is_translated_into_ten_languages_and_used_nowhere` reads
   *  the console for keys, finds no literal and no literal *head* to a
   *  template that opens with its own interpolation, and reported all six
   *  `agent.ask.*` and `studio.ask.*` rows dead. Its advice for a dead key is
   *  "wire them, or delete them", and both are wrong here.
   *
   *      asked     does the key render
   *      mattered  can anything but the running app tell that it does
   *
   *  Widening the guard was the wrong repair: it cannot know what a prop
   *  holds, and a check that guessed would go quiet on the real thing it
   *  catches. So the lookup moved back to the screens, where the key is a
   *  literal somebody can grep for, and this component takes sentences. */
  words: { title: string; sub: string; ph: string };
}) {
  return (
    <div className="card">
      <div className="row">
        <strong style={{ flex: 1 }}>{words.title}</strong>
        <button onClick={onToggleReach}>
          {showsReach ? tr("studio.reach.hide", lang)
                      : tr("studio.reach.show", lang)}
        </button>
      </div>
      <p className="muted small">{words.sub}</p>
      {showsReach && reach && (
        <ul className="muted small">
          {reach.map((line) => <li key={line}>{line}</li>)}
        </ul>
      )}
      {unavailable && (
        <p className="muted small">{tr("studio.ask.nomodel", lang)}</p>
      )}
      <textarea rows={3} value={ask} placeholder={words.ph}
                onChange={(e) => setAsk(e.target.value)} />
      <div className="row">
        <button className="primary" disabled={asking || !canSend || !ask.trim()}
                onClick={onSend}>
          {asking ? tr("studio.ask.working", lang) : tr("studio.ask.go", lang)}
        </button>
        {talk.length > 0 && (
          <button onClick={onForget}>{tr("studio.ask.forget", lang)}</button>
        )}
      </div>
      {talk.map((turn, i) => (
        <p key={i} className={turn.role === "user" ? "small" : "muted small"}>
          {turn.content}
        </p>
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
    </div>
  );
}
