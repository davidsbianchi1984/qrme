import { useEffect, useState } from "react";
import { api, type HeldMessage, type ObjectionAudit, type ObjectionOpened,
         type ObjectionStatus } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
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
export function Contest({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
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
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const fail = (e: unknown) => setError(e);

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
      setNote(tr("con.acted", lang)
        .replace("{said}", said)
        .replace("{status}", r.status)
        .replace("{profile}", r.profile_status));
      if (lookup.trim()) check(lookup.trim());
    } catch (e) { fail(e); }
  };

  return (
    <div className="screen">
      <h2>{tr("con.title", lang)}</h2>
      <p className="muted small">{tr("con.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("con.open", lang)}</h3>
        {/* Public on purpose. This sentence used to read "You do not need an
            account" — on a tab nobody without one could open, which made it
            a promise the app broke in the act of making it. The form is now
            also on the sign-in page, where the person it describes can
            actually reach it, and the copy points there instead of asserting
            something this surface cannot deliver. */}
        <p className="muted small">{tr("con.public", lang)}</p>
        <div className="row">
          <input value={profileId} onChange={(e) => setProfileId(e.target.value)}
                 placeholder={tr("con.pid.ph", lang)} style={{ flex: 1 }} />
          <input value={ref} onChange={(e) => setRef(e.target.value)}
                 placeholder={tr("con.ref.ph", lang)} />
        </div>
        <div className="row">
          <input value={reason} onChange={(e) => setReason(e.target.value)}
                 placeholder={tr("con.why.ph", lang)} style={{ flex: 1 }} />
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
          }}>{tr("con.openit", lang)}</button>
        </div>
        <p className="muted small">{tr("con.proofnote", lang)}</p>
      </div>

      {opened && (
        <div className="card">
          <h3>{fill(tr("con.opened", lang), { id: opened.id })}</h3>
          {/* Immediate, and reversible. Both halves, together. */}
          <p className="small">{opened.note}</p>
          <p className="small">
            {fill(tr("con.status", lang), {
              now: <strong>{opened.profile_status}</strong>,
              before: <strong>{opened.prior_status}</strong>,
            })}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{tr("con.check", lang)}</h3>
        <div className="row">
          <input value={lookup} onChange={(e) => setLookup(e.target.value)}
                 placeholder={tr("con.oid.ph", lang)} style={{ flex: 1 }} />
          <button disabled={!lookup.trim()}
                  onClick={() => check(lookup.trim())}>
            {tr("con.checkbtn", lang)}
          </button>
        </div>
        {status && (
          <>
            <p className="small">
              {fill(tr("con.caseline", lang), {
                status: <strong>{status.status}</strong>,
                pid: status.profile_id,
              })}
            </p>
            <p className="muted small">
              {fill(tr("con.yourref", lang), {
                ref: status.objector_ref,
                reattested: status.reattested
                  ? tr("con.reattested", lang)
                  : tr("con.notreattested", lang),
              })}
            </p>
          </>
        )}
      </div>

      {status && status.status === "open" && (
        <div className="card">
          <h3>{tr("con.endnow", lang)}</h3>
          <p className="muted small">{tr("con.shortcuts", lang)}</p>
          <div className="row">
            <button onClick={act(() => api.withdrawConsent(status.id),
                                 tr("con.consent.said", lang))}>
              {tr("con.subject", lang)}
            </button>
            <button onClick={act(() => api.revokeAuthorization(status.id),
                                 tr("con.auth.said", lang))}>
              {tr("con.estate", lang)}
            </button>
          </div>
        </div>
      )}

      {audit && (
        <div className="card">
          <h3>{tr("con.happened", lang)}</h3>
          {/* The claim depends on the vault, so the claim states the vault. */}
          <p className="muted small">
            {audit.vault_backed
              ? tr("con.sealedvault", lang) : tr("con.novault", lang)}
          </p>
          {audit.audit_events.map((e) => (
            <div key={e.id}>
              <p className="small">
                {fill(tr("con.event", lang), {
                  event: <strong>{e.event}</strong>, who: e.actor, at: e.at })}
                {e.sealed &&
                  <span className="chip"> {tr("con.sealed", lang)}</span>}
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
          <h4>{tr("con.adjudicate", lang)}</h4>
          <p className="muted small">{tr("con.reviewer", lang)}</p>
          <div className="row">
            <button onClick={act(
              () => api.resolveObjection(audit.objection_id, "uphold", token),
              tr("con.upheld.said", lang))}>{tr("con.uphold", lang)}</button>
            <button onClick={act(
              () => api.resolveObjection(audit.objection_id, "dismiss", token),
              tr("con.dismissed.said", lang))}>
              {tr("con.dismiss", lang)}
            </button>
          </div>
        </div>
      )}

      <div className="card">
        <h3>{tr("con.waiting", lang)}</h3>
        <p className="muted small">{tr("con.waiting.pitch", lang)}</p>
        {queue.length === 0 &&
          <p className="muted small">{tr("con.nothingheld", lang)}</p>}
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
                  setNote(tr("con.approved.said", lang)); loadQueue();
                } catch (e) { fail(e); }
              }}>{tr("con.approve", lang)}</button>
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  await api.rejectMessage(m.id, token);
                  setNote(tr("con.rejected.said", lang)); loadQueue();
                } catch (e) { fail(e); }
              }}>{tr("con.reject", lang)}</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
