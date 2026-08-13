import { useState } from "react";
import { fill, t as tr, visitorLang } from "../l10n";
import { api, type EmbodimentConsistency, type ObjectionOpened,
         type ObjectionTimeline, type ProfileAttention,
         type ObjectionStatus, type WatermarkRecovery } from "../api";
import { Access } from "./Access";

/**
 * The console, for somebody who does not have an account and should not need
 * one.
 *
 * ## What this screen is for
 *
 * Two of QRME's routes are public **on purpose**, and the backend says so in
 * its own words. `open_objection`:
 *
 *     Open an objection (public: the objecting party need not own an
 *     account). Suspends the profile pending review.
 *
 * And `Contest.tsx`, the tab that carried the form, says it in the copy a
 * person reads:
 *
 *     You do not need an account. Objecting to a profile should not require
 *     joining the platform that is hosting it.
 *
 * That sentence was printed on a surface reachable only after joining the
 * platform. `App.tsx` returns `<Onboarding />` for the entire window while
 * `session.profileId` is unset, so every one of the console's forty-six tabs
 * — Contest among them — was behind a sign-up. The person the route was
 * written for is, by construction, the one person who cannot get to it: they
 * have found a synthetic profile of themselves, they have no QRME account,
 * and the product's answer was that they should make one first.
 *
 * The same is true of the mark. Somebody sent a message, a picture or a
 * recording and wondering whether a person made it has no account either.
 * `recover` answers from the text alone — no credential id, and it keeps
 * answering after the text has been edited — which is exactly the shape of
 * the question a stranger arrives with.
 *
 * ## What it deliberately does not do
 *
 * It carries no owner controls, and nothing here reads a token. The objection
 * status check returns `objector_ref` so somebody can confirm the case is
 * theirs without being logged in as anybody; the audit trail, which quotes
 * the objector's reason, stays owner- and reviewer-gated on the Contest tab
 * where it was.
 *
 * ## How somebody arrives
 *
 * From the link on the sign-in screen, and from `#object` / `#mark` in the
 * URL — so a takedown notice, an email, or a line in a moderation reply can
 * point straight at the form rather than at a sign-up page. The console has
 * no router; the hash is read once at mount, which is enough for a link and
 * is not pretending to be more.
 */
/** The visitor's language, resolved once. There is no profile to watch for
 *  changes on — that is the whole point of this screen. */
const LANG = visitorLang();
const L = (key: string) => tr(key, LANG);

export function Public({ start, onBack }: {
  start: Pane;
  onBack: () => void;
}) {
  const [pane, setPane] = useState<Pane>(start);

  return (
    <div className="public-entry">
      <header className="public-head">
        <span className="orb" />
        <div>
          <div className="brand-name">QRME</div>
          <div className="brand-sub">{L("pub.sub")}</div>
        </div>
        <button className="linkish" onClick={onBack}>{L("pub.back")}</button>
      </header>

      {/* `.tabs`, not `.row` — the tab styling is scoped under it. */}
      <div className="tabs">
        <button className={pane === "object" ? "tab active" : "tab"}
                onClick={() => setPane("object")}>
          {L("pub.tab.object")}
        </button>
        <button className={pane === "mark" ? "tab active" : "tab"}
                onClick={() => setPane("mark")}>
          {L("pub.tab.mark")}
        </button>
        <button className={pane === "same" ? "tab active" : "tab"}
                onClick={() => setPane("same")}>
          {L("pub.tab.same")}
        </button>
        <button className={pane === "count" ? "tab active" : "tab"}
                onClick={() => setPane("count")}>
          {L("pub.count.title")}
        </button>
        <button className={pane === "access" ? "tab active" : "tab"}
                onClick={() => setPane("access")}>
          {L("pub.tab.access")}
        </button>
      </div>

      {pane === "object" && <ObjectPane />}
      {pane === "mark" && <MarkPane />}
      {pane === "same" && <SamePane />}
      {pane === "count" && <CountPane />}
      {/* The accessibility statement and its report door. Here as well as on
          the signed-in tab, and deliberately: the person this screen exists
          for may be the person the signup shut out. */}
      {pane === "access" && <Access />}

      <p className="muted small">
        {L("pub.notoken")} {L("pub.notoken.signedin")}
      </p>
    </div>
  );
}

/** The five questions a stranger arrives with. */
export type Pane = "object" | "mark" | "same" | "count" | "access";

function message(e: unknown): string {
  return e instanceof Error ? e.message : String(e);
}

