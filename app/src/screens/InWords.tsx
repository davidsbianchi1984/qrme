import { useEffect, useState } from "react";
import { api, type HandleClaimed, type LanguageCatalogue,
         type LanguagePref, type ProfilePost, type Translated } from "../api";
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
  }, [me]);

  if (!me) {
    return (
      <div className="screen">
        <h2>In its own words</h2>
        <p className="muted">Choose a profile first.</p>
      </div>
    );
  }

  return (
    <div className="screen">
      <h2>In its own words</h2>
      <Refusal error={error} />
      {said && <p className="small">{said}</p>}

      {/* --- the language ---------------------------------------------- */}
      <div className="card">
        <h3>What it speaks</h3>
        <p className="muted small">
          Not a display setting. The persona writes in this language natively
          on every surface it appears — chat, posts, rooms, a robot speaking
          aloud — rather than writing English and translating afterwards.
        </p>
        {pref && (
          <p className="small">
            Currently <strong>{pref.label}</strong>, {pref.mode === "pre"
              ? "already in that language everywhere"
              : "translated when asked for"}.
          </p>
        )}
        <select value={lang} onChange={(e) => setLang(e.target.value)}>
          {(catalogue?.languages || []).map((l) => (
            <option key={l.code} value={l.code}>{l.label}</option>
          ))}
        </select>
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="pre">everywhere, already</option>
          <option value="on_demand">when asked for</option>
        </select>
        <button disabled={!token} onClick={() => go(
          () => api.setProfileLanguage(me, { language: lang, mode }, token),
          (p) => { setPref(p); setSaid(`Now speaks ${p.label}.`); })}>
          Set it
        </button>
      </div>

      {/* --- translating something ------------------------------------- */}
      <div className="card">
        <h3>Translate something it ran across</h3>
        <p className="muted small">
          An interactor's message, a room turn, a listing. Done with this
          profile's own model, into its language unless you name another.
        </p>
        <textarea value={source} rows={3}
                  onChange={(e) => setSource(e.target.value)}
                  placeholder="paste the text" />
        <select value={target} onChange={(e) => setTarget(e.target.value)}>
          <option value="">into its own language</option>
          {(catalogue?.languages || []).map((l) => (
            <option key={l.code} value={l.code}>into {l.label}</option>
          ))}
        </select>
        <button disabled={!token || !source} onClick={() => go(
          () => api.translate(me, source, target || undefined, token),
          setDone)}>Translate</button>
        {done && (
          <div>
            <p className="small">{done.translation}</p>
            <p className="muted small">
              {done.engine === "none"
                ? `Not translated — ${done.note || "no model available"}.`
                : `${done.language} · via ${done.engine}`}
            </p>
          </div>
        )}
      </div>

      {/* --- the name it answers to ------------------------------------- */}
      <div className="card">
        <h3>The name it answers to</h3>
        <p className="muted small">
          Claiming a handle <strong>replaces</strong> whatever this profile had
          — the old one stops resolving, and anything printed or shared that
          named it stops working. That is why only its owner may do this, and
          why the route asking for nothing was worth more than a second name.
        </p>
        <input value={handle} onChange={(e) => setHandle(e.target.value)}
               placeholder="rosa" />
        <button disabled={!token || !handle} onClick={() => go(
          () => api.claimHandle(me, handle, token),
          (c) => { setClaimed(c);
                   setSaid(`Answers to ${c.handle}.`); })}>
          Claim it
        </button>
        {claimed && (
          <p className="muted small">
            Anybody can now reach it at <code>{claimed.summon}</code>.
          </p>
        )}
      </div>

      {/* --- composing --------------------------------------------------- */}
      <div className="card">
        <h3>Say something publicly</h3>
        <input value={topic} onChange={(e) => setTopic(e.target.value)}
               placeholder="what it should post about" />
        <input value={surface} onChange={(e) => setSurface(e.target.value)}
               placeholder="which surface (optional)" />
        <p className="muted small">
          A public post faces the widest audience there is, so it always runs
          the strict filter — and it carries a synthetic-media credential from
          the moment it exists.
        </p>
        <button disabled={!token || !topic} onClick={() => go(
          () => api.composePost(me, {
            topic, ...(surface ? { surface } : {}),
          }, token), (p) => { setComposed(p); setTopic(""); })}>
          Compose
        </button>
        {composed && (
          composed.status === "approved" ? (
            <div>
              <p className="small">{composed.content}</p>
              <p className="muted small">Published.</p>
            </div>
          ) : (
            <p className="muted small">
              Held — {composed.flag_reason || composed.status}. The text is not
              returned here, deliberately, and it is not public either. It is
              waiting in the mark screen's queue.
            </p>
          )
        )}
      </div>
    </div>
  );
}
