import { useEffect, useRef } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { Liveliness, Motion } from "./avatarMotion";

/**
 * The face, in three dimensions, with a mouth that moves when it speaks.
 *
 * The forge (`docker/forge/`) builds a head from one photograph and hands
 * back a `.glb` whose morph targets carry ARKit's own names — `jawOpen`,
 * `mouthPucker`, the smiles, the blinks. This component draws it and
 * drives those names.
 *
 * ## Why the names matter more than the model
 *
 * Nothing here knows or cares which machine built the head it is given.
 * It looks up morph targets BY NAME, so the same code draws a face our
 * forge made on the deployment's own hardware and a face somebody paid a
 * vendor for — provided the vendor ships ARKit blendshapes, which all of
 * them do. That is what keeps a provider a slot rather than a
 * foundation: the day somebody brings their own paid avatar, this file
 * does not change.
 *
 * ## The mouth
 *
 * `speaking` is an audio element that is currently playing — the room
 * already fetches a profile's voice and plays it piece by piece, so the
 * lip movement rides the sound that is already in the air rather than a
 * second machine learning model deciding what a mouth should do. Loudness
 * opens the jaw; a little pucker rides along so the shape is not a hinge.
 *
 * It is honest about what it is: amplitude, not phonemes. A face whose
 * jaw follows the voice reads as speaking, which is the claim; a face
 * whose lips form the letter M does not follow from an amplitude, and
 * this does not pretend otherwise.
 */

/** How much of the figure is in the frame.
 *
 *  The three the forge already names, so a person choosing here is
 *  choosing the same three words they chose when the face was built.
 *  Each is a slice of the model's OWN measured height rather than a
 *  distance in metres: the two shipped models stand 1.81 m and 1.73 m,
 *  and a camera placed at a fixed height frames one of them properly
 *  and beheads the other. */
const SHOTS = {
  face:  { at: 0.925, tall: 0.21 },
  upper: { at: 0.760, tall: 0.56 },
  full:  { at: 0.500, tall: 1.04 },
} as const;

export type Shot = keyof typeof SHOTS;

/** Bring a T-posed rig's arms down toward its sides.
 *
 * Every model out of the exporter arrives in a T-pose, which is how a
 * rig is authored and not how somebody stands in a room. Applied to the
 * bind pose rather than animated into: this is what the figure IS, not
 * something it does.
 *
 * ## Why this measures instead of naming an axis
 *
 *     asked     bring the arms down
 *     mattered  down in WHICH frame
 *
 * The first attempt added to `rotation.z`, and on a Mixamo-style rig the
 * arm bone's own frame is turned so that a local-Z swing sends the arm
 * BACKWARD rather than down. Measured on the models that ship: the hand
 * starts at (0.692, 1.446, 0.034), and 1.22 radians about local Z puts it
 * at (0.441, 1.459, −0.513) — thirteen millimetres of drop and half a
 * metre behind the figure. That is the pose that came back as "that
 * Naruto run is not funny". It was never a bad angle; it was the wrong
 * axis, and picking a different letter would only have been a luckier
 * guess.
 *
 * So nothing is named. Each arm is turned about each of its own three
 * axes, both ways, and the one that puts the far end of the arm LOWEST
 * is the one kept. `down` is the actual goal, so `down` is what gets
 * measured — and a rig whose exporter chose different axes, or whose
 * "Left" is on the right, gets arms that hang correctly without this
 * function knowing anything about it. On both shipped models the winner
 * is local +X, which puts the hand at (0.312, 0.947, 0.034): hip height,
 * just clear of the thigh. A person standing.
 *
 * Six trial rotations on two bones, once, at load. The cost is nothing
 * and the alternative is a constant that is right until somebody ships a
 * model from a different tool.
 *
 * Only the upper arm turns. Rotating the forearm as well compounds at
 * the elbow and folds it inward — tried, and it tore the elbows. The
 * shoulders are left alone for the same reason: a nudge on an axis
 * nobody measured is a guess, and a guess on top of a fix is how the fix
 * gets blamed.
 *
 * A rig with no arm bones is left exactly as it arrived. A head has no
 * arms, and a model from a vendor with different names is better
 * untouched than bent by a guess.
 */
