import { useEffect, useState } from "react";
import { api, type Display, type DisplayCatalog, type Front,
         type PageCatalog, type ProfilePage } from "../api";
import { useSession } from "../store";

/**
 * How this profile presents itself, everywhere it is seen.
 *
 * Twelve routes with no caller: the page it builds, the front page a stranger
 * lands on, the physical screens it is shown on, and which surfaces it is
 * allowed on at all.
 *
 * One of them stings more than the rest. `/pages/themes` publishes the allowed
 * HTML tags and CSS properties **specifically so an editor can grey out what
 * would be stripped** — the backend says exactly that in its own comment —
 * *"rather than letting somebody write it and lose it"*. Nothing was reading
 * them. So the editor here shows the surviving tag list up front, and shows
 * `html_removed` after a save, because the save succeeds either way: without
 * that, somebody's `<script>` vanishes and their page just quietly does less
 * than they wrote.
 *
 * The display half is built around an asymmetry worth making visible. What a
 * screen is showing is **public** — a fixture in a corridor displays to
 * whoever walks past, so it cannot be a secret from them. The list of your
 * screens is **not**, because that is a list of physical places. The screen
 * says which is which rather than leaving both looking like ordinary rows.
 *
 * And `never` is rendered verbatim: what a fixed screen may never show, each
 * with its reason. Those sentences are the product's posture argued carefully
 * once, and a paraphrase would be a worse version of it.
 */
