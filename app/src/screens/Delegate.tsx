import { useCallback, useEffect, useState } from "react";
import {
  api, type Delegation, type Grant, type TaskRunResult, type Workflow,
} from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// What the profile may do on the owner's behalf, and what it has done.
//
// The whole chain existed in the backend with no caller anywhere: mint a
// revocable grant, authorise which phases may run unattended, start a
// workflow, advance it, answer it when it stops, cancel it. A profile that
// can act for you and no way to say how far is the wrong half of the feature
// to ship, and it is the half that shipped.
//
// The order of the screen is the order of the decision. Grants come first
// because a phase reads through one; the policy second because it is a choice
// about scope, not about work; the runs last, because they are what the first
// two make possible.
//
// Then the other side of the same policy. Everything above is the owner's
// half — what my profile may do for me. Delegation exists for the person on
// the *other* end of a conversation: somebody already talking to a profile
// hands it a job, inside the limits its owner set. That half had four
// bindings and no screen, so an owner could publish a policy and nobody
// could take it up from here.
//
// Two refusals worth keeping visible, because both are the feature working:
// starting one needs an existing conversation — delegated work is not for a
// stranger holding a profile id — and a phase that would read every source
// item on the profile is refused unless the owner scoped a grant for it.
export function Delegate({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const pid = session.profileId;
  const token = session.ownerToken;

  const [policy, setPolicy] = useState<Delegation | null>(null);
  const [grant, setGrant] = useState<Grant | null>(null);
  const [runs, setRuns] = useState<Workflow[]>([]);
  const [tasks, setTasks] = useState<TaskRunResult[]>([]);
  const [goal, setGoal] = useState("");
  const [reply, setReply] = useState<Record<string, string>>({});
  const [topic, setTopic] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [said, setSaid] = useState<string | null>(null);

  // The delegate's half. `interactorToken` rather than `ownerToken`: here
  // you are the person asking somebody else's profile to do something.
  const me = session.interactorId || "";
  const mine = session.interactorToken || "";
  const [theirs, setTheirs] = useState("");
  const [offer, setOffer] = useState<Delegation | null>(null);
  const [handedGoal, setHandedGoal] = useState("");
  const [handed, setHanded] = useState<Workflow | null>(null);
  const [answer, setAnswer] = useState("");

  const load = useCallback(() => {
    if (!pid || !token) return;
    api.delegation(pid).then(setPolicy).catch(() => setPolicy(null));
    api.workflows(pid, token).then(setRuns).catch(() => setRuns([]));
    api.tasks(pid, token).then(setTasks).catch(() => setTasks([]));
  }, [pid, token]);
  useEffect(load, [load]);

  async function run(action: () => Promise<unknown>, ok?: string) {
    setBusy(true); setError(null); setSaid(null);
    try { await action(); if (ok) setSaid(ok); load(); }
    catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  if (!pid || !token) return <p>{tr("dlg.signin", lang)}</p>;

  // The server's own vocabulary, not a list retyped here. `delegable` is what
  // it says may be delegated at all; `phases` is what this owner has chosen
  // from it; `delegation` is the on/off itself, a boolean beside them rather
  // than an object around them. Reading the chosen list as the vocabulary
  // left nothing to draw whenever delegation was off — so it could not be
  // turned on — and reading `.enabled` off a boolean was `undefined`, so it
  // read as off even when it was on.
  const phases = policy?.delegable ?? [];
  const active: string[] = policy?.phases ?? [];
  const enabled = policy?.delegation ?? false;

  function toggle(phase: string) {
    const next = active.includes(phase)
      ? active.filter((p) => p !== phase)
      : [...active, phase];
    if (next.length === 0) {
      setError(tr("dlg.needone", lang));
      return;
    }
    run(() => api.setDelegation(pid!, {
      phases: next,
      // `research` reads every source item on the profile, so the backend
      // refuses to delegate it without a grant. Sending the one we hold means
      // the refusal is only ever met by someone who has not minted one — and
      // the message says so plainly rather than being pre-empted here.
      grant_token: grant?.token,
      enabled: true,
    }, token!), tr("dlg.delegating.said", lang)
      .replace("{what}", next.join(", ")));
  }

  return (
    <section className="screen">
      <h2>{tr("dlg.title", lang)}</h2>
      <Refusal error={error} onPlans={onPlans} variant="inline" />
      {said && <p className="muted">{said}</p>}

      <h3>{tr("dlg.grant", lang)}</h3>
      <p className="muted">{tr("dlg.grant.pitch", lang)}</p>
      {grant
        ? (
          <div className="card">
            <div className="row">
              <strong>{grant.id}</strong>
              <span className="muted">
                {grant.scope.join(", ") || tr("dlg.noscope", lang)}
              </span>
              {grant.revoked &&
                <span className="pill">{tr("dlg.revoked", lang)}</span>}
            </div>
            <button disabled={busy || grant.revoked}
              onClick={() => run(async () => {
                await api.revokeGrant(grant.id, token);
                setGrant({ ...grant, revoked: true });
              }, tr("dlg.revoked.said", lang))}>
              {tr("dlg.revoke", lang)}
            </button>
          </div>
        )
        : (
          <button disabled={busy}
            onClick={() => run(async () => {
              setGrant(await api.createGrant(pid, ["sources"], token));
            }, tr("dlg.minted.said", lang))}>
            {tr("dlg.mint", lang)}
          </button>
        )}

      <h3>{tr("dlg.unattended", lang)}</h3>
      <p className="muted">
        {enabled ? tr("dlg.on", lang) : tr("dlg.off", lang)}
      </p>
      <div className="row">
        {phases.map((p) => (
          <button key={p}
            disabled={busy}
            className={active.includes(p) ? "on" : ""}
            onClick={() => toggle(p)}>
            {active.includes(p) ? "✓ " : ""}{p}
          </button>
        ))}
      </div>
      {active.length > 0 && (
        <button disabled={busy}
          onClick={() => run(() => api.setDelegation(pid, {
            phases: active, grant_token: grant?.token, enabled: !enabled,
          }, token), enabled
            ? tr("dlg.off.said", lang) : tr("dlg.on.said", lang))}>
          {enabled ? tr("dlg.turn.off", lang) : tr("dlg.turn.on", lang)}
        </button>
      )}

      <h3>{tr("dlg.runs", lang)}</h3>
      <div className="row">
        <input value={goal} placeholder={tr("dlg.goal.ph", lang)}
          onChange={(e) => setGoal(e.target.value)} />
        <button disabled={busy || !goal.trim()}
          onClick={() => run(async () => {
            await api.createWorkflow(pid, {
              goal: goal.trim(), grant_token: grant?.token }, token);
            setGoal("");
          }, tr("dlg.started.said", lang))}>
          {tr("dlg.start", lang)}
        </button>
      </div>
      {runs.length === 0 &&
        <p className="muted">{tr("dlg.norun", lang)}</p>}
      {runs.map((w) => (
        <div key={w.id} className="card">
          <div className="row">
            <strong>{w.goal}</strong>
            <span className="muted">{w.status}</span>
            {w.next_phase && <span className="pill">
              {fill(tr("dlg.next", lang), { phase: w.next_phase })}</span>}
          </div>
          {w.plan?.length > 0 && (
            <p className="muted">
              {w.plan.map((step, i) => (
                <span key={i}>
                  {i === w.cursor ? <strong>{step}</strong> : step}
                  {i < w.plan.length - 1 ? " → " : ""}
                </span>
              ))}
            </p>
          )}
          {/* `awaiting` is the whole point of the pause: the run stopped
              because it needs a person, and it says what for. */}
          {w.awaiting
            ? (
              <div className="row">
                <span>{fill(tr("dlg.waiting", lang),
                  { what: <strong>{w.awaiting}</strong> })}</span>
                <input
                  value={reply[w.id] ?? ""}
                  placeholder={tr("dlg.answer.ph", lang)}
                  onChange={(e) =>
                    setReply({ ...reply, [w.id]: e.target.value })} />
                <button disabled={busy || !(reply[w.id] ?? "").trim()}
                  onClick={() => run(async () => {
                    await api.resumeWorkflow(pid, w.id,
                      (reply[w.id] ?? "").trim(), token);
                    setReply({ ...reply, [w.id]: "" });
                  }, tr("dlg.resumed.said", lang))}>
                  {tr("dlg.answer", lang)}
                </button>
              </div>
            )
            : w.status !== "done" && w.status !== "cancelled" && (
              <button disabled={busy}
                onClick={() => run(() =>
                  api.advanceWorkflow(pid, w.id, token))}>
                {tr("dlg.advance", lang)}
              </button>
            )}
          {w.status !== "done" && w.status !== "cancelled" && (
            <button disabled={busy}
              onClick={() => {
                if (confirm(tr("dlg.cancel.confirm", lang)))
                  run(() => api.cancelWorkflow(pid, w.id, token),
                      tr("dlg.cancelled.said", lang));
              }}>
              {tr("dlg.cancel", lang)}
            </button>
          )}
        </div>
      ))}

      <h3>{tr("dlg.oneoff", lang)}</h3>
      <p className="muted">{tr("dlg.oneoff.pitch", lang)}</p>
      <div className="row">
        <input value={topic} placeholder={tr("dlg.topic.ph", lang)}
          onChange={(e) => setTopic(e.target.value)} />
        <button disabled={busy || !topic.trim() || !grant || grant.revoked}
          onClick={() => run(async () => {
            await api.runTask(pid, {
              topic: topic.trim(), grant_token: grant!.token }, token);
            setTopic("");
          }, tr("dlg.done.said", lang))}>
          {tr("dlg.compose", lang)}
        </button>
      </div>
      {!grant && <p className="muted">{tr("dlg.mintfirst", lang)}</p>}
      {tasks.map((t) => (
        <div key={t.id} className="card">
          <div className="row">
            <span className="muted">{t.status}</span>
          </div>
          {t.output && <p>{t.output}</p>}
        </div>
      ))}

      <h3>{tr("dlg.handed", lang)}</h3>
      <p className="muted small">{tr("dlg.handed.pitch", lang)}</p>
      <div className="card">
        <div className="row">
          <input value={theirs} onChange={(e) => setTheirs(e.target.value)}
                 placeholder={tr("dlg.theirs.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !theirs.trim()}
                  onClick={() => {
                    setError(null);
                    api.delegation(theirs.trim()).then(setOffer)
                      .catch((e) => { setOffer(null); setError(e); });
                  }}>
            {tr("dlg.whatwill", lang)}
          </button>
        </div>
        {offer && (
          <p className="small">
            {offer.delegation
              ? tr("dlg.accepts", lang)
                  .replace("{phases}", offer.phases.join(", "))
              : tr("dlg.accepts.not", lang)}
            {" "}
            <span className="muted small">
              {/* The offer deliberately omits the grant id — which source
                  items the owner scoped is the owner's business, and the
                  caller only needs the shape of the request that will be
                  accepted. */}
              {tr("dlg.noscope.shown", lang)}
            </span>
          </p>
        )}
        <div className="row">
          <input value={handedGoal}
                 onChange={(e) => setHandedGoal(e.target.value)}
                 placeholder={tr("dlg.want.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !mine || !theirs.trim()
                            || !handedGoal.trim()}
                  onClick={async () => {
                    setError(null); setSaid(null); setBusy(true);
                    try {
                      setHanded(await api.startDelegatedWorkflow(
                        theirs.trim(),
                        { interactor_id: me, goal: handedGoal.trim() },
                        mine));
                      setHandedGoal("");
                    } catch (e) { setError(e); } finally { setBusy(false); }
                  }}>
            {tr("dlg.handover", lang)}
          </button>
        </div>
        <p className="muted small">{tr("dlg.talking", lang)}</p>
        {handed && (
          <>
            <p className="small">
              {fill(tr("dlg.handed.line", lang), {
                id: <code>{handed.id}</code>, status: handed.status })}
              {handed.next_phase && tr("dlg.handed.next", lang)
                .replace("{phase}", handed.next_phase)}
              {handed.awaiting && tr("dlg.handed.waiting", lang)
                .replace("{what}", handed.awaiting)}
            </p>
            <div className="row">
              <button disabled={busy}
                      onClick={async () => {
                        setError(null); setBusy(true);
                        try {
                          setHanded(await api.advanceDelegatedWorkflow(
                            theirs.trim(), handed.id, mine));
                        } catch (e) { setError(e); }
                        finally { setBusy(false); }
                      }}>
                {tr("dlg.nextphase", lang)}
              </button>
              <button disabled={busy}
                      onClick={async () => {
                        setError(null); setBusy(true);
                        try {
                          setHanded(await api.delegatedWorkflow(
                            theirs.trim(), handed.id, mine));
                        } catch (e) { setError(e); }
                        finally { setBusy(false); }
                      }}>
                {tr("dlg.refresh", lang)}
              </button>
            </div>
            <div className="row">
              <input value={answer}
                     onChange={(e) => setAnswer(e.target.value)}
                     placeholder={tr("dlg.answerit.ph", lang)}
                     style={{ flex: 1 }} />
              <button disabled={busy || !answer.trim()}
                      onClick={async () => {
                        setError(null); setBusy(true);
                        try {
                          setHanded(await api.resumeDelegatedWorkflow(
                            theirs.trim(), handed.id, answer.trim(), mine));
                          setAnswer("");
                        } catch (e) { setError(e); }
                        finally { setBusy(false); }
                      }}>
                {tr("dlg.answercont", lang)}
              </button>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