const ARM_DOWN = 1.32;

/** The far end of a limb: whichever descendant sits furthest from the
 *  bone itself. The fingertip on a rig with hands, the elbow on one
 *  without — either is a fair probe for whether the arm came down, and
 *  neither has to be found by name. */
function tip(bone: THREE.Object3D): THREE.Object3D | null {
  const from = new THREE.Vector3();
  bone.getWorldPosition(from);
  const at = new THREE.Vector3();
  let far: THREE.Object3D | null = null;
  let best = 0;
  bone.traverse((node) => {
    if (node === bone) return;
    node.getWorldPosition(at);
    const away = at.distanceTo(from);
    if (away > best) { best = away; far = node; }
  });
  return far;
}

function rest(root: THREE.Object3D) {
  // The trials read world positions, so the tree has to be current
  // before the first one runs.
  root.updateMatrixWorld(true);
  const arms: THREE.Object3D[] = [];
  root.traverse((node) => {
    const key = node.name.toLowerCase().replace(/^mixamorig:?/, "")
                         .replace(/[_.\s-]/g, "");
    if (key === "leftarm" || key === "rightarm") arms.push(node);
  });

  const AXES = [new THREE.Vector3(1, 0, 0),
                new THREE.Vector3(0, 1, 0),
                new THREE.Vector3(0, 0, 1)];
  const at = new THREE.Vector3();
  for (const arm of arms) {
    const probe = tip(arm);
    if (probe === null) continue;
    const was = arm.quaternion.clone();
    let bestAxis: THREE.Vector3 | null = null;
    let bestWay = 1;
    let lowest = Infinity;
    for (const axis of AXES) {
      for (const way of [1, -1]) {
        arm.quaternion.copy(was);
        arm.rotateOnAxis(axis, way * ARM_DOWN);
        arm.updateMatrixWorld(true);
        probe.getWorldPosition(at);
        if (at.y < lowest) { lowest = at.y; bestAxis = axis; bestWay = way; }
      }
    }
    arm.quaternion.copy(was);
    if (bestAxis !== null) arm.rotateOnAxis(bestAxis, bestWay * ARM_DOWN);
    arm.updateMatrixWorld(true);
  }
}

