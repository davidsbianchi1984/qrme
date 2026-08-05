import { useState } from "react";
import { api, type ConnJoined, type ConnMessage,
         type Summoned } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
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
  const lang = visitorLang();
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
      <h2>{tr("str.title", lang)}</h2>
      <Refusal error={error} />

      {/* --- what a reference resolves to ------------------------------ */}
      <div className="card">
        <h3>{tr("str.follow.hdr", lang)}</h3>
        <p className="muted small">
          {fill(tr("str.ref.pitch", lang), {
            handle: <code>{tr("str.handle.eg", lang)}</code>,
            tag: <code>{tr("str.tag.eg", lang)}</code>,
          })}
        </p>
        <input value={ref} onChange={(e) => setRef(e.target.value)}
               placeholder={tr("str.ref.ph", lang)} />
        <button disabled={!ref} onClick={() => go(
          () => api.summon(ref), setFound)}>
          {tr("str.followit", lang)}
        </button>
        {found && (
          <div>
            {found.type === "beacon" && (
              <p className="muted small">
                {fill(tr("str.leftat", lang), {
                  where: found.label || tr("str.somewhere", lang) })}
                {found.location && ` · ${found.location}`}
                {typeof found.scans === "number" && tr("str.scanned", lang)
                  .replace("{n}", String(found.scans))}
              </p>
            )}
            {cards.length === 0 && (
              <p className="muted small">{tr("str.nothing", lang)}</p>
            )}
            {cards.map((c) => (
              <div key={c.profile_id}>
                <p className="small">
                  <strong>{c.display_name}</strong>
                  {c.handle && <span className="muted"> {c.handle}</span>}
                </p>
                <p className="muted small">
                  {c.rated
                    ? tr("str.agewall", lang)
                    : c.purpose.replace(/_/g, " ")}
                  {c.status !== "active" && tr("str.nolonger", lang)}
                </p>
                {c.note && <p className="muted small">{c.note}</p>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* --- anonymous matchmaking ------------------------------------- */}
      <div className="card">
        <h3>{tr("str.talk", lang)}</h3>
        <p className="muted small">{tr("str.talk.pitch", lang)}</p>
        {!token && (
          <p className="muted small">{tr("str.needown", lang)}</p>
        )}
        <input value={alias} onChange={(e) => setAlias(e.target.value)}
               placeholder={tr("str.alias.ph", lang)} />
        <select value={tier} onChange={(e) => setTier(e.target.value)}>
          <option value="friendly">{tr("str.friendly", lang)}</option>
          <option value="rated">18+</option>
        </select>
        <p className="muted small">
          {fill(tr("str.ratedqueue", lang),
            { both: <em>{tr("str.both", lang)}</em> })}
        </p>
        <button disabled={!token || !me} onClick={() => go(
          () => api.joinQueue({ interactor_id: me, tier,
                                ...(alias ? { alias } : {}) }, token),
          (j) => { setJoined(j); setMessages([]); })}>
          {tier === "rated"
            ? tr("str.joinrated", lang) : tr("str.findsomebody", lang)}
        </button>

        {joined?.status === "waiting" && (
          <p className="muted small">
            {fill(tr("str.waiting", lang), { tier: joined.tier })}
          </p>
        )}

        {cid && (
          <div>
            <p className="small">
              {fill(tr("str.talkingto", lang), {
                who: <strong>
                  {joined?.matched_with || tr("str.stranger", lang)}
                </strong>,
              })}
            </p>
            <button className="ghost" onClick={refresh}>
              {tr("str.refresh", lang)}
            </button>
            {messages.map((m) => (
              <p key={m.id} className="small">
                <strong>{m.from}</strong> {m.content}
                {m.status === "blocked" && (
                  <span className="muted">
                    {" "}{tr("str.heldback", lang)}
                  </span>
                )}
              </p>
            ))}
            <input value={draft} onChange={(e) => setDraft(e.target.value)}
                   placeholder={tr("str.say.ph", lang)} />
            <button disabled={!draft} onClick={() => go(
              () => api.sendToConnection(cid, { interactor_id: me,
                                                message: draft }, token),
              () => { setDraft(""); refresh(); })}>
              {tr("str.send", lang)}
            </button>
            <button className="ghost" onClick={() => go(
              () => api.endConnection(cid, me, token),
              () => { setJoined(null); setMessages([]); })}>
              {tr("str.endit", lang)}
            </button>
            <p className="muted small">{tr("str.endnote", lang)}</p>
          </div>
        )}
      </div>
    </div>
  );
}
