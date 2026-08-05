import { useEffect, useState } from "react";
import { api } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// The doors: rooms (chat / voice / video / AR / VR) and live desks. The
// desktop console lists and creates them all, and joins what a desktop can
// honestly join — text and the desk views. An AR or VR room is shown with
// its badge; stepping inside one takes a headset or a phone, and the card
// says so instead of pretending.
const CHANNELS = [
  { id: "chat", key: "rms.ch.chat" },
  { id: "voice", key: "rms.ch.voice" },
  { id: "video", key: "rms.ch.video" },
  { id: "ar", key: "rms.ch.ar" },
  { id: "vr", key: "rms.ch.vr" },
];

export function Rooms({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [rooms, setRooms] = useState<Awaited<ReturnType<typeof api.listRooms>>>([]);
  const [desks, setDesks] = useState<Awaited<ReturnType<typeof api.listDesks>>>([]);
  const [topic, setTopic] = useState("");
  const [channel, setChannel] = useState("voice");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  function load() {
    api.listRooms().then(setRooms).catch((e) => setError(e));
    api.listDesks().then(setDesks).catch(() => setDesks([]));
  }
  useEffect(load, []);

  async function create() {
    if (!session.interactorId || !session.profileId) {
      setError(tr("rms.signinpick", lang));
      return;
    }
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
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  const badge = (ch: string) => {
    const found = CHANNELS.find((c) => c.id === ch);
    return found ? tr(found.key, lang) : ch;
  };

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("rms.title", lang)}</h2>
        <span className="muted small">{tr("rms.pitch", lang)}</span>
      </header>

      <div className="card">
        <h3>{tr("rms.openroom", lang)}</h3>
        <div className="row">
          <label>{tr("rms.topic", lang)}<input value={topic} placeholder={tr("rms.topic.ph", lang)}
                                onChange={(e) => setTopic(e.target.value)} /></label>
          <label>{tr("rms.kind", lang)}
            <select value={channel} onChange={(e) => setChannel(e.target.value)}>
              {CHANNELS.map((c) => (
                <option key={c.id} value={c.id}>{tr(c.key, lang)}</option>
              ))}
            </select>
          </label>
          <button className="primary" disabled={busy} onClick={create}>
            {tr("rms.open", lang)}
          </button>
        </div>
      </div>

      <div className="card">
        <h3>{tr("rms.livenow", lang)}</h3>
        {rooms.length === 0 && (
          <p className="muted center">{tr("rms.norooms", lang)}</p>
        )}
        {rooms.map((r) => (
          <div key={r.id} className="room-row">
            <span className={"tag ch-" + r.channel}>{badge(r.channel)}</span>
            <b>{r.topic || tr("rms.untitled", lang)}</b>
            <span className="muted small">
              {fill(tr("rms.inside", lang), { n: r.participants })}
            </span>
            {(r.channel === "ar" || r.channel === "vr") && (
              <span className="muted small">{tr("rms.headset", lang)}</span>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("rms.livedesks", lang)}</h3>
        {desks.length === 0 && (
          <p className="muted center">{tr("rms.nodesks", lang)}</p>
        )}
        {desks.map((d) => (
          <div key={d.id} className="room-row">
            <span className={"tag " + (d.presence === "attended" ? "live" : "")}>
              {d.presence === "attended" ? tr("rms.live", lang) : tr("rms.away", lang)}
            </span>
            <b>{d.display_name}</b>
            <span className="muted small">{d.trade}{d.location ? ` · ${d.location}` : ""}</span>
            {Boolean(d.rated) && <span className="tag rated">18+</span>}
          </div>
        ))}
      </div>

      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
