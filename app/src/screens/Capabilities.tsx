import { useEffect, useState } from "react";
import {
  api, type Avatar, type CameraSession, type HandGrant, type MicPlaces,
  type ProfileSteering, type RobotRow, type VoiceprintStatus,
} from "../api";
import { t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * The capability register: every faculty a profile can be given, what it
 * stands on, and where it is taken back.
 *
 * The sibling of JIM-mini's screen of the same name, and deliberately the
 * same four columns — but not the same nine rows, because the two products
 * grew these faculties for different reasons and named them differently
 * while doing it. QRME lends a profile an ear (**channel 2**) and an eye
 * (**channel 3**) *into a place*, where JIM attaches them to a monitor on
 * one person. Copying JIM's wording here would have produced a register
 * that described the wrong product accurately.
 *
 *     asked     do both products have the same capabilities
 *     mattered  does each register describe its own
 *
 * ## The four columns
 *
 *   * **what it is** — the function, in a sentence, in the reader's
 *     language;
 *   * **where it stands** — read live from the same route the owning
 *     screen reads, so this cannot drift into a brochure;
 *   * **what it rests on** — the permission that had to exist first;
 *   * **where it is withdrawn** — the screen that owns it, one press away.
 *
 * ## The naming
 *
 * Named for what each faculty does, not for the body part it resembles.
 * The shorthand behind these rows is anatomical and that shorthand is
 * exactly wrong on a screen a regulator or an attorney may read: "eyes"
 * claims a faculty, where "a live view through the holder's own camera,
 * opened by the holder, minuted, and disclosed to everybody present"
 * states a behaviour somebody else can hold this product to.
 *
 * ## Nothing here acts
 *
 * No control on this screen grants, opens, commands or revokes. It reads,
 * and it routes.
 */

type Tab = "live" | "rooms" | "voice" | "presence" | "robots" | "hands"
  | "agent";

type Faculty = { key: string; opens: Tab; surface: string };

//: The register, in the order a capability is acquired rather than
//: alphabetically: what a profile takes in, how it presents, what it can
//: move, and last what it may do on its own account.
const FACULTIES: Faculty[] = [
  { key: "sight", opens: "live", surface: "nav.live" },
  { key: "hearing", opens: "rooms", surface: "nav.rooms" },
  { key: "speech", opens: "voice", surface: "nav.voice" },
  { key: "appearance", opens: "presence", surface: "nav.presence" },
  { key: "body", opens: "robots", surface: "nav.robots" },
  { key: "movement", opens: "robots", surface: "nav.robots" },
  { key: "observation", opens: "hands", surface: "nav.hands" },
  { key: "operation", opens: "hands", surface: "nav.hands" },
  { key: "unattended", opens: "agent", surface: "nav.agent" },
];

type Held = {
  cameras: CameraSession[] | null;
  places: MicPlaces | null;
  voice: VoiceprintStatus | null;
  avatar: Avatar | null;
  robots: RobotRow[] | null;
  grants: HandGrant[] | null;
  steering: ProfileSteering | null;
};

const NOTHING: Held = {
  cameras: null, places: null, voice: null, avatar: null,
  robots: null, grants: null, steering: null,
};

export function Capabilities({ go }: { go: (tab: string) => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const L = (key: string) => tr(key, lang);
  const [held, setHeld] = useState<Held>(NOTHING);
  const [read, setRead] = useState(false);

  useEffect(() => {
    const me = session.profileId || "";
    const token = session.ownerToken || "";
    if (!me || !token) return;
    // `allSettled`, not `all`. A deployment with no voice forge, or a
    // profile that never opened a camera, refuses on its own route by
    // design — and one rejection must not blank the other eight rows.
    Promise.allSettled([
      api.liveCameras(me, token),
      api.micPlaces(),
      api.voiceprint(me, token),
      api.avatar(me, token),
      api.robots(me, token),
      api.handGrants(me, token, true),
      api.profileSteering(me, token),
    ]).then(([cam, places, voice, avatar, robots, grants, steering]) => {
      const got = <T,>(r: PromiseSettledResult<T>): T | null =>
        r.status === "fulfilled" ? r.value : null;
      setHeld({
        cameras: got(cam),
        places: got(places),
        voice: got(voice),
        avatar: got(avatar),
        robots: got(robots),
        grants: got(grants)?.grants ?? null,
        steering: got(steering),
      });
      setRead(true);
    });
  }, [session.profileId, session.ownerToken]);

  /** What each faculty is doing right now.
   *
   *  `null` is not "off" and is never drawn as off: it is this console
   *  not having been able to ask. The two are different facts and a
   *  register that let them look the same would be worse than none. */
  function standing(key: string): string | null {
    const live = held.grants ?? [];
    switch (key) {
      case "sight": {
        if (held.cameras === null) return null;
        const open = held.cameras.filter((c) => c.live);
        return open.length === 0 ? L("cap.sight.none")
          : L("cap.sight.some").replace("{n}", String(open.length))
              .replace("{where}", open.map((c) => c.surface).join(", "));
      }
      case "hearing":
        if (held.places === null) return null;
        return held.places.places.length === 0 ? L("cap.hearing.none")
          : L("cap.hearing.some").replace(
              "{n}", String(held.places.places.length));
      case "speech": {
        if (held.voice === null) return null;
        if (!held.voice.consent.granted) return L("cap.speech.nogate");
        if (held.voice.voiceprint?.active) return L("cap.speech.some");
        return held.voice.enrollment
          ? L("cap.speech.enrolling") : L("cap.speech.none");
      }
      case "appearance":
        if (held.avatar === null) return null;
        return held.avatar.asset
          ? L("cap.appearance.some")
          : L("cap.appearance.none");
      case "body":
        if (held.robots === null) return null;
        return held.robots.length === 0 ? L("cap.body.none")
          : L("cap.body.some").replace("{n}", String(held.robots.length))
              .replace("{names}", held.robots.map((r) => r.name).join(", "));
      case "movement": {
        if (held.robots === null) return null;
        // Movement is not its own binding: it is the intersection of what
        // the bound platforms will accept, so with nothing bound there is
        // nothing that could be told to move.
        const moves = new Set<string>();
        for (const r of held.robots) for (const c of r.commands) moves.add(c);
        return held.robots.length === 0 ? L("cap.movement.none")
          : L("cap.movement.some").replace(
              "{moves}", [...moves].sort().join(", "));
      }
      case "observation": {
        if (held.grants === null) return null;
        const looking = live.filter((g) => g.verbs.includes("look"));
        return looking.length === 0 ? L("cap.observation.none")
          : L("cap.observation.some").replace("{n}", String(looking.length));
      }
      case "operation": {
        if (held.grants === null) return null;
        const acting = live.filter(
          (g) => g.verbs.some((v) => v !== "look"));
        return acting.length === 0 ? L("cap.operation.none")
          : L("cap.operation.some").replace("{n}", String(acting.length));
      }
      case "unattended":
        if (held.steering === null) return null;
        return held.steering.lock
          ? L("cap.unattended.locked")
          : L("cap.unattended.some").replace(
              "{n}", String(held.steering.dials.length));
      default:
        return null;
    }
  }

  return (
    <>
      <div className="screen-head">
        <h2>{L("cap.title")}</h2>
        <p className="muted small">{L("cap.lead")}</p>
      </div>
      <div className="card">
        <p className="small">{L("cap.standing")}</p>
      </div>
      {FACULTIES.map((f) => {
        const now = standing(f.key);
        return (
          <div className="card" key={f.key}>
            <h3>{L(`cap.${f.key}.title`)}</h3>
            <p className="muted small">{L(`cap.${f.key}.what`)}</p>
            <p className="small">
              <strong>{L("cap.now")}</strong>{" "}
              {now === null
                ? <span className="muted">
                    {read ? L("cap.unreadable") : L("cap.reading")}
                  </span>
                : <span>{now}</span>}
            </p>
            <p className="small">
              <strong>{L("cap.rests")}</strong>{" "}
              <span className="muted">{L(`cap.${f.key}.rests`)}</span>
            </p>
            <button onClick={() => go(f.opens)}>
              {L("cap.open").replace("{screen}", L(f.surface))}
            </button>
          </div>
        );
      })}
    </>
  );
}
