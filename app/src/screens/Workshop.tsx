import { useEffect, useState } from "react";
import { api, type Embodiment, type EmbodimentConsistency,
         type ExperienceEntry, type FinetuneRun, type Perception,
         type ProfileSteering, type SourceItem,
         type Specialist } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * What a profile is made of, and how the owner shapes it.
 *
 * Source material, the dials, a CV, the specialists it hands work to, the
 * bodies it speaks through, and the local fine-tune that folds all of it back
 * in. Twelve routes and not one caller in the console — the profile could be
 * created and talked to, and everything that made it *this* profile rather
 * than a default one was unreachable.
 *
 * Two of these writes were silently permissive, and it is the same shape
 * twice: a Pydantic model with a default, so an unknown key is accepted,
 * discarded, and answered `200`.
 *
 * - `PUT .../steering` takes `values`. `dials` is the obvious guess, because
 *   that is what the *read* calls its catalogue;
 * - `PUT .../experience` takes `period`. `years` is the obvious guess,
 *   because that is what anybody writing a CV form reaches for.
 *
 * Neither produced an error. The row saved with no dates, the dials did not
 * move, and both requests looked like successes. Both models are strict now,
 * so the next wrong guess gets a 422 naming the field — but the tests that
 * catch a regression write and read back, because that is the only thing that
 * would have caught it in the first place.
 *
 * Three things rendered rather than summarised:
 *
 * - a source's `content` is shown when it is there, because *there* means
 *   sitting in the platform's database in the clear. A tick saying "stored"
 *   would hide which half of the custody argument this account is on;
 * - the fine-tune answer is mostly claims about what did *not* happen — no
 *   external transmission, computed on this host — and those are the reason
 *   the feature is what it is;
 * - the identity signature and its guarantee, which is the one thing on this
 *   screen a stranger can verify without an account.
 */
