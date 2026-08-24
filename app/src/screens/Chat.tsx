import { useEffect, useRef, useState } from "react";
import { fill, t as tr, visitorLang } from "../l10n";
import { api, getBase, type Avatar, type Briefing, type DialerPosture,
         type Escalated, type MyPerson } from "../api";
import { Briefcase } from "../Briefcase";
import { Refusal } from "../Refusal";
import { speakInPieces } from "../spoken";
import { TalkRail } from "../TalkRail";
import { Waveform } from "../Waveform";
import { presenceOf, presenceKey, animatedIn } from "../presence";
import { useSession } from "../store";
import { putAway, whenPutAway } from "../away";

interface Doc { id: string; name: string | null; url: string;
                ai_marked: boolean }
interface Msg { who: "you" | "assistant"; text: string; note?: string;
                /** A document this turn handed over (qrme/composing.py) —
                 *  the card, never the body. */
                doc?: Doc | null;
                /** Set when the model the owner chose did not answer and
                 *  the local fallback wrote this instead. */
                degradedFrom?: string | null }

export function Chat({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  // Bringing somebody real into it. `people` is yours-first for the area
  // asked about; `brief` is the whole file, read before anybody is
  // contacted, so declining is still free.
  const [realOpen, setRealOpen] = useState(false);
  const [realArea, setRealArea] = useState("");
  const [people, setPeople] = useState<MyPerson[]>([]);
  const [matter, setMatter] = useState("");
  const [grantToken, setGrantToken] = useState("");
  const [brief, setBrief] = useState<Briefing | null>(null);
  // Shown up front rather than produced mid-conversation: a person should
  // know what this profile can do before anything goes wrong.
  const [dialer, setDialer] = useState<DialerPosture | null>(null);
  const [escalated, setEscalated] = useState<Escalated | null>(null);
  const [said, setSaid] = useState("");
  // `signature_id`, not `envelope_id` — the ceremony returns the signature
  // and that is what arming checks. Same shape the referral form uses.
  const [waiverSig, setWaiverSig] = useState("");
  const lang = visitorLang();
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  // Where you are (spec clause 1): optional context the reply adapts to.
  // Off until opened, empty until filled — nothing is inferred or collected.
  const [whereOpen, setWhereOpen] = useState(false);
  const [location, setLocation] = useState("");
  const [conditions, setConditions] = useState("");
  const [activity, setActivity] = useState("");
  // Spec clauses 2/12: how the profile should work this turn. Empty means
  // "read my prompt and decide", which is what the backend does on its own.
  const [role, setRole] = useState("");
  const [rehearsal, setRehearsal] = useState<{ id: string; scenario: string } | null>(null);
  const [rhScenario, setRhScenario] = useState("");
  const [rhOpen, setRhOpen] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  // The reply mid-play, so leaving the screen can stop it. Navigating
  // away used to leave the bound voice talking with no screen behind it.
  const saying = useRef<{ stop: () => void } | null>(null);
  useEffect(() => () => {
    saying.current?.stop();
    saying.current = null;
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    // Leaving the screen closes the microphone too. This teardown stopped the
    // voice and left the ear open — put-away had its own handler and unmount
    // did not, so navigating away kept a browser tab's recording indicator
    // lit on a screen that was no longer there.
    wantsEar.current = false;
    talkRec.current?.stop();
    talkRec.current = null;
  }, []);
  // Voice: replies read aloud by the device's own engine, and a microphone
  // that fills the composer. Both feature-detected — the mic button simply
  // does not render on a browser without SpeechRecognition, because a
  // control that cannot work is worse than no control.
  const [speakOn, setSpeakOn] = useState(false);
  // The bound voice mid-utterance — `speechSynthesis.speaking` cannot see
  // an <audio> element, so the face needs its own word for it.
  const [voicing, setVoicing] = useState(false);
  // TS's DOM lib does not ship SpeechRecognition types; the constructor is
  // feature-detected and driven through the three members every engine has.
  const Recognition: (new () => any) | undefined =
    (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition;
  const [listening, setListening] = useState(false);
  // The live recogniser, so the page being put away can put it down. It had
  // no handle at all: the overlay relied on `onend` firing to drop the
  // light, and a frozen tab is exactly the case where `onend` never comes —
  // so the caption said the profile was listening to a microphone the
  // browser had already stopped.
  const talkRec = useRef<{ stop: () => void } | null>(null);
  // Whether the person still wants the ear open. A ref, not state: `onend`
  // fires from the engine outside React's render, and reading `listening`
  // there would read the value from the render that installed the handler.
  const wantsEar = useRef(false);
  // The talk surface: a full listening overlay in the sibling product's
  // shape — except this product's speaker has a face. The profile's avatar
  // is what you look at while it listens and answers; the abstract orb only
  // appears when the profile has no portrait yet.
  const [talking, setTalking] = useState(false);
  const [talkAvatar, setTalkAvatar] = useState<Avatar | null>(null);
  const [heard, setHeard] = useState("");
  // Handing your own profile something to read, and changing the face it
  // wears. Both shipped with a door on somebody *else's* homepage and none
  // here — so a person could give a starter they had just met a document,
  // and could not give one to the profile built from their own life.
  const [bcOpen, setBcOpen] = useState(false);
  // The composer's +. Five tools lived as full-size buttons in the bar and
  // the text box paid for it — the field report could not even see it. The
  // mic, the box and Send stay; everything else folds here.
  const [plusOpen, setPlusOpen] = useState(false);
  const [talkPlus, setTalkPlus] = useState(false);
  // The camera. A photograph goes into the briefcase rather than into a
  // route of its own — the briefcase is already the place material handed to
  // a profile lives, already says plainly that this deployment cannot see a
  // picture, and already scopes what you hand over to the two of you.
  const camRef = useRef<HTMLInputElement | null>(null);
  // The camera carries `capture`, which is what makes a phone open the lens.
  // These three deliberately do not: a picture already taken, a video, and
  // anything else are chosen from the device. All four land in the same
  // place — `shoot` imports whatever it is given.
  const libRef = useRef<HTMLInputElement | null>(null);
  const vidRef = useRef<HTMLInputElement | null>(null);
  const docRef = useRef<HTMLInputElement | null>(null);
  const [shooting, setShooting] = useState(false);
  const shoot = (file: File) => {
    if (!session.profileId || !session.interactorId) return;
    setShooting(true);
    api.importFile(session.profileId, session.interactorId, file,
                   tr("chat.camera.note", lang))
      .then(() => setBcOpen(true))   // land where it went, not nowhere
      .catch(setError)
      .finally(() => setShooting(false));
  };

  // What the conversation is doing, decided once. Before this the surface
  // had `listening` and used it for the pulse, the caption, and nothing
  // else — a profile that was thinking, speaking, or had just failed looked
  // identical to one sitting idle. `presence.ts` was written for this and
  // then nothing imported it, which is a module with no door.
  const presence = presenceOf({
    listening,
    awaiting: busy,
    // Two mouths, one face: the device recogniser reports through
    // `speechSynthesis.speaking`, the bound voice through `voicing`.
    speaking: (speakOn && !!window.speechSynthesis?.speaking) || voicing,
    working: shooting,
    failed: !!error,
  });

  // The conversation follows itself. The previous version scrolled from
  // `finally` inside a requestAnimationFrame, which can fire before React
  // commits the reply bubble — it measured yesterday's scrollHeight and the
  // newest message sat below the fold until the reader dragged it up. An
  // effect runs after the commit, so it sees the bubble it is scrolling to;
  // keying on busy too means the thinking indicator is followed as well.
  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [msgs, busy]);

  // Loaded on mount so the talk overlay opens with the face (or torso)
  // already in hand instead of flashing the placeholder.
  useEffect(() => {
    if (!session.profileId) return;
    api.avatar(session.profileId, session.ownerToken || "")
      .then(setTalkAvatar).catch(() => setTalkAvatar(null));
  }, [session.profileId, session.ownerToken]);

  async function speakAloud(text: string) {
    // The profile's own bound voice first — the person made it, bound it,
    // and this is the screen where the profile talks back; hearing the
    // browser's robot here was the binding not reaching the conversation.
    // The device's voice stands in when there is no binding, no engine, or
    // the reply outruns the synthesis ceiling.
    const token = session.ownerToken || session.interactorToken;
    if (session.profileId && token) {
      try {
        // Piece by piece: the first sentence plays while the rest is
        // still being synthesised — the talking face lights when the
        // first word is heard, not when the whole reply is rendered.
        const s = await speakInPieces(session.profileId, text, token);
        saying.current = s;
        setVoicing(true);
        void s.done.then(() => {
          if (saying.current === s) saying.current = null;
          setVoicing(false);
        });
        return;
      } catch { setVoicing(false); /* the device's voice stands in */ }
    }
    if (!("speechSynthesis" in window)) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang;
    window.speechSynthesis.speak(u);
  }

  function openTalk() {
    setTalking(true);
    setHeard("");
    if (session.profileId) {
      api.avatar(session.profileId, session.ownerToken || "")
        .then(setTalkAvatar).catch(() => setTalkAvatar(null));
    }
    talkListen();
  }

  // Listen → send → speak the reply → listen again, until closed. The
  // transcript is shown while it is being heard, so the surface never
  // swallows words silently.
  function talkListen() {
    if (!Recognition || putAway()) return;
    const rec = new Recognition();
    rec.lang = lang;
    // `continuous` defaults to **false**, and that was the whole defect: the
    // engine is specified to stop after the first utterance, so the ear shut
    // itself about a second in and the caption fell back to "tap to talk"
    // while somebody was still speaking. The room's dictation has set it
    // since it was written; this screen was a worse copy of a listener that
    // already worked here.
    rec.continuous = true;
    // Words appear as they are said rather than only when a phrase settles,
    // so the surface never looks deaf while it is hearing.
    rec.interimResults = true;
    let settled = "";
    let seen = 0;
    rec.onresult = (e: any) => {
      // A continuous session hands back a growing list. Reading
      // `results[0][0]` took the first phrase and only ever the first, so a
      // second sentence replaced nothing and was lost.
      let live = "";
      for (let i = seen; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) {
          const said = String(r[0].transcript).trim();
          if (said) settled += (settled ? " " : "") + said;
          seen = i + 1;
        } else {
          live += r[0].transcript;
        }
      }
      const text = (settled + (live ? " " + live : "")).trim();
      setHeard(text);
      setInput(text);
    };
    rec.onend = () => {
      talkRec.current = null;
      // Chrome ends the session on its own silence timeout even when
      // continuous, so an ear meant to stay open has to be reopened. Only
      // while the person still wants it and the screen has not been put
      // away — a press is not a thing to replay on somebody's behalf.
      if (wantsEar.current && !putAway()) { talkListen(); return; }
      wantsEar.current = false;
      setListening(false);
    };
    rec.onerror = (e: any) => {
      // A refused permission or a lost device is not a silence timeout, and
      // reopening on one would spin.
      if (e?.error === "no-speech" && wantsEar.current && !putAway()) return;
      wantsEar.current = false;
      talkRec.current = null;
      setListening(false);
    };
    talkRec.current = { stop: () => rec.stop() };
    wantsEar.current = true;
    setListening(true);
    rec.start();
  }

  /** Close the ear because the person asked, not because it timed out. */
  function talkStop() {
    wantsEar.current = false;
    const rec = talkRec.current;
    talkRec.current = null;
    setListening(false);
    rec?.stop();
  }

  // Put away mid-listen: the microphone goes down and the caption with it.
  // Nothing stands back up here — this overlay listens one turn at a time,
  // started by a press, and a press is not a thing to replay on somebody's
  // behalf when they come back.
  useEffect(() => whenPutAway(() => {
    wantsEar.current = false;
    talkRec.current?.stop();
    talkRec.current = null;
    setListening(false);
  }), []);

  async function send() {
    const message = input.trim();
    if (!message || !session.profileId || !session.interactorId) return;
    setInput("");
    setError(null);
    setMsgs((m) => [...m, { who: "you", text: message }]);
    setBusy(true);
    const environment =
      whereOpen && (location.trim() || conditions.trim() || activity.trim())
        ? {
            ...(location.trim() && { location: location.trim() }),
            ...(conditions.trim() && { conditions: conditions.trim() }),
            ...(activity.trim() && { activity: activity.trim() }),
            local_time: new Date().toTimeString().slice(0, 5),
          }
        : undefined;
    // An open rehearsal room takes the turn: the reply comes back marked
    // for what it is, and nothing lands in the remembered conversation.
    if (rehearsal) {
      try {
        const turn = await api.rehearse(
          session.profileId, rehearsal.id, message);
        setMsgs((m) => [...m, {
          who: "assistant", text: turn.reply,
          note: "🎭 " + rehearsal.scenario }]);
      } catch (e) { setError(e); }
      finally { setBusy(false); }
      return;
    }
    try {
      const reply = await api.chat(session.profileId, {
        interactor_id: session.interactorId,
        message,
        environment,
        // Spec clauses 2/12: ask the profile to work as an advisor,
        // collaborator or operator. Left on "read the prompt" the profile
        // decides for itself and the reply says which it chose.
        role: role || undefined,
      });
      const pm = reply.profile_message;
      const rc = reply.role_context;
      // Takes the sentence, not the key. Passing the key would put the
      // literal after `put(` instead of after `tr(`, where the dead-key
      // guard looks — four live keys would have read as dead.
      const put = (line: string, values: Record<string, string>) =>
        Object.entries(values).reduce(
          (out, [k, v]) => out.replace(`{${k}}`, v), line);
      const note = reply.handoff?.state
        ? put(tr("chat.handoff", lang), { state: reply.handoff.state })
        : pm.status !== "approved"
          ? pm.flag_reason
            ? put(tr("chat.moderated.why", lang),
                  { status: pm.status, why: pm.flag_reason })
            : put(tr("chat.moderated", lang), { status: pm.status })
          : rc
            ? put(tr("chat.workedas", lang), { role: rc.role, how: rc.how })
            : reply.environment
              ? tr("chat.adapted", lang)
              : undefined;
      const text = pm.status === "approved"
        ? pm.content
        : tr("chat.held", lang);
      // Who actually wrote it. Canned fallback text presented as the chosen
      // model is a lie the reader has no way to detect from the words alone —
      // the sibling product's Coach screen has said so in amber for releases.
      const degradedFrom = reply.provenance?.degraded_from ?? null;
      // What the turn handed over, if it handed anything over.
      const doc = (pm as { document?: Doc | null }).document ?? null;
      setMsgs((m) => [...m, { who: "assistant", text, note, degradedFrom,
                              doc }]);
      if ((speakOn || talking) && pm.status === "approved") speakAloud(text);
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="screen chat">
      <header className="screen-head">
        <h2>
          {fill(tr("chat.with", lang),
                { name: session.profile?.display_name })}
        </h2>
        <span className="muted small">{tr("chat.pitch", lang)}</span>
      </header>

      {/* role=log + aria-live: a screen reader is told when the reply
          arrives, instead of the conversation advancing silently. */}
      {/* The presence bubbles and the receding-grid backdrop stood here
          for one release and came back out on a field report: the names
          and portraits floated over the words people were trying to
          read. Presence rendering belongs to the rooms and the
          vastscape, where there is a scene to stand in — a text thread
          is its own scene. */}
      <div className="messages" role="log" aria-live="polite"
           ref={listRef}>
        {msgs.length === 0 && (
          <div className="muted center">
            {fill(tr("chat.sayhello", lang),
                  { name: session.profile?.display_name })}
          </div>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={"bubble " + m.who}>
            {m.text}
            {/* A document, as a card you can open and keep — the whole
              * point of the round: "how am I supposed to receive it and
              * how does it render on the screen?" The AI mark rides on it
              * because a composed document is synthetic media, which is
              * the mirror of a person's own photograph never being
              * marked. */}
            {m.doc && (
              <a className="bubble-doc" href={getBase() + m.doc.url}
                 target="_blank" rel="noreferrer" download={m.doc.name ?? true}>
                <span className="bubble-doc-icon" aria-hidden="true">📄</span>
                <span className="bubble-doc-name">
                  {m.doc.name || tr("chat.doc", lang)}
                </span>
                {m.doc.ai_marked && (
                  <span className="bubble-doc-ai">{tr("chat.doc.ai", lang)}</span>
                )}
              </a>
            )}
            {m.note && <div className="bubble-note">{m.note}</div>}
            {m.degradedFrom && (
              <div className="degraded">
                ⚠ {tr("chat.degraded.head", lang)}{" "}
                {m.degradedFrom} {tr("chat.degraded.tail", lang)}
              </div>
            )}
          </div>
        ))}
        {busy && <div className="bubble assistant thinking">…</div>}
      </div>

      <Refusal error={error} onPlans={onPlans} variant="inline" />

      {/* Spec clauses 2/12 — advisor counsels, collaborator co-creates,
          operator executes. "Let it read my prompt" is the honest default:
          the profile infers from the wording and the reply says which. */}
      <label className="role-pick">{tr("chat.rolepick", lang)}
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="">{tr("chat.role.read", lang)}</option>
          <option value="advisor">{tr("chat.role.advisor", lang)}</option>
          <option value="collaborator">{tr("chat.role.collaborator", lang)}</option>
          <option value="operator">{tr("chat.role.operator", lang)}</option>
        </select>
      </label>

      {/* --- what this profile can do, before anything goes wrong ------- */}
      <div className="card">
        <h3>{tr("esc.hdr", lang)}</h3>
        <p className="muted small">{tr("esc.pitch", lang)}</p>
        {!dialer
          ? <button className="ghost" onClick={() => {
              api.dialerPosture(session.interactorId || "",
                                session.interactorToken || "")
                .then(setDialer).catch(setError);
            }}>{tr("esc.show", lang)}</button>
          : (<>
              {/* The words, readable before anybody signs anything. */}
              <p className="small">{dialer.waiver}</p>
              <p className="muted small">
                {dialer.armed ? tr("esc.armed", lang) : tr("esc.notarmed", lang)}
              </p>
              {/* Said now, not discovered at the worst moment. */}
              {dialer.sealed && (
                <p className="small">
                  {fill(tr("esc.sealed", lang), { number: dialer.call_yourself })}
                </p>
              )}
              {!dialer.armed && (
                <>
                  <input value={waiverSig}
                         placeholder={tr("esc.sig.ph", lang)}
                         onChange={(e) => setWaiverSig(e.target.value)} />
                  <button className="ghost" disabled={!waiverSig} onClick={() => {
                    setError(null);
                    api.armDialer(session.interactorId || "", waiverSig,
                                  session.interactorToken || "")
                      .then(setDialer).catch(setError);
                  }}>{tr("esc.arm", lang)}</button>
                </>
              )}
              <button className="ghost" disabled={!matter} onClick={() => {
                setError(null);
                api.cannotResolve(session.profileId || "",
                                  { interactor_id: session.interactorId || "",
                                    matter },
                                  session.interactorToken || "")
                  .then(setEscalated).catch(setError);
              }}>{tr("esc.raise", lang)}</button>
              {escalated && (
                <button onClick={() => {
                  setError(null); setSaid("");
                  api.dialEmergency(escalated.id, session.interactorId || "",
                                    session.interactorToken || "")
                    .then(() => setSaid(tr("esc.placed", lang)))
                    .catch(setError);
                }}>{tr("esc.press", lang)}</button>
              )}
              <button className="ghost" onClick={() => {
                api.myEscalations(session.interactorId || "",
                                  session.interactorToken || "")
                  .then((rows) => setSaid(rows.length === 0
                    ? tr("esc.none", lang)
                    : rows.map((r) => `${r.matter} · ` + (r.placed
                        ? tr("esc.was.placed", lang)
                        : tr("esc.was.not", lang))).join("\n")))
                  .catch(setError);
              }}>{tr("esc.past", lang)}</button>
              {said && <p className="small">{said}</p>}
            </>)}
      </div>

      {/* --- bringing somebody real into it ---------------------------- */}
      <div className="card">
        <h3>{tr("real.hdr", lang)}</h3>
        <p className="muted small">{tr("real.pitch", lang)}</p>
        {!realOpen
          ? <button className="ghost" onClick={() => {
              setRealOpen(true);
              // Yours first, before any area is typed: that is what keeping
              // them was for.
              api.myPeople(session.interactorId || "",
                           session.interactorToken || "")
                .then(setPeople).catch(() => setPeople([]));
            }}>
              {tr("real.open", lang)}
            </button>
          : (<>
              <input value={realArea} placeholder={tr("real.area.ph", lang)}
                     onChange={(e) => setRealArea(e.target.value)} />
              <button disabled={!realArea} onClick={() => {
                setError(null);
                api.peopleForArea(session.interactorId || "", realArea,
                                  session.interactorToken || "")
                  .then(setPeople).catch(setError);
              }}>{tr("real.find", lang)}</button>
              {people.map((p) => (
                <div key={p.provider_id}>
                  <p className="small">
                    <b>{p.name}</b>{" · "}{p.area}
                    {p.location ? ` · ${p.location}` : ""}
                    {" · "}
                    {/* Yours and found-for-you are different claims. */}
                    {p.yours ? tr("real.yours", lang) : tr("real.found", lang)}
                    {p.preferred ? ` · ${tr("real.first", lang)}` : ""}
                  </p>
                  {p.yours
                    ? (<>
                        {!p.preferred && (
                          <button className="ghost" onClick={() => {
                            api.preferPerson(session.interactorId || "",
                                             p.provider_id,
                                             session.interactorToken || "")
                              .then(() => setPeople([])).catch(setError);
                          }}>{tr("real.prefer", lang)}</button>
                        )}
                        <button className="ghost" onClick={() => {
                          api.dropPerson(session.interactorId || "",
                                         p.provider_id,
                                         session.interactorToken || "")
                            .then(() => setPeople([])).catch(setError);
                        }}>{tr("real.drop", lang)}</button>
                      </>)
                    : <button className="ghost" onClick={() => {
                        api.keepPerson(session.interactorId || "",
                                       { provider_id: p.provider_id },
                                       session.interactorToken || "")
                          .then(() => setPeople([])).catch(setError);
                      }}>{tr("real.keep", lang)}</button>}
                </div>
              ))}
              <input value={matter} placeholder={tr("real.matter.ph", lang)}
                     onChange={(e) => setMatter(e.target.value)} />
              <input value={grantToken} type="password"
                     placeholder={tr("real.grant.ph", lang)}
                     onChange={(e) => setGrantToken(e.target.value)} />
              {people.filter((p) => p.yours).map((p) => (
                <button key={p.provider_id} className="ghost"
                        disabled={!matter || !grantToken}
                        onClick={() => {
                          setError(null); setBrief(null);
                          api.previewBriefing({
                            interactor_id: session.interactorId || "",
                            profile_id: session.profileId || "",
                            provider_id: p.provider_id, matter,
                            grant_token: grantToken,
                          }, session.interactorToken || "")
                            .then(setBrief).catch(setError);
                        }}>
                  {fill(tr("real.preview", lang), { name: p.name })}
                </button>
              ))}
              {brief && (
                <div>
                  {/* Read before anybody is contacted, counted out loud. */}
                  <p className="small">{brief.reads}</p>
                  {brief.package.attachments.map((a, i) => (
                    <p className="muted small" key={i}>
                      {a.kind} · {a.title}
                      {a.sealed ? ` · ${tr("real.sealed", lang)}` : ""}
                    </p>
                  ))}
                </div>
              )}
            </>)}
      </div>

      {whereOpen && (
        <div className="row" style={{ padding: "4px 0" }}>
          <label>{tr("chat.where", lang)}<input value={location}
                             placeholder={tr("chat.where.ph", lang)}
                             onChange={(e) => setLocation(e.target.value)} /></label>
          <label>{tr("chat.conditions", lang)}<input value={conditions}
                                  placeholder={tr("chat.conditions.ph", lang)}
                                  onChange={(e) => setConditions(e.target.value)} /></label>
          <label>{tr("chat.doing", lang)}<input value={activity}
                             placeholder={tr("chat.doing.ph", lang)}
                             onChange={(e) => setActivity(e.target.value)} /></label>
        </div>
      )}

      {talking && (
        <div className="talk-overlay" role="dialog"
             aria-label={tr("chat.talk", lang)}>
          <button className="talk-close" onClick={() => {
            setTalking(false); window.speechSynthesis?.cancel();
          }}>×</button>
          {/* The torso form stands at full figure where there is one; the
              circular face is next; the orb is only for a profile with no
              portrait at all. */}
          {talkAvatar?.torso ? (
            <img className={"talk-torso" + (animatedIn(presence) ? " listening" : "")}
                 src={talkAvatar.torso.startsWith("http")
                        ? talkAvatar.torso
                        : getBase() + talkAvatar.torso}
                 alt={session.profile?.display_name || ""} />
          ) : talkAvatar?.asset ? (
            /* The face, or the empty frame — `render()` decides which, and
               `placeholder` only says how to caption it. This branch used to
               fall through to an abstract orb whenever the asset was a
               placeholder, which made every portrait-less profile look
               identical to every other and looked like a thing rather than
               like something to fill. */
            <div className={"talk-face" + (animatedIn(presence) ? " listening" : "")
                            + (talkAvatar.placeholder ? " empty" : "")}>
              <img src={talkAvatar.asset.startsWith("http")
                          ? talkAvatar.asset
                          : getBase() + talkAvatar.asset}
                   alt={session.profile?.display_name || ""} />
            </div>
          ) : null}
          <div className="talk-name">{session.profile?.display_name}</div>
          {/* Seven states rather than two, and the strip below reads from the
              same decision — so the caption and the bars cannot disagree
              about what is happening. */}
          <div className="talk-state muted small">
            {tr(presenceKey(presence), lang)}
          </div>
          <Waveform presence={presence} lang={lang} />
          {heard && <div className="talk-heard">{heard}</div>}
          {talkAvatar && (!talkAvatar.asset || talkAvatar.placeholder) && (
            <div className="muted small">{tr("chat.talk.noface", lang)}</div>
          )}
          <div className="row" style={{ justifyContent: "center" }}>
            {/* One control, both directions. While it was only "Speak
                again" there was no way to close an ear that had opened, and
                no way to tell from the button that it was open. */}
            <button className={listening ? "" : "primary"}
                    onClick={listening ? talkStop : talkListen}>
              {listening ? tr("chat.talk.stop", lang) : tr("chat.talk.again", lang)}
            </button>
            <button className="primary" disabled={busy || !input.trim()}
                    onClick={() => { setHeard(""); send(); }}>
              {tr("chat.send", lang)}
            </button>
            {/* Sharing from the face, not only from the composer below it.
                This is the screen somebody is actually on while talking, and
                it was the one surface with no way to hand anything over. */}
            <button className="agent-plusbtn" aria-label={tr("agent.plus", lang)}
                    aria-expanded={talkPlus}
                    onClick={() => setTalkPlus((o) => !o)}>+</button>
          </div>
          {talkPlus && (
            <div className="agent-plus talk-plus" role="menu">
              <button role="menuitem"
                      disabled={!session.profileId || !session.interactorId}
                      onClick={() => { setTalkPlus(false); libRef.current?.click(); }}>
                🖼️ {tr("chat.share.photo", lang)}
              </button>
              <button role="menuitem"
                      disabled={!session.profileId || !session.interactorId}
                      onClick={() => { setTalkPlus(false); vidRef.current?.click(); }}>
                🎬 {tr("chat.share.video", lang)}
              </button>
              <button role="menuitem"
                      disabled={!session.profileId || !session.interactorId}
                      onClick={() => { setTalkPlus(false); camRef.current?.click(); }}>
                📷 {tr("chat.camera", lang)}
              </button>
              <button role="menuitem"
                      disabled={!session.profileId || !session.interactorId}
                      onClick={() => { setTalkPlus(false); docRef.current?.click(); }}>
                📄 {tr("chat.share.file", lang)}
              </button>
            </div>
          )}
          {/* Who they are, what they hold about you, what you are to each
              other, and how they behave — beside the face rather than three
              screens away from it. */}
          {session.profileId && (
            <TalkRail profileId={session.profileId}
                      interactorId={session.interactorId || null}
                      lang={lang}
                      ownerToken={session.ownerToken || null}
                      interactorToken={session.interactorToken || null}
                      onError={setError} />
          )}
        </div>
      )}

      {/* Rehearsal: practice the hard conversation — the transcript lives
          only in the room, and closing the room wipes it. While a room is
          open, turns go there instead of the remembered conversation. */}
      {rhOpen && (
        <div className="card">
          <h3>{tr("cht.rh", lang)}</h3>
          <p className="muted small">{tr("cht.rh.pitch", lang)}</p>
          {rehearsal ? (
            <div className="row">
              <span className="muted small" style={{ flex: 1 }}>
                🎭 {rehearsal.scenario}
              </span>
              <button className="danger" onClick={async () => {
                if (!session.profileId) return;
                try {
                  await api.closeRehearsal(session.profileId, rehearsal.id);
                } catch { /* the room may already be gone */ }
                setRehearsal(null);
              }}>{tr("cht.rh.close", lang)}</button>
            </div>
          ) : (
            <div className="row">
              <input value={rhScenario}
                     placeholder={tr("cht.rh.scenario.ph", lang)}
                     onChange={(e) => setRhScenario(e.target.value)}
                     style={{ flex: 1 }} />
              <button className="primary"
                      disabled={busy || !rhScenario.trim()}
                      onClick={async () => {
                        if (!session.profileId || !session.interactorId) return;
                        try {
                          const room = await api.openRehearsal(
                            session.profileId, session.interactorId,
                            rhScenario.trim());
                          setRehearsal({ id: room.id, scenario: room.scenario });
                          setRhScenario("");
                        } catch (e) { setError(e); }
                      }}>{tr("cht.rh.open", lang)}</button>
            </div>
          )}
        </div>
      )}

      {bcOpen && session.profileId && session.interactorId && (
        <div className="card">
          <Briefcase profileId={session.profileId}
                     interactorId={session.interactorId}
                     name={session.profile?.display_name || ""}
                     onError={setError} />
        </div>
      )}

      <div className="composer">
        {plusOpen && (
          <div className="agent-plus composer-plus" role="menu">
            <button role="menuitem"
                    onClick={() => { setPlusOpen(false); setBcOpen((o) => !o); }}>
              📎 {tr("prf.bc.heading", lang)}{bcOpen ? " ✓" : ""}
            </button>
            <button role="menuitem"
                    disabled={!session.profileId || !session.interactorId}
                    onClick={() => { setPlusOpen(false); camRef.current?.click(); }}>
              📷 {tr("chat.camera", lang)}
            </button>
            <button role="menuitem"
                    onClick={() => { setPlusOpen(false); setRhOpen((o) => !o); }}>
              🎭 {tr("cht.rh", lang)}{rhOpen || rehearsal ? " ✓" : ""}
            </button>
            <button role="menuitem"
                    onClick={() => { setPlusOpen(false); setWhereOpen((w) => !w); }}>
              📍 {tr("chat.wheretitle", lang)}{whereOpen ? " ✓" : ""}
            </button>
            <button role="menuitem" aria-pressed={speakOn}
                    onClick={() => { setPlusOpen(false); setSpeakOn((v) => !v); }}>
              {speakOn ? "🔊" : "🔇"} {tr("chat.speak", lang)}{speakOn ? " ✓" : ""}
            </button>
          </div>
        )}
        <button className="agent-plusbtn" aria-label={tr("agent.plus", lang)}
                aria-expanded={plusOpen}
                onClick={() => setPlusOpen(!plusOpen)}>+</button>
        {/* The camera. `capture="environment"` is what makes a phone open the
            lens rather than the picker — without it this is the paperclip
            again with a different glyph, which is how a camera button ends up
            shipping that never took a photograph. On a desktop browser the
            attribute is ignored and the file chooser opens, which is the
            honest fallback rather than a control that does nothing. */}
        <input ref={libRef} type="file" accept="image/*"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0];
                 e.target.value = "";
                 if (f) shoot(f);
               }} />
        <input ref={vidRef} type="file" accept="video/*"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0];
                 e.target.value = "";
                 if (f) shoot(f);
               }} />
        <input ref={docRef} type="file"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0];
                 e.target.value = "";
                 if (f) shoot(f);
               }} />
        <input ref={camRef} type="file" accept="image/*" capture="environment"
               style={{ display: "none" }}
               onChange={(e) => {
                 const f = e.target.files?.[0];
                 e.target.value = "";
                 if (f) shoot(f);
               }} />
        {Recognition && (
          <button title={tr("chat.mic", lang)}
                  aria-label={tr("chat.mic", lang)}
                  className={listening ? "primary" : ""}
                  onClick={openTalk}>🎤</button>
        )}
        <input
          value={input}
          placeholder={tr("chat.type.ph", lang)}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button className="primary" onClick={send} disabled={busy}>
          {tr("chat.send", lang)}
        </button>
      </div>
    </div>
  );
}
