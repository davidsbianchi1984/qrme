import { useEffect, useState } from "react";
import { api, type Display, type DisplayCatalog, type Front,
         type PageCatalog, type ProfilePage } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
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
export function Presence({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [pages, setPages] = useState<PageCatalog | null>(null);
  const [page, setPage] = useState<ProfilePage | null>(null);
  const [front, setFront] = useState<Front | null>(null);
  const [cat, setCat] = useState<DisplayCatalog | null>(null);
  const [mine, setMine] = useState<Display[]>([]);
  const [surfaces, setSurfaces] = useState<string[]>([]);
  const [error, setError] = useState<unknown>(null);
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

  const fail = (e: unknown) => setError(e);

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
      setTheme(p.page_theme.id);
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
        setNote(tr("prs.saved.removed", lang)
          .replace("{what}", p.html_removed.join(", ")));
      } else if (p.about_blocked) {
        setNote(tr("prs.saved.held", lang)
          .replace("{why}", p.about_blocked));
      } else {
        setNote(tr("prs.saved.said", lang));
      }
    } catch (e) { fail(e); }
  }

  const chosen = cat?.kinds.find((k) => k.kind === kind);

  return (
    <div className="screen">
      <h2>{tr("prs.title", lang)}</h2>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {front && (
        <div className="card">
          <h3>{tr("prs.front", lang)}</h3>
          <p className="small">
            <strong>{front.display_name}</strong>
            {front.handle && <> · @{front.handle}</>}
            {front.headline && <> — {front.headline}</>}
          </p>
          {/* Part of the page, not chrome around it. */}
          <p className="muted small">{front.ai_disclosure}</p>
          <p className="muted small">
            {front.rating_summary.count > 0
              ? fill(front.rating_summary.count === 1
                  ? tr("prs.review", lang) : tr("prs.reviews", lang),
                  { avg: front.rating_summary.average, n: front.rating_summary.count })
              : front.rating_summary.note}
            {fill(front.talked_with === 1
                ? tr("prs.talked.one", lang) : tr("prs.talked", lang),
                { n: front.talked_with })}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{tr("prs.page", lang)}</h3>
        <div className="row">
          <select value={theme} onChange={(e) => setTheme(e.target.value)}>
            {pages?.themes.map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </select>
          <select value={layout} onChange={(e) => setLayout(e.target.value)}>
            {pages?.layouts.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        {/* Its own row, and a box that grows: a one-line input clipped the
            words as they were typed — "the topic cuts off what I have
            written". */}
        <textarea value={tagline} rows={2}
                  onChange={(e) => setTagline(e.target.value)}
                  placeholder={tr("prs.tagline.ph", lang)} />
        <p className="muted small">
          {pages?.themes.find((t) => t.id === theme)?.note}
        </p>
        <div className="row">
          <input value={about} onChange={(e) => setAbout(e.target.value)}
                 placeholder={tr("prs.about.ph", lang)} style={{ flex: 1 }} />
        </div>
        <div className="row">
          <input value={html} onChange={(e) => setHtml(e.target.value)}
                 placeholder={tr("prs.html.ph", lang)} style={{ flex: 1 }} />
          <button disabled={!token} onClick={savePage}>
            {tr("prs.save", lang)}
          </button>
        </div>
        {/* Shown before the save, which is the whole reason the backend
            publishes them. */}
        {pages && (
          <p className="muted small">
            {fill(tr("prs.survive", lang),
              { tags: pages.html_tags.join(" ") })}
          </p>
        )}
        {page && page.html_removed.length > 0 && (
          <p className="small">
            {fill(tr("prs.lastremoved", lang),
              { what: <strong>{page.html_removed.join(", ")}</strong> })}
          </p>
        )}
        {page?.about_blocked && (
          <div className="card error">
            <p className="small">{fill(tr("prs.held", lang),
              { why: page.about_blocked })}</p>
          </div>
        )}
      </div>

      <div className="card">
        <h3>{tr("prs.screens", lang)}</h3>
        <p className="muted small">
          {fill(tr("prs.screens.pitch", lang),
            { showing: <em>{tr("prs.showing", lang)}</em> })}
        </p>
        {mine.length === 0 &&
          <p className="muted small">{tr("prs.noneplaced", lang)}</p>}
        {mine.map((d) => (
          <div key={d.id}>
            <div className="row">
              <div style={{ flex: 1 }}>
                <strong>{d.label}</strong>
                {!d.live &&
                  <span className="chip"> {tr("prs.takendown", lang)}</span>}
                {d.passers_by &&
                  <span className="chip"> {tr("prs.passersby", lang)}</span>}
                <div className="muted small">
                  {fill(tr("prs.screenline", lang), {
                    kind: <>{d.kind}{d.location && <> · {d.location}</>}</>,
                    size: d.size, finish: d.finish,
                    faces: d.faces.join(", "),
                  })}
                </div>
              </div>
              {d.live && (
                <button onClick={async () => {
                  setError(null); setNote(null);
                  try {
                    await api.removeDisplay(d.id, token);
                    setNote(tr("prs.takendown.said", lang));
                    reload();
                  } catch (e) { fail(e); }
                }}>{tr("prs.takedown", lang)}</button>
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

        <h4>{tr("prs.puton", lang)}</h4>
        <div className="row">
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            {cat?.kinds.map((k) => (
              <option key={k.kind} value={k.kind}>{k.kind}</option>
            ))}
          </select>
          <input value={label} onChange={(e) => setLabel(e.target.value)}
                 placeholder={tr("prs.label.ph", lang)} style={{ flex: 1 }} />
          <input value={where} onChange={(e) => setWhere(e.target.value)}
                 placeholder={tr("prs.where.ph", lang)} />
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
              setNote(tr("prs.placed.said", lang));
              reload();
            } catch (e) { fail(e); }
          }}>{tr("prs.place", lang)}</button>
        </div>
        {/* The distinction the vocabulary exists to draw. */}
        {chosen && (
          <p className="muted small">
            {fill(tr("prs.chosen", lang), {
              means: chosen.means,
              who: chosen.passers_by
                ? tr("prs.passers.yes", lang) : tr("prs.passers.no", lang),
            })}
          </p>
        )}
      </div>

      {cat && (
        <div className="card">
          <h3>{tr("prs.nevershows", lang)}</h3>
          {/* Verbatim. These sentences are the argument, made once, carefully. */}
          <ul className="small">
            {cat.never.map((n) => (
              <li key={n.thing}>{fill(tr("prs.never.row", lang), {
                thing: <strong>{n.thing}</strong>, why: n.why })}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="card">
        <h3>{tr("prs.surfaces", lang)}</h3>
        <p className="muted small">
          {fill(tr("prs.currently", lang), {
            what: surfaces.length > 0
              ? surfaces.join(", ") : tr("prs.none", lang),
          })}
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