export function Avatar3D({ src, speaking, motion, shot, className }: {
  src: string;
  /** The audio in the air right now, if any. Its loudness moves the jaw. */
  speaking?: HTMLAudioElement | null;
  /** How this face carries itself, as `avatars.motion_of` derived it from
   *  the profile's own history. Absent means breathe at the default pace. */
  motion?: Motion | null;
  /** Face, upper torso or full body. Omitted, the model is centred in
   *  the frame the way every caller got before there was a choice — so
   *  adding the option changes nothing for a surface that does not take
   *  it. */
  shot?: Shot;
  className?: string;
}) {
  const holder = useRef<HTMLDivElement | null>(null);
  // The analyser is built once per audio element and kept: a media
  // element can be routed into Web Audio exactly once, and asking twice
  // throws — which on a room reading several turns in a row would end
  // the voice rather than the animation.
  const listened = useRef<Map<HTMLAudioElement, AnalyserNode>>(new Map());

  useEffect(() => {
    const mount = holder.current;
    if (!mount) return;
    let stop = false;
    let frame = 0;
    // Asked of the machine, not of the profile. Somebody who told their
    // system to stop animating things did not mean "except faces".
    const calm = window.matchMedia
      && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      30, mount.clientWidth / Math.max(mount.clientHeight, 1), 0.1, 100);
    camera.position.set(0, 0, 2.4);
    const renderer = new THREE.WebGLRenderer({
      antialias: true, alpha: true,
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    mount.appendChild(renderer.domElement);
    // A photographed face already carries its own light, and the scene's
    // job is to not fight it. It was fighting it: ambient 1.6 plus a 0.6
    // key over a lit material multiplies the photograph by more than two,
    // so every pixel above about four-tenths brightness clipped to white
    // and the head came back as a featureless white blob with a little
    // facet shading on it — which is exactly what the field reported.
    //
    //     asked     is the face lit
    //     mattered  is the photograph still visible after lighting it
    //
    // The skin is swapped to an unlit material below, so these lights
    // only reach a head that arrived without one. Kept faint for that
    // case rather than removed, because an unlit material with no map is
    // a flat silhouette and a lit one at least has a shape.
    scene.add(new THREE.AmbientLight(0xffffff, 0.9));
    const key = new THREE.DirectionalLight(0xffffff, 0.35);
    key.position.set(0, 1, 2);
    scene.add(key);

    // Every mesh that carries shapes, not the first one found.
    //
    // This bound to the first mesh with morph targets, and on a vendor
    // model that is the eyelashes — which carry the eye shapes and no
    // `jawOpen` at all, so the mouth was being driven on a mesh that has
    // no mouth. The head and the lower teeth both carry `jawOpen` and are
    // both supposed to move on it; that is what the teeth mesh's own
    // nineteen shapes are for.
    //
    //     asked     which mesh is the face
    //     mattered  which meshes carry the shape being driven
    const shaped: { mesh: THREE.Mesh; at: Record<string, number> }[] = [];
    let live: Liveliness | null = null;

    new GLTFLoader().load(src, (loaded) => {
      if (stop) return;
      loaded.scene.traverse((thing) => {
        const mesh = thing as THREE.Mesh;
        if (!mesh.isMesh) return;
        // The photograph, shown as photographed — on EVERY painted mesh,
        // not only the ones that carry shapes.
        //
        // glTF's own material is a lit one, and lighting a texture that
        // was already lit when it was baked is how the skin got washed
        // out of it. An unlit material draws the texture at the
        // brightness it was made at, and morph targets work on it
        // exactly as they do on the lit one, so the jaw still moves.
        //
        //     asked     is the face lit correctly
        //     mattered  is the face lit the same as the neck under it
        //
        // This test used to be `isMesh && morphTargetInfluences`, so a
        // vendor model got an unlit HEAD and a lit BODY. The lights are
        // faint on purpose — they exist only for a head that arrived
        // with no texture at all — so the body came out near black under
        // a face at full brightness, and the seam ran straight across
        // the collar. Reported from a phone, in four words: "the skin
        // tones don't match."
        //
        // Whether a mesh carries shapes says something about whether it
        // can speak. It says nothing about how its paint should be lit.
        const lit = mesh.material as THREE.MeshStandardMaterial;
        if (lit?.map) {
          mesh.material = new THREE.MeshBasicMaterial({
            map: lit.map, side: THREE.DoubleSide,
            // Eyelashes and hair cards are cut out by their alpha, and a
            // fresh material that forgets that draws them as black
            // rectangles.
            transparent: lit.transparent,
            alphaTest: lit.alphaTest,
            depthWrite: lit.depthWrite,
          });
          lit.dispose();
        }
        if (mesh.morphTargetInfluences) {
          // The names ride in the mesh's extras, which is where the forge
          // put them and where every exporter puts them.
          const named = (mesh.morphTargetDictionary
            || (mesh.userData?.targetNames
                ? Object.fromEntries(
                    (mesh.userData.targetNames as string[])
                      .map((n, i) => [n, i]))
                : {})) as Record<string, number>;
          shaped.push({ mesh, at: named });
        }
      });
      // The skeleton, if this model brought one. A head with no rig still
      // speaks and blinks; it simply does not breathe.
      // Arms down before `Liveliness` is built, and that ordering is the
      // whole trick: it remembers each bone's rotation as the rest it
      // breathes around, so posing first makes THIS the rest and the
      // idle motion carries on from here. Posing afterwards would have
      // the sway fighting the pose.
      rest(loaded.scene);
      live = new Liveliness(loaded.scene, motion, calm);
      // Framed on the head: the model is built around its own centre, so
      // the camera only has to look at the middle of what arrived.
      const box = new THREE.Box3().setFromObject(loaded.scene);
      if (shot) {
        // Stood on the floor and framed from there. Centring works for a
        // head and falls apart on a body: the middle of a standing figure
        // is its waist, so "full" would have put the camera at the belt
        // and cropped both ends.
        const size = box.getSize(new THREE.Vector3());
        const middle = box.getCenter(new THREE.Vector3());
        loaded.scene.position.sub(
          new THREE.Vector3(middle.x, box.min.y, middle.z));
        const pick = SHOTS[shot];
        const eye = size.y * pick.at;
        const view = size.y * pick.tall;
        const half = (camera.fov * Math.PI / 180) / 2;
        camera.position.set(0, eye, (view / 2) / Math.tan(half) * 1.1);
        camera.lookAt(0, eye, 0);
      } else {
        const middle = box.getCenter(new THREE.Vector3());
        loaded.scene.position.sub(middle);
      }
      scene.add(loaded.scene);
    }, undefined, () => {
      // A model that will not load leaves the portrait standing — the
      // seat drew a picture before this component mounted and keeps it.
    });

    function loudness(): number {
      if (!speaking || speaking.paused) return 0;
      let analyser = listened.current.get(speaking);
      if (!analyser) {
        try {
          const Ctx = window.AudioContext
            || (window as unknown as { webkitAudioContext: typeof AudioContext })
                 .webkitAudioContext;
          const audio = new Ctx();
          const source = audio.createMediaElementSource(speaking);
          analyser = audio.createAnalyser();
          analyser.fftSize = 256;
          source.connect(analyser);
          // Straight back out to the speakers: routing the element into
          // the graph takes it OFF the default output, so forgetting
          // this line is a silent room with a moving mouth.
          analyser.connect(audio.destination);
          listened.current.set(speaking, analyser);
        } catch {
          return 0;                     // no Web Audio: the face is still
        }
      }
      const bins = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteTimeDomainData(bins);
      let sum = 0;
      for (const b of bins) sum += Math.abs(b - 128);
      return Math.min(1, (sum / bins.length) / 24);
    }

    // One named shape, set on every mesh that has it. See `shaped`.
    const set = (name: string, value: number) => {
      for (const { mesh, at } of shaped) {
        const index = at[name];
        if (index !== undefined && mesh.morphTargetInfluences) {
          mesh.morphTargetInfluences[index] = value;
        }
      }
    };

    let openness = 0;
    let last = performance.now();
    const began = last;
    function draw() {
      if (stop) return;
      frame = requestAnimationFrame(draw);
      const now = performance.now();
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      const want = loudness();
      // Eased rather than snapped: a jaw that tracks every sample reads
      // as a rattle, and a mouth is a hinge with mass on it.
      openness += (want - openness) * (want > openness ? 0.5 : 0.2);
      set("jawOpen", openness);
      // A little rounding rides with the opening so the shape reads as
      // speech rather than a yawn.
      set("mouthPucker", openness * 0.25);
      // Breath, weight, a glance and a blink. Driven after the mouth so a
      // blink is never overwritten by the frame's mouth shapes.
      live?.update((now - began) / 1000, dt, openness, set);
      renderer.render(scene, camera);
    }
    draw();

    const resize = () => {
      if (!mount.clientWidth) return;
      camera.aspect = mount.clientWidth / Math.max(mount.clientHeight, 1);
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    };
    window.addEventListener("resize", resize);

    return () => {
      stop = true;
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      // A WebGL context is a real device resource and browsers cap how
      // many a page may hold — a room of eight seats that never released
      // them would go black on the ninth.
      renderer.dispose();
      renderer.forceContextLoss();
      mount.removeChild(renderer.domElement);
    };
  }, [src, speaking, motion, shot]);

  return <div ref={holder} className={className || "avatar3d"} />;
}
