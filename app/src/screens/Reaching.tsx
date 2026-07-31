import { useState } from "react";
import { api, type Engagement, type FeedbackResult,
         type PersonaEmbedding, type ProactiveOutreach,
         type QuietHours } from "../api";
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
  const me = session.profileId || "";
  const token = session.ownerToken || "";
  const myInteractor = session.interactorId || "";
  const interactorToken = session.interactorToken || "";

  const [person, setPerson] = useState("");
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

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); }
    catch (e) { setError(e); } finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>Reaching out, and what stops it</h2>
      <p className="muted small">
        Four different refusals, and only two of them are yours to lift.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Somebody in particular</h3>
        <div className="row">
          <input value={person} onChange={(e) => setPerson(e.target.value)}
                 placeholder="a person's id" style={{ flex: 1 }} />
          <button disabled={busy || !who || !me || !token}
                  onClick={act(async () => {
                    setState(await api.engagement(me, who, token));
                  })}>How are we going</button>
        </div>
        {state && (
          <>
            <p className="small">
              {state.interactions} exchange{state.interactions === 1 ? "" : "s"}
              {" "}across {state.sessions}{" "}
              session{state.sessions === 1 ? "" : "s"} · score{" "}
              {state.score.toFixed(2)}
              <br />
              <span className="muted">
                {state.feedback_pos} up · {state.feedback_neg} down
              </span>
            </p>
            <p className="muted small">
              Readable by you and by them, and by nobody else. It is a record
              of how often somebody talks to this profile, which is a fact
              about them as much as about it.
            </p>
          </>
        )}
      </div>

      <div className="card">
        <h3>Reaching out first</h3>
        <p className="muted small">
          Three gates, and they refuse in three different sentences because
          they are three different facts. <strong>Reactive-only</strong> means
          you never switched outreach on. <strong>Awaiting a reply</strong>
          {" "}means it already reached out and heard nothing — it will not
          send twice into silence. <strong>Rate cap</strong> means it reached
          out recently. And <strong>quiet hours</strong> is not yours at all.
        </p>
        <button disabled={busy || !who || !me || !token}
                onClick={act(async () => {
                  setSent(await api.reachOut(me, who, token));
                }, "Sent.")}>Reach out now</button>
        {sent && (
          <>
            <p className="muted small">
              Its own reason for sending: <em>{sent.reason}</em>
            </p>
            <p className="small">{sent.message.content}</p>
            <p className="muted small">
              {sent.message.status === "pending"
                ? "Held for approval rather than delivered — an unprompted "
                  + "message is exactly the kind that should not slip past "
                  + "moderation."
                : "Delivered, and watermarked like every other thing this "
                  + "profile says."}
            </p>
          </>
        )}
      </div>

      <div className="card">
        <h3>Quiet hours</h3>
        <p className="muted small">
          The window during which nothing may reach out unprompted. Set by the
          person it protects — sending this with an owner token is refused,
          and that refusal is the point. A boundary your correspondent can
          move is not one.
        </p>
        {myInteractor && interactorToken ? (
          <>
            <div className="row">
              <label className="small">from{" "}
                <input type="number" min={0} max={23} value={start}
                       onChange={(e) => setStart(Number(e.target.value))}
                       style={{ width: 70 }} />
              </label>
              <label className="small">until{" "}
                <input type="number" min={0} max={23} value={end}
                       onChange={(e) => setEnd(Number(e.target.value))}
                       style={{ width: 70 }} />
              </label>
              <button disabled={busy}
                      onClick={act(async () => setWindow(
                        await api.setQuietHours(myInteractor, {
                          quiet_start: start, quiet_end: end },
                          interactorToken)), "Set.")}>
                Set my quiet hours
              </button>
              <button className="chip" disabled={busy}
                      onClick={act(async () => setWindow(
                        await api.setQuietHours(myInteractor, {
                          quiet_start: null, quiet_end: null },
                          interactorToken)), "Cleared.")}>
                clear
              </button>
            </div>
            <p className="muted small">
              Hours are UTC, 0 to 23. Both empty means no window.
              {window_ && ` Currently ${window_.quiet_start ?? "—"} to `}
              {window_ && `${window_.quiet_end ?? "—"}.`}
            </p>
            {start === end && (
              <p className="muted small">
                Those are the <strong>same hour</strong>, which covers
                nothing rather than everything — the window runs from the
                first up to but not including the second. To be quiet all
                day, end one hour before you start.
              </p>
            )}
          </>
        ) : (
          <p className="muted small">
            This is your own control, not one you hold over anybody else — so
            it needs your token as a person rather than as a profile's owner.
            Sign in as yourself to set it.
          </p>
        )}
      </div>

      <div className="card">
        <h3>Rate an exchange</h3>
        <p className="muted small">
          Gated on the rater's own token. A rating in somebody else's name is
          a lie about what they thought, and a thumbs-up is also the trigger
          for contributing that exchange to the shared model — so it is not a
          button anybody else gets to press for you.
        </p>
        <div className="row">
          {(["up", "down"] as const).map((r) => (
            <button key={r} className="chip"
                    disabled={busy || !me || !myInteractor || !interactorToken}
                    onClick={act(async () => setRated(
                      await api.rateExchange(me, myInteractor, r,
                                             interactorToken)))}>
              {r === "up" ? "👍 good" : "👎 not good"}
            </button>
          ))}
        </div>
        {rated && (
          <p className="muted small">
            {/* The two fields the read does not carry. */}
            Last seen {rated.last_seen ?? "—"} ·{" "}
            {rated.contributed
              ? "this exchange was contributed to the shared model, "
                + "anonymised"
              : "nothing left this deployment"}
            .
          </p>
        )}
      </div>

      <div className="card">
        <h3>What it has learned about them</h3>
        <p className="muted small">
          A latent picture of one relationship, and what the profile actually
          behaves from. Owner-only, and shown rather than described: a number
          nobody can see is a number nobody can argue with.
        </p>
        <button disabled={busy || !who || !me || !token}
                onClick={act(async () => {
                  setEmbedding(await api.personaEmbedding(me, who, token));
                })}>Show it</button>
        {embedding && (
          <>
            {Object.entries(embedding.vector).map(([k, v]) => (
              <p className="small" key={k}>
                {k} — {typeof v === "number" ? v.toFixed(2) : String(v)}
              </p>
            ))}
            <p className="muted small">
              Version {embedding.version}, moved {embedding.updated_at}.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
