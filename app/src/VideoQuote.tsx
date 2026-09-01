import { fill, t as tr, type Lang } from "./l10n";

/**
 * How long this will run, and how long it will take to make.
 *
 * Both are stated. Neither is offered.
 *
 *     asked     how long should this video be
 *     mattered  how long is the thing it is a video of
 *
 * The control this replaces was a slider, and a slider makes the video fit
 * the setting instead of the content: two sentences padded out to thirty
 * seconds, or a paragraph hurried into five, footage stretched or clipped
 * to hit a number nobody meant. `filming.length_for` works the duration
 * out from the passage and the backend renders for exactly that, so the
 * only honest thing a screen can do with the number is show it.
 *
 * The arithmetic is duplicated here rather than fetched, and that is a
 * deliberate trade. `/video/estimate` exists and is the authority, but
 * quoting as somebody types would be a request per keystroke to answer a
 * question that is a division. The constants ride in on `doors()` — this
 * does not hard-code 150 or 12 — so a deployment that changes them changes
 * this too, and the worst case is a quote that lags one render behind.
 */
export function VideoQuote({ text, film, lang }: {
  text: string;
  film: {
    max_seconds: number; min_seconds: number; words_per_minute: number;
    seconds_per_second: number;
  };
  lang: Lang;
}) {
  const words = text.trim().split(/\s+/).filter(Boolean).length;
  const spoken = Math.round(words / (film.words_per_minute / 60));
  const seconds = Math.max(film.min_seconds,
                           Math.min(film.max_seconds, spoken));
  const wait = seconds * film.seconds_per_second;
  // Over a minute and there is no point standing here. The threshold is
  // the same one `filming.estimate` reports as `worth_leaving`.
  const leaving = wait > 60;

  const clock = (total: number) => {
    const m = Math.floor(total / 60);
    const s = total % 60;
    if (!m) return `${s}s`;
    return s ? `${m}m ${s}s` : `${m}m`;
  };

  return (
    <div className={"video-quote" + (leaving ? " long" : "")}>
      <p>{fill(tr("idn.video.quote", lang), {
        words: String(words), seconds: String(seconds), wait: clock(wait),
      })}</p>
      <p className="muted small">
        {/* The `tr(` goes inside each branch. A key chosen by a ternary
            and then looked up is invisible to the extractor next door,
            which reports both strings as translated and read by nobody —
            and it is right to, because it cannot prove otherwise. */}
        {leaving ? tr("idn.video.leave", lang) : tr("idn.video.stay", lang)}
      </p>
      {/* Said, never done silently. A video that quietly drops its last
          sentence is worse than one that was never made, because nobody
          watching it can tell. */}
      {spoken > film.max_seconds && (
        <p className="video-quote-over">
          {fill(tr("idn.video.toolong", lang),
                { max: String(film.max_seconds) })}
        </p>
      )}
    </div>
  );
}
