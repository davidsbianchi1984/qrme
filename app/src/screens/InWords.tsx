import { useEffect, useState } from "react";
import { api, type HandleClaimed, type LanguageCatalogue,
         type LanguagePref, type ProfilePost, type Translated } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The words a profile uses, and the name it answers to.
 *
 * Four owner controls with no door in this console: which language it speaks,
 * translating something it ran across, claiming its `@handle`, and composing
 * a post.
 *
 * ## Claiming a handle took no credential at all
 *
 * And the damage was not that a stranger could give a profile a second name.
 * Claiming one **deletes whatever the profile had** — that is how changing
 * your handle works — so anybody could take `@rosa` away from Rosa. The old
 * handle stopped resolving, `@notrosa` resolved to her profile, and every
 * printed reference, shared link and beacon that named her went dead at once,
 * with the name she now answered to chosen by whoever did it.
 *
 * The three beacon routes sitting immediately below it in the same file were
 * given this exact check in an earlier pass, and `place_beacon` states the
 * reason in words that fit here unchanged: *it was anybody's, which meant a
 * stranger could print stickers pointing at somebody else's profile.* This
 * route was missed.
 *
 * ## Language is not a display setting
 *
 * The persona generates **natively** in the chosen language on every surface —
 * chat, posts, rooms, robot speech — rather than writing English and
 * translating afterwards. `mode` picks whether that is already true
 * everywhere (`pre`) or done when asked (`on_demand`). The screen says which,
 * because a control that looked like an interface toggle would be the wrong
 * mental model for something that changes what the model is asked to produce.
 *
 * The translator is honest when it cannot work: the offline stub answers
 * `engine: "none"` with a note, rather than handing the input back as though
 * it had translated it.
 */
