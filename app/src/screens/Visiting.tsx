import { useState } from "react";
import { api, type BeaconScanCard, type BellRung, type DeskCard,
         type DeskGuest, type DeskJoined, type PlacedBeacon,
         type ProfileBeacon } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The other side of a desk, and leaving a profile somewhere.
 *
 * `Desk` is the host's console: open a desk, set your presence, point the
 * camera, read who rang, bring a guest up. Every route it calls is owner-only.
 * There was no visitor's side at all — and the visitor is the person the whole
 * feature is *for*. Somebody standing in front of an empty chair with a sign
 * on it saying to ring the bell could not, from here, see the card, ring it,
 * or join the stream.
 *
 * `askToComeUp` had been written months ago and no screen ever called it.
 *
 * ## What the room was, before anyone was allowed in
 *
 * Joining as a `guest` needs an account: the host is deciding about a person,
 * not an anonymous request. The route said so and answered `401`. It also
 * minted the stream's room first — a real row, committed — and *then* checked
 * who was asking. So a refused anonymous request left a room behind it.
 *
 * `ask_to_come_up`, the very next route in the same file, already had the
 * order right: gate the rating, identify the caller, then write. A caller we
 * are about to turn away should not be able to change what is stored on the
 * way out.
 *
 * ## Two families of sticker
 *
 * A desk beacon points at a live person. A profile beacon points at a
 * profile. Both print as a QR code and they are easy to confuse, so they are
 * kept visibly apart here.
 *
 * All three profile-beacon routes are owner-only, and each check exists
 * because the route shipped without it. Placing was anybody's, so a stranger
 * could print stickers pointing at somebody else's profile in places its
 * owner never chose and cannot see. The list carries free text like *the back
 * table at the Tuesday meeting* — a list of physical places a person
 * frequents — readable from the profile id alone. And picking one up was a
 * way to switch off somebody else's stickers, with the paper still on the
 * wall and nothing to see wrong with it.
 */
