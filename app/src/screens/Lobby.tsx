import { useEffect, useState } from "react";
import { api, type HandoffMade, type HandoffPackage, type Lobby as LobbyView,
         type LobbyContext, type LobbyVocabulary,
         type Provider } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
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
  const lang = visitorLang();
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
      <h2>{tr("lby.title", lang)}</h2>
      <p className="muted small">{tr("lby.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {vocab && (
        <div className="card">
          <h3>{tr("lby.line", lang)}</h3>
          {/* The sentence the whole feature rests on. */}
          <p className="small">{vocab.fair_play}</p>
          <h4>{tr("lby.never", lang)}</h4>
          {/* All twelve, verbatim. Each closes a route somebody would
              otherwise argue for, and a summary would lose the argument
              rather than make it. */}
          {vocab.never.map((n) => (
            <p className="muted small" key={n.thing}>
              {fill(tr("lby.never.row", lang), {
                thing: <strong>{n.thing.replace(/_/g, " ")}</strong>,
                means: n.means,
              })}
            </p>
          ))}
          <h4>{tr("lby.rules", lang)}</h4>
          {vocab.rules.map((r, i) => (
            <p className="muted small" key={i}>{r}</p>
          ))}
        </div>
      )}

      <div className="card">
        <h3>{tr("lby.lobby", lang)}</h3>
        <div className="row">
          <input value={sessionId}
                 onChange={(e) => setSessionId(e.target.value)}
                 placeholder={tr("lby.session.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !sessionId.trim() || !token}
                  onClick={loadLobby}>{tr("lby.openit", lang)}</button>
        </div>

        {lobby && (
          <>
            <p className="small">
              {fill(tr("lby.counts", lang), {
                game: lobby.game, platform: lobby.platform,
                people: (lobby.people === 1
                  ? tr("lby.person", lang) : tr("lby.people", lang)
                ).replace("{n}", String(lobby.people)),
                profiles: (lobby.profiles === 1
                  ? tr("lby.profile", lang) : tr("lby.profiles", lang)
                ).replace("{n}", String(lobby.profiles)),
                agents: (lobby.agents === 1
                  ? tr("lby.agent", lang) : tr("lby.agents", lang)
                ).replace("{n}", String(lobby.agents)),
              })}
            </p>
            <p className="muted small">
              {fill(tr("lby.seatsleft", lang), {
                n: lobby.synthetic_seats_left,
                seat: lobby.synthetic_seats_left === 1
                  ? tr("lby.seat.one", lang) : tr("lby.seats", lang),
              })}
            </p>
            {lobby.members.map((m) => (
              <div key={m.member_id}>
                <p className="small">
                  {fill(tr("lby.member", lang), {
                    who: <strong>{m.callsign || m.member_id}</strong>,
                    role: m.role,
                  })}
                  {m.host && tr("lby.host", lang)}
                  <br />
                  <span className="muted">
                    {/* The server's own sentence for what this kind is. */}
                    {fill(tr("lby.isdoes", lang),
                      { is: m.is, does: m.does })}
                  </span>
                </p>
                {/* The host may remove anybody; a player may remove
                    themselves. Not offered on the host's own seat, which
                    would be a session ending itself sideways. */}
                {!m.host && (
                  <button className="chip" disabled={busy}
                          onClick={act(() => api.leaveLobby(
                            sessionId.trim(), m.member_id, token),
                            tr("lby.left.said", lang))}>
                    {tr("lby.takeseat", lang)}
                  </button>
                )}
              </div>
            ))}

            <h4>{tr("lby.seatsomebody", lang)}</h4>
            <div className="row">
              <select value={memberKind}
                      onChange={(e) => setMemberKind(e.target.value)}>
                {vocab?.kinds.map((k) => (
                  <option key={k.kind} value={k.kind}>{k.kind}</option>
                ))}
              </select>
              <input value={memberId}
                     onChange={(e) => setMemberId(e.target.value)}
                     placeholder={tr("lby.member.ph", lang)} style={{ flex: 1 }} />
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                {vocab?.seats.map((s) => (
                  <option key={s.role} value={s.role}>{s.role}</option>
                ))}
              </select>
              <input value={callsign}
                     onChange={(e) => setCallsign(e.target.value)}
                     placeholder={tr("lby.callsign.ph", lang)} style={{ width: 120 }} />
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
                      }, tr("lby.seated.said", lang))}>
                {tr("lby.seat", lang)}
              </button>
            </div>
            <p className="muted small">{tr("lby.seatrule", lang)}</p>
          </>
        )}
      </div>

      {context && (
        <div className="card">
          <h3>{tr("lby.told", lang)}</h3>
          <p className="muted small">{tr("lby.told.pitch", lang)}</p>
          {/* Verbatim, and it is long on purpose. */}
          <p className="small">{context.instruction}</p>
          <p className="muted small">
            {fill(tr("lby.here", lang), {
              n: context.people, syn: context.synthetic_here,
              maturity: context.maturity,
            })}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{tr("lby.handing", lang)}</h3>
        <p className="muted small">{tr("lby.handing.pitch", lang)}</p>
        <div className="row">
          <select value={providerId}
                  onChange={(e) => setProviderId(e.target.value)}>
            <option value="">{tr("lby.pick", lang)}</option>
            {providers.map((p) => (
              <option key={p.id} value={p.id}>{p.name} — {p.area}</option>
            ))}
          </select>
          <label className="small">
            <input type="checkbox" checked={consent}
                   onChange={(e) => setConsent(e.target.checked)} />
            {" "}{tr("lby.agree", lang)}
          </label>
          {/* Consent is a field on the request, not a UI convention: the
              route 403s without it, so an unchecked box is refused by the
              server rather than by a disabled button alone. */}
          <button disabled={busy || !providerId || !interactor}
                  onClick={act(async () => setMade(await api.handoff({
                    interactor_id: interactor, provider_id: providerId,
                    profile_id: me || undefined, consent }, interactorToken)))}>
            {tr("lby.handover", lang)}
          </button>
        </div>
        {made && (
          <>
            <p className="small">
              {fill(tr("lby.to", lang), {
                who: made.provider, area: made.area,
                link: <code>{made.token}</code>,
              })}
            </p>
            <p className="muted small">
              {made.sealed
                ? tr("lby.sealed", lang) : tr("lby.unsealed", lang)}
            </p>
            <div className="row">
              <button disabled={busy}
                      onClick={act(async () => setOpened(
                        (await api.openHandoff(made.id, made.token)).package))}>
                {tr("lby.seewhat", lang)}
              </button>
              <button disabled={busy}
                      onClick={act(async () => {
                        await api.revokeHandoff(made.id, interactorToken);
                        setMade(null); setOpened(null);
                      }, tr("lby.revoked.said", lang))}>
                {tr("lby.takeback", lang)}
              </button>
            </div>
          </>
        )}
        {opened && (
          <>
            <h4>{tr("lby.package", lang)}</h4>
            <p className="muted small">
              {opened.user} · {opened.provider_area}
              {opened.specialist && ` · via ${opened.specialist}`}
              {opened.sessions !== null && ` · ${opened.sessions} session`}
              {opened.sessions !== null && opened.sessions !== 1 && "s"}
            </p>
            {(opened.recent_exchange || []).map((m, i) => (
              <p className="small" key={i}>
                <strong>{m.role === "profile"
                  ? tr("lby.theprofile", lang) : tr("lby.you", lang)}</strong>:{" "}
                {m.content}
              </p>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
