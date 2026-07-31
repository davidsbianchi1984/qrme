import { useEffect, useState } from "react";
import { api, type AppConnector, type Excursion, type FeedbackBoard,
         type GameSession, type PackDetail, type PackRegistry,
         type SocialPublished, type SteeringHub } from "../api";
import { Refusal } from "../Refusal";
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
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [error, setError] = useState<unknown>(null);
  const [said, setSaid] = useState("");

  const [board, setBoard] = useState<FeedbackBoard | null>(null);
  const [category, setCategory] = useState("idea");
  const [message, setMessage] = useState("");

  const [registries, setRegistries] = useState<PackRegistry[]>([]);
  const [apps, setApps] = useState<AppConnector[]>([]);
  const [trips, setTrips] = useState<Excursion[]>([]);
  const [hub, setHub] = useState<SteeringHub | null>(null);
  const [games, setGames] = useState<GameSession[]>([]);

  const [topic, setTopic] = useState("");
  const [question, setQuestion] = useState("");
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
    go(() => api.steeringHub(me, token), setHub);
    go(() => api.gameSessions(me, token), setGames);
  };

  useEffect(reload, [me, token]);
  useEffect(() => { go(() => api.mediaLimits(), setLimits); }, []);

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
      <h2>Everything else</h2>
      <Refusal error={error} />
      {said && <p className="small">{said}</p>}

      {/* --- feedback ---------------------------------------------------- */}
      <div className="card">
        <h3>Tell us about the app</h3>
        <p className="muted small">
          Your own submissions come back to you and to nobody else. All anyone
          else ever sees is the count by category.
        </p>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {(board?.categories || ["idea"]).map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <textarea value={message} rows={3}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="what would make this better" />
        <button disabled={!message} onClick={() => go(
          () => api.sendFeedback({ category, message }, token || undefined),
          (r) => { setMessage(""); setSaid(r.note); reload(); })}>
          Send it
        </button>
        {board && (
          <div>
            {board.mine.map((f) => (
              <p key={f.id} className="muted small">
                {f.category} · {f.status} — {f.message}
              </p>
            ))}
            <p className="muted small">
              {board.total} in total across everybody.
            </p>
          </div>
        )}
      </div>

      {/* --- mod registries ---------------------------------------------- */}
      <div className="card">
        <h3>Where mods come from</h3>
        <p className="muted small">
          Third-party catalogues. `audience` says what each one stocks — task
          mods for a robot body, or knowledge mods for a profile.
        </p>
        {lastSync.length > 0 && (
          <div>
            {lastSync.map((k) => (
              <p key={k.pack_id} className="muted small">
                <button className="ghost" onClick={() => go(
                  () => api.pack(k.pack_id, token || undefined),
                  setShopWindow)}>{k.title}</button>
                {k.price === 0 ? " · free" : ` · ${k.price}`}
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
              {shopWindow.publisher} · {shopWindow.items} items ·{" "}
              {shopWindow.installs} installs
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
                for a {r.audience} · {r.available} available, {r.synced} synced
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
              })}>Sync</button>
          </div>
        ))}
      </div>

      {/* --- connected apps ---------------------------------------------- */}
      <div className="card">
        <h3>Apps it is connected to</h3>
        {apps.length === 0 && <p className="muted small">None yet.</p>}
        {apps.map((a) => (
          <p key={a.id} className="muted small">
            <strong>{a.label}</strong> — {a.directions.join(" and ")} ·{" "}
            {a.capabilities.join(", ")} · {a.status}
          </p>
        ))}
        <button className="ghost" disabled={!me || !token} onClick={() => go(
          () => api.connectApp(me, { provider: "google", app: "calendar" },
                               token),
          () => { setSaid("Connected."); reload(); })}>
          Connect Google Calendar
        </button>
      </div>

      {/* --- excursions --------------------------------------------------- */}
      <div className="card">
        <h3>Going out to look something up</h3>
        <p className="muted small">
          The question is stripped before it leaves. The answer says how much
          was taken out and whether it left this machine at all — which is the
          part worth reading, not the findings.
        </p>
        <input value={topic} onChange={(e) => setTopic(e.target.value)}
               placeholder="topic" />
        <input value={question} onChange={(e) => setQuestion(e.target.value)}
               placeholder="what to find out" />
        <button disabled={!me || !token || !topic || !question}
                onClick={() => go(
                  () => api.startExcursion(me, { topic, question }, token),
                  () => { setTopic(""); setQuestion(""); reload(); })}>
          Go and look
        </button>
        {trips.map((t) => (
          <div key={t.id}>
            <p className="small">{t.findings}</p>
            <p className="muted small">
              {t.topic} · {t.redactions === 0
                ? "nothing needed stripping"
                : `${t.redactions} thing${t.redactions === 1 ? "" : "s"} stripped out first`}
              {" · "}
              {t.left_host ? "left this machine" : "never left this machine"}
              {t.learned && " · folded in"}
            </p>
            {!t.learned && (
              <button className="ghost" onClick={() => go(
                () => api.learnFromExcursion(t.id, token),
                (r) => { setSaid(r.note); reload(); })}>
                Fold it in
              </button>
            )}
          </div>
        ))}
      </div>

      {/* --- the steering hub --------------------------------------------- */}
      <div className="card">
        <h3>Every dial in one place</h3>
        {hub && (
          <p className="muted small">
            {hub.dials.length} dials
            {hub.adult_mode
              ? ", including the ones only a rated profile has."
              : ". The rated-only ones are listed and refused here, rather "
                + "than hidden, so the refusal has something to point at."}
          </p>
        )}
        {(hub?.dials || []).map((d) => (
          <div key={d.name} className="row">
            <p className="muted small">
              <strong>{d.label}</strong> ({d.group}) — {d.low} … {d.high}
              {d.adult_only && " · 18+ only"}
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
        <h3>Playing alongside somebody</h3>
        <p className="muted small">
          The companion plays within the game's rules. Fair play is enforced
          rather than promised.
        </p>
        <input value={platform} onChange={(e) => setPlatform(e.target.value)}
               placeholder="steam, xbox, playstation…" />
        <input value={game} onChange={(e) => setGame(e.target.value)}
               placeholder="which game" />
        <button disabled={!me || !token || !game} onClick={() => go(
          () => api.startGameSession(me, { platform, game }, token),
          () => { setGame(""); reload(); })}>Start a session</button>
        {games.map((g) => (
          <div key={g.id} className="row">
            <div>
              <p className="small">
                <strong>{g.game}</strong> on {g.platform_label} · {g.role}
              </p>
              <p className="muted small">{g.status}</p>
            </div>
            {g.status === "active" && (
              <>
                <button className="ghost" onClick={() => go(
                  () => api.gameCallout(g.id, "what should I do here?", token),
                  (c) => setSaid(c.line))}>Ask it</button>
                <button className="ghost" onClick={() => go(
                  () => api.endGameSession(g.id, token),
                  (e) => { setSaid(`Ended after ${e.callouts} callouts.`);
                           reload(); })}>End</button>
              </>
            )}
          </div>
        ))}
      </div>

      {/* --- the inspector -------------------------------------------------- */}
      <div className="card">
        <h3>Look something up by its id</h3>
        <p className="muted small">
          Nine of these reads had a binding written for them and no screen
          calling it. They are not nine features — they are one question asked
          about nine kinds of record, so this is one control rather than nine
          buttons nobody would find.
        </p>
        <select value={lookupKind}
                onChange={(e) => { setLookupKind(e.target.value);
                                   setFound(null); }}>
          {Object.keys(LOOKUPS).map((k) => (
            <option key={k} value={k}>{k}</option>
          ))}
        </select>
        <input value={lookupId} onChange={(e) => setLookupId(e.target.value)}
               placeholder="the id" />
        <button disabled={!lookupId} onClick={() => go(
          () => LOOKUPS[lookupKind](lookupId), setFound)}>Fetch it</button>
        {found !== null && (
          <pre className="small" style={{ whiteSpace: "pre-wrap",
                                          overflowX: "auto" }}>
            {JSON.stringify(found, null, 1)}
          </pre>
        )}
      </div>

      {/* --- the portrait ---------------------------------------------------- */}
      <div className="card">
        <h3>Its portrait</h3>
        <p className="muted small">
          The mark is burned into the pixels rather than drawn over them, so
          it survives a screenshot or a crop.
          {limits && ` Up to ${Math.round(limits.image.max_bytes / 1e6)} MB `
            + `for a picture, ${Math.round(limits.video.max_bytes / 1e6)} MB `
            + "for video."}
        </p>
        <input value={avatarAsset}
               onChange={(e) => setAvatarAsset(e.target.value)}
               placeholder="an asset path" />
        <button disabled={!me || !token || !avatarAsset} onClick={() => go(
          () => api.setAvatar(me, avatarAsset, token),
          () => { setAvatarAsset(""); setSaid("Portrait set."); })}>
          Set it
        </button>
      </div>

      {/* --- publishing outward -------------------------------------------- */}
      <div className="card">
        <h3>Publishing to a platform we do not run</h3>
        <p className="muted small">
          This is the one place a profile's words genuinely leave. It runs the
          strict filter — not the profile's own setting — and it stamps a
          synthetic-media credential, because content going somewhere we cannot
          see is the case the mark exists for. It used to do neither.
        </p>
        <input value={socialId} onChange={(e) => setSocialId(e.target.value)}
               placeholder="a publish connection id" />
        <textarea value={postText} rows={3}
                  onChange={(e) => setPostText(e.target.value)}
                  placeholder="what to post" />
        <button disabled={!token || !socialId || !postText} onClick={() => go(
          () => api.publishSocial(socialId, { topic: "post",
                                              content: postText }, token),
          (r) => { setPublished(r); setPostText(""); })}>
          Publish it
        </button>
        <h4>Or read from one</h4>
        <p className="muted small">
          The other direction on the same connection: what the account already
          published becomes source material this profile is built from.
        </p>
        <textarea value={collectText} rows={2}
                  onChange={(e) => setCollectText(e.target.value)}
                  placeholder="a post to read in" />
        <button disabled={!token || !socialId || !collectText} onClick={() => go(
          () => api.collectSocial(socialId, [{ content: collectText }], token),
          (r) => { setCollectText("");
                   setSaid(`${r.ingested} in — ${r.total_sources} sources `
                     + "now feed this profile."); })}>
          Read it in
        </button>
        {published && (
          <div>
            <p className="small">
              {published.status === "approved"
                ? `Posted to ${published.platform}.`
                : `Held — ${published.flag_reason}.`}
            </p>
            <p className="muted small">
              Credential {published.watermark.watermark_id} ·{" "}
              {published.watermark.disclosure}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
