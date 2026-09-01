/* The ring both stages stand on.
 *
 *     asked     the app is able to render on any devices with the screen
 *     mattered  a headset and a phone must show the SAME room
 *
 * The flat stage draws the circle with CSS transforms; the headset draws
 * it with WebXR. Two renderers, one geometry — the seat angles and the
 * circle's radius live here so the two cannot drift apart, and a guard
 * holds both renderers to this module. The radii differ only in unit:
 * the CSS stage works in pixels at a 640px perspective, the headset in
 * metres around where you actually stand; both put seat 3 of 8 in the
 * same direction. */

/** The flat stage's circle, in CSS pixels (`translateZ(-RADIUS)`). */
export const RING_RADIUS_CSS = 280;

/** The headset's circle, in metres — close enough to read a face,
 *  far enough that eight people are a room rather than a crowd. */
export const RING_RADIUS_XR = 2.4;

/** Seat height in the headset, metres: faces at standing eye level. */
export const RING_HEIGHT_XR = 1.5;

/** Where seat `i` of `n` sits, in degrees. Even spacing, seat 0 ahead. */
export function seatAngle(i: number, n: number): number {
  return (360 / Math.max(n, 1)) * i;
}
