import { useState } from "react";
import { api, type PackSeed, type PackSummary, type Profile,
         type Succession } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * A beginning, an ending, what it is taught, and a press from the wrist.
 *
 * **The owner token cannot be the gate on succession**, and that is the whole
 * shape of it: the signal this route responds to is that the owner has died or
 * cannot act, so requiring their authorisation would be requiring the one
 * thing that is known to be unavailable. It is held by a reviewer instead —
 * outside profile ownership, against an out-of-band `verification_ref` such as
 * a death certificate or a power of attorney. With a named successor, control
 * passes and a fresh owner token is minted. With none, the profile sunsets to
 * memorial: **frozen rather than orphaned**, because a profile whose owner has
 * died and which nobody can reach is worse than one that has plainly stopped.
 *
 * A contested identity cannot be handed on. An open objection blocks
 * succession with a 409 — inheriting a profile somebody is disputing would
 * settle the dispute by transfer rather than by resolving it.
 *
 * At the other end, **genesis** is a profile born from four questions, and it
 * may choose its own name from the answers. Omit `display_name` and it does.
 *
 * Publishing a pack now needs an owner token, and the account sales accrue to
 * is read from that token rather than from the request body. It used to take
 * neither: anybody could publish under any publisher name and name any account
 * as the one the money went to. The argument against that was already written
 * down one module over, about gifts — *a body-supplied beneficiary would let
 * anyone direct a gift meant for a performer into their own balance.*
 *
 * And the wrist. One press goes down the same paths the full apps use — same
 * auth, same allowlists, same moderation. A shortcut that skipped any of those
 * would be a second, weaker way in, which is exactly what a wrist should not
 * be.
 */
