import { useEffect, useRef } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

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

export function Avatar3D({ src, speaking, className }: {
  src: string;
  /** The audio in the air right now, if any. Its loudness moves the jaw. */
  speaking?: HTMLAudioElement | null;
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

    let head: THREE.Mesh | null = null;
    let targets: Record<string, number> = {};

    new GLTFLoader().load(src, (loaded) => {
      if (stop) return;
      loaded.scene.traverse((thing) => {
        const mesh = thing as THREE.Mesh;
        if (!head && mesh.isMesh && mesh.morphTargetInfluences) {
          head = mesh;
          // The photograph, shown as photographed.
          //
          // glTF's own material is a lit one, and lighting a face that
          // was already lit when the shutter opened is how the skin got
          // washed out of it. An unlit material draws the texture at the
          // brightness it was taken at — which is the whole point of
          // building a head out of somebody's own picture — and morph
          // targets work on it exactly as they do on the lit one, so the
          // jaw still moves with the voice.
          const lit = mesh.material as THREE.MeshStandardMaterial;
          if (lit?.map) {
            mesh.material = new THREE.MeshBasicMaterial({
              map: lit.map, side: THREE.DoubleSide,
            });
            lit.dispose();
          }
          // The names ride in the mesh's extras, which is where the forge
          // put them and where every exporter puts them.
          const named = (mesh.morphTargetDictionary
            || (mesh.userData?.targetNames
                ? Object.fromEntries(
                    (mesh.userData.targetNames as string[])
                      .map((n, i) => [n, i]))
                : {})) as Record<string, number>;
          targets = named;
        }
      });
      // Framed on the head: the model is built around its own centre, so
      // the camera only has to look at the middle of what arrived.
      const box = new THREE.Box3().setFromObject(loaded.scene);
      const middle = box.getCenter(new THREE.Vector3());
      loaded.scene.position.sub(middle);
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

    let openness = 0;
    function draw() {
      if (stop) return;
      frame = requestAnimationFrame(draw);
      const want = loudness();
      // Eased rather than snapped: a jaw that tracks every sample reads
      // as a rattle, and a mouth is a hinge with mass on it.
      openness += (want - openness) * (want > openness ? 0.5 : 0.2);
      const mesh = head as THREE.Mesh | null;
      if (mesh?.morphTargetInfluences) {
        const set = (name: string, value: number) => {
          const at = targets[name];
          if (at !== undefined) mesh.morphTargetInfluences![at] = value;
        };
        set("jawOpen", openness);
        // A little rounding rides with the opening so the shape reads as
        // speech rather than a yawn.
        set("mouthPucker", openness * 0.25);
      }
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
  }, [src, speaking]);

  return <div ref={holder} className={className || "avatar3d"} />;
}
