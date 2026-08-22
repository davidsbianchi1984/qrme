import { useEffect, useState, type ReactNode } from "react";
import { api, getBase, type ChatMessage, type Homepage,
         type MediaUpload,
         type PageFriend, type Profile as ProfileRow, type ProfilePage,
         type WallPost } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Briefcase } from "../Briefcase";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// Somebody else's homepage — the place you land when you press their face.
//
// What was there before was a card on Home: their name, their tagline, a
// Close button, and underneath it the signed-in profile's own memory count,
// engagement average and moderation rate. Four different friends produced
// four identical screens, because only the header was ever theirs.
//
//     asked     does pressing a face open something
//     mattered  is what opens theirs
//
// This screen carries no stats row at all, and that is not an omission:
// `GET /profiles/{id}/stats` is `require_owner`. Somebody else's numbers are
// not readable and should not be — which is exactly why the old card, having
// no way to fetch theirs, showed yours under their name.
//
// Everything here is a public route. The page, the homepage sandbox, the
// wall, the friends and the uploads are all visitor-readable by design: this
// is what a visitor came to look at. The actions are the ones a visitor may
// actually take — say something to their profile, send them a message, open
// a room with them, and hand them something to read — and each is signed as
// the person pressing it.
//
// The briefcase is the fourth of those and the odd one: what you hand over
// belongs to the two of you, not to the page. It is drawn inside the same
// card as the composer because handing somebody a document is part of
// talking to them, not a separate errand.
//
// In QRME a friend *is* a profile, so a synthetic profile has this same
// homepage: one screen, not two.

type Pane = "wall" | "photos" | "videos" | "friends";

