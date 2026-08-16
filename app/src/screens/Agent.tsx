import { useEffect, useState } from "react";
import { AgentTalk } from "../AgentTalk";
import { api, type AgentTurn } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The Agent — the collaborator, with its own front door.
 *
 * The agent that can rebuild your page and write your widgets has existed
 * since the Studio shipped, and the only way to reach it was to open the
 * widget workshop first. So the person who wanted to say *make my page say
 * what I actually do* had to go somewhere about code to find it.
 *
 *     asked     can an agent edit this person's app
 *     mattered  can the person find the agent
 *
 * ## It says what it can touch before it is asked to touch anything
 *
 * `authoring.TOOLS` is a written list — eleven of them today — and the
 * backend renders it into sentences a person can read rather than tool names
 * a developer would. That roster is on this screen and open by default,
 * because an agent whose reach you discover by watching what it does is one
 * you have to supervise instead of instruct.
 *
 * ## What it cannot do yet, said here rather than discovered
 *
 * Eleven tools is your page, your homepage, your friends list and your
 * widgets — not the marketplace, not rooms, not the wall. A screen that
 * implies a general assistant and then refuses two thirds of what is asked
 * of it teaches people to stop asking, so the boundary is drawn on the screen
 * in the roster, in the words the backend itself uses.
 */
export function Agent({ onPlans, onStudio }: {
  onPlans: () => void;
  /** Where the widgets it writes actually live. The agent can build one from
   *  here; running and editing it is the Studio's job, and a person who has
   *  just been told a widget was written should be one press from it. */
  onStudio: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();

  const [reach, setReach] = useState<
    { can_touch: string[]; available: boolean } | null>(null);
  const [showsReach, setShowsReach] = useState(true);
  const [ask, setAsk] = useState("");
  const [asking, setAsking] = useState(false);
  // The conversation is this screen's, and it is not written down anywhere:
  // leaving the tab is the whole of forgetting it, the same bargain the
  // Studio's own agent makes.
  const [talk, setTalk] = useState<{ role: string; content: string }[]>([]);
  const [did, setDid] = useState<AgentTurn | null>(null);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    api.studioAgent().then(setReach).catch(() => setReach(null));
  }, []);

  async function send() {
    if (!session.profileId || !session.ownerToken) return;
    const said = ask;
    setAsking(true); setError(null);
    try {
      const turn = await api.authoringTurn(
        session.profileId, said, talk, session.ownerToken);
      setDid(turn);
      setTalk([...talk, { role: "user", content: said },
               { role: "assistant", content: turn.reply }]);
      setAsk("");
      // What it may have changed is somebody's own page, so the roster is
      // re-read rather than assumed — a tool that stopped being available
      // mid-conversation should stop being offered.
      api.studioAgent().then(setReach).catch(() => undefined);
    } catch (e) { setError(e); }
    finally { setAsking(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("agent.title", lang)}</h2>
      </header>
      {/* The mark, at a size where it is the artwork rather than a smudge.
          The tab carries the same picture at icon size; here it has room. */}
      <img className="agent-mark" src="agent.png" alt="" />
      <p className="muted small">{tr("agent.pitch", lang)}</p>

      <Refusal error={error} onPlans={onPlans} variant="inline" />

      {!session.profileId ? (
        <div className="card"><p className="muted center">
          {tr("agent.signin", lang)}
        </p></div>
      ) : (
        <AgentTalk
          lang={lang} labels="agent.ask"
          ask={ask} setAsk={setAsk} asking={asking}
          canSend={!!session.ownerToken} onSend={send}
          talk={talk} did={did}
          onForget={() => { setTalk([]); setDid(null); }}
          reach={reach ? reach.can_touch : null}
          showsReach={showsReach}
          onToggleReach={() => setShowsReach(!showsReach)}
          unavailable={!!reach && !reach.available} />
      )}

      <div className="card">
        <h3>{tr("agent.widgets.title", lang)}</h3>
        <p className="muted small">{tr("agent.widgets.sub", lang)}</p>
        <button onClick={onStudio}>{tr("agent.widgets.go", lang)}</button>
      </div>
    </div>
  );
}