export function Visiting() {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const ownerToken = session.ownerToken || "";
  const visitorToken = session.interactorToken || "";

  const [error, setError] = useState<unknown>(null);
  const [said, setSaid] = useState("");

  // Visiting somebody's desk
  const [deskId, setDeskId] = useState("");
  const [card, setCard] = useState<DeskCard | null>(null);
  const [note, setNote] = useState("");
  const [rung, setRung] = useState<BellRung | null>(null);
  const [joined, setJoined] = useState<DeskJoined | null>(null);
  const [hand, setHand] = useState<DeskGuest | null>(null);
  const [why, setWhy] = useState("");

  // Leaving this profile somewhere
  const [placed, setPlaced] = useState<PlacedBeacon[]>([]);
  const [fresh, setFresh] = useState<ProfileBeacon | null>(null);
  const [label, setLabel] = useState("");
  const [where, setWhere] = useState("");
  const [mode, setMode] = useState("chat");

  // Scanning one
  const [scanId, setScanId] = useState("");
  const [scanned, setScanned] = useState<BeaconScanCard | null>(null);

  async function go<T>(work: () => Promise<T>, then: (v: T) => void) {
    setError(null);
    try { then(await work()); } catch (e) { setError(e); }
  }

  const beacons = () =>
    go(() => api.profileBeacons(me, ownerToken), setPlaced);

  return (
    <div className="screen">
      <h2>{tr("vis.title", lang)}</h2>
      <p className="muted">{tr("vis.lead", lang)}</p>
      <Refusal error={error} />
      {said && <p className="small">{said}</p>}

      {/* --- the visitor's side ---------------------------------------- */}
      <div className="card">
        <h3>{tr("vis.desk", lang)}</h3>
        <p className="muted small">{tr("vis.desk.pitch", lang)}</p>
        <input value={deskId} onChange={(e) => setDeskId(e.target.value)}
               placeholder={tr("vis.desk.ph", lang)} />
        <button disabled={!deskId}
                onClick={() => go(() => api.visitDesk(deskId), (c) => {
                  setCard(c); setRung(null); setJoined(null); setHand(null);
                })}>{tr("vis.look", lang)}</button>

        {card && (
          <div>
            <p className="small">
              <strong>{card.display_name}</strong> — {card.trade}
              {card.location && <span className="muted"> · {card.location}</span>}
            </p>
            {/* The inversion of the mark every synthetic profile carries, and
                the sentence the whole desk feature rests on. */}
            <p className="small"><strong>{card.designation}</strong></p>
            <p className="muted small">
              {card.presence === "attended"
                ? tr("vis.here", lang) : tr("vis.away", lang)}
            </p>
            <p className="muted small">
              {fill(tr("vis.attested", lang), {
                who: card.attestation.attestor,
                basis: card.attestation.basis,
              })}{" "}
              {card.attestation.signed
                ? tr("vis.signed", lang) : tr("vis.recorded", lang)}
            </p>
            {card.age_wall && (
              <p className="muted small">{tr("vis.agewall", lang)}</p>
            )}
          </div>
        )}
      </div>

      {card && !card.age_wall && (
        <div className="card">
          <h3>{tr("vis.ring", lang)}</h3>
          <input value={note} onChange={(e) => setNote(e.target.value)}
                 placeholder={tr("vis.note.ph", lang)} />
          <button onClick={() => go(
            () => api.ringBell(deskId, note ? { note } : {}),
            (r) => { setRung(r); setSaid(r.note); })}>
            {tr("vis.ringbell", lang)}
          </button>
          {rung && (
            <p className="muted small">
              {rung.waiting === 1
                ? tr("vis.waiting.one", lang)
                : fill(tr("vis.waiting.n", lang), { n: rung.waiting })}
            </p>
          )}

          <button onClick={() => go(
            () => api.joinDesk(deskId, "audience"), setJoined)}>
            {tr("vis.watch", lang)}
          </button>
          {joined && (
            <p className="muted small">
              {fill(tr("vis.inroom", lang), {
                room: joined.room_id,
                likes: joined.overlay.likes,
                comments: joined.overlay.comments.length,
              })}
            </p>
          )}

          <h4>{tr("vis.hand", lang)}</h4>
          <p className="muted small">
            {fill(tr("vis.hand.pitch", lang),
              { on: <em>{tr("vis.hand.on", lang)}</em> })}
          </p>
          <input value={why} onChange={(e) => setWhy(e.target.value)}
                 placeholder={tr("vis.why.ph", lang)} />
          {!visitorToken && (
            <p className="muted small">{tr("vis.notvisitor", lang)}</p>
          )}
          <button disabled={!visitorToken} onClick={() => go(
            () => api.askToComeUp(deskId, { note: why }, visitorToken),
            (g) => { setHand(g); setSaid(tr("vis.hand.said", lang)); })}>
            {tr("vis.askup", lang)}
          </button>
          {hand && (
            <p className="muted small">
              {hand.status === "requested"
                ? tr("vis.hand.wait", lang)
                : fill(tr("vis.hand.status", lang), { status: hand.status })}
              {hand.on_stream && tr("vis.hand.onstream", lang)}
            </p>
          )}
        </div>
      )}

      {/* --- leaving your profile somewhere ---------------------------- */}
      <div className="card">
        <h3>{tr("vis.leave", lang)}</h3>
        <p className="muted small">{tr("vis.leave.pitch", lang)}</p>
        <input value={label} onChange={(e) => setLabel(e.target.value)}
               placeholder={tr("vis.label.ph", lang)} />
        <input value={where} onChange={(e) => setWhere(e.target.value)}
               placeholder={tr("vis.where.ph", lang)} />
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="chat">{tr("vis.mode.chat", lang)}</option>
          <option value="room">{tr("vis.mode.room", lang)}</option>
        </select>
        <p className="muted small">{tr("vis.room.pitch", lang)}</p>
        <button disabled={!me || !ownerToken || !label}
                onClick={() => go(
                  () => api.placeBeacon(me, {
                    label, ...(where ? { location: where } : {}), mode,
                  }, ownerToken),
                  (b) => { setFresh(b); setSaid(tr("vis.placed.said", lang));
                           beacons(); })}>
          {tr("vis.place", lang)}
        </button>
        {fresh && (
          <p className="muted small">
            {fill(tr("vis.print", lang),
              { url: <code>{fresh.scan_url}</code> })}
            {fresh.room_id && tr("vis.oneroom", lang)}
          </p>
        )}

        <button className="ghost" disabled={!me || !ownerToken}
                onClick={beacons}>{tr("vis.already", lang)}</button>
        {placed.map((b) => (
          <div key={b.id} className="row">
            <div>
              <p className="small">
                <strong>{b.label}</strong>
                {b.location && <span className="muted"> · {b.location}</span>}
                {!b.active &&
                  <span className="muted"> {tr("vis.pickedup", lang)}</span>}
              </p>
              <p className="muted small">
                {b.scans === 0 ? tr("vis.scans.none", lang)
                  : fill(tr("vis.scans.n", lang),
                         { n: b.scans, s: b.scans === 1 ? "" : "s" })}
                {b.room_id && tr("vis.sharedroom", lang)}
              </p>
            </div>
            {b.active && (
              <button className="ghost" onClick={() => go(
                () => api.pickUpBeacon(b.id, ownerToken),
                () => { setSaid(tr("vis.pickedup.said", lang));
                        beacons(); })}>
                {tr("vis.pickup", lang)}
              </button>
            )}
          </div>
        ))}
      </div>

      {/* --- what a scanner gets --------------------------------------- */}
      <div className="card">
        <h3>{tr("vis.scan", lang)}</h3>
        <p className="muted small">
          {fill(tr("vis.scan.pitch", lang),
            { with: <em>{tr("vis.scan.with", lang)}</em> })}
        </p>
        <input value={scanId} onChange={(e) => setScanId(e.target.value)}
               placeholder={tr("vis.beacon.ph", lang)} />
        <button disabled={!scanId} onClick={() => go(
          () => api.beaconCard(scanId), setScanned)}>
          {tr("vis.scanit", lang)}
        </button>
        {scanned && (scanned.age_wall ? (
          <p className="muted small">
            {scanned.note || tr("vis.scan.wall.default", lang)}{" "}
            {tr("vis.scan.wall", lang)}
          </p>
        ) : (
          <div>
            <p className="small">
              <strong>{scanned.display_name}</strong>
              {scanned.label && <span className="muted"> · {scanned.label}</span>}
            </p>
            <p className="small">{scanned.watermark}</p>
            <p className="muted small">
              {scanned.portrait_marked
                ? tr("vis.marked", lang) : tr("vis.unmarked", lang)}
              {scanned.shared_room && tr("vis.scan.sharedroom", lang)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
