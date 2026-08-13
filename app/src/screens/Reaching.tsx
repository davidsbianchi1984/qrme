import { useEffect, useState } from "react";
import { api, type Engagement, type FeedbackResult,
         type PersonaEmbedding, type ProactiveOutreach,
         type QuietHours } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * One person, and what reaching out to them costs.
 *
 * **Three gates stand between a profile and an unprompted message**, and they
 * refuse in three different sentences because they are three different facts.
 * A screen that collapsed them into "can't right now" would be throwing away
 * the only information the owner can act on — one is a setting they control,
 * one clears itself when somebody replies, and one is not theirs at all:
 *
 * | | who lifts it | how |
 * |---|---|---|
 * | reactive-only (403) | the owner | turn proactive outreach on |
 * | awaiting a reply (429) | the recipient | reply once |
 * | rate cap (429) | time | wait out the interval |
 * | quiet hours (429) | **the recipient** | change their own window |
 *
 * The last row is the one worth knowing. **The owner cannot set somebody
 * else's quiet hours** — sending it with an owner token is a 403, and that
 * refusal is the feature rather than a gap in it. A window your correspondent
 * can move is not a boundary. So this screen shows the control to whoever
 * holds the person's token and explains the refusal to everybody else.
 *
 * The embedding is the uncomfortable card, and it is here for the same reason
 * the lobby's instruction card is: it is a latent model of a named person —
 * how engaged, how warm, how stressed — and it is what the profile actually
 * behaves from. Owner-only, and shown rather than described, because a number
 * nobody can see is a number nobody can argue with.
 *
 * A rating and the engagement record answer **different shapes on purpose**:
 * the write hands back `last_seen` and `contributed`, the read does not. And
 * `contributed` is worth rendering, because a thumbs-up is the trigger for
 * sending an anonymised exchange to the cloud — it happens only on `up`, only
 * with the profile opted in, and the field says whether it actually did.
 */
