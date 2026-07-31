import { useEffect, useState } from "react";
import { api } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// The friends list, founder first — the backend pins David Bianchi and his
// synthetic profile at positions one and two on every list, by design; the
// console finally shows it.
export function Friends({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const [data, setData] = useState<Awaited<ReturnType<typeof api.friends>> | null>(null);
  const [suggested, setSuggested] = useState<{ profile_id: string; display_name: string }[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);

  function load() {
    if (!session.profileId) return;
    api.friends(session.profileId).then(setData).catch((e) => setError(e));
    api.suggestedFriends(session.profileId).then((s) => {
      const list = Array.isArray(s) ? s : (s.suggestions || []);
      setSuggested(list as { profile_id: string; display_name: string }[]);
    }).catch(() => setSuggested([]));
  }
  useEffect(load, [session.profileId]);

  if (!session.profileId) return <div className="screen"><p className="muted center">Sign in first.</p></div>;

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
      setNote(r.removed ? `${name} removed.`
                        : `Nothing to remove — ${r.reason || "not a friend"}.`);
      load();
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  const founderHandles = new Set(data?.founder_handles || []);

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Friends</h2>
      </header>

      <div className="card">
        {(data?.friends || []).length === 0 && (
          <p className="muted center">Loading, or no friends yet — add friends from Discover.</p>
        )}
        {(data?.friends || []).map((f, i) => {
          const isFounder = f.pinned || (f.handle != null && founderHandles.has(f.handle));
          return (
            <div key={f.profile_id} className={"friend-row" + (isFounder ? " founder" : "")}>
              <span className="friend-rank">{i + 1}</span>
              <b>{f.display_name}</b>
              {isFounder && <span className="tag founder-tag">founder</span>}
              {f.handle && <span className="muted small">@{f.handle}</span>}
              {/* Not offered on the founder's two rows. They are pinned by
                  the platform and answer 409, and the list marks them — so
                  the control is absent rather than present and refused. */}
              {!isFounder && (
                <button className="chip" disabled={busy}
                        onClick={() => remove(f.profile_id, f.display_name)}>
                  remove
                </button>
              )}
            </div>
          );
        })}
      </div>

      {suggested.length > 0 && (
        <div className="card">
          <h3>Suggested</h3>
          {suggested.map((s) => (
            <div key={s.profile_id} className="friend-row">
              <b>{s.display_name}</b>
              <button className="primary" disabled={busy} onClick={() => add(s.profile_id)}>Add</button>
            </div>
          ))}
        </div>
      )}

      {note && <p className="muted small">{note}</p>}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
