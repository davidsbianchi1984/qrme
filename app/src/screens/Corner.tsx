import { useCallback, useEffect, useState } from "react";
import {
  api, type DmMessage, type DmThread, type Homepage,
} from "../api";
import { Refusal } from "../Refusal";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

// Your corner of the platform: the homepage sandbox and your messages.
//
// The homepage is the old MySpace idea, kept honest by its walls: a
// headline, an about, a theme (hex colors only), links (http(s) only),
// and top friends (actual friends only). The messages are between the
// people behind profiles, friends only — and both surfaces answer to the
// switches on the Settings screen, refusing by naming the switch.
export function Corner({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();

  const [page, setPage] = useState<Homepage | null>(null);
  const [headline, setHeadline] = useState("");
  const [about, setAbout] = useState("");
  const [bg, setBg] = useState("#1a1333");
  const [accent, setAccent] = useState("#7b5cff");
  const [links, setLinks] = useState("");
  const [tops, setTops] = useState("");
  const [lookId, setLookId] = useState("");
  const [looking, setLooking] = useState<Homepage | null>(null);

  const [threads, setThreads] = useState<DmThread[]>([]);
  const [withId, setWithId] = useState("");
  const [thread, setThread] = useState<DmMessage[]>([]);
  const [draft, setDraft] = useState("");

  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  const load = useCallback(async () => {
    if (!session.profileId || !session.ownerToken) return;
    try {
      const mine = await api.homepage(session.profileId, session.ownerToken);
      setPage(mine);
      setHeadline(mine.headline); setAbout(mine.about);
      setBg(mine.theme.bg); setAccent(mine.theme.accent);
      setLinks(mine.links.map((l) => `${l.label} ${l.url}`).join("\n"));
      setTops(mine.top_friends.map((t) => t.profile_id).join(", "));
      const box = await api.dmThreads(session.profileId, session.ownerToken);
      setThreads(box.threads);
    } catch (e) { setError(e); }
  }, [session.profileId, session.ownerToken]);
  useEffect(() => { load(); }, [load]);

  async function run(op: () => Promise<void>) {
    setBusy(true); setError(null); setNote(null);
    try { await op(); } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  function save() {
    if (!session.profileId || !session.ownerToken) return;
    run(async () => {
      const parsedLinks = links.split("\n").map((s) => s.trim())
        .filter(Boolean).map((line) => {
          const ix = line.lastIndexOf(" ");
          return ix > 0
            ? { label: line.slice(0, ix), url: line.slice(ix + 1) }
            : { label: line, url: line };
        });
      const updated = await api.editHomepage(session.profileId!, {
        headline, about, theme: { bg, accent },
        links: parsedLinks,
        top_friends: tops.split(",").map((s) => s.trim()).filter(Boolean),
      }, session.ownerToken!);
      setPage(updated);
      setNote(tr("corner.saved", lang));
    });
  }

  function look() {
    run(async () => setLooking(await api.homepage(lookId.trim())));
  }

  function openThread(other: string) {
    if (!session.profileId || !session.ownerToken) return;
    setWithId(other);
    run(async () => {
      const t = await api.dmThread(session.profileId!, other,
                                   session.ownerToken!);
      setThread(t.messages);
    });
  }

  function send() {
    if (!session.profileId || !session.ownerToken || !withId) return;
    run(async () => {
      await api.sendDm(session.profileId!, withId, draft,
                       session.ownerToken!);
      setDraft("");
      const t = await api.dmThread(session.profileId!, withId,
                                   session.ownerToken!);
      setThread(t.messages);
      const box = await api.dmThreads(session.profileId!,
                                      session.ownerToken!);
      setThreads(box.threads);
    });
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("corner.title", lang)}</h2>
        <span className="muted small">{tr("corner.sub", lang)}</span>
      </header>

      <div className="card" style={page ? {
        background: page.theme.bg, borderColor: page.theme.accent,
      } : undefined}>
        <h3>{tr("corner.page", lang)}</h3>
        <p className="muted small">{tr("corner.walls", lang)}</p>
        <label>{tr("corner.headline", lang)}
          <input value={headline} onChange={(e) => setHeadline(e.target.value)} />
        </label>
        <label>{tr("corner.about", lang)}
          <textarea rows={3} value={about}
                    onChange={(e) => setAbout(e.target.value)} />
        </label>
        <div className="row">
          <label>{tr("corner.bg", lang)}
            <input value={bg} onChange={(e) => setBg(e.target.value)} />
          </label>
          <label>{tr("corner.accent", lang)}
            <input value={accent} onChange={(e) => setAccent(e.target.value)} />
          </label>
        </div>
        <label>{tr("corner.links", lang)}
          <textarea rows={2} value={links}
                    onChange={(e) => setLinks(e.target.value)} />
        </label>
        <label>{tr("corner.tops", lang)}
          <input value={tops} onChange={(e) => setTops(e.target.value)} />
        </label>
        <button className="primary" disabled={busy} onClick={save}>
          {tr("corner.save", lang)}</button>
      </div>

      <div className="card">
        <h3>{tr("corner.visit", lang)}</h3>
        <div className="row">
          <label>{tr("corner.visit_id", lang)}
            <input value={lookId} onChange={(e) => setLookId(e.target.value)} />
          </label>
          <button disabled={busy || !lookId.trim()} onClick={look}>
            {tr("corner.visit_go", lang)}</button>
        </div>
        {looking && (
          <div style={{ background: looking.theme.bg, borderRadius: 8,
                        padding: 12, borderLeft: `4px solid ${looking.theme.accent}` }}>
            <h3 style={{ color: looking.theme.accent }}>
              {looking.display_name} — {looking.headline}</h3>
            <p style={{ whiteSpace: "pre-wrap" }}>{looking.about}</p>
            <ul className="refs">
              {looking.links.map((l) => (
                <li key={l.url}><a href={l.url} target="_blank"
                                   rel="noreferrer">{l.label}</a></li>
              ))}
            </ul>
            {looking.top_friends.length > 0 && (
              <p className="muted small">
                {tr("corner.their_tops", lang)}:{" "}
                {looking.top_friends.map((t) => t.display_name).join(" · ")}
              </p>
            )}
          </div>
        )}
      </div>

      <div className="card">
        <h3>{tr("corner.messages", lang)}</h3>
        <p className="muted small">{tr("corner.friends_only", lang)}</p>
        {threads.map((t) => (
          <div key={t.other_id} className="row"
               style={{ justifyContent: "space-between" }}>
            <span>{t.other_name || t.other_id} ·{" "}
              <span className="muted small">{t.messages_count}</span></span>
            <button onClick={() => openThread(t.other_id)}>
              {tr("corner.open", lang)}</button>
          </div>
        ))}
        <div className="row">
          <label>{tr("corner.to", lang)}
            <input value={withId} onChange={(e) => setWithId(e.target.value)} />
          </label>
        </div>
        {thread.map((m) => (
          <div key={m.id} className="muted small">
            {m.sender_id === session.profileId
              ? `→ ${m.body}` : `← ${m.body}`}
          </div>
        ))}
        <div className="voice-row">
          <input value={draft} onChange={(e) => setDraft(e.target.value)}
                 onKeyDown={(e) => e.key === "Enter" && send()} />
          <button disabled={busy || !draft.trim() || !withId.trim()}
                  onClick={send}>{tr("corner.send", lang)}</button>
        </div>
      </div>

      {note && <div className="muted small">{note}</div>}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
