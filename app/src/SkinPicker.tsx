import { useEffect, useState } from "react";
import { api, getBase, type Avatar, type RegistryRow } from "./api";
import { AvatarStage } from "./AvatarStage";
import { fill, t as tr, visitorLang } from "./l10n";
import { SkinTiles, type SkinSource } from "./SkinTiles";

// Bring a character skin from somewhere you already have one, where you are
// looking at the face — the way the model picker and the voice picker work.
//
// The shelf is old: `GET /avatars/market` has named eight systems since the
// avatar deck was written, each with the provider's own export route. Its
// only door was a dropdown beside a URL box on Identity, which is a form
// rather than a picker, and it is not where a person is when they are
// looking at their own avatar.
//
//     asked     can an owner bring a face from somewhere else
//     mattered  can they do it while looking at the one they have
//
// Imports, not integrations. QRME never holds a provider credential: you
// export on their surface and hand the result over here, and the AI badge
// and the likeness record ride on it like any other portrait.
export function SkinPicker({ profileId, token, onError, onChanged }: {
  profileId: string;
  token: string;
  onError: (e: unknown) => void;
  /** So the surface showing the avatar can re-read it after a change. */
  onChanged?: (a: Avatar) => void;
}) {
  const lang = visitorLang();
  const [sources, setSources] = useState<SkinSource[]>([]);
  const [chosen, setChosen] = useState("ready_player_me");
  const [url, setUrl] = useState("");
  const [torso, setTorso] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");
  const [worn, setWorn] = useState<Avatar | null>(null);
  const [providerId, setProviderId] = useState("");
  const [staged, setStaged] = useState(false);
  // The deployment's shelf: the default faces the operator stocked — the
  // ElevenLabs collection under the house key, and whatever else was put
  // up. Tapping one claims it, so "pick a default" is one press and not
  // a form. The registry link is the point: a retired row leaves every
  // profile that wore it at once.
  const [shelfRows, setShelfRows] = useState<RegistryRow[]>([]);

  useEffect(() => {
    api.avatarMarket().then((r) => setSources(r.skin_sources)).catch(() => setSources([]));
    api.avatarShelf().then((r) => setShelfRows(r.shelf))
      .catch(() => setShelfRows([]));
  }, []);
  useEffect(() => { void reload(); }, [profileId]);

  async function reload() {
    try {
      const a = await api.avatar(profileId, token);
      setWorn(a);
      onChanged?.(a);
    } catch { setWorn(null); }
  }

  async function bring() {
    if (!url.trim()) return;
    setBusy(true); setNote("");
    try {
      await api.importAvatar(profileId, {
        source: chosen, asset: url.trim(),
        ...(torso.trim() ? { torso: torso.trim() } : {}),
        ...(providerId.trim()
          ? { provider_asset_id: providerId.trim() } : {}),
      }, token);
      setUrl(""); setTorso(""); setProviderId("");
      setNote(tr("idn.deck.done", lang));
      await reload();
    } catch (e) { onError(e); }
    finally { setBusy(false); }
  }

  // Uploading is the other half of "or paste a link": a person who exported a
  // file rather than a URL has one on disk, and telling them to host it first
  // is telling them to do our job.
  async function upload(file: File) {
    setBusy(true); setNote("");
    try {
      const saved = await api.uploadMedia(profileId, file, token);
      await api.importAvatar(profileId,
                             { source: chosen, asset: saved.url }, token);
      setNote(tr("idn.deck.done", lang));
      await reload();
    } catch (e) { onError(e); }
    finally { setBusy(false); }
  }

  async function wear(row: RegistryRow) {
    setBusy(true); setNote("");
    try {
      await api.claimFace(profileId, row.id, token);
      setNote(tr("idn.deck.done", lang));
      await reload();
    } catch (e) { onError(e); }
    finally { setBusy(false); }
  }

  const kind = worn?.presentation?.kind || "image";

  return (
    <div className="skin-picker">
      {/* The default faces, first: most people pick, few import. */}
      <div className="tile-label">{tr("idn.deck.defaults", lang)}</div>
      <p className="muted small">{tr("idn.deck.defaults.sub", lang)}</p>
      {shelfRows.length === 0 ? (
        <p className="muted small">{tr("idn.deck.defaults.none", lang)}</p>
      ) : (
        <div className="shelf-grid">
          {shelfRows.map((r) => (
            <button key={r.id} className="shelf-face" disabled={busy}
                    title={r.label || r.provider}
                    aria-label={r.label || r.provider}
                    onClick={() => void wear(r)}>
              <img alt="" src={r.asset.startsWith("http")
                ? r.asset : getBase() + r.asset} />
              {r.marked && (
                <span className="shelf-mark" aria-hidden="true">✦</span>
              )}
            </button>
          ))}
        </div>
      )}
      <div className="tile-label">{tr("idn.deck.market", lang)}</div>
      <p className="muted small">{tr("idn.deck.market.sub", lang)}</p>
      <SkinTiles sources={sources} chosen={chosen} onPick={setChosen}
                 busy={busy} />
      <div className="pp-bc-add">
        <input type="url" value={url} disabled={busy}
               placeholder={tr("idn.deck.url.ph", lang)}
               aria-label={tr("idn.deck.url.ph", lang)}
               onChange={(e) => setUrl(e.target.value)}
               onKeyDown={(e) => {
                 if (e.key === "Enter") { e.preventDefault(); void bring(); }
               }} />
        <input type="text" value={torso} disabled={busy}
               placeholder={tr("idn.deck.torso.ph", lang)}
               aria-label={tr("idn.deck.torso.ph", lang)}
               onChange={(e) => setTorso(e.target.value)} />
        <input type="text" value={providerId} disabled={busy}
               placeholder={tr("idn.deck.pid.ph", lang)}
               aria-label={tr("idn.deck.pid.ph", lang)}
               onChange={(e) => setProviderId(e.target.value)} />
        <button disabled={busy || !url.trim()} onClick={bring}>
          {tr("idn.deck.import", lang)}
        </button>
        <input type="file" disabled={busy}
               aria-label={tr("idn.deck.upload", lang)}
               onChange={(e) => {
                 const f = e.target.files?.[0];
                 e.target.value = "";
                 if (f) void upload(f);
               }} />
      </div>
      {note && <p className="muted small">{note}</p>}

      {/* What is actually on, in the words of what it *is* rather than of
          what it points at. This is the half the shelf never had: an owner
          who pasted a `.glb` had no way to learn whether anything downstream
          knew it was a model. */}
      {worn && (
        <p className="muted small">
          {fill(tr("skin.now", lang), { kind: tr(`skin.kind.${kind}`, lang) })}
          {worn.presentation && !CONSOLE_RENDERS.includes(kind) && (
            <> {tr("skin.notshown", lang)}</>
          )}
        </p>
      )}
      {/* The avatar ring: the worn face, tappable — tap it and the
        * render takes the screen, wheel and wardrobe with it. */}
      {worn?.asset && CONSOLE_RENDERS.includes(kind) && (
        <button className="skin-ring" aria-label={tr("stage.open", lang)}
                title={tr("stage.open", lang)}
                onClick={() => setStaged(true)}>
          <img className="skin-preview" alt=""
               src={worn.asset.startsWith("http") ? worn.asset
                                                  : getBase() + worn.asset} />
        </button>
      )}
      {staged && worn && (
        <AvatarStage profileId={profileId} token={token} avatar={worn}
                     owned
                     onClose={() => setStaged(false)}
                     onChanged={(a) => { setWorn(a); onChanged?.(a); }}
                     onError={onError} />
      )}
    </div>
  );
}

/** What this console can draw. A kind outside it is still imported, still on
 *  the record, and still reaches surfaces that can run it — the screen says
 *  so rather than rendering a poster and letting an owner believe their model
 *  is on screen. */
const CONSOLE_RENDERS = ["image", "video"];