export function Passing({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const me = session.profileId || "";
  const token = session.ownerToken || "";
  const account = session.accountId || "";

  const [answers, setAnswers] = useState({
    social_style: "", humor: "", what_matters: "", comfort: "",
  });
  const [birthdate, setBirthdate] = useState("");
  const [chosenName, setChosenName] = useState("");
  const [born, setBorn] = useState<Profile | null>(null);

  const [subject, setSubject] = useState("");
  const [ref, setRef] = useState("");
  const [reviewerToken, setReviewerToken] = useState("");
  const [passed, setPassed] = useState<Succession | null>(null);

  const [packTitle, setPackTitle] = useState("");
  const [packIndustry, setPackIndustry] = useState("trades");
  const [itemTitle, setItemTitle] = useState("");
  const [itemBody, setItemBody] = useState("");
  const [published, setPublished] = useState<PackSummary | null>(null);
  const [seeded, setSeeded] = useState<PackSeed | null>(null);

  const [target, setTarget] = useState<"workflow" | "robot" | "approval">(
    "workflow");
  const [actId, setActId] = useState("");
  const [action, setAction] = useState("advance");
  const [actInput, setActInput] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); }
    catch (e) { setError(e); } finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>Beginning, and passing on</h2>
      <p className="muted small">
        How a profile starts, what it is taught, who holds it after, and the
        one press from a wrist.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Born from four questions</h3>
        <p className="muted small">
          Leave the name blank and it picks its own from the answers. That is
          not decoration: a persona assembled from what somebody said about
          themselves should not then be handed a label by a form field.
        </p>
        {([
          ["social_style", "warm, but needs quiet evenings"],
          ["humor", "dry, gentle teasing"],
          ["what_matters", "family, honesty, the garden"],
          ["comfort", "sits with you rather than fixing it"],
        ] as const).map(([k, hint]) => (
          <div className="row" key={k}>
            <label className="small" style={{ width: 130 }}>
              {k.replace(/_/g, " ")}
            </label>
            <input value={answers[k]} placeholder={hint} style={{ flex: 1 }}
                   onChange={(e) =>
                     setAnswers({ ...answers, [k]: e.target.value })} />
          </div>
        ))}
        <div className="row">
          <input value={birthdate} onChange={(e) => setBirthdate(e.target.value)}
                 placeholder="your birthdate, YYYY-MM-DD" style={{ flex: 1 }} />
          <input value={chosenName}
                 onChange={(e) => setChosenName(e.target.value)}
                 placeholder="a name, or blank to let it choose"
                 style={{ flex: 1 }} />
          <button disabled={busy || !account || !birthdate.trim()}
                  onClick={act(async () => setBorn(await api.genesis({
                    owner_id: account, verification: { birthdate },
                    answers,
                    display_name: chosenName.trim() || undefined,
                  })), "Born.")}>Bring it into being</button>
        </div>
        {born && (
          <p className="small">
            <strong>{born.display_name}</strong> — <code>{born.id}</code>
            <br />
            <span className="muted">
              {chosenName.trim()
                ? "You named it."
                : "It named itself from what you said."}
            </span>
          </p>
        )}
        <p className="muted small">
          An owner under 18 needs a parent or guardian's consent, and the
          refusal says so rather than failing generically.
        </p>
      </div>

      <div className="card">
        <h3>Passing it on</h3>
        <p className="muted small">
          The one route in this product an <strong>owner token cannot
          open</strong> — because the signal it answers is that the owner has
          died or cannot act, and requiring their authorisation would be
          requiring the one thing known to be unavailable. A reviewer holds
          it, against a verification reference kept out of band: a death
          certificate, a power of attorney.
        </p>
        <div className="row">
          <input value={subject} onChange={(e) => setSubject(e.target.value)}
                 placeholder="the profile" style={{ flex: 1 }} />
          <input value={ref} onChange={(e) => setRef(e.target.value)}
                 placeholder="verification reference" style={{ flex: 1 }} />
          <input value={reviewerToken} type="password"
                 onChange={(e) => setReviewerToken(e.target.value)}
                 placeholder="reviewer token" style={{ flex: 1 }} />
          <button disabled={busy || !subject.trim() || !ref.trim()
                            || !reviewerToken}
                  onClick={act(async () => setPassed(await api.succeed(
                    subject.trim(), ref.trim(), reviewerToken)))}>
            Pass it on
          </button>
        </div>
        {passed && (
          <>
            <p className="small">
              Now <strong>{passed.status}</strong>
              {passed.successor_owner && (
                <> — held by <code>{passed.successor_owner}</code></>
              )}
            </p>
            {passed.owner_token ? (
              <p className="muted small">
                Their owner token, shown once:{" "}
                <code>{passed.owner_token}</code>
              </p>
            ) : (
              <p className="muted small">
                Nobody was named, so it sunsets to memorial: frozen rather
                than orphaned. A profile whose owner has died and which
                nobody can reach is worse than one that has plainly stopped.
              </p>
            )}
          </>
        )}
        <p className="muted small">
          A contested identity cannot be handed on: an open objection blocks
          this with a 409. Inheriting a profile somebody is disputing would
          settle the dispute by transfer rather than by resolving it.
        </p>
      </div>

      <div className="card">
        <h3>What it can be taught</h3>
        <p className="muted small">
          Publishing needs your owner token, and the account sales accrue to
          is read from it — not from the request. Naming somebody else's
          account in a body is how money ends up somewhere it was not earned.
        </p>
        <div className="row">
          <input value={packIndustry}
                 onChange={(e) => setPackIndustry(e.target.value)}
                 placeholder="industry" style={{ width: 140 }} />
          <input value={packTitle} onChange={(e) => setPackTitle(e.target.value)}
                 placeholder="the pack's title" style={{ flex: 1 }} />
        </div>
        <div className="row">
          <input value={itemTitle} onChange={(e) => setItemTitle(e.target.value)}
                 placeholder="one item's title" style={{ flex: 1 }} />
          <input value={itemBody} onChange={(e) => setItemBody(e.target.value)}
                 placeholder="what it teaches" style={{ flex: 1 }} />
          <button disabled={busy || !packTitle.trim() || !itemTitle.trim()
                            || !token}
                  onClick={act(async () => setPublished(
                    await api.publishPack({
                      industry: packIndustry.trim(), title: packTitle.trim(),
                      price: 0,
                      items: [{ title: itemTitle.trim(),
                                content: itemBody.trim() }],
                    }, token)), "Published.")}>
            Publish it
          </button>
        </div>
        <p className="muted small">
          A pack needs at least one item, a price cannot be negative, and
          every item in a robot pack needs a task — the command verb. Three
          refusals, each naming what is missing.
        </p>
        {published && (
          <p className="small">
            <strong>{published.title}</strong> — {published.items}{" "}
            {published.items === 1 ? "item" : "items"} ·{" "}
            {published.free ? "free" : `${published.price} ${published.currency}`}
            {" "}· published by {published.publisher}
          </p>
        )}
        <div className="row">
          <button className="chip" disabled={busy}
                  onClick={act(async () =>
                    setSeeded(await api.seedPacks()))}>
            seed the starter packs
          </button>
        </div>
        {seeded && (
          /* Both numbers. Reporting only `created` would make the second
             press look like it failed rather than like there was nothing
             left to do. */
          <p className="muted small">
            {seeded.created} created, {seeded.skipped} already there, across{" "}
            {seeded.industries} industries. Pressing again is safe.
          </p>
        )}
      </div>

      <div className="card">
        <h3>One press from the wrist</h3>
        <p className="muted small">
          Down the same paths the full apps use — same auth, same allowlists,
          same moderation. A shortcut that skipped any of those would be a
          second, weaker way in, which is exactly what a wrist should not be.
        </p>
        <div className="row">
          <select value={target}
                  onChange={(e) => setTarget(
                    e.target.value as typeof target)}>
            {(["workflow", "robot", "approval"] as const).map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <input value={actId} onChange={(e) => setActId(e.target.value)}
                 placeholder="its id" style={{ flex: 1 }} />
          <input value={action} onChange={(e) => setAction(e.target.value)}
                 placeholder="advance / assist / cancel"
                 style={{ width: 150 }} />
          <input value={actInput}
                 onChange={(e) => setActInput(e.target.value)}
                 placeholder="what it asked for" style={{ flex: 1 }} />
          <button disabled={busy || !me || !token || !actId.trim()}
                  onClick={act(() => api.watchAct(me, {
                    target, id: actId.trim(), action: action.trim(),
                    input: actInput.trim() || undefined }, token), "Done.")}>
            Press it
          </button>
        </div>
        <p className="muted small">
          <em>assist</em> needs input — the paused phase asked for something,
          and sending nothing would advance past the question rather than
          answer it.
        </p>
      </div>
    </div>
  );
}
