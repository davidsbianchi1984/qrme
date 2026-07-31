import { useEffect, useState } from "react";
import { api, type VoiceprintStatus } from "../api";
import { Refusal } from "../Refusal";
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
  const [state, setState] = useState<VoiceprintStatus | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [seconds, setSeconds] = useState(45);
  const [source, setSource] = useState<"call" | "voice_note" | "direct">("voice_note");
  const [say, setSay] = useState("");
  const [spoken, setSpoken] = useState<{ basis: string; disclosure: string } | null>(null);

  const pid = session.profileId;

  async function load() {
    if (!pid) return;
    try { setState(await api.voiceprint(pid)); }
    catch (e) { setError(e); }
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
        <h2>Voice</h2>
        <span className="muted small">your own voice, with your permission</span>
      </header>

      <Refusal error={error} onPlans={onPlans} variant="inline" />

      {/* Step 802 — the permission, before anything is collected. */}
      <div className="card">
        <h3>1 · Permission</h3>
        {consented ? (
          <>
            <p>
              Granted for: <b>{state?.consent.sources?.join(", ")}</b>
              <span className="muted small"> · {state?.consent.granted_at?.slice(0, 10)}</span>
            </p>
            <button className="warn" disabled={busy}
                    onClick={() => run(() => api.revokeVoiceprint(pid!))}>
              Withdraw consent — delete the samples, retire the voice
            </button>
          </>
        ) : (
          <>
            <p>
              Nothing is recorded until you say so. QRME will only learn{" "}
              <b>your own voice</b> — there is no path here for anybody else's.
            </p>
            <button className="primary" disabled={busy}
                    onClick={() => run(() => api.grantVoiceConsent(pid!, {
                      own_voice: true, sources: ["call", "voice_note", "direct"],
                    }))}>
              This is my own voice — allow enrollment
            </button>
          </>
        )}
      </div>

      {/* Steps 806–810 — samples, and what they add up to. */}
      {consented && (
        <div className="card">
          <h3>2 · Enrollment</h3>
          <div className="row">
            <label>Where from
              <select value={source} onChange={(e) => setSource(e.target.value as typeof source)}>
                <option value="voice_note">A voice note</option>
                <option value="call">A call</option>
                <option value="direct">A direct recording</option>
              </select></label>
            <label>Seconds of speech
              <input type="number" min="1" value={seconds}
                     onChange={(e) => setSeconds(+e.target.value)} /></label>
          </div>
          <button disabled={busy} onClick={() => run(() => api.addVoiceSample(pid!, {
            source, seconds, turns: Math.max(1, Math.round(seconds / 4)),
          }))}>Add this sample</button>

          {enrol && (
            <>
              <div className="spec-row" style={{ marginTop: 12 }}>
                <div>
                  <b>{enrol.samples} sample(s) · {enrol.seconds}s</b>
                  <div className="muted small">
                    {enrol.mean_turn_seconds
                      ? `about ${enrol.mean_turn_seconds}s a turn`
                      : "no turns counted yet"}
                    {" · needs "}{enrol.threshold.samples} samples and{" "}
                    {enrol.threshold.seconds}s
                  </div>
                </div>
                <span className={enrol.ready ? "tag ok" : "tag warn"}>
                  {enrol.ready ? "ready" : "not yet"}
                </span>
              </div>
              {!enrol.ready && enrol.needs.length > 0 && (
                <p className="muted small">Still wants: {enrol.needs.join(", ")}.</p>
              )}
              <p className="muted small">{enrol.method}</p>
            </>
          )}
        </div>
      )}

      {/* Step 812 — the print, and speaking with it. */}
      {consented && (
        <div className="card">
          <h3>3 · The voice</h3>
          {print?.active ? (
            <>
              <p className="muted small">
                Built {print.built_at?.slice(0, 10)} · {print.id}
              </p>
              <label>Say something in it
                <textarea rows={2} value={say}
                          onChange={(e) => setSay(e.target.value)} /></label>
              <button className="primary" disabled={busy || !say.trim()}
                      onClick={() => run(async () => {
                        setSpoken(await api.speakInVoice(pid!, say));
                      })}>Speak</button>
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
                  ? "Enough of your voice is on record — mint the voiceprint."
                  : "Add a few more samples first."}
              </p>
              <button className="primary" disabled={busy || !enrol?.ready}
                      onClick={() => run(() => api.buildVoiceprint(pid!))}>
                Build my voiceprint
              </button>
              {print && !print.active && (
                <p className="muted small">
                  A previous voiceprint was retired when consent was withdrawn.
                  That record stays.
                </p>
              )}
            </>
          )}
        </div>
      )}

      <div className="card">
        <h3>What always holds</h3>
        <ul className="refs">
          <li>Anything spoken in this voice carries a watermark and says it is synthesized.</li>
          <li>Only your own voice — the permission is an attestation, not a checkbox.</li>
          <li>Withdrawing deletes the samples and silences the voice; the withdrawal stays on record.</li>
        </ul>
        {state?.disclosure && <p className="muted small">{state.disclosure}</p>}
      </div>
    </div>
  );
}
