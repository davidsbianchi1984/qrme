import { useEffect, useState } from "react";
import { api, getBase, type Avatar } from "./api";
import { t as tr, visitorLang } from "./l10n";

// The full-screen face: tap the avatar ring and the render takes the
// screen, the way an uploaded room background does — same takeover, same
// feel — with the same settings-wheel pattern the room seats wear.
//
// Down the right edge runs a rail of hidden windows, the way the room's
// four panels do: the prompt bar alone, the wardrobe (apparel, jewelry,
// hair, backdrop), and the body (physique, gender). Each opens the same
// card filtered to its half; the wheel opens everything. The center is
// always the prompt bar — "users should be able to get away with
// prompting for what they want" — and the chips are canned prompts for
// people who don't want to type. Every tap and every sentence goes
// through the one painting door the platform has (portraitist.paint:
// house style, the profile's brief, its age as it is today, the AI mark
// burned in), so the wardrobe cannot say anything the platform wouldn't.
//
// Who gets the bar: the owner always, and — while the profile's
// guest_styling switch is on, which it is by default — anyone talking to
// it. The owner's switch lives here too, on their own view of the card.
//
// The doctrine gate renders instead of hiding: a real person's face is
// never painted from words — that is the platform's own deepfake line,
// and it protects the owner most of all — so a real-likeness profile sees
// the sentence and the import road, not a broken prompt bar.
type Rail = "prompt" | "looks" | "body" | "all";

export function AvatarStage({ profileId, token, avatar, owned, clear,
                              onClose, onChanged, onError }: {
  profileId: string;
  token: string;
  /** Null when the profile has no face yet — the stage opens on the empty
   *  frame and the wardrobe paints the first one. */
  avatar: Avatar | null;
  /** Does this surface hold the profile's owner token. Decides whether
   *  the guest switch is shown, and paints past a closed wardrobe. */
  owned?: boolean;
  /** Let the scene behind show through — an AR room's passthrough, a VR
   *  room's stage — so the avatar stands in the environment instead of
   *  on a black card. Flat surfaces keep the dark takeover. */
  clear?: boolean;
  onClose: () => void;
  onChanged: (a: Avatar) => void;
  onError: (e: unknown) => void;
}) {
  const lang = visitorLang();
  const [kind, setKind] = useState<string | null>(null);
  const [guestsOk, setGuestsOk] = useState(true);
  const [rail, setRail] = useState<Rail | null>(null);
  const [words, setWords] = useState("");
  const [busy, setBusy] = useState(false);
  const [face, setFace] = useState<Avatar | null>(avatar);

  useEffect(() => {
    api.getProfile(profileId).then((p) => {
      setKind(p.kind);
      setGuestsOk(p.guest_styling !== false);
    }).catch(() => setKind(null));
  }, [profileId]);

  const fictional = kind === "fictional";
  const paintable = fictional && (owned || guestsOk);
  // The whole figure when the platform holds one, the face otherwise —
  // the stage is a person standing in a frame, not a passport photo.
  const art = face?.torso || face?.asset || null;
  const src = art
    ? (art.startsWith("http") ? art : getBase() + art)
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

  async function setGuests(open: boolean) {
    setGuestsOk(open);
    try { await api.editProfile(profileId, { guest_styling: open }, token); }
    catch (e) { setGuestsOk(!open); onError(e); }
  }

  // Canned prompts, not separate systems: a chip fills the bar with a
  // starting sentence the person can edit before painting. Age never
  // appears here — the render is always at the profile's own age.
  const CHIPS: { key: string; seed: string;
                 cat: Exclude<Rail, "prompt" | "all"> }[] = [
    { key: "ward.apparel", seed: "wearing a worn leather jacket",
      cat: "looks" },
    { key: "ward.apparel2", seed: "in formal evening wear", cat: "looks" },
    { key: "ward.hair", seed: "with a completely new hairstyle",
      cat: "looks" },
    { key: "ward.hair2", seed: "with much shorter hair", cat: "looks" },
    { key: "ward.jewelry", seed: "wearing a silver chain and rings",
      cat: "looks" },
    { key: "ward.backdrop", seed: "against a warm sunset backdrop",
      cat: "looks" },
    { key: "ward.physique", seed: "with a broader, stronger build",
      cat: "body" },
    { key: "ward.physique2", seed: "with a slighter, leaner build",
      cat: "body" },
    { key: "ward.gender", seed: "presenting more femininely", cat: "body" },
    { key: "ward.gender2", seed: "presenting more masculinely",
      cat: "body" },
  ];
  const chips = rail === "looks" || rail === "body"
    ? CHIPS.filter((c) => c.cat === rail)
    : CHIPS;

  const RAIL: { key: Rail; glyph: string; labelKey: string }[] = [
    { key: "prompt", glyph: "✏️", labelKey: "stage.prompt" },
    { key: "looks", glyph: "\u{1F457}", labelKey: "stage.ward" },
    { key: "body", glyph: "\u{1F9CD}", labelKey: "stage.body" },
  ];

  return (
    <div className={"avatar-stage" + (clear ? " clear" : "")} role="dialog"
         aria-label={tr("stage.title", lang)}>
      {src
        ? <img className={"stage-face" + (face?.torso ? " standing" : "")}
               src={src} alt="" />
        : <div className="stage-empty">{tr("stage.none", lang)}</div>}
      <span className="stage-mark" aria-hidden="true">✦ AI</span>
      <button className="stage-close" aria-label={tr("stage.close", lang)}
              title={tr("stage.close", lang)}
              onClick={onClose}>✕</button>
      <div className="stage-rail">
        {RAIL.map((w) => (
          <button key={w.key} className={rail === w.key ? "lit" : ""}
                  aria-label={tr(w.labelKey, lang)}
                  title={tr(w.labelKey, lang)}
                  onClick={() =>
                    setRail((r) => r === w.key ? null : w.key)}>
            {w.glyph}
          </button>
        ))}
        <button className={rail === "all" ? "lit" : ""} aria-pressed={!!rail}
                aria-label={tr("stage.wheel", lang)}
                title={tr("stage.wheel", lang)}
                onClick={() => setRail((r) => r === "all" ? null : "all")}>
          ⚙️
        </button>
      </div>
      {rail && (
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
              {rail !== "prompt" && (
                <div className="ward-chips">
                  {chips.map((c) => (
                    <button key={c.key} className="chip" disabled={busy}
                            onClick={() => setWords(c.seed)}>
                      {tr(c.key, lang)}
                    </button>
                  ))}
                </div>
              )}
              <p className="muted small">{tr("ward.age", lang)}</p>
            </>
          ) : fictional && !owned ? (
            // The wardrobe exists and the owner shut it. Said, not hidden.
            <p className="muted small">{tr("ward.locked", lang)}</p>
          ) : (
            // The gate, said instead of hidden: real faces arrive by
            // photograph under a recorded grant, never by prompt.
            <p className="muted small">{tr("ward.real", lang)}</p>
          )}
          {owned && fictional && (
            <label className="ward-switch">
              <input type="checkbox" checked={guestsOk}
                     onChange={(e) => void setGuests(e.target.checked)} />
              {tr("ward.guests", lang)}
            </label>
          )}
        </div>
      )}
    </div>
  );
}
