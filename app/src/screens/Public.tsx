import { useState } from "react";
import { t as tr, visitorLang } from "../l10n";
import { api, type EmbodimentConsistency, type ObjectionOpened,
         type ObjectionStatus, type WatermarkRecovery } from "../api";

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
      </div>

      {pane === "object" && <ObjectPane />}
      {pane === "mark" && <MarkPane />}
      {pane === "same" && <SamePane />}

      <p className="muted small">
        {L("pub.notoken")} If you do have a profile, signing in gets you the
        same forms with your own case history beside them.
      </p>
    </div>
  );
}

/** The three questions a stranger arrives with. */
export type Pane = "object" | "mark" | "same";

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
          You do not need an account, and this page is the proof of it rather
          than a promise about it. Opening an objection restricts the profile
          straight away — public surfaces off, no new interactors — before
          anybody reviews it.
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
          The proof reference points at an identity check held outside this
          system — it is not a login, and it is what lets you object without
          one.
        </p>
      </div>

      {opened && (
        <div className="card">
          <h3>Opened — {opened.id}</h3>
          <p className="small">{opened.note}</p>
          <p className="small">
            The profile is <strong>{opened.profile_status}</strong> from this
            moment. It was <strong>{opened.prior_status}</strong>, and if the
            objection is dismissed it goes back to exactly that.
          </p>
          <p className="muted small">
            Write the id down. It is how you check this case later without an
            account — there is no inbox here to come back to.
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
            <strong>{status.status}</strong>
            {status.objector_ref && <> · opened against{" "}
              {status.objector_ref}</>}
            {/* The reference is echoed back so somebody can confirm the case
                is theirs. The reason is not: it is quoted in the audit trail,
                which stays gated. */}
          </p>
        )}
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
          A profile keeps one identity signature across every form it takes —
          a chat window, a voice on a speaker, a body in a room. Put the id in
          and compare it with the one you were given elsewhere.
        </p>
        <div className="row">
          <input value={profileId} onChange={(e) => setProfileId(e.target.value)}
                 placeholder="the profile's id" style={{ flex: 1 }} />
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
            Signature <code>{same.signature}</code> · invariant across{" "}
            {same.invariant_across}.
          </p>
          {same.surfaces.length > 0 && (
            <p className="muted small">Also present on: {same.surfaces.join(", ")}.</p>
          )}
          {same.embodiments.length > 0 && (
            <p className="muted small">
              Forms: {same.embodiments.map((e) => e.name).join(", ")}.
            </p>
          )}
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
        <p className="muted small">
          Paste it. This asks whose work it is with no credential id, and keeps
          answering after the text has been reworded — which is the state text
          usually arrives in. It is the right question for a stranger holding a
          screenshot; checking a credential you already hold is a different one
          and lives inside an account.
        </p>
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
              <p className="small">
                Produced by a QRME synthetic profile — <strong>{found.state}</strong>.
              </p>
              <p className="muted small">
                {found.matched_windows} of {found.stored_windows} stored
                windows matched, out of {found.examined_windows} examined
                (similarity {found.similarity}). {found.method}
              </p>
              {found.verbatim === false && (
                <p className="small">
                  The wording has changed since it was stamped. That does not
                  make it less traceable — it is what the score above is
                  measuring.
                </p>
              )}
              <p className="muted small">{found.disclosure}</p>
            </>
          ) : (
            <>
              <h3>{L("pub.mark.unknown")}</h3>
              <p className="small">{found.reason}</p>
              <p className="muted small">
                This says nothing about whether a person wrote it. It says no
                profile <em>on this deployment</em> has stamped work that shares
                enough wording with it.
              </p>
            </>
          )}
        </div>
      )}

      {error && <p className="error small">{error}</p>}
    </>
  );
}
