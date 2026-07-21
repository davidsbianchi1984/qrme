import { useRef, useState } from "react";
import { api } from "../api";
import { useSession } from "../store";

interface Msg { who: "you" | "ava"; text: string; note?: string }

export function Chat() {
  const { session } = useSession();
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  async function send() {
    const message = input.trim();
    if (!message || !session.profileId || !session.interactorId) return;
    setInput("");
    setError(null);
    setMsgs((m) => [...m, { who: "you", text: message }]);
    setBusy(true);
    try {
      const reply = await api.chat(session.profileId, {
        interactor_id: session.interactorId,
        message,
      });
      const pm = reply.profile_message;
      const note = reply.handoff?.state
        ? `specialist handoff: ${reply.handoff.state}`
        : pm.status !== "approved"
          ? `${pm.status} by moderation${pm.flag_reason ? ` — ${pm.flag_reason}` : ""}`
          : undefined;
      const text = pm.status === "approved"
        ? pm.content
        : "(this reply was held by moderation)";
      setMsgs((m) => [...m, { who: "ava", text, note }]);
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
        {busy && <div className="bubble ava thinking">…</div>}
      </div>

      {error && <div className="error">⚠ {error}</div>}

      <div className="composer">
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
