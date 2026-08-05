import { useEffect, useState } from "react";
import { api, getBase, type PlacementAnalytics, type PlacementMade,
         type PlacementRow, type Venue } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Where a rated profile is marketed.
 *
 * An adult-mode profile can be advertised at an adult venue — a creator
 * platform, a directory — as a link or a printable QR. The feature only makes
 * sense because of one sentence the backend puts on every venue, which this
 * screen renders verbatim and never paraphrases:
 *
 *   *every summon of a rated profile resolves through QRME's 18+ age wall,
 *   regardless of where the QR or handle was found*
 *
 * The wall does not move to the venue. That is the whole argument, and a
 * console that summarised it into "18+" would be dropping the load-bearing
 * half — *regardless of where it was found*.
 *
 * Four things that were only visible by driving the running API:
 *
 * - **the create response and the list response are different shapes.** The
 *   create carries `scan_url`, `summon_url` and `qr_svg`; the list carries the
 *   scan counts and none of those. A screen assuming otherwise renders blanks
 *   after a reload, so the list derives the QR path from `beacon_id`;
 * - **`scan_url` and `summon_url` are not interchangeable.** `summon_url` is
 *   the JSON surface existing clients read; `scan_url` is where a phone camera
 *   lands and what the printed QR encodes. Publishing the wrong one gives
 *   somebody a page of JSON;
 * - **`funnel.chat_rate` is null, not zero**, until something has got through
 *   the wall. There is no rate to state yet, and `.toFixed()` on it prints
 *   nonsense;
 * - **removing a placement deactivates the beacon rather than deleting it**,
 *   so a QR already printed at a venue stops resolving instead of pointing
 *   somewhere new. The screen says so before you press it.
 */