/** Opening an objection, and checking one you have already opened. */
function ObjectPane() {
  const [profileId, setProfileId] = useState("");
  const [ref, setRef] = useState("");
  const [reason, setReason] = useState("");
  const [opened, setOpened] = useState<ObjectionOpened | null>(null);
  const [lookup, setLookup] = useState("");
  const [status, setStatus] = useState<ObjectionStatus | null>(null);
  const [timeline, setTimeline] = useState<ObjectionTimeline | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function open() {
    setBusy(true); setError(null);
    try {
      const o = await api.openObjection({
        profile_id: profileId.trim(), objector_ref: ref.trim(),
        reason: reason.trim() || undefined,
      });
      setOpened(o);
      setLookup(o.id);
      setStatus(await api.objection(o.id));
    } catch (e) { setError(message(e)); }
    setBusy(false);
  }

  async function check() {
    setBusy(true); setError(null);
    try { setStatus(await api.objection(lookup.trim())); }
    catch (e) { setError(message(e)); }
    setBusy(false);
  }

  return (
    <>
      <div className="card">
        <h3>{L("pub.object.title")}</h3>
        <p className="muted small">
          {L("pub.object.restricts")}
        </p>
        <div className="row">
          <input value={profileId} onChange={(e) => setProfileId(e.target.value)}
                 placeholder={L("pub.object.profileId")} style={{ flex: 1 }} />
          <input value={ref} onChange={(e) => setRef(e.target.value)}
                 placeholder={L("pub.object.ref")} />
        </div>
        <div className="row">
          <input value={reason} onChange={(e) => setReason(e.target.value)}
                 placeholder={L("pub.object.reason")} style={{ flex: 1 }} />
          <button disabled={busy || !profileId.trim() || !ref.trim()}
                  onClick={open}>{L("pub.object.open")}</button>
        </div>
        <p className="muted small">
          {L("pub.object.ref.note")}
        </p>
      </div>

      {opened && (
        <div className="card">
          <h3>{fill(L("pub.object.opened"), { id: opened.id })}</h3>
          <p className="small">{opened.note}</p>
          <p className="small">
            {/* The state words come back in the API's own vocabulary, on
                purpose — `Contest.tsx` branches on `status === "open"`, and a
                translated value there would hide the card that ends a case.
                Translating for display is this screen's job, not the
                route's. */}
            {fill(L("pub.object.opened.status"), {
              now: <strong>{L(`pub.state.${opened.profile_status}`)}</strong>,
              before: <strong>{L(`pub.state.${opened.prior_status}`)}</strong>,
            })}
          </p>
          <p className="muted small">
            {L("pub.object.writeitdown")}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{L("pub.check.title")}</h3>
        <div className="row">
          <input value={lookup} onChange={(e) => setLookup(e.target.value)}
                 placeholder={L("pub.check.id")} style={{ flex: 1 }} />
          <button disabled={busy || !lookup.trim()} onClick={check}>{L("pub.check.go")}</button>
        </div>
        {status && (
          <p className="small">
            <strong>{L(`pub.state.${status.status}`)}</strong>
            {status.objector_ref && <>{" "}
              {fill(L("pub.check.against"), { ref: status.objector_ref })}</>}
            {/* The reference is echoed back so somebody can confirm the case
                is theirs. The reason is not: it is quoted in the audit trail,
                which stays gated. */}
          </p>
        )}
      </div>

      {/* The record of their own case. Public, because the party who raised
          it has no account — and carrying no free text, which is what keeps
          the full audit trail gated. Before this it was gated too, so the
          person who could END the profile could not read what happened. */}
      <div className="card">
        <h3>{L("pub.timeline.title")}</h3>
        <p className="muted small">{L("pub.timeline.lead")}</p>
        <div className="row">
          <button disabled={busy || !lookup.trim()} onClick={async () => {
            setBusy(true); setError(null);
            try { setTimeline(await api.objectionTimeline(lookup.trim())); }
            catch (e) { setError(message(e)); }
            setBusy(false);
          }}>{L("pub.timeline.go")}</button>
        </div>
        {timeline && (timeline.events.length === 0
          ? <p className="muted small">{L("pub.timeline.empty")}</p>
          : <ul className="refs">
              {timeline.events.map((e) => (
                <li key={e.id}>
                  <strong>{L(`pub.event.${e.event}`)}</strong>{" · "}
                  {L(`pub.actor.${e.actor}`)}{" · "}{e.at}
                  {e.sealed && <>{" · "}{L("pub.timeline.sealed")}</>}
                </li>
              ))}
            </ul>)}
      </div>

      {error && <p className="error small">{error}</p>}
    </>
  );
}

/**
 * Is the thing I met here the thing I met there.
 *
 * `embodiment_consistency` is public in its own words — *"anyone meeting the
 * profile through any form can verify it is the same personality"* — and the
 * only screen calling it was the owner's Workshop, which said so, in a card
 * only the owner could see. The person the sentence describes met the profile
 * on a speaker or in a room. They are not the owner and have no console.
 */
function SamePane() {
  const [profileId, setProfileId] = useState("");
  const [same, setSame] = useState<EmbodimentConsistency | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function check() {
    setBusy(true); setError(null); setSame(null);
    try { setSame(await api.embodimentConsistency(profileId.trim())); }
    catch (e) { setError(message(e)); }
    setBusy(false);
  }

  return (
    <>
      <div className="card">
        <h3>{L("pub.same.title")}</h3>
        <p className="muted small">
          {L("pub.same.explain")}
        </p>
        <div className="row">
          <input value={profileId} onChange={(e) => setProfileId(e.target.value)}
                 placeholder={L("pub.object.profileId")} style={{ flex: 1 }} />
          <button disabled={busy || !profileId.trim()} onClick={check}>
            {L("pub.same.go")}
          </button>
        </div>
      </div>

      {same && (
        <div className="card">
          <h3>{same.name}</h3>
          <p className="small">{same.guarantee}</p>
          <p className="muted small">
            {fill(L("pub.same.signature"), {
              sig: <code>{same.signature}</code>,
              across: same.invariant_across,
            })}
          </p>
          {same.surfaces.length > 0 && (
            <p className="muted small">
              {fill(L("pub.same.alsoon"),
                    { surfaces: same.surfaces.join(", ") })}
            </p>
          )}
          {same.embodiments.length > 0 && (
            <p className="muted small">
              {fill(L("pub.same.forms"),
                    { forms: same.embodiments.map((e) => e.name).join(", ") })}
            </p>
          )}
        </div>
      )}

      {error && <p className="error small">{error}</p>}
    </>
  );
}

/** How many people is this thing talking to.
 *
 *  Here rather than behind sign-in, and deliberately: a synthetic profile
 *  talks to many people by construction, and the harm was never the
 *  multiplicity — it is finding out, late, that the number was available the
 *  whole time and nobody offered it. Making somebody get an account first is
 *  the same withholding with a form in front of it.
 *
 *  What the answer does *not* contain is the other half: no names, no
 *  ranking, and no favourite. Those three come back as fields so this screen
 *  renders the refusals next to the number instead of composing a reassuring
 *  sentence of its own.
 */
function CountPane() {
  const [profileId, setProfileId] = useState("");
  const [found, setFound] = useState<ProfileAttention | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function ask() {
    setBusy(true); setError(null); setFound(null);
    try { setFound(await api.profileAttention(profileId.trim())); }
    catch (e) { setError(message(e)); }
    setBusy(false);
  }

  return (
    <>
      <div className="card">
        <h3>{L("pub.count.title")}</h3>
        <input value={profileId} onChange={(e) => setProfileId(e.target.value)}
               placeholder={L("pub.count.id")} />
        <button disabled={busy || !profileId.trim()} onClick={ask}>
          {L("pub.count.ask")}
        </button>
      </div>

      {found && (
        <div className="card">
          {/* No punctuation between the interpolations: a bare separator is
              JsxText, and the pre-session English ratchet counts JsxText —
              correctly, since it cannot know a middot from a word. */}
          <div className="row">
            <span style={{ flex: 1 }}>{found.people_this_week}</span>
            <span className="muted small">{L("pub.count.week")}</span>
            <span style={{ flex: 1 }}>{found.people_ever}</span>
            <span className="muted small">{L("pub.count.ever")}</span>
          </div>
          <p>{found.says}</p>
          <p className="muted small">{found.note}</p>
        </div>
      )}

      {error && <p className="error small">{error}</p>}
    </>
  );
}

/** Whose work is this — from the content alone. */
function MarkPane() {
  const [content, setContent] = useState("");
  const [found, setFound] = useState<WatermarkRecovery | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function ask() {
    setBusy(true); setError(null); setFound(null);
    try { setFound(await api.recoverWatermark(content)); }
    catch (e) { setError(message(e)); }
    setBusy(false);
  }

  return (
    <>
      <div className="card">
        <h3>{L("pub.mark.title")}</h3>
        <p className="muted small">{L("pub.mark.explain")}</p>
        <textarea value={content} onChange={(e) => setContent(e.target.value)}
                  rows={6} placeholder={L("pub.mark.paste")} />
        <button disabled={busy || !content.trim()} onClick={ask}>
          {L("pub.mark.ask")}
        </button>
      </div>

      {found && (
        <div className="card">
          {found.recovered ? (
            <>
              <h3>{found.display?.mark} {found.display?.label}</h3>
              {/* The plain verdict first — a field report wanted the human
                  question answered in one sentence, not inferred from a
                  credential id. */}
              <p className="small"><strong>{L("pub.mark.synth")}</strong></p>
              <p className="small">
                {fill(L("pub.mark.producedby"),
                      { state: <strong>{found.state}</strong> })}
              </p>
              <p className="muted small">
                {fill(L("pub.mark.windows"), {
                  matched: found.matched_windows,
                  stored: found.stored_windows,
                  examined: found.examined_windows,
                  similarity: found.similarity,
                })}{" "}
                {found.method}
              </p>
              {found.verbatim === false && (
                <p className="small">
                  {L("pub.mark.altered")}
                </p>
              )}
              <p className="muted small">{found.disclosure}</p>
            </>
          ) : (
            <>
              <h3>{L("pub.mark.unknown")}</h3>
              {/* Honest about what absence proves: no mark means no profile
                  of this deployment wrote it — likely a person, possibly a
                  machine that signs nothing. Certainty would be a lie. */}
              <p className="small"><strong>{L("pub.mark.maybehuman")}</strong></p>
              <p className="small">{found.reason}</p>
              <p className="muted small">
                {fill(L("pub.mark.unknown.explain"),
                      { here: <em>{L("pub.mark.here")}</em> })}
              </p>
            </>
          )}
        </div>
      )}

      {error && <p className="error small">{error}</p>}
    </>
  );
}
