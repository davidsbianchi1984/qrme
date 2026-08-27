/** The four panels that sit beside the face.
 *
 * 526.P002 asked for a rail of four buttons on the conversation screen —
 * Profile, Memory, Relationship, Controls — and the reason it belongs here
 * rather than on a settings screen is the same reason the skin picker moved
 * here: this is the one surface where you are actually looking at the thing
 * you would be changing.
 *
 *     asked     is each of these reachable somewhere in the console
 *     mattered  is it reachable from the screen it is about
 *
 * Two of the four are the owner's and two are the pair's, and the rail shows
 * what the person can actually open rather than four buttons of which two
 * refuse. A button that 403s is worse than an absent one: it reads as a
 * broken product rather than as somebody else's business.
 */

import { useEffect, useState } from "react";
import { api } from "./api";
import type {
  MemoryAccount, Profile, ProfileSteering, RecollectionShelf,
} from "./api";
import { t as tr, fill } from "./l10n";

export type RailPanel = "profile" | "memory" | "relationship" | "controls";

/** Owner-only panels, named once so the rail and the opener agree. */
const OWNERS: RailPanel[] = ["relationship", "controls"];

export function TalkRail({
  profileId, interactorId, lang, ownerToken, interactorToken, onError,
}: {
  profileId: string;
  interactorId: string | null;
  lang: string;
  ownerToken: string | null;
  interactorToken: string | null;
  onError: (m: string) => void;
}) {
  const [open, setOpen] = useState<RailPanel | null>(null);

  // The pair's own credential where there is one, the owner's otherwise —
  // `require_owner_or_interactor` takes either, and an owner talking to
  // their own profile holds only the first.
  const pairToken = interactorToken || ownerToken;

  const panels: RailPanel[] =
    (["profile", "memory", "relationship", "controls"] as RailPanel[])
      .filter((p) => {
        if (OWNERS.includes(p)) return !!ownerToken;
        if (p === "memory") return !!interactorId && !!pairToken;
        return true;
      });

  return (
    <>
      <div className="talk-rail" role="group"
           aria-label={tr("rail.group", lang)}>
        {panels.map((p) => (
          <button key={p}
                  className={"talk-rail-btn" + (open === p ? " on" : "")}
                  aria-pressed={open === p}
                  title={tr(`rail.${p}`, lang)}
                  onClick={() => setOpen((o) => (o === p ? null : p))}>
            <span aria-hidden="true">{GLYPH[p]}</span>
            <span className="talk-rail-label">{tr(`rail.${p}`, lang)}</span>
          </button>
        ))}
      </div>

      {open && (
        // The way out, twice over — the field report: "the only way to
        // exit is pressing the same button you used to get in." A tap
        // anywhere outside the panel minimises it (the scrim is the
        // whole screen, transparent, and sits under the panel), and the
        // red close at the top is the exit a person can see.
        <div className="talk-panel-scrim" aria-hidden="true"
             onClick={() => setOpen(null)} />
      )}
      {open && (
        <div className="card talk-panel" role="region"
             aria-label={tr(`rail.${open}`, lang)}>
          <button className="talk-panel-close"
                  aria-label={tr("rail.close", lang)}
                  title={tr("rail.close", lang)}
                  onClick={() => setOpen(null)}>✕</button>
          {open === "profile" && (
            <ProfilePanel profileId={profileId} lang={lang}
                          onError={onError} />
          )}
          {open === "memory" && interactorId && pairToken && (
            <MemoryPanel profileId={profileId} interactorId={interactorId}
                         token={pairToken} lang={lang} onError={onError} />
          )}
          {open === "relationship" && interactorId && ownerToken && (
            <RelationshipPanel profileId={profileId}
                               interactorId={interactorId}
                               token={ownerToken} pairToken={pairToken}
                               lang={lang} onError={onError} />
          )}
          {open === "relationship" && !interactorId && (
            <p className="muted small">{tr("rail.rel.nobody", lang)}</p>
          )}
          {open === "controls" && ownerToken && (
            <ControlsPanel profileId={profileId} token={ownerToken}
                           lang={lang} onError={onError} />
          )}
        </div>
      )}
    </>
  );
}

const GLYPH: Record<RailPanel, string> = {
  profile: "☰", memory: "◔", relationship: "⇄", controls: "🎛️",
};

