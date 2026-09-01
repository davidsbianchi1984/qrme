/* The surroundings a person chooses to stand in.
 *
 *     asked     view the avatars in a room or environment of your
 *               choosing
 *     mattered  VR was one dark studio, take it or leave it
 *
 * A closed set of environments, drawn by this product's own scene code —
 * no third-party platform and no downloaded world. Each is a palette the
 * two stage renderers interpret: the flat stage paints it as a backdrop,
 * the headset builds it as sky, ground and fog around where you stand.
 *
 * Per-viewer and browser-only, exactly like the room format: which
 * surroundings you stand in is your seat's business, never sent to the
 * server, and two people in one room can stand in different places while
 * hearing the same conversation. */

export type StagePlace = "studio" | "dusk" | "forest" | "shore" | "void";

export const PLACES: readonly StagePlace[] = [
  "studio", "dusk", "forest", "shore", "void"];

/** The colours each place is made of. `sky` is the dome overhead — the
 *  flat stage's backdrop gradient top and the headset's clear colour —
 *  `horizon` the band it falls to, `ground` the floor underfoot. */
export const PALETTES: Record<StagePlace, {
  sky: string; horizon: string; ground: string;
}> = {
  studio: { sky: "#0b0d12", horizon: "#12151d", ground: "#151a24" },
  dusk:   { sky: "#1b1440", horizon: "#8a4d6b", ground: "#241d33" },
  forest: { sky: "#0e1f16", horizon: "#28503a", ground: "#16301f" },
  shore:  { sky: "#10263b", horizon: "#4a7fa0", ground: "#8f8468" },
  void:   { sky: "#000000", horizon: "#000000", ground: "#000000" },
};

const KEY = "qrme.stagePlace";

function known(value: string | null): value is StagePlace {
  return PLACES.includes(value as StagePlace);
}

export function stagePlace(): StagePlace {
  try {
    const stored = localStorage.getItem(KEY);
    if (known(stored)) return stored;
  } catch { /* private windows forget; the default stands. */ }
  return "studio";
}

export function setStagePlace(place: StagePlace) {
  try {
    localStorage.setItem(KEY, place);
  } catch { /* same: a browser that keeps nothing still gets a place. */ }
}
