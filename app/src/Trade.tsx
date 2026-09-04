/** The two lines under the name: what this profile does, and where.
 *
 * A name answers "who" and leaves "and who is that?" standing. The pool is
 * thirty-odd faces, one a family physician and one a master mechanic, and
 * until this there was nothing on any card, seat or talk surface saying
 * which. Asked for in two goes — "I think there should be a profession
 * under the name", then "I like how you put the profession, but I need you
 * to also put the position" — and then "that needs to be implemented
 * across the board", which is why it is a component rather than a line of
 * JSX copied onto five screens that would then drift.
 *
 *     asked     does the screen name the profile
 *     mattered  does the screen introduce it
 *
 * Two fields, because they answer different questions. `position` is the
 * job — *Software architect* — and it is the one a person choosing between
 * faces reads. `industry` is the sector — *Technology* — and it is the one
 * that groups. The position leads for that reason, and the sector sits
 * under it in the quieter register.
 *
 * **Neither is translated, and that is the point.** Both are the profile's
 * own words in whatever language they were written in, the same standing
 * as the display name above them. What this does is presentation only: the
 * column stores `real_estate` and a person reads "Real estate".
 *
 * A profile that has said neither draws nothing. An empty line under a
 * name is worse than no line — it reads as something that failed to load.
 */

/** `real_estate` → `Real estate`. */
export function tradeOf(industry?: string | null): string {
  return (industry || "").trim()
    .replace(/_/g, " ")
    .replace(/^./, (c) => c.toUpperCase());
}

export function Trade({ industry, position, className }: {
  industry?: string | null;
  position?: string | null;
  /** The surface's own class, where its type scale differs — a card's
   *  line is smaller than the talk surface's. */
  className?: string;
}) {
  const field = tradeOf(industry);
  const job = (position || "").trim();
  if (!field && !job) return null;
  const cls = className ? ` ${className}` : "";
  return (
    <div className={"trade" + cls}>
      {job && <span className="trade-job">{job}</span>}
      {field && <span className="trade-field">{field}</span>}
    </div>
  );
}
