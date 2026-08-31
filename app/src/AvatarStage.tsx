import { useEffect, useState } from "react";
import { Avatar3D, type Shot } from "./Avatar3D";
import { SpeakingPortrait } from "./SpeakingPortrait";
import { nowPlaying } from "./spoken";
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
                              inline, framing, onFraming, onExpand,
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
  /** Run in a frame instead of over the whole screen.
   *
   * The owner's correction, and the reason this is one component in two
   * sizes rather than two components: "the avatars can run inside of
   * windows like these... but if they don't wanna go full screen, you'll
   * still have to add those four buttons that allow you to change the
   * wardrobe or body."
   *
   *     asked     where does the avatar go
   *     mattered  do the four controls come with it
   *
   * They do, because it is the same code. A second, smaller avatar
   * component would have been a second wardrobe to keep in step, and the
   * one in the frame would have drifted into being the poor relation —
   * which is how a control ends up existing only in the mode nobody
   * uses. */
  inline?: boolean;
  /** How much of the rendered avatar is in the frame.
   *
   *  Deliberately not called `shot`. That word is already taken here by
   *  the framing of the photograph going IN to the forge, and the two
   *  are different pictures — somebody can hand over a head-and-
   *  shoulders photograph and still want the whole body drawn from the
   *  model built out of it. */
  framing?: Shot;
  onFraming?: (s: Shot) => void;
  /** Take the frame to the whole screen. Drawn in place of the close
   *  button when inline: filling a window and closing a screen are
   *  different actions and must not share a glyph. */
  onExpand?: () => void;
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
  const [shot, setShot] = useState("face");
  // Where this face's points sit, fetched once when the profile carries
  // a measurement. A small JSON beside the picture, not a model.
  const [speech, setSpeech] = useState<Parameters<
    typeof SpeakingPortrait>[0]["map"] | null>(null);

  useEffect(() => {
    const where = face?.speaking;
    if (!where) { setSpeech(null); return; }
    let stop = false;
    fetch(where.startsWith("http") ? where : getBase() + where)
      .then((r) => r.json())
      .then((m) => { if (!stop) setSpeech(m); })
      // A measurement that will not load leaves the still standing,
      // which is a perfectly good portrait and always was.
      .catch(() => { if (!stop) setSpeech(null); });
    return () => { stop = true; };
  }, [face?.speaking]);

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

  /** The import road the doctrine gate always promised and never drew.
   *
   * The rail's three windows all landed on the same sentence — "a real
   * person's face is never painted from words" — because for a real
   * likeness there was nothing else on the card. Four buttons, one
   * refusal, repeated: the field read that as four broken buttons, and
   * it was right that nothing worked. The sentence stands, and under it
   * is the thing that does work: a photograph, through the forge, which
   * is how a real face has always been allowed to arrive.
   */
  async function forgeFrom(file: File | undefined) {
    if (!file || busy) return;
    setBusy(true);
    try {
      const bytes = new Uint8Array(await file.arrayBuffer());
      let binary = "";
      // Chunked — one apply() over a multi-megabyte photograph blows the
      // argument limit on every browser that matters.
      for (let at = 0; at < bytes.length; at += 0x8000) {
        binary += String.fromCharCode(...bytes.subarray(at, at + 0x8000));
      }
      const built = await api.speakingFace(profileId, btoa(binary),
                                          shot, token);
      setFace(built.avatar);
      onChanged(built.avatar);
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
    <div className={"avatar-stage" + (clear ? " clear" : "")
                    + (inline ? " inline" : "")}
         data-screen="205"
         /* A window in a frame is not a dialog: `role="dialog"` on
            something that has not taken the screen tells a screen reader
            everything behind it is inert, which is false — the room is
            still there and still usable. */
         role={inline ? "group" : "dialog"}
         aria-modal={inline ? undefined : true}
         aria-label={tr("stage.title", lang)}>
      {/* The head the forge built, when there is one: the same face in
          three dimensions, its mouth moving with whatever voice is in
          the air. The still is what a face without a model shows, and
          what shows while the model is still loading — a component that
          nothing mounted is the failure this replaces (the `.glb` was
          built, stored and served for a release before any screen drew
          it), so the drawing lives here rather than in a file the
          census merely knew about. */}
      {/* The photograph, moving — preferred over the head whenever this
          face has been measured, because it goes on looking like the
          person and a landmark head cannot. The head is still drawn for
          a face that only has one. */}
      {speech && src
        ? <SpeakingPortrait src={src} map={speech}
                            speaking={nowPlaying()}
                            className="stage-face" />
        : face?.model
        ? <Avatar3D src={face.model.startsWith("http")
                          ? face.model : getBase() + face.model}
                    speaking={nowPlaying()}
                    motion={face.motion}
                    shot={framing}
                    className="stage-face" />
        : src
        ? <img className={"stage-face" + (face?.torso ? " standing" : "")}
               src={src} alt="" />
        : <div className="stage-empty">{tr("stage.none", lang)}</div>}
      <span className="stage-mark" aria-hidden="true">✦ AI</span>
      {inline
        ? <button className="stage-grow" aria-label={tr("stage.full", lang)}
                  title={tr("stage.full", lang)}
                  onClick={onExpand}>⛶</button>
        : <button className="stage-close" aria-label={tr("stage.close", lang)}
                  title={tr("stage.close", lang)}
                  onClick={onClose}>✕</button>}
      {/* Face, upper torso, full body — the forge's own three words, so
          choosing here is choosing what the face was built as. Drawn only
          where something asked to be told; the takeover inherits whatever
          the frame was set to. */}
      {inline && onFraming && (
        <div className="stage-shots">
          {/* Written out rather than mapped from a list of keys: a lookup
              built with a template literal is invisible to the string
              extractor next door. */}
          {([["face", tr("idn.forge.face", lang)],
             ["upper", tr("idn.forge.upper", lang)],
             ["full", tr("idn.forge.full", lang)]] as const).map(
            ([key, name]) => (
              <button key={key} type="button"
                      className={framing === key ? "lit" : ""}
                      aria-pressed={framing === key}
                      onClick={() => onFraming(key)}>{name}</button>
            ))}
        </div>
      )}
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
        <button className={rail === "all" ? "lit" : ""}
                aria-pressed={rail === "all"}
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
            // The gate, said instead of hidden — and then the road that
            // is open, because a card that only says no is a card the
            // field reads as a broken button.
            <>
              <p className="muted small">{tr("ward.real", lang)}</p>
              {owned && (
                <div className="ward-import">
                  <label>{tr("ward.shot", lang)}
                    <select value={shot} disabled={busy}
                            onChange={(e) => setShot(e.target.value)}>
                      <option value="face">{tr("ward.shot.face", lang)}</option>
                      <option value="upper">{tr("ward.shot.upper", lang)}</option>
                      <option value="full">{tr("ward.shot.full", lang)}</option>
                    </select>
                  </label>
                  <input type="file" accept="image/*" disabled={busy}
                         aria-label={tr("ward.photo", lang)}
                         onChange={(e) =>
                           void forgeFrom(e.target.files?.[0] ?? undefined)} />
                  <p className="muted small">
                    {busy ? tr("ward.building", lang) : tr("ward.photo.note", lang)}
                  </p>
                </div>
              )}
            </>
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
