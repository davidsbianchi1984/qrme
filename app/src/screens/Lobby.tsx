import { useEffect, useState } from "react";
import { api, type HandoffMade, type HandoffPackage, type Lobby as LobbyView,
         type LobbyContext, type LobbyVocabulary,
         type Provider } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * Who is in the game with you, and handing a conversation on.
 *
 * The lobby's entire design is one sentence it publishes about itself:
 * **everything in this lobby observes and talks; nothing in it plays.** The
 * `never` list spells that out a dozen ways, and each entry closes a route
 * somebody would otherwise argue for — its own console, a second controller on
 * yours, a Bluetooth pad paired to it, a capture card feeding it the picture.
 * The console renders all of them verbatim. "No cheating" is not the same
 * statement, and shortening an argument to a slogan is how the argument gets
 * lost.
 *
 * The context card is the uncomfortable one, and it is here on purpose: it is
 * what a synthetic member is *told* about its own position, including that
 * some of the others are synthetic too. A model that believes every callsign
 * is a person addresses them as people, and a lobby that reads as five friends
 * when it is one player and four generated voices is precisely the impression
 * this product exists to prevent. Showing the owner that instruction is how
 * they can check it.
 *
 * The handoff is the **lighter sibling of a referral**, and the pair is worth
 * seeing together:
 *
 * | | referral | handoff |
 * |---|---|---|
 * | authorised by | a device signature over the bytes | explicit consent |
 * | lifetime | one open, ever | until revoked |
 * | on revoke | — | the package is purged, not just hidden |
 *
 * Neither is a substitute for the other, and a screen that offered only the
 * heavier one would push people to skip it.
 */
