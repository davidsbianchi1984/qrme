import * as THREE from "three";

/**
 * What makes a head look alive rather than propped up.
 *
 * `avatars.motion_of` has derived `style`, `energy` and `tempo_ms` from a
 * profile's own interaction history since the moving image was built, and
 * no renderer has ever read it. The face loaded, the jaw followed the
 * voice, and between words the model sat perfectly still — which is the
 * one thing a living face never does.
 *
 *     asked     does the mouth move when it speaks
 *     mattered  is anything moving when it doesn't
 *
 * ## Why this is procedural and not a library of clips
 *
 * A clip has to be authored for a skeleton and retargeted onto anything
 * else, and the models arriving here are built one at a time by a vendor
 * whose rig we do not control. Breath, weight and a glance are small
 * rotations on bones every humanoid rig has under names every humanoid
 * rig agrees on, so generating them costs no assets, ships nothing, and
 * works on the next vendor's model as well as this one — the same
 * reasoning that put ARKit's names in `avatarforge`.
 *
 * It is honest about its ceiling. This is idle life and conversational
 * emphasis: breathing, weight shifting, a head that drifts and nods and
 * blinks. It is not a gesture library and does not pretend to be one —
 * nothing here will fold its arms or point at something.
 *
 * ## The rest pose is the origin
 *
 * Every offset is applied *from a remembered rest rotation* rather than
 * added to whatever the bone currently holds. Accumulating instead is
 * how a subtle sway becomes a character slowly screwing itself into the
 * floor over a long conversation.
 */

/** What the backend derives about how this face carries itself. */
export type Motion = {
  style: string;
  energy: number;
  warmth: number;
  tempo_ms: number;
};

/** Sets a named ARKit shape wherever it exists. See `Avatar3D`. */
export type SetMorph = (name: string, value: number) => void;

/** How much of the motion each style wants. `still` is a real choice a
 *  person can make, so it resolves to nothing moving at all rather than
 *  to a little bit of movement. */
const STYLE_GAIN: Record<string, number> = {
  still: 0,
  breathe: 1,
  lively: 1.6,
};

/** The bones this reaches for, and the names rigs give them. Matched on a
 *  normalised name so `mixamorig:LeftArm`, `Left_Arm` and `leftarm` are
 *  one bone; the first match in each list wins. */
const WANTED: Record<string, string[]> = {
  hips: ["hips", "pelvis"],
  spine: ["spine"],
  chest: ["spine1", "chest"],
  upper: ["spine2", "upperchest"],
  neck: ["neck"],
  head: ["head"],
  armL: ["leftarm", "leftupperarm", "upperarm_l", "l_upperarm"],
  armR: ["rightarm", "rightupperarm", "upperarm_r", "r_upperarm"],
  foreL: ["leftforearm", "lowerarm_l", "l_forearm"],
  foreR: ["rightforearm", "lowerarm_r", "r_forearm"],
};

function normalise(name: string): string {
  return name.toLowerCase().replace(/^mixamorig[:_]?/, "").replace(/[_.:\s]/g, "");
}

type Held = { bone: THREE.Object3D; rest: THREE.Euler };

/**
 * The living part of a loaded model: the bones it found, and what it does
 * to them each frame.
 */
export class Liveliness {
  private held: Partial<Record<keyof typeof WANTED, Held>> = {};
  private gain: number;
  private energy: number;
  private period: number;
  private nextBlink: number;
  private blinkStart = -1;
  private nod = 0;

  /** Whether anything was found to move. A model with no skeleton is not
   *  a failure — the mouth still works — so the caller can just skip. */
  readonly rigged: boolean;

  constructor(root: THREE.Object3D, motion?: Motion | null, calm = false) {
    const lists = Object.entries(WANTED) as [keyof typeof WANTED, string[]][];
    root.traverse((thing) => {
      const flat = normalise(thing.name);
      for (const [slot, names] of lists) {
        if (this.held[slot]) continue;
        if (names.includes(flat)) {
          this.held[slot] = { bone: thing, rest: thing.rotation.clone() };
          break;
        }
      }
    });

    const style = motion?.style ?? "breathe";
    // `calm` is the viewer's own operating-system setting, and it wins over
    // the profile's disposition: somebody who asked their machine to stop
    // animating things did not mean "except faces".
    this.gain = calm ? 0 : (STYLE_GAIN[style] ?? 1);
    // Energy arrives 0..1 and is a disposition, not a volume knob — a
    // listless profile should still breathe.
    this.energy = 0.55 + 0.45 * Math.min(1, Math.max(0, motion?.energy ?? 0.5));
    // The breath period the backend already computed. `still` reports 0,
    // which would divide the wave by nothing, so the floor is a real
    // number and the gain above is what actually silences it.
    this.period = Math.max(1200, motion?.tempo_ms || 5200) / 1000;
    this.nextBlink = 1 + Math.random() * 3;
    this.rigged = Object.keys(this.held).length > 0;
  }