export function Reaching({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";
  const myInteractor = session.interactorId || "";
  const interactorToken = session.interactorToken || "";

  const [person, setPerson] = useState("");
  // The people this profile has actually talked to — a field report typed
  // nothing into "a person's id" and found every button on the screen
  // dead. The id field stays for ids from elsewhere; the list is for
  // everyone else.
  const [known, setKnown] = useState<
    { interactor_id: string; interactor_name: string }[]>([]);
  const [state, setState] = useState<Engagement | null>(null);
  const [rated, setRated] = useState<FeedbackResult | null>(null);
  const [embedding, setEmbedding] = useState<PersonaEmbedding | null>(null);
  const [sent, setSent] = useState<ProactiveOutreach | null>(null);
  const [window_, setWindow] = useState<QuietHours | null>(null);

  const [start, setStart] = useState(22);
  const [end, setEnd] = useState(7);

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const who = person.trim();

  useEffect(() => {
    if (!me || !token) return;
    api.memories(me, token)
      .then((rows) => setKnown(rows.map((r) => ({
        interactor_id: r.interactor_id,
        interactor_name: r.interactor_name }))))
      .catch(() => setKnown([]));
  }, [me, token]);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); }
    catch (e) { setError(e); } finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>{tr("rch.title", lang)}</h2>
      <p className="muted small">{tr("rch.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("rch.who", lang)}</h3>
        {known.length > 0 && (
          <select value={known.some((k) => k.interactor_id === person)
                    ? person : ""}
                  onChange={(e) => setPerson(e.target.value)}>
            <option value="">{tr("rch.pick", lang)}</option>
            {known.map((k) => (
              <option key={k.interactor_id} value={k.interactor_id}>
                {k.interactor_name}
              </option>
            ))}
          </select>
        )}
        <div className="row">
          <input value={person} onChange={(e) => setPerson(e.target.value)}
                 placeholder={tr("rch.who.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !who || !me || !token}
                  onClick={act(async () => {
                    setState(await api.engagement(me, who, token));
                  })}>{tr("rch.how", lang)}</button>
        </div>
        {!who && (
          <p className="muted small">{tr("rch.pickfirst", lang)}</p>
        )}
        {state && (
          <>
            <p className="small">
              {fill(tr("rch.state", lang), {
                n: state.interactions,
                s: state.interactions === 1 ? "" : "s",
                m: state.sessions,
                t: state.sessions === 1 ? "" : "s",
                score: state.score.toFixed(2),
              })}
              <br />
              <span className="muted">
                {fill(tr("rch.updown", lang), {
                  up: state.feedback_pos, down: state.feedback_neg })}
              </span>
            </p>
            <p className="muted small">{tr("rch.read", lang)}</p>
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("rch.first", lang)}</h3>
        <p className="muted small">
          {fill(tr("rch.gates", lang), {
            reactive: <strong>{tr("rch.reactive", lang)}</strong>,
            awaiting: <strong>{tr("rch.awaiting", lang)}</strong>,
            ratecap: <strong>{tr("rch.ratecap", lang)}</strong>,
            quiet: <strong>{tr("rch.quiet.low", lang)}</strong>,
          })}
        </p>
        <button disabled={busy || !who || !me || !token}
                onClick={act(async () => {
                  setSent(await api.reachOut(me, who, token));
                }, tr("rch.sent.said", lang))}>{tr("rch.now", lang)}</button>
        {sent && (
          <>
            <p className="muted small">
              {fill(tr("rch.reason", lang), { why: <em>{sent.reason}</em> })}
            </p>
            <p className="small">{sent.message.content}</p>
            <p className="muted small">
              {sent.message.status === "pending"
                ? tr("rch.held", lang) : tr("rch.delivered", lang)}
            </p>
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("rch.quiet", lang)}</h3>
        <p className="muted small">{tr("rch.quiet.pitch", lang)}</p>
        {myInteractor && interactorToken ? (
          <>
            <div className="row">
              <label className="small">{tr("rch.from", lang)}{" "}
                <input type="number" min={0} max={23} value={start}
                       onChange={(e) => setStart(Number(e.target.value))}
                       style={{ width: 70 }} />
              </label>
              <label className="small">{tr("rch.until", lang)}{" "}
                <input type="number" min={0} max={23} value={end}
                       onChange={(e) => setEnd(Number(e.target.value))}
                       style={{ width: 70 }} />
              </label>
              <button disabled={busy}
                      onClick={act(async () => setWindow(
                        await api.setQuietHours(myInteractor, {
                          quiet_start: start, quiet_end: end },
                          interactorToken)), tr("rch.set.said", lang))}>
                {tr("rch.set", lang)}
              </button>
              <button className="chip" disabled={busy}
                      onClick={act(async () => setWindow(
                        await api.setQuietHours(myInteractor, {
                          quiet_start: null, quiet_end: null },
                          interactorToken)), tr("rch.cleared.said", lang))}>
                {tr("rch.clear", lang)}
              </button>
            </div>
            <p className="muted small">
              {tr("rch.utc", lang)}
              {window_ && fill(tr("rch.currently", lang), {
                a: window_.quiet_start ?? "—",
                b: window_.quiet_end ?? "—",
              })}
            </p>
            {start === end && (
              <p className="muted small">
                {fill(tr("rch.samehour", lang), {
                  same: <strong>{tr("rch.samehour.term", lang)}</strong>,
                })}
              </p>
            )}
          </>
        ) : (
          <p className="muted small">{tr("rch.notyours", lang)}</p>
        )}
      </div>

      <div className="card">
        <h3>{tr("rch.rate", lang)}</h3>
        <p className="muted small">{tr("rch.rate.pitch", lang)}</p>
        <div className="row">
          {(["up", "down"] as const).map((r) => (
            <button key={r} className="chip"
                    disabled={busy || !me || !myInteractor || !interactorToken}
                    onClick={act(async () => setRated(
                      await api.rateExchange(me, myInteractor, r,
                                             interactorToken)))}>
              {r === "up" ? tr("rch.up", lang) : tr("rch.down", lang)}
            </button>
          ))}
        </div>
        {rated && (
          <p className="muted small">
            {/* The two fields the read does not carry. */}
            {fill(tr("rch.lastseen", lang), {
              when: rated.last_seen ?? "—",
              what: rated.contributed
                ? tr("rch.contributed", lang) : tr("rch.nothingleft", lang),
            })}
          </p>
        )}
      </div>

      <div className="card">
        <h3>{tr("rch.learned", lang)}</h3>
        <p className="muted small">{tr("rch.learned.pitch", lang)}</p>
        <button disabled={busy || !who || !me || !token}
                onClick={act(async () => {
                  setEmbedding(await api.personaEmbedding(me, who, token));
                })}>{tr("rch.show", lang)}</button>
        {embedding && (
          <>
            {Object.entries(embedding.vector).map(([k, v]) => (
              <p className="small" key={k}>
                {k} — {typeof v === "number" ? v.toFixed(2) : String(v)}
              </p>
            ))}
            <p className="muted small">
              {fill(tr("rch.version", lang), {
                v: embedding.version, when: embedding.updated_at })}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