export function InWords() {
  const { session } = useSession();
  const uiLang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [error, setError] = useState<unknown>(null);
  const [said, setSaid] = useState("");

  const [catalogue, setCatalogue] = useState<LanguageCatalogue | null>(null);
  const [pref, setPref] = useState<LanguagePref | null>(null);
  const [lang, setLang] = useState("en");
  const [mode, setMode] = useState("pre");

  const [source, setSource] = useState("");
  const [target, setTarget] = useState("");
  const [done, setDone] = useState<Translated | null>(null);

  const [handle, setHandle] = useState("");
  const [claimed, setClaimed] = useState<HandleClaimed | null>(null);

  const [topic, setTopic] = useState("");
  const [surface, setSurface] = useState("");
  const [surfaces, setSurfaces] = useState<string[]>([]);
  const [composed, setComposed] = useState<ProfilePost | null>(null);

  async function go<T>(work: () => Promise<T>, then: (v: T) => void) {
    setError(null);
    try { then(await work()); } catch (e) { setError(e); }
  }

  useEffect(() => {
    go(() => api.languages(), setCatalogue);
    if (me) go(() => api.profileLanguage(me), (p) => {
      setPref(p); setLang(p.language); setMode(p.mode);
    });
    // The surfaces this profile can actually speak on — a picker, not a
    // blank the person has to already know the answer to.
    if (me) api.surfaces(me).then((s) => setSurfaces(s.surfaces))
      .catch(() => setSurfaces([]));
  }, [me]);

  if (!me) {
    return (
      <div className="screen">
        <h2>{tr("iw.title", uiLang)}</h2>
        <p className="muted">{tr("iw.pickfirst", uiLang)}</p>
      </div>
    );
  }

  return (
    <div className="screen">
      <h2>{tr("iw.title", uiLang)}</h2>
      <Refusal error={error} />
      {said && <p className="small">{said}</p>}

      {/* --- the language ---------------------------------------------- */}
      <div className="card">
        <h3>{tr("iw.speaks", uiLang)}</h3>
        <p className="muted small">{tr("iw.notdisplay", uiLang)}</p>
        {pref && (
          <p className="small">
            {fill(tr("iw.currently", uiLang), {
              label: <strong>{pref.label}</strong>,
              mode: pref.mode === "pre"
                ? tr("iw.mode.pre", uiLang) : tr("iw.mode.ondemand", uiLang),
            })}
          </p>
        )}
        <select value={lang} onChange={(e) => setLang(e.target.value)}>
          {(catalogue?.languages || []).map((l) => (
            <option key={l.code} value={l.code}>{l.label}</option>
          ))}
        </select>
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="pre">{tr("iw.opt.pre", uiLang)}</option>
          <option value="on_demand">{tr("iw.opt.ondemand", uiLang)}</option>
        </select>
        <button disabled={!token} onClick={() => go(
          () => api.setProfileLanguage(me, { language: lang, mode }, token),
          (p) => { setPref(p); setSaid(tr("iw.nowspeaks", uiLang)
            .replace("{label}", p.label)); })}>
          {tr("iw.setit", uiLang)}
        </button>
      </div>

      {/* --- translating something ------------------------------------- */}
      <div className="card">
        <h3>{tr("iw.translate.hdr", uiLang)}</h3>
        <p className="muted small">{tr("iw.translate.pitch", uiLang)}</p>
        <textarea value={source} rows={3}
                  onChange={(e) => setSource(e.target.value)}
                  placeholder={tr("iw.paste.ph", uiLang)} />
        <select value={target} onChange={(e) => setTarget(e.target.value)}>
          <option value="">{tr("iw.intoown", uiLang)}</option>
          {(catalogue?.languages || []).map((l) => (
            <option key={l.code} value={l.code}>
              {tr("iw.into", uiLang).replace("{label}", l.label)}
            </option>
          ))}
        </select>
        <button disabled={!token || !source} onClick={() => go(
          () => api.translate(me, source, target || undefined, token),
          setDone)}>{tr("iw.translate", uiLang)}</button>
        {done && (
          <div>
            <p className="small">{done.translation}</p>
            <p className="muted small">
              {done.engine === "none"
                ? tr("iw.nottranslated", uiLang).replace(
                    "{why}", done.note || tr("iw.nomodel", uiLang))
                : tr("iw.via", uiLang)
                    .replace("{language}", done.language)
                    .replace("{engine}", done.engine)}
            </p>
          </div>
        )}
      </div>

      {/* --- the name it answers to ------------------------------------- */}
      <div className="card">
        <h3>{tr("iw.name", uiLang)}</h3>
        <p className="muted small">
          {fill(tr("iw.claiming", uiLang),
            { replaces: <strong>{tr("iw.replaces", uiLang)}</strong> })}
        </p>
        <input value={handle} onChange={(e) => setHandle(e.target.value)}
               placeholder={tr("iw.handle.ph", uiLang)} />
        <button disabled={!token || !handle} onClick={() => go(
          () => api.claimHandle(me, handle, token),
          (c) => { setClaimed(c);
                   setSaid(tr("iw.answers", uiLang)
                     .replace("{handle}", c.handle)); })}>
          {tr("iw.claim", uiLang)}
        </button>
        {claimed && (
          <p className="muted small">
            {fill(tr("iw.reachat", uiLang),
              { url: <code>{claimed.summon}</code> })}
          </p>
        )}
      </div>

      {/* --- composing --------------------------------------------------- */}
      <div className="card">
        <h3>{tr("iw.saypublic", uiLang)}</h3>
        <input value={topic} onChange={(e) => setTopic(e.target.value)}
               placeholder={tr("iw.topic.ph", uiLang)} />
        {/* A picker over the surfaces the profile actually has, not a blank
            the person must already know the answer to. No surfaces yet →
            the post stays in-app, and the line below says where to get one. */}
        {surfaces.length > 0 ? (
          <select value={surface} onChange={(e) => setSurface(e.target.value)}>
            <option value="">{tr("iw.surface.inapp", uiLang)}</option>
            {surfaces.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        ) : (
          <p className="muted small">{tr("iw.surface.none", uiLang)}</p>
        )}
        <p className="muted small">{tr("iw.public.pitch", uiLang)}</p>
        <button disabled={!token || !topic} onClick={() => go(
          () => api.composePost(me, {
            topic, ...(surface ? { surface } : {}),
          }, token), (p) => { setComposed(p); setTopic(""); })}>
          {tr("iw.compose", uiLang)}
        </button>
        {composed && (
          composed.status === "approved" ? (
            <div>
              <p className="small">{composed.content}</p>
              <p className="muted small">{tr("iw.published", uiLang)}</p>
            </div>
          ) : (
            <p className="muted small">
              {fill(tr("iw.held", uiLang),
                { why: composed.flag_reason || composed.status })}
            </p>
          )
        )}
      </div>
    </div>
  );
}