export function Lobby({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const me = session.profileId || "";
  const token = session.ownerToken || "";
  const interactor = session.interactorId || "";
  const interactorToken = session.interactorToken || token;

  const [vocab, setVocab] = useState<LobbyVocabulary | null>(null);
  const [sessionId, setSessionId] = useState("");
  const [lobby, setLobby] = useState<LobbyView | null>(null);
  const [context, setContext] = useState<LobbyContext | null>(null);

  const [memberKind, setMemberKind] = useState("profile");
  const [memberId, setMemberId] = useState("");
  const [role, setRole] = useState("companion");
  const [callsign, setCallsign] = useState("");

  const [providers, setProviders] = useState<Provider[]>([]);
  const [providerId, setProviderId] = useState("");
  const [consent, setConsent] = useState(false);
  const [made, setMade] = useState<HandoffMade | null>(null);
  const [opened, setOpened] = useState<HandoffPackage | null>(null);

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fail = (e: unknown) => setError(e);

  useEffect(() => {
    api.lobbyVocabulary().then(setVocab).catch(fail);
    api.providers().then(setProviders).catch(() => setProviders([]));
  }, []);

  function loadLobby() {
    if (!sessionId.trim() || !token) return;
    api.lobby(sessionId.trim(), token).then(setLobby).catch(() => setLobby(null));
    api.lobbyContext(sessionId.trim(), token).then(setContext)
      .catch(() => setContext(null));
  }

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); loadLobby(); }
    catch (e) { fail(e); } finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>Who is in the game with you</h2>
      <p className="muted small">
        And, below, how a conversation gets handed to somebody local.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {vocab && (
        <div className="card">
          <h3>The line</h3>
          {/* The sentence the whole feature rests on. */}
          <p className="small">{vocab.fair_play}</p>
          <h4>What nothing here will do</h4>
          {/* All twelve, verbatim. Each closes a route somebody would
              otherwise argue for, and a summary would lose the argument
              rather than make it. */}
          {vocab.never.map((n) => (
            <p className="muted small" key={n.thing}>
              <strong>{n.thing.replace(/_/g, " ")}</strong> — {n.means}
            </p>
          ))}
          <h4>The rules of the room</h4>
          {vocab.rules.map((r, i) => (
            <p className="muted small" key={i}>{r}</p>
          ))}
        </div>
      )}

      <div className="card">
        <h3>A lobby</h3>
        <div className="row">
          <input value={sessionId}
                 onChange={(e) => setSessionId(e.target.value)}
                 placeholder="a gaming session id" style={{ flex: 1 }} />
          <button disabled={busy || !sessionId.trim() || !token}
                  onClick={loadLobby}>Open it</button>
        </div>

        {lobby && (
          <>
            <p className="small">
              {lobby.game} on {lobby.platform} — {lobby.people}{" "}
              {lobby.people === 1 ? "person" : "people"}, {lobby.profiles}{" "}
              {lobby.profiles === 1 ? "profile" : "profiles"}, {lobby.agents}{" "}
              {lobby.agents === 1 ? "agent" : "agents"}.
            </p>
            <p className="muted small">
              {lobby.synthetic_seats_left} synthetic{" "}
              {lobby.synthetic_seats_left === 1 ? "seat" : "seats"} left.
              Everyone in a match is owed the knowledge of who is synthetic in
              it, so this list says so per member rather than in a footnote.
            </p>
            {lobby.members.map((m) => (
              <div key={m.member_id}>
                <p className="small">
                  <strong>{m.callsign || m.member_id}</strong> — {m.role}
                  {m.host && " · host"}
                  <br />
                  <span className="muted">
                    {/* The server's own sentence for what this kind is. */}
                    {m.is} · {m.does}
                  </span>
                </p>
                {/* The host may remove anybody; a player may remove
                    themselves. Not offered on the host's own seat, which
                    would be a session ending itself sideways. */}
                {!m.host && (
                  <button className="chip" disabled={busy}
                          onClick={act(() => api.leaveLobby(
                            sessionId.trim(), m.member_id, token),
                            "Out of the lobby.")}>
                    take this seat back
                  </button>
                )}
              </div>
            ))}

            <h4>Seat somebody</h4>
            <div className="row">
              <select value={memberKind}
                      onChange={(e) => setMemberKind(e.target.value)}>
                {vocab?.kinds.map((k) => (
                  <option key={k.kind} value={k.kind}>{k.kind}</option>
                ))}
              </select>
              <input value={memberId}
                     onChange={(e) => setMemberId(e.target.value)}
                     placeholder="the member's id" style={{ flex: 1 }} />
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                {vocab?.seats.map((s) => (
                  <option key={s.role} value={s.role}>{s.role}</option>
                ))}
              </select>
              <input value={callsign}
                     onChange={(e) => setCallsign(e.target.value)}
                     placeholder="callsign" style={{ width: 120 }} />
              {/* `member_kind`, not `kind` — the read calls it one thing and
                  the write another, which is the mistake this binding was
                  written to stop repeating. */}
              <button disabled={busy || !memberId.trim()}
                      onClick={act(async () => {
                        await api.takeSeat(sessionId.trim(), {
                          member_kind: memberKind, member_id: memberId.trim(),
                          role, callsign: callsign.trim() || undefined },
                          token);
                        setMemberId(""); setCallsign("");
                      }, "Seated.")}>Seat</button>
            </div>
            <p className="muted small">
              A real person seats only themselves — an id in a request body is
              a claim, and the route checks it against the token. Somebody
              else's profile is a two-party agreement and lives in the lent-
              skills routes, which ask both sides.
            </p>
          </>
        )}
      </div>

      {context && (
        <div className="card">
          <h3>What a synthetic member is told</h3>
          <p className="muted small">
            Shown to you because it is the only way to check it. It says
            openly that some of the others here are synthetic too — a model
            that believes every callsign is a person will talk to them as
            people, and a lobby that reads as friends when it is one player
            and several generated voices is the impression this product
            exists to prevent.
          </p>
          {/* Verbatim, and it is long on purpose. */}
          <p className="small">{context.instruction}</p>
          <p className="muted small">
            {context.people} here{context.people === 1 ? "" : ""} ·{" "}
            {context.synthetic_here} synthetic · maturity {context.maturity}
          </p>
        </div>
      )}

      <div className="card">
        <h3>Handing it to somebody local</h3>
        <p className="muted small">
          The lighter of the two ways to pass a conversation on. A referral is
          signed with your device and opens once; this one is consented and
          revocable — and revoking purges the package rather than hiding it.
        </p>
        <div className="row">
          <select value={providerId}
                  onChange={(e) => setProviderId(e.target.value)}>
            <option value="">pick somebody</option>
            {providers.map((p) => (
              <option key={p.id} value={p.id}>{p.name} — {p.area}</option>
            ))}
          </select>
          <label className="small">
            <input type="checkbox" checked={consent}
                   onChange={(e) => setConsent(e.target.checked)} />
            {" "}I agree to send this
          </label>
          {/* Consent is a field on the request, not a UI convention: the
              route 403s without it, so an unchecked box is refused by the
              server rather than by a disabled button alone. */}
          <button disabled={busy || !providerId || !interactor}
                  onClick={act(async () => setMade(await api.handoff({
                    interactor_id: interactor, provider_id: providerId,
                    profile_id: me || undefined, consent }, interactorToken)))}>
            Hand it over
          </button>
        </div>
        {made && (
          <>
            <p className="small">
              To {made.provider} — {made.area}. Their link:{" "}
              <code>{made.token}</code>
            </p>
            <p className="muted small">
              {made.sealed
                ? "The package is sealed in the vault."
                : "No vault on this deployment, so the package sits in this "
                  + "platform's database until you revoke it."}
            </p>
            <div className="row">
              <button disabled={busy}
                      onClick={act(async () => setOpened(
                        (await api.openHandoff(made.id, made.token)).package))}>
                See what they will see
              </button>
              <button disabled={busy}
                      onClick={act(async () => {
                        await api.revokeHandoff(made.id, interactorToken);
                        setMade(null); setOpened(null);
                      }, "Revoked, and the package purged.")}>
                Take it back
              </button>
            </div>
          </>
        )}
        {opened && (
          <>
            <h4>The package</h4>
            <p className="muted small">
              {opened.user} · {opened.provider_area}
              {opened.specialist && ` · via ${opened.specialist}`}
              {opened.sessions !== null && ` · ${opened.sessions} session`}
              {opened.sessions !== null && opened.sessions !== 1 && "s"}
            </p>
            {(opened.recent_exchange || []).map((m, i) => (
              <p className="small" key={i}>
                <strong>{m.role === "profile" ? "the profile" : "you"}</strong>:{" "}
                {m.content}
              </p>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
