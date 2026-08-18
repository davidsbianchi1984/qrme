import { useEffect, useState } from "react";
import { api, getBase, InboxEvent } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// The friends list, founder first — the backend pins David Bianchi and his
// synthetic profile at positions one and two on every list, by design; the
// console finally shows it.
export function Friends({ onPlans, onVisit }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
  /** Open somebody's profile — their page, their homepage, their own
   *  friends. `Profile.tsx` calls itself "the place you land when you press
   *  their face", and until now this screen was the one list of faces that
   *  could not send anybody there: `Home` and `Profile` were both handed
   *  `visitProfile` and this was mounted without it.
   *
   *      asked     the friends picture should open their profile homepage
   *      mattered  the screen whose whole subject is friends could not
   *
   *  It matters more now than it did: every starter's homepage used to be
   *  the same blank page, so the missing link cost nothing. They carry
   *  their own pages this release. */
  onVisit: (profileId: string) => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [data, setData] = useState<Awaited<ReturnType<typeof api.friends>> | null>(null);
  const [suggested, setSuggested] = useState<{ profile_id: string; display_name: string }[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  // The finder: beta testers looking for each other by the name they know.
  const [findQ, setFindQ] = useState("");
  const [found, setFound] = useState<
    { profile_id: string; display_name: string; handle: string | null;
      avatar: string | null }[] | null>(null);

  async function findPeople() {
    if (!findQ.trim()) return;
    setBusy(true); setError(null);
    try {
      const r = await api.findPeople(findQ.trim());
      setFound(r.found);
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }
  const [inbox, setInbox] = useState<{ events: InboxEvent[]; unseen: number } | null>(null);

  function load() {
    if (!session.profileId) return;
    api.friends(session.profileId).then(setData).catch((e) => setError(e));
    api.suggestedFriends(session.profileId).then((s) => {
      setSuggested(s.suggested);
    }).catch(() => setSuggested([]));
    if (session.ownerToken) {
      api.inbox(session.profileId, session.ownerToken)
        .then(setInbox).catch(() => setInbox(null));
    }
  }
  useEffect(load, [session.profileId]);

  async function markSeen() {
    if (!session.profileId || !session.ownerToken) return;
    setBusy(true);
    try {
      await api.inboxSeen(session.profileId, session.ownerToken);
      const fresh = await api.inbox(session.profileId, session.ownerToken);
      setInbox(fresh);
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  // Saying yes to a room somebody asked you into. The invite is the inbox
  // row, so accepting does not remove it — the news that you were asked
  // stays true after you have gone.
  async function acceptRoom(roomId: string) {
    if (!session.profileId || !session.ownerToken) return;
    setBusy(true); setError(null); setNote(null);
    try {
      const room = await api.acceptRoomInvite(
        roomId, session.profileId, session.ownerToken);
      setNote(tr("frn.roomjoined", lang)
        .replace("{topic}", room.topic || tr("frn.aroom", lang)));
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  if (!session.profileId) {
    return <div className="screen">
      <p className="muted center">{tr("frn.signin", lang)}</p>
    </div>;
  }

  async function add(profileId: string) {
    setBusy(true); setError(null); setNote(null);
    try {
      await api.addFriend(session.profileId!, profileId, session.ownerToken!);
      load();
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  // Unfriending answers 200 even when there was nothing to remove — unlike
  // the comment and listing deletes, which 404. So the flag is what says
  // whether anything happened; reporting success from the status code alone
  // would tell somebody a friendship they never had has ended.
  async function remove(profileId: string, name: string) {
    setBusy(true); setError(null); setNote(null);
    try {
      const r = await api.removeFriend(session.profileId!, profileId,
                                       session.ownerToken!);
      setNote(r.removed
        ? tr("frn.removed", lang).replace("{name}", name)
        : tr("frn.nothingtoremove", lang)
            .replace("{why}", r.reason || tr("frn.notafriend", lang)));
      load();
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  const founderHandles = new Set(data?.founder_handles || []);

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("frn.title", lang)}</h2>
      </header>

      {inbox && inbox.events.length > 0 && (
        <div className="card">
          <h3>
            {tr("inbox.title", lang)}
            {inbox.unseen > 0 && (
              <span className="tag"> {inbox.unseen} {tr("inbox.new", lang)}</span>
            )}
          </h3>
          {inbox.events.map((e) => (
            <div key={e.id} className={"friend-row" + (e.seen ? "" : " unseen")}>
              <b>{e.actor_name || e.actor_id}</b>
              <span className="muted small">
                {tr(`inbox.kind.${e.kind}`, lang)}
              </span>
              {/* The half that makes it an invitation rather than a
                  notification. The accept is authorized as the guest, so
                  this row — in the guest's own inbox, under the guest's own
                  owner token — is the only place it can be pressed. */}
              {e.kind === "room_invite" && e.ref && (
                <button className="primary" disabled={busy}
                        onClick={() => acceptRoom(e.ref!)}>
                  {tr("frn.acceptroom", lang)}
                </button>
              )}
            </div>
          ))}
          {inbox.unseen > 0 && (
            <button className="chip" disabled={busy} onClick={markSeen}>
              {tr("inbox.seen", lang)}
            </button>
          )}
        </div>
      )}

      <div className="card">
        <h3>{tr("frn.find", lang)}</h3>
        <div className="row">
          <input value={findQ} placeholder={tr("frn.find.ph", lang)}
                 onChange={(e) => setFindQ(e.target.value)}
                 onKeyDown={(e) => { if (e.key === "Enter") findPeople(); }} />
          <button disabled={busy || !findQ.trim()} onClick={findPeople}>
            {tr("dsc.search", lang)}
          </button>
        </div>
        {found !== null && found.length === 0 && (
          <p className="muted small">{tr("frn.found.none", lang)}</p>
        )}
        {(found || []).map((p) => {
          const mine = (data?.friends || []).some(
            (f) => f.profile_id === p.profile_id);
          return (
            <div key={p.profile_id} className="friend-row">
              {p.avatar ? (
                <img className="friend-photo" src={getBase() + p.avatar} alt="" />
              ) : (
                <span className="friend-photo friend-initials" aria-hidden="true">
                  {p.display_name.split(/\s+/).map((w) => w[0]).join("").slice(0, 2)}
                </span>
              )}
              <button className="linkish friend-name"
                      onClick={() => onVisit(p.profile_id)}>
                {p.display_name}
              </button>
              {p.handle && <span className="muted small">@{p.handle}</span>}
              {mine ? (
                <span className="muted small">{tr("frn.already", lang)}</span>
              ) : (
                <button className="primary" disabled={busy}
                        onClick={() => add(p.profile_id)}>
                  {tr("frn.add", lang)}
                </button>
              )}
            </div>
          );
        })}
      </div>

      <div className="card">
        {(data?.friends || []).length === 0 && (
          <p className="muted center">{tr("frn.nofriends", lang)}</p>
        )}
        {(data?.friends || []).map((f, i) => {
          const isFounder = f.pinned || (f.handle != null && founderHandles.has(f.handle));
          return (
            <div key={f.profile_id} className={"friend-row" + (isFounder ? " founder" : "")}>
              <span className="friend-rank">{i + 1}</span>
              {f.avatar ? (
                <img className="friend-photo" src={getBase() + f.avatar} alt="" />
              ) : (
                <span className="friend-photo friend-initials" aria-hidden="true">
                  {f.display_name.split(/\s+/).map((w) => w[0]).join("").slice(0, 2)}
                </span>
              )}
              {/* The name is the door. A row that carries somebody's name,
                  their handle and a Remove button, and no way to look at
                  them, is a list about people you cannot visit. */}
              <button className="linkish friend-name"
                      onClick={() => onVisit(f.profile_id)}>
                {f.display_name}
              </button>
              {isFounder && (
                <span className="tag founder-tag">{tr("frn.founder", lang)}</span>
              )}
              {f.handle && <span className="muted small">@{f.handle}</span>}
              {/* Not offered on the founder's two rows. They are pinned by
                  the platform and answer 409, and the list marks them — so
                  the control is absent rather than present and refused. */}
              {!isFounder && (
                <button className="friend-x" disabled={busy}
                        aria-label={tr("frn.remove", lang)}
                        title={tr("frn.remove", lang)}
                        onClick={() => remove(f.profile_id, f.display_name)}>
                  ✕
                </button>
              )}
            </div>
          );
        })}
      </div>

      {suggested.length > 0 && (
        <div className="card">
          <h3>{tr("frn.suggested", lang)}</h3>
          {suggested.map((s) => (
            <div key={s.profile_id} className="friend-row">
              <b>{s.display_name}</b>
              <button className="primary" disabled={busy}
                      onClick={() => add(s.profile_id)}>
                {tr("frn.add", lang)}
              </button>
            </div>
          ))}
        </div>
      )}

      {note && <p className="muted small">{note}</p>}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
