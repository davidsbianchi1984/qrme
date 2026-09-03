import { useEffect, useState } from "react";
import { api, getBase, type SceneRender } from "./api";
import { t as tr, type Lang } from "./l10n";
import { mediaIdOf, playable, useRenderRow } from "./sceneRender";

/**
 * The turn, as footage, in the room's own frame.
 *
 * A turn on the video road comes back with a row, not a video: rendering
 * is minutes and a reply is not, so `auto_render` starts the job, records
 * it, and returns. This is the other end of that — it polls the row until
 * it settles and plays what came back.
 *
 *     asked     show the room's video
 *     mattered  show THIS turn's video, where the turn is
 *
 * ## It shows; it does not commission
 *
 * Nothing here starts a render. Whether a profile's replies become
 * footage is `presence_road` on the server, set by the person whose
 * ceiling it spends. A viewer switching their own screen to the video
 * format is saying "draw me what exists", and a frame with no footage
 * falls down the list to the avatar or the photograph — because the
 * alternative is a screen that spends somebody else's money by being
 * looked at.
 *
 * ## Full screen, and the way out of it
 *
 * The expand sits in the bottom-right of the frame, and full screen
 * carries a red X. Both were asked for in those words. The X is red and
 * it is the only red thing on the surface: somebody who has just filled
 * their screen with a video needs the way out to be the thing they see
 * first, not a control they have to hunt for along an edge.
 */
export function SeatFilm({ profileId, display, talking, lang, onFull,
                           turn }: {
  profileId: string;
  display: string;
  /** The id of this profile's newest turn in the transcript. Footage is
   *  fetched once per profile — a render outlives the page — but a NEW
   *  turn can carry new footage, and a frame keyed only on the profile
   *  showed the room yesterday's film while today's finished rendering.
   *  Field report: "I'm not seeing any videos render when a chat is
   *  coming my way." The turn id re-asks; it still never commissions. */
  turn?: string | null;
  /** Whether this is the turn the room is on. The frame wears the same
   *  green the seat does, so the eye joins the person to their footage. */
  talking: boolean;
  lang: Lang;
  /** Told when the film goes full screen or comes back, so the room can
   *  stop drawing everything behind it. */
  onFull?: (full: boolean) => void;
}) {
  const [scene, setScene] = useState<SceneRender | null>(null);
  const [full, setFull] = useState(false);
  const { row, gaveUp } = useRenderRow(
    scene ?? { status: "none" } as SceneRender);

  // What this profile has already rendered. Asked once per profile: a
  // render outlives the page, so arriving in a room is exactly when
  // there is something to find.
  useEffect(() => {
    let live = true;
    setFull(false);
    api.videoLatest(profileId)
      .then((r) => { if (live) setScene(r.scene); })
      .catch(() => undefined);
    return () => { live = false; };
  }, [profileId, turn]);

  useEffect(() => { onFull?.(full); }, [full]);

  // Leaving the room, or the turn moving on, closes the full screen with
  // it. A takeover that outlives the thing it took over is a screen
  // nobody can get out of.
  useEffect(() => () => { onFull?.(false); }, []);

  const ready = row.status === "done" && row.video_url;

  if (!ready) {
    // No footage. Said in one quiet line rather than drawn as an empty
    // player — and never as an offer, because this screen cannot start a
    // render on somebody else's profile.
    return (
      <div className={"rs-film rs-film-empty" + (talking ? " talking" : "")}>
        <span className="rs-film-note">
          {row.status === "pending" && !gaveUp
            ? tr("ins.film.making", lang)
            : row.status === "failed"
              ? tr("ins.film.failed", lang)
              : tr("ins.film.none", lang)}
        </span>
      </div>
    );
  }

  const src = playable(row.video_url as string);

  return (
    <>
      <div className={"rs-film" + (talking ? " talking" : "")}>
        <video src={src} controls playsInline preload="metadata"
               controlsList="nofullscreen nodownload"
               aria-label={display} />
        {/* Marked on the surface as well as in the file. The stored file
            carries the badge, but somebody watching in a room reads the
            corner of the frame, not the URL it came from. */}
        <span className="rs-film-ai">{tr("ins.film.ai", lang)}</span>
        {mediaIdOf(row.video_url as string) && (
          <a className="rs-film-down" download
             href={getBase() + "/media/" + mediaIdOf(row.video_url as string) + "/download"}
             aria-label={tr("ins.film.download", lang)}
             title={tr("ins.film.download", lang)}
             onClick={(e) => e.stopPropagation()}>⤓</a>
        )}
        <button className="rs-film-grow" type="button"
                aria-label={tr("ins.film.full", lang)}
                title={tr("ins.film.full", lang)}
                onClick={(e) => { e.stopPropagation(); setFull(true); }}>
          <span aria-hidden="true">⛶</span>
        </button>
      </div>

      {full && (
        <div className="rs-film-over" role="dialog" aria-modal="true"
             aria-label={display}>
          <video src={src} controls autoPlay playsInline
                 controlsList="nofullscreen nodownload" />
          {/* The badge rides the takeover too — the outermost layer,
              above the player, above the way out. */}
          <span className="rs-film-ai">{tr("ins.film.ai", lang)}</span>
          <button className="rs-film-x" type="button"
                  aria-label={tr("ins.film.close", lang)}
                  title={tr("ins.film.close", lang)}
                  onClick={(e) => { e.stopPropagation(); setFull(false); }}>
            <span aria-hidden="true">✕</span>
          </button>
          <span className="rs-film-who">{display}</span>
        </div>
      )}
    </>
  );
}
