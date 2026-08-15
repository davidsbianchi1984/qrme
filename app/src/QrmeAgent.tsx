/**
 * The Agent's mark.
 *
 * Drawn rather than imported, for the reason the sibling product's menu icon
 * was redrawn after a field report: a lockup shrunk to nav size is not a
 * smaller mark, it is an illegible one. The source artwork is a neon QRME
 * wordmark over a night city with a plate beneath it — beautiful at poster
 * size, mud at 28 pixels, and a raster cannot take the viewer's theme or a
 * focus ring.
 *
 * So the same split `JimMiniOS` uses:
 *
 *   default   the Q alone — the one element of that artwork that survives
 *             being made small, and the one a person recognises
 *   full      the artwork: night, city, wordmark, and the plate reading
 *             Agent where the poster reads Future
 *
 * The full form keeps the night and the city, because they are the artwork
 * rather than a frame around it. The **small** form has no ground at all, and
 * that is a deliberate difference rather than an oversight: a 28px button
 * carrying its own black panel boxes the one icon in a sidebar that should
 * share a surface with its neighbours, and at that size the city is four
 * unreadable smudges anyway. Line and glow survive being made small; scenery
 * does not.
 *
 * The palette is the artwork's: cyan through violet to hot pink. Stated once
 * as tokens rather than repeated down the file, because the next thing
 * anybody does to this is retune the colour.
 */

const CYAN = "#6ee7ff";
const VIOLET = "#b57bff";
const PINK = "#ff5ce1";
const NIGHT = "#0a0620";

export function QrmeAgent({ size = 28, full = false, title = "Agent" }: {
  /** Rendered square. The nav asks for 28; the full lockup wants 200+. */
  size?: number;
  /** The whole artwork rather than the Q alone. */
  full?: boolean;
  /** What the plate reads, and what a screen reader is told. The artwork
   *  says FUTURE; this product's button says Agent. */
  title?: string;
}) {
  // One gradient set, two ids per instance. Two marks on one page sharing an
  // id is how the second one renders with the first one's colours.
  const uid = `qa${size}${full ? "f" : "s"}`;

  if (!full) {
    return (
      <svg width={size} height={size} viewBox="0 0 100 100" role="img"
           aria-label={title}>
        <defs>
          <linearGradient id={`${uid}g`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor={CYAN} />
            <stop offset="0.55" stopColor={VIOLET} />
            <stop offset="1" stopColor={PINK} />
          </linearGradient>
          <radialGradient id={`${uid}h`}>
            <stop offset="0" stopColor={VIOLET} stopOpacity="0.55" />
            <stop offset="1" stopColor={VIOLET} stopOpacity="0" />
          </radialGradient>
        </defs>
        {/* No ground. The first draft put the Q on a black rounded square,
            which is a black silhouette behind the mark rather than the mark
            — and in a sidebar it also boxed the one icon that should sit on
            the same surface as its neighbours. The glow is additive, so it
            reads over a light ground as well as a dark one. */}
        <circle cx="50" cy="50" r="42" fill={`url(#${uid}h)`} />
        {/* The Q: a ring and its tail. Stroked rather than filled so it stays
            legible when the whole thing is 28px across — a filled letterform
            at this size closes its own counter and reads as a blob. */}
        <circle cx="48" cy="48" r="26" fill="none"
                stroke={`url(#${uid}g)`} strokeWidth="7" />
        <path d="M62 62 L78 80" stroke={`url(#${uid}g)`} strokeWidth="9"
              strokeLinecap="round" />
      </svg>
    );
  }

  return (
    <svg width={size} height={size * 0.66} viewBox="0 0 300 198" role="img"
         aria-label={title}>
      <defs>
        <linearGradient id={`${uid}g`} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor={CYAN} />
          <stop offset="0.5" stopColor={VIOLET} />
          <stop offset="1" stopColor={PINK} />
        </linearGradient>
        <linearGradient id={`${uid}sky`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#140a38" />
          <stop offset="1" stopColor={NIGHT} />
        </linearGradient>
        <radialGradient id={`${uid}h`}>
          <stop offset="0" stopColor={VIOLET} stopOpacity="0.5" />
          <stop offset="1" stopColor={VIOLET} stopOpacity="0" />
        </radialGradient>
      </defs>
      {/* The night and the city under it, which are the artwork rather than
          scenery around it — a wordmark floating on nothing is not the thing
          in the poster. A draft removed both on a misread of "not the black
          behind it": the black meant was the letterboxing a phone screenshot
          adds above and below, not the sky the city stands in. */}
      <rect width="300" height="198" rx="16" fill={`url(#${uid}sky)`} />
      <ellipse cx="150" cy="96" rx="130" ry="60" fill={`url(#${uid}h)`} />
      <g opacity="0.55" fill={VIOLET}>
        <rect x="20" y="158" width="14" height="30" />
        <rect x="40" y="146" width="11" height="42" />
        <rect x="57" y="164" width="15" height="24" />
        <rect x="78" y="152" width="10" height="36" />
        <rect x="212" y="150" width="13" height="38" />
        <rect x="231" y="138" width="17" height="50" />
        <rect x="254" y="158" width="11" height="30" />
        <rect x="271" y="148" width="12" height="40" />
      </g>

      <text x="150" y="104" textAnchor="middle" fontSize="62"
            fontWeight="800" letterSpacing="2"
            fontFamily="-apple-system,BlinkMacSystemFont,'SF Pro Display',Segoe UI,Roboto,system-ui,sans-serif"
            fill={`url(#${uid}g)`}>QRME</text>

      {/* The plate. The artwork reads FUTURE here; this button reads what it
          opens, because a menu icon that names a mood rather than a
          destination is a menu icon people press once. */}
      <rect x="105" y="126" width="90" height="30" rx="7"
            fill="rgba(110,231,255,0.10)" stroke={CYAN} strokeWidth="1.5" />
      <text x="150" y="147" textAnchor="middle" fontSize="17"
            fontWeight="800" letterSpacing="1"
            fontFamily="-apple-system,BlinkMacSystemFont,'SF Pro Display',Segoe UI,Roboto,system-ui,sans-serif"
            fill="#eaf6ff">{title}</text>
    </svg>
  );
}
