import { useEffect, useState } from "react";
import { api, type HeldMessage, type ObjectionAudit, type ObjectionOpened,
         type ObjectionStatus } from "../api";
import { useSession } from "../store";

/**
 * Contesting a profile that depicts you, and holding what one says.
 *
 * Nine routes with no caller — including the takedown path for a product whose
 * whole subject is synthetic people who can be mistaken for real ones. A person
 * who found a profile of themselves had no way, from here, to say so.
 *
 * Two things about this feature the screen has to carry, because they are what
 * make it a protection rather than a form:
 *
 * **Opening an objection restricts the profile immediately** — public surfaces
 * off, no new interactors — *before* anybody reviews it. The asymmetry is
 * deliberate: the person depicted should not have to wait out a review while
 * the thing they are contesting keeps meeting people. `prior_status` is the
 * other half of that bargain and is shown beside it, because a restriction is
 * only fair if it is reversible: a dismissal puts the profile back to exactly
 * what it was, active or a departed memorial.
 *
 * **Objecting needs no account.** The route is public on purpose — somebody who
 * has just found a profile of themselves should not have to join the platform
 * depicting them in order to object to it. So the form here works with no token
 * and the status check does too, and `objector_ref` comes back so they can
 * confirm it is their case without being logged in as anybody.
 *
 * The audit panel says `vault_backed` out loud. "Tamper-evident" is a claim
 * that depends on a PDI vault being configured; where none is, the timeline is
 * still the timeline but nothing is hash-chained, and a screen that showed the
 * events without that caveat would be overstating what it has.
 */
