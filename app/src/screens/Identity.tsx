import { useEffect, useRef, useState } from "react";
import { SkinTiles } from "../SkinTiles";
import { VideoQuote } from "../VideoQuote";
import { api, getBase, getSignupKey, type Anonymity, type Avatar,
         type AvatarBrief, type Deleted,
         type Emblem, type IdentityVocabulary, type Memorial,
         type RegistryRow, type Sibling,
         type Sunset, type Verifiable, type Verification } from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr, visitorLang } from "../l10n";
import { useSession } from "../store";

/**
 * Who this profile is, who is allowed to know, and how it ends.
 *
 * Nineteen routes with no caller — including `DELETE /profiles/{id}`, so the
 * console could make a profile and never remove one.
 *
 * The screen is arranged around the rule that holds the feature together:
 * **you may have as many profiles as you like, any of them may be anonymous,
 * and at most one may be verified — because the badge says you are a
 * particular real person, and said of two profiles at once it is either false
 * of one or a claim that you are two people.** So the roster comes first, with
 * the badge shown as a thing that *sits somewhere and can move*, rather than a
 * checkbox on each profile that happens to refuse.
 *
 * Three things are shown rather than paraphrased:
 *
 * - the `not_withheld` list, at the same weight as `withheld`. Anonymity here
 *   is a promise about what the platform publishes, not a promise that nobody
 *   can recognise your writing, and a screen that showed only the first half
 *   would be selling the second;
 * - whichever refusal the server sends when a claim is rejected — 422 for a
 *   malformed one, 409 for the one-badge rule — because both already carry the
 *   sentence a person needs;
 * - the itemised deletion receipt, one count per table. "Deleted" is a claim;
 *   twenty-five numbers are evidence.
 */
