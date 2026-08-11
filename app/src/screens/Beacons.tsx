import { useEffect, useState } from "react";
import { api, getBase, type SocialBeacon,
         type SocialConnection } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Connections to the world: a code on a wall, and a code on a platform.
 *
 * Both are QR pictures and they look identical, so the screen says what each
 * one does. A **placed beacon** lands a stranger on QRME — the profile answers
 * them there. A **platform beacon** lands them on Instagram or Mastodon: it
 * carries them *away*, to an account that already exists. Only where there is
 * no handle to build a link from does the second fall back to a QRME summon
 * page. Scanning to find out which kind you printed is not a reasonable way to
 * learn it.
 *
 * **Fetching a QR is free; opening a scan page is not.** Every scan surface —
 * `/b/{id}`, `/d/{id}`, `/d/{id}/card`, and the older `/summon?ref=` —
 * increments the beacon's count, and there is no preview that doesn't. So this
 * screen renders the images freely and never opens a scan page on its own: the
 * link is a deliberate press, labelled with what it costs. An owner checking
 * their own sticker would otherwise inflate the number they are checking it
 * against.
 *
 * A connection has a direction and the two never overlap: `collect` pulls an
 * account's content in to grow the profile, `publish` runs the profile out.
 * Only `publish` has a beacon — the server answers 409 otherwise — and the
 * list already says so by giving `beacon: null`, so the QR is simply not
 * offered rather than offered and refused.
 */
export function Beacons({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [conns, setConns] = useState<SocialConnection[]>([]);
  const [beacon, setBeacon] = useState<SocialBeacon | null>(null);

  const [platform, setPlatform] = useState("instagram");
  const [direction, setDirection] = useState("publish");
  const [handle, setHandle] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function load() {
    if (!me || !token) return;
    api.socialConnections(me, token).then(setConns).catch(() => setConns([]));
  }
  useEffect(load, [me, token]);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { setError(e); } finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>{tr("bcn.title", lang)}</h2>
      <p className="muted small">
        {fill(tr("bcn.lead", lang),
          { here: <em>{tr("bcn.here", lang)}</em> })}
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("bcn.connect", lang)}</h3>
        <p className="muted small">
          {fill(tr("bcn.directions", lang), {
            collect: <strong>{tr("bcn.collect", lang)}</strong>,
            publish: <strong>{tr("bcn.publish", lang)}</strong>,
          })}
        </p>
        <div className="row">
          <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
            {["instagram", "x", "tiktok", "facebook", "linkedin", "youtube",
              "reddit", "threads", "mastodon", "twitch", "pinterest",
              "discord"].map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <select value={direction}
                  onChange={(e) => setDirection(e.target.value)}>
            <option value="publish">{tr("bcn.opt.publish", lang)}</option>
            <option value="collect">{tr("bcn.opt.collect", lang)}</option>
          </select>
          <input value={handle} onChange={(e) => {
                   const v = e.target.value;
                   setHandle(v);
                   // A pasted link is something to fetch: pre-select collect
                   // (still a dropdown — the choice stays changeable).
                   if (v.startsWith("http")) setDirection("collect");
                 }}
                 placeholder={tr("bcn.handle.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !me || !token}
                  onClick={act(async () => {
                    await api.connectSocial(me, {
                      platform, direction,
                      handle: handle.trim() || undefined }, token);
                    setHandle("");
                  }, tr("bcn.connected.said", lang))}>
            {tr("bcn.connectbtn", lang)}
          </button>
        </div>
        <p className="muted small">{tr("bcn.nohandle", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("bcn.connectedhdr", lang)}</h3>
        {conns.length === 0 &&
          <p className="muted small">{tr("bcn.none", lang)}</p>}
        {conns.map((c) => (
          <div key={c.id}>
            <p className="small">
              <strong>{c.platform}</strong> — {c.direction}
              {c.handle && ` · ${c.handle}`} · {c.status}
              <br />
              <span className="muted">
                {fill(tr("bcn.counts", lang), {
                  collected: c.collected, published: c.published })}
              </span>
            </p>
            <div className="row">
              {/* Offered only where the server has one. A `collect` row
                  answers 409, and the list says so already by leaving
                  `beacon` null — so the button is absent rather than
                  present and refused. */}
              {c.beacon && (
                <button className="chip" disabled={busy}
                        onClick={act(async () =>
                          setBeacon(await api.socialBeacon(c.id)))}>
                  {tr("bcn.showcode", lang)}
                </button>
              )}
              {/* Only a collect connection with a handle has an address
                  to visit; the server answers 400/409 for the rest, so the
                  button is absent rather than present and refused. */}
              {c.direction === "collect" && c.handle && (
                <button className="chip" disabled={busy}
                        onClick={act(() => api.scrapeSocial(c.id, token),
                          tr("bcn.scraped.said", lang))}>
                  {tr("bcn.scrape", lang)}
                </button>
              )}
              <button className="chip" disabled={busy}
                      onClick={act(() => api.disconnectSocial(c.id, token),
                        tr("bcn.disconnected.said", lang))}>
                {tr("bcn.disconnect", lang)}
              </button>
            </div>
          </div>
        ))}
      </div>

      {beacon && (
        <div className="card">
          <h3>{fill(tr("bcn.codefor", lang),
            { platform: beacon.platform })}</h3>
          {/* Free to fetch. The scan surfaces are not — see below. */}
          <img src={getBase() + `/social/${beacon.connection}/qr.svg`}
               width={180} height={180}
               alt={tr("bcn.qralt", lang)} />
          <p className="small">
            {fill(tr("bcn.opens", lang),
              { url: <code>{beacon.presence_url}</code> })}
            {beacon.handle
              ? tr("bcn.opens.handle", lang)
                  .replace("{handle}", beacon.handle)
                  .replace("{platform}", beacon.platform)
              : tr("bcn.opens.summon", lang)}
          </p>
          <p className="muted small">
            {fill(tr("bcn.carries", lang),
              { away: <em>{tr("bcn.away", lang)}</em> })}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{tr("bcn.cost", lang)}</h3>
        <p className="muted small">
          {fill(tr("bcn.cost.pitch", lang),
            { is: <em>{tr("bcn.is", lang)}</em> })}
        </p>
        <p className="muted small">
          {fill(tr("bcn.cost.links", lang),
            { placements: <strong>{tr("bcn.placements", lang)}</strong> })}
        </p>
      </div>
    </div>
  );
}
