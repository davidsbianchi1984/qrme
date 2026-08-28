import { useEffect, useState } from "react";
import { api, type XrPlatform } from "../api";
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

export function Rooms({ onPlans, onInside }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
  /** After a join, the Inside screen opens on the room just entered —
   *  threaded from the shell for the same reason as onPlans. */
  onInside: (roomId: string) => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [rooms, setRooms] = useState<Awaited<ReturnType<typeof api.listRooms>>>([]);
  const [desks, setDesks] = useState<Awaited<ReturnType<typeof api.listDesks>>>([]);
  const [templates, setTemplates] =
    useState<Awaited<ReturnType<typeof api.roomTemplates>>>([]);
  const [topic, setTopic] = useState("");
  const [channel, setChannel] = useState("voice");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  // Who you might ask in. The friends list is the picker rather than a text
  // box wanting a `prf_…`: an id somebody has to fetch from somewhere else
  // is a form nobody fills in.
  const [friends, setFriends] =
    useState<{ profile_id: string; display_name: string }[]>([]);
  const [asking, setAsking] = useState<Record<string, string>>({});
  const [asked, setAsked] = useState<string | null>(null);
  // The XR shelf: every headset on the market and its road into these
  // rooms. The rooms are pages, so the road is the headset's own browser
  // — the card says which, and marks the futures as futures.
  const [xr, setXr] = useState<XrPlatform[]>([]);

  function load() {
    api.listRooms().then(setRooms).catch((e) => setError(e));
    api.listDesks().then(setDesks).catch(() => setDesks([]));
    api.xrPlatforms().then((r) => setXr(r.xr_platforms))
      .catch(() => setXr([]));
    api.roomTemplates().then(setTemplates).catch(() => setTemplates([]));
    // This profile's own friends. Without one signed in there is nobody to
    // offer, and the control below is absent rather than empty.
    if (session.profileId) {
      api.friends(session.profileId)
        .then((r) => setFriends(r.friends))
        .catch(() => setFriends([]));
    }
  }
  useEffect(load, []);

  // One press on a standing room: the room, not a copy of it. The first
  // build minted a fresh room every press — twelve templates always on
  // screen, a live list filling with identical Front Porches. The server
  // joins the live one with a seat left and opens fresh only when nobody
  // is there, and the press lands you Inside either way.
  async function openTemplate(t: { key: string }) {
    if (!session.interactorToken || !session.profileId) {
      setError(tr("rms.signinpick", lang));
      return;
    }
    setBusy(true); setError(null);
    try {
      const room = await api.openStandingRoom(
        t.key, session.profileId, session.interactorToken);
      onInside(room.id);
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

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
        <h3>{tr("rms.standing", lang)}</h3>
        <p className="muted small">{tr("rms.standing.pitch", lang)}</p>
        {templates.map((t) => (
          <div key={t.key} className="room-row">
            <span className={"tag ch-" + t.channel}>{badge(t.channel)}</span>
            <b>{t.topic}</b>
            <span className="muted small">{t.pitch}</span>
            <button className="ghost" disabled={busy}
                    onClick={() => openTemplate(t)}>
              {tr("rms.standing.open", lang)}
            </button>
          </div>
        ))}
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
            {/* Look before entering — the roster on the card, not a
                separate screen away. */}
            {r.who.length > 0 && (
              <span className="muted small rms-who">
                {r.who.join(" · ")}
              </span>
            )}
            {/* The list used to show rooms nobody could enter — the door
                in was frozen at creation. Joining takes the interactor
                token, and lands you Inside. */}
            <button className="ghost" disabled={busy || !session.interactorToken}
                    onClick={async () => {
                      setBusy(true); setError(null);
                      try {
                        await api.joinRoom(r.id, session.interactorToken!);
                        onInside(r.id);
                      } catch (e) { setError(e); }
                      finally { setBusy(false); }
                    }}>
              {tr("rms.standing.open", lang)}
            </button>
            {/* Asking somebody in. Rooms could be opened and walked into and
                nobody could be invited to one: the only ways were to name
                them in the create body — which needs their id before the
                room exists — or to send them the id by some means this
                product does not provide. */}
            {friends.length > 0 && session.interactorToken && (
              <>
                <select value={asking[r.id] || ""}
                        onChange={(e) => setAsking(
                          { ...asking, [r.id]: e.target.value })}>
                  <option value="">{tr("rms.askwho", lang)}</option>
                  {friends.map((f) => (
                    <option key={f.profile_id} value={f.profile_id}>
                      {f.display_name}
                    </option>
                  ))}
                </select>
                <button className="ghost" disabled={busy || !asking[r.id]}
                        onClick={async () => {
                          setBusy(true); setError(null); setAsked(null);
                          try {
                            const out = await api.inviteToRoom(
                              r.id, asking[r.id], session.interactorToken!);
                            // Said rather than implied: a second press is a
                            // no-op, and whoever pressed again deserves to be
                            // told it already went rather than left to wonder.
                            setAsked(out.already_invited
                              ? tr("rms.askedalready", lang)
                              : tr("rms.asked", lang));
                          } catch (e) { setError(e); }
                          finally { setBusy(false); }
                        }}>
                  {tr("rms.ask", lang)}
                </button>
              </>
            )}
          </div>
        ))}
        {asked && <p className="muted small">{asked}</p>}
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

      {/* Headsets & glasses — the market, honestly. Steam, Meta, Apple
          and the rest each get their row: the browser road that works
          today, the VR/AR badges the hardware earns, and the sign-in and
          native-app futures said as futures rather than buttons. */}
      {xr.length > 0 && (
        <div className="card">
          <h3>{tr("rms.xr.title", lang)}</h3>
          <p className="muted small">{tr("rms.xr.lead", lang)}</p>
          {xr.map((p) => (
            <div key={p.platform} className="room-row">
              <b>{p.name}</b>
              {p.wears.includes("vr") && (
                <span className="tag ch-vr">{tr("rms.ch.vr", lang)}</span>
              )}
              {p.wears.includes("ar") && (
                <span className="tag ch-ar">{tr("rms.ch.ar", lang)}</span>
              )}
              {p.open_now && (
                <span className="muted small">
                  {fill(tr("rms.xr.now", lang), { browser: p.browser })}
                </span>
              )}
              {p.signin === "planned" && (
                <span className="muted small">{tr("rms.xr.signin", lang)}</span>
              )}
              {p.signin === "unconfigured" && (
                <span className="muted small">{tr("rms.xr.off", lang)}</span>
              )}
            </div>
          ))}
          <p className="muted small">{tr("rms.xr.app", lang)}</p>
        </div>
      )}

      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