export function Identity({ onPlans, onPassing }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
  /** Beginning and passing on — pre-building, recovery, how it ends. An
   *  option taken from here rather than a tab lived in. */
  onPassing: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const token = session.ownerToken || "";

  const [vocab, setVocab] = useState<IdentityVocabulary | null>(null);
  const [roster, setRoster] = useState<Sibling[]>([]);
  const [verification, setVerification] = useState<Verification | null>(null);
  const [verifiable, setVerifiable] = useState<Verifiable | null>(null);
  const [anon, setAnon] = useState<Anonymity | null>(null);
  const [avatar, setAvatar] = useState<Avatar | null>(null);
  // The avatar deck: market import sources, the file input, and the selfie
  // capture (camera frames from several angles, uploaded through the same
  // media door as any photo, then imported as the portrait).
  const [market, setMarket] = useState<{ key: string; name: string;
                                         how: string }[]>([]);
  // The first live row of the market list. It used to be a hard-coded
  // "ready_player_me", which is how a picker came to open on a service
  // Netflix had shut down — a default naming one row is a default that
  // rots when that row goes. The server's own list decides now.
  const [marketKey, setMarketKey] = useState("");
  // The forge: what this deployment can build from a photograph, and the
  // framing of the picture being handed to it.
  // Which of the three roads this profile's presence takes.
  //
  // Stored on the server, not held here. It used to be component state,
  // and that was fine while the only thing it did was decide which block
  // this screen drew — but auto-render reads the road on a turn nobody
  // is looking at this screen for, and a choice living in a component is
  // a choice `/profiles/{id}/chat` cannot see. `budget` is the other
  // half: every reply renders, so the ceiling is what makes video safe
  // to pick, and it is shown next to the road rather than on a settings
  // page somebody finds after the bill.
  const [road, setRoad] = useState<"photo" | "avatar" | "video">("photo");
  const [budget, setBudget] = useState<
    { daily_seconds: number; spent: number; left: number;
      providers?: string[] } | null>(null);
  const [capDraft, setCapDraft] = useState("");
  // Which company renders this profile. Held here rather than read off
  // `film` because that is the DEPLOYMENT's choice: once an owner picks,
  // the two disagree, and the tile has to light on the owner's.
  const [filmPick, setFilmPick] = useState("");
  // The drawer the roads open, so pressing one can bring it to the eye
  // rather than leaving it somewhere below the fold.
  const drawer = useRef<HTMLDivElement | null>(null);
  const [film, setFilm] = useState<
    Awaited<ReturnType<typeof api.videoDoors>> | null>(null);
  const [passage, setPassage] = useState("");
  const [videoShape, setVideoShape] = useState("landscape");
  const [filming, setFilming] = useState(false);
  // How this profile's scenes are shot, carried from one render to the
  // next. Amended in the owner's own words rather than typed out again.
  const [direction, setDirection] = useState("");
  const [sceneAsk, setSceneAsk] = useState("");
  const [directing, setDirecting] = useState(false);
  const [sceneLog, setSceneLog] = useState<
    Awaited<ReturnType<typeof api.videoDirectionLog>>["log"]>([]);

  const [forge, setForge] = useState<
    { provider: string; configured: boolean; shots: string[] } | null>(null);
  const [shot, setShot] = useState("face");
  const [forging, setForging] = useState(false);
  const [marketUrl, setMarketUrl] = useState("");
  const [marketTorso, setMarketTorso] = useState("");
  // The provider's own id for an imported avatar (an ElevenLabs avatar
  // id, a Ready Player Me GUID) — recorded into the registry row's
  // provenance so the face remembers where it came from.
  const [marketPid, setMarketPid] = useState("");
  // The deployment's default faces: the shelf the operator stocked.
  // Tapping one claims it through the registry, so a takedown later
  // still reaches every profile that wore it.
  const [shelfRows, setShelfRows] = useState<RegistryRow[]>([]);
  const [capturing, setCapturing] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const captureAngles = ["front", "left", "right", "up", "down"];
  const [captured, setCaptured] = useState<string[]>([]);

  // The stream attaches in an effect, not in the click handler: the <video>
  // only exists after React commits the `capturing` render, and a single
  // requestAnimationFrame raced that commit — permission granted, camera
  // running, and a screen showing nothing. The effect runs after commit by
  // definition, and the explicit play() is for the phones, which do not
  // autoplay a stream attached after mount.
  useEffect(() => {
    if (capturing && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(() => undefined);
    }
  }, [capturing]);

  // Leaving the screen mid-capture must release the camera — a light that
  // stays on after the person walked away is a promise broken.
  useEffect(() => () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  const reloadAvatar = () =>
    api.avatar(me, token).then(setAvatar).catch(() => undefined);

  // One camera frame, as a JPEG file the media door already accepts.
  const frameToFile = (angle: string): File | null => {
    const v = videoRef.current;
    if (!v || !v.videoWidth) return null;
    const c = document.createElement("canvas");
    c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext("2d")!.drawImage(v, 0, 0);
    const data = c.toDataURL("image/jpeg", 0.92);
    const bytes = atob(data.split(",")[1]);
    const arr = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
    return new File([arr], `capture-${angle}.jpg`, { type: "image/jpeg" });
  };

  async function startCapture() {
    setError(null); setCaptured([]);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" } });
      streamRef.current = stream;
      setCapturing(true);   // the effect above attaches it after commit
    } catch (e) { fail(e); }
  }

  function stopCapture() {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setCapturing(false);
  }

  async function snapAngle(angle: string) {
    const file = frameToFile(angle);
    if (!file) return;
    try {
      const saved = await api.uploadMedia(me, file, token);
      setCaptured((c) => [...c, saved.url]);
    } catch (e) { fail(e); }
  }

  async function finishCapture() {
    stopCapture();
    if (captured.length === 0) return;
    try {
      // The first frame taken (front) becomes the portrait; every angle
      // travels with it as provenance.
      await api.importAvatar(me,
        { source: "capture", asset: captured[0], extra: captured.slice(1) },
        token);
      setNote(tr("idn.deck.done", lang));
      setCaptured([]);
      reloadAvatar();
    } catch (e) { fail(e); }
  }

  /** Every file a person actually has, taken by the same box.
   *
   *      asked     do the FBX conversion in the app
   *      mattered  the door could not ACCEPT one to begin with
   *
   * `media.save` proves a format from its bytes and an FBX matches
   * nothing it knows, so an FBX upload came back "unrecognized file" and
   * the shelf's answer was a page of Blender menus. A model goes to the
   * converter first and arrives here as the `.glb` it came back as; a
   * picture goes the way it always did. */
  function isModelExport(file: File): boolean {
    const name = file.name.toLowerCase();
    return name.endsWith(".fbx") || name.endsWith(".zip");
  }

  /** What this box may be handed, asked of the deployment rather than
   *  assumed. A console that offers to convert an FBX on a box with no
   *  forge is a button that fails, and the shelf's own row now promises
   *  the conversion in writing — so the promise and the accept list come
   *  from the same answer. */
  const [takesModels, setTakesModels] = useState(false);
  useEffect(() => {
    let gone = false;
    api.convertDoors()
      .then((d) => { if (!gone) setTakesModels(!!d.configured); })
      .catch(() => { if (!gone) setTakesModels(false); });
    return () => { gone = true; };
  }, []);

  async function importPhoto(file: File) {
    setError(null); setNote(null);
    try {
      let asset: string;
      if (isModelExport(file)) {
        setNote(tr("idn.model.converting", lang));
        const bytes = new Uint8Array(await file.arrayBuffer());
        let binary = "";
        // Chunked for the same reason the forge's reader is: one apply()
        // over a seven-megabyte model blows the argument limit.
        for (let at = 0; at < bytes.length; at += 0x8000) {
          binary += String.fromCharCode(...bytes.subarray(at, at + 0x8000));
        }
        const made = await api.convertModel(me, btoa(binary), file.name, token);
        asset = made.asset;
        // What survived, said rather than assumed. A conversion that
        // dropped the mouth shapes would still return a model, and the
        // only place anybody would notice is a face that stopped being
        // able to speak.
        setNote(tr("idn.model.done", lang)
                  .replace("{shapes}", String(made.named)));
      } else {
        const saved = await api.uploadMedia(me, file, token);
        asset = saved.url;
      }
      await api.importAvatar(me, { source: "photos", asset }, token);
      if (!isModelExport(file)) setNote(tr("idn.deck.done", lang));
      reloadAvatar();
    } catch (e) { fail(e); }
  }

  /** A photograph becomes a face, built here rather than bought.
   *
   *  The bytes go up as base64 rather than through the media door,
   *  because the photograph is the INPUT and not the keepsake: what is
   *  stored afterwards is the head it became. */
  /** The 3-D head, for anybody who wants one.
   *
   * It is second on the card and says what it is, because a head built
   * from 478 face landmarks has no skull, no hair and no ears — it is a
   * mask, and the field said so looking at one. It stays reachable
   * because it is real and it works, and because deleting the only door
   * to a capability is a different act from taking it off the front of a
   * screen. Sharing `forgeFrom`'s reading and encoding rather than
   * copying them: one road in, two things it can build.
   */
  async function headFrom(file: File | undefined) {
    await forgeFrom(file, "head");
  }

  async function forgeFrom(file: File | undefined,
                           makes: "speaking" | "head" = "speaking") {
    if (!file) return;
    setError(null); setNote(null); setForging(true);
    try {
      const bytes = new Uint8Array(await file.arrayBuffer());
      let binary = "";
      // Chunked: one apply() over a multi-megabyte photograph blows the
      // argument limit on every browser that matters.
      for (let at = 0; at < bytes.length; at += 0x8000) {
        binary += String.fromCharCode(...bytes.subarray(at, at + 0x8000));
      }
      if (makes === "head") {
        await api.forgeFace(me, btoa(binary), shot, token);
      } else {
        await api.speakingFace(me, btoa(binary), shot, token);
      }
      setNote(tr("idn.forge.done", lang));
      reloadAvatar();
    } catch (e) { fail(e); } finally { setForging(false); }
  }

  async function importMarket() {
    if (!marketUrl.trim()) return;
    setError(null); setNote(null);
    try {
      await api.importAvatar(me,
        { source: marketKey, asset: marketUrl.trim(),
          ...(marketTorso.trim() ? { torso: marketTorso.trim() } : {}),
          ...(marketPid.trim()
            ? { provider_asset_id: marketPid.trim() } : {}) },
        token);
      setNote(tr("idn.deck.done", lang));
      setMarketUrl("");
      reloadAvatar();
    } catch (e) { fail(e); }
  }
  const [emblems, setEmblems] = useState<Emblem[]>([]);
  const [briefs, setBriefs] = useState<AvatarBrief[]>([]);
  const [memorial, setMemorial] = useState<Memorial | null>(null);
  const [gone, setGone] = useState<Deleted | null>(null);
  const [ended, setEnded] = useState<Sunset | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  // Which brief's full prompt is open, shown inline under its own row.
  const [promptFor, setPromptFor] = useState<string | null>(null);
  const [promptText, setPromptText] = useState("");
  // The minted handoff, rendered as a scannable code under the button.
  const [exportQr, setExportQr] =
    useState<Awaited<ReturnType<typeof api.exportTicket>> | null>(null);
  // A handoff link scanned or pasted on this device, waiting to redeem.
  const [handoffLink, setHandoffLink] = useState("");

  const [level, setLevel] = useState("self_asserted");
  const [attestor, setAttestor] = useState("");
  const [method, setMethod] = useState("");
  const [name, setName] = useState("");
  // What kind of thing this profile is, read back from the profile itself
  // rather than assumed — the picker must show what is stored, not what
  // the last press asked for.
  const [kind, setKind] = useState("fictional");
  // Shown, never set from here. Null until the profile is read, so an
  // unknown state reads as unknown rather than as "off".
  const [rated, setRated] = useState<boolean | null>(null);
  // Your own picture — the PERSON's, not this profile's portrait. Read
  // here as well as in a room, because until this card the only way to
  // put a face on your own seat was to already be sitting in one.
  const [myPic, setMyPic] = useState<string | null>(null);
  const myPicker = useRef<HTMLInputElement | null>(null);
  const iAm = session.interactorId || "";
  const myToken = session.interactorToken || "";
  function reloadMyPic() {
    if (!iAm || !myToken) return;
    api.ownPicture(iAm, myToken)
      .then((r) => setMyPic(r.url))
      .catch(() => setMyPic(null));
  }
  useEffect(reloadMyPic, [iAm, myToken]);
  // The people in your phone — the book, or the reason there is none.
  // The refusal is the information: not granted says so in the person's
  // own language, and the switch is on the same card.
  const [book, setBook] = useState<
    { book: { id: string; name: string; holds_account: boolean;
              added_at: string }[]; held: number } | null>(null);
  const [bookError, setBookError] = useState<string | null>(null);
  function reloadBook() {
    if (!iAm || !myToken) return;
    api.contactsBook(iAm, myToken)
      .then((b) => { setBook(b); setBookError(null); })
      .catch((e) => { setBook(null); setBookError((e as Error).message); });
  }
  useEffect(reloadBook, [iAm, myToken]);
  /** The device's book, through the browser's own picker. A synced
   *  source, never something people type; where the platform offers no
   *  picker the honest sentence stands in, and the shell backlogs carry
   *  the native road. Picking IS the grant: the switch is flipped on the
   *  same press that hands the book over, and the withdraw button is the
   *  way back. */
  async function syncBook() {
    if (!iAm || !myToken) return;
    const nav = navigator as unknown as {
      contacts?: {
        select: (props: string[], opts: { multiple: boolean })
          => Promise<{ name?: string[]; tel?: string[] }[]>;
      };
    };
    if (!nav.contacts?.select) {
      setBookError(tr("idn.book.nopicker", lang));
      return;
    }
    let picked: { name?: string[]; tel?: string[] }[];
    try {
      picked = await nav.contacts.select(["name", "tel"], { multiple: true });
    } catch {
      return; // closed the picker; nothing to say
    }
    const entries = picked.flatMap((person) =>
      (person.tel || []).map((number) => ({
        name: (person.name || [])[0] || "", number })));
    if (!entries.length) return;
    setError(null); setNote(null);
    try {
      await api.decideContacts(iAm, true, myToken);
      await api.syncContacts(iAm, entries, myToken);
      reloadBook();
    } catch (e) { fail(e); }
  }
  const [confirmEnd, setConfirmEnd] = useState<"" | "sunset" | "delete">("");
  // Everything this person holds, across every profile they have talked
  // to. Loaded on a press rather than on mount: it is the single most
  // private read in this product, and a screen that fetches somebody's
  // whole record just for being opened is a screen that decided for them.
  const [mine, setMine] = useState<Awaited<
    ReturnType<typeof api.ownMemories>> | null>(null);
  // The bargain the free tier is, and the switch that makes "you can turn
  // it off" a fact rather than a sentence. Read on mount, unlike the
  // memories themselves: this is a setting, not somebody's words.
  const [giving, setGiving] = useState<Awaited<
    ReturnType<typeof api.ownContribution>> | null>(null);
  useEffect(() => {
    if (!iAm || !myToken) return;
    api.ownContribution(iAm, myToken).then(setGiving).catch(() => undefined);
  }, [iAm, myToken]);

  const fail = (e: unknown) => setError(e);

  useEffect(() => {
    api.identityVocabulary().then((v) => {
      setVocab(v);
      setLevel(v.proofing_levels[0]?.level || "self_asserted");
    }).catch(fail);
    api.emblems().then((r) => setEmblems(r.emblems)).catch(() => undefined);
    api.avatarBriefs().then((r) => setBriefs(r.briefs)).catch(() => undefined);
    api.avatarMarket().then((r) => {
      setMarket(r.skin_sources);
      // Open on whatever the server actually offers first, so a row
      // being struck from the list can never leave the picker pointing
      // at it.
      setMarketKey((k) => k || r.skin_sources[0]?.key || "");
    }).catch(() => undefined);
    api.forgeDoors().then(setForge).catch(() => setForge(null));
    // The video road's own door, asked before anybody writes anything:
    // a screen that draws the road on a deployment with none is a button
    // that fails, and somebody who has just written what they wanted is
    // the worst moment to find out.
    api.videoDoors().then(setFilm).catch(() => setFilm(null));
    if (me) {
      // The stored road, so the picker opens on what the chat endpoint
      // will actually do rather than on this component's default.
      api.videoRoad(me, token).then((r) => {
        setRoad(r.road as "photo" | "avatar" | "video");
        setBudget(r);
        setCapDraft(String(r.daily_seconds));
        setFilmPick(r.provider);
      }).catch(() => setBudget(null));
      api.videoDirection(me).then((r) => setDirection(r.direction))
        .catch(() => setDirection(""));
      api.videoDirectionLog(me).then((r) => setSceneLog(r.log))
        .catch(() => setSceneLog([]));
    }
    api.avatarShelf().then((r) => setShelfRows(r.shelf))
      .catch(() => setShelfRows([]));
  }, []);

  /** Take the road, and keep it.
   *
   * The picker moves first and the request follows, because the block
   * below it is the whole reason somebody pressed: making them wait on a
   * round trip to see the video options would be a spinner in place of a
   * fold. If the write fails the server's answer wins — a picker showing
   * "video" over a profile still stored as "photo" is the one state that
   * would have somebody wondering why no footage ever arrives.
   */
  async function chooseRoad(key: "photo" | "avatar" | "video") {
    setRoad(key);
    // After the paint that adds it, not before — the element does not
    // exist yet on the press that opens it, and scrolling to a ref that
    // is still null is the silent no-op version of this whole bug.
    requestAnimationFrame(() => {
      drawer.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    if (!me) return;
    try {
      const got = await api.videoSetRoad(me, token, key);
      setRoad(got.road as "photo" | "avatar" | "video");
      setBudget(got);
      setCapDraft(String(got.daily_seconds));
      setFilmPick(got.provider);
    } catch (e) {
      fail(e);
      api.videoRoad(me, token).then((r) => {
        setRoad(r.road as "photo" | "avatar" | "video");
        setBudget(r);
        setFilmPick(r.provider);
      }).catch(() => undefined);
    }
  }

  /** Move the ceiling. Sent with the road it belongs to, since that is
   *  the pair the server stores — and a ceiling is only ever raised or
   *  lowered by the person who has to live under it. */
  async function setCeiling() {
    if (!me) return;
    const seconds = Number(capDraft);
    if (!Number.isFinite(seconds) || seconds < 0) return;
    try {
      const got = await api.videoSetRoad(me, token, road, Math.round(seconds));
      setBudget(got);
      setCapDraft(String(got.daily_seconds));
      setFilmPick(got.provider);
    } catch (e) {
      fail(e);
    }
  }

  /** Choose which company renders this profile's footage.
   *
   *  Sent with the road for the same reason the ceiling is — the three
   *  live in one row — and the answer wins over the press, so a tile lit
   *  on screen always names the service the next render will actually go
   *  to. This picker had no handler at all until now: it drew every
   *  provider, highlighted the deployment's, and dropped every click, so
   *  picking a service looked like it worked and changed nothing.
   */
  async function chooseFilmProvider(key: string) {
    if (!me) return;
    try {
      const got = await api.videoSetRoad(me, token, road, undefined, key);
      setBudget(got);
      setFilmPick(got.provider);
    } catch (e) {
      fail(e);
    }
  }

  /** Send the passage to be rendered. Length is never passed: the
   *  backend derives it from the words, which is the whole reason there
   *  is no dial on this screen. */
  async function renderScene() {
    setFilming(true);
    setNote(null);
    try {
      const got = await api.videoRender(passage, videoShape, me);
      // `fill` answers nodes for the places that render markup; this is a
      // plain note, so the two strings are plain too.
      setNote(got.video_url ? tr("idn.video.done", lang)
                            : tr("idn.video.queued", lang));
    } catch (e) {
      fail(e);
    } finally {
      setFilming(false);
    }
  }

  /** Their words, applied. The direction comes back rewritten rather
   *  than lengthened — see `filming.amend` for why appending degrades. */
  async function directScene() {
    setDirecting(true);
    try {
      const got = await api.videoDirect(me, sceneAsk, "window");
      setDirection(got.direction);
      setSceneAsk("");
      setSceneLog((await api.videoDirectionLog(me)).log);
    } catch (e) {
      fail(e);
    } finally {
      setDirecting(false);
    }
  }

  async function undirectScene() {
    try {
      setDirection((await api.videoUndirect(me)).direction);
      setSceneLog((await api.videoDirectionLog(me)).log);
    } catch (e) {
      fail(e);
    }
  }

  function reload() {
    if (!me || !token) return;
    api.siblings(me, token).then((r) => setRoster(r.profiles)).catch(fail);
    api.verification(me, token).then(setVerification).catch(fail);
    api.verifiable(me, token).then(setVerifiable).catch(() => setVerifiable(null));
    api.anonymity(me, token).then(setAnon).catch(fail);
    api.avatar(me, token).then(setAvatar).catch(() => setAvatar(null));
    api.getProfile(me).then((p) => {
      setKind(p.kind);
      setRated(!!p.adult_mode);
    }).catch(() => undefined);
    // 409 while the profile is active, which is the ordinary case rather
    // than a failure worth a banner.
    api.memorial(me).then(setMemorial).catch(() => setMemorial(null));
  }
  useEffect(reload, [me, token]);

  async function claim() {
    setError(null); setNote(null);
    try {
      setVerification(await api.claimVerification(me, {
        level,
        attestor: attestor.trim() || undefined,
        method: method.trim() || undefined,
      }, token));
      setNote("Recorded.");
      reload();
    } catch (e) { fail(e); }   // 422 or 409 — the server's own sentence
  }

  const needsAttestor =
    vocab?.proofing_levels.find((l) => l.level === level)?.needs_attestor ?? false;

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("idn.title", lang)}</h2>
        {/* Beginning and passing on left the sidebar: pre-building an
            account, recovery, and how it ends are options taken from the
            identity they concern. */}
        <button className="chip" data-go="passing" onClick={onPassing}>
          {tr("idn.passing", lang)}
        </button>
      </header>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {vocab && (
        <div className="card">
          <h3>{tr("idn.rules", lang)}</h3>
          {/* The backend's own six sentences. */}
          <ul className="small">{vocab.rules.map((r) => <li key={r}>{r}</li>)}</ul>
        </div>
      )}

      <div className="card">
        <h3>{tr("idn.roster", lang)}</h3>
        <p className="muted small">{tr("idn.roster.pitch", lang)}</p>
        {roster.length === 0 && <p className="muted small">{tr("idn.roster.none", lang)}</p>}
        {roster.map((s) => (
          <div key={s.profile_id} className="row">
            <div style={{ flex: 1 }}>
              <strong>{s.shown_as}</strong>
              {s.profile_id === me && <span className="chip"> {tr("idn.roster.thisone", lang)}</span>}
              {s.anonymous && <span className="chip"> {tr("idn.roster.anon", lang)}</span>}
              <div className="muted small">
                {s.kind} · {s.status}
                {s.verified
                  ? <> · <b>{fill(tr("idn.roster.verified", lang),
                       { level: s.level })}</b></>
                  : s.can_be_verified
                    ? <> · {tr("idn.roster.notverified", lang)}</>
                    /* Not the same as "not yet". There is nobody to check. */
                    : <> · {tr("idn.roster.unverifiable", lang)}</>}
              </div>
            </div>
            {/* The badge moves; it is not re-earned. Offered on any sibling
                that could hold it and does not. */}
            {!s.verified && s.can_be_verified && s.profile_id !== me && (
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  const r = await api.moveBadge(s.profile_id, token);
                  setNote(`${r.note} It is now on ${s.shown_as}.`);
                  reload();
                } catch (e) { fail(e); }
              }}>{tr("idn.roster.move", lang)}</button>
            )}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("idn.ver", lang)}</h3>
        {verification && !verification.verified && (
          <p className="small">{verification.note}</p>
        )}
        {verification && verification.verified && (
          <>
            <p className="small">
              {fill(tr("idn.ver.means", lang), {
                means: <b>{verification.means}</b>,
                level: verification.level, rank: verification.rank,
              })}
            </p>
            <p className="muted small">
              {verification.attestor
                ? fill(tr("idn.ver.checkedby", lang),
                    { who: verification.attestor })
                : tr("idn.ver.withheld", lang)}
              {verification.method && <> · {verification.method}</>}
              {" · "}{verification.checked_at}
            </p>
            {verification.caveat && (
              <p className="small">{verification.caveat}</p>
            )}
          </>
        )}

        {verifiable && !verifiable.can_verify && (
          <div className="card">
            <p className="small">{verifiable.reason}</p>
            {verifiable.movable && verifiable.held_by && (
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  const r = await api.moveBadge(me, token);
                  setNote(r.note);
                  reload();
                } catch (e) { fail(e); }
              }}>{tr("idn.ver.movehere", lang)}</button>
            )}
          </div>
        )}

        {verifiable?.can_verify && (
          <>
            <div className="row">
              <select value={level} onChange={(e) => setLevel(e.target.value)}>
                {vocab?.proofing_levels.map((l) => (
                  <option key={l.level} value={l.level}>{l.level}</option>
                ))}
              </select>
              <input value={attestor} onChange={(e) => setAttestor(e.target.value)}
                     placeholder={needsAttestor ? "who checked (required)" : "who checked"}
                     style={{ flex: 1 }} />
              <input value={method} onChange={(e) => setMethod(e.target.value)}
                     placeholder={tr("idn.ver.how.ph", lang)} />
              <button disabled={needsAttestor && !attestor.trim()} onClick={claim}>
                {tr("idn.ver.record", lang)}
              </button>
            </div>
            <p className="muted small">
              {vocab?.proofing_levels.find((l) => l.level === level)?.means}
              {needsAttestor && tr("idn.proof.whochecked", lang)}
            </p>
          </>
        )}
      </div>

      {anon && (
        <div className="card">
          <h3>{tr("idn.anon", lang)}</h3>
          <p className="small">
            {fill(tr("idn.anon.shown", lang), {
              name: <strong>{anon.shown_as}</strong>, note: anon.note,
            })}
          </p>
          <div className="row">
            <button onClick={async () => {
              setError(null); setNote(null);
              try {
                const a = await api.setAnonymity(me, !anon.anonymous, token);
                setAnon(a);
                if (a.note_on_change) setNote(a.note_on_change);
                reload();
              } catch (e) { fail(e); }
            }}>
              {anon.anonymous ? tr("idn.anon.publish", lang)
                : tr("idn.anon.withhold", lang)}
            </button>
            {anon.reversible && (
              <span className="muted small">{tr("idn.anon.reversible", lang)}</span>
            )}
          </div>
          <div className="row">
            <div style={{ flex: 1 }}>
              <h4>{tr("idn.anon.withheld", lang)}</h4>
              <ul className="small">
                {anon.withheld.map((w) => <li key={w}>{w}</li>)}
              </ul>
            </div>
            {/* Same weight, deliberately. This is the half people are
                surprised by, and a screen that showed only the other one
                would be promising something the product does not do. */}
            <div style={{ flex: 1 }}>
              <h4>{tr("idn.anon.notwithheld", lang)}</h4>
              <ul className="small">
                {anon.not_withheld.map((w) => <li key={w}>{w}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h3>{tr("idn.bubble", lang)}</h3>
        {avatar && (
          <>
            {/* The picture itself, first. This card used to *describe* the
                bubble — an asset path in a code span — and the field report
                read exactly as that deserved: not sure what is going on
                here. A picture card shows the picture. */}
            <div className="idn-bubble-row">
              {avatar.asset && !avatar.placeholder ? (
                <img className="idn-bubble" src={getBase() + avatar.asset}
                     alt={tr("idn.bubble", lang)} />
              ) : (
                <span className="idn-bubble idn-bubble-empty" aria-hidden="true" />
              )}
              {(avatar.placeholder || avatar.silhouette) && (
                <p className="small" style={{ flex: 1 }}>
                  {tr("idn.bubble.empty", lang)}
                </p>
              )}
            </div>
            {/* Always displayed, by the product's own rule — so the screen
                shows it rather than implying it is a setting. */}
            <p className="muted small">
              {avatar.watermark.line} — {avatar.watermark.disclosure}
            </p>
            <p className="muted small">{avatar.likeness.note}</p>
            {/* The moving image: the style is the owner's choice; the
                animation itself follows the interaction history, so the
                numbers here change as the relationships do. */}
            <p className="small">
              {tr("idn.motion", lang)}{" "}
              {["still", "breathe", "lively"].map((s) => (
                <button key={s} className="chip"
                        disabled={!avatar.asset && s !== "still"}
                        style={s === avatar.motion.style
                          ? { fontWeight: 700 } : undefined}
                        onClick={async () => {
                          setError(null);
                          try {
                            setAvatar(await api.setAvatar(
                              me, avatar.asset ?? "", token, s));
                          } catch (err) { fail(err); }
                        }}>{s}</button>
              ))}
              {avatar.motion.tempo_ms > 0 && (
                <span className="motion-dot" aria-hidden
                      style={{ animationDuration:
                               `${avatar.motion.tempo_ms}ms` }} />
              )}
            </p>
            <p className="muted small">{tr("idn.motion.note", lang)}</p>
          </>
        )}
        <div className="row">
          {emblems.slice(0, 8).map((e) => (
            <button key={e.emblem} className="chip" onClick={async () => {
              setError(null); setNote(null);
              try {
                const r = await api.setEmblem(me, e.emblem, token);
                setNote(`${e.means} — ${r.note}`);
                api.avatar(me, token).then(setAvatar).catch(() => undefined);
              } catch (err) { fail(err); }
            }}>{e.emblem}</button>
          ))}
        </div>
        {/* ---- the avatar deck ---------------------------------------
            Three shelves. Characters: the starter portraits, pick one and
            it becomes the face. Your own face: import a photo, or capture
            it from several angles with the camera. Market: an avatar the
            person already owns somewhere else, imported — the provider's
            license governs it, and the import is on the record. */}
        <h4>{tr("idn.deck.characters", lang)}</h4>
        {/* The asset path comes from the brief itself — the server names
            where its portraits live; the client never spells a path. */}
        <div className="deck-grid">
          {briefs.filter((b) => b.asset).slice(0, 12).map((b) => (
            <button key={b.handle} className="deck-face" title={b.handle}
                    onClick={async () => {
                      setError(null); setNote(null);
                      try {
                        await api.setAvatar(me, b.asset!, token);
                        setNote(tr("idn.deck.done", lang));
                        reloadAvatar();
                      } catch (e) { fail(e); }
                    }}>
              <img src={getBase() + b.asset} alt={b.handle} loading="lazy" />
            </button>
          ))}
        </div>

        <h4>{tr("idn.deck.own", lang)}</h4>
        <p className="muted small">{tr("idn.deck.own.sub", lang)}</p>
        <div className="row">
          <label className="chip" style={{ marginBottom: 0 }}>
            {tr("idn.deck.upload", lang)}
            <input type="file"
                   accept={takesModels
                     ? "image/*,.glb,.fbx,.zip" : "image/*,.glb"}
                   style={{ display: "none" }}
                   onChange={(e) => {
                     const f = e.target.files?.[0];
                     if (f) importPhoto(f);
                     e.target.value = "";
                   }} />
          </label>
          {!capturing ? (
            <button className="chip" onClick={startCapture}>
              {tr("idn.deck.capture", lang)}
            </button>
          ) : (
            <button className="chip" onClick={finishCapture}
                    disabled={captured.length === 0}>
              {tr("idn.deck.capture.done", lang)}
            </button>
          )}
        </div>
        {capturing && (
          <div className="capture">
            <video ref={videoRef} autoPlay playsInline muted />
            <div className="row">
              {captureAngles.map((a) => (
                <button key={a} className="chip"
                        disabled={captured.length >= captureAngles.length}
                        onClick={() => snapAngle(a)}>
                  {tr(`idn.deck.angle.${a}`, lang)}
                </button>
              ))}
            </div>
            <p className="muted small">
              {fill(tr("idn.deck.frames", lang),
                    { n: captured.length, total: captureAngles.length })}
            </p>
          </div>
        )}

        {/* The deployment's default faces, first: most people pick, few
            import. One tap claims through the registry — the road a
            takedown can still travel. */}
        <h4>{tr("idn.deck.defaults", lang)}</h4>
        <p className="muted small">{tr("idn.deck.defaults.sub", lang)}</p>
        {getSignupKey() && (
          <button className="chip" onClick={async () => {
            setError(null); setNote(null);
            try {
              const got = await api.pullShelf();
              setNote(got.note === "provider_door_closed"
                ? tr("idn.deck.pull.closed", lang)
                : tr("idn.deck.done", lang));
              const r = await api.avatarShelf();
              setShelfRows(r.shelf);
            } catch (e) { fail(e); }
          }}>{tr("idn.deck.pull", lang)}</button>
        )}
        {shelfRows.length === 0 ? (
          <p className="muted small">{tr("idn.deck.defaults.none", lang)}</p>
        ) : (
          <div className="shelf-grid">
            {shelfRows.map((row) => (
              <button key={row.id} className="shelf-face"
                      title={row.label || row.provider}
                      aria-label={row.label || row.provider}
                      onClick={async () => {
                        setError(null); setNote(null);
                        try {
                          await api.claimFace(me, row.id, token);
                          setNote(tr("idn.deck.done", lang));
                          reloadAvatar();
                        } catch (e) { fail(e); }
                      }}>
                <img alt="" src={row.asset.startsWith("http")
                  ? row.asset : getBase() + row.asset} />
                {row.marked && (
                  <span className="shelf-mark" aria-hidden="true">✦</span>
                )}
              </button>
            ))}
          </div>
        )}

        {/* The three roads, one question above the framing choice.
            Framing — face, upper torso, full body — is about the
            photograph going IN. This is about which road the presence
            takes on the way out, and video is not a fourth way to crop a
            photo. Each surface already falls back down this list when
            the one above it is not there, so the picker names something
            true rather than inventing a hierarchy. */}
        <h4>{tr("idn.road", lang)}</h4>
        <p className="muted small">{tr("idn.road.sub", lang)}</p>
        <div className="roads">
          {/* Keys written out rather than built from the road name. A
              lookup assembled with a template literal is invisible to the
              extractor next door, which then reports six strings
              translated into ten languages and read by nobody — and it
              would be right, because it could not prove otherwise. */}
          {([
            ["photo", tr("idn.road.photo", lang), tr("idn.road.photo.sub", lang)],
            ["avatar", tr("idn.road.avatar", lang), tr("idn.road.avatar.sub", lang)],
            ["video", tr("idn.road.video", lang), tr("idn.road.video.sub", lang)],
          ] as const).map(([key, name, note]) => (
            <button key={key} type="button"
                    className={"road" + (road === key ? " lit" : "")}
                    aria-pressed={road === key}
                    onClick={() => void chooseRoad(key)}>
              <span className="road-name">{name}</span>
              <span className="road-note">{note}</span>
            </button>
          ))}
        </div>

        {/* What the pressed button opens, attached to it.
          *
          *     asked     when you press video generation or avatar it
          *               should pop up below the buttons, so we don't
          *               have to scroll even further past avatar
          *     mattered  it already WAS below them, and that was not the
          *               same thing as being findable
          *
          * The order was never wrong — roads, then the video block, then
          * the forge. But the block is long and the page is longer, so
          * pressing a road opened a panel below the fold: it "shows up
          * for a split second" as the layout grows and then the screen is
          * still showing the buttons, with the thing you asked for
          * somewhere underneath. Reported as the options going away.
          *
          * So the two panels share one drawer that is visibly the
          * button's own — its own ground, hairline and a notch pointing
          * back up at the row — and choosing a road scrolls it into
          * view. Nothing moved in the markup; what changed is that the
          * screen now takes you to what you pressed. */}
        {(road === "video" || (road === "avatar" && forge?.configured)) && (
        <div className="road-drawer" ref={drawer}>

        {/* The video road. Drawn whatever the deployment has chosen: with
            nothing configured it says WHICH of the three variables is
            missing, because "not configured" teaches an operator nothing
            and is how a door stays shut by accident rather than by
            decision. */}
        {road === "video" && (
          <>
            {/* The ceiling, first — above the service and above the
                passage, because it is the sentence that makes the rest of
                this block a safe thing to have pressed. Every reply is
                rendered once this road is taken; a limit offered after
                that is a limit offered after the bill. */}
            <h4>{tr("idn.road.cap", lang)}</h4>
            <p className="muted small">{tr("idn.road.cap.sub", lang)}</p>
            <div className="row">
              <input type="number" min={0} max={3600} value={capDraft}
                     aria-label={tr("idn.road.cap", lang)}
                     onChange={(e) => setCapDraft(e.target.value)} />
              <button className="chip" onClick={() => void setCeiling()}>
                {tr("idn.road.cap.set", lang)}
              </button>
            </div>
            {budget && (
              <p className="muted small">
                {fill(tr("idn.road.left", lang), {
                  left: String(budget.left),
                  cap: String(budget.daily_seconds),
                })}
              </p>
            )}
            <p className="muted small">{tr("idn.road.spent", lang)}</p>

            <h4>{tr("idn.video.service", lang)}</h4>
            <p className="muted small">{tr("idn.video.service.sub", lang)}</p>
            {/* The menu THIS profile's region is offered (the road's own
                answer), not the whole shelf the deployment can send to:
                a tile drawn here is a tile the set accepts. */}
            <SkinTiles
              sources={(budget?.providers || film?.providers || [])
                .map((k) => ({ key: k, name: k, how: "" }))}
              chosen={filmPick}
              onPick={(key) => void chooseFilmProvider(key)} />
            {!film?.configured && (
              <p className="muted small">{tr("idn.video.service.shut", lang)}</p>
            )}
            {/* The field question was "why is fal.ai not the default" —
                because it is the road, not a row: one aggregator serves
                every model on this shelf. Read from the adapter's own
                health, so the sentence is true of THIS deployment. */}
            {film?.served_through && (
              <p className="muted small">
                {fill(tr("idn.video.through", lang),
                      { host: film.served_through })}
              </p>
            )}

            {/* The standing direction, above the passage because it is
                the frame the passage sits inside — and because somebody
                who does not like what they saw looks here first. Shown
                as prose rather than as fields: the vocabulary of a shot
                is not a form, and "it's too dark" is not a dropdown. */}
            <h4>{tr("idn.scene.direction", lang)}</h4>
            <p className="muted small">
              {tr("idn.scene.direction.sub", lang)}
            </p>
            {direction !== "" && <p className="scene-direction">{direction}</p>}
            <div className="row">
              <input value={sceneAsk} style={{ flex: 1 }}
                     placeholder={tr("idn.scene.ask.ph", lang)}
                     aria-label={tr("idn.scene.ask", lang)}
                     onChange={(e) => setSceneAsk(e.target.value)} />
              <button disabled={directing || sceneAsk.trim() === ""}
                      onClick={() => void directScene()}>
                {tr("idn.scene.ask", lang)}
              </button>
              <button className="chip" onClick={() => void undirectScene()}>
                {tr("idn.scene.reset", lang)}
              </button>
            </div>

            {/* What was asked, in their own words. Folded away because
                it is a record rather than a control — but present,
                because a direction that only says where somebody ended
                up cannot tell them which request took them there. */}
            <details className="scene-log">
              <summary>{tr("idn.scene.log", lang)}</summary>
              {sceneLog.length === 0
                ? <p className="muted small">{tr("idn.scene.log.none", lang)}</p>
                : <ul>
                    {sceneLog.map((entry, at) => (
                      <li key={at}>
                        <span>{entry.asked || tr("idn.scene.log.reset", lang)}</span>
                        {entry.surface !== null && (
                          <em className="muted"> · {entry.surface}</em>
                        )}
                      </li>
                    ))}
                  </ul>}
            </details>

            <h4>{tr("idn.video.passage", lang)}</h4>
            <p className="muted small">{tr("idn.video.passage.sub", lang)}</p>
            <textarea rows={4} value={passage}
                      aria-label={tr("idn.video.passage", lang)}
                      onChange={(e) => setPassage(e.target.value)} />

            <h4>{tr("idn.video.shape", lang)}</h4>
            <div className="row">
              {["portrait", "landscape", "square"].map((shape) => (
                <button key={shape} type="button"
                        className={"chip" + (videoShape === shape ? " lit" : "")}
                        aria-pressed={videoShape === shape}
                        onClick={() => setVideoShape(shape)}>
                  {shape === "portrait" ? tr("idn.video.portrait", lang)
                   : shape === "landscape" ? tr("idn.video.landscape", lang)
                   : tr("idn.video.square", lang)}
                </button>
              ))}
            </div>

            {/* The number this screen SHOWS and never offers to change. */}
            {film && passage.trim() !== "" && (
              <VideoQuote text={passage} film={film} lang={lang} />
            )}

            {film?.configured
              ? <button className="primary"
                        disabled={filming || passage.trim() === ""}
                        onClick={() => void renderScene()}>
                  {tr("idn.video.go", lang)}
                </button>
              : <p className="muted small">{film?.why}</p>}

            <p className="muted small">{tr("idn.video.marked", lang)}</p>
          </>
        )}

        {/* The forge, above the import list on purpose: this is the road
            that MAKES a face, and the list below is for a face somebody
            already has somewhere else. It draws only where a forge is
            actually configured — a button that fails is worse than an
            absence, and worst of all at the moment somebody has just
            chosen a photograph of themselves. */}
        {road === "avatar" && forge?.configured && (
          <>
            <h4>{tr("idn.forge", lang)}</h4>
            <p className="muted small">{tr("idn.forge.sub", lang)}</p>
            <div className="row">
              <select value={shot} aria-label={tr("idn.forge.shot", lang)}
                      onChange={(e) => setShot(e.target.value)}>
                <option value="face">{tr("idn.forge.face", lang)}</option>
                <option value="upper">{tr("idn.forge.upper", lang)}</option>
                <option value="full">{tr("idn.forge.full", lang)}</option>
              </select>
              <input type="file" accept="image/*" disabled={forging}
                     aria-label={tr("idn.forge.pick", lang)}
                     onChange={(e) => void forgeFrom(e.target.files?.[0])} />
            </div>
            <p className="muted small">
              {forging ? tr("idn.forge.working", lang)
                       : tr("idn.forge.where", lang)}
            </p>
            {/* The head, second and labelled. See `headFrom`. */}
            <details className="idn-head">
              <summary>{tr("idn.head", lang)}</summary>
              <p className="muted small">{tr("idn.head.sub", lang)}</p>
              <input type="file" accept="image/*" disabled={forging}
                     aria-label={tr("idn.head.pick", lang)}
                     onChange={(e) => void headFrom(e.target.files?.[0])} />
            </details>
          </>
        )}

        </div>
        )}

        <h4>{tr("idn.deck.market", lang)}</h4>
        <p className="muted small">{tr("idn.deck.market.sub", lang)}</p>
        {/* Tiles, not a dropdown. This component was written for exactly
            this spot — its own note says the old shape was "a dropdown
            next to a URL box — which is a form, not a picker" — and then
            nothing mounted it, so the form is what shipped. A person
            choosing where their face comes from should see the places,
            not read a list. */}
        <SkinTiles sources={market} chosen={marketKey}
                   onPick={setMarketKey} />
        <div className="row">
          <input value={marketUrl} placeholder={tr("idn.deck.url.ph", lang)}
                 onChange={(e) => setMarketUrl(e.target.value)}
                 style={{ flex: 1 }} />
          {/* Optional: the same avatar's upper-torso export, for surfaces
              that stand the figure in a scene at 1:1. */}
          <input value={marketTorso}
                 placeholder={tr("idn.deck.torso.ph", lang)}
                 onChange={(e) => setMarketTorso(e.target.value)}
                 style={{ flex: 1 }} />
          <input value={marketPid}
                 placeholder={tr("idn.deck.pid.ph", lang)}
                 aria-label={tr("idn.deck.pid.ph", lang)}
                 onChange={(e) => setMarketPid(e.target.value)}
                 style={{ flex: 1 }} />
          <button disabled={!marketUrl.trim()} onClick={importMarket}>
            {tr("idn.deck.import", lang)}
          </button>
        </div>
        {market.find((m) => m.key === marketKey) && (
          <p className="muted small">
            {market.find((m) => m.key === marketKey)!.how}
          </p>
        )}

        {briefs.length > 0 && (
          <>
            <h4>{tr("idn.bubble.portrait", lang)}</h4>
            <p className="muted small">{tr("idn.bubble.brief", lang)}</p>
            {briefs.slice(0, 3).map((b) => (
              <div key={b.handle}>
                <div className="row">
                  <div style={{ flex: 1 }}>
                    <strong>{b.handle}</strong>
                    <div className="muted small">{b.portrait}</div>
                  </div>
                  <button onClick={async () => {
                    setError(null);
                    if (promptFor === b.handle) { setPromptFor(null); return; }
                    try {
                      const full = await api.avatarBrief(b.handle);
                      // Right here, under the button that asked — this used
                      // to land in the note at the top of the screen, which
                      // on a phone is above the fold: "I gotta show the
                      // prompt and nothing happens."
                      setPromptFor(b.handle);
                      setPromptText(full.prompt || full.portrait);
                    } catch (e) { fail(e); }
                  }}>{tr("idn.bubble.prompt", lang)}</button>
                </div>
                {promptFor === b.handle && (
                  <p className="muted small">{promptText}</p>
                )}
              </div>
            ))}
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("idn.rename", lang)}</h3>
        <div className="row">
          <input value={name} onChange={(e) => setName(e.target.value)}
                 placeholder={tr("idn.rename.ph", lang)} style={{ flex: 1 }} />
          <button disabled={!name.trim()} onClick={async () => {
            setError(null); setNote(null);
            try {
              await api.editProfile(me, { display_name: name.trim() }, token);
              setNote("Renamed."); setName(""); reload();
            } catch (e) { fail(e); }
          }}>{tr("idn.rename.save", lang)}</button>
        </div>
      </div>

      {/* What kind of thing this profile is.
       *
       *     asked     can an owner correct what their profile is
       *     mattered  or is a creation-time default permanent
       *
       * It was permanent. `kind` had no update site anywhere, defaults to
       * "fictional", and decides `likeness().real_person` — so a digital
       * twin made outside the onboarding flow was recorded forever as an
       * invented character whose portrait depicts nobody, and every
       * surface reading that record refused to draw it as a face.
       *
       * "Somebody else, with their say-so" is offered but sends the
       * caller to the consent record it requires, because a rights claim
       * about a real third party is not a dropdown. Rated profiles of
       * another real person are refused outright at the door, whatever
       * this picker sends. */}
      <div className="card">
        <h3>{tr("idn.kind", lang)}</h3>
        <p className="muted small">{tr("idn.kind.lead", lang)}</p>
        <select value={kind} disabled={!token}
                onChange={async (e) => {
                  const want = e.target.value;
                  setKind(want);
                  setError(null); setNote(null);
                  try {
                    await api.editProfile(me, { kind: want }, token);
                    setNote(tr("idn.kind.saved", lang));
                    reload();
                  } catch (err) { fail(err); }
                }}>
          <option value="self">{tr("idn.kind.self", lang)}</option>
          <option value="fictional">{tr("idn.kind.fictional", lang)}</option>
          <option value="other_person">
            {tr("idn.kind.other", lang)}
          </option>
        </select>
      </div>

      {/* Adult mode: shown, and shut.
       *
       *     asked     can an owner see what this profile is set to
       *     mattered  can they change it here
       *
       * Seen and not settable, which is a deliberate pair rather than an
       * unfinished one. Every guard on this flag lives in
       * `create_profile`: a verified adult owner, never a rated persona of
       * another real person (the hard line
       * `test_a_real_likeness_can_never_be_rated` holds), and a plan that
       * can hold rated content. A field on PATCH would be a way around all
       * three, so there is no field — and `tests/profile_columns_doorless.txt`
       * records that with its reason.
       *
       * Hiding the state as well as the switch would be the worse version:
       * somebody who cannot tell what their own profile is set to cannot
       * check it, and a setting nobody can see is a setting nobody can
       * audit. So the state is on screen and the control is not. */}
      {/* A person's own picture, reachable without being in a room.
       *
       *     asked     can a person put a face on themselves
       *     mattered  do they have to be in a room to do it
       *
       * They did. The upload lived only in the room seat's controls, so
       * setting your own face meant joining something first — and the
       * read door existed with nothing calling it, which is how a binding
       * ends up unused: the surface it was built for was never drawn. */}
      {iAm && myToken && (
        <div className="card">
          <h3>{tr("idn.mypic", lang)}</h3>
          <p className="muted small">{tr("idn.mypic.lead", lang)}</p>
          {myPic && (
            <img className="idn-mypic" alt={tr("idn.mypic", lang)}
                 src={myPic.startsWith("http") ? myPic : getBase() + myPic} />
          )}
          <div className="row">
            <button onClick={() => myPicker.current?.click()}>
              {myPic ? tr("idn.mypic.replace", lang)
                     : tr("idn.mypic.add", lang)}
            </button>
            {myPic && (
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  await api.clearOwnPicture(iAm, myToken);
                  setMyPic(null);
                  setNote(tr("idn.mypic.gone", lang));
                } catch (e) { fail(e); }
              }}>{tr("idn.mypic.remove", lang)}</button>
            )}
          </div>
          <input ref={myPicker} type="file" accept="image/*"
                 style={{ display: "none" }}
                 onChange={async (e) => {
                   const file = e.target.files?.[0];
                   e.target.value = "";
                   if (!file) return;
                   setError(null); setNote(null);
                   try {
                     const r = await api.setOwnPicture(iAm, file, myToken);
                     setMyPic(r.url);
                     setNote(tr("idn.mypic.saved", lang));
                   } catch (err) { fail(err); }
                 }} />
        </div>
      )}

      {/* The people in your phone — QRME's half of the estate's address
          book (qrme/contacts.py). A synced source, never typed; names
          come back and the numbers never do. */}
      {iAm && myToken && (
        <div className="card">
          <h3>{tr("idn.book", lang)}</h3>
          <p className="muted small">{tr("idn.book.lead", lang)}</p>
          {bookError && <p className="muted small">{bookError}</p>}
          {book && (
            <p className="muted small">
              {fill(tr("idn.book.held", lang),
                    { n: String(book.held) })}
            </p>
          )}
          {book && book.book.slice(0, 30).map((c) => (
            <div className="row" key={c.id}>
              <span style={{ flex: 1 }}>{c.name}</span>
              {c.holds_account && (
                <span className="muted small">
                  {tr("idn.book.account", lang)}
                </span>
              )}
            </div>
          ))}
          {book && book.book.length > 30 && (
            <p className="muted small">
              {fill(tr("idn.book.more", lang),
                    { n: String(book.book.length - 30) })}
            </p>
          )}
          <div className="row">
            <button onClick={() => void syncBook()}>
              {tr("idn.book.sync", lang)}
            </button>
            {book && (
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  await api.decideContacts(iAm, false, myToken);
                  reloadBook();
                } catch (e) { fail(e); }
              }}>{tr("idn.book.withdraw", lang)}</button>
            )}
          </div>
        </div>
      )}

      {/* Hosted storage and contribution are one bargain, said here rather
        * than buried. On for the free tier because it is what the tier is;
        * off is one press, and the press reaches backwards. Nothing sealed
        * in a vault is ever contributed whatever this says. */}
      {iAm && myToken && giving && (
        <div className="card">
          <h3>{tr("idn.give", lang)}</h3>
          <p className="muted small">{tr("idn.give.lead", lang)}</p>
          <p className="small">
            {giving.contributes
              ? fill(tr("idn.give.on", lang),
                     { count: String(giving.contributed_count) })
              : tr("idn.give.off", lang)}
          </p>
          {giving.contributes && (
            <div className="row">
              <button onClick={async () => {
                setError(null); setNote(null);
                try {
                  const out = await api.stopOwnContribution(iAm, myToken);
                  setGiving({ contributes: false, contributed_count: 0 });
                  // `.replace` rather than `fill`: fill returns ReactNode[]
                  // for interpolating into JSX, and a note is a string.
                  setNote(out.deleted_at_gateway
                    ? tr("idn.give.stopped", lang)
                        .replace("{count}", String(out.revoked_count))
                    : tr("idn.give.stopped.partly", lang));
                } catch (e) { fail(e); }
              }}>{tr("idn.give.stop", lang)}</button>
            </div>
          )}
        </div>
      )}

      {/* What you hold, not what a profile holds about you.
        *
        * A memory is what YOU said — only a person's own turns are ever
        * sealed — and it lives in your vault, on your plan. Deleting a
        * profile no longer takes it, which left this missing: the only
        * way to read a memory back began by looking the profile up, so a
        * record that outlived the profile had no door at all. Keeping
        * somebody's words where they cannot reach them is the opposite
        * of the promise. */}
      {iAm && myToken && (
        <div className="card">
          <h3>{tr("idn.mymem", lang)}</h3>
          <p className="muted small">{tr("idn.mymem.lead", lang)}</p>
          <div className="row">
            <button onClick={async () => {
              setError(null); setNote(null);
              try { setMine(await api.ownMemories(iAm, myToken)); }
              catch (e) { fail(e); }
            }}>{tr("idn.mymem.show", lang)}</button>
          </div>
          {mine && mine.conversations.length === 0 && (
            <p className="muted small">{tr("idn.mymem.none", lang)}</p>
          )}
          {mine && !mine.readable && (
            <p className="muted small">{tr("idn.mymem.unreadable", lang)}</p>
          )}
          {mine?.conversations.map((c) => (
            <div key={c.profile_id} className="idn-mymem-talk">
              <h4>
                {c.display_name || c.profile_id}
                {c.gone && (
                  <span className="muted small"> — {tr("idn.mymem.gone", lang)}</span>
                )}
              </h4>
              {c.memories.map((m) => (
                <p key={m.ref} className="small">{m.line || "—"}</p>
              ))}
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h3>{tr("idn.rated", lang)}</h3>
        <p className="muted small">
          {rated === null ? tr("idn.rated.unknown", lang)
                          : rated ? tr("idn.rated.on", lang)
                                  : tr("idn.rated.off", lang)}
        </p>
        <label className="muted small">
          <input type="checkbox" checked={!!rated} disabled readOnly />
          {" "}{tr("idn.rated.shut", lang)}
        </label>
        <p className="muted small">{tr("idn.rated.why", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("idn.export", lang)}</h3>
        <p className="muted small">{tr("idn.export.pitch", lang)}</p>
        <div className="row">
          <button onClick={async () => {
            setError(null); setNote(null);
            try {
              const data = await api.exportProfile(me, token);
              setNote(`Exported: ${Object.keys(data).join(", ")}.`);
            } catch (e) { fail(e); }
          }}>{tr("idn.export.go", lang)}</button>
          {/* The QR door a field report pointed at this card and asked
              for. The code carries a single-use, minutes-long ticket —
              the owner token never leaves this screen. */}
          <button onClick={async () => {
            setError(null); setNote(null); setExportQr(null);
            try {
              setExportQr(await api.exportTicket(me, token));
            } catch (e) { fail(e); }
          }}>{tr("idn.export.qr", lang)}</button>
        </div>
        {exportQr && (
          <>
            <img src={getBase() + `/profiles/${me}/export/handoff/${exportQr.ticket}/qr.svg`}
                 alt={tr("idn.export.qr", lang)}
                 style={{ width: 220, height: 220, borderRadius: 12 }} />
            <p className="muted small">{exportQr.note}</p>
          </>
        )}
        {/* The redeeming side, for a link pasted from a scan on this
            device. Tokenless — the single-use ticket is the authority. */}
        <div className="row">
          <input value={handoffLink} placeholder={tr("idn.export.redeem.ph", lang)}
                 onChange={(e) => setHandoffLink(e.target.value)}
                 style={{ flex: 1 }} />
          <button disabled={!handoffLink.includes("/export/handoff/")}
                  onClick={async () => {
            setError(null); setNote(null);
            try {
              const m = handoffLink.match(
                /\/profiles\/([^/]+)\/export\/handoff\/([^/?#]+)/);
              if (!m) return;
              const data = await api.exportHandoff(m[1], m[2]);
              setNote(`Exported: ${Object.keys(data).join(", ")}.`);
              setHandoffLink("");
            } catch (e) { fail(e); }
          }}>{tr("idn.export.redeem", lang)}</button>
        </div>
      </div>

      {memorial && (
        <div className="card">
          <h3>{tr("idn.mem", lang)}</h3>
          <p className="small">{memorial.note}</p>
          <p className="muted small">
            {fill(tr("idn.mem.line", lang), {
              status: memorial.status, n: memorial.relationships_touched,
              s: memorial.relationships_touched === 1 ? "" : "s",
            })}
          </p>
        </div>
      )}

      <div className="card">
        <h3>{tr("idn.end", lang)}</h3>
        <p className="muted small">{tr("idn.end.pitch", lang)}</p>

        <div className="row">
          <div style={{ flex: 1 }}>
            <strong>{tr("idn.end.retire", lang)}</strong>
            <div className="muted small">
              {tr("idn.end.retire.note", lang)}
            </div>
          </div>
          {confirmEnd === "sunset" ? (
            <button onClick={async () => {
              setError(null); setNote(null); setConfirmEnd("");
              try {
                setEnded(await api.sunsetProfile(me, token));
                reload();
              } catch (e) { fail(e); }
            }}>{tr("idn.end.retire.yes", lang)}</button>
          ) : (
            <button onClick={() => setConfirmEnd("sunset")}>{tr("idn.end.retire", lang)}</button>
          )}
        </div>
        {ended && (
          <p className="small">
            {fill(tr("idn.end.sunset.line", lang), {
              status: ended.status, n: ended.farewells,
              s: ended.farewells === 1 ? "" : "s", memory: ended.memory,
            })}
          </p>
        )}

        <div className="row">
          <div style={{ flex: 1 }}>
            <strong>{tr("idn.end.delete", lang)}</strong>
            <div className="muted small">
              {tr("idn.end.delete.note", lang)}
            </div>
          </div>
          {confirmEnd === "delete" ? (
            <button onClick={async () => {
              setError(null); setNote(null); setConfirmEnd("");
              try {
                setGone(await api.deleteProfile(me, token));
              } catch (e) { fail(e); }
            }}>{tr("idn.end.delete.yes", lang)}</button>
          ) : (
            <button onClick={() => setConfirmEnd("delete")}>{tr("idn.end.delete", lang)}</button>
          )}
        </div>
        {/* The receipt, itemised. "Deleted" is a claim; these are evidence,
            and the row that reads `profile: 1` is the one that matters. */}
        {gone && (
          <>
            <h4>{tr("idn.end.erased", lang)}</h4>
            <ul className="small">
              {Object.entries(gone.deleted)
                .filter(([, n]) => n > 0)
                .map(([table, n]) => <li key={table}>{table}: {n}</li>)}
            </ul>
            <p className="muted small">
              {fill(tr("idn.end.zeros", lang), {
                n: Object.values(gone.deleted).filter((n) => n === 0).length,
              })}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
