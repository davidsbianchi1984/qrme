import { useEffect, useState } from "react";
import { api, type Matter, type MatterQueue } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * Somebody's matter, from saying it to seeing what happened to it.
 *
 * The support door the agent's remit has needed since that remit went into
 * `privileges.py` as prose: something wrong with the app, with your profiles,
 * or with the platform, raised here and answerable afterwards.
 *
 * Four things this screen will not smooth over:
 *
 * - **the claim is shown once, and said to be shown once.** A matter raised
 *   without an account is reachable by one string and nothing else, and a
 *   surface that displayed it as decoration would be handing somebody the only
 *   key to their own complaint without saying so;
 * - **`answered` is drawn as a question, not as a conclusion.** The backend
 *   deliberately refuses to let the help box settle anything, and a screen
 *   that rendered "answered" as a tick would put the closure back that the
 *   server took out. It reads *an answer is waiting on you*, with **That was
 *   it** and **That was not it** side by side and neither preselected;
 * - **`offered` is labelled as not being an answer.** When help did not
 *   recognise the question it still says something — a model's sentence, or
 *   the fallback naming what it covers. It is drawn under a line that says so;
 * - **the standings and the subjects are the server's closed sets**, said here
 *   in the reader's language. Nothing on this screen composes a sentence about
 *   a matter's state, because ten languages of that would be ten chances to
 *   disagree with the backend about what `with_a_person` means.
 */
export function Matters() {
  const { session } = useSession();
  const token = session.ownerToken || "";
  const lang = visitorLang();
  // Typed here rather than held in the session, the same way the
  // accessibility reports take it: whoever stands for the deployment is not
  // whoever is signed in on this machine, and storing it would blur the two.
  const [reviewer, setReviewer] = useState("");

  const [trouble, setTrouble] = useState("");
  const [concerns, setConcerns] = useState("app");
  const [raised, setRaised] = useState<Matter | null>(null);
  const [claim, setClaim] = useState("");
  const [mine, setMine] = useState<Matter[]>([]);
  const [queue, setQueue] = useState<MatterQueue | null>(null);
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");

  async function refresh() {
    try {
      setMine((await api.myMatters(token || undefined)).my_matters);
    } catch { /* an unsigned-in reader has no list, and that is not an error */ }
    if (reviewer) {
      try { setQueue(await api.matterQueue(reviewer)); } catch { setQueue(null); }
    }
  }

  useEffect(() => { void refresh(); }, [token, reviewer]);

  async function send() {
    setError("");
    try {
      const m = await api.raiseMatter({ trouble, concerns },
                                      token || undefined);
      setRaised(m);
      // Held in component state and nowhere else: writing it to storage would
      // make a durable copy of the one thing the backend deliberately does
      // not keep.
      setClaim(m.claim || "");
      setTrouble("");
      await refresh();
    } catch (e) { setError(String(e)); }
  }

  const opts = { ...(token ? { token } : {}), ...(claim ? { claim } : {}) };

  async function settle(id: string, helped: boolean) {
    setError("");
    try {
      const said = helped ? (raised?.answer || answer) : answer;
      setRaised(await api.settleMatter(id, { answer: said, helped }, opts));
      setAnswer("");
      await refresh();
    } catch (e) { setError(String(e)); }
  }

  async function reject(id: string) {
    setError("");
    try {
      setRaised(await api.rejectMatterAnswer(id, opts));
      await refresh();
    } catch (e) { setError(String(e)); }
  }

  async function take(id: string) {
    try {
      await api.takeMatter(id, reviewer);
      await api.recordMatterStep(id, { did: "handed_to_a_person" }, reviewer);
      // Read it back the way its raiser will see it rather than the way the
      // queue does — the queue is the reviewer's view of somebody else's
      // matter, and this pane is drawing the raiser's.
      if (claim) setRaised(await api.matter(id, { claim }));
      await refresh();
    } catch (e) { setError(String(e)); }
  }

  const standing = (m: Matter) => tr(`matter.standing.${m.standing}`, lang);

  return (
    <div className="screen">
      <h2>{tr("matter.title", lang)}</h2>
      <p className="sub">{tr("matter.sub", lang)}</p>

      <div className="card">
        <label>
          {tr("matter.concerns.app", lang)}
          <select value={concerns} onChange={(e) => setConcerns(e.target.value)}>
            <option value="app">{tr("matter.concerns.app", lang)}</option>
            <option value="profiles">{tr("matter.concerns.profiles", lang)}</option>
            <option value="platform">{tr("matter.concerns.platform", lang)}</option>
          </select>
        </label>
        <textarea value={trouble} rows={3}
                  onChange={(e) => setTrouble(e.target.value)} />
        <button onClick={() => void send()} disabled={!trouble.trim()}>
          {tr("matter.send", lang)}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {claim && (
        <p className="claim">
          <strong>{tr("matter.claim.keep", lang)}</strong>
          <code>{claim}</code>
        </p>
      )}

      {raised && (
        <div className="card">
          <p>{standing(raised)}</p>
          {raised.answer && <blockquote>{raised.answer}</blockquote>}
          {raised.offered && (
            <>
              <p className="muted">{tr("matter.offered", lang)}</p>
              <blockquote className="muted">{raised.offered}</blockquote>
            </>
          )}
          {raised.standing === "answered" && (
            <div className="row">
              <button onClick={() => void settle(raised.id, true)}>
                {tr("matter.that_was_it", lang)}
              </button>
              <button onClick={() => void reject(raised.id)}>
                {tr("matter.not_it", lang)}
              </button>
            </div>
          )}
          {raised.standing !== "settled" && (
            <div className="row">
              <input value={answer} onChange={(e) => setAnswer(e.target.value)} />
              <button onClick={() => void settle(raised.id, false)}
                      disabled={!answer.trim()}>
                {tr("matter.settle", lang)}
              </button>
            </div>
          )}
          <ul>
            {raised.trail.map((s) => (
              <li key={s.stepped_at + s.did}>{s.did} — {s.stepped_at}</li>
            ))}
          </ul>
        </div>
      )}

      <h3>{tr("matter.title", lang)}</h3>
      {mine.length === 0 && <p className="muted">{tr("matter.empty", lang)}</p>}
      <ul>
        {mine.map((m) => (
          <li key={m.id}>
            <span>{tr(`matter.concerns.${m.concern}`, lang)}</span>
            {" — "}
            <span>{m.trouble}</span>
            {" — "}
            <em>{standing(m)}</em>
          </li>
        ))}
      </ul>

      <div className="card">
        <input type="password" value={reviewer} placeholder={tr("acc.review.token", lang)}
               onChange={(e) => setReviewer(e.target.value)} />
      </div>

      {reviewer && queue && (
        <>
          <h3>{tr("matter.queue", lang)}</h3>
          {queue.unsettled.length === 0 && (
            <p className="muted">{tr("matter.empty", lang)}</p>
          )}
          <ul>
            {queue.unsettled.map((m) => (
              <li key={m.id}>
                <span>{m.trouble}</span>{" — "}<em>{standing(m)}</em>
                {m.standing !== "with_a_person" && (
                  <button onClick={() => void take(m.id)}>
                    {tr("matter.take", lang)}
                  </button>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
