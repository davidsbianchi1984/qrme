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
  reach, showsReach, onToggleReach, unavailable, labels,
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
  /** The l10n key prefix, so each screen speaks in its own voice: Studio
   *  asks about a widget, Agent asks about the app. */
  labels: string;
}) {
  return (
    <div className="card">
      <div className="row">
        <strong style={{ flex: 1 }}>{tr(`${labels}.title`, lang)}</strong>
        <button onClick={onToggleReach}>
          {showsReach ? tr("studio.reach.hide", lang)
                      : tr("studio.reach.show", lang)}
        </button>
      </div>
      <p className="muted small">{tr(`${labels}.sub`, lang)}</p>
      {showsReach && reach && (
        <ul className="muted small">
          {reach.map((line) => <li key={line}>{line}</li>)}
        </ul>
      )}
      {unavailable && (
        <p className="muted small">{tr("studio.ask.nomodel", lang)}</p>
      )}
      <textarea rows={3} value={ask} placeholder={tr(`${labels}.ph`, lang)}
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
