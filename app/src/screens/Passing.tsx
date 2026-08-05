import { useState } from "react";
import { api, type PackSeed, type PackSummary, type Profile,
         type Succession } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
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
  const lang = visitorLang();
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
      <h2>{tr("pas.title", lang)}</h2>
      <p className="muted small">{tr("pas.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("pas.born", lang)}</h3>
        <p className="muted small">{tr("pas.born.pitch", lang)}</p>
        {/* The label and the example both come from the table. The example
            is the part a form like this is actually read from, so leaving it
            in English would leave the question in English. */}
        {([
          ["social_style", "social"],
          ["humor", "humor"],
          ["what_matters", "matters"],
          ["comfort", "comfort"],
        ] as const).map(([k, suffix]) => (
          <div className="row" key={k}>
            <label className="small" style={{ width: 130 }}>
              {tr(`pas.q.${suffix}`, lang)}
            </label>
            <input value={answers[k]} style={{ flex: 1 }}
                   placeholder={tr(`pas.h.${suffix}`, lang)}
                   onChange={(e) =>
                     setAnswers({ ...answers, [k]: e.target.value })} />
          </div>
        ))}
        <div className="row">
          <input value={birthdate} onChange={(e) => setBirthdate(e.target.value)}
                 placeholder={tr("pas.birth.ph", lang)} style={{ flex: 1 }} />
          <input value={chosenName}
                 onChange={(e) => setChosenName(e.target.value)}
                 placeholder={tr("pas.name.ph", lang)}
                 style={{ flex: 1 }} />
          <button disabled={busy || !account || !birthdate.trim()}
                  onClick={act(async () => setBorn(await api.genesis({
                    owner_id: account, verification: { birthdate },
                    answers,
                    display_name: chosenName.trim() || undefined,
                  })), tr("pas.born.said", lang))}>
            {tr("pas.bring", lang)}
          </button>
        </div>
        {born && (
          <p className="small">
            <strong>{born.display_name}</strong> — <code>{born.id}</code>
            <br />
            <span className="muted">
              {chosenName.trim()
                ? tr("pas.younamed", lang) : tr("pas.itnamed", lang)}
            </span>
          </p>
        )}
        <p className="muted small">{tr("pas.minor", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("pas.on", lang)}</h3>
        <p className="muted small">
          {fill(tr("pas.on.pitch", lang),
            { cannot: <strong>{tr("pas.cannot", lang)}</strong> })}
        </p>
        <div className="row">
          <input value={subject} onChange={(e) => setSubject(e.target.value)}
                 placeholder={tr("pas.subject.ph", lang)} style={{ flex: 1 }} />
          <input value={ref} onChange={(e) => setRef(e.target.value)}
                 placeholder={tr("pas.ref.ph", lang)} style={{ flex: 1 }} />
          <input value={reviewerToken} type="password"
                 onChange={(e) => setReviewerToken(e.target.value)}
                 placeholder={tr("pas.reviewer.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !subject.trim() || !ref.trim()
                            || !reviewerToken}
                  onClick={act(async () => setPassed(await api.succeed(
                    subject.trim(), ref.trim(), reviewerToken)))}>
            {tr("pas.passit", lang)}
          </button>
        </div>
        {passed && (
          <>
            <p className="small">
              {fill(tr("pas.now", lang),
                { status: <strong>{passed.status}</strong> })}
              {passed.successor_owner && (
                <>{" "}{fill(tr("pas.heldby", lang),
                  { who: <code>{passed.successor_owner}</code> })}</>
              )}
            </p>
            {passed.owner_token ? (
              <p className="muted small">
                {fill(tr("pas.token.once", lang),
                  { token: <code>{passed.owner_token}</code> })}
              </p>
            ) : (
              <p className="muted small">{tr("pas.memorial", lang)}</p>
            )}
          </>
        )}
        <p className="muted small">{tr("pas.contested", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("pas.taught", lang)}</h3>
        <p className="muted small">{tr("pas.taught.pitch", lang)}</p>
        <div className="row">
          <input value={packIndustry}
                 onChange={(e) => setPackIndustry(e.target.value)}
                 placeholder={tr("pas.industry.ph", lang)} style={{ width: 140 }} />
          <input value={packTitle} onChange={(e) => setPackTitle(e.target.value)}
                 placeholder={tr("pas.packtitle.ph", lang)} style={{ flex: 1 }} />
        </div>
        <div className="row">
          <input value={itemTitle} onChange={(e) => setItemTitle(e.target.value)}
                 placeholder={tr("pas.itemtitle.ph", lang)} style={{ flex: 1 }} />
          <input value={itemBody} onChange={(e) => setItemBody(e.target.value)}
                 placeholder={tr("pas.itemwhat.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !packTitle.trim() || !itemTitle.trim()
                            || !token}
                  onClick={act(async () => setPublished(
                    await api.publishPack({
                      industry: packIndustry.trim(), title: packTitle.trim(),
                      price: 0,
                      items: [{ title: itemTitle.trim(),
                                content: itemBody.trim() }],
                    }, token)), tr("pas.published.said", lang))}>
            {tr("pas.publish", lang)}
          </button>
        </div>
        <p className="muted small">{tr("pas.packrules", lang)}</p>
        {published && (
          <p className="small">
            {fill(tr("pas.pack.row", lang), {
              title: <strong>{published.title}</strong>,
              n: published.items,
              s: published.items === 1 ? "" : "s",
              price: published.free ? tr("pas.free", lang)
                : `${published.price} ${published.currency}`,
              who: published.publisher,
            })}
          </p>
        )}
        <div className="row">
          <button className="chip" disabled={busy}
                  onClick={act(async () =>
                    setSeeded(await api.seedPacks()))}>
            {tr("pas.seed", lang)}
          </button>
        </div>
        {seeded && (
          /* Both numbers. Reporting only `created` would make the second
             press look like it failed rather than like there was nothing
             left to do. */
          <p className="muted small">
            {fill(tr("pas.seeded", lang), {
              created: seeded.created, skipped: seeded.skipped,
              n: seeded.industries,
            })}
          </p>
        )}
      </div>

      <div className="card">
        <h3>{tr("pas.wrist", lang)}</h3>
        <p className="muted small">{tr("pas.wrist.pitch", lang)}</p>
        <div className="row">
          <select value={target}
                  onChange={(e) => setTarget(
                    e.target.value as typeof target)}>
            {(["workflow", "robot", "approval"] as const).map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <input value={actId} onChange={(e) => setActId(e.target.value)}
                 placeholder={tr("pas.id.ph", lang)} style={{ flex: 1 }} />
          <input value={action} onChange={(e) => setAction(e.target.value)}
                 placeholder={tr("pas.action.ph", lang)}
                 style={{ width: 150 }} />
          <input value={actInput}
                 onChange={(e) => setActInput(e.target.value)}
                 placeholder={tr("pas.input.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !me || !token || !actId.trim()}
                  onClick={act(() => api.watchAct(me, {
                    target, id: actId.trim(), action: action.trim(),
                    input: actInput.trim() || undefined }, token),
                    tr("pas.done.said", lang))}>
            {tr("pas.press", lang)}
          </button>
        </div>
        <p className="muted small">
          {fill(tr("pas.assist.note", lang),
            { assist: <em>{tr("pas.assist", lang)}</em> })}
        </p>
      </div>
    </div>
  );
}
