import { useEffect, useRef, useState } from "react";
import { api, getBase, type Anonymity, type Avatar, type AvatarBrief, type Deleted,
         type Emblem, type IdentityVocabulary, type Memorial, type Sibling,
         type Sunset, type Verifiable, type Verification } from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * Who this profile is, who is allowed to know, and how it ends.
 *
 * Nineteen routes with no caller — including `DELETE /profiles/{id}`, so the
 * console could make a profile and never remove one.
 *
 * The screen is arranged around the rule that holds the feature together:
 * **you may have as many profiles as you like, any of them may be anonymous,
 * and at most one may be verified — because the badge says you are a
 * particular real person, and said of two profiles at once it is either false
 * of one or a claim that you are two people.** So the roster comes first, with
 * the badge shown as a thing that *sits somewhere and can move*, rather than a
 * checkbox on each profile that happens to refuse.
 *
 * Three things are shown rather than paraphrased:
 *
 * - the `not_withheld` list, at the same weight as `withheld`. Anonymity here
 *   is a promise about what the platform publishes, not a promise that nobody
 *   can recognise your writing, and a screen that showed only the first half
 *   would be selling the second;
 * - whichever refusal the server sends when a claim is rejected — 422 for a
 *   malformed one, 409 for the one-badge rule — because both already carry the
 *   sentence a person needs;
 * - the itemised deletion receipt, one count per table. "Deleted" is a claim;
 *   twenty-five numbers are evidence.
 */