export function Placements({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [venues, setVenues] = useState<Venue[]>([]);
  const [rows, setRows] = useState<PlacementRow[]>([]);
  const [made, setMade] = useState<PlacementMade | null>(null);
  const [stats, setStats] = useState<PlacementAnalytics | null>(null);
  const [custody, setCustody] = useState<string | null>(null);

  const [venue, setVenue] = useState("");
  const [label, setLabel] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const fail = (e: unknown) => setError(e);

  useEffect(() => { api.venues().then(setVenues).catch(fail); }, []);

  function load() {
    if (!me || !token) { setRows([]); setStats(null); return; }
    api.placements(me, token).then(setRows).catch(() => setRows([]));
    api.placementAnalytics(me, token).then(setStats).catch(() => setStats(null));
    // A 409 here is a deployment posture, not a failure: no vault is
    // configured, so nothing is sealed. Reported as what it is.
    api.placementCustody(me, token)
      .then(() => setCustody(null))
      .catch((e) => setCustody((e as Error).message));
  }
  useEffect(load, [me, token]);

  async function place() {
    setError(null); setNote(null); setMade(null);
    try {
      setMade(await api.placeAtVenue(
        me, { venue, label: label.trim() || undefined }, token));
      setLabel(""); load();
    } catch (e) { fail(e); }
  }

  async function remove(id: string) {
    setError(null); setNote(null);
    try {
      const r = await api.removePlacement(id, token);
      setNote(tr("plc.takendown.said", lang).replace("{state}",
        r.beacon_active
          ? tr("plc.stilllive", lang) : tr("plc.nolonger", lang)));
      if (made?.placement_id === id) setMade(null);
      load();
    } catch (e) { fail(e); }
  }

  return (
    <div className="screen">
      <h2>{tr("plc.title", lang)}</h2>
      <p className="muted small">{tr("plc.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("plc.venues", lang)}</h3>
        {venues.map((v) => (
          <div key={v.key}>
            <h4>
              {v.name}
              {v.url && <> · <a href={v.url} target="_blank"
                                rel="noreferrer">{v.url}</a></>}
            </h4>
            <p className="small">{v.blurb}</p>
            <p className="muted small">
              {fill(tr("plc.carries", lang),
                { what: v.hosts.join(" and ") })}
            </p>
            {/* Verbatim. Never summarised — "regardless of where the QR or
                handle was found" is the load-bearing half. */}
            <p className="muted small"><strong>{v.note}</strong></p>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("plc.place", lang)}</h3>
        <div className="row">
          <select value={venue} onChange={(e) => setVenue(e.target.value)}>
            <option value="">{tr("plc.pick", lang)}</option>
            {venues.map((v) => (
              <option key={v.key} value={v.key}>{v.name}</option>
            ))}
          </select>
          <input value={label} onChange={(e) => setLabel(e.target.value)}
                 placeholder={tr("plc.label.ph", lang)}
                 style={{ flex: 1 }} />
          <button disabled={!me || !token || !venue} onClick={place}>
            {tr("plc.placebtn", lang)}
          </button>
        </div>
        <p className="muted small">{tr("plc.adultonly", lang)}</p>
      </div>

      {made && (
        <div className="card">
          <h3>{tr("plc.publish", lang)}</h3>
          <img src={getBase() + made.qr_svg} width={180} height={180}
               alt={tr("plc.qr.made", lang)} />
          <p className="small">
            <strong>{tr("plc.printshare", lang)}</strong>{" "}
            <a href={made.scan_url} target="_blank" rel="noreferrer">
              {made.scan_url}
            </a>
          </p>
          {/* Said plainly, because the two urls look alike and one of them
              is a page of JSON. */}
          <p className="muted small">
            {fill(tr("plc.thatone", lang),
              { url: <code>{made.summon_url}</code> })}
          </p>
          <p className="muted small">
            {made.handle
              ? fill(tr("plc.alsoas", lang), { handle: made.handle })
              : tr("plc.nohandle", lang)}
          </p>
          <p className="muted small">{made.note}</p>
          <p className="muted small">{tr("plc.keepthis", lang)}</p>
        </div>
      )}

      <div className="card">
        <h3>{tr("plc.placedat", lang)}</h3>
        {rows.length === 0 && (
          <p className="muted small">
            {me && token
              ? tr("plc.nowhere", lang) : tr("plc.signin", lang)}
          </p>
        )}
        {rows.map((r) => (
          <div className="row" key={r.id}>
            <div style={{ flex: 1 }}>
              <strong>{r.label}</strong>
              <div className="muted small">
                {fill(tr("plc.row", lang), {
                  venue: r.venue_name, n: r.scans,
                  s: r.scans === 1 ? "" : "s",
                })}
                {!r.active && tr("plc.takendown", lang)}
              </div>
            </div>
            {/* Free to fetch: asking for the picture is not a scan, unlike
                following the link beside it. */}
            <img src={getBase() + `/beacons/${r.beacon_id}/qr.svg`}
                 width={56} height={56} alt={tr("plc.qr.row", lang)} />
            {/* The list response carries no urls, so this is derived — and
                deliberately labelled "on this deployment", because the
                published link uses the configured public host and this one
                uses whatever API the console is pointed at. They are the
                same route on different hosts, and quietly calling this one
                "the link" would hand somebody the wrong address to print.
                Written as `getBase() + literal` rather than one template:
                a template opening with `${...}` is a string the route audit
                cannot resolve to a path, and this door counted as missing
                for as long as it was written that way. */}
            <a href={getBase() + `/b/${r.beacon_id}`} target="_blank"
               rel="noreferrer">{tr("plc.openhere", lang)}</a>
            <button onClick={() => remove(r.id)}>
              {tr("plc.takedown", lang)}
            </button>
          </div>
        ))}
      </div>

      {stats && (
        <div className="card">
          <h3>{tr("plc.brings", lang)}</h3>
          <p className="muted small">{tr("plc.countsonly", lang)}</p>
          {stats.venues.map((v) => (
            <div key={v.placement_id}>
              <h4>{v.venue_name} — {v.label}</h4>
              <p className="small">
                {fill(tr("plc.venue.line", lang), {
                  n: v.scans, s: v.scans === 1 ? "" : "s",
                  walled: v.walled, verified: v.verified,
                })}
              </p>
              {v.by_day.length > 0 && (
                <p className="muted small">
                  {v.by_day.map((d) => `${d.day}: ${d.scans}`).join(" · ")}
                </p>
              )}
            </div>
          ))}
          <h4>{tr("plc.everything", lang)}</h4>
          <p className="muted small">
            {fill(tr("plc.direct", lang), {
              walled: stats.direct.walled,
              verified: stats.direct.verified,
            })}
          </p>
          <h4>{tr("plc.funnel", lang)}</h4>
          <p className="small">
            {fill(tr("plc.funnel.line", lang), {
              res: stats.funnel.resolutions,
              views: stats.funnel.verified_views,
              chat: stats.funnel.unique_chatters,
            })}
          </p>
          <p className="muted small">
            {fill(tr("plc.through", lang),
              { pct: (stats.funnel.verified_rate * 100).toFixed(0) })}{" "}
            {/* Null, not zero, until something has. There is no rate yet, and
                saying "0%" would be a claim rather than an absence. */}
            {stats.funnel.chat_rate === null
              ? tr("plc.norate", lang)
              : tr("plc.chatrate", lang).replace(
                  "{pct}", (stats.funnel.chat_rate * 100).toFixed(0))}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{tr("plc.kept", lang)}</h3>
        {custody ? (
          <>
            {/* Lead with the part addressed to the person reading this
                screen. The backend's sentence names environment variables,
                which is the right message for whoever runs the deployment
                and not something a creator can act on — so it is kept, and
                kept second. */}
            <p className="small">{tr("plc.novault", lang)}</p>
            <p className="muted small">
              {fill(tr("plc.reported", lang), { what: custody })}
            </p>
          </>
        ) : (
          <p className="muted small">{tr("plc.sealed", lang)}</p>
        )}
      </div>
    </div>
  );
}
