import { useEffect, useState } from "react";
import { api, type VoiceprintStatus , type ProfileVoice } from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The voiceprint, walked in the order FIG. 800 draws it: permission, then
 * collection, then the characteristics, then the print.
 *
 * The screen deliberately mirrors that order rather than presenting one
 * "clone my voice" button — the permission is the first box in the drawing
 * because it is the first thing that has to be true, and the readiness
 * numbers are shown because a thin enrollment should look thin.
 */
export function Voice({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [state, setState] = useState<VoiceprintStatus | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [seconds, setSeconds] = useState(45);
  const [source, setSource] = useState<"call" | "voice_note" | "direct">("voice_note");
  const [say, setSay] = useState("");
  const [spoken, setSpoken] = useState<{ basis: string; disclosure: string } | null>(null);

  const [bound, setBound] = useState<ProfileVoice | null>(null);
  const [voiceId, setVoiceId] = useState("");
  const [voiceLabel, setVoiceLabel] = useState("");

  const pid = session.profileId;

  // The voices on offer. Fetched once for the screen rather than per
  // profile: they are the deployment's, not this profile's, and the server
  // caches them anyway. A failure leaves the list empty and the typed
  // field is still there — the picker is a convenience over the id, never
  // a replacement for it.
  const [library, setLibrary] = useState<
    { id: string; name: string; gender: string; note: string;
      cloned: boolean }[]>([]);
  useEffect(() => {
    api.voiceLibrary().then((r) => setLibrary(r.voices || []))
      .catch(() => setLibrary([]));
  }, []);

  async function load() {
    if (!pid) return;
    try { setState(await api.voiceprint(pid)); }
    catch (e) { setError(e); }
    api.profileVoice(pid).then(setBound).catch(() => setBound(null));
  }
  useEffect(() => { load(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [pid]);

  async function run(fn: () => Promise<unknown>) {
    if (!pid) return;
    setBusy(true); setError(null);
    try { await fn(); await load(); }
    catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  const consented = state?.consent?.granted === true;
  const enrol = state?.enrollment;
  const print = state?.voiceprint;

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("vce.title", lang)}</h2>
        <span className="muted small">{tr("vce.lead", lang)}</span>
      </header>

      <Refusal error={error} onPlans={onPlans} variant="inline" />

      {/* Step 802 — the permission, before anything is collected. */}
      <div className="card">
        <h3>{tr("vce.step1", lang)}</h3>
        {consented ? (
          <>
            <p>
              {fill(tr("vce.granted", lang), {
                what: <b>{state?.consent.sources?.join(", ")}</b> })}
              <span className="muted small"> · {state?.consent.granted_at?.slice(0, 10)}</span>
            </p>
            <button className="warn" disabled={busy}
                    onClick={() => run(() => api.revokeVoiceprint(pid!))}>
              {tr("vce.withdraw", lang)}
            </button>
          </>
        ) : (
          <>
            <p>
              {fill(tr("vce.nothingrec", lang),
                { own: <b>{tr("vce.ownvoice", lang)}</b> })}
            </p>
            <button className="primary" disabled={busy}
                    onClick={() => run(() => api.grantVoiceConsent(pid!, {
                      own_voice: true, sources: ["call", "voice_note", "direct"],
                    }))}>
              {tr("vce.allow", lang)}
            </button>
          </>
        )}
      </div>

      {/* Steps 806–810 — samples, and what they add up to. */}
      {consented && (
        <div className="card">
          <h3>{tr("vce.step2", lang)}</h3>
          <div className="row">
            <label>{tr("vce.wherefrom", lang)}
              <select value={source} onChange={(e) => setSource(e.target.value as typeof source)}>
                <option value="voice_note">{tr("vce.src.note", lang)}</option>
                <option value="call">{tr("vce.src.call", lang)}</option>
                <option value="direct">{tr("vce.src.direct", lang)}</option>
              </select></label>
            <label>{tr("vce.seconds", lang)}
              <input type="number" min="1" value={seconds}
                     onChange={(e) => setSeconds(+e.target.value)} /></label>
          </div>
          <button disabled={busy} onClick={() => run(() => api.addVoiceSample(pid!, {
            source, seconds, turns: Math.max(1, Math.round(seconds / 4)),
          }))}>{tr("vce.addsample", lang)}</button>

          {enrol && (
            <>
              <div className="spec-row" style={{ marginTop: 12 }}>
                <div>
                  <b>{fill(tr("vce.samples", lang),
                    { n: enrol.samples, s: enrol.seconds })}</b>
                  <div className="muted small">
                    {enrol.mean_turn_seconds
                      ? tr("vce.perturn", lang).replace(
                          "{n}", String(enrol.mean_turn_seconds))
                      : tr("vce.noturns", lang)}
                    {fill(tr("vce.needs", lang), {
                      n: enrol.ready_when.samples,
                      s: enrol.ready_when.seconds,
                    })}
                  </div>
                </div>
                <span className={enrol.ready ? "tag ok" : "tag warn"}>
                  {enrol.ready
                    ? tr("vce.ready", lang) : tr("vce.notyet", lang)}
                </span>
              </div>
              {!enrol.ready && enrol.needs.length > 0 && (
                <p className="muted small">{fill(tr("vce.stillwants", lang),
                  { what: enrol.needs.join(", ") })}</p>
              )}
              <p className="muted small">{enrol.method}</p>
            </>
          )}
        </div>
      )}

      {/* Step 812 — the print, and speaking with it. */}
      {consented && (
        <div className="card">
          <h3>{tr("vce.step3", lang)}</h3>
          {print?.active ? (
            <>
              <p className="muted small">
                {fill(tr("vce.built", lang), {
                  when: print.built_at?.slice(0, 10), id: print.id })}
              </p>
              <label>{tr("vce.sayit", lang)}
                <textarea rows={2} value={say}
                          onChange={(e) => setSay(e.target.value)} /></label>
              <button className="primary" disabled={busy || !say.trim()}
                      onClick={() => run(async () => {
                        setSpoken(await api.speakInVoice(pid!, say));
                      })}>{tr("vce.speak", lang)}</button>
              {spoken && (
                <div className="guidance">
                  <div className="guidance-src">{spoken.basis}</div>
                  <p>{spoken.disclosure}</p>
                </div>
              )}
            </>
          ) : (
            <>
              <p className="muted small">
                {enrol?.ready
                  ? tr("vce.enough", lang) : tr("vce.addmore", lang)}
              </p>
              <button className="primary" disabled={busy || !enrol?.ready}
                      onClick={() => run(() => api.buildVoiceprint(pid!))}>
                {tr("vce.build", lang)}
              </button>
              {print && !print.active && (
                <p className="muted small">
                  {tr("vce.retired", lang)}
                </p>
              )}
            </>
          )}
        </div>
      )}

      <div className="card">
        <h3>{tr("vce.holds", lang)}</h3>
        <ul className="refs">
          <li>{tr("vce.hold1", lang)}</li>
          <li>{tr("vce.hold2", lang)}</li>
          <li>{tr("vce.hold3", lang)}</li>
        </ul>
        {state?.disclosure && <p className="muted small">{state.disclosure}</p>}
      </div>
      {/* The spoken voice: a reference, not a clone. The enrollment above
          is QRME learning *your* voice under an attestation; this is the
          profile speaking with a voice you made and verified on the
          engine's own surface — the deployment holds the engine key, this
          screen holds only the reference. */}
      <div className="card">
        <h3>{tr("voice.spoken.title", lang)}</h3>
        <p className="muted small">{tr("voice.spoken.lead", lang)}</p>
        {bound?.speaks && (
          <p className="small">
            {tr("voice.spoken.bound", lang)}{" "}
            <strong>{bound.label || bound.voice_id}</strong>
          </p>
        )}
        {/* The picker. Binding was an opaque id typed by hand — true to how
            the provider works, and not something a person building a
            profile can do without already knowing the id, so the voices
            actually available to them were invisible.

                asked     can a profile be pointed at a voice
                mattered  can its owner see which voices there are

            Gender rides along as a hint and nothing filters on it: a
            profile here can be a device, a drawing, an invention or an
            idea, and a voice with no stated gender is as bindable as any
            other. `cloned` is shown for the same reason the AI mark is —
            somebody choosing a real person's enrolled voice should be
            able to see that is what it is — and it restricts nobody. */}
        {library.length > 0 && (
          <select value={voiceId}
                  onChange={(e) => {
                    const v = library.find((x) => x.id === e.target.value);
                    setVoiceId(e.target.value);
                    if (v && !voiceLabel.trim()) setVoiceLabel(v.name);
                  }}
                  style={{ width: "100%", marginBottom: 8 }}>
            <option value="">{tr("voice.spoken.pick", lang)}</option>
            {library.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name}
                {v.gender ? ` · ${v.gender}` : ""}
                {v.cloned ? ` · ${tr("voice.spoken.isclone", lang)}` : ""}
                {v.note ? ` — ${v.note}` : ""}
              </option>
            ))}
          </select>
        )}
        <div className="row">
          <input value={voiceId} placeholder={tr("voice.spoken.id.ph", lang)}
                 onChange={(e) => setVoiceId(e.target.value)}
                 style={{ flex: 1 }} />
          <input value={voiceLabel}
                 placeholder={tr("voice.spoken.label.ph", lang)}
                 onChange={(e) => setVoiceLabel(e.target.value)}
                 style={{ flex: 1 }} />
        </div>
        <div className="row">
          <button disabled={busy || !pid || !session.ownerToken || !voiceId.trim()}
                  onClick={() => run(async () => {
                    await api.setProfileVoice(pid as string,
                      { voice_id: voiceId.trim(), label: voiceLabel.trim() },
                      session.ownerToken as string);
                    setVoiceId(""); setVoiceLabel("");
                  })}>
            {tr("voice.spoken.save", lang)}
          </button>
          {bound?.speaks && (
            <>
              <button disabled={busy}
                      onClick={() => run(async () => {
                        await api.setProfileVoice(pid as string,
                          { voice_id: "" }, session.ownerToken as string);
                      })}>
                {tr("voice.spoken.unbind", lang)}
              </button>
              <button disabled={busy}
                      onClick={() => run(async () => {
                        const blob = await api.sayInProfileVoice(
                          pid as string, tr("voice.spoken.bound", lang),
                          session.ownerToken as string);
                        const src = URL.createObjectURL(blob);
                        const sound = new Audio(src);
                        sound.onended = () => URL.revokeObjectURL(src);
                        void sound.play();
                      })}>
                {tr("voice.spoken.test", lang)}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}