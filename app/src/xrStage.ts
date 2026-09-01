/* The stage, on a headset.
 *
 *     asked     the app is able to render on any devices with the screen
 *     mattered  a paired VR headset or AR glasses that cannot show the
 *               room is a screen the product claims and never uses
 *
 * The flat stage (Inside.tsx) draws the room's circle with CSS
 * transforms; this draws the same circle through WebXR, in the browser a
 * headset already carries — Quest's, Vision Pro's — so "render on the
 * device" needs no app store and no second codebase. VR gets a floor and
 * the dark; AR gets the seats alone over the headset's own passthrough,
 * composited by the device, never by us.
 *
 * The flat stage's promise is kept here word for word: no pixels of
 * yours and no room of anybody else's crosses the wire for this. The
 * session renders locally, nothing here touches a camera or microphone,
 * and leaving the session leaves nothing behind — a guard reads this
 * file for capture vocabulary the same way the pairing model is read.
 */
import * as THREE from "three";
import { RING_RADIUS_XR, RING_HEIGHT_XR, seatAngle } from "./stageRing";

export type XrSeat = {
  id: string;
  display: string;
  /** Same URL the flat stage's face shows, resolved by the same rules. */
  photo: string | null;
  /** Wears the AI mark — drawn on the label, as on every other seat. */
  ai: boolean;
};

export type XrMode = "immersive-vr" | "immersive-ar";

/** Whether this browser can open the given session — the button's gate.
 *  Absent API or a refusal both answer no; nothing is offered on hope. */
export async function headsetDoor(mode: XrMode): Promise<boolean> {
  const xr = (navigator as { xr?: XRSystem }).xr;
  if (!xr?.isSessionSupported) return false;
  try {
    return await xr.isSessionSupported(mode);
  } catch {
    return false;
  }
}

/** A face card: the photo (or initials) above the name, marked when the
 *  seat is synthetic. Sprites billboard on their own, which is what the
 *  flat stage does with counter-rotation — a face is for facing you. */
function label(seat: XrSeat): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = 512; c.height = 128;
  const g = c.getContext("2d")!;
  g.fillStyle = "rgba(10,12,16,0.72)";
  g.fillRect(0, 0, c.width, c.height);
  g.fillStyle = "#f2f4f8";
  g.font = "600 44px system-ui, sans-serif";
  g.textAlign = "center"; g.textBaseline = "middle";
  const name = seat.ai ? `✦ ${seat.display}` : seat.display;
  g.fillText(name.slice(0, 24), c.width / 2, c.height / 2);
  return new THREE.CanvasTexture(c);
}

function initials(seat: XrSeat): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = 256; c.height = 256;
  const g = c.getContext("2d")!;
  g.fillStyle = "#2a3140";
  g.beginPath(); g.arc(128, 128, 124, 0, Math.PI * 2); g.fill();
  g.fillStyle = "#e8ecf2";
  g.font = "700 96px system-ui, sans-serif";
  g.textAlign = "center"; g.textBaseline = "middle";
  const two = (seat.display || "?").split(/\s+/).map((w) => w[0])
    .join("").slice(0, 2);
  g.fillText(two, 128, 136);
  return new THREE.CanvasTexture(c);
}

/** Step onto the stage through the headset. Resolves when the person
 *  takes the headset's own way out; the flat stage is still there. */
export async function enterHeadset(opts: {
  mode: XrMode;
  seats: XrSeat[];
  /** Read each frame so the green ring follows the voice being heard. */
  isTalking: (id: string) => boolean;
  onEnd: () => void;
}): Promise<void> {
  const xr = (navigator as { xr?: XRSystem }).xr;
  if (!xr) { opts.onEnd(); return; }

  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.xr.enabled = true;
  const scene = new THREE.Scene();
  if (opts.mode === "immersive-vr") {
    scene.background = new THREE.Color(0x0b0d12);
    const floor = new THREE.Mesh(
      new THREE.CircleGeometry(RING_RADIUS_XR + 1.2, 48),
      new THREE.MeshBasicMaterial({ color: 0x151a24 }));
    floor.rotation.x = -Math.PI / 2;
    scene.add(floor);
  }
  const camera = new THREE.PerspectiveCamera();

  const rings: { id: string; ring: THREE.Sprite }[] = [];
  const loader = new THREE.TextureLoader();
  const n = opts.seats.length;
  opts.seats.forEach((seat, i) => {
    // The one circle both stages agree on.
    const a = (seatAngle(i, n) * Math.PI) / 180;
    const x = Math.sin(a) * RING_RADIUS_XR;
    const z = -Math.cos(a) * RING_RADIUS_XR;

    const tex = seat.photo ? loader.load(seat.photo) : initials(seat);
    const face = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex }));
    face.position.set(x, RING_HEIGHT_XR, z);
    face.scale.set(0.55, 0.55, 1);
    scene.add(face);

    const tag = new THREE.Sprite(new THREE.SpriteMaterial({
      map: label(seat), transparent: true }));
    tag.position.set(x, RING_HEIGHT_XR - 0.42, z);
    tag.scale.set(0.8, 0.2, 1);
    scene.add(tag);

    // The talking halo, hidden until the voice is theirs.
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      color: 0x7bc47f, opacity: 0.35, transparent: true }));
    halo.position.set(x, RING_HEIGHT_XR, z);
    halo.scale.set(0.7, 0.7, 1);
    halo.visible = false;
    scene.add(halo);
    rings.push({ id: seat.id, ring: halo });
  });

  const session = await xr.requestSession(opts.mode, {
    optionalFeatures: ["local-floor"],
  });
  await renderer.xr.setSession(session as XRSession);
  renderer.setAnimationLoop(() => {
    for (const r of rings) r.ring.visible = opts.isTalking(r.id);
    renderer.render(scene, camera);
  });
  session.addEventListener("end", () => {
    renderer.setAnimationLoop(null);
    renderer.dispose();
    opts.onEnd();
  });
}
