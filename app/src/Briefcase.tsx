import { useEffect, useState } from "react";
import { api, type BriefcaseItem } from "./api";
import { fill, t as tr, visitorLang } from "./l10n";

// What you hand a profile, on whichever surface you are talking to it.
//
// ## The finding
//
// The briefcase shipped with a door on `Profile.tsx` — somebody else's
// homepage — and no door on `Chat.tsx`, which is where you talk to your
// *own* synthetic profile. So a person could hand a document to a starter
// they had just met and could not hand one to the profile built from their
// own life, which is the profile most likely to need it.
//
//     asked     does the feature have a door
//     mattered  does it have one on every surface a conversation happens on
//
// The same shape as the odd-client-out defect, one level up: the doorless
// guard counts a route as reachable if *any* console file reaches it, so one
// screen was enough to satisfy it and the second screen's absence was
// invisible. A guard cannot see a screen that was never written.
//
// ## Why a component rather than a second copy
//
// Pasting the panel into the other screen would have closed today's gap and
// set up tomorrow's: two copies of a thing drift, and the drift is silent
// because both sides still work. One component, two call sites — and the
// next surface that needs it gets the finished thing rather than a
// re-implementation.
//
// It is deliberately told who is talking to whom rather than reading a
// session: the pair is the whole scope of a briefcase, and a component that
// looked it up itself could not be used for a conversation between two
// parties it was not expecting.
/** Why a document could not be read, in the reader's word for it, as a
 *  sentence in this person's language.
 *
 *  Branches with the key written out at each `tr` rather than a table of key
 *  strings or a `prf.bc.why.${key}` template. Both of those are invisible to
 *  the lookup scanner — the guard that proves no translated string is going
 *  unread sees a literal inside a `tr` call and nothing else — and this
 *  console has now made that mistake in both of its shapes.
 *
 *  `null` for a key it does not recognise, so a reader that learns a fourth
 *  kind of unreadable puts nothing under somebody's filing rather than a
 *  missing-translation placeholder. */
function whySays(key: string | null | undefined, lang: string): string | null {
  if (key === "scanned") return tr("prf.bc.why.scanned", lang);
  if (key === "locked") return tr("prf.bc.why.locked", lang);
  if (key === "unmapped") return tr("prf.bc.why.unmapped", lang);
  return null;
}

