import { useCallback, useEffect, useState } from "react";
import {
  accountApi, api, type DmMessage, type DmThread, type Homepage,
  type MailDeskProfile, type MailMessage,
} from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr, visitorLang } from "../l10n";
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
        <h2>{session.profile?.display_name
          ? fill(tr("nav.corner.of", lang), { name: session.profile.display_name })
          : tr("corner.title", lang)}</h2>
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

      <MailDesk />

      {note && <div className="muted small">{note}</div>}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}


// The operator's mailboxes: every profile this account holds — under its
// own name or seated in one of its companies — has an inbox of its own and
// works it itself (qrme/mailbox.py). This card is the review desk over all
// of them: what each held for you, approve / edit / discard from here, and
// for the profile you are signed in as, a way to hand a message in or ask
// it to write one.
function MailDesk() {
  const { session } = useSession();
  const lang = visitorLang();
  const [profiles, setProfiles] = useState<MailDeskProfile[]>([]);
  const [held, setHeld] = useState(0);
  const [transport, setTransport] = useState("console");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [said, setSaid] = useState<string | null>(null);
  const [edits, setEdits] = useState<Record<string, string>>({});
  const [inFrom, setInFrom] = useState("");
  const [inSubject, setInSubject] = useState("");
  const [inBody, setInBody] = useState("");
  const [outTo, setOutTo] = useState("");
  const [outSubject, setOutSubject] = useState("");
  const [outObjective, setOutObjective] = useState("");

  const load = useCallback(() => {
    if (session.accountId && session.accountToken) {
      accountApi.mailDesk(session.accountId, session.accountToken).then((d) => {
        setProfiles(d.profiles); setHeld(d.held); setTransport(d.outbound_transport);
      }).catch((e) => setError(e));
      return;
    }
    // No account on this session — a device signed in with an owner token
    // alone. The desk is then the one profile's own mailbox, through the
    // profile's own door.
    if (session.profileId && session.ownerToken && session.profile) {
      const pid = session.profileId;
      const name = session.profile.display_name;
      api.profileMail(pid, session.ownerToken).then((m) => {
        const mine = m.threads.reduce((n, t) => n + t.held_drafts, 0);
        setProfiles([{ profile_id: pid, display_name: name, via: "own",
                       held: mine, threads: m.threads, posture: m.posture }]);
        setHeld(mine); setTransport(m.posture.outbound_transport);
      }).catch((e) => setError(e));
    }
  }, [session.accountId, session.accountToken, session.profileId,
      session.ownerToken, session.profile]);
  useEffect(load, [load]);

  async function run(action: () => Promise<unknown>, ok?: string) {
    setBusy(true); setError(null); setSaid(null);
    try { await action(); if (ok) setSaid(ok); load(); }
    catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  function decide(owner: string, draft: MailMessage,
                  action: "approve" | "edit" | "discard") {
    const edited = action === "edit" ? edits[draft.id] : undefined;
    // The signed-in profile decides through its own door; anything else
    // the account holds goes through the desk's.
    if (owner === session.profileId && session.ownerToken) {
      void run(() => api.mailModerate(owner, draft.id, { action, edited },
                                      session.ownerToken!));
      return;
    }
    const acc = session.accountId, accTok = session.accountToken;
    if (!acc || !accTok) return;
    void run(() => accountApi.mailDeskModerate(acc, draft.id, { action, edited }, accTok));
  }

  if (!session.accountId && !session.profileId) {
    return (
      <div className="card">
        <h3>{tr("mail.desk", lang)}</h3>
        <p className="muted small">{tr("mail.desk.signin", lang)}</p>
      </div>
    );
  }

  const me = session.profileId;
  const token = session.ownerToken;

  return (
    <div className="card">
      <h3>{tr("mail.desk", lang)}{held > 0 && (
        <span className="muted small"> · {fill(tr("mail.held", lang), { n: String(held) })}</span>
      )}</h3>
      <p className="muted small">{tr("mail.desk.pitch", lang)}</p>
      {transport !== "smtp" && (
        <p className="muted small">{tr("mail.posture.staged", lang)}</p>
      )}
      {profiles.length === 0 && (
        <p className="muted small">{tr("mail.desk.none", lang)}</p>
      )}
      {profiles.map((p) => (
        <div key={p.profile_id} className="card">
          <div className="row">
            <strong>{fill(tr("nav.corner.of", lang), { name: p.display_name })}</strong>
            <span className="muted small">
              {p.posture.self_operated ? tr("mail.self", lang) : tr("mail.heldmode", lang)}
            </span>
            {p.held > 0 && (
              <span className="tag">{fill(tr("mail.held", lang), { n: String(p.held) })}</span>
            )}
          </div>
          <p className="muted small">
            {p.posture.inbox_attached
              ? tr("mail.inbox.attached", lang)
              : tr("mail.inbox.none", lang)}
          </p>
          {p.threads.length === 0 && (
            <p className="muted small">{tr("mail.none", lang)}</p>
          )}
          {p.threads.map((t) => (
            <div key={t.id} className="card">
              <div className="row">
                <strong>{t.correspondent}</strong>
                <span className="muted small">{t.subject}</span>
              </div>
              {t.messages.map((m) => (
                <div key={m.id} style={{ marginTop: 6 }}>
                  <div className="muted small">
                    {m.direction === "inbound" ? tr("mail.dir.inbound", lang) : tr("mail.dir.outbound", lang)}
                    {" · "}
                    {tr(`mail.state.${m.state}`, lang)}
                    {m.note && m.state === "draft" && (
                      <> · {fill(tr("mail.heldnote", lang), { why: m.note })}</>
                    )}
                  </div>
                  {m.state === "draft" ? (
                    <>
                      <textarea aria-label={tr("mail.edit.aria", lang)} rows={4}
                                value={edits[m.id] ?? m.body}
                                onChange={(e) => setEdits({ ...edits, [m.id]: e.target.value })} />
                      <div className="row">
                        <button disabled={busy} onClick={() => decide(p.profile_id, m, "approve")}>
                          {tr("mail.approve", lang)}
                        </button>
                        <button disabled={busy || !(edits[m.id] ?? "").trim()}
                                onClick={() => decide(p.profile_id, m, "edit")}>
                          {tr("mail.saveedit", lang)}
                        </button>
                        <button disabled={busy} onClick={() => decide(p.profile_id, m, "discard")}>
                          {tr("mail.discard", lang)}
                        </button>
                      </div>
                    </>
                  ) : (
                    <div style={{ whiteSpace: "pre-wrap" }}>{m.body}</div>
                  )}
                  {m.direction === "inbound" && me === p.profile_id && token && (
                    <button disabled={busy}
                            onClick={() => void run(() => api.mailDraft(me, m.id, token))}>
                      {tr("mail.draftreply", lang)}
                    </button>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      ))}

      {me && token && (<>
        <h4>{tr("mail.receive", lang)}</h4>
        <div className="row">
          <input placeholder={tr("mail.receive.from", lang)} value={inFrom}
                 onChange={(e) => setInFrom(e.target.value)} />
          <input placeholder={tr("mail.receive.subject", lang)} value={inSubject}
                 onChange={(e) => setInSubject(e.target.value)} />
        </div>
        <textarea placeholder={tr("mail.receive.body", lang)} rows={3} value={inBody}
                  onChange={(e) => setInBody(e.target.value)} />
        <button disabled={busy || !inFrom.trim() || !inBody.trim()}
                onClick={() => void run(async () => {
                  const r = await api.mailReceive(
                    me, { from_addr: inFrom.trim(), subject: inSubject.trim(), body: inBody.trim() },
                    token);
                  setInFrom(""); setInSubject(""); setInBody("");
                  if (r.answered_on_its_own) setSaid(tr("mail.answered", lang));
                })}>
          {tr("mail.receive.go", lang)}
        </button>

        <h4>{tr("mail.compose", lang)}</h4>
        <div className="row">
          <input placeholder={tr("mail.compose.to", lang)} value={outTo}
                 onChange={(e) => setOutTo(e.target.value)} />
          <input placeholder={tr("mail.compose.subject", lang)} value={outSubject}
                 onChange={(e) => setOutSubject(e.target.value)} />
        </div>
        <textarea placeholder={tr("mail.compose.objective", lang)} rows={2}
                  value={outObjective} onChange={(e) => setOutObjective(e.target.value)} />
        <button disabled={busy || !outTo.trim() || !outObjective.trim()}
                onClick={() => void run(async () => {
                  await api.mailCompose(
                    me, { to: outTo.trim(), subject: outSubject.trim(), objective: outObjective.trim() },
                    token);
                  setOutTo(""); setOutSubject(""); setOutObjective("");
                })}>
          {tr("mail.compose.go.profile", lang)}
        </button>
      </>)}

      {said && <div className="muted small">{said}</div>}
      <Refusal error={error} onPlans={() => undefined} variant="inline" />
    </div>
  );
}
