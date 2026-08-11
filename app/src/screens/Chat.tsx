import { useEffect, useRef, useState } from "react";
import { fill, t as tr, visitorLang } from "../l10n";
import { api } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

interface Msg { who: "you" | "assistant"; text: string; note?: string;
                /** Set when the model the owner chose did not answer and
                 *  the local fallback wrote this instead. */
                degradedFrom?: string | null }

export function Chat({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
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
  const listRef = useRef<HTMLDivElement>(null);
  // Voice: replies read aloud by the device's own engine, and a microphone
  // that fills the composer. Both feature-detected — the mic button simply
  // does not render on a browser without SpeechRecognition, because a
  // control that cannot work is worse than no control.
  const [speakOn, setSpeakOn] = useState(false);
  // TS's DOM lib does not ship SpeechRecognition types; the constructor is
  // feature-detected and driven through the three members every engine has.
  const Recognition: (new () => any) | undefined =
    (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;
  const [listening, setListening] = useState(false);

  // The conversation follows itself. The previous version scrolled from
  // `finally` inside a requestAnimationFrame, which can fire before React
  // commits the reply bubble — it measured yesterday's scrollHeight and the
  // newest message sat below the fold until the reader dragged it up. An
  // effect runs after the commit, so it sees the bubble it is scrolling to;
  // keying on busy too means the thinking indicator is followed as well.
  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [msgs, busy]);

  function speakAloud(text: string) {
    if (!("speechSynthesis" in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang;
    window.speechSynthesis.speak(u);
  }

  function listen() {
    if (!Recognition || listening) return;
    const rec = new Recognition();
    rec.lang = lang;
    rec.onresult = (e: any) =>
      setInput((v) => (v ? v + " " : "") + e.results[0][0].transcript);
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    setListening(true);
    rec.start();
  }

  async function send() {
    const message = input.trim();
    if (!message || !session.profileId || !session.interactorId) return;
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
      setMsgs((m) => [...m, { who: "assistant", text, note, degradedFrom }]);
      if (speakOn && pm.status === "approved") speakAloud(text);
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="screen chat">
      <header className="screen-head">
        <h2>
          {fill(tr("chat.with", lang),
                { name: session.profile?.display_name })}
        </h2>
        <span className="muted small">{tr("chat.pitch", lang)}</span>
      </header>

      {/* role=log + aria-live: a screen reader is told when the reply
          arrives, instead of the conversation advancing silently. */}
      <div className="messages" role="log" aria-live="polite" ref={listRef}>
        {msgs.length === 0 && (
          <div className="muted center">
            {fill(tr("chat.sayhello", lang),
                  { name: session.profile?.display_name })}
          </div>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={"bubble " + m.who}>
            {m.text}
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

      <div className="composer">
        <button title={tr("chat.wheretitle", lang)}
                className={whereOpen ? "primary" : ""}
                onClick={() => setWhereOpen((w) => !w)}>📍</button>
        <button title={tr("chat.speak", lang)}
                aria-label={tr("chat.speak", lang)}
                aria-pressed={speakOn}
                className={speakOn ? "primary" : ""}
                onClick={() => setSpeakOn((s) => !s)}>{speakOn ? "🔊" : "🔇"}</button>
        {Recognition && (
          <button title={tr("chat.mic", lang)}
                  aria-label={tr("chat.mic", lang)}
                  className={listening ? "primary" : ""}
                  onClick={listen}>🎤</button>
        )}
        <input
          value={input}
          placeholder={tr("chat.type.ph", lang)}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button className="primary" onClick={send} disabled={busy}>
          {tr("chat.send", lang)}
        </button>
      </div>
    </div>
  );
}