  private turn(slot: keyof typeof WANTED, x: number, y: number, z: number) {
    const got = this.held[slot];
    if (!got) return;
    got.bone.rotation.set(
      got.rest.x + x, got.rest.y + y, got.rest.z + z, got.rest.order);
  }

  /**
   * One frame.
   *
   * @param t        seconds since the model mounted
   * @param dt       seconds since the previous frame
   * @param loudness 0..1 of the voice in the air right now
   * @param setMorph applies an ARKit shape by name
   */
  update(t: number, dt: number, loudness: number, setMorph: SetMorph) {
    this.blink(t, dt, setMorph);
    if (!this.gain) return;

    const g = this.gain * this.energy;
    const breath = Math.sin((t / this.period) * Math.PI * 2);
    // Weight moves on its own clock. An irrational ratio to the breath so
    // the two never line up into one obvious loop.
    const shift = Math.sin((t / (this.period * 1.618)) * Math.PI * 2);
    // Two slow waves that do not share a period read as attention
    // wandering; one wave reads as a metronome.
    const driftY = Math.sin(t / 4.3) * 0.6 + Math.sin(t / 7.1) * 0.4;
    const driftX = Math.sin(t / 5.7) * 0.5 + Math.sin(t / 9.3) * 0.5;

    // Speech is emphasis on top of the idle, not a replacement for it: a
    // face that stops breathing to talk is the uncanny half of this.
    this.nod += (loudness - this.nod) * Math.min(1, dt * 6);
    const beat = Math.sin(t * 7.5) * this.nod;

    this.turn("spine", breath * 0.010 * g, shift * 0.012 * g, 0);
    this.turn("chest", breath * 0.014 * g, 0, shift * 0.010 * g);
    this.turn("upper", breath * 0.008 * g, 0, 0);
    this.turn("hips", 0, shift * 0.014 * g, shift * 0.008 * g);
    this.turn("neck", driftX * 0.020 * g, driftY * 0.030 * g, 0);
    this.turn(
      "head",
      driftX * 0.030 * g + beat * 0.055,
      driftY * 0.055 * g + Math.sin(t * 3.1) * this.nod * 0.02,
      driftY * 0.014 * g,
    );
    // Arms ride the weight shift only. Anything more expressive would be
    // a gesture, and a gesture invented from an amplitude is the kind of
    // motion that reads as a puppet.
    this.turn("armL", 0, 0, shift * 0.020 * g);
    this.turn("armR", 0, 0, -shift * 0.020 * g);
    this.turn("foreL", 0, 0, breath * 0.010 * g);
    this.turn("foreR", 0, 0, -breath * 0.010 * g);
  }

  /**
   * Blinking, which is the cheapest life on the list and the one whose
   * absence is read fastest — a face that never blinks is noticed as
   * wrong long before anybody can say why.
   *
   * Driven even when the style is `still`: a person who asked for a
   * motionless portrait did not ask for a staring one. Only the viewer's
   * reduced-motion setting stops it, and that is handled by `gain` being
   * zero *and* this returning early on `calm`.
   */
  private blink(t: number, dt: number, setMorph: SetMorph) {
    if (this.blinkStart < 0 && t >= this.nextBlink) this.blinkStart = t;
    let shut = 0;
    if (this.blinkStart >= 0) {
      const through = (t - this.blinkStart) / 0.14;
      if (through >= 1) {
        this.blinkStart = -1;
        // Human blink spacing is irregular; a fixed interval reads as a
        // tic. Two to seven seconds, which is roughly what people do.
        this.nextBlink = t + 2 + Math.random() * 5;
      } else {
        shut = Math.sin(through * Math.PI);
      }
    }
    setMorph("eyeBlinkLeft", shut);
    setMorph("eyeBlinkRight", shut);
    void dt;
  }
}
