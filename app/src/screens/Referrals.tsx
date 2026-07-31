import { useEffect, useState } from "react";
import { api, openCeremony, type Certificate, type Clinician,
         type ClinicalNote, type Provider, type ReferralHistory,
         type ReferralOpened, type ReferralPrepared,
         type SigningCredential } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Handing a conversation to a clinician.
 *
 * A profile is not a clinician and this screen never pretends otherwise — the
 * package it assembles carries that sentence and shows it before anything is
 * signed. What the feature actually is: a person who has been talking to a
 * profile about a symptom can hand that conversation to somebody qualified,
 * once, under a signature that covers the exact words.
 *
 * The order matters and the screen keeps it visible:
 *
 * 1. **prepare** assembles the summary and releases *nothing*. The challenge
 *    it raises **is the hash of those bytes**, so signing it signs this
 *    summary rather than a checkbox — and a summary edited afterwards cannot
 *    ride the old signature;
 * 2. **the ceremony** runs in a window on the API's own origin, because
 *    WebAuthn refuses a mismatched `rpId` and an opaque origin has none to
 *    match. It carries no token: a bearer token in a query string ends up in
 *    logs and history;
 * 3. **release** mints a one-time link, and only if the signature really
 *    covers this referral.
 *
 * Three pairs are easy to confuse, and each one is labelled here rather than
 * left to the reader:
 *
 * - the **referral token** opens it; the **reply token** answers it, and does
 *   not exist until the link has been opened;
 * - `envelope_id` is what you sign; `signature_id` is what release checks;
 * - a **second open fails on purpose**. A replayed link is something the
 *   patient should be able to discover, so it 410s with the time of the first
 *   open rather than quietly working again.
 *
 * The signing credential's `can_sign` list is shown rather than the tier
 * rules, because that is the fact somebody needs: a self-asserted credential
 * signs `basic` only, and a referral is `high`.
 */
