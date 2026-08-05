import { useEffect, useRef, useState } from "react";
import { api, openCeremony, type SignatureEnvelope, type SignatureResult,
         type SigningCredential, type SigningPolicy,
         type VerifyVerdict } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Signing, from the console.
 *
 * Seven routes with no door here at all. The console could list signing
 * credentials and reproof one, and could do nothing else: not enrol one, not
 * revoke one, not read the rules a counterparty is asked to accept, not mint
 * an envelope, not sign it, not check a package handed to it from outside.
 *
 * `Referrals` had already written the gap down as a sentence — *None
 * enrolled. The ceremony can enrol one.* — under a heading with no button.
 * The ceremony page existed, `openCeremony` existed, and it posts the raw
 * assertion back to its host by `postMessage`. Nothing in this console was
 * listening, so the message went nowhere and the loop was never closed.
 * That is what this screen is: the listener, and the two calls on the far
 * side of it.
 *
 * ## Why the ceremony is a window and not a request
 *
 * WebAuthn refuses a mismatched `rpId`, and an opaque origin has none to
 * match. So the ceremony is served from the relying party's own origin and
 * the browser navigates to it. It carries no token — a bearer token in a
 * query string ends up in logs and history — which is exactly why the page
 * hands the assertion *back* and this screen makes the authenticated call.
 *
 * ## What a verdict actually says
 *
 * `valid` is only the conjunction of `checks`, so the checks are what is
 * drawn. A check that is **absent did not run**, and that is a different
 * thing from one that failed. It reads as pedantry until you see what it
 * cost: a package missing one field used to come back `signature: false` —
 * the strongest and most damaging thing this endpoint can say, said about
 * cryptography that had verified perfectly well, with the missing field
 * named in a bare Python repr. A counterparty reading that would conclude
 * they had been handed a forgery.
 *
 * So this screen never renders a tick over a partial answer. Unrun checks
 * are drawn as unrun, and `notes` is rendered verbatim underneath.
 */
