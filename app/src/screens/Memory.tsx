import { useEffect, useState } from "react";
import { api, type MemoryAccount, type MemoryEntry, type Remembrance } from "../api";
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
  const [kept, setKept] = useState<Remembrance | null>(null);
  const [account, setAccount] = useState<MemoryAccount | null>(null);
  const [forgetWords, setForgetWords] = useState("");
  const [forgot, setForgot] = useState<number | null>(null);
  const [error, setError] = useState<unknown>(null);
  // Curation mode: checkboxes appear beside every turn and tapping a turn
  // opens it for rewriting — the two doors a field report asked for by
  // name: "little clear boxes you could select and a delete button", and
  // "an edit at top where we can tap into any of the conversations".
  const [curating, setCurating] = useState(false);
  const [picked, setPicked] = useState<Set<string>>(new Set());
  const [editing, setEditing] = useState<string | null>(null); // message id
  const [draft, setDraft] = useState("");

  function load() {
    if (!session.profileId || !session.ownerToken) return;
    api.memories(session.profileId, session.ownerToken)
      .then(setConvos).catch((e) => setError(e));
  }
  useEffect(load, [session.profileId]);

  async function view(interactorId: string) {
    if (!session.profileId || !session.ownerToken) return;
    setOpen(interactorId); setEntries([]); setKept(null);
    setAccount(null); setForgot(null);
    setPicked(new Set()); setEditing(null);
    try {
      const data = await api.memory(session.profileId, interactorId, session.ownerToken);
      setEntries(Array.isArray(data) ? data : data.history || []);
      setKept(await api.remembrance(session.profileId, interactorId, session.ownerToken));
      setAccount(await api.memoryAccount(session.profileId, interactorId, session.ownerToken));
    } catch (e) { setError(e); }
  }

  async function forget() {
    if (!session.profileId || !session.ownerToken || !open || !forgetWords.trim()) return;
    try {
      const out = await api.forgetMemory(
        session.profileId, open, forgetWords.trim(), session.ownerToken);
      setForgot(out.forgotten_turns); setForgetWords("");
      await view(open); setForgot(out.forgotten_turns);
      load();
    } catch (e) { setError(e); }
  }

  function pick(id: string) {
    setPicked((old) => {
      const next = new Set(old);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }

  async function strikePicked() {
    if (!session.profileId || !session.ownerToken || !open) return;
    if (picked.size === 0) return;
    if (!confirm(tr("mem.strike.confirm", lang)
                   .replace("{n}", String(picked.size)))) return;
    try {
      await api.strikeTurns(session.profileId, open, [...picked],
                            session.ownerToken);
      setPicked(new Set());
      await view(open); setCurating(true);
      load();
    } catch (e) { setError(e); }
  }

  async function saveEdit() {
    if (!session.profileId || !session.ownerToken || !open || !editing) return;
    try {
      await api.editTurn(session.profileId, open, editing, draft.trim(),
                         session.ownerToken);
      setEditing(null); setDraft("");
      await view(open); setCurating(true);
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

      {open && kept?.content && (
        // The remembrance: what the profile still carries of this person
        // from turns older than the recent transcript. Erased with the rest.
        <div className="card remembrance">
          <b>{tr("mem.kept", lang)}</b>
          <p>{kept.content}</p>
          <span className="muted small">
            {fill(tr("mem.kept.covers", lang), { n: kept.covers })}
          </span>
        </div>
      )}

      {open && account && (
        // The account: what it remembers, answered from the records — the
        // honest counts around the kept paragraph.
        <div className="card">
          <b>{tr("mem.account", lang)}</b>
          <p className="muted small">
            {fill(tr("mem.account.span", lang), {
              folded: account.folded_turns, recent: account.recent_turns,
            })}
          </p>
          {/* Forget that one thing — the scalpel beside the erase-all. */}
          <div className="row">
            <input value={forgetWords} placeholder={tr("mem.forget.ph", lang)}
                   onChange={(e) => setForgetWords(e.target.value)}
                   style={{ flex: 1 }} />
            <button className="danger" disabled={!forgetWords.trim()}
                    onClick={forget}>{tr("mem.forget", lang)}</button>
          </div>
          {forgot !== null && (
            <p className="muted small">
              {fill(tr("mem.forgot", lang), { n: forgot })}
            </p>
          )}
        </div>
      )}

      {open && entries.length > 0 && (
        // Curation controls sit at the top of the transcript, where the
        // field report asked for them.
        <div className="actions" style={{ justifyContent: "flex-end", gap: 8 }}>
          {curating && picked.size > 0 && (
            <button className="danger" onClick={strikePicked}>
              {fill(tr("mem.strike.sel", lang), { n: picked.size })}
            </button>
          )}
          <button onClick={() => {
            setCurating(!curating); setPicked(new Set()); setEditing(null);
          }}>
            {curating ? tr("mem.curate.done", lang) : tr("mem.curate", lang)}
          </button>
        </div>
      )}
      {open && (
        <div className="memory-list">
          {entries.length === 0 && (
            <div className="muted center">{tr("mem.loading", lang)}</div>
          )}
          {entries.map((e, i) => (
            <div className={"mem " + e.role} key={e.id ?? i}>
              {curating && e.id && (
                <input type="checkbox" checked={picked.has(e.id)}
                       onChange={() => pick(e.id!)}
                       aria-label={tr("mem.pick", lang)} />
              )}
              <span className="mem-role">{e.role}</span>
              {editing === e.id ? (
                <span className="mem-text" style={{ flex: 1 }}>
                  <textarea value={draft} rows={3} style={{ width: "100%" }}
                            onChange={(ev) => setDraft(ev.target.value)} />
                  <span className="actions">
                    <button className="primary" disabled={!draft.trim()}
                            onClick={saveEdit}>
                      {tr("mem.save", lang)}
                    </button>
                    <button onClick={() => { setEditing(null); setDraft(""); }}>
                      {tr("mem.cancel", lang)}
                    </button>
                  </span>
                </span>
              ) : (
                <span className="mem-text"
                      style={curating && e.id ? { cursor: "pointer" } : undefined}
                      onClick={() => {
                        if (!curating || !e.id) return;
                        setEditing(e.id); setDraft(e.content || "");
                      }}>
                  {e.content}
                  {e.edited && (
                    <span className="muted small"> {tr("mem.edited", lang)}</span>
                  )}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
