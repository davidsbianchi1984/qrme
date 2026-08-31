/**
 * How THIS person's room screen is laid out — and nobody else's.
 *
 * The format is a property of the viewer, not of the room and not of the
 * seat being viewed. Two people in the same room see different screens:
 * one in video, one in audio, neither changing anything for the other.
 * The owner's words, and the correction this file exists to obey:
 *
 *     "when that video button gets pressed it changed the shape and
 *      format of just the user screen. It doesn't affect everybody
 *      else's own chat room screens... it just renders formatting
 *      differently per user"
 *
 *     asked     which format is this room in
 *     mattered  which format is this PERSON in
 *
 * So it is kept in the browser and never sent. That is not a shortcut
 * around a table — a server-side format would be a value one person can
 * write and another person's screen reads, which is precisely the thing
 * that must not happen here.
 *
 * ## What this is NOT
 *
 * It is not `presence_road`. That one lives on the server and decides
 * whether a profile's replies are *rendered into video at all*, which
 * spends the profile owner's money against a ceiling they set. This
 * decides only what a viewer's own screen draws with whatever already
 * exists. Switching your screen to video cannot start a render on
 * somebody else's profile, and that separation is the whole reason the
 * two are different things:
 *
 *     the road      does footage get made, and on whose budget
 *     the format    do I want to look at footage, avatars or photos
 *
 * A format with nothing to show falls down the list the way every other
 * surface does — video to avatar to photo — rather than drawing an empty
 * frame or, worse, commissioning one.
 */

export type RoomFormat = "audio" | "avatar" | "video";

export const FORMATS: readonly RoomFormat[] = ["audio", "avatar", "video"];

const KEY = "qrme.roomFormat";

/** Photo. The one road every profile has and the only one that always
 *  works, so it is what a screen opens on before anybody chooses. */
export const DEFAULT_FORMAT: RoomFormat = "audio";

function known(value: string | null): value is RoomFormat {
  return value === "audio" || value === "avatar" || value === "video";
}

export function roomFormat(): RoomFormat {
  try {
    const stored = localStorage.getItem(KEY);
    return known(stored) ? stored : DEFAULT_FORMAT;
  } catch {
    // A private window, cleared site data, or a browser set to block it.
    // A screen that cannot remember the choice still has to draw.
    return DEFAULT_FORMAT;
  }
}

export function setRoomFormat(format: RoomFormat) {
  try {
    localStorage.setItem(KEY, format);
  } catch {
    // Forgetting the preference is not worth an error. The format still
    // applies for as long as this screen is open.
  }
}