export function Referrals({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const me = session.profileId || "";
  const interactor = session.interactorId || "";
  const token = session.interactorToken || session.ownerToken || "";
  const ownerToken = session.ownerToken || "";

  const [area, setArea] = useState("");
  const [where, setWhere] = useState("");
  const [found, setFound] = useState<Clinician[]>([]);
  const [directory, setDirectory] = useState<Provider[]>([]);

  const [prepared, setPrepared] = useState<ReferralPrepared | null>(null);
  const [signatureId, setSignatureId] = useState("");
  const [released, setReleased] = useState<{ id: string; token: string } | null>(
    null);

  const [history, setHistory] = useState<ReferralHistory[]>([]);
  const [notes, setNotes] = useState<ClinicalNote[]>([]);
  const [creds, setCreds] = useState<SigningCredential[]>([]);
  const [cert, setCert] = useState<Certificate | null>(null);

  const [openId, setOpenId] = useState("");
  const [openToken, setOpenToken] = useState("");
  const [opened, setOpened] = useState<ReferralOpened | null>(null);
  const [reply, setReply] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fail = (e: unknown) => setError(e);

  function load() {
    api.providers().then(setDirectory).catch(() => setDirectory([]));
    if (interactor && token) {
      api.myReferrals(interactor, token).then(setHistory)
        .catch(() => setHistory([]));
      api.signingCredentials(token).then((r) => setCreds(r.credentials))
        .catch(() => setCreds([]));
    }
    if (me && interactor && ownerToken) {
      api.clinicalNotes(me, interactor, ownerToken).then(setNotes)
        .catch(() => setNotes([]));
    }
  }
  useEffect(load, [me, interactor, token, ownerToken]);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { fail(e); } finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>Handing it to somebody qualified</h2>
      <p className="muted small">
        A profile is not a clinician. This is how a conversation with one
        reaches somebody who is — once, and only under your signature.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Who can help</h3>
        <p className="muted small">
          Expertise filters and geography ranks, never the other way round —
          a cardiologist two streets away is not a substitute for a
          psychiatrist. An empty list is an answer.
        </p>
        <div className="row">
          <input value={area} onChange={(e) => setArea(e.target.value)}
                 placeholder="what you need, e.g. physiotherapy"
                 style={{ flex: 1 }} />
          <input value={where} onChange={(e) => setWhere(e.target.value)}
                 placeholder="where you are" style={{ flex: 1 }} />
          <button disabled={busy || !area.trim()}
                  onClick={act(async () => setFound(await api.clinicians(
                    area.trim(), where.trim() || undefined)))}>Find</button>
        </div>
        {found.length === 0 && (
          <p className="muted small">
            Nobody listed for that yet — which is said plainly rather than
            offering a near-miss.
          </p>
        )}
        {found.map((cl) => (
          <div className="row" key={cl.id}>
            <div style={{ flex: 1 }}>
              <strong>{cl.name}</strong>
              <div className="muted small">
                {cl.area}{cl.location && ` · ${cl.location}`} ·{" "}
                {/* In words, not a score. */}
                matched on {cl.match}
                {cl.in_your_area && " · near you"}
              </div>
            </div>
            <button disabled={busy || !me || !interactor || !token}
                    onClick={act(async () => {
                      setReleased(null); setSignatureId("");
                      setPrepared(await api.prepareReferral({
                        interactor_id: interactor, profile_id: me,
                        provider_id: cl.id }, token));
                    })}>Prepare</button>
          </div>
        ))}
        <details>
          <summary className="small">
            The directory — {directory.length}{" "}
            {directory.length === 1 ? "clinician" : "clinicians"} listed
          </summary>
          {directory.map((d) => (
            <p className="muted small" key={d.id}>
              {d.name} — {d.area}{d.location && ` · ${d.location}`}
            </p>
          ))}
          <AddProvider onAdded={load} />
        </details>
      </div>

      {prepared && (
        <div className="card">
          <h3>Read this before you sign</h3>
          {/* Nothing has been released at this point, and saying so is the
              reason prepare is a separate step at all. */}
          <p className="muted small">
            Nothing has gone anywhere yet. This is what would.
          </p>
          <p className="small">{prepared.display_text}</p>

          {/* The single most important line in the package. */}
          <div className="error">
            <p className="small">{prepared.package.specialist.note}</p>
          </div>

          <h4>The summary</h4>
          {prepared.package.recent_exchange.map((m, i) => (
            <p className="small" key={i}>
              <strong>{m.role === "profile" ? "the profile" : "you"}</strong>:{" "}
              {m.content}
            </p>
          ))}

          <p className="muted small">
            The signature is over these exact words — the challenge is their
            hash — so a summary changed afterwards cannot ride it.
          </p>

          <div className="row">
            <button disabled={busy} onClick={() => openCeremony({
              mode: "sign", challenge: prepared.sign.challenge,
              display_text: prepared.sign.display_text,
              meaning: String(prepared.sign.payload.meaning || ""),
            })}>Sign it with your device</button>
          </div>
          <div className="row">
            {/* `signature_id`, not `envelope_id` — the ceremony returns the
                first and the card above shows the second, and release
                checks the first. */}
            <input value={signatureId}
                   onChange={(e) => setSignatureId(e.target.value)}
                   placeholder="the signature id the ceremony gave back"
                   style={{ flex: 1 }} />
            <button disabled={busy || !signatureId.trim()}
                    onClick={act(async () => {
                      const r = await api.releaseReferral(
                        prepared.referral_id, signatureId.trim(), token);
                      setReleased({ id: r.id, token: r.token });
                    }, "Released.")}>Release it</button>
          </div>
        </div>
      )}

      {released && (
        <div className="card">
          <h3>The link for the clinician</h3>
          <p className="small"><code>{released.token}</code></p>
          <p className="muted small">
            It opens once. A second attempt fails with the time of the first,
            rather than quietly working — a replayed link is something you
            should be able to find out about.
          </p>
        </div>
      )}

      <div className="card">
        <h3>Your signing credentials</h3>
        <p className="muted small">
          A referral is a <strong>high</strong>-tier signature. What a
          credential can sign follows from how your identity was checked, and
          from whether the key stayed on one device.
        </p>
        {creds.length === 0 && (
          <p className="muted small">
            None enrolled. The ceremony can enrol one.
          </p>
        )}
        {creds.map((cr) => (
          <div key={cr.id}>
            <p className="small">
              <strong>{cr.display_name}</strong> — checked as{" "}
              {cr.proofing_level.replace(/_/g, " ")}
              {!cr.device_bound && (
                <span className="muted"> · syncs between devices</span>
              )}
            </p>
            {/* The consequence, not the rule. */}
            <p className="muted small">
              Can sign: {cr.can_sign.join(", ") || "nothing"}
              {!cr.can_sign.includes("high")
                && " — not enough for a referral yet"}
            </p>
            <Reproof rowId={cr.id} token={token} onDone={load} />
          </div>
        ))}
      </div>

      {history.length > 0 && (
        <div className="card">
          <h3>What you have released</h3>
          {history.map((h) => (
            <p className="small" key={h.id}>
              <code>{h.id}</code> ·{" "}
              {h.opened_at
                ? `opened ${h.opened_at.replace("T", " ").slice(0, 16)}`
                : "not opened yet"}
              {h.signature_id && (
                <>
                  {" "}·{" "}
                  <button className="chip" disabled={busy}
                          onClick={act(async () => setCert(
                            await api.certificate(h.signature_id!)))}>
                    certificate
                  </button>
                </>
              )}
            </p>
          ))}
        </div>
      )}

      {cert && (
        <div className="card">
          <h3>The certificate</h3>
          <p className="small">
            <strong>{cert.printed_name}</strong> signed{" "}
            {cert.signed_at.replace("T", " ").slice(0, 16)}, identity checked
            as {cert.identity_verified_as.replace(/_/g, " ")} ({cert.tier}).
          </p>
          <p className="small">{cert.meaning}</p>
          {/* The bytes that were actually shown, beside the hash of them. A
              signature over a document nobody saw is a signature over
              nothing, and this is the field that proves otherwise. */}
          <h4>What was on the screen</h4>
          <p className="small">{cert.what_was_shown}</p>
          <p className="muted small">
            Document <code>{cert.document_sha256.slice(0, 16)}…</code>
          </p>
          <p className="muted small">{cert.standard}</p>
        </div>
      )}

      {notes.length > 0 && (
        <div className="card">
          <h3>What the clinician wrote back</h3>
          <p className="muted small">
            Their words, attributed to them. The profile never recites this
            as its own knowledge.
          </p>
          {notes.map((n) => (
            <p className="small" key={n.id}>
              <strong>{n.from}</strong> · {n.at.slice(0, 10)}<br />
              {n.content}
            </p>
          ))}
        </div>
      )}

      <div className="card">
        <h3>If you are the clinician</h3>
        <p className="muted small">
          No account needed — the link is the credential, and it works once.
        </p>
        <div className="row">
          <input value={openId} onChange={(e) => setOpenId(e.target.value)}
                 placeholder="referral id" style={{ flex: 1 }} />
          <input value={openToken}
                 onChange={(e) => setOpenToken(e.target.value)}
                 placeholder="the token from the link" style={{ flex: 1 }} />
          <button disabled={busy || !openId.trim() || !openToken.trim()}
                  onClick={act(async () => setOpened(await api.openReferral(
                    openId.trim(), openToken.trim())))}>Open it</button>
        </div>
        {opened && (
          <>
            <div className="error">
              <p className="small">{opened.package.specialist.note}</p>
            </div>
            {opened.package.recent_exchange.map((m, i) => (
              <p className="small" key={i}>
                <strong>{m.role === "profile" ? "the profile" : "the patient"}
                </strong>: {m.content}
              </p>
            ))}
            <p className="muted small">{opened.note}</p>
            <h4>Write back, once</h4>
            <p className="muted small">{opened.reply_note}</p>
            <textarea value={reply} onChange={(e) => setReply(e.target.value)}
                      rows={3} placeholder="what you want the patient to know" />
            {/* The reply token, which arrived with the open — not the token
                that opened it. */}
            <button disabled={busy || !reply.trim()}
                    onClick={act(async () => {
                      await api.replyToReferral(
                        opened.id, opened.reply_token, reply.trim());
                      setReply("");
                    }, "Sent.")}>Send it</button>
          </>
        )}
      </div>
    </div>
  );
}

