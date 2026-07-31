import { useState } from "react";
import { api, type ConnJoined, type ConnMessage,
         type Summoned } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Arriving, and talking to a stranger.
 *
 * Two things a person does before they have anything of their own here.
 * `summon` is what a scanned sticker or a shared `@handle` resolves through —
 * public, because the person following one has no account yet. And the
 * connection routes are anonymous matchmaking between two people with no
 * profile involved at all: you see each other's chosen alias, never a name.
 *
 * Neither had a door in this console.
 *
 * ## The id was never the answer to who is asking
 *
 * Every connection route read `interactor_id` out of the request body or the
 * query string and checked only that it named one of the two participants.
 * Nothing checked that the caller *was* that person, and nothing asked for a
 * token at all. So two public ids were enough to:
 *
 * * join the queue as somebody else, and be matched with a stranger under
 *   their name — on the rated tier, borrowing an adult's id past the age
 *   check;
 * * send messages as either party;
 * * read the pair's entire conversation as either party, **including the
 *   blocked messages** this feature deliberately keeps back for their
 *   sender's eyes alone;
 * * and end it.
 *
 * Ending was the worst of the four. The check was `if ender:` over an
 * *optional* body and an *optional* query parameter, so supplying neither
 * skipped it: a bare POST with no id and no credential ended a stranger's
 * conversation, and returned any wearable lent inside it.
 *
 * This is the room defect a few rounds back, in a feature whose entire
 * premise is anonymity and consent — and `community._require_in_room` had
 * already settled the argument in the same words. An id is a claim. The token
 * is the answer.
 */
export function Stranger() {
  const { session } = useSession();
  const me = session.interactorId || "";
  const token = session.interactorToken || "";

  const [error, setError] = useState<unknown>(null);

  // Arriving
  const [ref, setRef] = useState("");
  const [found, setFound] = useState<Summoned | null>(null);

  // Talking to a stranger
  const [alias, setAlias] = useState("");
  const [tier, setTier] = useState("friendly");
  const [joined, setJoined] = useState<ConnJoined | null>(null);
  const [messages, setMessages] = useState<ConnMessage[]>([]);
  const [draft, setDraft] = useState("");

  const cid = joined?.connection_id || "";

  async function go<T>(work: () => Promise<T>, then: (v: T) => void) {
    setError(null);
    try { then(await work()); } catch (e) { setError(e); }
  }

  const refresh = () => {
    if (!cid) return;
    go(() => api.connectionMessages(cid, me, token), setMessages);
  };

  const cards = found
    ? (found.profiles ?? (found.profile ? [found.profile] : []))
    : [];

  return (
    <div className="screen">
      <h2>Arriving, and strangers</h2>
      <Refusal error={error} />

      {/* --- what a reference resolves to ------------------------------ */}
      <div className="card">
        <h3>Follow a reference</h3>
        <p className="muted small">
          An <code>@handle</code>, a <code>#tag</code>, or the id off a printed
          sticker. Public, because somebody following one has no account yet —
          which is the whole point of leaving one somewhere.
        </p>
        <input value={ref} onChange={(e) => setRef(e.target.value)}
               placeholder="@rosa, #locksmith, or a beacon id" />
        <button disabled={!ref} onClick={() => go(
          () => api.summon(ref), setFound)}>Follow it</button>
        {found && (
          <div>
            {found.type === "beacon" && (
              <p className="muted small">
                Left at {found.label || "somewhere"}
                {found.location && ` · ${found.location}`}
                {typeof found.scans === "number"
                  && ` · scanned ${found.scans} times`}
              </p>
            )}
            {cards.length === 0 && (
              <p className="muted small">Nothing answers to that.</p>
            )}
            {cards.map((c) => (
              <div key={c.profile_id}>
                <p className="small">
                  <strong>{c.display_name}</strong>
                  {c.handle && <span className="muted"> {c.handle}</span>}
                </p>
                <p className="muted small">
                  {c.rated
                    ? "18+ — this resolves to a wall unless you are signed in "
                      + "as a verified adult."
                    : c.purpose.replace(/_/g, " ")}
                  {c.status !== "active" && " · no longer answering"}
                </p>
                {c.note && <p className="muted small">{c.note}</p>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* --- anonymous matchmaking ------------------------------------- */}
      <div className="card">
        <h3>Talk to a stranger</h3>
        <p className="muted small">
          No profile in this one — two people, each seeing only the alias the
          other chose. Everything here goes out under your own credential:
          the id in the request says whose turn it is, and the token says who
          is asking, which is the part that used to be missing.
        </p>
        {!token && (
          <p className="muted small">
            You need an interactor of your own before you can queue.
          </p>
        )}
        <input value={alias} onChange={(e) => setAlias(e.target.value)}
               placeholder="what to be called (defaults to Stranger)" />
        <select value={tier} onChange={(e) => setTier(e.target.value)}>
          <option value="friendly">friendly</option>
          <option value="rated">18+</option>
        </select>
        <p className="muted small">
          The 18+ queue needs a verified adult on <em>both</em> sides before
          either is admitted to it.
        </p>
        <button disabled={!token || !me} onClick={() => go(
          () => api.joinQueue({ interactor_id: me, tier,
                                ...(alias ? { alias } : {}) }, token),
          (j) => { setJoined(j); setMessages([]); })}>
          {tier === "rated" ? "Join the 18+ queue" : "Find somebody"}
        </button>

        {joined?.status === "waiting" && (
          <p className="muted small">
            Waiting for somebody else on the {joined.tier} queue.
          </p>
        )}

        {cid && (
          <div>
            <p className="small">
              Talking to <strong>{joined?.matched_with || "Stranger"}</strong>.
              That is the name they chose, and all either of you gets.
            </p>
            <button className="ghost" onClick={refresh}>Refresh</button>
            {messages.map((m) => (
              <p key={m.id} className="small">
                <strong>{m.from}</strong> {m.content}
                {m.status === "blocked" && (
                  <span className="muted">
                    {" "}· held back — only you can see this
                  </span>
                )}
              </p>
            ))}
            <input value={draft} onChange={(e) => setDraft(e.target.value)}
                   placeholder="say something" />
            <button disabled={!draft} onClick={() => go(
              () => api.sendToConnection(cid, { interactor_id: me,
                                                message: draft }, token),
              () => { setDraft(""); refresh(); })}>Send</button>
            <button className="ghost" onClick={() => go(
              () => api.endConnection(cid, me, token),
              () => { setJoined(null); setMessages([]); })}>
              End it
            </button>
            <p className="muted small">
              Either side may end it, and ending returns any microphone lent
              inside — the permission was scoped to this conversation and does
              not survive it.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