export function Presence() {
  const { session } = useSession();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [pages, setPages] = useState<PageCatalog | null>(null);
  const [page, setPage] = useState<ProfilePage | null>(null);
  const [front, setFront] = useState<Front | null>(null);
  const [cat, setCat] = useState<DisplayCatalog | null>(null);
  const [mine, setMine] = useState<Display[]>([]);
  const [surfaces, setSurfaces] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);

  const [theme, setTheme] = useState("midnight");
  const [layout, setLayout] = useState("classic");
  const [tagline, setTagline] = useState("");
  const [about, setAbout] = useState("");
  const [html, setHtml] = useState("");

  const [kind, setKind] = useState("wall_panel");
  const [label, setLabel] = useState("");
  const [where, setWhere] = useState("");
  const [size, setSize] = useState("full");
  const [finish, setFinish] = useState("opaque");

  const fail = (e: unknown) => setError((e as Error).message);

  useEffect(() => {
    api.pageCatalog().then((c) => {
      setPages(c);
      setLayout(c.layouts[0] || "classic");
    }).catch(fail);
    api.displayCatalog().then((c) => {
      setCat(c);
      setKind(c.kinds[0]?.kind || "wall_panel");
      setSize(c.sizes[c.sizes.length - 1]?.size || "full");
      setFinish(c.finishes[0]?.finish || "opaque");
    }).catch(fail);
  }, []);

  function reload() {
    if (!me) return;
    api.page(me).then((p) => {
      setPage(p);
      setTheme(p.theme.id);
      setLayout(p.layout);
      setTagline(p.tagline || "");
      setAbout(p.about || "");
      setHtml(p.html || "");
    }).catch(fail);
    api.front(me).then(setFront).catch(fail);
    api.surfaces(me).then((r) => setSurfaces(r.surfaces)).catch(fail);
    if (token) {
      api.myDisplays(me, token).then((r) => setMine(r.displays)).catch(fail);
    }
  }
  useEffect(reload, [me, token]);

  async function savePage() {
    setError(null); setNote(null);
    try {
      const p = await api.setPage(me, {
        theme, layout,
        tagline: tagline.trim() || null,
        about: about.trim() || null,
        html: html.trim() || null,
      }, token);
      setPage(p);
      // The save succeeded whatever was stripped, so say what went.
      if (p.html_removed.length > 0) {
        setNote(`Saved. These were removed: ${p.html_removed.join(", ")}.`);
      } else if (p.about_blocked) {
        setNote(`Saved, but the about text is held: ${p.about_blocked}`);
      } else {
        setNote("Saved.");
      }
    } catch (e) { fail(e); }
  }

  const chosen = cat?.kinds.find((k) => k.kind === kind);

  return (
    <div className="screen">
      <h2>Where this is seen</h2>

      {error && <div className="card error">{error}</div>}
      {note && <div className="card"><p className="small">{note}</p></div>}

      {front && (
        <div className="card">
          <h3>What a stranger lands on</h3>
          <p className="small">
            <strong>{front.display_name}</strong>
            {front.handle && <> · @{front.handle}</>}
            {front.headline && <> — {front.headline}</>}
          </p>
          {/* Part of the page, not chrome around it. */}
          <p className="muted small">{front.ai_disclosure}</p>
          <p className="muted small">
            {front.rating.count > 0
              ? <>{front.rating.average} from {front.rating.count} review
                  {front.rating.count === 1 ? "" : "s"}</>
              : front.rating.note}
            {" · "}{front.talked_with} {front.talked_with === 1 ? "person has" : "people have"} talked with it
          </p>
        </div>
      )}

      <div className="card">
        <h3>The page you make yourself</h3>
        <div className="row">
          <select value={theme} onChange={(e) => setTheme(e.target.value)}>
            {pages?.themes.map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
          <select value={layout} onChange={(e) => setLayout(e.target.value)}>
            {pages?.layouts.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
          <input value={tagline} onChange={(e) => setTagline(e.target.value)}
                 placeholder="a tagline" style={{ flex: 1 }} />
        </div>
        <p className="muted small">
          {pages?.themes.find((t) => t.id === theme)?.note}
        </p>
        <div className="row">
          <input value={about} onChange={(e) => setAbout(e.target.value)}
                 placeholder="about" style={{ flex: 1 }} />
        </div>
        <div className="row">
          <input value={html} onChange={(e) => setHtml(e.target.value)}
                 placeholder="your own HTML" style={{ flex: 1 }} />
          <button disabled={!token} onClick={savePage}>Save</button>
        </div>
        {/* Shown before the save, which is the whole reason the backend
            publishes them. */}
        {pages && (
          <p className="muted small">
            These survive: {pages.html_tags.join(" ")}. Anything else is
            removed on save, and the save still succeeds — so the list is
            here rather than in a message afterwards.
          </p>
        )}
        {page && page.html_removed.length > 0 && (
          <p className="small">
            Last save removed: <strong>{page.html_removed.join(", ")}</strong>
          </p>
        )}
        {page?.about_blocked && (
          <div className="card error">
            <p className="small">About text held: {page.about_blocked}</p>
          </div>
        )}
      </div>

      <div className="card">
        <h3>Screens it is on</h3>
        <p className="muted small">
          Only you can see this list — it is a list of physical places. What
          any one screen is <em>showing</em> is public, because a fixture in a
          corridor displays to whoever walks past.
        </p>
        {mine.length === 0 && <p className="muted small">None placed.</p>}
        {mine.map((d) => (
          <div key={d.id}>
            <div className="row">
              <div style={{ flex: 1 }}>
                <strong>{d.label}</strong>
                {!d.live && <span className="chip"> taken down</span>}
                {d.passers_by && <span className="chip"> passers-by</span>}
                <div className="muted small">
                  {d.kind}{d.location && <> · {d.location}</>} · {d.size} ·{" "}
                  {d.finish} · showing {d.faces.join(", ")}
                </div>
              </div>
              {d.live && (
                <button onClick={async () => {
                  setError(null); setNote(null);
                  try {
                    await api.removeDisplay(d.id, token);
                    setNote("Taken down. The record stays; the screen stops.");
                    reload();
                  } catch (e) { fail(e); }
                }}>Take down</button>
              )}
            </div>
            {d.live && cat && (
              <div className="row">
                {cat.faces.map((f) => {
                  const on = d.faces.includes(f.face);
                  return (
                    <button key={f.face} className="chip" onClick={async () => {
                      setError(null); setNote(null);
                      const next = on
                        ? d.faces.filter((x) => x !== f.face)
                        : [...d.faces, f.face];
                      try {
                        await api.setDisplayFaces(d.id, next, token);
                        reload();
                      } catch (e) { fail(e); }
                    }}>{on ? "✓ " : ""}{f.face}</button>
                  );
                })}
              </div>
            )}
            {/* The mark's own rule, from the server. */}
            {d.live && <p className="muted small">{d.mark.note}</p>}
          </div>
        ))}

        <h4>Put it on a screen</h4>
        <div className="row">
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            {cat?.kinds.map((k) => (
              <option key={k.kind} value={k.kind}>{k.kind}</option>
            ))}
          </select>
          <input value={label} onChange={(e) => setLabel(e.target.value)}
                 placeholder="what to call it" style={{ flex: 1 }} />
          <input value={where} onChange={(e) => setWhere(e.target.value)}
                 placeholder="where it is" />
        </div>
        <div className="row">
          <select value={size} onChange={(e) => setSize(e.target.value)}>
            {cat?.sizes.map((s) => <option key={s.size} value={s.size}>{s.size}</option>)}
          </select>
          <select value={finish} onChange={(e) => setFinish(e.target.value)}>
            {cat?.finishes.map((f) => (
              <option key={f.finish} value={f.finish}>{f.finish}</option>
            ))}
          </select>
          <button disabled={!token || !label.trim()} onClick={async () => {
            setError(null); setNote(null);
            try {
              await api.placeDisplay(me, {
                kind, label: label.trim(),
                location: where.trim() || null, size, finish,
              }, token);
              setLabel(""); setWhere("");
              setNote("Placed.");
              reload();
            } catch (e) { fail(e); }
          }}>Place</button>
        </div>
        {/* The distinction the vocabulary exists to draw. */}
        {chosen && (
          <p className="muted small">
            {chosen.means} —{" "}
            {chosen.passers_by
              ? "read by people who did not choose to look at it."
              : "faces you, in your own space."}
          </p>
        )}
      </div>

      {cat && (
        <div className="card">
          <h3>What a fixed screen never shows</h3>
          {/* Verbatim. These sentences are the argument, made once, carefully. */}
          <ul className="small">
            {cat.never.map((n) => (
              <li key={n.thing}><strong>{n.thing}</strong> — {n.why}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="card">
        <h3>Surfaces it appears on</h3>
        <p className="muted small">
          Currently: {surfaces.length > 0 ? surfaces.join(", ") : "none"}
        </p>
        <div className="row">
          {["web", "kiosk", "watch", "mobile", "wall"].map((s) => {
            const on = surfaces.includes(s);
            return (
              <button key={s} className="chip" disabled={!token}
                      onClick={async () => {
                setError(null); setNote(null);
                const next = on ? surfaces.filter((x) => x !== s)
                                : [...surfaces, s];
                try {
                  const r = await api.setSurfaces(me, next, token);
                  setSurfaces(r.surfaces);
                } catch (e) { fail(e); }
              }}>{on ? "✓ " : ""}{s}</button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
