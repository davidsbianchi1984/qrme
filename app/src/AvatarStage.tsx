import { useEffect, useState } from "react";
import { api, getBase, type Avatar } from "./api";
import { t as tr, visitorLang } from "./l10n";

// The full-screen face: tap the avatar ring and the render takes the
// screen, the way an uploaded room background does — same takeover, same
// feel — with the same settings-wheel pattern the room seats wear.
//
// The wheel opens the wardrobe. Its center is the prompt bar — "users
// should be able to get away with prompting for what they want" — and the
// chips are canned prompts for people who don't want to type. Every tap
// and every sentence goes through the one painting door the platform has
// (portraitist.paint: house style, the profile's brief, its age as it is
// today, the AI mark burned in), so the wardrobe cannot say anything the
// platform wouldn't.
//
// The doctrine gate renders instead of hiding: a real person's face is
// never painted from words — that is the platform's own deepfake line,
// and it protects the owner most of all — so a real-likeness profile sees
// the sentence and the import road, not a broken prompt bar.
export function AvatarStage({ profileId, token, avatar, onClose, onChanged,
                              onError }: {
  profileId: string;
  token: string;
  avatar: Avatar;
  onClose: () => void;
  onChanged: (a: Avatar) => void;
  onError: (e: unknown) => void;
}) {
  const lang = visitorLang();
  const [kind, setKind] = useState<string | null>(null);
  const [wheel, setWheel] = useState(false);
  const [words, setWords] = useState("");
  const [busy, setBusy] = useState(false);
  const [face, setFace] = useState<Avatar>(avatar);

  useEffect(() => {
    api.getProfile(profileId).then((p) => setKind(p.kind))
      .catch(() => setKind(null));
  }, [profileId]);

  const paintable = kind === "fictional";
  const src = face.asset
    ? (face.asset.startsWith("http") ? face.asset : getBase() + face.asset)
    : null;

  async function paint(direction: string) {
    if (!direction.trim() || busy) return;
    setBusy(true);
    try {
      const a = await api.paintFace(profileId, direction.trim(), token);
      setFace(a);
      onChanged(a);
      setWords("");
    } catch (e) { onError(e); }
    finally { setBusy(false); }
  }

  // Canned prompts, not separate systems: a chip fills the bar with a
  // starting sentence the person can edit before painting. Age never
  // appears here — the render is always at the profile's own age.
  const CHIPS: [string, string][] = [
    ["ward.apparel", "wearing a worn leather jacket"],
    ["ward.apparel2", "in formal evening wear"],
    ["ward.hair", "with a completely new hairstyle"],
    ["ward.hair2", "with much shorter hair"],
    ["ward.physique", "with a broader, stronger build"],
    ["ward.physique2", "with a slighter, leaner build"],
    ["ward.gender", "presenting more femininely"],
    ["ward.gender2", "presenting more masculinely"],
    ["ward.jewelry", "wearing a silver chain and rings"],
    ["ward.backdrop", "against a warm sunset backdrop"],
  ];

  return (
    <div className="avatar-stage" role="dialog"
         aria-label={tr("stage.title", lang)}>
      {src
        ? <img className="stage-face" src={src} alt="" />
        : <div className="stage-empty">{tr("stage.none", lang)}</div>}
      <span className="stage-mark" aria-hidden="true">✦ AI</span>
      <button className="stage-close" aria-label={tr("stage.close", lang)}
              title={tr("stage.close", lang)}
              onClick={onClose}>✕</button>
      <button className="stage-wheel" aria-pressed={wheel}
              aria-label={tr("stage.wheel", lang)}
              title={tr("stage.wheel", lang)}
              onClick={() => setWheel((w) => !w)}>⚙️</button>
      {wheel && (
        <div className="wardrobe card">
          {paintable ? (
            <>
              <div className="tile-label">{tr("ward.title", lang)}</div>
              <div className="ward-prompt">
                <input value={words} disabled={busy}
                       placeholder={tr("ward.ph", lang)}
                       onChange={(e) => setWords(e.target.value)}
                       onKeyDown={(e) => {
                         if (e.key === "Enter") void paint(words);
                       }} />
                <button disabled={busy || !words.trim()}
                        onClick={() => void paint(words)}>
                  {busy ? tr("ward.painting", lang) : tr("ward.paint", lang)}
                </button>
              </div>
              <div className="ward-chips">
                {CHIPS.map(([key, seed]) => (
                  <button key={key} className="chip" disabled={busy}
                          onClick={() => setWords(seed)}>
                    {tr(key, lang)}
                  </button>
                ))}
              </div>
              <p className="muted small">{tr("ward.age", lang)}</p>
            </>
          ) : (
            // The gate, said instead of hidden: real faces arrive by
            // photograph under a recorded grant, never by prompt.
            <p className="muted small">{tr("ward.real", lang)}</p>
          )}
        </div>
      )}
    </div>
  );
}
