import { useEffect, useState } from "react";
import { api, getBase, type WallComment, type WallPost } from "../api";
import { useSession } from "../store";

// The community wall — the For You feed, in the console at last. The
// backend has carried posts, likes, comments, shares and shared-video
// links since the community round; the desktop just never got the door,
// which read in the field as the features not existing.
//
// Shared videos honor the facade contract (qrme/embeds.py): the card is
// drawn from stored fields only, and no request reaches the other
// platform until the viewer presses play — at which point the embed
// iframe loads and the card says whose player it is.
export function Wall() {
  const { session } = useSession();
  const [posts, setPosts] = useState<WallPost[]>([]);
  const [mine, setMine] = useState<WallPost[]>([]);
  const [platforms, setPlatforms] = useState<string>("");
  const [body, setBody] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [videoTitle, setVideoTitle] = useState("");
  const [playing, setPlaying] = useState<string | null>(null);   // post id
  const [liked, setLiked] = useState<Set<string>>(new Set());
  const [openComments, setOpenComments] = useState<string | null>(null);
  const [comments, setComments] = useState<WallComment[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    if (!session.profileId) return;
    api.feed(session.profileId).then((r) => setPosts(r.posts))
      .catch((e) => setError((e as Error).message));
    // The For You feed deliberately excludes your own posts, so without
    // this section a solo owner posts into apparent silence.
    api.myWall(session.profileId).then((r) => setMine(r.posts)).catch(() => {});
  }
  useEffect(() => {
    load();
    api.videoPlatforms()
      .then((r) => setPlatforms(r.platforms.map((p) => p.name).join(", ")))
      .catch(() => {});
  }, [session.profileId]);

  async function publish() {
    if (!session.profileId || !session.ownerToken) return;
    setBusy(true); setError(null); setNote(null);
    try {
      const post = await api.publishPost(session.profileId, {
        body: body.trim(),
        video_url: videoUrl.trim() || undefined,
        video_title: videoTitle.trim() || undefined,
      }, session.ownerToken);
      if (post.status === "blocked") {
        setError(`Moderation held this post: ${post.blocked_reason}`);
      } else {
        setBody(""); setVideoUrl(""); setVideoTitle("");
        setNote("Posted to your wall.");
        load();
      }
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function toggleLike(p: WallPost) {
    if (!session.ownerToken) return;
    const isLiked = liked.has(p.id);
    try {
      if (isLiked) await api.unlikePost(p.id, session.ownerToken);
      else await api.likePost(p.id, session.ownerToken);
      setLiked((cur) => {
        const next = new Set(cur);
        if (isLiked) next.delete(p.id); else next.add(p.id);
        return next;
      });
      setPosts((cur) => cur.map((x) => x.id === p.id
        ? { ...x, likes: (x.likes || 0) + (isLiked ? -1 : 1) } : x));
    } catch (e) { setError((e as Error).message); }
  }

  async function showComments(postId: string) {
    if (openComments === postId) { setOpenComments(null); return; }
    setOpenComments(postId); setComments([]);
    try {
      const r = await api.postComments(postId);
      setComments(Array.isArray(r) ? r : r.comments || []);
    } catch (e) { setError((e as Error).message); }
  }

  async function sendComment(postId: string) {
    if (!session.ownerToken || !draft.trim()) return;
    try {
      await api.addComment(postId, draft.trim(), session.ownerToken);
      setDraft("");
      const r = await api.postComments(postId);
      setComments(Array.isArray(r) ? r : r.comments || []);
    } catch (e) { setError((e as Error).message); }
  }

  async function share(postId: string) {
    if (!session.ownerToken) return;
    try { await api.sharePost(postId, session.ownerToken); setNote("Shared."); }
    catch (e) { setError((e as Error).message); }
  }

  const renderPost = (p: WallPost) => (
    <div key={p.id} className="card wall-post">
      <div className="wp-head">
        {p.avatar
      ? <img className="wp-avatar" src={getBase() + p.avatar} alt="" />
      : <span className="wp-avatar wp-initials">
          {(p.display_name || "Y").split(/\s+/).map((w) => w[0]).join("").slice(0, 2)}
        </span>}
        <div>
      <b>{p.display_name || (p.profile_id === session.profileId ? "You" : "someone")}</b>
      {p.reason && <div className="wp-reason">{p.reason}</div>}
        </div>
      </div>
      <p className="wp-body">{p.body}</p>

      {p.video && (
        <div className="wp-video">
      {playing === p.id ? (
        <iframe src={p.video.embed_url} title={p.video.title || "shared video"}
                allow="autoplay; encrypted-media; picture-in-picture"
                allowFullScreen />
      ) : (
        <button className="wp-facade" onClick={() => setPlaying(p.id)}>
          <span className="wp-play">▶</span>
          <span>
            <b>{p.video.title || "Shared video"}</b>
            <span className="muted small"> · {p.video.platform_name}</span>
            <div className="muted small">{p.video.note}</div>
          </span>
        </button>
      )}
        </div>
      )}

      <div className="wp-actions">
        <button onClick={() => toggleLike(p)}>
      {liked.has(p.id) ? "♥" : "♡"} {p.likes || 0}
        </button>
        <button onClick={() => showComments(p.id)}>💬 comments</button>
        <button onClick={() => share(p.id)}>↗ share</button>
      </div>

      {openComments === p.id && (
        <div className="wp-comments">
      {comments.length === 0 && <p className="muted small">No comments yet.</p>}
      {comments.map((c) => (
        <div key={c.id} className="muted small">• {c.body}</div>
      ))}
      <div className="voice-row">
        <input value={draft} placeholder="say something kind"
               onChange={(e) => setDraft(e.target.value)}
               onKeyDown={(e) => e.key === "Enter" && sendComment(p.id)} />
        <button onClick={() => sendComment(p.id)}>Send</button>
      </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Wall</h2>
        <span className="muted small">the For You feed · every card says why it's here</span>
      </header>

      <div className="card">
        <h3>Say something</h3>
        <label>Post
          <textarea rows={2} value={body} placeholder="what's on your wall"
                    onChange={(e) => setBody(e.target.value)} />
        </label>
        <div className="row">
          <label>Share a video (optional)
            <input value={videoUrl} placeholder="paste a link"
                   onChange={(e) => setVideoUrl(e.target.value)} />
          </label>
          <label>Its title, in your words
            <input value={videoTitle} placeholder="what you're sharing"
                   onChange={(e) => setVideoTitle(e.target.value)} />
          </label>
        </div>
        {platforms && (
          <p className="muted small">
            Links from {platforms} render right here — nothing loads from
            their side until someone presses play.
          </p>
        )}
        <button className="primary" disabled={busy || !body.trim()}
                onClick={publish}>Post</button>
      </div>

      {posts.length === 0 && (
        <div className="card">
          <p className="muted center">Nothing in the feed yet — friends'
            posts, profiles you talk to, and tags you engage with land here.</p>
        </div>
      )}

      {mine.length > 0 && (
        <div className="muted small" style={{ marginTop: 18 }}>Your wall</div>
      )}
      {mine.map(renderPost)}

      {posts.length > 0 && (
        <div className="muted small" style={{ marginTop: 18 }}>For you</div>
      )}
      {posts.map(renderPost)}

      {note && <div className="muted small">{note}</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
