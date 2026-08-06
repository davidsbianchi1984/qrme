import { useCallback, useEffect, useRef, useState } from "react";
import { api, FeedItem } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The feed: one card at a time, swipe for the next.
 *
 * Three kinds of card come back from `/feed` — footage this deployment holds,
 * a facade for footage it does not, a live room, and a desk with a person
 * behind it. This screen renders what the server sent and decides nothing
 * about it, and that is the point of two fields in particular:
 *
 *   * **`plays`** is the server's. Only footage QRME holds comes back `true`.
 *     Everything else stays a card until somebody presses it, so that flicking
 *     past fifty videos does not announce this viewer to fifty other
 *     companies. A client that autoplayed on its own would undo the promise
 *     `qrme/db.py` makes about `post_videos`, so the flag is read here and
 *     never overridden — see `qrme/feed.py`.
 *
 *   * **`entering` and `ringing`** are shown *before* the button, not after.
 *     A live room and a desk reach a human being; a person who swipes into one
 *     should know that walking in puts them in the room.
 *
 * Keyboard as well as pointer: this is a desktop console, and a stream you can
 * only use by dragging is a stream somebody on a keyboard cannot use at all.
 */
export function Feed({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const [items, setItems] = useState<FeedItem[]>([]);
  const [rules, setRules] = useState<{ plays: string; facade: string;
                                       public: string } | null>(null);
  const [cursor, setCursor] = useState<string | null>(null);
  const [at, setAt] = useState(0);
  const [playing, setPlaying] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const frame = useRef<HTMLDivElement | null>(null);

  const load = useCallback((after?: string | null) => {
    setBusy(true);
    api.publicFeed(after ?? undefined, session.profileId ?? undefined)
      .then((r) => {
        setItems((prev) => (after ? [...prev, ...r.items] : r.items));
        setCursor(r.cursor);
        setRules(r.rules);
      })
      .catch((e) => setError(e))
      .finally(() => setBusy(false));
  }, [session.profileId]);

  useEffect(() => { load(null); }, [load]);

  // A link somebody was sent. `#feed/<id>` opens that card first and the
  // stream continues underneath it, so a shared item is a place in the feed
  // rather than a page of its own — and it is fetched through `/feed/{id}`,
  // which applies the same rules as the stream. A rated item a reader is not
  // verified for 404s there rather than arriving as an empty card.
  useEffect(() => {
    const shared = /^#feed\/(.+)$/.exec(window.location.hash);
    if (!shared) return;
    let live = true;
    api.publicFeedItem(shared[1])
      .then((one) => {
        if (!live) return;
        setItems((prev) => [one, ...prev.filter((i) => i.id !== one.id)]);
        setAt(0);
      })
      .catch((e) => { if (live) setError(e); });
    return () => { live = false; };
  }, []);

  const go = useCallback((delta: number) => {
    setAt((i) => {
      const next = Math.max(0, Math.min(items.length - 1, i + delta));
      // One page ahead of the end, so the swipe never waits on the network.
      if (cursor && next >= items.length - 2 && !busy) load(cursor);
      return next;
    });
  }, [items.length, cursor, busy, load]);

  useEffect(() => {
    function key(e: KeyboardEvent) {
      if (e.key === "ArrowDown" || e.key === "PageDown") { e.preventDefault(); go(1); }
      if (e.key === "ArrowUp" || e.key === "PageUp") { e.preventDefault(); go(-1); }
    }
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [go]);

  const item = items[at];

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("feed.title", lang)}</h2>
        <span className="muted small">{tr("feed.sub", lang)}</span>
      </header>

      {error != null && <Refusal error={error} onPlans={onPlans} />}

      {items.length === 0 && !busy && (
        <div className="card">
          <p className="muted small">{tr("feed.empty", lang)}</p>
        </div>
      )}

      {item && (
        <div className="card feed-card" ref={frame}
             onWheel={(e) => { if (Math.abs(e.deltaY) > 24) go(e.deltaY > 0 ? 1 : -1); }}>
          <div className="row">
            <span className="pill">{tr(`feed.kind.${item.kind}`, lang)}</span>
            <span className="muted small" style={{ flex: 1 }}>{item.reason}</span>
            <span className="muted small">{at + 1} / {items.length}</span>
          </div>

          {item.kind === "video" && (
            <>
              <video src={item.src} loop autoPlay muted playsInline
                     style={{ width: "100%", borderRadius: 8 }} />
              <p><strong>{item.title}</strong></p>
              <p className="muted small">{item.said}</p>
              <p className="muted small">{item.note}</p>
            </>
          )}

          {item.kind === "offsite" && (
            <>
              {/* No frame, no thumbnail, no request — until this button. */}
              {playing[item.id] ? (
                <iframe title={item.title} src={item.facade?.url}
                        style={{ width: "100%", aspectRatio: "16 / 9",
                                 border: 0, borderRadius: 8 }} />
              ) : (
                <div className="facade">
                  <p><strong>{item.title}</strong></p>
                  <p className="muted small">{item.facade?.platform_name}</p>
                  <button className="primary"
                          onClick={() => setPlaying((p) => ({ ...p, [item.id]: true }))}>
                    {tr("feed.play", lang)}
                  </button>
                </div>
              )}
              <p className="muted small">{item.note}</p>
            </>
          )}

          {item.kind === "room" && (
            <>
              <p><strong>{item.topic || tr("feed.room.untitled", lang)}</strong></p>
              <p className="muted small">
                {item.channel} · {item.people} · {item.display_name}
              </p>
              {/* Before the button, deliberately. */}
              <p className="muted small">{item.entering}</p>
              <button className="primary"
                      onClick={() => item.enter && window.open(item.enter, "_self")}>
                {tr("feed.enter", lang)}
              </button>
            </>
          )}

          {item.kind === "desk" && (
            <>
              <p><strong>{item.display_name}</strong> — {item.trade}</p>
              <p className="muted small">
                {item.presence}{item.location ? ` · ${item.location}` : ""}
                {item.live ? ` · ${tr("feed.desk.live", lang)}` : ""}
              </p>
              {item.blurb && <p>{item.blurb}</p>}
              <p className="muted small">{item.ringing}</p>
              <div className="row">
                <button className="primary" disabled={busy}
                        onClick={() => api.ringBell(item.id, {
                          caller_id: session.profileId,
                        }).catch((e) => setError(e))}>
                  {tr("feed.ring", lang)}
                </button>
              </div>
              {item.shop && (
                <div className="card">
                  <p><strong>{item.shop.name}</strong></p>
                  {item.shop.blurb && <p className="muted small">{item.shop.blurb}</p>}
                  {item.shop.offerings.map((o) => (
                    <div key={o.id} className="row">
                      <span style={{ flex: 1 }}>{o.title}</span>
                      <span className="muted small">
                        {o.price} {o.currency}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          <div className="row">
            <button disabled={at === 0} onClick={() => go(-1)}>
              {tr("feed.back", lang)}
            </button>
            <button className="primary" onClick={() => go(1)}>
              {tr("feed.next", lang)}
            </button>
          </div>
        </div>
      )}

      {rules && (
        <div className="card">
          <p className="muted small">{rules.public}</p>
          <p className="muted small">{rules.facade}</p>
        </div>
      )}
    </div>
  );
}
