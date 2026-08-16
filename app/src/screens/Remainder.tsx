import { useEffect, useState } from "react";
import { api, uploadMedia, type AppConnector, type ConnectorCatalogue,
         type Excursion, type FeedbackBoard, type GameSession, type Inquiry,
         type PackDetail, type Visited,
         type PackRegistry, type SocialPublished, type SteeringHub } from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The last eighteen.
 *
 * Six small features that each had a couple of routes and no door, kept
 * together on one screen because that is honestly what they are — the tail of
 * the audit rather than a coherent product area. Feedback on the app, mod
 * registries, connected apps, excursions, the steering hub, playing alongside
 * somebody, and the two halves of a social connection.
 *
 * ## The one that mattered
 *
 * `POST /social/{cid}/publish` writes a post to a platform QRME does not run.
 * It is the single route in this product where synthetic media genuinely
 * **leaves the building**, and it stored that post with `watermark_id` NULL —
 * while `compose`, the in-app equivalent, stamped a credential every time.
 *
 * `compose_post` even says why, in a sentence that describes this route and
 * not itself: *a public post is synthetic media leaving the platform: it
 * carries a verifiable synthetic-media credential from the moment it exists.*
 * The only posts going out unmarked were the ones actually going out.
 *
 * It also ran `profile["maturity"]` as the moderation filter, where `compose`
 * forces `strict` with the note *public posts face the widest audience:
 * always the strict filter*. So a profile whose owner set it to `open` was
 * held to the loosest rule on the way to an audience QRME cannot see, and to
 * the strictest one when posting where it can.
 *
 * Both now match the in-app path, and `publish` hands the credential back so
 * whatever posts it onward can carry the disclosure rather than look it up.
 *
 * ## What the excursion answer is actually saying
 *
 * `redactions` and `left_host` are the feature, not decoration. The first is
 * how many things were stripped out of the question before it went anywhere;
 * the second is whether it went anywhere at all. A screen that showed the
 * findings and dropped those two would be showing the answer and hiding the
 * cost of having asked.
 */