export function Contest() {
  const { session } = useSession();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [profileId, setProfileId] = useState("");
  const [ref, setRef] = useState("");
  const [reason, setReason] = useState("");
  const [opened, setOpened] = useState<ObjectionOpened | null>(null);

  const [lookup, setLookup] = useState("");
  const [status, setStatus] = useState<ObjectionStatus | null>(null);
  const [audit, setAudit] = useState<ObjectionAudit | null>(null);

  const [queue, setQueue] = useState<HeldMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  const fail = (e: unknown) => setError((e as Error).message);

  function loadQueue() {
    if (!me || !token) return;
    api.moderationQueue(me, token).then(setQueue).catch(() => setQueue([]));
  }
  useEffect(loadQueue, [me, token]);

  async function check(id: string) {
    setError(null);
    try {
      setStatus(await api.objection(id));
    } catch (e) { fail(e); setStatus(null); }
    // Owner- or reviewer-gated, so an objector checking their own case will
    // not get this — an ordinary outcome rather than a failure worth a banner.
    try {
      setAudit(await api.objectionAudit(id, token));
    } catch { setAudit(null); }
  }

  const act = (fn: () => Promise<{ status: string; profile_status: string }>,
               said: string) => async () => {
    setError(null); setNote(null);
    try {
      const r = await fn();
      setNote(`${said} The objection is ${r.status}; the profile is ${r.profile_status}.`);
      if (lookup.trim()) check(lookup.trim());
    } catch (e) { fail(e); }
  };

  return (
    <div className="screen">
      <h2>Contesting a profile</h2>
      <p className="muted small">
        If a profile here represents you, or somebody whose estate you speak
        for, this is how you say so.
      </p>

      {error && <div className="card error">{error}</div>}
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Open an objection</h3>
        {/* Public on purpose. Said out loud, because somebody who has just
            found a profile of themselves will assume they have to sign up. */}
        <p className="muted small">
          You do not need an account. Objecting to a profile should not require
          joining the platform that is hosting it.
        </p>
        <div className="row">
          <input value={profileId} onChange={(e) => setProfileId(e.target.value)}
                 placeholder="the profile's id" style={{ flex: 1 }} />
          <input value={ref} onChange={(e) => setRef(e.target.value)}
                 placeholder="your proof reference" />
        </div>
        <div className="row">
          <input value={reason} onChange={(e) => setReason(e.target.value)}
                 placeholder="why — in your own words" style={{ flex: 1 }} />
          <button disabled={!profileId.trim() || !ref.trim()}
                  onClick={async () => {
            setError(null); setNote(null);
            try {
              const o = await api.openObjection({
                profile_id: profileId.trim(), objector_ref: ref.trim(),
                reason: reason.trim() || undefined,
              });
              setOpened(o);
              setLookup(o.id);
              check(o.id);
            } catch (e) { fail(e); }
          }}>Open it</button>
        </div>
        <p className="muted small">
          The proof reference points at an identity check held outside this
          system — it is not a login, and it is what lets you object without
          one.
        </p>
      </div>

      {opened && (
        <div className="card">
          <h3>Opened — {opened.id}</h3>
          {/* Immediate, and reversible. Both halves, together. */}
          <p className="small">{opened.note}</p>
          <p className="small">
            The profile is <strong>{opened.profile_status}</strong> from this
            moment — before anybody reviews it. It was{" "}
            <strong>{opened.prior_status}</strong>, and if the objection is
            dismissed it goes back to exactly that.
          </p>
        </div>
      )}

      <div className="card">
        <h3>Check a case</h3>
        <div className="row">
          <input value={lookup} onChange={(e) => setLookup(e.target.value)}
                 placeholder="objection id" style={{ flex: 1 }} />
          <button disabled={!lookup.trim()}
                  onClick={() => check(lookup.trim())}>Check</button>
        </div>
        {status && (
          <>
            <p className="small">
              <strong>{status.status}</strong> · profile {status.profile_id}
            </p>
            <p className="muted small">
              Your reference: {status.objector_ref} ·{" "}
              {status.reattested
                ? "the owner has re-attested their rights basis"
                : "the owner has not yet re-attested their rights basis"}
            </p>
          </>
        )}
      </div>

      {status && status.status === "open" && (
        <div className="card">
          <h3>End it now</h3>
          <p className="muted small">
            Two shortcuts skip review entirely, because a standing party's
            rights outweigh preserving the profile. Both terminate it
            immediately, even mid-review. Each applies to one rights basis
            only — if it is not the one this profile was made under, the
            refusal says which one it is.
          </p>
          <div className="row">
            <button onClick={act(() => api.withdrawConsent(status.id),
                                 "Consent withdrawn.")}>
              I am the subject — withdraw my consent
            </button>
            <button onClick={act(() => api.revokeAuthorization(status.id),
                                 "Authorization revoked.")}>
              I speak for the estate — revoke
            </button>
          </div>
        </div>
      )}

      {audit && (
        <div className="card">
          <h3>What has happened to this case</h3>
          {/* The claim depends on the vault, so the claim states the vault. */}
          <p className="muted small">
            {audit.vault_backed
              ? "Each event below is sealed into the vault, which hash-chains "
                + "every write — so this timeline is independently "
                + "tamper-evident."
              : "No vault is configured on this deployment, so these events "
                + "are recorded but not hash-chained. The timeline is the "
                + "timeline; it is not independently tamper-evident."}
          </p>
          {audit.events.map((e) => (
            <div key={e.id}>
              <p className="small">
                <strong>{e.event}</strong> by {e.actor} — {e.at}
                {e.sealed && <span className="chip"> sealed</span>}
              </p>
              {Object.keys(e.detail).length > 0 && (
                <p className="muted small">
                  {Object.entries(e.detail)
                    .map(([k, v]) => `${k}: ${String(v)}`)
                    .join(" · ")}
                </p>
              )}
            </div>
          ))}
          <h4>Adjudicate</h4>
          <p className="muted small">
            Reviewer only — an owner must not decide an objection against
            their own profile. Upholding terminates the profile and erases its
            content; dismissing restores what it was.
          </p>
          <div className="row">
            <button onClick={act(
              () => api.resolveObjection(audit.objection_id, "uphold", token),
              "Upheld.")}>Uphold</button>
            <button onClick={act(
              () => api.resolveObjection(audit.objection_id, "dismiss", token),
              "Dismissed.")}>Dismiss</button>
          </div>
        </div>
      )}

      <div className="card">
        <h3>Waiting on you</h3>
        <p className="muted small">
          What this profile said, held for your approval before anybody sees
          it. Only appears when the profile is set to manual moderation.
        </p>
        {queue.length === 0 && <p className="muted small">Nothing held.</p>}
        {queue.map((m) => (
          <div key={m.id}>
            <p className="small">{m.content}</p>
            <div className="row">
              <div style={{ flex: 1 }}>
                <span className="muted small">
                  {m.flag_reason || m.status} · {m.created_at}
                </span>
              </div>
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  await api.approveMessage(m.id, token);
                  setNote("Approved."); loadQueue();
                } catch (e) { fail(e); }
              }}>Approve</button>
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  await api.rejectMessage(m.id, token);
                  setNote("Rejected."); loadQueue();
                } catch (e) { fail(e); }
              }}>Reject</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
