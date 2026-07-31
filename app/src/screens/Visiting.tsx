import { useState } from "react";
import { api, type BeaconScanCard, type BellRung, type DeskCard,
         type DeskGuest, type DeskJoined, type PlacedBeacon,
         type ProfileBeacon } from "../api";
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
      <h2>Visiting, and being found</h2>
      <p className="muted">
        Two halves of the same idea: standing in front of somebody else's
        desk, and leaving your own profile somewhere for a stranger to find.
      </p>
      <Refusal error={error} />
      {said && <p className="small">{said}</p>}

      {/* --- the visitor's side ---------------------------------------- */}
      <div className="card">
        <h3>Stand in front of a desk</h3>
        <p className="muted small">
          The card is public — a desk is a shopfront. So is the bell: the
          visitor at an empty chair is exactly the person who has no account
          yet. An 18+ stream is the one exception, because an anonymous ping
          channel to an adult performer is not something to hand out.
        </p>
        <input value={deskId} onChange={(e) => setDeskId(e.target.value)}
               placeholder="a desk id, or scan the code on the counter" />
        <button disabled={!deskId}
                onClick={() => go(() => api.visitDesk(deskId), (c) => {
                  setCard(c); setRung(null); setJoined(null); setHand(null);
                })}>Look</button>

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
                ? "They are here."
                : "They are away — ring the bell and they will see it."}
            </p>
            <p className="muted small">
              Attested by {card.attestation.attestor}: “
              {card.attestation.basis}”.{" "}
              {card.attestation.signed
                ? "Signed, so it can be checked."
                : "Recorded, not proven — nobody has signed for it."}
            </p>
            {card.age_wall && (
              <p className="muted small">
                18+ — sign in with a verified adult account to see any of it.
              </p>
            )}
          </div>
        )}
      </div>

      {card && !card.age_wall && (
        <div className="card">
          <h3>Ring, or come in</h3>
          <input value={note} onChange={(e) => setNote(e.target.value)}
                 placeholder="anything you want them to see (optional)" />
          <button onClick={() => go(
            () => api.ringBell(deskId, note ? { note } : {}),
            (r) => { setRung(r); setSaid(r.note); })}>Ring the bell</button>
          {rung && (
            <p className="muted small">
              {rung.waiting === 1
                ? "You are the only one waiting."
                : `${rung.waiting} waiting, including you.`}
            </p>
          )}

          <button onClick={() => go(
            () => api.joinDesk(deskId, "audience"), setJoined)}>
            Watch the stream
          </button>
          {joined && (
            <p className="muted small">
              In room {joined.room_id}. {joined.overlay.likes} likes,{" "}
              {joined.overlay.comments.length} comments over the picture.
              {" "}Never marked as AI: there is a real person on the other end.
            </p>
          )}

          <h4>Put a hand up</h4>
          <p className="muted small">
            Coming up <em>on</em> the stream is the host's call, so this asks
            rather than does — and it needs an account, because the host is
            deciding about a person rather than an anonymous request. Nothing
            is minted until you are somebody.
          </p>
          <input value={why} onChange={(e) => setWhy(e.target.value)}
                 placeholder="why you would like to come up" />
          {!visitorToken && (
            <p className="muted small">
              You are not signed in as a visitor, so this would be refused.
            </p>
          )}
          <button disabled={!visitorToken} onClick={() => go(
            () => api.askToComeUp(deskId, { note: why }, visitorToken),
            (g) => { setHand(g); setSaid("Hand up. Nothing happens until "
                                         + "they accept."); })}>
            Ask to come up
          </button>
          {hand && (
            <p className="muted small">
              {hand.status === "requested"
                ? "Waiting on the host."
                : `Status: ${hand.status}.`}
              {hand.on_stream && " You are on the stream."}
            </p>
          )}
        </div>
      )}

      {/* --- leaving your profile somewhere ---------------------------- */}
      <div className="card">
        <h3>Leave this profile somewhere</h3>
        <p className="muted small">
          A printed code on a bench, at a meeting, on a counter. Where a
          profile is left is a decision about the profile — a recovery
          sponsor's code belongs at a meeting and not on a billboard — so only
          its owner may place one, list them, or pick one back up.
        </p>
        <input value={label} onChange={(e) => setLabel(e.target.value)}
               placeholder="what to call it" />
        <input value={where} onChange={(e) => setWhere(e.target.value)}
               placeholder="where it is going" />
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="chat">a private thread each</option>
          <option value="room">one room everybody joins</option>
        </select>
        <p className="muted small">
          One room means the people who found the same sticker end up talking
          to it together. A rated profile is placed one-to-one and asking for
          a room is refused rather than quietly downgraded.
        </p>
        <button disabled={!me || !ownerToken || !label}
                onClick={() => go(
                  () => api.placeBeacon(me, {
                    label, ...(where ? { location: where } : {}), mode,
                  }, ownerToken),
                  (b) => { setFresh(b); setSaid("Placed."); beacons(); })}>
          Place it
        </button>
        {fresh && (
          <p className="muted small">
            Print <code>{fresh.scan_url}</code> — that is what the QR encodes.
            {fresh.room_id && " Everyone who scans it lands in one room."}
          </p>
        )}

        <button className="ghost" disabled={!me || !ownerToken}
                onClick={beacons}>Where it is already</button>
        {placed.map((b) => (
          <div key={b.id} className="row">
            <div>
              <p className="small">
                <strong>{b.label}</strong>
                {b.location && <span className="muted"> · {b.location}</span>}
                {!b.active && <span className="muted"> · picked up</span>}
              </p>
              <p className="muted small">
                {b.scans === 0 ? "Not scanned yet"
                  : `${b.scans} scan${b.scans === 1 ? "" : "s"}`}
                {b.room_id && " · one shared room"}
              </p>
            </div>
            {b.active && (
              <button className="ghost" onClick={() => go(
                () => api.pickUpBeacon(b.id, ownerToken),
                () => { setSaid("Picked up. The paper is still on the wall, "
                                + "so the code keeps answering — with "
                                + "nothing."); beacons(); })}>
                Pick it up
              </button>
            )}
          </div>
        ))}
      </div>

      {/* --- what a scanner gets --------------------------------------- */}
      <div className="card">
        <h3>What a stranger sees when they scan it</h3>
        <p className="muted small">
          The overlay draws this over the sticker in the live viewfinder —
          nobody has navigated anywhere and the camera is still running. The
          mark travels <em>with</em> the card, so a surface cannot draw the
          face without also having been handed the disclosure to draw with it.
        </p>
        <input value={scanId} onChange={(e) => setScanId(e.target.value)}
               placeholder="a beacon id" />
        <button disabled={!scanId} onClick={() => go(
          () => api.beaconCard(scanId), setScanned)}>Scan it</button>
        {scanned && (scanned.age_wall ? (
          <p className="muted small">
            {scanned.note || "18+ — open in QRME with a verified adult "
              + "account."} Nothing else came back: not the name, not the
            portrait. The wall is drawn without ever holding what it refuses.
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
                ? "The disclosure is already in the image."
                : "The image is unmarked, so the badge must be composited over it."}
              {scanned.shared_room && " Scanning joins one shared room."}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