export function Remainder() {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [error, setError] = useState<unknown>(null);
  const [said, setSaid] = useState("");

  const [board, setBoard] = useState<FeedbackBoard | null>(null);
  const [category, setCategory] = useState("idea");
  const [message, setMessage] = useState("");

  const [registries, setRegistries] = useState<PackRegistry[]>([]);
  const [apps, setApps] = useState<AppConnector[]>([]);
  // The connect picker reads the whole catalog — forty apps across six
  // providers — where this card used to offer exactly one hardcoded button.
  const [connCatalog, setConnCatalog] = useState<ConnectorCatalogue | null>(null);
  const [connProvider, setConnProvider] = useState("");
  const [connApp, setConnApp] = useState("");
  const [trips, setTrips] = useState<Excursion[]>([]);
  // Questions put to people rather than to a model. `asks` is the list;
  // `opened` is whichever one is expanded, because the answers only come
  // back on the single-question route.
  const [asks, setAsks] = useState<Inquiry[]>([]);
  const [opened, setOpened] = useState<Inquiry | null>(null);
  // The far hosts this agent keeps returning to. One row per host with a
  // count — never a list of individual visits, which would be the movement
  // log this card exists to warn about.
  const [been, setBeen] = useState<Visited[]>([]);
  const [hub, setHub] = useState<SteeringHub | null>(null);
  const [games, setGames] = useState<GameSession[]>([]);

  const [topic, setTopic] = useState("");
  const [question, setQuestion] = useState("");
  const [askTopic, setAskTopic] = useState("");
  const [askQuestion, setAskQuestion] = useState("");
  const [platform, setPlatform] = useState("steam");
  const [game, setGame] = useState("");

  const [lastSync, setLastSync] = useState<
    { pack_id: string; title: string; price: number }[]>([]);
  const [shopWindow, setShopWindow] = useState<PackDetail | null>(null);

  // The inspector's one field, and whatever the last lookup returned.
  const [lookupKind, setLookupKind] = useState("profile");
  const [lookupId, setLookupId] = useState("");
  const [found, setFound] = useState<unknown>(null);
  const [limits, setLimits] = useState<
    { image: { max_bytes: number }; video: { max_bytes: number } } | null>(null);
  const [avatarAsset, setAvatarAsset] = useState("");

  const [socialId, setSocialId] = useState("");
  const [collectText, setCollectText] = useState("");
  const [postText, setPostText] = useState("");
  const [published, setPublished] = useState<SocialPublished | null>(null);

  async function go<T>(work: () => Promise<T>, then: (v: T) => void) {
    setError(null);
    try { then(await work()); } catch (e) { setError(e); }
  }

  const reload = () => {
    go(() => api.feedback(token || undefined), setBoard);
    if (!me || !token) return;
    go(() => api.packRegistries(token), setRegistries);
    go(() => api.profileApps(me, token), setApps);
    go(() => api.excursions(me, token), setTrips);
    go(() => api.inquiries(me, token), setAsks);
    go(() => api.visits(me, token), setBeen);
    go(() => api.steeringHub(me, token), setHub);
    go(() => api.gameSessions(me, token), setGames);
  };

  useEffect(reload, [me, token]);
  useEffect(() => { go(() => api.mediaLimits(), setLimits); }, []);
  useEffect(() => {
    api.connectorCatalogue().then((c) => {
      setConnCatalog(c);
      // The play card's platform picker draws from the catalog's gaming
      // provider; land the selection on a real key the moment we know them.
      const consoles = c.providers.find((p) => p.provider === "gaming")?.apps;
      if (consoles?.length && !consoles.some((a) => a.app === "steam")) {
        setPlatform(consoles[0].app);
      }
    }).catch(() => setConnCatalog(null));
  }, []);

  /* Eleven bindings existed for eleven single reads, each fetching one thing
     by its id, and no screen called any of them. They are not eleven
     features — they are one: *show me the record behind this id*. So this is
     one control rather than eleven buttons nobody would find. */
  const LOOKUPS: Record<string, (id: string) => Promise<unknown>> = {
    profile: (id) => api.getProfile(id),
    stats: (id) => api.stats(id, token),
    badge: (id) => api.badge(id),
    composition: (id) => api.composition(id),
    display: (id) => api.display(id),
    exchange: (id) => api.exchange(id, token),
    camera: (id) => api.cameraSession(id, token),
    watermark: (id) => api.watermark(id),
    workflow: (id) => api.workflow(me, id, token),
  };

  return (
    <div className="screen">
      <h2>{tr("rem.title", lang)}</h2>
      <Refusal error={error} />
      {said && <p className="small">{said}</p>}

      {/* --- feedback ---------------------------------------------------- */}
      <div className="card">
        <h3>{tr("rem.fb", lang)}</h3>
        <p className="muted small">{tr("rem.fb.pitch", lang)}</p>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {(board?.categories || ["idea"]).map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <textarea value={message} rows={3}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder={tr("rem.fb.msg.ph", lang)} />
        <button disabled={!message} onClick={() => go(
          () => api.sendFeedback({ category, message }, token || undefined),
          (r) => { setMessage(""); setSaid(r.note); reload(); })}>
          {tr("rem.fb.send", lang)}
        </button>
        {board && (
          <div>
            {board.mine.map((f) => (
              <p key={f.id} className="muted small">
                {f.category} · {f.status} — {f.message}
              </p>
            ))}
            <p className="muted small">
              {fill(tr("rem.fb.total", lang), { n: board.total })}
            </p>
          </div>
        )}
      </div>

      {/* --- mod registries ---------------------------------------------- */}
      <div className="card">
        <h3>{tr("rem.mods", lang)}</h3>
        <p className="muted small">{tr("rem.mods.pitch", lang)}</p>
        {lastSync.length > 0 && (
          <div>
            {lastSync.map((k) => (
              <p key={k.pack_id} className="muted small">
                <button className="ghost" onClick={() => go(
                  () => api.pack(k.pack_id, token || undefined),
                  setShopWindow)}>{k.title}</button>
                {k.price === 0 ? tr("rem.pack.free", lang) : ` · ${k.price}`}
              </p>
            ))}
          </div>
        )}
        {shopWindow && (
          <div>
            <p className="small">
              <strong>{shopWindow.title}</strong> — {shopWindow.blurb}
            </p>
            <p className="muted small">
              {fill(tr("rem.mods.counts", lang), {
                pub: shopWindow.publisher,
                items: shopWindow.items,
                installs: shopWindow.installs,
              })}
              {shopWindow.rated && " · 18+"}
            </p>
            {/* Titles only. The contents are what you are buying, and they
                arrive by installing rather than by looking. */}
            <p className="muted small">
              {shopWindow.item_titles.join(" · ")}
            </p>
          </div>
        )}
        {registries.map((r) => (
          <div key={r.key} className="row">
            <div>
              <p className="small"><strong>{r.name}</strong> — {r.tagline}</p>
              <p className="muted small">
                {fill(tr("rem.mods.reg", lang), {
                  aud: r.audience, avail: r.available_packs, sync: r.synced,
                })}
              </p>
            </div>
            <button className="ghost" disabled={!token} onClick={() => go(
              () => api.syncRegistry(r.key, token),
              (out) => {
                // Idempotent, so the two numbers are the answer rather than
                // one total: pressing it again should say "0 new".
                setSaid(`${out.name}: ${out.created} new, `
                  + `${out.skipped} already had.`);
                setLastSync(out.packs);
                reload();
              })}>{tr("rem.mods.sync", lang)}</button>
          </div>
        ))}
      </div>

      {/* --- connected apps ---------------------------------------------- */}
      <div className="card">
        <h3>{tr("rem.apps", lang)}</h3>
        {apps.length === 0 && <p className="muted small">{tr("rem.apps.none", lang)}</p>}
        {apps.map((a) => (
          <p key={a.id} className="muted small">
            <strong>{a.label}</strong> — {a.directions.join(" and ")} ·{" "}
            {a.capabilities.join(", ")} · {a.status}
          </p>
        ))}
        {/* This used to be one hardcoded Google Calendar button in front of
            a forty-app catalog the backend had all along. The picker asks
            the catalog instead of pretending its first entry is its only
            one. */}
        {connCatalog && (
          <>
            <p className="muted small">
              {fill(tr("rem.apps.count", lang), {
                apps: connCatalog.app_count,
                providers: connCatalog.provider_count,
              })}
            </p>
            <div className="row">
              <label>{tr("rem.apps.provider", lang)}
                <select value={connProvider} onChange={(e) => {
                  setConnProvider(e.target.value);
                  // Every provider means every app — there is nothing
                  // narrower to choose once the answer is "all of it".
                  setConnApp(e.target.value === "*" ? "*" : "");
                }}>
                  <option value="">{tr("rem.apps.pick", lang)}</option>
                  {connCatalog.providers.map((p) => (
                    <option key={p.provider} value={p.provider}>{p.label}</option>
                  ))}
                  <option value="*">{tr("rem.apps.all", lang)}</option>
                </select>
              </label>
              <label>{tr("rem.apps.app", lang)}
                <select value={connApp} disabled={!connProvider}
                        onChange={(e) => setConnApp(e.target.value)}>
                  <option value="">{tr("rem.apps.pick", lang)}</option>
                  {connProvider !== "*" && connCatalog.providers
                    .find((p) => p.provider === connProvider)
                    ?.apps.map((a) => (
                      <option key={a.app} value={a.app}>{a.label}</option>
                    ))}
                  <option value="*">{tr("rem.apps.all", lang)}</option>
                </select>
              </label>
              <button className="ghost" disabled={!me || !token || !connApp}
                      onClick={() => go(async () => {
                        // "All of the above" is a list, not a wildcard the
                        // backend knows: connect each pair, one honest call
                        // per app.
                        const pairs = connCatalog.providers
                          .filter((p) => connProvider === "*"
                                         || p.provider === connProvider)
                          .flatMap((p) => p.apps
                            .filter((a) => connApp === "*" || a.app === connApp)
                            .map((a) => ({ provider: p.provider, app: a.app })));
                        for (const pair of pairs) {
                          await api.connectApp(me, pair, token);
                        }
                        return pairs.length;
                      }, (n) => {
                        setSaid(tr("rem.apps.connected", lang)
                          .replace("{n}", String(n)));
                        setConnApp(""); reload();
                      })}>
                {tr("rem.apps.connect", lang)}
              </button>
            </div>
            {connProvider && connApp && (() => {
              const entry = connCatalog.providers
                .find((p) => p.provider === connProvider)
                ?.apps.find((a) => a.app === connApp);
              return entry ? (
                <p className="muted small">
                  {entry.directions.join(" and ")} · {entry.capabilities.join(", ")}
                </p>
              ) : null;
            })()}
          </>
        )}
      </div>

      {/* --- excursions --------------------------------------------------- */}
      <div className="card">
        <h3>{tr("rem.trip", lang)}</h3>
        <p className="muted small">{tr("rem.trip.pitch", lang)}</p>
        <input value={topic} onChange={(e) => setTopic(e.target.value)}
               placeholder={tr("rem.trip.topic.ph", lang)} />
        <input value={question} onChange={(e) => setQuestion(e.target.value)}
               placeholder={tr("rem.trip.q.ph", lang)} />
        <button disabled={!me || !token || !topic || !question}
                onClick={() => go(
                  () => api.startExcursion(me, { topic, question }, token),
                  (fresh) => {
                    // The answer lands here, at once — a field report pressed
                    // this and read nothing, because the result only joined a
                    // list further down after a background reload.
                    setTrips((old) => [fresh,
                                       ...old.filter((t) => t.id !== fresh.id)]);
                    setTopic(""); setQuestion("");
                    setSaid(tr("rem.trip.back", lang));
                  })}>
          {tr("rem.trip.go", lang)}
        </button>
        {trips.map((t) => (
          <div key={t.id}>
            <p className="small">{t.findings}</p>
            <p className="muted small">
              {t.topic} · {t.redactions === 0
                ? tr("rem.exc.nostrip", lang)
                : tr("rem.exc.stripped", lang).replace("{n}",
                    t.redactions === 1
                      ? tr("rem.exc.thing.one", lang)
                      : tr("rem.exc.thing.many", lang)
                          .replace("{n}", String(t.redactions)))}
              {" · "}
              {t.left_host ? tr("rem.exc.left", lang) : tr("rem.exc.stayed", lang)}
              {t.learned && tr("rem.exc.folded", lang)}
            </p>
            {!t.learned && (
              <button className="ghost" onClick={() => go(
                () => api.learnFromExcursion(t.id, token),
                (r) => { setSaid(r.note); reload(); })}>
                {tr("rem.trip.fold", lang)}
              </button>
            )}
          </div>
        ))}
      </div>

      {/* --- asking people ------------------------------------------------ */}
      <div className="card">
        <h3>{tr("rem.ask", lang)}</h3>
        <p className="muted small">{tr("rem.ask.pitch", lang)}</p>
        <input value={askTopic} onChange={(e) => setAskTopic(e.target.value)}
               placeholder={tr("rem.trip.topic.ph", lang)} />
        <input value={askQuestion}
               onChange={(e) => setAskQuestion(e.target.value)}
               placeholder={tr("rem.ask.q.ph", lang)} />
        <button disabled={!me || !token || !askTopic || !askQuestion}
                onClick={() => go(
                  () => api.openInquiry(
                    me, { topic: askTopic, question: askQuestion }, token),
                  (fresh) => {
                    setAsks((old) => [fresh,
                                      ...old.filter((a) => a.id !== fresh.id)]);
                    setAskTopic(""); setAskQuestion("");
                    setSaid(tr("rem.ask.out", lang));
                  })}>
          {tr("rem.ask.go", lang)}
        </button>
        {asks.map((a) => (
          <div key={a.id}>
            {/* The brief, not the typed question: this is the line that went
                out, so it is the line worth showing. */}
            <p className="small">{a.brief}</p>
            <p className="muted small">
              {a.topic} · {fill(tr("rem.ask.count", lang), { n: a.answer_count })}
              {a.closed ? ` · ${tr("rem.ask.closed", lang)}` : ""}
              {" · "}
              {a.redactions === 0
                ? tr("rem.exc.nostrip", lang)
                : tr("rem.exc.stripped", lang).replace("{n}",
                    a.redactions === 1
                      ? tr("rem.exc.thing.one", lang)
                      : tr("rem.exc.thing.many", lang)
                          .replace("{n}", String(a.redactions)))}
            </p>
            <button className="ghost" onClick={() => go(
              () => api.inquiry(a.id, token), setOpened)}>
              {fill(tr("rem.ask.count", lang), { n: a.answer_count })}
            </button>
            {!a.closed && (
              <button className="ghost" onClick={() => go(
                () => api.closeInquiry(a.id, token),
                () => { setOpened(null); reload(); })}>
                {tr("rem.ask.close", lang)}
              </button>
            )}
            {opened?.id === a.id && (
              (opened.answers || []).length === 0
                ? <p className="muted small">{tr("rem.ask.none", lang)}</p>
                : (opened.answers || []).map((ans) => (
                    <div key={ans.id}>
                      <p className="small">
                        <b>{ans.alias || tr("rem.ask.anon", lang)}</b>
                        {" — "}{ans.body}
                      </p>
                      {ans.points_to && (
                        <p className="muted small">
                          {tr("rem.ask.points", lang)} {ans.points_to}
                        </p>
                      )}
                      {ans.blocked
                        ? <p className="muted small">{tr("rem.ask.held", lang)}</p>
                        : !ans.folded && (
                            <button className="ghost" onClick={() => go(
                              () => api.learnFromAnswer(a.id, ans.id, token),
                              (r) => { setSaid(r.note); reload();
                                       go(() => api.inquiry(a.id, token),
                                          setOpened); })}>
                              {tr("rem.trip.fold", lang)}
                            </button>)}
                    </div>
                  ))
            )}
          </div>
        ))}
      </div>

      {/* --- where it keeps going back to ---------------------------------- */}
      <div className="card">
        <h3>{tr("rem.been", lang)}</h3>
        <p className="muted small">{tr("rem.been.pitch", lang)}</p>
        {been.length === 0 && (
          <p className="muted small">{tr("rem.been.none", lang)}</p>
        )}
        {been.map((v) => (
          <div key={v.host}>
            <p className="small">
              <code>{v.host}</code>{" · "}
              {fill(tr("rem.been.times", lang), { n: v.times })}
            </p>
            {v.persistent && !v.stood_down && (
              <p className="muted small">{tr("rem.been.persistent", lang)}</p>
            )}
            {v.stood_down
              ? (<>
                  <p className="muted small">{tr("rem.been.stopped", lang)}</p>
                  <button className="ghost" onClick={() => go(
                    () => api.visitHostAgain(me, v.host, token),
                    () => reload())}>
                    {tr("rem.been.resume", lang)}
                  </button>
                </>)
              : (<button className="ghost" onClick={() => go(
                  () => api.standDownFromHost(me, v.host, token),
                  () => reload())}>
                  {tr("rem.been.stop", lang)}
                </button>)}
          </div>
        ))}
      </div>

      {/* --- the steering hub --------------------------------------------- */}
      <div className="card">
        <h3>{tr("rem.hub", lang)}</h3>
        {hub && (
          <p className="muted small">
            {fill(tr("rem.hub.dials", lang), { n: hub.dials.length })}
            {hub.adult_mode
              ? tr("rem.hub.rated.on", lang)
              : tr("rem.hub.rated.off", lang)}
          </p>
        )}
        {(hub?.dials || []).map((d) => (
          <div key={d.name} className="row">
            <p className="muted small">
              <strong>{d.label}</strong> ({d.group}) — {d.low} … {d.high}
              {d.adult_only && tr("rem.hub.adult", lang)}
            </p>
            <input type="range" min={d.min} max={d.max}
                   defaultValue={hub?.values?.[d.name] ?? d.default}
                   onMouseUp={(e) => go(
                     () => api.setSteeringHub(me, {
                       values: { [d.name]: Number(e.currentTarget.value) },
                     }, token),
                     (h) => { setHub(h); setSaid(`${d.label} set.`); })} />
          </div>
        ))}
      </div>

      {/* --- playing alongside -------------------------------------------- */}
      <div className="card">
        <h3>{tr("rem.play", lang)}</h3>
        <p className="muted small">{tr("rem.play.pitch", lang)}</p>
        {/* The platform is a closed set the backend already publishes under
            its gaming provider — a field report typed into a bare text box
            and asked for "a connector console or gaming account" instead. */}
        {(() => {
          const consoles = connCatalog?.providers
            .find((p) => p.provider === "gaming")?.apps || [];
          return consoles.length > 0 ? (
            <select value={platform}
                    onChange={(e) => setPlatform(e.target.value)}>
              {consoles.map((c) => (
                <option key={c.app} value={c.app}>{c.label}</option>
              ))}
            </select>
          ) : (
            <input value={platform}
                   onChange={(e) => setPlatform(e.target.value)}
                   placeholder={tr("rem.play.platform.ph", lang)} />
          );
        })()}
        <input value={game} onChange={(e) => setGame(e.target.value)}
               placeholder={tr("rem.play.game.ph", lang)} />
        <button disabled={!me || !token || !game} onClick={() => go(
          () => api.startGameSession(me, { platform, game }, token),
          () => { setGame(""); reload(); })}>{tr("rem.play.start", lang)}</button>
        {games.map((g) => (
          <div key={g.id} className="row">
            <div>
              <p className="small">
                {fill(tr("rem.play.line", lang), {
                  game: <strong>{g.game}</strong>,
                  platform: g.platform_label, role: g.role,
                })}
              </p>
              <p className="muted small">{g.status}</p>
            </div>
            {g.status === "active" && (
              <>
                <button className="ghost" onClick={() => go(
                  () => api.gameCallout(g.id, "what should I do here?", token),
                  (c) => setSaid(c.line))}>{tr("rem.play.ask", lang)}</button>
                <button className="ghost" onClick={() => go(
                  () => api.endGameSession(g.id, token),
                  (e) => { setSaid(`Ended after ${e.callouts} callouts.`);
                           reload(); })}>{tr("rem.play.end", lang)}</button>
              </>
            )}
          </div>
        ))}
      </div>

      {/* --- the inspector -------------------------------------------------- */}
      <div className="card">
        <h3>{tr("rem.look", lang)}</h3>
        <p className="muted small">{tr("rem.look.pitch", lang)}</p>
        <select value={lookupKind}
                onChange={(e) => { setLookupKind(e.target.value);
                                   setFound(null); }}>
          {Object.keys(LOOKUPS).map((k) => (
            <option key={k} value={k}>{k}</option>
          ))}
        </select>
        <input value={lookupId} onChange={(e) => setLookupId(e.target.value)}
               placeholder={tr("rem.look.id.ph", lang)} />
        <button disabled={!lookupId} onClick={() => go(
          () => LOOKUPS[lookupKind](lookupId), setFound)}>{tr("rem.look.go", lang)}</button>
        {found !== null && (
          <pre className="small" style={{ whiteSpace: "pre-wrap",
                                          overflowX: "auto" }}>
            {JSON.stringify(found, null, 1)}
          </pre>
        )}
      </div>

      {/* --- the portrait ---------------------------------------------------- */}
      <div className="card">
        <h3>{tr("rem.avatar", lang)}</h3>
        <p className="muted small">
          {tr("rem.avatar.pitch", lang)}
          {limits && tr("rem.avatar.limits", lang)
            .replace("{img}", String(Math.round(limits.image.max_bytes / 1e6)))
            .replace("{vid}", String(Math.round(limits.video.max_bytes / 1e6)))}
        </p>
        {/* "An asset path" meant nothing to a person holding a phone. The
            ordinary way in is a picture from the device; pasting an uploaded
            file's url stays possible underneath. */}
        <label className="chip">
          <input type="file" accept="image/*,video/*" hidden
                 onChange={(e) => {
                   const f = e.target.files?.[0];
                   e.target.value = "";
                   if (!f || !me || !token) return;
                   go(async () => {
                     const saved = await uploadMedia(me, f, token);
                     await api.setAvatar(me, saved.url, token);
                   }, () => setSaid(tr("rem.avatar.done", lang)));
                 }} />
          {tr("rem.avatar.upload", lang)}
        </label>
        <input value={avatarAsset}
               onChange={(e) => setAvatarAsset(e.target.value)}
               placeholder={tr("rem.avatar.asset.ph", lang)} />
        <button disabled={!me || !token || !avatarAsset} onClick={() => go(
          () => api.setAvatar(me, avatarAsset, token),
          () => { setAvatarAsset(""); setSaid(tr("rem.avatar.done", lang)); })}>
          {tr("rem.avatar.set", lang)}
        </button>
      </div>

      {/* --- publishing outward -------------------------------------------- */}
      <div className="card">
        <h3>{tr("rem.pub", lang)}</h3>
        <p className="muted small">{tr("rem.pub.pitch", lang)}</p>
        <input value={socialId} onChange={(e) => setSocialId(e.target.value)}
               placeholder={tr("rem.pub.cid.ph", lang)} />
        <textarea value={postText} rows={3}
                  onChange={(e) => setPostText(e.target.value)}
                  placeholder={tr("rem.pub.text.ph", lang)} />
        <button disabled={!token || !socialId || !postText} onClick={() => go(
          () => api.publishSocial(socialId, { topic: "post",
                                              content: postText }, token),
          (r) => { setPublished(r); setPostText(""); })}>
          {tr("rem.pub.go", lang)}
        </button>
        <h4>{tr("rem.pub.read", lang)}</h4>
        <p className="muted small">{tr("rem.pub.read.pitch", lang)}</p>
        <textarea value={collectText} rows={2}
                  onChange={(e) => setCollectText(e.target.value)}
                  placeholder={tr("rem.pub.collect.ph", lang)} />
        <button disabled={!token || !socialId || !collectText} onClick={() => go(
          () => api.collectSocial(socialId, [{ content: collectText }], token),
          (r) => { setCollectText("");
                   setSaid(`${r.ingested} in — ${r.total_sources} sources `
                     + "now feed this profile."); })}>
          {tr("rem.pub.collect", lang)}
        </button>
        {published && (
          <div>
            <p className="small">
              {published.status === "approved"
                ? `Posted to ${published.platform}.`
                : `Held — ${published.flag_reason}.`}
            </p>
            <p className="muted small">
              {fill(tr("rem.pub.cred", lang), {
                id: published.watermark.watermark_id,
                disclosure: published.watermark.disclosure,
              })}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