export function Briefcase({ profileId, interactorId, name, onError }: {
  /** Whose conversation this is — your own profile or somebody else's. */
  profileId: string;
  /** Who is handing things over. Not read from the session: see above. */
  interactorId: string;
  /** What to call the profile in the sentences. */
  name: string;
  /** Errors go to the host screen's own refusal surface rather than to a
   *  second one drawn in here, so a person reads refusals in one place. */
  onError: (e: unknown) => void;
}) {
  const lang = visitorLang();
  const [carried, setCarried] = useState<BriefcaseItem[]>([]);
  const [offline, setOffline] = useState(false);
  const [handUrl, setHandUrl] = useState("");
  const [handNote, setHandNote] = useState("");
  const [opened, setOpened] = useState<string | null>(null);
  const [takenText, setTakenText] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    // Cleared first: walking from one conversation to the next must not show
    // the last one's papers under somebody else's name, even for a frame.
    setCarried([]); setHandUrl(""); setHandNote("");
    setOpened(null); setTakenText("");
    api.briefcase(profileId, interactorId)
      .then((r) => { setCarried(r.items); setOffline(r.offline); })
      .catch(() => setCarried([]));
  }, [profileId, interactorId]);

  async function refresh() {
    try {
      const held = await api.briefcase(profileId, interactorId);
      setCarried(held.items);
      setOffline(held.offline);
    } catch { setCarried([]); }
  }

  async function run(op: () => Promise<void>) {
    setBusy(true);
    try { await op(); } catch (e) { onError(e); }
    finally { setBusy(false); }
  }

  return (
    <div className="pp-briefcase">
      <div className="tile-label">{tr("prf.bc.heading", lang)}</div>
      <p className="muted small">{fill(tr("prf.bc.why", lang), { name })}</p>
      <div className="pp-bc-add">
        <input type="file" disabled={busy}
               aria-label={tr("prf.bc.file", lang)}
               onChange={(e) => {
                 const file = e.target.files?.[0];
                 e.target.value = "";
                 if (file) void run(async () => {
                   await api.importFile(profileId, interactorId, file,
                                        handNote.trim());
                   setHandNote("");
                   await refresh();
                 });
               }} />
        <input type="url" value={handUrl} disabled={busy || offline}
               placeholder={tr("prf.bc.linkhint", lang)}
               aria-label={tr("prf.bc.linkhint", lang)}
               onChange={(e) => setHandUrl(e.target.value)}
               onKeyDown={(e) => {
                 if (e.key === "Enter") {
                   e.preventDefault();
                   if (!busy && handUrl.trim()) void handLink();
                 }
               }} />
        <input type="text" value={handNote} disabled={busy}
               placeholder={tr("prf.bc.notehint", lang)}
               aria-label={tr("prf.bc.notehint", lang)}
               onChange={(e) => setHandNote(e.target.value)} />
        <button disabled={busy || !handUrl.trim() || offline}
                onClick={handLink}>
          {tr("prf.bc.import", lang)}
        </button>
      </div>
      {offline && <p className="muted small">{tr("prf.bc.offline", lang)}</p>}
      {carried.length === 0 ? (
        <p className="muted small">{tr("prf.bc.empty", lang)}</p>
      ) : (
        <ul className="pp-bc-list">
          {carried.map((item) => (
            <li key={item.id} className="pp-bc-row">
              <div className="pp-bc-head">
                <strong>{item.title}</strong>
                <span className="chip small">{item.kind}</span>
              </div>
              <p className="muted small">
                {item.read
                  // A prefix, said as one. "read once — 20,000 characters"
                  // for a 70,000-character filing is the KEPT length wearing
                  // the document's name, and the person who uploaded it has
                  // no way to tell the two apart.
                  ? (item.full_chars
                      ? fill(tr("prf.bc.part", lang), {
                          chars: item.chars.toLocaleString(),
                          whole: item.full_chars.toLocaleString(),
                          digest: String(item.digest_chars) })
                      : fill(tr("prf.bc.read", lang), {
                          chars: String(item.chars),
                          digest: String(item.digest_chars) }))
                  : fill(tr("prf.bc.unread", lang), { name })}
              </p>
              {/* And what to do about it. A number alone tells somebody
                  their filing was cut and leaves them there; the next move
                  is to paste the part that matters. */}
              {item.read && item.full_chars ? (
                <p className="muted small">{tr("prf.bc.part.why", lang)}</p>
              ) : null}
              {/* And WHY, where the reader knows. "Not opened" is true of a
                  scan, a locked file and a font this reader cannot follow,
                  and only one of those is something the person can act on —
                  a different export, a password, or nothing. Four field
                  reports arrived without this line. */}
              {!item.read && whySays(item.unread_why, lang) && (
                <p className="muted small">{whySays(item.unread_why, lang)}</p>
              )}
              <div className="pp-buttons">
                {item.read && (
                  <button className="chip small" disabled={busy}
                          onClick={() => showTaken(item.id)}>
                    {opened === item.id ? tr("prf.bc.hide", lang)
                                        : tr("prf.bc.show", lang)}
                  </button>
                )}
                <button className="chip small" disabled={busy}
                        onClick={() => void takeBack(item.id)}>
                  {tr("prf.bc.remove", lang)}
                </button>
              </div>
              {opened === item.id && (
                <p className="small pp-bc-text">{takenText}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );

  function handLink() {
    if (!handUrl.trim()) return;
    void run(async () => {
      await api.importLink(profileId, interactorId, handUrl.trim(),
                           handNote.trim());
      setHandUrl(""); setHandNote("");
      await refresh();
    });
  }

  // What the profile actually took from a file is readable, because "it read
  // your document" is a claim somebody is entitled to check.
  function showTaken(itemId: string) {
    if (opened === itemId) { setOpened(null); setTakenText(""); return; }
    void run(async () => {
      const one = await api.briefcaseItem(profileId, interactorId, itemId);
      setOpened(itemId);
      setTakenText(one.text || one.digest);
    });
  }

  async function takeBack(itemId: string) {
    await run(async () => {
      await api.forgetImport(profileId, interactorId, itemId);
      if (opened === itemId) { setOpened(null); setTakenText(""); }
      await refresh();
    });
  }
}
