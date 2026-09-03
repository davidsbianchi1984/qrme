import { t as tr, fill, type Lang } from "./l10n";
import { type SceneRender } from "./api";
import { useState } from "react";
import { getBase } from "./api";
import { mediaIdOf, playable, useRenderRow } from "./sceneRender";

/**
 * The reply, as footage — and the wait in between.
 *
 * A turn on the video road comes back with a row, not a video: rendering
 * is minutes and a reply is not, so `auto_render` starts the job, records
 * it, and returns. This is the other end of that. It polls the row until
 * it settles and then plays what came back.
 *
 *     asked     show the video
 *     mattered  say what is happening while there isn't one
 *
 * Four states, and three of them have no video in them. A component that
 * only draws the finished case leaves the common case — a person who just
 * read a reply and is looking at nothing — with a blank space and no way
 * to tell a render in progress from one that failed, or from a ceiling
 * they set themselves. So each says which it is, in words.
 *
 * The polling lives in `sceneRender`, shared with the room's own frame:
 * two copies of a loop with a lifecycle and a stop is two chances to get
 * the stop wrong, and a screen left polling has no symptom on the screen
 * itself.
 */
export function SceneFilm({ scene, lang }: { scene: SceneRender; lang: Lang }) {
  const { row, gaveUp } = useRenderRow(scene);
  const [full, setFull] = useState(false);

  if (row.status === "capped") {
    return (
      <div className="bubble-scene capped" data-screen="209">
        {fill(tr("chat.scene.capped", lang), {
          left: String(row.left ?? 0),
          cap: String(row.daily_seconds ?? 0),
        })}
      </div>
    );
  }

  if (row.status === "failed") {
    return (
      <div className="bubble-scene failed" data-screen="209">
        <span>{tr("chat.scene.failed", lang)}</span>
        {row.detail && <em className="muted small"> {row.detail}</em>}
      </div>
    );
  }

  if (row.status === "done" && row.video_url) {
    const src = playable(row.video_url);
    return (
      <div className="bubble-scene done" data-screen="209">
        {/* Marked on the surface as well as in storage. `asset_is_marked`
            decides by path and the file itself carries the badge, but a
            person watching a video in a chat bubble reads the caption
            under it, not the URL it came from. */}
        {/* The badge is the outermost layer, never in the pixels: the
            player's own full-screen and download are switched off so the
            only way to fill the screen is the takeover below, which
            carries the badge, and the only download is the burned copy. */}
        <video src={src} controls playsInline preload="metadata"
               controlsList="nofullscreen nodownload" />
        <span className="bubble-scene-ai">{tr("chat.scene.ai", lang)}</span>
        {mediaIdOf(row.video_url) && (
          <a className="rs-film-down" download
             href={getBase() + `/media/${mediaIdOf(row.video_url)}/download`}
             aria-label={tr("ins.film.download", lang)}
             title={tr("ins.film.download", lang)}>⤓</a>
        )}
        <button className="rs-film-grow" type="button"
                aria-label={tr("ins.film.full", lang)}
                title={tr("ins.film.full", lang)}
                onClick={() => setFull(true)}>
          <span aria-hidden="true">⛶</span>
        </button>
        {full && (
          <div className="rs-film-over" role="dialog" aria-modal="true">
            <video src={src} controls autoPlay playsInline
                   controlsList="nofullscreen nodownload" />
            <span className="rs-film-ai">{tr("ins.film.ai", lang)}</span>
            <button className="rs-film-x" type="button"
                    aria-label={tr("ins.film.close", lang)}
                    title={tr("ins.film.close", lang)}
                    onClick={() => setFull(false)}>
              <span aria-hidden="true">✕</span>
            </button>
          </div>
        )}
      </div>
    );
  }

  if (gaveUp) {
    return (
      <div className="bubble-scene waiting" data-screen="209">
        {tr("chat.scene.gaveup", lang)}
      </div>
    );
  }

  return (
    <div className="bubble-scene making" aria-live="polite"
         data-screen="209">
      {fill(tr("chat.scene.making", lang),
            { seconds: String(row.seconds ?? 0) })}
    </div>
  );
}
