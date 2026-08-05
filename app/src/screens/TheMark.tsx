import { useEffect, useState } from "react";
import { api, type ObjectionRow, type ProfilePost,
         type WatermarkDesign } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The mark this profile's work carries, what it has published, and somebody
 * contesting that it should exist.
 *
 * Three surfaces that belong together because they are the same question from
 * three sides: *is it clear what this is, and who says otherwise.*
 *
 * ## The designation is not a field you can empty
 *
 * An owner designs the mark and the label. Whatever they type, the line comes
 * back with `AI ·` in front of it — ask for "Rosa" and get "✦ AI · Rosa". The
 * screen shows the answer rather than the request for exactly that reason:
 * typing a label and being shown your own text back would teach the wrong
 * lesson about what this control does.
 *
 * ## Published is not the same as written
 *
 * `compose` withholds the text of a post that is `pending` — the strict filter
 * held it, or the owner set this profile to approve its own posts by hand —
 * and returns `content: null` **even to the owner who asked for it**.
 *
 * The route that lists posts used to return every column of every row to
 * anybody with no token at all. So the hold was enforced against the author
 * and against nobody else: a post the moderation filter refused was published
 * in full by the route whose job is to list what was published, alongside
 * `flag_reason` — the sentence naming which rule the text broke.
 *
 * Approved posts are public. Everything else is a queue, and this screen only
 * shows it because it is signed in as the owner.
 *
 * ## Re-attesting is the only move the owner has
 *
 * An objection restricts the profile the moment it is opened, and the owner
 * cannot resolve it. That is deliberate and worth stating on the screen: an
 * owner who could dismiss an objection against their own profile is an owner
 * adjudicating their own case. All they can do is re-attest the basis on
 * which they claim the right, inside the review window, and wait.
 */
export function TheMark() {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [error, setError] = useState<unknown>(null);
  const [said, setSaid] = useState("");

  const [design, setDesign] = useState<WatermarkDesign | null>(null);
  const [mark, setMark] = useState("");
  const [label, setLabel] = useState("");

  const [posts, setPosts] = useState<ProfilePost[]>([]);
  const [objections, setObjections] = useState<ObjectionRow[]>([]);

  async function go<T>(work: () => Promise<T>, then: (v: T) => void) {
    setError(null);
    try { then(await work()); } catch (e) { setError(e); }
  }

  const loadPosts = () => {
    if (!me) return;
    go(() => api.profilePosts(me, token || undefined), setPosts);
  };

  useEffect(() => {
    if (!me) return;
    go(() => api.watermarkDesign(me), setDesign);
    loadPosts();
    if (token) go(() => api.profileObjections(me, token), setObjections);
  }, [me, token]);

  const held = posts.filter((p) => p.status !== "approved");
  const live = posts.filter((p) => p.status === "approved");

  if (!me) {
    return (
      <div className="screen">
        <h2>{tr("mrk.title.short", lang)}</h2>
        <p className="muted">{tr("mrk.chooseprofile", lang)}</p>
      </div>
    );
  }

  return (
    <div className="screen">
      <h2>{tr("mrk.title", lang)}</h2>
      <Refusal error={error} />
      {said && <p className="small">{said}</p>}

      {/* --- the mark --------------------------------------------------- */}
      <div className="card">
        <h3>{tr("mrk.everyrender", lang)}</h3>
        {design && (
          <div>
            <p className="small"><strong>{design.line}</strong></p>
            <p className="muted small">
              {design.custom
                ? tr("mrk.yourdesign", lang)
                : tr("mrk.thedefault", lang)}
              {design.always_displayed && " " + tr("mrk.always", lang)}
            </p>
            <p className="muted small">{design.disclosure}</p>
          </div>
        )}
        <input value={mark} onChange={(e) => setMark(e.target.value)}
               placeholder={tr("mrk.glyph.ph", lang)} maxLength={8} />
        <input value={label} onChange={(e) => setLabel(e.target.value)}
               placeholder={tr("mrk.label.ph", lang)} maxLength={60} />
        {/* One sentence with the designation as a hole, not three fragments
            around a <strong>: the words on either side of "AI ·" do not stay
            on either side of it in Japanese or Arabic. */}
        <p className="muted small">
          {fill(tr("mrk.designation", lang), { ai: <strong>AI ·</strong> })}
        </p>
        <button disabled={!token} onClick={() => go(
          () => api.setWatermarkDesign(me, {
            ...(mark ? { mark } : {}), ...(label ? { label } : {}),
          }, token),
          (d) => { setDesign(d);
                   setSaid(tr("mrk.nowreads", lang).replace("{line}", d.line)); })}>
          {tr("mrk.setit", lang)}
        </button>
        <button className="ghost" disabled={!token} onClick={() => go(
          () => api.setWatermarkDesign(me, { mark: "", label: "" }, token),
          (d) => { setDesign(d); setMark(""); setLabel("");
                   setSaid(tr("mrk.backtodefault", lang)); })}>
          {tr("mrk.reset", lang)}
        </button>
      </div>

      {/* --- published, and held ---------------------------------------- */}
      <div className="card">
        <h3>{tr("mrk.published", lang)}</h3>
        {live.length === 0 && <p className="muted small">{tr("mrk.nothingyet", lang)}</p>}
        {live.map((p) => (
          <div key={p.id}>
            <p className="small">{p.content}</p>
            <p className="muted small">
              {p.topic}{p.surface && ` · ${p.surface}`} ·{" "}
              {p.watermark?.disclosure}
            </p>
          </div>
        ))}
      </div>

      {token && (
        <div className="card">
          <h3>{tr("mrk.heldback", lang)}</h3>
          <p className="muted small">{tr("mrk.onlyyou", lang)}</p>
          {held.length === 0 && (
            <p className="muted small">{tr("mrk.nothingwaiting", lang)}</p>
          )}
          {held.map((p) => (
            <div key={p.id}>
              <p className="small">{p.content}</p>
              <p className="muted small">
                {p.status}
                {p.flag_reason && ` — ${p.flag_reason}`}
              </p>
            </div>
          ))}
          <button className="ghost" onClick={loadPosts}>{tr("mrk.refresh", lang)}</button>
        </div>
      )}

      {/* --- somebody contesting it -------------------------------------- */}
      {token && (
        <div className="card">
          <h3>{tr("mrk.objections", lang)}</h3>
          <p className="muted small">{tr("mrk.claiming", lang)}</p>
          {objections.length === 0 && (
            <p className="muted small">{tr("mrk.none", lang)} </p>
          )}
          {objections.map((o) => (
            <div key={o.id}>
              <p className="small">
                <strong>{o.status}</strong>
                {o.reason && ` — ${o.reason}`}
              </p>
              <p className="muted small">
                {fill(tr("mrk.refline", lang),
                      { ref: o.objector_ref, at: o.created_at })}
                {o.reattested ? " " + tr("mrk.reattested", lang) : ""}
                {o.status !== "open" && " "
                  + tr("mrk.wouldreturn", lang)
                      .replace("{status}", o.prior_status)}
              </p>
              {o.status === "open" && !o.reattested && (
                <button onClick={() => go(
                  () => api.reattestBasis(me, o.id, token),
                  (r) => { setSaid(r.note);
                           go(() => api.profileObjections(me, token),
                              setObjections); })}>
                  {tr("mrk.reattest", lang)}
                </button>
              )}
            </div>
          ))}
          <p className="muted small">{tr("mrk.reattesting", lang)}</p>
        </div>
      )}
    </div>
  );
}
