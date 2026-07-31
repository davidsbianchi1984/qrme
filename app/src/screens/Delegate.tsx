import { useCallback, useEffect, useState } from "react";
import {
  api, type Delegation, type Grant, type TaskRunResult, type Workflow,
} from "../api";
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
export function Delegate({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
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

  if (!pid || !token) return <p>Sign in as the owner to set delegation.</p>;

  // The server's own vocabulary, not a list retyped here. `phases` is what it
  // says may be delegated at all.
  const phases = policy?.phases ?? [];
  const active: string[] = (policy?.delegation?.phases as string[]) ?? [];
  const enabled = policy?.delegation?.enabled ?? false;

  function toggle(phase: string) {
    const next = active.includes(phase)
      ? active.filter((p) => p !== phase)
      : [...active, phase];
    if (next.length === 0) {
      setError("A policy needs at least one phase. Turn delegation off "
        + "instead if the profile should do nothing unattended.");
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
    }, token!), `Delegating: ${next.join(", ")}.`);
  }

  return (
    <section className="screen">
      <h2>Delegation &amp; work</h2>
      <Refusal error={error} onPlans={onPlans} variant="inline" />
      {said && <p className="muted">{said}</p>}

      <h3>The grant it reads through</h3>
      <p className="muted">
        A grant is a revocable scope. It is what a phase reads the profile's
        own material through, and it can be withdrawn mid-run — the work stops
        seeing what the grant covered from that moment, not at the end.
      </p>
      {grant
        ? (
          <div className="card">
            <div className="row">
              <strong>{grant.id}</strong>
              <span className="muted">{grant.scope.join(", ") || "no scope"}</span>
              {grant.revoked && <span className="pill">revoked</span>}
            </div>
            <button disabled={busy || grant.revoked}
              onClick={() => run(async () => {
                await api.revokeGrant(grant.id, token);
                setGrant({ ...grant, revoked: true });
              }, "Revoked. Anything running stops reading through it now.")}>
              Revoke
            </button>
          </div>
        )
        : (
          <button disabled={busy}
            onClick={() => run(async () => {
              setGrant(await api.createGrant(pid, ["sources"], token));
            }, "Grant minted.")}>
            Mint a grant over my sources
          </button>
        )}

      <h3>What it may do unattended</h3>
      <p className="muted">
        {enabled
          ? "On. Anything not ticked still stops and waits for you."
          : "Off. Every phase stops and waits for you."}
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
          }, token), enabled ? "Delegation off." : "Delegation on.")}>
          Turn delegation {enabled ? "off" : "on"}
        </button>
      )}

      <h3>Runs</h3>
      <div className="row">
        <input value={goal} placeholder="What should it work on?"
          onChange={(e) => setGoal(e.target.value)} />
        <button disabled={busy || !goal.trim()}
          onClick={() => run(async () => {
            await api.createWorkflow(pid, {
              goal: goal.trim(), grant_token: grant?.token }, token);
            setGoal("");
          }, "Started.")}>
          Start
        </button>
      </div>
      {runs.length === 0 && <p className="muted">Nothing has been run yet.</p>}
      {runs.map((w) => (
        <div key={w.id} className="card">
          <div className="row">
            <strong>{w.goal}</strong>
            <span className="muted">{w.status}</span>
            {w.next_phase && <span className="pill">next: {w.next_phase}</span>}
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
                <span>Waiting on you: <strong>{w.awaiting}</strong></span>
                <input
                  value={reply[w.id] ?? ""}
                  placeholder="Your answer"
                  onChange={(e) =>
                    setReply({ ...reply, [w.id]: e.target.value })} />
                <button disabled={busy || !(reply[w.id] ?? "").trim()}
                  onClick={() => run(async () => {
                    await api.resumeWorkflow(pid, w.id,
                      (reply[w.id] ?? "").trim(), token);
                    setReply({ ...reply, [w.id]: "" });
                  }, "Resumed.")}>
                  Answer &amp; continue
                </button>
              </div>
            )
            : w.status !== "done" && w.status !== "cancelled" && (
              <button disabled={busy}
                onClick={() => run(() =>
                  api.advanceWorkflow(pid, w.id, token))}>
                Advance
              </button>
            )}
          {w.status !== "done" && w.status !== "cancelled" && (
            <button disabled={busy}
              onClick={() => {
                if (confirm("Cancel this run? What it has already done stays."))
                  run(() => api.cancelWorkflow(pid, w.id, token), "Cancelled.");
              }}>
              Cancel
            </button>
          )}
        </div>
      ))}

      <h3>One-off tasks</h3>
      <p className="muted">
        A single piece of work rather than a run with phases. It needs a grant,
        because it composes from the profile's own sources.
      </p>
      <div className="row">
        <input value={topic} placeholder="Topic"
          onChange={(e) => setTopic(e.target.value)} />
        <button disabled={busy || !topic.trim() || !grant || grant.revoked}
          onClick={() => run(async () => {
            await api.runTask(pid, {
              topic: topic.trim(), grant_token: grant!.token }, token);
            setTopic("");
          }, "Done.")}>
          Compose from my sources
        </button>
      </div>
      {!grant && <p className="muted">Mint a grant first.</p>}
      {tasks.map((t) => (
        <div key={t.id} className="card">
          <div className="row">
            <span className="muted">{t.status}</span>
          </div>
          {t.output && <p>{t.output}</p>}
        </div>
      ))}
    </section>
  );
}