// -- who they are ----------------------------------------------------------

function ProfilePanel({ profileId, lang, onError }: {
  profileId: string; lang: string; onError: (m: string) => void;
}) {
  const [p, setP] = useState<Profile | null>(null);

  useEffect(() => {
    api.getProfile(profileId).then(setP)
       .catch((e) => onError(String(e.message || e)));
  }, [profileId]);

  if (!p) return <p className="muted small">{tr("rail.loading", lang)}</p>;
  return (
    <div className="talk-panel-body">
      <div className="tile-label">{tr("rail.profile", lang)}</div>
      <h4>{p.display_name}</h4>
      {p.persona && <p className="small">{p.persona}</p>}
      {/* The disclosure travels with the face wherever the face is drawn,
          and this panel is a place the face is drawn. */}
      <p className="muted small">{tr("rail.profile.ai", lang)}</p>
    </div>
  );
}

// -- what it holds about you ----------------------------------------------

function MemoryPanel({ profileId, interactorId, token, lang, onError }: {
  profileId: string; interactorId: string; token: string;
  lang: string; onError: (m: string) => void;
}) {
  const [acc, setAcc] = useState<MemoryAccount | null>(null);
  const [sealed, setSealed] = useState<RecollectionShelf | null>(null);
  const [about, setAbout] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () =>
    api.memoryAccount(profileId, interactorId, token).then(setAcc)
       .catch((e) => onError(String(e.message || e)));
  // The sealed shelf beside the distilled account — the other axis of
  // memory, shown the same way it is held. Absent rather than broken on
  // deployments without a vault: nothing was sealed, nothing lists.
  const loadSealed = () =>
    api.recollections(profileId, interactorId, token).then(setSealed)
       .catch(() => setSealed(null));
  useEffect(() => { load(); loadSealed(); }, [profileId, interactorId]);

  const forget = () => {
    const words = about.trim();
    if (!words) return;
    setBusy(true);
    api.forgetMemory(profileId, interactorId, words, token)
       .then(() => { setAbout(""); return load(); })
       .catch((e) => onError(String(e.message || e)))
       .finally(() => setBusy(false));
  };

  if (!acc) return <p className="muted small">{tr("rail.loading", lang)}</p>;
  return (
    <div className="talk-panel-body">
      <div className="tile-label">{tr("rail.memory", lang)}</div>
      {/* Counts before prose: the door's whole claim is that it answers
          from the records rather than by generation. */}
      <p className="small">
        {fill(tr("rail.mem.counts", lang), {
          folded: String(acc.folded_turns),
          recent: String(acc.recent_turns),
        })}
      </p>
      {acc.remembers
        ? <p className="small">{acc.remembers}</p>
        : <p className="muted small">{tr("rail.mem.nothing", lang)}</p>}
      <div className="row">
        <input value={about} onChange={(e) => setAbout(e.target.value)}
               placeholder={tr("rail.mem.forgethint", lang)}
               aria-label={tr("rail.mem.forgethint", lang)} />
        <button disabled={busy || !about.trim()} onClick={forget}>
          {tr("rail.mem.forget", lang)}
        </button>
      </div>
      <p className="muted small">{tr("rail.mem.scalpel", lang)}</p>
      {sealed && (
        <>
          <div className="tile-label">{tr("rail.mem.sealed", lang)}</div>
          <p className="muted small">{tr("rail.mem.sealed.lead", lang)}</p>
          {!sealed.readable && (
            <p className="muted small">
              {tr("rail.mem.sealed.unreadable", lang)}
            </p>
          )}
          {sealed.memories.length === 0 && (
            <p className="muted small">{tr("rail.mem.sealed.none", lang)}</p>
          )}
          {sealed.memories.map((m) => (
            <div className="row" key={m.ref}>
              <span className="small" style={{ flex: 1 }}>
                {m.line ?? "…"}
                {m.at && (
                  <span className="muted small"> — {m.at.slice(0, 10)}</span>
                )}
              </span>
              <button disabled={busy} onClick={() => {
                setBusy(true);
                api.forgetRecollection(profileId, interactorId, m.ref, token)
                   .then(() => loadSealed())
                   .catch((e) => onError(String(e.message || e)))
                   .finally(() => setBusy(false));
              }}>
                {tr("rail.mem.sealed.forget", lang)}
              </button>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

// -- what you are to each other -------------------------------------------

function RelationshipPanel({
  profileId, interactorId, token, pairToken, lang, onError,
}: {
  profileId: string; interactorId: string; token: string;
  pairToken: string | null; lang: string; onError: (m: string) => void;
}) {
  const [type, setType] = useState("");
  const [nickname, setNickname] = useState("");
  const [tone, setTone] = useState("");
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);

  // Read through the pair's own account of itself. The relationship had no
  // GET of its own until this round, which is why the form used to open
  // blank over a standing that already existed.
  useEffect(() => {
    if (!pairToken) return;
    api.memoryAccount(profileId, interactorId, pairToken).then((a) => {
      const r = a.relationship;
      if (!r) return;
      setType(r.relationship_type || "");
      setNickname(r.nickname || "");
      setTone(r.tone || "");
    }).catch((e) => onError(String(e.message || e)));
  }, [profileId, interactorId]);

  const save = () => {
    if (!type.trim()) return;
    setBusy(true); setSaved(false);
    api.setRelationship(profileId, interactorId, {
      relationship_type: type.trim(),
      nickname: nickname.trim() || undefined,
      tone: tone.trim() || undefined,
    }, token)
      .then(() => setSaved(true))
      .catch((e) => onError(String(e.message || e)))
      .finally(() => setBusy(false));
  };

  return (
    <div className="talk-panel-body">
      <div className="tile-label">{tr("rail.relationship", lang)}</div>
      <label>{tr("rail.rel.type", lang)}
        <input value={type} onChange={(e) => setType(e.target.value)} /></label>
      <label>{tr("rail.rel.nickname", lang)}
        <input value={nickname}
               onChange={(e) => setNickname(e.target.value)} /></label>
      <label>{tr("rail.rel.tone", lang)}
        <input value={tone} onChange={(e) => setTone(e.target.value)} /></label>
      <div className="row">
        <button className="primary" disabled={busy || !type.trim()}
                onClick={save}>{tr("rail.rel.save", lang)}</button>
        {saved && <span className="muted small">
          {tr("rail.rel.saved", lang)}</span>}
      </div>
    </div>
  );
}

// -- how it behaves --------------------------------------------------------

function ControlsPanel({ profileId, token, lang, onError }: {
  profileId: string; token: string; lang: string;
  onError: (m: string) => void;
}) {
  const [st, setSt] = useState<ProfileSteering | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.profileSteering(profileId, token).then(setSt)
       .catch((e) => onError(String(e.message || e)));
  }, [profileId]);

  const move = (key: string, value: number) => {
    if (!st) return;
    setSt({ ...st, values: { ...st.values, [key]: value } });
  };

  const commit = () => {
    if (!st) return;
    setBusy(true);
    api.setProfileSteering(profileId, st.values, token)
       .catch((e) => onError(String(e.message || e)))
       .finally(() => setBusy(false));
  };

  if (!st) return <p className="muted small">{tr("rail.loading", lang)}</p>;
  // The lock is not decoration: while it stands no write lands, the owner's
  // own slip included, so the sliders say so rather than failing silently.
  const locked = !!st.lock;
  return (
    <div className="talk-panel-body">
      <div className="tile-label">{tr("rail.controls", lang)}</div>
      {locked && <p className="muted small">{tr("rail.ctl.locked", lang)}</p>}
      {/* `adult_only` dials are drawn only where the profile is in adult
          mode — the catalogue is shared with bodies and carries both. */}
      {st.dials.filter((d) => st.adult_mode || !d.adult_only).map((d) => (
        <label key={d.name} className="talk-dial">
          <span className="small">{d.label}</span>
          <input type="range" min={d.min} max={d.max} disabled={locked}
                 value={st.values[d.name] ?? d.default}
                 onChange={(e) => move(d.name, Number(e.target.value))}
                 onMouseUp={commit} onTouchEnd={commit} />
          <span className="muted small talk-dial-n">
            {st.values[d.name] ?? d.default}</span>
        </label>
      ))}
      {busy && <p className="muted small">{tr("rail.ctl.saving", lang)}</p>}
    </div>
  );
}
