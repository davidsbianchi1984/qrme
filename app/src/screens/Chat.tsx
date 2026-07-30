import { useRef, useState } from "react";
import { api } from "../api";
import { useSession } from "../store";

interface Msg { who: "you" | "assistant"; text: string; note?: string }

export function Chat() {
  const { session } = useSession();
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
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
      const note = reply.handoff?.state
        ? `specialist handoff: ${reply.handoff.state}`
        : pm.status !== "approved"
          ? `${pm.status} by moderation${pm.flag_reason ? ` — ${pm.flag_reason}` : ""}`
          : rc
            ? `worked as ${rc.role} (${rc.how})`
            : reply.environment
              ? "adapted to where you are"
              : undefined;
      const text = pm.status === "approved"
        ? pm.content
        : "(this reply was held by moderation)";
      setMsgs((m) => [...m, { who: "assistant", text, note }]);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
      requestAnimationFrame(() =>
        listRef.current?.scrollTo({ top: listRef.current.scrollHeight }),
      );
    }
  }

  return (
    <div className="screen chat">
      <header className="screen-head">
        <h2>Chat with {session.profile?.display_name}</h2>
        <span className="muted small">every response is persona- &amp; relationship-conditioned</span>
      </header>

      <div className="messages" ref={listRef}>
        {msgs.length === 0 && (
          <div className="muted center">Say hello to {session.profile?.display_name}.</div>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={"bubble " + m.who}>
            {m.text}
            {m.note && <div className="bubble-note">{m.note}</div>}
          </div>
        ))}
        {busy && <div className="bubble assistant thinking">…</div>}
      </div>

      {error && <div className="error">⚠ {error}</div>}

      {/* Spec clauses 2/12 — advisor counsels, collaborator co-creates,
          operator executes. "Let it read my prompt" is the honest default:
          the profile infers from the wording and the reply says which. */}
      <label className="role-pick">How should they work this turn?
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="">Let it read my prompt</option>
          <option value="advisor">Advisor — weigh it and recommend</option>
          <option value="collaborator">Collaborator — work it with me</option>
          <option value="operator">Operator — just do it</option>
        </select>
      </label>

      {whereOpen && (
        <div className="row" style={{ padding: "4px 0" }}>
          <label>Where<input value={location} placeholder="a trailhead, the kitchen"
                             onChange={(e) => setLocation(e.target.value)} /></label>
          <label>Conditions<input value={conditions} placeholder="raining, quiet"
                                  onChange={(e) => setConditions(e.target.value)} /></label>
          <label>Doing<input value={activity} placeholder="hiking, cooking"
                             onChange={(e) => setActivity(e.target.value)} /></label>
        </div>
      )}

      <div className="composer">
        <button title="Tell it where you are — the reply meets you there"
                className={whereOpen ? "primary" : ""}
                onClick={() => setWhereOpen((w) => !w)}>📍</button>
        <input
          value={input}
          placeholder="Type a message…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button className="primary" onClick={send} disabled={busy}>Send</button>
      </div>
    </div>
  );
}