export function Workshop({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [steering, setSteering] = useState<ProfileSteering | null>(null);
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [experience, setExperience] = useState<ExperienceEntry[]>([]);
  const [bodies, setBodies] = useState<Embodiment[]>([]);
  const [same, setSame] = useState<EmbodimentConsistency | null>(null);
  const [run, setRun] = useState<FinetuneRun | null>(null);
  const [seen, setSeen] = useState<Perception | null>(null);

  const [srcKind, setSrcKind] = useState("writing");
  const [srcTitle, setSrcTitle] = useState("");
  const [srcBody, setSrcBody] = useState("");

  const [domain, setDomain] = useState("");
  const [specialistId, setSpecialistId] = useState("");

  const [expTitle, setExpTitle] = useState("");
  const [expOrg, setExpOrg] = useState("");
  const [expPeriod, setExpPeriod] = useState("");

  const [bodyName, setBodyName] = useState("");
  const [bodyKind, setBodyKind] = useState("speaker");
  const [bodyLlm, setBodyLlm] = useState(false);

  const [scene, setScene] = useState("");
  const [goal, setGoal] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fail = (e: unknown) => setError(e);

  function load() {
    if (!me) return;
    // Public, and the only thing here that does not need the owner token.
    api.embodimentConsistency(me).then(setSame).catch(() => setSame(null));
    if (!token) return;
    api.profileSteering(me, token).then(setSteering).catch(fail);
    api.sources(me, token).then(setSources).catch(() => setSources([]));
    api.specialists(me, token).then(setSpecialists).catch(() => setSpecialists([]));
    api.embodiments(me, token).then(setBodies).catch(() => setBodies([]));
  }
  useEffect(load, [me, token]);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { fail(e); } finally { setBusy(false); }
  };

  async function steer(dial: string, value: number) {
    setError(null);
    try {
      const r = await api.setProfileSteering(me, { [dial]: value }, token);
      setSteering((s) => s && { ...s, values: r.values });
    } catch (e) { fail(e); }
  }

  return (
    <div className="screen">
      <h2>What it is made of</h2>
      <p className="muted small">
        The material a profile is built from, the manner it comes across in,
        and everything it can hand on to somebody who knows more.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {same && (
        <div className="card">
          <h3>The same personality, wherever it is met</h3>
          <p className="small">{same.guarantee}</p>
          <p className="muted small">
            Signature <code>{same.signature}</code> · invariant across{" "}
            {same.invariant_across}.
          </p>
          {/* Said because it is unusual and load-bearing: this one route
              needs no account, so somebody who has just met the profile on
              a speaker can check it against the one they met in a room. */}
          <p className="muted small">
            This check is public — anybody who meets {same.name} in any form
            can read it without an account.
          </p>
          {same.surfaces.length > 0 && (
            <p className="muted small">
              Also present on: {same.surfaces.join(", ")}.
            </p>
          )}
        </div>
      )}

      {steering && (
        <div className="card">
          <h3>How it comes across</h3>
          <p className="muted small">
            Manner, not permissions. Steering never touches identity,
            boundaries, age-gating, or what the profile may be asked to do.
          </p>
          {!steering.adult_mode && (
            /* Named rather than left as an absence: a dial that is missing
               because of what this profile is reads as a bug otherwise. */
            <p className="muted small">
              This is not an adult-mode profile, so the intimacy dial does
              not exist here at all.
            </p>
          )}
          {steering.dials.map((d) => (
            <div key={d.name}>
              <label className="small">
                {d.label} — {steering.values[d.name] ?? d.default}
                {d.adult_only && " · 18+"}
              </label>
              <input type="range" min={d.min} max={d.max}
                     value={steering.values[d.name] ?? d.default}
                     onChange={(e) => steer(d.name, Number(e.target.value))} />
              <div className="muted small">{d.low} → {d.high}</div>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h3>What it knows</h3>
        <p className="muted small">
          Source material: the writing, conversations and life events the
          persona is built on.
        </p>
        <div className="row">
          <select value={srcKind} onChange={(e) => setSrcKind(e.target.value)}>
            {["writing", "conversation", "social_post", "photo", "voice_note",
              "life_event", "knowledge", "linked_account"].map((k) => (
              <option key={k} value={k}>{k.replace(/_/g, " ")}</option>
            ))}
          </select>
          <input value={srcTitle} onChange={(e) => setSrcTitle(e.target.value)}
                 placeholder="what it is" style={{ flex: 1 }} />
        </div>
        <textarea value={srcBody} onChange={(e) => setSrcBody(e.target.value)}
                  placeholder="the material itself" rows={3} />
        <button disabled={busy || !token || !srcBody.trim()}
                onClick={act(async () => {
                  await api.addSource(me, {
                    kind: srcKind, title: srcTitle.trim() || undefined,
                    content: srcBody.trim() }, token);
                  // Cleared, like the CV form below. A form that keeps its
                  // contents after a successful submit is one people press
                  // twice.
                  setSrcTitle(""); setSrcBody("");
                }, "Added.")}>Add it</button>
        {sources.length === 0 && (
          <p className="muted small">Nothing added yet.</p>
        )}
        {sources.map((s) => (
          <div key={s.id}>
            <p className="small">
              <strong>{s.title || s.kind.replace(/_/g, " ")}</strong>{" "}
              <span className="muted">· {s.kind.replace(/_/g, " ")}</span>
            </p>
            {/* Content present means content readable — by this platform,
                by whoever operates it, and by a lawful request. The screen
                shows the material rather than a tick, because the tick
                would hide which side of the custody line this account is
                on. */}
            {s.pdi_key ? (
              <p className="muted small">
                Sealed in the vault. Only the reference is held here.
              </p>
            ) : (
              <>
                <p className="muted small">{s.content}</p>
                <p className="muted small">
                  Stored in the clear on this deployment — that is what you
                  are looking at.
                </p>
              </>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Who it hands work to</h3>
        <p className="muted small">
          A domain, and the profile that knows more about it. A question in
          that domain goes there instead of being guessed at here.
        </p>
        <div className="row">
          <input value={domain} onChange={(e) => setDomain(e.target.value)}
                 placeholder="a domain, e.g. plumbing" style={{ flex: 1 }} />
          <input value={specialistId}
                 onChange={(e) => setSpecialistId(e.target.value)}
                 placeholder="the specialist's profile id" style={{ flex: 1 }} />
          {/* One pair per call, despite the plural route. */}
          <button disabled={busy || !token || !domain.trim() || !specialistId.trim()}
                  onClick={act(async () => {
                    await api.attachSpecialist(
                      me, domain.trim(), specialistId.trim(), token);
                    setDomain(""); setSpecialistId("");
                  }, "Attached.")}>Attach</button>
        </div>
        {specialists.length === 0 && (
          <p className="muted small">Nothing handed on.</p>
        )}
        {specialists.map((s) => (
          <p className="small" key={s.domain}>
            <strong>{s.domain}</strong>{" "}
            {/* The route answers with an id and no name; the join would be
                a second request per row, so the id is shown as an id
                rather than dressed up as something it is not. */}
            <code className="muted">{s.specialist_profile_id}</code>
          </p>
        ))}
      </div>

      <div className="card">
        <h3>What it has done</h3>
        <p className="muted small">
          Replaced whole rather than edited row by row — a history is a
          statement, not a set of fields.
        </p>
        <div className="row">
          <input value={expTitle} onChange={(e) => setExpTitle(e.target.value)}
                 placeholder="title" style={{ flex: 1 }} />
          <input value={expOrg} onChange={(e) => setExpOrg(e.target.value)}
                 placeholder="where" style={{ flex: 1 }} />
          {/* `period`, and the placeholder says so — `years` is the natural
              word and it is not the field. */}
          <input value={expPeriod}
                 onChange={(e) => setExpPeriod(e.target.value)}
                 placeholder="period, e.g. 2011–2019" style={{ flex: 1 }} />
        </div>
        <button disabled={busy || !token || !expTitle.trim()}
                onClick={act(async () => {
                  const next = [...experience, {
                    title: expTitle.trim(),
                    org: expOrg.trim() || null,
                    period: expPeriod.trim() || null }];
                  const r = await api.setExperience(me, next, token);
                  setExperience(r.experience);
                  setExpTitle(""); setExpOrg(""); setExpPeriod("");
                }, "Saved.")}>Add a line</button>
        {experience.map((e, i) => (
          <p className="small" key={e.id || i}>
            <strong>{e.title}</strong>
            {e.org && <> — {e.org}</>}
            {e.period && <span className="muted"> · {e.period}</span>}
          </p>
        ))}
      </div>

      <div className="card">
        <h3>What it speaks through</h3>
        <p className="muted small">
          A speaker, an earpiece, a hologram, a robot. The distinction that
          matters is whether the form can hold a conversation or only relay
          one.
        </p>
        <div className="row">
          <input value={bodyName} onChange={(e) => setBodyName(e.target.value)}
                 placeholder="what you call it" style={{ flex: 1 }} />
          <select value={bodyKind} onChange={(e) => setBodyKind(e.target.value)}>
            {/* The server's enum, exactly. Three of the words that came
                naturally here — screen, wearable, vehicle — are not in it,
                and each would have 422'd on submit while looking like a
                perfectly ordinary option in the list. */}
            {["speaker", "earpiece", "hologram", "robot", "humanoid",
              "other"].map((k) => <option key={k} value={k}>{k}</option>)}
          </select>
          <label className="small">
            <input type="checkbox" checked={bodyLlm}
                   onChange={(e) => setBodyLlm(e.target.checked)} />
            {" "}can hold a conversation
          </label>
          <button disabled={busy || !token || !bodyName.trim()}
                  onClick={act(async () => {
                    await api.addEmbodiment(me, {
                      name: bodyName.trim(), kind: bodyKind,
                      has_llm: bodyLlm }, token);
                    setBodyName("");
                  }, "Added.")}>Add</button>
        </div>
        {bodies.map((b) => (
          <p className="small" key={b.name}>
            <strong>{b.name}</strong> — {b.kind}
            <span className="muted">
              {b.has_llm ? " · answers for itself" : " · relays only"}
            </span>
          </p>
        ))}
      </div>

      <div className="card">
        <h3>Fold it back in</h3>
        <p className="muted small">
          Recompute the profile's own model from the history it already has.
          No body to send, and nothing to configure.
        </p>
        <button disabled={busy || !token}
                onClick={act(async () => setRun(await api.finetune(me, token)))}>
          Run it
        </button>
        {run && (
          <>
            <p className="small">
              {run.messages_processed} message
              {run.messages_processed === 1 ? "" : "s"} across{" "}
              {run.interactors} {run.interactors === 1 ? "person" : "people"}.
            </p>
            {/* Almost every field here is a claim about what did not
                happen, and those are the reason the feature reads the way
                it does. Rendered from the answer rather than asserted by
                the console. */}
            <p className="muted small">
              Computed {run.computed}.{" "}
              {run.external_transmission
                ? "Something was transmitted externally."
                : "Nothing was transmitted anywhere."}{" "}
              {run.sealed_in_vault
                ? "The result is sealed in the vault."
                : "No vault here, so the result stays in the clear."}
            </p>
          </>
        )}
      </div>

      <div className="card">
        <h3>Show it something</h3>
        <p className="muted small">
          Name what is in front of you and what you are trying to do, and the
          profile talks you through it hands-free.
        </p>
        <div className="row">
          <input value={scene} onChange={(e) => setScene(e.target.value)}
                 placeholder="what it can see, comma separated"
                 style={{ flex: 1 }} />
          <input value={goal} onChange={(e) => setGoal(e.target.value)}
                 placeholder="what you are trying to do" style={{ flex: 1 }} />
          <button disabled={busy || !token || !scene.trim()}
                  onClick={act(async () => setSeen(await api.perceive(me, {
                    objects: scene.split(",").map((s) => s.trim())
                      .filter(Boolean),
                    goal: goal.trim() || undefined }, token)))}>
            Ask
          </button>
        </div>
        {seen && (
          <>
            <p className="muted small">
              Recognised {seen.recognized_count}:{" "}
              {Object.values(seen.recognized).flat().join(", ")}
            </p>
            <p className="small">{seen.guidance}</p>
            {/* Beside the words, not under a link. Everything generated
                here is marked, and the mark travels with it. */}
            <p className="muted small">
              {seen.watermark.display.line} — {seen.watermark.disclosure}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
