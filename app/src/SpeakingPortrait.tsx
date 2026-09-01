import { useEffect, useRef } from "react";
import * as THREE from "three";

/**
 * The photograph, with a mouth that moves.
 *
 * ## Why this is not `Avatar3D`
 *
 * `Avatar3D` draws a head the forge built out of 478 face landmarks —
 * and a head from face landmarks has no skull, no hair and no ears. It
 * is a mask, and the field said so in one sentence looking at it:
 * *"that isn't the photo I uploaded, that's a white moving skeleton
 * frame."* That is an exact description of a landmark mesh, and no
 * amount of texturing or lighting fixes what it fundamentally is.
 *
 *     asked     let the avatar speak
 *     mattered  let it still be them while it does
 *
 * So nothing here is rebuilt. The photograph is drawn as a photograph,
 * full frame. Over it, at the exact places the landmarker measured, sits
 * a mesh of the same picture — its texture coordinates ARE its
 * positions, so at rest it is a copy of the picture laid over the
 * picture and cannot be seen at all. The only thing that ever moves is
 * the mouth, and everything that is not a mouth is never touched.
 *
 * That is the whole trick, and it is why the person on screen goes on
 * being the person in the photo.
 *
 * ## What drives it
 *
 * The same audio element the room is already playing. No second model,
 * no phoneme timeline, no network call while somebody is speaking — an
 * `AnalyserNode` over the voice already in the ear, eased so the jaw
 * travels rather than flickers on every buffer.
 */
type Shape = [number, number, number];          // index, dx, dy
type Map = {
  points: [number, number][];
  triangles: [number, number, number][];
  shapes: Record<string, Shape[]>;
  width: number;
  height: number;
};

/** One analyser per audio element. A media element can only be routed
 *  into a graph once, and asking twice throws — the lesson `Avatar3D`
 *  already paid for. */
const heard = new WeakMap<HTMLAudioElement,
                          { ctx: AudioContext; node: AnalyserNode }>();

function listen(audio: HTMLAudioElement) {
  const had = heard.get(audio);
  if (had) return had;
  const w = window as unknown as {
    AudioContext?: typeof AudioContext;
    webkitAudioContext?: typeof AudioContext;
  };
  const Ctx = w.AudioContext ?? w.webkitAudioContext;
  if (!Ctx) return null;
  try {
    const ctx = new Ctx();
    const node = ctx.createAnalyser();
    node.fftSize = 512;
    const source = ctx.createMediaElementSource(audio);
    source.connect(node);
    // Straight on to the speakers as well, or routing it silences it.
    node.connect(ctx.destination);
    const made = { ctx, node };
    heard.set(audio, made);
    return made;
  } catch {
    return null;                    // already routed, or refused: stay still
  }
}

export function SpeakingPortrait({ src, map, speaking, className }: {
  /** The photograph. The same URL every other surface draws. */
  src: string;
  /** Where its face's points sit, from the forge's `/speak` door. */
  map: Map;
  /** The voice being played right now, or null for a still face. */
  speaking: HTMLAudioElement | null;
  className?: string;
}) {
  const mount = useRef<HTMLDivElement>(null);
  const voice = useRef<HTMLAudioElement | null>(null);
  voice.current = speaking;

  useEffect(() => {
    const host = mount.current;
    if (!host || !map?.points?.length) return;
    let stop = false;

    const scene = new THREE.Scene();
    // Flat on purpose. There is no depth in a photograph, and inventing
    // one is how the mask got built in the first place.
    const camera = new THREE.OrthographicCamera(-0.5, 0.5, 0.5, -0.5, 0, 10);
    camera.position.z = 1;
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(host.clientWidth, host.clientHeight);
    host.appendChild(renderer.domElement);

    const texture = new THREE.TextureLoader().load(src, () => {
      texture.colorSpace = THREE.SRGBColorSpace;
    });
    texture.colorSpace = THREE.SRGBColorSpace;
    const skin = new THREE.MeshBasicMaterial({
      map: texture, transparent: true,
    });

    // The picture itself, whole, behind everything.
    const behind = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), skin);
    behind.position.z = -0.01;
    scene.add(behind);

    // The face, over the picture, at the places it was measured. Picture
    // space counts y downward and a scene counts it upward, which is the
    // one flip that has to be right or the face lands upside down.
    const at = map.points.length;
    const rest = new Float32Array(at * 3);
    const uv = new Float32Array(at * 2);
    map.points.forEach(([x, y], i) => {
      rest[i * 3] = x - 0.5;
      rest[i * 3 + 1] = 0.5 - y;
      rest[i * 3 + 2] = 0;
      uv[i * 2] = x;
      uv[i * 2 + 1] = 1 - y;
    });
    const geometry = new THREE.BufferGeometry();
    const live = new Float32Array(rest);
    geometry.setAttribute("position", new THREE.BufferAttribute(live, 3));
    geometry.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
    geometry.setIndex(map.triangles.flat());
    const face = new THREE.Mesh(geometry, skin);
    scene.add(face);

    const jaw = map.shapes?.jawOpen || [];
    const pucker = map.shapes?.mouthPucker || [];
    let open = 0;

    let frame = 0;
    const wave = new Uint8Array(256);
    const draw = () => {
      if (stop) return;
      frame = requestAnimationFrame(draw);

      // How loud the voice is right now, eased. A jaw that tracked every
      // buffer would chatter; one that eases reads as speech.
      let want = 0;
      const audio = voice.current;
      if (audio && !audio.paused) {
        const ear = listen(audio);
        if (ear) {
          if (ear.ctx.state === "suspended") void ear.ctx.resume();
          ear.node.getByteTimeDomainData(wave);
          let peak = 0;
          for (const value of wave) peak = Math.max(peak, Math.abs(value - 128));
          want = Math.min(1, (peak / 128) * 2.6);
        }
      }
      open += (want - open) * 0.35;

      live.set(rest);
      for (const [index, dx, dy] of jaw as Shape[]) {
        live[index * 3] += dx * open;
        live[index * 3 + 1] -= dy * open;      // picture y is downward
      }
      // A little roundness with the opening, which is what stops a mouth
      // reading as a hinge.
      const round = open * 0.45;
      for (const [index, dx, dy] of pucker as Shape[]) {
        live[index * 3] += dx * round;
        live[index * 3 + 1] -= dy * round;
      }
      geometry.attributes.position.needsUpdate = true;
      renderer.render(scene, camera);
    };
    draw();

    const fit = () => {
      if (!host.clientWidth) return;
      renderer.setSize(host.clientWidth, host.clientHeight);
      // The picture keeps its own proportions inside whatever box it is
      // given, so a square seat does not stretch somebody's face.
      const box = host.clientWidth / Math.max(host.clientHeight, 1);
      const shot = map.width / Math.max(map.height, 1);
      const wide = shot > box;
      camera.left = wide ? -0.5 : -0.5 * (box / shot);
      camera.right = -camera.left;
      camera.top = wide ? 0.5 * (shot / box) : 0.5;
      camera.bottom = -camera.top;
      camera.updateProjectionMatrix();
    };
    fit();
    const watcher = new ResizeObserver(fit);
    watcher.observe(host);

    return () => {
      stop = true;
      cancelAnimationFrame(frame);
      watcher.disconnect();
      geometry.dispose();
      skin.dispose();
      texture.dispose();
      renderer.dispose();
      renderer.forceContextLoss();
      if (renderer.domElement.parentNode === host) {
        host.removeChild(renderer.domElement);
      }
    };
  }, [src, map]);

  return <div ref={mount} className={className} />;
}