export function Profile({ profileId, onBack, onPlans, onVisit, onInside }: {
  /** Whose page this is. Changing it reloads everything — that is how the
   *  Top 8 keeps walking without unmounting the screen. */
  profileId: string;
  onBack: () => void;
  /** Where a plan refusal sends somebody, threaded from the shell. */
  onPlans: () => void;
  /** Press a face in *their* Top 8 and land on that page instead. */
  onVisit: (id: string) => void;
  /** A room opened from here is a room you are then standing in. */
  onInside: (roomId: string) => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [who, setWho] = useState<ProfileRow | null>(null);
  const [page, setPage] = useState<ProfilePage | null>(null);
  const [home, setHome] = useState<Homepage | null>(null);
  const [posts, setPosts] = useState<WallPost[]>([]);
  const [friends, setFriends] = useState<PageFriend[]>([]);
  const [media, setMedia] = useState<MediaUpload[]>([]);
  // Your own list, so the screen can tell which of three states this is.
  // `social.send_message` refuses between strangers — "messages travel
  // between friends; befriend them first" — and `_are_friends` is *mutual*
  // on purpose: "consent that only one person can end is not consent". So a
  // Message button drawn on a stranger's page always fails, and one drawn
  // the moment *you* add *them* still fails, which is the worse of the two
  // because it looks like it should have worked.
  //
  //     asked     are they on your friends list
  //     mattered  are you on theirs
  //
  // Adding them is a real act either way — it lists them, and `friends.
  // befriend` drops a note in their inbox — so it is offered as itself
  // rather than as a promise about the button beside it.
  const [befriended, setBefriended] = useState<string[]>([]);
  const [pane, setPane] = useState<Pane>("wall");
  const [said, setSaid] = useState("");
  const [reply, setReply] = useState<ChatMessage | null>(null);
  const [note, setNote] = useState<ReactNode>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);

  const mine = profileId === session.profileId;

  useEffect(() => {
    setWho(null); setPage(null); setHome(null); setPosts([]); setFriends([]);
    setMedia([]); setPane("wall"); setReply(null); setNote(null);
    setError(null);
    // Their name, from the public profile row. The page carries no name and
    // the homepage carries one — but a homepage kept private answers 404, and
    // a visitor should not be handed a raw `prf_…` id as somebody's heading
    // because they chose not to publish a sandbox.
    api.getProfile(profileId).then(setWho).catch(() => setWho(null));
    api.page(profileId).then(setPage).catch(setError);
    // A homepage kept private answers 404. That is a choice, not an error,
    // so it degrades to the decorated page rather than to a broken screen.
    api.homepage(profileId).then(setHome).catch(() => setHome(null));
    api.myWall(profileId).then((r) => setPosts(r.posts)).catch(() => setPosts([]));
    api.friends(profileId).then((r) => setFriends(r.friends))
      .catch(() => setFriends([]));
    api.profileMedia(profileId).then((r) => setMedia(r.media))
      .catch(() => setMedia([]));
    if (session.profileId) {
      api.friends(session.profileId)
        .then((r) => setBefriended(r.friends.map((f) => f.profile_id)))
        .catch(() => setBefriended([]));
    }
  }, [profileId, session.profileId, session.interactorId]);

  // Their Top 8 as they arranged it; their friends list is the fallback, so
  // a page whose owner never picked eight is still somewhere you can walk on
  // from rather than a dead end.
  const top: PageFriend[] = (page?.top_friends?.length ? page.top_friends
                                                       : friends).slice(0, 8);
  const photos = media.filter((m) => m.kind === "image");
  const videos = media.filter((m) => m.kind === "video");
  const name = who?.display_name || home?.display_name || profileId;
  const listedThem = befriended.includes(profileId);
  const listedYou = friends.some((f) => f.profile_id === session.profileId);
  const mutual = listedThem && listedYou;
  const accent = page?.accent || home?.theme?.accent || undefined;

  async function talk() {
    if (!session.interactorId || !said.trim()) return;
    setBusy(true); setError(null);
    try {
      const answer = await api.chat(profileId,
        { interactor_id: session.interactorId, message: said.trim() });
      setReply(answer.profile_message);
      setSaid("");
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  async function message() {
    if (!session.profileId || !session.ownerToken || !said.trim()) return;
    setBusy(true); setError(null);
    try {
      await api.sendDm(session.profileId, profileId, said.trim(),
                       session.ownerToken);
      setSaid(""); setNote(tr("prf.sent", lang));
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  /** Add them to this profile's list.
   *
   *  The guard used to be a bare `return`: no request, no error, no note.
   *  Pressed without a profile of your own — which is every visitor, and
   *  anybody signed in as a person rather than as one of their profiles —
   *  the button did nothing and said nothing, and the field report was the
   *  only way anyone found out. Discover's identical guard has always said
   *  which; this one learned it late.
   *
   *      asked     did the friendship get added
   *      mattered  does anyone find out either way
   *
   *  And a 200 is not a yes: adding somebody already on the list answers
   *  `added: false` on purpose. That answer was being dropped too. */
  async function befriend() {
    if (!session.profileId || !session.ownerToken) {
      setNote(tr("prf.needprofile", lang)); return;
    }
    setBusy(true); setError(null); setNote(null);
    try {
      const said = await api.addFriend(
        session.profileId, profileId, session.ownerToken);
      setBefriended((ids) => [...ids, profileId]);
      // Each key inside its own `tr(`, not chosen inside the call. A key
      // picked by a ternary in the argument is invisible to the lookup
      // scanner, which then reads it as translated-and-never-used — and the
      // check is right to say so: it cannot tell that case apart from a
      // string nobody renders, which is the English still being read.
      setNote(fill(said.added ? tr("prf.befriended", lang)
                              : tr("prf.alreadyfriend", lang), { name }));
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  async function openRoom() {
    if (!session.interactorId) { setNote(tr("prf.needuser", lang)); return; }
    setBusy(true); setError(null);
    try {
      // You as a person, them as a profile — the two-participant shape the
      // backend requires, with the second one actually being them.
      const room = await api.createRoom({
        channel: "chat",
        participants: [
          { kind: "user", id: session.interactorId },
          { kind: "profile", id: profileId },
        ],
      });
      onInside(room.id);
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  const face = (f: PageFriend) => (
    <button key={f.profile_id} className="pp-face"
            onClick={() => onVisit(f.profile_id)}>
      {f.avatar ? (
        <img className="presence-bubble" alt=""
             src={f.avatar.startsWith("http") ? f.avatar
                                              : getBase() + f.avatar} />
      ) : null}
      <span className="presence-name">{f.display_name}</span>
    </button>
  );

  return (
    <div className="screen profile-page">
      <header className="screen-head">
        <button className="ghost" onClick={onBack}>{tr("prf.back", lang)}</button>
        <h2>{name}</h2>
        <span className="muted small">{tr("prf.theirs", lang)}</span>
      </header>

      <Refusal error={error} onPlans={onPlans} variant="inline" />
      {note && <p className="muted small">{note}</p>}

      {/* The page as they decorated it. The accent is theirs, the markup was
          sanitised in storage rather than here — a renderer never sees raw
          markup, so no renderer can forget to clean it. */}
      <div className="card pp-hero"
           style={{ borderColor: accent, background: page?.theme?.bg }}>
        <h3 style={{ color: accent }}>
          {home?.headline || page?.tagline || name}
        </h3>
        {page?.tagline && home?.headline && (
          <p className="muted small">{page.tagline}</p>
        )}
        {(home?.about || page?.about) && (
          <p className="small">{home?.about || page?.about}</p>
        )}
        {(page?.links?.length ?? 0) > 0 && (
          <p className="muted small">
            {page!.links.map((l) => (
              <a key={l.url} href={l.url} target="_blank" rel="noreferrer"
                 style={{ marginRight: 10 }}>{l.label || l.url}</a>
            ))}
          </p>
        )}
        {/* Their own markup — the MySpace half of the promise, and the one
            piece of this screen no client had ever rendered.

            In its own browsing context with `sandbox` empty, which switches
            every capability off: no scripts, no forms, no navigation, no
            same-origin. `pages.py` sanitises on the way *in* and does it
            well; this is not a second opinion about that, it is about who
            pays if it is ever wrong. Interpolating it into this document
            would put a stranger's stored markup inside the console's own
            origin, beside the session — and the console has never trusted
            the sanitiser that far. React's escape hatch is a floor at zero
            in this repo for exactly that reason, and being the screen that
            finally wanted it is not a reason to move the floor. */}
        {page?.html && (
          <iframe className="pp-markup" title={tr("prf.theirmarkup", lang)}
                  sandbox="" referrerPolicy="no-referrer"
                  srcDoc={page.html} />
        )}
        {page && !page.customised && (
          <p className="muted small">
            {fill(tr("prf.plain", lang), { name })}
          </p>
        )}
      </div>

      {/* What a visitor may actually do. Nothing here is owner-gated, and
          nothing here reads their record — each action is signed as the
          person pressing it. */}
      {!mine && (
        <div className="card pp-actions">
          <label className="muted small" htmlFor="pp-say">
            {fill(tr("prf.saylabel", lang), { name })}
          </label>
          {/* Enter sends, Shift+Enter breaks the line. The field was a
              textarea with no key handler, so the only way out of it was the
              button — and the button said "Talk to their profile", which is
              a description of the screen rather than a name for the act.
              Both halves of that are the same fix: make the obvious gesture
              work, and name the control after what it does. */}
          <textarea id="pp-say" rows={2} value={said}
                    placeholder={tr("prf.sayhint", lang)}
                    onChange={(e) => setSaid(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        if (!busy && said.trim()) void talk();
                      }
                    }} />
          <div className="pp-buttons">
            <button disabled={busy || !said.trim()} onClick={talk}>
              {tr("prf.talk", lang)}
            </button>
            {mutual ? (
              <button disabled={busy || !said.trim()} onClick={message}>
                {tr("prf.message", lang)}
              </button>
            ) : listedThem ? null : (
              <button disabled={busy} onClick={befriend}>
                {tr("prf.befriend", lang)}
              </button>
            )}
            <button disabled={busy} onClick={openRoom}>
              {tr("prf.room", lang)}
            </button>
          </div>
          <p className="muted small">
            {mutual ? tr("prf.actionsnote", lang)
              : listedThem ? fill(tr("prf.waiting", lang), { name })
                : tr("prf.notyetfriends", lang)}
          </p>
          {reply && <p className="small pp-reply">{reply.content}</p>}

          {/* The briefcase, which is the same component the own-profile
              conversation uses. It shipped here and only here, so a person
              could hand a document to a starter they had just met and not to
              the profile built from their own life. One component, two call
              sites — a second copy would have closed today's gap and set up
              tomorrow's. */}
          {session.interactorId && (
            <Briefcase profileId={profileId}
                       interactorId={session.interactorId}
                       name={name} onError={setError} />
          )}
        </div>
      )}

      {top.length > 0 && (
        <div className="top-friends">
          <div className="tile-label">
            {fill(tr("prf.topfriends", lang), { n: String(top.length) })}
          </div>
          <div className="friends-row">{top.map(face)}</div>
        </div>
      )}

      <div className="pp-panes">
        <button className={"chip" + (pane === "wall" ? " on" : "")}
                onClick={() => setPane("wall")}>
          {fill(tr("prf.pane.wall", lang), { n: String(posts.length) })}
        </button>
        <button className={"chip" + (pane === "photos" ? " on" : "")}
                onClick={() => setPane("photos")}>
          {fill(tr("prf.pane.photos", lang), { n: String(photos.length) })}
        </button>
        <button className={"chip" + (pane === "videos" ? " on" : "")}
                onClick={() => setPane("videos")}>
          {fill(tr("prf.pane.videos", lang), { n: String(videos.length) })}
        </button>
        <button className={"chip" + (pane === "friends" ? " on" : "")}
                onClick={() => setPane("friends")}>
          {fill(tr("prf.pane.friends", lang), { n: String(friends.length) })}
        </button>
      </div>

      {pane === "wall" && (posts.length === 0
        ? <p className="muted small">{fill(tr("prf.nowall", lang), { name })}</p>
        : posts.map((p) => (
            <div key={p.id} className="card wall-post">
              <p className="wp-body">{p.body}</p>
              {(p.media || []).length > 0 && (
                <div className="wp-media">
                  {(p.media || []).map((m) => m.kind === "image"
                    ? <img key={m.id} src={getBase() + m.url}
                           alt={m.alt || ""} />
                    : m.kind === "video"
                      ? <video key={m.id} src={getBase() + m.url} controls />
                      : null)}
                </div>
              )}
              {p.created_at && (
                <div className="muted small">{p.created_at.slice(0, 10)}</div>
              )}
            </div>
          )))}

      {pane === "photos" && (photos.length === 0
        ? <p className="muted small">{tr("prf.nophotos", lang)}</p>
        : <div className="pp-gallery">
            {photos.map((m) => (
              <img key={m.id} src={getBase() + m.url} alt={m.alt || ""} />
            ))}
          </div>)}

      {pane === "videos" && (videos.length === 0
        ? <p className="muted small">{tr("prf.novideos", lang)}</p>
        : <div className="pp-gallery">
            {videos.map((m) => (
              <video key={m.id} src={getBase() + m.url} controls />
            ))}
          </div>)}

      {pane === "friends" && (friends.length === 0
        ? <p className="muted small">{tr("prf.nofriends", lang)}</p>
        : <div className="friends-row wrap">{friends.map(face)}</div>)}

      {(page?.offers?.length ?? 0) > 0 && (
        <div className="card">
          <div className="tile-label">{tr("prf.offers", lang)}</div>
          {page!.offers.map((o) => (
            <p key={o.id} className="small">
              <b>{o.title}</b>
              {o.blurb && <span className="muted"> — {o.blurb}</span>}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
