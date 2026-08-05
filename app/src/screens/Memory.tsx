import { useEffect, useState } from "react";
import { api, type MemoryEntry } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// The vault, with real names: one row per remembered conversation — the
// profile's name and the person's name, never "profile" and "interactor" —
// and each row individually erasable. Ids are plumbing; names are memory.
export function Memory({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [convos, setConvos] = useState<Awaited<ReturnType<typeof api.memories>>>([]);
  const [open, setOpen] = useState<string | null>(null);   // interactor_id
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const [error, setError] = useState<unknown>(null);

  function load() {
    if (!session.profileId || !session.ownerToken) return;
    api.memories(session.profileId, session.ownerToken)
      .then(setConvos).catch((e) => setError(e));
  }
  useEffect(load, [session.profileId]);

  async function view(interactorId: string) {
    if (!session.profileId || !session.ownerToken) return;
    setOpen(interactorId); setEntries([]);
    try {
      const data = await api.memory(session.profileId, interactorId, session.ownerToken);
      setEntries(Array.isArray(data) ? data : data.history || []);
    } catch (e) { setError(e); }
  }

  async function eraseAll() {
    if (!session.profileId || !session.ownerToken || convos.length === 0) return;
    if (!confirm(tr("mem.confirmall", lang)
                   .replace("{n}", String(convos.length)))) return;
    try {
      for (const c of convos) {
        await api.clearMemory(session.profileId, c.interactor_id, session.ownerToken);
      }
      setOpen(null); setEntries([]);
      load();
    } catch (e) { setError(e); }
  }

  async function erase(interactorId: string, name: string) {
    if (!session.profileId || !session.ownerToken) return;
    if (!confirm(tr("mem.confirmone", lang).replace("{name}", name))) return;
    try {
      await api.clearMemory(session.profileId, interactorId, session.ownerToken);
      if (open === interactorId) { setOpen(null); setEntries([]); }
      load();
    } catch (e) { setError(e); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("mem.title", lang)}</h2>
        <span className="muted small">{tr("mem.pitch", lang)}</span>
      </header>

      <Refusal error={error} onPlans={onPlans} variant="inline" />

      <div className="card">
        {convos.length > 0 && (
          <div className="actions" style={{ justifyContent: "flex-end", marginBottom: 8 }}>
            <button className="danger" onClick={eraseAll}>
              {tr("mem.eraseall", lang)}
            </button>
          </div>
        )}
        {convos.length === 0 && (
          <p className="muted center">{tr("mem.nomemories", lang)}</p>
        )}
        {convos.map((c) => (
          <div key={c.interactor_id} className="convo-row">
            {/* Two sentences with the names as holes, not four fragments
                stitched by JSX: "with" sits between the names in English
                and after both of them in Japanese. */}
            <div className="convo-names">
              {fill(tr("mem.with", lang), {
                profile: <b>{c.profile_name}</b>,
                person: <b>{c.interactor_name}</b>,
              })}
              <span className="muted small">
                {" "}
                {fill(tr("mem.turns", lang), {
                  n: c.turns,
                  when: new Date(c.last_at).toLocaleDateString(),
                })}
              </span>
            </div>
            <div className="actions">
              <button onClick={() => view(c.interactor_id)}>
                {open === c.interactor_id
                  ? tr("mem.viewing", lang) : tr("mem.view", lang)}
              </button>
              <button className="danger" onClick={() => erase(c.interactor_id, c.interactor_name)}>
                {tr("mem.erasethis", lang)}
              </button>
            </div>
          </div>
        ))}
      </div>

      {open && (
        <div className="memory-list">
          {entries.length === 0 && (
            <div className="muted center">{tr("mem.loading", lang)}</div>
          )}
          {entries.map((e, i) => (
            <div className={"mem " + e.role} key={i}>
              <span className="mem-role">{e.role}</span>
              <span className="mem-text">{e.content}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
