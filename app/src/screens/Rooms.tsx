import { useEffect, useState } from "react";
import { api } from "../api";
import { useSession } from "../store";

// The doors: rooms (chat / voice / video / AR / VR) and live desks. The
// desktop console lists and creates them all, and joins what a desktop can
// honestly join — text and the desk views. An AR or VR room is shown with
// its badge; stepping inside one takes a headset or a phone, and the card
// says so instead of pretending.
const CHANNELS = [
  { id: "chat", label: "Text" },
  { id: "voice", label: "Voice chat only" },
  { id: "video", label: "Video" },
  { id: "ar", label: "AR" },
  { id: "vr", label: "VR" },
];

export function Rooms() {
  const { session } = useSession();
  const [rooms, setRooms] = useState<Awaited<ReturnType<typeof api.listRooms>>>([]);
  const [desks, setDesks] = useState<Awaited<ReturnType<typeof api.listDesks>>>([]);
  const [topic, setTopic] = useState("");
  const [channel, setChannel] = useState("voice");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function load() {
    api.listRooms().then(setRooms).catch((e) => setError((e as Error).message));
    api.listDesks().then(setDesks).catch(() => setDesks([]));
  }
  useEffect(load, []);

  async function create() {
    if (!session.interactorId) { setError("Sign in first."); return; }
    setBusy(true); setError(null);
    try {
      // A room of one isn't a room: the backend requires two participants,
      // so you and your own profile open it together — anyone else joins.
      await api.createRoom({
        topic: topic.trim() || undefined, channel,
        participants: [
          { kind: "user", id: session.interactorId },
          { kind: "profile", id: session.profileId! },
        ],
      });
      setTopic(""); load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  const badge = (ch: string) => CHANNELS.find((c) => c.id === ch)?.label || ch;

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Rooms</h2>
        <span className="muted small">2D, AR and VR sessions · live desks</span>
      </header>

      <div className="card">
        <h3>Open a room</h3>
        <div className="row">
          <label>Topic<input value={topic} placeholder="what it's about" onChange={(e) => setTopic(e.target.value)} /></label>
          <label>Kind
            <select value={channel} onChange={(e) => setChannel(e.target.value)}>
              {CHANNELS.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
            </select>
          </label>
          <button className="primary" disabled={busy} onClick={create}>Open</button>
        </div>
      </div>

      <div className="card">
        <h3>Live now</h3>
        {rooms.length === 0 && <p className="muted center">No rooms open — start one above.</p>}
        {rooms.map((r) => (
          <div key={r.id} className="room-row">
            <span className={"tag ch-" + r.channel}>{badge(r.channel)}</span>
            <b>{r.topic || "untitled room"}</b>
            <span className="muted small">{r.participants} inside</span>
            {(r.channel === "ar" || r.channel === "vr") && (
              <span className="muted small">— join from a headset or phone; this desktop shows the room</span>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Live desks</h3>
        {desks.length === 0 && <p className="muted center">Nobody is at a desk right now.</p>}
        {desks.map((d) => (
          <div key={d.id} className="room-row">
            <span className={"tag " + (d.presence === "attended" ? "live" : "")}>
              {d.presence === "attended" ? "● live" : "away"}
            </span>
            <b>{d.display_name}</b>
            <span className="muted small">{d.trade}{d.location ? ` · ${d.location}` : ""}</span>
            {Boolean(d.rated) && <span className="tag rated">18+</span>}
          </div>
        ))}
      </div>

      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
