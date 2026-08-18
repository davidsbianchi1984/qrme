import { useCallback, useEffect, useRef, useState } from "react";
import { api, FeedItem, getBase } from "../api";
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
export function Feed({ onPlans, onParty }: {
  onPlans: () => void;
  /** Where a joined party opens. Joining from a card must land the person
   *  in the room, not leave them in the feed having joined invisibly. */
  onParty?: (partyId: string) => void;
}) {
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
  const panes = useRef<(HTMLElement | null)[]>([]);

  // Whether footage held elsewhere may load without being asked for.
  //
  // Off, and a card from another platform stays a facade until it is
  // pressed — which is the sentence the feed prints about itself. On, and
  // the deck plays everything as it arrives, which means every item scrolled
  // past is a request that tells that platform somebody watched.
  //
  //     asked     does the feed feel like a feed
  //     mattered  does scrolling past something tell anybody
  //
  // Kept on the device rather than on the profile, deliberately: this is a
  // fact about what this browser fetches, not a fact about who somebody is,
  // and it should not follow them onto a machine they did not choose it on.
  const [autoOffsite, setAutoOffsite] = useState(
    () => window.localStorage.getItem("feed.autoplay.offsite") === "yes");

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
      panes.current[next]?.scrollIntoView({ behavior: "smooth" });
      return next;
    });
  }, [items.length, cursor, busy, load]);

  // Which pane the person is actually looking at. Read from the scroll
  // position rather than only from the buttons, because a swipe moves the
  // deck without asking this component anything — and the answer decides
  // which single video is playing.
  useEffect(() => {
    const deck = frame.current;
    if (!deck) return;
    const watching = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const seen = panes.current.indexOf(entry.target as HTMLElement);
        if (seen >= 0) {
          setAt(seen);
          if (cursor && seen >= items.length - 2 && !busy) load(cursor);
        }
      }
    }, { root: deck, threshold: 0.6 });
    for (const pane of panes.current) if (pane) watching.observe(pane);
    return () => watching.disconnect();
  }, [items.length, cursor, busy, load]);

  useEffect(() => {
    function key(e: KeyboardEvent) {
      if (e.key === "ArrowDown" || e.key === "PageDown") { e.preventDefault(); go(1); }
      if (e.key === "ArrowUp" || e.key === "PageUp") { e.preventDefault(); go(-1); }
    }
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [go]);


  return (
    <div className="screen screen-deck">
      {error != null && <Refusal error={error} onPlans={onPlans} />}

      {items.length === 0 && !busy && (
        <div className="card">
          <p className="muted small">{tr("feed.empty", lang)}</p>
        </div>
      )}

      <div className="deck" ref={frame}>
      {items.map((item, index) => (
        <section key={item.id}
                 className={"deck-pane" + (item.kind === "video"
                   || item.kind === "offsite" ? " deck-pane-full" : "")}
                 ref={(el) => { panes.current[index] = el; }}>
          <div className="row deck-head">
            <span className="pill">{tr(`feed.kind.${item.kind}`, lang)}</span>
            <span className="muted small" style={{ flex: 1 }}>{item.reason}</span>
            <span className="muted small">{index + 1} / {items.length}</span>
          </div>

          {item.kind === "video" && (
            <>
              {/* Footage this deployment holds, so playing it asks nobody
                  anything. Only the pane being looked at gets a decoder:
                  a deck that plays every video it has loaded is a phone
                  that gets warm and a battery that goes. */}
              {/* The stream hands `/media/{id}` relative to the API, and
                  this document lives on the console origin — resolved bare,
                  the request went to a host that has no media and the pane
                  stayed black. The wall resolved it correctly all along,
                  which is exactly how the report read: only on my wall. */}
              <div className="deck-media">
                {Math.abs(index - at) <= 1 ? (
                  <video src={getBase() + (item.src || "")} loop muted playsInline
                         autoPlay={index === at}
                         ref={(el) => {
                           if (!el) return;
                           if (index === at) void el.play().catch(() => {});
                           else el.pause();
                         }} />
                ) : null}
              </div>
              <div className="deck-said">
                <p><strong>{item.title}</strong></p>
                <p className="muted small">{item.said}</p>
                <p className="muted small">{item.note}</p>
              </div>
            </>
          )}

          {item.kind === "offsite" && (
            <>
              {/* No frame, no thumbnail, no request — until this button, or
                  until the person turned that requirement off themselves.
                  The frame is only built for the pane in front of them, so
                  scrolling past an item is not a request either way. */}
              <div className="deck-media">
                {(playing[item.id] || autoOffsite) && index === at ? (
                  <iframe title={item.title} src={item.facade?.url}
                          allow="autoplay; encrypted-media; picture-in-picture"
                          /* The document sends no referrer at all, which is
                             right for a page reached from a QR sticker and
                             wrong here: a player handed no origin cannot
                             check whether it may embed on this site, and
                             YouTube answers `Error 153` rather than play.
                             Origin only — the host, never the path. */
                          referrerPolicy="strict-origin-when-cross-origin"
                          style={{ width: "100%", height: "100%", border: 0 }} />
                ) : (
                  <div className="deck-facade">
                    <p><strong>{item.title}</strong></p>
                    <p className="muted small">{item.facade?.platform_name}</p>
                    <button className="primary"
                            onClick={() => setPlaying((p) => ({ ...p, [item.id]: true }))}>
                      {tr("feed.play", lang)}
                    </button>
                  </div>
                )}
              </div>
              <div className="deck-said">
                <p className="muted small">{item.note}</p>
              </div>
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

          {item.kind === "party" && (
            <>
              <p><strong>{item.title || tr("feed.room.untitled", lang)}</strong></p>
              <p className="muted small">
                {item.video?.platform_name}
                {typeof item.people === "number" ? ` · ${item.people}` : ""}
              </p>
              {/* Before the button. Joining puts your name in the room. */}
              <p className="muted small">{item.joining}</p>
              <button className="primary"
                      disabled={busy || !session.interactorId || !session.interactorToken}
                      onClick={() => api.joinWatchParty(item.id, {
                        member_id: session.interactorId!,
                      }, session.interactorToken!)
                        .then(() => onParty?.(item.id))
                        .catch((e) => setError(e))}>
                {tr("feed.joinparty", lang)}
              </button>
            </>
          )}

          {/* The swipe is the way through. These stay for the keyboard, the
              mouse, and anybody whose gesture does not land. */}
          <div className="row deck-steps">
            <button disabled={index === 0} onClick={() => go(-1)}>
              {tr("feed.back", lang)}
            </button>
            <button className="primary" onClick={() => go(1)}>
              {tr("feed.next", lang)}
            </button>
          </div>
        </section>
      ))}

      {rules && (
        <section className="deck-pane deck-rules"
                 ref={(el) => { panes.current[items.length] = el; }}>
          <div className="card">
            <h2 style={{ margin: "0 0 2px" }}>{tr("feed.title", lang)}</h2>
            <p className="muted small">{tr("feed.sub", lang)}</p>
            <p className="muted small">{rules.public}</p>
            <p className="muted small">{rules.facade}</p>
            <label className="row">
              <input type="checkbox" checked={autoOffsite}
                     onChange={(e) => {
                       setAutoOffsite(e.target.checked);
                       window.localStorage.setItem(
                         "feed.autoplay.offsite", e.target.checked ? "yes" : "no");
                     }} />
              <span style={{ flex: 1 }}>{tr("feed.autoplay", lang)}</span>
            </label>
            <p className="muted small">{tr("feed.autoplay.cost", lang)}</p>
          </div>
        </section>
      )}
      </div>
    </div>
  );
}
