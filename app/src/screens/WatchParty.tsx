import { useEffect, useState } from "react";
import { api, type PartyContext, type PartyLine,
         type WatchParty as Party } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Watching a posted video together, with synthetic profiles in the room.
 *
 * Nine routes with no caller. The one worth building a door for on its own is
 * `/context`: it is everything a synthetic profile in the party is allowed to
 * know, and what it pointedly does not include is the video. The reply carries
 * `you_have_not_seen_it` and the literal instruction that goes into the prompt
 * — *"if somebody asks what you thought of a moment in it, say you have not
 * seen it rather than inventing one."*
 *
 * That instruction is rendered verbatim here, in a panel of its own. A person
 * whose profile is sitting in a room talking about a film can read exactly what
 * it was told, instead of taking on trust that it was told anything. A model
 * handed only chat lines will otherwise fill the gap with a plausible opinion
 * about footage nobody showed it, which is the most ordinary-looking lie this
 * product could tell — so the absence is drawn rather than described.
 *
 * The rest follows the room's two rules: only the host moves the position, and
 * moving it moves a *number*. Nobody's player is started remotely, which is
 * what keeps the embed promise from being broken twenty times at once. The
 * screen says so in the server's own words rather than ours.
 */
export function WatchParty({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const me = session.interactorId || "";
  const token = session.interactorToken || "";

  const [party, setParty] = useState<Party | null>(null);
  const [lines, setLines] = useState<PartyLine[]>([]);
  const [ctx, setCtx] = useState<PartyContext | null>(null);
  const [lookup, setLookup] = useState("");
  const [postId, setPostId] = useState("");
  const [title, setTitle] = useState("");
  const [say, setSay] = useState("");
  const [bring, setBring] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);

  const fail = (e: unknown) => setError(e);

  const landed = (p: Party, said?: string) => {
    setParty(p); setError(null); if (said) setNote(said);
  };

  const act = (fn: () => Promise<Party>, said?: string) => async () => {
    setError(null); setNote(null);
    try { landed(await fn(), said); } catch (e) { fail(e); }
  };

  // Chat and context follow whichever party is open. Both are members-only,
  // so a failure here is ordinary rather than a banner.
  useEffect(() => {
    if (!party || !token) return;
    api.watchPartyChat(party.id, token).then((r) => setLines(r.lines))
      .catch(() => undefined);
    api.watchPartyContext(party.id, token).then(setCtx)
      .catch(() => setCtx(null));
  }, [party, token]);

  async function post() {
    if (!party) return;
    setError(null); setNote(null);
    try {
      const posted = await api.sayInWatchParty(party.id, {
        member_id: me, body: say.trim(),
        at_position_s: party.position_s,
      }, token);
      setSay("");
      // The reply carries a moderation verdict, so a line can come back
      // blocked. Say so rather than optimistically showing it in the room.
      if (posted.status !== "approved") {
        setNote(`Held: ${posted.blocked_reason || posted.status}`);
      }
      const r = await api.watchPartyChat(party.id, token);
      setLines(r.lines);
    } catch (e) { fail(e); }
  }

  const iAmHost = party ? party.host_id === me : false;

  return (
    <div className="screen">
      <h2>Watch together</h2>
      <p className="muted small">
        A posted video, a shared position, and whoever you bring — including
        your own profiles.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Start or join</h3>
        <div className="row">
          <input value={postId} onChange={(e) => setPostId(e.target.value)}
                 placeholder="post id (a post with a video)" style={{ flex: 1 }} />
          <input value={title} onChange={(e) => setTitle(e.target.value)}
                 placeholder="call it something" />
          <button disabled={!postId.trim() || !token} onClick={act(
            () => api.startWatchParty(
              { post_id: postId.trim(), host_id: me, title: title.trim() }, token),
            "Open. Bring people in.")}>Start</button>
        </div>
        <div className="row">
          <input value={lookup} onChange={(e) => setLookup(e.target.value)}
                 placeholder="party id" style={{ flex: 1 }} />
          <button disabled={!lookup.trim() || !token} onClick={act(
            () => api.joinWatchParty(lookup.trim(), { member_id: me }, token),
            "You are in.")}>Join</button>
          <button disabled={!lookup.trim() || !token} onClick={act(
            () => api.watchParty(lookup.trim(), token))}>Open</button>
        </div>
      </div>

      {party && (
        <>
          <div className="card">
            <h3>{party.title || "Watch party"}</h3>
            <p className="small">
              <strong>{party.video.title}</strong> on {party.video.platform_name}
            </p>
            {/* The platform note, verbatim: nothing is requested from them
                until somebody presses play. */}
            <p className="muted small">{party.video.note}</p>
            <p className="muted small">{party.note}</p>
            <p className="small">
              At {party.position_s}s · {party.playing ? "playing" : "paused"} ·{" "}
              {party.people} {party.people === 1 ? "person" : "people"},{" "}
              {party.profiles} profile{party.profiles === 1 ? "" : "s"}
            </p>
          </div>

          <div className="card">
            <h3>Who is here</h3>
            {party.members.map((m) => (
              <div key={m.member_id} className="row">
                <div style={{ flex: 1 }}>
                  <strong>{m.display_name || m.member_id}</strong>
                  {/* Travels with every member, so the room can always say
                      who is not a person. */}
                  {m.synthetic && <span className="chip"> synthetic</span>}
                  <div className="muted small">{m.role}</div>
                </div>
                {(m.member_id === me || iAmHost) && (
                  <button onClick={act(
                    () => api.leaveWatchParty(party.id, m.member_id, token),
                    m.member_id === me ? "You left." : "Removed.")}>
                    {m.member_id === me ? "Leave" : "Remove"}
                  </button>
                )}
              </div>
            ))}
            <div className="row">
              <input value={bring} onChange={(e) => setBring(e.target.value)}
                     placeholder="a profile id of yours" style={{ flex: 1 }} />
              <button disabled={!bring.trim()} onClick={act(
                () => api.joinWatchParty(
                  party.id, { member_id: bring.trim(), kind: "profile" },
                  session.ownerToken || token),
                "Brought in.")}>Bring a profile</button>
            </div>
            <p className="muted small">
              Bringing a profile in speaks in its voice, so it needs that
              profile's own owner token — not yours as a person.
            </p>
          </div>

          {iAmHost && (
            <div className="card">
              <h3>The room's position</h3>
              <div className="row">
                <button onClick={act(() => api.seekWatchParty(party.id, {
                  host_id: me, position_s: Math.max(0, party.position_s - 15),
                }, token))}>−15s</button>
                <button onClick={act(() => api.seekWatchParty(party.id, {
                  host_id: me, position_s: party.position_s + 15,
                }, token))}>+15s</button>
                <button onClick={act(() => api.seekWatchParty(party.id, {
                  host_id: me, position_s: party.position_s,
                  playing: !party.playing,
                }, token))}>{party.playing ? "Mark paused" : "Mark playing"}</button>
                <button onClick={async () => {
                  setError(null);
                  try {
                    const r = await api.endWatchParty(party.id, me, token);
                    setNote(`Ended. ${r.grants_closed} grant(s) closed, `
                      + `${r.microphones_returned} microphone(s) returned.`);
                    setParty(null); setLines([]); setCtx(null);
                  } catch (e) { fail(e); }
                }}>End the party</button>
              </div>
              <p className="muted small">
                This moves a number. It does not press play on anybody's device
                — each person's own player still starts when they start it.
              </p>
            </div>
          )}

          <div className="card">
            <h3>The room</h3>
            {lines.length === 0 && <p className="muted small">Nothing said yet.</p>}
            {lines.map((l) => (
              <p key={l.id} className="small">
                <strong>{l.display_name || l.member_id}</strong>
                {l.synthetic && <span className="chip"> synthetic</span>}
                {" — "}{l.body}
                {l.position_s !== null && (
                  <span className="muted"> (at {l.position_s}s)</span>
                )}
              </p>
            ))}
            <div className="row">
              <input value={say} onChange={(e) => setSay(e.target.value)}
                     placeholder="say something" style={{ flex: 1 }}
                     onKeyDown={(e) => e.key === "Enter" && say.trim() && post()} />
              <button disabled={!say.trim()} onClick={post}>Say it</button>
            </div>
          </div>

          {ctx && (
            <div className="card">
              <h3>What a profile in here knows</h3>
              <p className="muted small">
                Everything a synthetic profile in this party is given — and the
                absences are the point, so they are listed too.
              </p>
              <p className="small">
                Title: <strong>{ctx.watching.title}</strong> on{" "}
                {ctx.watching.platform}
              </p>
              <p className="small">
                Description: {ctx.watching.description_available ? "yes" : "not available"}
                {" · "}Transcript:{" "}
                {ctx.watching.transcript_available ? "yes" : "not available"}
                {ctx.you_have_not_seen_it && " · it has not seen the video"}
              </p>
              <p className="small">
                It can see {ctx.recent.length} recent line
                {ctx.recent.length === 1 ? "" : "s"} and the position ({ctx.position_s}s).
              </p>
              {/* Verbatim. The claim and the object are the same thing, so
                  this cannot go stale while still looking honest. */}
              <p className="muted small"><em>{ctx.instruction}</em></p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