export function Signing() {
  const { session } = useSession();
  const lang = visitorLang();
  const token = session.ownerToken || "";

  const [policy, setPolicy] = useState<SigningPolicy | null>(null);
  const [creds, setCreds] = useState<SigningCredential[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [said, setSaid] = useState("");

  // Enrolment
  const [enrolName, setEnrolName] = useState("");
  const [level, setLevel] = useState("self_asserted");
  const [attestor, setAttestor] = useState("");

  // Signing
  const [document, setDocument] = useState("");
  const [meaning, setMeaning] = useState("I have read and agree to this");
  const [displayText, setDisplayText] = useState("");
  const [tier, setTier] = useState("basic");
  const [envelope, setEnvelope] = useState<SignatureEnvelope | null>(null);
  const [signed, setSigned] = useState<SignatureResult | null>(null);

  // Verifying somebody else's package
  const [pasted, setPasted] = useState("");
  const [verdict, setVerdict] = useState<VerifyVerdict | null>(null);

  /* What the pending ceremony was for. The page posts one message and stops,
     and the two modes come back on the same channel, so the listener needs
     to know which call it is completing — and, for a signature, which
     envelope. Held in a ref because the listener is registered once.

     The challenge is carried here rather than read off the message: the
     ceremony page posts the *assertion* and nothing else, so an enrolment
     that expected to find the challenge in the reply would send an empty
     one and be refused for answering no challenge at all. */
  const pending = useRef<{ mode: "enroll" | "sign"; challenge: string;
                           envelope?: SignatureEnvelope } | null>(null);
  const [awaiting, setAwaiting] = useState(false);

  const refresh = () => {
    if (!token) return;
    api.signingCredentials(token)
      .then((r) => setCreds(r.credentials)).catch(setError);
  };

  useEffect(() => { api.signingPolicy().then(setPolicy).catch(setError); }, []);
  useEffect(refresh, [token]);

  useEffect(() => {
    async function onMessage(ev: MessageEvent) {
      let msg: Record<string, unknown>;
      try {
        msg = typeof ev.data === "string" ? JSON.parse(ev.data) : ev.data;
      } catch { return; }
      if (!msg || typeof msg !== "object" || !("mode" in msg)) return;
      const job = pending.current;
      if (!job) return;
      pending.current = null;
      setBusy(false); setAwaiting(false);
      if (!msg.ok) {
        // The page surfaces its own error too; repeating it here is the
        // point, because the window may already have been closed.
        setError(new Error(String(msg.error
          || tr("sgn.incomplete", lang))));
        return;
      }
      try {
        if (job.mode === "enroll" && msg.mode === "enroll") {
          const row = await api.enrollCredential({
            credential_id: String(msg.credential_id),
            attestation_object: String(msg.attestation_object),
            client_data_json: String(msg.client_data_json),
            challenge: job.challenge,
            proofing_level: level,
            display_name: enrolName || tr("sgn.thisdevice", lang),
            ...(attestor ? { proofing_attestor: attestor } : {}),
          }, token);
          setSaid(tr("sgn.enrolled.said", lang).replace(
            "{what}", row.can_sign.join(", ") || tr("sgn.nothingyet", lang)));
          refresh();
        } else if (job.mode === "sign" && msg.mode === "sign"
                   && job.envelope) {
          const res = await api.signEnvelope({
            envelope_id: job.envelope.envelope_id,
            credential_id: String(msg.credential_id),
            signature: String(msg.signature),
            authenticator_data: String(msg.authenticator_data),
            client_data_json: String(msg.client_data_json),
            platform: navigator.platform || undefined,
          }, token);
          setSigned(res);
          setEnvelope(null);
        }
      } catch (e) { setError(e); }
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [token, level, enrolName, attestor, lang]);

  async function enrol() {
    setError(null); setSaid(""); setBusy(true);
    try {
      const opts = await api.enrollOptions(
        enrolName || tr("sgn.thisdevice", lang), token);
      // The challenge rides through the ceremony and comes back to
      // `enrollCredential`, which is how the server knows this registration
      // answers the challenge it just issued rather than an older one.
      pending.current = { mode: "enroll", challenge: opts.challenge };
      const w = openCeremony({
        mode: "enroll", challenge: opts.challenge,
        user_id: opts.user.id, user_name: opts.user.name,
        display_name: opts.user.displayName,
      });
      if (!w) { pending.current = null; setBusy(false);
        setError(new Error(tr("sgn.blocked", lang))); }
      else setAwaiting(true);
    } catch (e) { setBusy(false); setError(e); }
  }

  async function mintAndSign() {
    setError(null); setSaid(""); setSigned(null); setBusy(true);
    try {
      const env = await api.requestSignature({
        document, meaning, display_text: displayText || document, tier,
      }, token);
      setEnvelope(env);
      pending.current = { mode: "sign", challenge: env.challenge,
                          envelope: env };
      const w = openCeremony({
        mode: "sign", challenge: env.challenge,
        display_text: env.display_text, meaning: env.meaning,
      });
      if (!w) { pending.current = null; setBusy(false);
        setError(new Error(tr("sgn.blocked", lang))); }
      else setAwaiting(true);
    } catch (e) { setBusy(false); setError(e); }
  }

  async function verify() {
    setError(null); setVerdict(null);
    try {
      setVerdict(await api.verifyPackage(JSON.parse(pasted)));
    } catch (e) { setError(e); }
  }

  const CHECKS = ["signature", "challenge_matches", "ceremony_is_signing",
                  "challenge_binds_payload", "payload_binds_document",
                  "payload_binds_display", "display_text_matches",
                  "user_verified"] as const;

  if (!token) {
    return (
      <div className="screen">
        <h2>{tr("sgn.title", lang)}</h2>
        <p className="muted">{tr("sgn.noaccount", lang)}</p>
      </div>
    );
  }

  return (
    <div className="screen">
      <h2>{tr("sgn.title", lang)}</h2>
      <p className="muted">{tr("sgn.lead", lang)}</p>
      <Refusal error={error} />
      {said && <p className="small">{said}</p>}

      {/* --- enrol ---------------------------------------------------- */}
      <div className="card">
        <h3>{tr("sgn.enrol", lang)}</h3>
        <p className="muted small">{tr("sgn.enrol.pitch", lang)}</p>
        <input value={enrolName} onChange={(e) => setEnrolName(e.target.value)}
               placeholder={tr("sgn.device.ph", lang)} />
        <label className="small">{tr("sgn.checked", lang)}</label>
        <select value={level} onChange={(e) => setLevel(e.target.value)}>
          {(policy?.proofing_levels || ["self_asserted"]).map((p) => (
            <option key={p} value={p}>{p.replace(/_/g, " ")}</option>
          ))}
        </select>
        {level !== "self_asserted" && (
          <input value={attestor} onChange={(e) => setAttestor(e.target.value)}
                 placeholder={tr("sgn.attestor.ph", lang)} />
        )}
        <p className="muted small">
          {fill(tr("sgn.tierpitch", lang),
            { and: <em>{tr("sgn.and", lang)}</em> })}
        </p>
        <button disabled={busy} onClick={enrol}>
          {tr("sgn.open", lang)}
        </button>
        {awaiting && (
          <p className="muted small">{tr("sgn.waiting", lang)}</p>
        )}
      </div>

      {/* --- what is enrolled ----------------------------------------- */}
      <div className="card">
        <h3>{tr("sgn.have", lang)}</h3>
        {creds.length === 0 && (
          <p className="muted small">{tr("sgn.none", lang)}</p>
        )}
        {creds.map((c) => (
          <div key={c.id} className="row">
            <div>
              <p className="small">
                {fill(tr("sgn.cred.line", lang), {
                  name: <strong>{c.display_name}</strong>,
                  level: c.proofing_level.replace(/_/g, " "),
                })}
                {!c.device_bound && <span className="muted">
                  {" "}{tr("sgn.syncs", lang)}</span>}
                {c.revoked_at && <span className="muted">
                  {" "}{tr("sgn.revoked", lang)}</span>}
              </p>
              <p className="muted small">
                {c.can_sign.length
                  ? tr("sgn.signs", lang)
                      .replace("{what}", c.can_sign.join(", "))
                  : tr("sgn.signsnothing", lang)}
              </p>
            </div>
            {!c.revoked_at && (
              <button className="ghost" disabled={busy}
                      onClick={async () => {
                        setError(null);
                        try {
                          await api.revokeCredential(c.id, token);
                          setSaid(tr("sgn.revoked.said", lang));
                          refresh();
                        } catch (e) { setError(e); }
                      }}>{tr("sgn.revoke", lang)}</button>
            )}
          </div>
        ))}
      </div>

      {/* --- sign something ------------------------------------------- */}
      <div className="card">
        <h3>{tr("sgn.sign", lang)}</h3>
        <textarea value={document} rows={4}
                  onChange={(e) => setDocument(e.target.value)}
                  placeholder={tr("sgn.doc.ph", lang)} />
        <input value={meaning} onChange={(e) => setMeaning(e.target.value)}
               placeholder={tr("sgn.meaning.ph", lang)} />
        <input value={displayText}
               onChange={(e) => setDisplayText(e.target.value)}
               placeholder={tr("sgn.display.ph", lang)} />
        <select value={tier} onChange={(e) => setTier(e.target.value)}>
          {Object.keys(policy?.tiers || { basic: null }).map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <p className="muted small">
          {fill(tr("sgn.challenge", lang),
            { is: <em>{tr("sgn.is", lang)}</em> })}
        </p>
        <button disabled={busy || !document} onClick={mintAndSign}>
          {tr("sgn.mint", lang)}
        </button>
        {envelope && !signed && (
          <p className="muted small">
            {fill(tr("sgn.envelope", lang), {
              id: envelope.envelope_id, when: envelope.expires_at })}
          </p>
        )}
        {signed && (
          <div>
            <p className="small">
              {fill(tr("sgn.signedas", lang), {
                name: <strong>{signed.signer.name}</strong>,
                level: signed.signer.proofing_level.replace(/_/g, " "),
                tier: signed.tier,
              })}
            </p>
            <p className="muted small">
              {fill(tr("sgn.sigline", lang), {
                id: signed.signature_id, text: signed.display_text,
                meaning: signed.meaning,
              })}
            </p>
          </div>
        )}
      </div>

      {/* --- check somebody else's ------------------------------------ */}
      <div className="card">
        <h3>{tr("sgn.check", lang)}</h3>
        <p className="muted small">{tr("sgn.check.pitch", lang)}</p>
        <textarea value={pasted} rows={5}
                  onChange={(e) => setPasted(e.target.value)}
                  placeholder={tr("sgn.paste.ph", lang)} />
        <button disabled={!pasted} onClick={verify}>
          {tr("sgn.checkit", lang)}
        </button>
        {verdict && (
          <div>
            <p className="small">
              <strong>
                {verdict.valid
                  ? tr("sgn.holds", lang) : tr("sgn.doesnot", lang)}
              </strong>
            </p>
            {CHECKS.map((k) => {
              const v = verdict.checks[k];
              return (
                <p key={k} className="muted small">
                  {v === true ? "✓" : v === false ? "✗" : "—"}{" "}
                  {k.replace(/_/g, " ")}
                  {v === undefined && (
                    <span> {tr("sgn.didnotrun", lang)}</span>
                  )}
                </p>
              );
            })}
            {verdict.notes.map((n, i) => (
              <p key={i} className="muted small">{n}</p>
            ))}
          </div>
        )}
      </div>

      {/* --- the rules ------------------------------------------------ */}
      {policy && (
        <div className="card">
          <h3>{tr("sgn.limits", lang)}</h3>
          <p className="muted small">{policy.standard}</p>
          {policy.limits.map((l, i) => (
            <p key={i} className="muted small">{l}</p>
          ))}
        </div>
      )}
    </div>
  );
}
