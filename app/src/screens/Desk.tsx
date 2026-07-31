import { useCallback, useEffect, useState } from "react";
import {
  api, getBase, type Desk as DeskRow, type DeskBeacon, type DeskGuest,
  type DeskOverlay, type DeskRing, type DeskScanCard, type LivePerson,
} from "../api";
import { Refusal } from "../Refusal";

// A staffed counter somebody can walk up to.
//
// The desk is the one surface in QRME where the promise is a *person*: a real
// tradesperson, attested by somebody, reachable now. All of it existed in the
// backend and none of it was reachable from a client — you could not open a
// desk, say whether anybody was behind it, answer the bell, or let a visitor
// come up.
//
// A desk is not a profile with a different name, and the API says so: it
// answers `desk_id` and `desk_token`, and holding a desk token is what makes
// you the desk rather than a visitor to it. The token is kept in component
// state rather than the shared session for that reason — signing in as an
// owner does not make you the desk, and conflating the two would let one
// person's session speak for a counter they do not staff.
export function Desk({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const [deskId, setDeskId] = useState("");
  const [deskToken, setDeskToken] = useState("");
  const [desk, setDesk] = useState<DeskRow | null>(null);
  const [rings, setRings] = useState<DeskRing[]>([]);
  const [guests, setGuests] = useState<DeskGuest[]>([]);
  const [overlay, setOverlay] = useState<DeskOverlay | null>(null);
  const [who, setWho] = useState<LivePerson | null>(null);
  const [beacons, setBeacons] = useState<DeskBeacon[]>([]);
  const [card, setCard] = useState<DeskScanCard | null>(null);

  const [form, setForm] = useState({
    owner_id: "", display_name: "", trade: "", attestor: "", basis: "",
    location: "", blurb: "",
  });
  const [label, setLabel] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [said, setSaid] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!deskId || !deskToken) return;
    api.deskRings(deskId, deskToken)
      .then((r) => setRings(r.rings ?? [])).catch(() => setRings([]));
    api.deskGuests(deskId, deskToken)
      .then((g) => setGuests(g.guests ?? [])).catch(() => setGuests([]));
    api.deskOverlay(deskId, deskToken).then(setOverlay).catch(() => setOverlay(null));
    api.deskBeacons(deskId, deskToken)
      .then((b) => setBeacons(b.beacons ?? [])).catch(() => setBeacons([]));
    api.deskLivePerson(deskId).then(setWho).catch(() => setWho(null));
  }, [deskId, deskToken]);
  useEffect(load, [load]);

  async function run(action: () => Promise<unknown>, ok?: string) {
    setBusy(true); setError(null); setSaid(null);
    try { await action(); if (ok) setSaid(ok); load(); }
    catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  const staffing = Boolean(desk && deskToken);

  return (
    <section className="screen">
      <h2>Desk</h2>
      <Refusal error={error} onPlans={onPlans} variant="inline" />
      {said && <p className="muted">{said}</p>}

      {!staffing && (
        <>
          <h3>Open a desk</h3>
          <p className="muted">
            A desk claims a person is behind it, so it is opened with who
            attests that and on what basis — a guild, a licence number. The
            claim is shown to every visitor and can be burned, which is why it
            is asked for at the start rather than added later.
          </p>
          <div className="row">
            <input placeholder="Your owner id" value={form.owner_id}
              onChange={(e) => setForm({ ...form, owner_id: e.target.value })} />
            <input placeholder="Name shown on the desk" value={form.display_name}
              onChange={(e) => setForm({ ...form, display_name: e.target.value })} />
            <input placeholder="Trade" value={form.trade}
              onChange={(e) => setForm({ ...form, trade: e.target.value })} />
          </div>
          <div className="row">
            <input placeholder="Who attests it" value={form.attestor}
              onChange={(e) => setForm({ ...form, attestor: e.target.value })} />
            <input placeholder="On what basis" value={form.basis}
              onChange={(e) => setForm({ ...form, basis: e.target.value })} />
            <input placeholder="Where (optional)" value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })} />
          </div>
          <button
            disabled={busy || !form.owner_id.trim() || !form.display_name.trim()
              || !form.trade.trim() || !form.attestor.trim() || !form.basis.trim()}
            onClick={() => run(async () => {
              const d = await api.openDesk({
                owner_id: form.owner_id.trim(),
                display_name: form.display_name.trim(),
                trade: form.trade.trim(),
                attestor: form.attestor.trim(),
                basis: form.basis.trim(),
                location: form.location.trim() || undefined,
                blurb: form.blurb.trim() || undefined,
              });
              setDesk(d);
              setDeskId(d.desk_id);
              // Shown once and held here only. It is the desk's credential,
              // not the person's.
              setDeskToken(d.desk_token ?? "");
            }, "Desk open.")}>
            Open the desk
          </button>

          <h3>Or take up a desk you already have</h3>
          <div className="row">
            <input placeholder="Desk id" value={deskId}
              onChange={(e) => setDeskId(e.target.value)} />
            <input type="password" placeholder="Desk token" value={deskToken}
              onChange={(e) => setDeskToken(e.target.value)} />
            <button disabled={busy || !deskId.trim() || !deskToken.trim()}
              onClick={() => run(async () => {
                const w = await api.deskLivePerson(deskId.trim());
                setWho(w);
                setDesk({ desk_id: deskId.trim(), display_name: w.whose ?? "",
                  trade: "", presence: "", rated: false });
              })}>
              Take it up
            </button>
          </div>
        </>
      )}

      {staffing && desk && (
        <>
          <div className="card">
            <div className="row">
              <strong>{desk.display_name}</strong>
              {desk.trade && <span className="muted">{desk.trade}</span>}
              {desk.location && <span className="muted">{desk.location}</span>}
              {desk.rated && <span className="pill">rated</span>}
            </div>
            {/* The attestation, shown to the desk's own keeper as well as to
                visitors. `burned` is the word the server uses for a claim that
                has been withdrawn, and it is worth showing loudly. */}
            {who && (
              <p className="muted">
                {who.real_person
                  ? `A real person: ${who.whose ?? "—"}`
                  : "No person attested."}
                {who.attestor ? ` · attested by ${who.attestor}` : ""}
                {who.attestation_basis ? ` (${who.attestation_basis})` : ""}
                {who.burned ? " · CLAIM BURNED" : ""}
              </p>
            )}
            {/* The frame a visitor is shown. It was never rendered anywhere
                in this console — the whole point of the `feed` block is a
                picture that carries its own honesty note, and the note was
                being served to nobody. `live` is false on a deployment with
                no camera, and the server says so in words rather than
                letting a sample frame pass for a live one. */}
            <img src={getBase() + `/desks/${deskId}/view.webp`}
                 width={240} alt="the view from this desk" />
            {desk.feed && (
              <p className="muted small">
                {desk.feed.live ? "Live." : "Not live."} {desk.feed.note}
                {desk.feed.watermark && ` · watermark: ${desk.feed.watermark}`}
              </p>
            )}
          </div>

          <h3>Is anybody there?</h3>
          <p className="muted">
            The one thing a visitor most wants to know. <em>Away</em> says come
            back; <em>closed</em> says the counter is shut. They are different
            promises and the desk gets to make either.
          </p>
          <div className="row">
            {["attended", "away", "closed"].map((p) => (
              <button key={p} disabled={busy || desk.presence === p}
                onClick={() => run(async () => {
                  setDesk(await api.setDeskPresence(deskId, p, deskToken));
                }, `Presence: ${p}.`)}>
                {desk.presence === p ? "✓ " : ""}{p}
              </button>
            ))}
          </div>

          <h3>The bell</h3>
          {rings.length === 0 && <p className="muted">Nobody has rung.</p>}
          {rings.map((r, i) => (
            <div key={String(r.id ?? i)} className="card">
              <div className="row">
                <span>{String(r.note ?? "rang the bell")}</span>
                {r.acked && <span className="muted">answered</span>}
              </div>
              {!r.acked && r.id && (
                <button disabled={busy}
                  onClick={() => run(() =>
                    api.ackRing(deskId, String(r.id), deskToken), "Answered.")}>
                  Answer
                </button>
              )}
            </div>
          ))}

          <h3>Who wants to come up</h3>
          {guests.length === 0 && <p className="muted">Nobody waiting.</p>}
          {guests.map((g, i) => (
            <div key={String(g.id ?? i)} className="card">
              <div className="row">
                <strong>{String(g.display_name ?? "someone")}</strong>
                {g.state && <span className="muted">{String(g.state)}</span>}
              </div>
              {g.note && <p className="muted">{String(g.note)}</p>}
              {g.id && g.state !== "accepted" && g.state !== "declined" && (
                <div className="row">
                  <button disabled={busy}
                    onClick={() => run(() =>
                      api.acceptGuest(deskId, String(g.id), deskToken),
                      "They are up.")}>
                    Let them up
                  </button>
                  <button disabled={busy}
                    onClick={() => run(() =>
                      api.declineGuest(deskId, String(g.id), deskToken),
                      "Declined.")}>
                    Not now
                  </button>
                </div>
              )}
            </div>
          ))}

          {overlay && (
            <>
              <h3>On the stream</h3>
              <p className="muted">
                {overlay.on_stream.length} up, {overlay.waiting.length} waiting ·
                {" "}{overlay.likes} likes · {overlay.comments} comments ·
                {" "}{overlay.shares} shares
                {overlay.gift_total > 0
                  ? ` · ${overlay.gift_total} in gifts` : ""}
                {" "}· laid out as a {overlay.style}
              </p>
              <button disabled={busy}
                onClick={() => run(() => api.stepDown(deskId, deskToken),
                  "Stepped down.")}>
                Step down from the stream
              </button>
            </>
          )}

          <h3>Look and camera</h3>
          <div className="row">
            <input placeholder="Portrait asset"
              onChange={(e) => setForm({ ...form, blurb: e.target.value })} />
            <button disabled={busy}
              onClick={() => run(async () => {
                setDesk(await api.setDeskPortrait(
                  deskId, form.blurb.trim() || null, deskToken));
              }, "Portrait set.")}>
              Set portrait
            </button>
            <button disabled={busy}
              onClick={() => run(async () => {
                setDesk(await api.setDeskCamera(deskId, null, deskToken));
              }, "Camera cleared.")}>
              Clear camera
            </button>
          </div>

          <h3>Beacons</h3>
          <p className="muted">
            The desk as a sticker: somebody scans it in the street and reaches
            this counter. Picking one up retires it — the sticker on the wall
            stops working, which is the point.
          </p>
          {beacons.map((b) => (
            <div key={b.id} className="card">
              <div className="row">
                <strong>{b.label}</strong>
                {b.location && <span className="muted">{b.location}</span>}
                <span className="muted">{b.scans} scan{b.scans === 1 ? "" : "s"}</span>
                {!b.active && <span className="muted">retired</span>}
              </div>
              {/* The picture to print. Fetching it is free; following the
                  link below it is not — the server counts that as a scan,
                  because it cannot tell the owner from a stranger. */}
              <img src={getBase() + `/desk-beacons/${b.id}/qr.svg`}
                   width={120} height={120} alt="this desk code's QR" />
              {/* Derived rather than taken from `b.scan_url`, which says the
                  same thing: the literal is what the route audit can read.
                  `scan_url` itself was a bare path until this link went to
                  use it and resolved against the console's own origin — it
                  is absolute now, and describes the address the printed code
                  actually carries rather than this deployment's. */}
              <a href={getBase() + `/d/${b.id}`} target="_blank"
                 rel="noreferrer">open it here (counts as a scan)</a>
              <span className="muted small">Printed: {b.scan_url}</span>
              {/* What a native app receives when its camera recognises this
                  code — the same scan as the page, shaped for drawing an
                  overlay in place. Offered because seeing it is the only way
                  to check what a scanner will actually be told. It counts as
                  a scan for the same reason the page does. */}
              <button disabled={busy}
                onClick={() => run(async () =>
                  setCard(await api.deskScanCard(b.id)))}>
                What a scanner sees
              </button>
              {b.active && (
                <button disabled={busy}
                  onClick={() => run(() =>
                    api.pickUpDeskBeacon(b.id, deskToken), "Picked up.")}>
                  Pick it up
                </button>
              )}
            </div>
          ))}
          <div className="row">
            <input value={label} placeholder="Label (Shop window)"
              onChange={(e) => setLabel(e.target.value)} />
            <button disabled={busy || !label.trim()}
              onClick={() => run(async () => {
                await api.placeDeskBeacon(deskId, { label: label.trim() },
                  deskToken);
                setLabel("");
              }, "Placed.")}>
              Place a beacon
            </button>
          </div>

          {card && (
            <div className="card">
              <h4>What a scanner sees</h4>
              <p className="small">
                {card.display_name} — {card.trade}
                {card.location && ` · ${card.location}`}
                <br />
                {/* The line that makes the whole desk feature honest, and
                    the one a scanner is shown first. */}
                <strong>{card.designation}</strong> · {card.presence}
              </p>
              {card.age_wall && (
                <p className="muted small">
                  This desk is rated, so a scan lands on the age wall. A
                  sticker carries no token that could clear it — that is the
                  right answer rather than a gap.
                </p>
              )}
              <p className="muted small">
                Attested by {card.attestation.attestor}:{" "}
                {card.attestation.basis}. {card.attestation.note}
              </p>
              <p className="muted small">{card.feed.note}</p>
              <p className="muted small">That read counted as a scan.</p>
            </div>
          )}
        </>
      )}
    </section>
  );
}