export function Identity({ onPlans, onPassing }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
  /** Beginning and passing on — pre-building, recovery, how it ends. An
   *  option taken from here rather than a tab lived in. */
  onPassing: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [vocab, setVocab] = useState<IdentityVocabulary | null>(null);
  const [roster, setRoster] = useState<Sibling[]>([]);
  const [verification, setVerification] = useState<Verification | null>(null);
  const [verifiable, setVerifiable] = useState<Verifiable | null>(null);
  const [anon, setAnon] = useState<Anonymity | null>(null);
  const [avatar, setAvatar] = useState<Avatar | null>(null);
  // The avatar deck: market import sources, the file input, and the selfie
  // capture (camera frames from several angles, uploaded through the same
  // media door as any photo, then imported as the portrait).
  const [market, setMarket] = useState<{ key: string; name: string;
                                         how: string }[]>([]);
  const [marketKey, setMarketKey] = useState("ready_player_me");
  const [marketUrl, setMarketUrl] = useState("");
  const [marketTorso, setMarketTorso] = useState("");
  const [capturing, setCapturing] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const captureAngles = ["front", "left", "right", "up", "down"];
  const [captured, setCaptured] = useState<string[]>([]);

  const reloadAvatar = () =>
    api.avatar(me, token).then(setAvatar).catch(() => undefined);

  // One camera frame, as a JPEG file the media door already accepts.
  const frameToFile = (angle: string): File | null => {
    const v = videoRef.current;
    if (!v || !v.videoWidth) return null;
    const c = document.createElement("canvas");
    c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext("2d")!.drawImage(v, 0, 0);
    const data = c.toDataURL("image/jpeg", 0.92);
    const bytes = atob(data.split(",")[1]);
    const arr = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
    return new File([arr], `capture-${angle}.jpg`, { type: "image/jpeg" });
  };

  async function startCapture() {
    setError(null); setCaptured([]);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" } });
      setCapturing(true);
      // The ref renders with `capturing`; attach on the next frame.
      requestAnimationFrame(() => {
        if (videoRef.current) videoRef.current.srcObject = stream;
      });
    } catch (e) { fail(e); }
  }

  function stopCapture() {
    const s = videoRef.current?.srcObject as MediaStream | null;
    s?.getTracks().forEach((t) => t.stop());
    setCapturing(false);
  }

  async function snapAngle(angle: string) {
    const file = frameToFile(angle);
    if (!file) return;
    try {
      const saved = await api.uploadMedia(me, file, token);
      setCaptured((c) => [...c, saved.url]);
    } catch (e) { fail(e); }
  }

  async function finishCapture() {
    stopCapture();
    if (captured.length === 0) return;
    try {
      // The first frame taken (front) becomes the portrait; every angle
      // travels with it as provenance.
      await api.importAvatar(me,
        { source: "capture", asset: captured[0], extra: captured.slice(1) },
        token);
      setNote(tr("idn.deck.done", lang));
      setCaptured([]);
      reloadAvatar();
    } catch (e) { fail(e); }
  }

  async function importPhoto(file: File) {
    setError(null); setNote(null);
    try {
      const saved = await api.uploadMedia(me, file, token);
      await api.importAvatar(me, { source: "photos", asset: saved.url }, token);
      setNote(tr("idn.deck.done", lang));
      reloadAvatar();
    } catch (e) { fail(e); }
  }

  async function importMarket() {
    if (!marketUrl.trim()) return;
    setError(null); setNote(null);
    try {
      await api.importAvatar(me,
        { source: marketKey, asset: marketUrl.trim(),
          ...(marketTorso.trim() ? { torso: marketTorso.trim() } : {}) },
        token);
      setNote(tr("idn.deck.done", lang));
      setMarketUrl("");
      reloadAvatar();
    } catch (e) { fail(e); }
  }
  const [emblems, setEmblems] = useState<Emblem[]>([]);
  const [briefs, setBriefs] = useState<AvatarBrief[]>([]);
  const [memorial, setMemorial] = useState<Memorial | null>(null);
  const [gone, setGone] = useState<Deleted | null>(null);
  const [ended, setEnded] = useState<Sunset | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);

  const [level, setLevel] = useState("self_asserted");
  const [attestor, setAttestor] = useState("");
  const [method, setMethod] = useState("");
  const [name, setName] = useState("");
  const [confirmEnd, setConfirmEnd] = useState<"" | "sunset" | "delete">("");

  const fail = (e: unknown) => setError(e);

  useEffect(() => {
    api.identityVocabulary().then((v) => {
      setVocab(v);
      setLevel(v.proofing_levels[0]?.level || "self_asserted");
    }).catch(fail);
    api.emblems().then((r) => setEmblems(r.emblems)).catch(() => undefined);
    api.avatarBriefs().then((r) => setBriefs(r.briefs)).catch(() => undefined);
    api.avatarMarket().then((r) => setMarket(r.sources)).catch(() => undefined);
  }, []);

  function reload() {
    if (!me || !token) return;
    api.siblings(me, token).then((r) => setRoster(r.profiles)).catch(fail);
    api.verification(me, token).then(setVerification).catch(fail);
    api.verifiable(me, token).then(setVerifiable).catch(() => setVerifiable(null));
    api.anonymity(me, token).then(setAnon).catch(fail);
    api.avatar(me, token).then(setAvatar).catch(() => setAvatar(null));
    // 409 while the profile is active, which is the ordinary case rather
    // than a failure worth a banner.
    api.memorial(me).then(setMemorial).catch(() => setMemorial(null));
  }
  useEffect(reload, [me, token]);

  async function claim() {
    setError(null); setNote(null);
    try {
      setVerification(await api.claimVerification(me, {
        level,
        attestor: attestor.trim() || undefined,
        method: method.trim() || undefined,
      }, token));
      setNote("Recorded.");
      reload();
    } catch (e) { fail(e); }   // 422 or 409 — the server's own sentence
  }

  const needsAttestor =
    vocab?.proofing_levels.find((l) => l.level === level)?.needs_attestor ?? false;

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("idn.title", lang)}</h2>
        {/* Beginning and passing on left the sidebar: pre-building an
            account, recovery, and how it ends are options taken from the
            identity they concern. */}
        <button className="chip" onClick={onPassing}>
          {tr("idn.passing", lang)}
        </button>
      </header>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {vocab && (
        <div className="card">
          <h3>{tr("idn.rules", lang)}</h3>
          {/* The backend's own six sentences. */}
          <ul className="small">{vocab.rules.map((r) => <li key={r}>{r}</li>)}</ul>
        </div>
      )}

      <div className="card">
        <h3>{tr("idn.roster", lang)}</h3>
        <p className="muted small">{tr("idn.roster.pitch", lang)}</p>
        {roster.length === 0 && <p className="muted small">{tr("idn.roster.none", lang)}</p>}
        {roster.map((s) => (
          <div key={s.profile_id} className="row">
            <div style={{ flex: 1 }}>
              <strong>{s.shown_as}</strong>
              {s.profile_id === me && <span className="chip"> {tr("idn.roster.thisone", lang)}</span>}
              {s.anonymous && <span className="chip"> {tr("idn.roster.anon", lang)}</span>}
              <div className="muted small">
                {s.kind} · {s.status}
                {s.verified
                  ? <> · <b>{fill(tr("idn.roster.verified", lang),
                       { level: s.level })}</b></>
                  : s.can_be_verified
                    ? <> · {tr("idn.roster.notverified", lang)}</>
                    /* Not the same as "not yet". There is nobody to check. */
                    : <> · {tr("idn.roster.unverifiable", lang)}</>}
              </div>
            </div>
            {/* The badge moves; it is not re-earned. Offered on any sibling
                that could hold it and does not. */}
            {!s.verified && s.can_be_verified && s.profile_id !== me && (
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  const r = await api.moveBadge(s.profile_id, token);
                  setNote(`${r.note} It is now on ${s.shown_as}.`);
                  reload();
                } catch (e) { fail(e); }
              }}>{tr("idn.roster.move", lang)}</button>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("idn.ver", lang)}</h3>
        {verification && !verification.verified && (
          <p className="small">{verification.note}</p>
        )}
        {verification && verification.verified && (
          <>
            <p className="small">
              {fill(tr("idn.ver.means", lang), {
                means: <b>{verification.means}</b>,
                level: verification.level, rank: verification.rank,
              })}
            </p>
            <p className="muted small">
              {verification.attestor
                ? fill(tr("idn.ver.checkedby", lang),
                    { who: verification.attestor })
                : tr("idn.ver.withheld", lang)}
              {verification.method && <> · {verification.method}</>}
              {" · "}{verification.checked_at}
            </p>
            {verification.caveat && (
              <p className="small">{verification.caveat}</p>
            )}
          </>
        )}

        {verifiable && !verifiable.can_verify && (
          <div className="card">
            <p className="small">{verifiable.reason}</p>
            {verifiable.movable && verifiable.held_by && (
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  const r = await api.moveBadge(me, token);
                  setNote(r.note);
                  reload();
                } catch (e) { fail(e); }
              }}>{tr("idn.ver.movehere", lang)}</button>
            )}
          </div>
        )}

        {verifiable?.can_verify && (
          <>
            <div className="row">
              <select value={level} onChange={(e) => setLevel(e.target.value)}>
                {vocab?.proofing_levels.map((l) => (
                  <option key={l.level} value={l.level}>{l.level}</option>
                ))}
              </select>
              <input value={attestor} onChange={(e) => setAttestor(e.target.value)}
                     placeholder={needsAttestor ? "who checked (required)" : "who checked"}
                     style={{ flex: 1 }} />
              <input value={method} onChange={(e) => setMethod(e.target.value)}
                     placeholder={tr("idn.ver.how.ph", lang)} />
              <button disabled={needsAttestor && !attestor.trim()} onClick={claim}>
                {tr("idn.ver.record", lang)}
              </button>
            </div>
            <p className="muted small">
              {vocab?.proofing_levels.find((l) => l.level === level)?.means}
              {needsAttestor && " — who checked is part of the record, not a footnote."}
            </p>
          </>
        )}
      </div>

      {anon && (
        <div className="card">
          <h3>{tr("idn.anon", lang)}</h3>
          <p className="small">
            {fill(tr("idn.anon.shown", lang), {
              name: <strong>{anon.shown_as}</strong>, note: anon.note,
            })}
          </p>
          <div className="row">
            <button onClick={async () => {
              setError(null); setNote(null);
              try {
                const a = await api.setAnonymity(me, !anon.anonymous, token);
                setAnon(a);
                if (a.note_on_change) setNote(a.note_on_change);
                reload();
              } catch (e) { fail(e); }
            }}>
              {anon.anonymous ? "Publish my name again" : "Withhold my name"}
            </button>
            {anon.reversible && (
              <span className="muted small">{tr("idn.anon.reversible", lang)}</span>
            )}
          </div>
          <div className="row">
            <div style={{ flex: 1 }}>
              <h4>{tr("idn.anon.withheld", lang)}</h4>
              <ul className="small">
                {anon.withheld.map((w) => <li key={w}>{w}</li>)}
              </ul>
            </div>
            {/* Same weight, deliberately. This is the half people are
                surprised by, and a screen that showed only the other one
                would be promising something the product does not do. */}
            <div style={{ flex: 1 }}>
              <h4>{tr("idn.anon.notwithheld", lang)}</h4>
              <ul className="small">
                {anon.not_withheld.map((w) => <li key={w}>{w}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h3>{tr("idn.bubble", lang)}</h3>
        {avatar && (
          <>
            <p className="small">
              {avatar.placeholder || avatar.silhouette
                ? "Nothing in it yet."
                : fill(tr("idn.bubble.showing", lang),
                    { asset: <code>{avatar.asset}</code> })}
            </p>
            {/* Always displayed, by the product's own rule — so the screen
                shows it rather than implying it is a setting. */}
            <p className="muted small">
              {avatar.watermark.line} — {avatar.watermark.disclosure}
            </p>
            <p className="muted small">{avatar.likeness.note}</p>
          </>
        )}
        <div className="row">
          {emblems.slice(0, 8).map((e) => (
            <button key={e.emblem} className="chip" onClick={async () => {
              setError(null); setNote(null);
              try {
                const r = await api.setEmblem(me, e.emblem, token);
                setNote(`${e.means} — ${r.note}`);
                api.avatar(me, token).then(setAvatar).catch(() => undefined);
              } catch (err) { fail(err); }
            }}>{e.emblem}</button>
          ))}
        </div>
        {/* ---- the avatar deck ---------------------------------------
            Three shelves. Characters: the starter portraits, pick one and
            it becomes the face. Your own face: import a photo, or capture
            it from several angles with the camera. Market: an avatar the
            person already owns somewhere else, imported — the provider's
            license governs it, and the import is on the record. */}
        <h4>{tr("idn.deck.characters", lang)}</h4>
        {/* The asset path comes from the brief itself — the server names
            where its portraits live; the client never spells a path. */}
        <div className="deck-grid">
          {briefs.filter((b) => b.asset).slice(0, 12).map((b) => (
            <button key={b.handle} className="deck-face" title={b.handle}
                    onClick={async () => {
                      setError(null); setNote(null);
                      try {
                        await api.setAvatar(me, b.asset!, token);
                        setNote(tr("idn.deck.done", lang));
                        reloadAvatar();
                      } catch (e) { fail(e); }
                    }}>
              <img src={getBase() + b.asset} alt={b.handle} loading="lazy" />
            </button>
          ))}
        </div>

        <h4>{tr("idn.deck.own", lang)}</h4>
        <p className="muted small">{tr("idn.deck.own.sub", lang)}</p>
        <div className="row">
          <label className="chip" style={{ marginBottom: 0 }}>
            {tr("idn.deck.upload", lang)}
            <input type="file" accept="image/*" style={{ display: "none" }}
                   onChange={(e) => {
                     const f = e.target.files?.[0];
                     if (f) importPhoto(f);
                     e.target.value = "";
                   }} />
          </label>
          {!capturing ? (
            <button className="chip" onClick={startCapture}>
              {tr("idn.deck.capture", lang)}
            </button>
          ) : (
            <button className="chip" onClick={finishCapture}
                    disabled={captured.length === 0}>
              {tr("idn.deck.capture.done", lang)}
            </button>
          )}
        </div>
        {capturing && (
          <div className="capture">
            <video ref={videoRef} autoPlay playsInline muted />
            <div className="row">
              {captureAngles.map((a) => (
                <button key={a} className="chip"
                        disabled={captured.length >= captureAngles.length}
                        onClick={() => snapAngle(a)}>
                  {tr(`idn.deck.angle.${a}`, lang)}
                </button>
              ))}
            </div>
            <p className="muted small">
              {fill(tr("idn.deck.frames", lang),
                    { n: captured.length, total: captureAngles.length })}
            </p>
          </div>
        )}

        <h4>{tr("idn.deck.market", lang)}</h4>
        <p className="muted small">{tr("idn.deck.market.sub", lang)}</p>
        <div className="row">
          <select value={marketKey}
                  onChange={(e) => setMarketKey(e.target.value)}>
            {market.map((m) => (
              <option key={m.key} value={m.key}>{m.name}</option>
            ))}
          </select>
          <input value={marketUrl} placeholder={tr("idn.deck.url.ph", lang)}
                 onChange={(e) => setMarketUrl(e.target.value)}
                 style={{ flex: 1 }} />
          {/* Optional: the same avatar's upper-torso export, for surfaces
              that stand the figure in a scene at 1:1. */}
          <input value={marketTorso}
                 placeholder={tr("idn.deck.torso.ph", lang)}
                 onChange={(e) => setMarketTorso(e.target.value)}
                 style={{ flex: 1 }} />
          <button disabled={!marketUrl.trim()} onClick={importMarket}>
            {tr("idn.deck.import", lang)}
          </button>
        </div>
        {market.find((m) => m.key === marketKey) && (
          <p className="muted small">
            {market.find((m) => m.key === marketKey)!.how}
          </p>
        )}

        {briefs.length > 0 && (
          <>
            <h4>{tr("idn.bubble.portrait", lang)}</h4>
            <p className="muted small">{tr("idn.bubble.brief", lang)}</p>
            {briefs.slice(0, 3).map((b) => (
              <div key={b.handle} className="row">
                <div style={{ flex: 1 }}>
                  <strong>{b.handle}</strong>
                  <div className="muted small">{b.portrait}</div>
                </div>
                <button onClick={async () => {
                  setError(null); setNote(null);
                  try {
                    const full = await api.avatarBrief(b.handle);
                    setNote(full.prompt || full.portrait);
                  } catch (e) { fail(e); }
                }}>{tr("idn.bubble.prompt", lang)}</button>
              </div>
            ))}
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("idn.rename", lang)}</h3>
        <div className="row">
          <input value={name} onChange={(e) => setName(e.target.value)}
                 placeholder={tr("idn.rename.ph", lang)} style={{ flex: 1 }} />
          <button disabled={!name.trim()} onClick={async () => {
            setError(null); setNote(null);
            try {
              await api.editProfile(me, { display_name: name.trim() }, token);
              setNote("Renamed."); setName(""); reload();
            } catch (e) { fail(e); }
          }}>{tr("idn.rename.save", lang)}</button>
        </div>
      </div>

      <div className="card">
        <h3>{tr("idn.export", lang)}</h3>
        <p className="muted small">{tr("idn.export.pitch", lang)}</p>
        <button onClick={async () => {
          setError(null); setNote(null);
          try {
            const data = await api.exportProfile(me, token);
            setNote(`Exported: ${Object.keys(data).join(", ")}.`);
          } catch (e) { fail(e); }
        }}>{tr("idn.export.go", lang)}</button>
      </div>

      {memorial && (
        <div className="card">
          <h3>{tr("idn.mem", lang)}</h3>
          <p className="small">{memorial.note}</p>
          <p className="muted small">
            {fill(tr("idn.mem.line", lang), {
              status: memorial.status, n: memorial.relationships_touched,
              s: memorial.relationships_touched === 1 ? "" : "s",
            })}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{tr("idn.end", lang)}</h3>
        <p className="muted small">{tr("idn.end.pitch", lang)}</p>

        <div className="row">
          <div style={{ flex: 1 }}>
            <strong>{tr("idn.end.retire", lang)}</strong>
            <div className="muted small">
              {tr("idn.end.retire.note", lang)}
            </div>
          </div>
          {confirmEnd === "sunset" ? (
            <button onClick={async () => {
              setError(null); setNote(null); setConfirmEnd("");
              try {
                setEnded(await api.sunsetProfile(me, token));
                reload();
              } catch (e) { fail(e); }
            }}>{tr("idn.end.retire.yes", lang)}</button>
          ) : (
            <button onClick={() => setConfirmEnd("sunset")}>{tr("idn.end.retire", lang)}</button>
          )}
        </div>
        {ended && (
          <p className="small">
            {fill(tr("idn.end.sunset.line", lang), {
              status: ended.status, n: ended.farewells,
              s: ended.farewells === 1 ? "" : "s", memory: ended.memory,
            })}
          </p>
        )}

        <div className="row">
          <div style={{ flex: 1 }}>
            <strong>{tr("idn.end.delete", lang)}</strong>
            <div className="muted small">
              {tr("idn.end.delete.note", lang)}
            </div>
          </div>
          {confirmEnd === "delete" ? (
            <button onClick={async () => {
              setError(null); setNote(null); setConfirmEnd("");
              try {
                setGone(await api.deleteProfile(me, token));
              } catch (e) { fail(e); }
            }}>{tr("idn.end.delete.yes", lang)}</button>
          ) : (
            <button onClick={() => setConfirmEnd("delete")}>{tr("idn.end.delete", lang)}</button>
          )}
        </div>
        {/* The receipt, itemised. "Deleted" is a claim; these are evidence,
            and the row that reads `profile: 1` is the one that matters. */}
        {gone && (
          <>
            <h4>{tr("idn.end.erased", lang)}</h4>
            <ul className="small">
              {Object.entries(gone.deleted)
                .filter(([, n]) => n > 0)
                .map(([table, n]) => <li key={table}>{table}: {n}</li>)}
            </ul>
            <p className="muted small">
              {fill(tr("idn.end.zeros", lang), {
                n: Object.values(gone.deleted).filter((n) => n === 0).length,
              })}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
