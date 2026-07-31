import { useEffect, useState } from "react";
import { api, getBase, type SocialBeacon,
         type SocialConnection } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Where people find you: a code on a wall, and a code on a platform.
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
      <h2>Where people find you</h2>
      <p className="muted small">
        Two kinds of code, and they look the same. A placed beacon brings
        somebody <em>here</em>; a platform beacon sends them to an account
        somewhere else.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Connect a platform</h3>
        <p className="muted small">
          Two directions, never the same row. <strong>Collect</strong> pulls
          that account's content in to grow this profile.{" "}
          <strong>Publish</strong> runs the profile out on the platform. Kept
          apart so a read-only import can never also post.
        </p>
        <div className="row">
          <select value={platform} onChange={(e) => setPlatform(e.target.value)}>
            {["instagram", "x", "tiktok", "facebook", "linkedin", "youtube",
              "reddit", "threads", "mastodon", "twitch", "pinterest",
              "discord"].map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <select value={direction}
                  onChange={(e) => setDirection(e.target.value)}>
            <option value="publish">publish — run it out there</option>
            <option value="collect">collect — pull it in</option>
          </select>
          <input value={handle} onChange={(e) => setHandle(e.target.value)}
                 placeholder="the handle, without the @" style={{ flex: 1 }} />
          <button disabled={busy || !me || !token}
                  onClick={act(async () => {
                    await api.connectSocial(me, {
                      platform, direction,
                      handle: handle.trim() || undefined }, token);
                    setHandle("");
                  }, "Connected.")}>Connect</button>
        </div>
        <p className="muted small">
          Without a handle the beacon has no account page to point at, so it
          falls back to a QRME summon link — still a working code, but it
          brings people here rather than to the platform.
        </p>
      </div>

      <div className="card">
        <h3>Connected</h3>
        {conns.length === 0 && <p className="muted small">Nothing yet.</p>}
        {conns.map((c) => (
          <div key={c.id}>
            <p className="small">
              <strong>{c.platform}</strong> — {c.direction}
              {c.handle && ` · ${c.handle}`} · {c.status}
              <br />
              <span className="muted">
                {c.collected} collected · {c.published} published
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
                  show its code
                </button>
              )}
              <button className="chip" disabled={busy}
                      onClick={act(() => api.disconnectSocial(c.id, token),
                        "Disconnected.")}>
                disconnect
              </button>
            </div>
          </div>
        ))}
      </div>

      {beacon && (
        <div className="card">
          <h3>The code for {beacon.platform}</h3>
          {/* Free to fetch. The scan surfaces are not — see below. */}
          <img src={getBase() + `/social/${beacon.connection}/qr.svg`}
               width={180} height={180}
               alt="the QR code for this platform presence" />
          <p className="small">
            Scanning it opens{" "}
            <code>{beacon.presence_url}</code>
            {beacon.handle
              ? ` — ${beacon.handle} on ${beacon.platform}.`
              : " — a QRME summon page, because this connection has no "
                + "handle to build a platform link from."}
          </p>
          <p className="muted small">
            This code carries people <em>away</em> from QRME. A placed beacon
            does the opposite. Same picture, opposite destination.
          </p>
        </div>
      )}

      <div className="card">
        <h3>What a scan costs to check</h3>
        <p className="muted small">
          A QR image is free to ask for — fetching the picture is not a scan.
          Opening the page it points to <em>is</em> one, and every scan
          surface counts it, because the server cannot tell an owner checking
          their own sticker from a stranger who found it. There is no preview
          that doesn't count.
        </p>
        <p className="muted small">
          So no screen here opens a scan page on its own. The links on{" "}
          <strong>Placements</strong> and on a desk are deliberate presses,
          and following one adds to the number you were checking. The desk
          code also has a JSON twin — the same scan shaped for a native app
          drawing the overlay in place rather than for a browser — and it
          counts the same.
        </p>
      </div>
    </div>
  );
}