function AddProvider({ onAdded }: { onAdded: () => void }) {
  const [name, setName] = useState("");
  const [area, setArea] = useState("");
  const [where, setWhere] = useState("");
  const [contact, setContact] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <div className="row">
      <input value={name} onChange={(e) => setName(e.target.value)}
             placeholder="name" style={{ flex: 1 }} />
      <input value={area} onChange={(e) => setArea(e.target.value)}
             placeholder="area of expertise" style={{ flex: 1 }} />
      <input value={where} onChange={(e) => setWhere(e.target.value)}
             placeholder="where" style={{ flex: 1 }} />
      <input value={contact} onChange={(e) => setContact(e.target.value)}
             placeholder="how to reach them" style={{ flex: 1 }} />
      <button disabled={busy || !name.trim() || !area.trim()}
              onClick={async () => {
                setBusy(true);
                try {
                  await api.addProvider({
                    name: name.trim(), area: area.trim(),
                    location: where.trim() || undefined,
                    contact: contact.trim() || undefined, business: true });
                  setName(""); setArea(""); setWhere(""); setContact("");
                  onAdded();
                } finally { setBusy(false); }
              }}>Add</button>
    </div>
  );
}

/** Recording a fresh identity check against a credential already enrolled.
 *
 *  Enrolment fixes a level; this is how it moves — and it applies going
 *  forward only, because a signature already made carries the level it was
 *  made at. Raising it later cannot retroactively strengthen something
 *  somebody signed under a weaker check. */
function Reproof({ rowId, token, onDone }: {
  rowId: string; token: string; onDone: () => void;
}) {
  const [level, setLevel] = useState("document");
  const [attestor, setAttestor] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <div className="row">
      <select value={level} onChange={(e) => setLevel(e.target.value)}>
        {["self_asserted", "federated", "document", "in_person"].map((l) => (
          <option key={l} value={l}>{l.replace(/_/g, " ")}</option>
        ))}
      </select>
      <input value={attestor} onChange={(e) => setAttestor(e.target.value)}
             placeholder="who checked it" style={{ flex: 1 }} />
      <button disabled={busy || !attestor.trim() || !token}
              onClick={async () => {
                setBusy(true);
                try {
                  await api.reproof(rowId, {
                    proofing_level: level,
                    proofing_attestor: attestor.trim() }, token);
                  setAttestor(""); onDone();
                } finally { setBusy(false); }
              }}>Record a check</button>
    </div>
  );
}
