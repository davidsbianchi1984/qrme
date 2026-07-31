import { useEffect, useState } from "react";
import { api, type SkillGrant, type SkillGrantUse,
         type SkillGrantVocabulary } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Lending a skill inside a place two people already share.
 *
 * Eight routes with no caller. The asymmetry is the feature and this screen is
 * built around it: **two people to open a grant, either one alone to close
 * it.** Requiring both to close would mean somebody who has changed their mind
 * needs the agreement of the person benefiting from it — which is exactly when
 * withdrawal has to work. So the close button is never disabled by whose grant
 * it is.
 *
 * The use log is shown to both sides, not just the lender. A borrower is
 * entitled to see what is being written down about them, and a log only one
 * party can read is surveillance with extra steps.
 *
 * `where` and `means` come back from the server as plain English for the
 * `surface` and `skill_kind` keys, so the screen shows those rather than
 * inventing labels that could drift from the vocabulary.
 */
export function Grants({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const me = session.interactorId || "";
  const token = session.interactorToken || "";

  const [vocab, setVocab] = useState<SkillGrantVocabulary | null>(null);
  const [grant, setGrant] = useState<SkillGrant | null>(null);
  const [uses, setUses] = useState<SkillGrantUse[]>([]);
  const [lookup, setLookup] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);

  const [borrower, setBorrower] = useState("");
  const [surface, setSurface] = useState("room");
  const [surfaceId, setSurfaceId] = useState("");
  const [kind, setKind] = useState("profession");
  const [ref, setRef] = useState("");
  const [title, setTitle] = useState("");
  const [what, setWhat] = useState("");
  const [reason, setReason] = useState("");

  const fail = (e: unknown) => setError(e);

  useEffect(() => {
    api.skillGrantVocabulary().then((v) => {
      setVocab(v);
      setSurface(v.surfaces[0]?.key || "room");
      setKind(v.skill_kinds[0]?.key || "pack");
    }).catch(fail);
  }, []);

  function landed(g: SkillGrant, said?: string) {
    setGrant(g);
    setUses(g.recent_uses);
    setError(null);
    if (said) setNote(said);
  }

  const act = (fn: () => Promise<SkillGrant>, said?: string) => async () => {
    setError(null); setNote(null);
    try { landed(await fn(), said); } catch (e) { fail(e); }
  };

  async function offer() {
    setError(null); setNote(null);
    try {
      landed(await api.offerSkill({
        lender_id: me, borrower_id: borrower.trim(), surface,
        surface_id: surfaceId.trim(), skill_kind: kind,
        skill_ref: ref.trim(), title: title.trim(),
      }, token), "Offered. Nothing is usable until they accept.");
    } catch (e) { fail(e); }
  }

  // The receipt, not the grant — so the reply says what was used and repeats
  // that nothing was installed. Refresh the grant afterwards for the count.
  async function use() {
    if (!grant) return;
    setError(null); setNote(null);
    try {
      const r = await api.useSkill(grant.id, me, what.trim(), token);
      setNote(`${r.title} — ${r.note}`);
      setWhat("");
      landed(await api.skillGrant(grant.id, token));
    } catch (e) { fail(e); }
  }

  const iAmLender = grant ? grant.lender_id === me : false;

  return (
    <div className="screen">
      <h2>Lent skills</h2>
      <p className="muted small">
        Something you can do, made usable by somebody else, in one place, for as
        long as you both want it there.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {vocab && (
        <div className="card">
          <h3>The terms</h3>
          {/* The backend's own four sentences. */}
          <ul className="small">{vocab.terms.map((t) => <li key={t}>{t}</li>)}</ul>
        </div>
      )}

      <div className="card">
        <h3>Lend something</h3>
        <div className="row">
          <input value={borrower} onChange={(e) => setBorrower(e.target.value)}
                 placeholder="who may use it" />
          <select value={surface} onChange={(e) => setSurface(e.target.value)}>
            {vocab?.surfaces.map((s) => (
              <option key={s.key} value={s.key}>{s.key}</option>
            ))}
          </select>
          <input value={surfaceId} onChange={(e) => setSurfaceId(e.target.value)}
                 placeholder="which one" />
        </div>
        {/* There is deliberately no "everywhere" surface: a grant with no
            place is a permission nobody can see the edges of. */}
        <p className="muted small">
          {vocab?.surfaces.find((s) => s.key === surface)?.means}
        </p>
        <div className="row">
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            {vocab?.skill_kinds.map((k) => (
              <option key={k.key} value={k.key}>{k.key}</option>
            ))}
          </select>
          <input value={ref} onChange={(e) => setRef(e.target.value)}
                 placeholder="which skill" style={{ flex: 1 }} />
        </div>
        <p className="muted small">
          {vocab?.skill_kinds.find((k) => k.key === kind)?.means}
        </p>
        <div className="row">
          <input value={title} onChange={(e) => setTitle(e.target.value)}
                 placeholder="what to call it" style={{ flex: 1 }} />
          <button disabled={!me || !token || !borrower.trim() || !surfaceId.trim()
                            || !ref.trim() || !title.trim()}
                  onClick={offer}>Offer</button>
        </div>
      </div>

      <div className="card">
        <h3>Open one</h3>
        <div className="row">
          <input value={lookup} onChange={(e) => setLookup(e.target.value)}
                 placeholder="grant id" style={{ flex: 1 }} />
          <button disabled={!lookup.trim() || !token} onClick={async () => {
            setError(null); setNote(null);
            try {
              const g = await api.skillGrant(lookup.trim(), token);
              landed(g);
              const log = await api.skillGrantUses(g.id, token);
              setUses(log.uses);
            } catch (e) { fail(e); }
          }}>Open</button>
        </div>
      </div>

      {grant && (
        <>
          <div className="card">
            <h3>{grant.title}</h3>
            <p className="muted small">
              {grant.means} — {grant.skill_ref}
            </p>
            <p className="muted small">
              In {grant.where} ({grant.surface_id}) · {grant.state} · used{" "}
              {grant.used_count} time{grant.used_count === 1 ? "" : "s"}
            </p>
            <p className="small">
              {iAmLender ? "You are lending this." : "You are borrowing this."}
            </p>
            {/* Both of these are the server's own claims about itself. */}
            <p className="muted small">
              {grant.transfers_anything
                ? "Something is transferred by this grant."
                : "Nothing is transferred — the skill is used, never copied."}
              {grant.either_can_end_it && " Either of you can end it, alone."}
            </p>
            {grant.close_reason && (
              <p className="muted small">
                Closed by {grant.closed_by === me ? "you" : grant.closed_by}:{" "}
                {grant.close_reason}
              </p>
            )}
          </div>

          <div className="card">
            <h3>Act on it</h3>
            <div className="row">
              <button disabled={grant.state !== "offered"}
                      onClick={act(() => api.acceptSkillGrant(grant.id, me, token),
                                   "Accepted. Now it is usable.")}>Accept</button>
              <button disabled={grant.state !== "offered"}
                      onClick={act(() => api.declineSkillGrant(grant.id, me, token),
                                   "Declined.")}>Decline</button>
            </div>
            <div className="row">
              <input value={reason} onChange={(e) => setReason(e.target.value)}
                     placeholder="why (optional)" style={{ flex: 1 }} />
              {/* Never disabled by side. Whoever wants out, gets out. */}
              <button disabled={grant.state === "closed"}
                      onClick={act(
                        () => api.closeSkillGrant(grant.id, me, reason, token),
                        "Closed. The next use is refused, not just the next grant.")}>
                End it
              </button>
            </div>
          </div>

          {!iAmLender && (
            <div className="card">
              <h3>Use it</h3>
              <div className="row">
                <input value={what} onChange={(e) => setWhat(e.target.value)}
                       placeholder="what for" style={{ flex: 1 }} />
                <button disabled={!grant.active || !what.trim()} onClick={use}>
                  Use
                </button>
              </div>
              <p className="muted small">
                Every use is written down and the lender can see it. So can you —
                that is the list below.
              </p>
            </div>
          )}

          <div className="card">
            <h3>Every use</h3>
            {uses.length === 0 && <p className="muted small">Not used yet.</p>}
            {uses.map((u, i) => (
              <p key={`${u.used_at}-${i}`} className="small">
                {u.what || "(unlabelled)"} — {u.used_at}
                {u.borrower_id !== me && <> · by {u.borrower_id}</>}
              </p>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
