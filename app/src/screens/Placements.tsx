import { useEffect, useState } from "react";
import { api, getBase, type PlacementAnalytics, type PlacementMade,
         type PlacementRow, type Venue } from "../api";
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
      setNote(`Taken down. The beacon is ${r.beacon_active ? "still live"
        : "no longer live"} — anything already printed at the venue now stops `
        + "resolving rather than pointing somewhere else.");
      if (made?.placement_id === id) setMade(null);
      load();
    } catch (e) { fail(e); }
  }

  return (
    <div className="screen">
      <h2>Where it is marketed</h2>
      <p className="muted small">
        An adult-mode profile can be advertised at an adult venue, as a link or
        a printable code.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Venues</h3>
        {venues.map((v) => (
          <div key={v.key}>
            <h4>
              {v.name}
              {v.url && <> · <a href={v.url} target="_blank"
                                rel="noreferrer">{v.url}</a></>}
            </h4>
            <p className="small">{v.blurb}</p>
            <p className="muted small">
              Carries: {v.hosts.join(" and ")}.
            </p>
            {/* Verbatim. Never summarised — "regardless of where the QR or
                handle was found" is the load-bearing half. */}
            <p className="muted small"><strong>{v.note}</strong></p>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Place this profile</h3>
        <div className="row">
          <select value={venue} onChange={(e) => setVenue(e.target.value)}>
            <option value="">pick a venue</option>
            {venues.map((v) => (
              <option key={v.key} value={v.key}>{v.name}</option>
            ))}
          </select>
          <input value={label} onChange={(e) => setLabel(e.target.value)}
                 placeholder="what to call it (optional)"
                 style={{ flex: 1 }} />
          <button disabled={!me || !token || !venue} onClick={place}>
            Place
          </button>
        </div>
        <p className="muted small">
          Only an adult-mode profile can be placed at an adult venue, and the
          refusal says so rather than hiding the button.
        </p>
      </div>

      {made && (
        <div className="card">
          <h3>Publish this</h3>
          <img src={getBase() + made.qr_svg} width={180} height={180}
               alt="the beacon's QR code" />
          <p className="small">
            <strong>Print or share:</strong>{" "}
            <a href={made.scan_url} target="_blank" rel="noreferrer">
              {made.scan_url}
            </a>
          </p>
          {/* Said plainly, because the two urls look alike and one of them
              is a page of JSON. */}
          <p className="muted small">
            That is the one a phone camera lands on and the one the code
            encodes. <code>{made.summon_url}</code> is the machine-readable
            surface for clients, not a link to give anybody.
          </p>
          <p className="muted small">
            {made.handle
              ? <>Also reachable as {made.handle}.</>
              : <>This profile has not claimed a handle, so the code and the
                  link are the only ways in.</>}
          </p>
          <p className="muted small">{made.note}</p>
          <p className="muted small">
            Keep this. The list below can reopen the beacon on whatever API
            this console is pointed at, but only this card knows the address
            the code was minted with.
          </p>
        </div>
      )}

      <div className="card">
        <h3>Placed at</h3>
        {rows.length === 0 && (
          <p className="muted small">
            {me && token ? "Nowhere yet." : "Sign in as an owner."}
          </p>
        )}
        {rows.map((r) => (
          <div className="row" key={r.id}>
            <div style={{ flex: 1 }}>
              <strong>{r.label}</strong>
              <div className="muted small">
                {r.venue_name} · {r.scans} scan{r.scans === 1 ? "" : "s"}
                {!r.active && " · taken down"}
              </div>
            </div>
            {/* The list response carries no urls, so this is derived — and
                deliberately labelled "on this deployment", because the
                published link uses the configured public host and this one
                uses whatever API the console is pointed at. They are the
                same route on different hosts, and quietly calling this one
                "the link" would hand somebody the wrong address to print. */}
            <a href={`${getBase()}/b/${r.beacon_id}`} target="_blank"
               rel="noreferrer">open here</a>
            <button onClick={() => remove(r.id)}>Take down</button>
          </div>
        ))}
      </div>

      {stats && (
        <div className="card">
          <h3>What each venue brings</h3>
          <p className="muted small">
            Counts and rates only. Nobody who scans is identified, here or
            anywhere else.
          </p>
          {stats.venues.map((v) => (
            <div key={v.placement_id}>
              <h4>{v.venue_name} — {v.label}</h4>
              <p className="small">
                {v.scans} resolution{v.scans === 1 ? "" : "s"} ·{" "}
                {v.walled} reached the age wall · {v.verified} got through it
              </p>
              {v.by_day.length > 0 && (
                <p className="muted small">
                  {v.by_day.map((d) => `${d.day}: ${d.scans}`).join(" · ")}
                </p>
              )}
            </div>
          ))}
          <h4>Everything else</h4>
          <p className="muted small">
            Arrivals that did not come through a placement:{" "}
            {stats.direct.walled} walled, {stats.direct.verified} verified.
          </p>
          <h4>The funnel</h4>
          <p className="small">
            {stats.funnel.resolutions} resolutions →{" "}
            {stats.funnel.verified_views} verified views →{" "}
            {stats.funnel.unique_chatters} people who talked
          </p>
          <p className="muted small">
            {(stats.funnel.verified_rate * 100).toFixed(0)}% get through the
            wall.{" "}
            {/* Null, not zero, until something has. There is no rate yet, and
                saying "0%" would be a claim rather than an absence. */}
            {stats.funnel.chat_rate === null
              ? "Nothing has got through yet, so there is no conversion to quote."
              : `${(stats.funnel.chat_rate * 100).toFixed(0)}% of those talk.`}
          </p>
        </div>
      )}

      <div className="card">
        <h3>What is kept, and where</h3>
        {custody ? (
          <>
            {/* Lead with the part addressed to the person reading this
                screen. The backend's sentence names environment variables,
                which is the right message for whoever runs the deployment
                and not something a creator can act on — so it is kept, and
                kept second. */}
            <p className="small">
              This deployment has no vault, so nothing here is sealed. Rated
              resolutions are counted in the ordinary database.
            </p>
            <p className="muted small">Reported as: {custody}</p>
          </>
        ) : (
          <p className="muted small">
            Rated resolutions are sealed in the vault — so the record of who
            was age-checked is not this platform's to read.
          </p>
        )}
      </div>
    </div>
  );
}
