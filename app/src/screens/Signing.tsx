import { useEffect, useRef, useState } from "react";
import { api, openCeremony, type SignatureEnvelope, type SignatureResult,
         type SigningCredential, type SigningPolicy,
         type VerifyVerdict } from "../api";
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
          || "the ceremony did not complete")));
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
            display_name: enrolName || "This device",
            ...(attestor ? { proofing_attestor: attestor } : {}),
          }, token);
          setSaid(`Enrolled — this credential can sign `
            + `${row.can_sign.join(", ") || "nothing yet"}.`);
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
  }, [token, level, enrolName, attestor]);

  async function enrol() {
    setError(null); setSaid(""); setBusy(true);
    try {
      const opts = await api.enrollOptions(enrolName || "This device", token);
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
        setError(new Error("the ceremony window was blocked")); }
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
        setError(new Error("the ceremony window was blocked")); }
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
        <h2>Signing</h2>
        <p className="muted">
          Signing is done as an account, not as a profile page. Sign in as an
          owner to enrol a credential.
        </p>
      </div>
    );
  }

  return (
    <div className="screen">
      <h2>Signing</h2>
      <p className="muted">
        A signature here is a device credential used with user verification
        over one exact document. What that does and does not prove is written
        below, in the words a counterparty will read.
      </p>
      <Refusal error={error} />
      {said && <p className="small">{said}</p>}

      {/* --- enrol ---------------------------------------------------- */}
      <div className="card">
        <h3>Enrol a credential</h3>
        <p className="muted small">
          The ceremony opens in its own window, on the API's own origin —
          WebAuthn refuses a credential whose relying party does not match,
          and this app's origin is not one it can match. That window carries
          no token; it hands the registration back here, and this screen makes
          the call.
        </p>
        <input value={enrolName} onChange={(e) => setEnrolName(e.target.value)}
               placeholder="what to call this device" />
        <label className="small">How your identity was checked</label>
        <select value={level} onChange={(e) => setLevel(e.target.value)}>
          {(policy?.proofing_levels || ["self_asserted"]).map((p) => (
            <option key={p} value={p}>{p.replace(/_/g, " ")}</option>
          ))}
        </select>
        {level !== "self_asserted" && (
          <input value={attestor} onChange={(e) => setAttestor(e.target.value)}
                 placeholder="who checked it (required above self-asserted)" />
        )}
        <p className="muted small">
          This fixes what the credential may sign. A self-asserted one signs
          the basic tier only; the high tier wants a document check <em>and</em>
          {" "}a key that stayed on one device.
        </p>
        <button disabled={busy} onClick={enrol}>Open the ceremony</button>
        {awaiting && (
          <p className="muted small">Waiting for the ceremony window.</p>
        )}
      </div>

      {/* --- what is enrolled ----------------------------------------- */}
      <div className="card">
        <h3>What this account can sign with</h3>
        {creds.length === 0 && (
          <p className="muted small">Nothing enrolled yet.</p>
        )}
        {creds.map((c) => (
          <div key={c.id} className="row">
            <div>
              <p className="small">
                <strong>{c.display_name}</strong> — checked as{" "}
                {c.proofing_level.replace(/_/g, " ")}
                {!c.device_bound
                  && <span className="muted"> · syncs between devices</span>}
                {c.revoked_at && <span className="muted"> · revoked</span>}
              </p>
              <p className="muted small">
                {c.can_sign.length
                  ? `Signs: ${c.can_sign.join(", ")}`
                  : "Signs nothing — revoked, or not proofed to any tier"}
              </p>
            </div>
            {!c.revoked_at && (
              <button className="ghost" disabled={busy}
                      onClick={async () => {
                        setError(null);
                        try {
                          await api.revokeCredential(c.id, token);
                          setSaid("Revoked, going forward. Anything already "
                                  + "signed with it stays verifiable — its "
                                  + "public key is in the evidence, not here.");
                          refresh();
                        } catch (e) { setError(e); }
                      }}>Revoke</button>
            )}
          </div>
        ))}
      </div>

      {/* --- sign something ------------------------------------------- */}
      <div className="card">
        <h3>Sign a document</h3>
        <textarea value={document} rows={4}
                  onChange={(e) => setDocument(e.target.value)}
                  placeholder="the exact text being signed" />
        <input value={meaning} onChange={(e) => setMeaning(e.target.value)}
               placeholder="what signing it means" />
        <input value={displayText}
               onChange={(e) => setDisplayText(e.target.value)}
               placeholder="what you will be shown when you sign" />
        <select value={tier} onChange={(e) => setTier(e.target.value)}>
          {Object.keys(policy?.tiers || { basic: null }).map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <p className="muted small">
          The challenge <em>is</em> the hash of this document, so the signature
          covers these bytes and no others. Edit the text afterwards and the
          old signature will not carry — which is the point of it.
        </p>
        <button disabled={busy || !document} onClick={mintAndSign}>
          Mint an envelope and sign it
        </button>
        {envelope && !signed && (
          <p className="muted small">
            Envelope {envelope.envelope_id}, good until {envelope.expires_at}.
            Finish in the ceremony window.
          </p>
        )}
        {signed && (
          <div>
            <p className="small">
              Signed as <strong>{signed.signer.name}</strong>, proofed{" "}
              {signed.signer.proofing_level.replace(/_/g, " ")} — {signed.tier}{" "}
              tier.
            </p>
            <p className="muted small">
              Signature {signed.signature_id}. Over “{signed.display_text}”,
              meaning “{signed.meaning}”.
            </p>
          </div>
        )}
      </div>

      {/* --- check somebody else's ------------------------------------ */}
      <div className="card">
        <h3>Check a package somebody handed you</h3>
        <p className="muted small">
          This asks nothing of us. The package carries its own public key and
          its own hashes, and the arithmetic either holds or it does not — a
          check that needed our blessing would be us vouching, which is the
          opposite of what the evidence is for.
        </p>
        <textarea value={pasted} rows={5}
                  onChange={(e) => setPasted(e.target.value)}
                  placeholder="paste the evidence package (JSON)" />
        <button disabled={!pasted} onClick={verify}>Check it</button>
        {verdict && (
          <div>
            <p className="small">
              <strong>
                {verdict.valid ? "Holds up." : "Does not hold up."}
              </strong>
            </p>
            {CHECKS.map((k) => {
              const v = verdict.checks[k];
              return (
                <p key={k} className="muted small">
                  {v === true ? "✓" : v === false ? "✗" : "—"}{" "}
                  {k.replace(/_/g, " ")}
                  {v === undefined && (
                    <span> · did not run, so it is not a pass</span>
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
          <h3>What this does not prove</h3>
          <p className="muted small">{policy.standard}</p>
          {policy.limits.map((l, i) => (
            <p key={i} className="muted small">{l}</p>
          ))}
        </div>
      )}
    </div>
  );
}
