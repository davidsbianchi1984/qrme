import { useEffect, useState } from "react";
import { api, getBase, type MediaUpload, type WallComment, type WallPost } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
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
export function Wall({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [posts, setPosts] = useState<WallPost[]>([]);
  const [mine, setMine] = useState<WallPost[]>([]);
  const [platforms, setPlatforms] = useState<string>("");
  const [body, setBody] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [videoTitle, setVideoTitle] = useState("");
  const [uploads, setUploads] = useState<MediaUpload[]>([]);
  const [mediaAlt, setMediaAlt] = useState("");
  const [uploading, setUploading] = useState(false);
  const [playing, setPlaying] = useState<string | null>(null);   // post id
  const [liked, setLiked] = useState<Set<string>>(new Set());
  const [openComments, setOpenComments] = useState<string | null>(null);
  const [comments, setComments] = useState<WallComment[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [error, setError] = useState<unknown>(null);

  function load() {
    if (!session.profileId) return;
    api.feed(session.profileId).then((r) => setPosts(r.posts))
      .catch((e) => setError(e));
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
        media_ids: uploads.map((u) => u.id),
      }, session.ownerToken);
      if (post.status === "blocked") {
        setError(tr("wll.moderation", lang)
          .replace("{why}", post.blocked_reason || ""));
      } else {
        setBody(""); setVideoUrl(""); setVideoTitle(""); setUploads([]);
        setNote(tr("wll.posted", lang));
        load();
      }
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  async function pickFiles(files: FileList | null) {
    if (!files || !session.profileId || !session.ownerToken) return;
    setUploading(true); setError(null);
    try {
      for (const file of Array.from(files)) {
        const up = await api.uploadMedia(session.profileId, file,
                                         session.ownerToken, mediaAlt.trim());
        setUploads((cur) => [...cur, up]);
      }
      setMediaAlt("");
    } catch (e) { setError(e); }
    finally { setUploading(false); }
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
    } catch (e) { setError(e); }
  }

  async function showComments(postId: string) {
    if (openComments === postId) { setOpenComments(null); return; }
    setOpenComments(postId); setComments([]);
    try {
      const r = await api.postComments(postId);
      setComments(Array.isArray(r) ? r : r.comments || []);
    } catch (e) { setError(e); }
  }

  async function sendComment(postId: string) {
    if (!session.ownerToken || !draft.trim()) return;
    try {
      await api.addComment(postId, draft.trim(), session.ownerToken);
      setDraft("");
      const r = await api.postComments(postId);
      setComments(Array.isArray(r) ? r : r.comments || []);
    } catch (e) { setError(e); }
  }

  // Withdrawing your own. The route refuses somebody else's with a 403 and
  // a missing one with a 404, which is worth knowing beside the friends
  // delete next door — that one answers 200 and reports failure in a flag.
  async function withdrawComment(commentId: string, postId: string) {
    if (!session.ownerToken) return;
    try {
      await api.deleteComment(commentId, session.ownerToken);
      const r = await api.postComments(postId);
      setComments(Array.isArray(r) ? r : r.comments || []);
      setNote(tr("wll.withdrawn", lang));
    } catch (e) { setError(e); }
  }

  async function share(postId: string) {
    if (!session.ownerToken) return;
    try { await api.sharePost(postId, session.ownerToken); setNote(tr("wll.shared", lang)); }
    catch (e) { setError(e); }
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
      <b>{p.display_name
            || (p.profile_id === session.profileId
                  ? tr("wll.you", lang) : tr("wll.someone", lang))}</b>
      {p.reason && <div className="wp-reason">{p.reason}</div>}
        </div>
      </div>
      <p className="wp-body">
        {p.body.split(/(https?:\/\/\S+)/g).map((part, i) =>
          part.startsWith("http")
            ? <a key={i} href={part} target="_blank" rel="noreferrer">{part}</a>
            : part)}
      </p>

      {(p.media || []).length > 0 && (
        <div className="wp-media">
          {(p.media || []).map((m) => m.kind === "image"
            ? <img key={m.id} src={getBase() + m.url} alt={m.alt || ""} />
            : m.kind === "video"
              ? <video key={m.id} src={getBase() + m.url} controls />
              : <a key={m.id} className="wp-file" href={getBase() + m.url}
                   target="_blank" rel="noreferrer" download={m.name || undefined}>
                  📄 {m.name || tr("wll.attachedfile", lang)}
                </a>)}
        </div>
      )}

      {p.video && (
        <div className="wp-video">
      {playing === p.id ? (
        <iframe src={p.video.embed_url}
                title={p.video.title || tr("wll.sharedvideo", lang)}
                allow="autoplay; encrypted-media; picture-in-picture"
                /* See Feed.tsx: the document's `no-referrer` leaves the
                   player unable to check its own embedding and it refuses
                   to play. Origin only. */
                referrerPolicy="strict-origin-when-cross-origin"
                allowFullScreen />
      ) : (
        <button className="wp-facade" onClick={() => setPlaying(p.id)}>
          <span className="wp-play">▶</span>
          <span>
            <b>{p.video.title || tr("wll.sharedvideo", lang)}</b>
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
        <button onClick={() => showComments(p.id)}>{tr("wll.comments", lang)}</button>
        <button onClick={() => share(p.id)}>{tr("wll.share", lang)}</button>
      </div>

      {openComments === p.id && (
        <div className="wp-comments">
      {comments.length === 0 && (
        <p className="muted small">{tr("wll.nocomments", lang)}</p>
      )}
      {comments.map((c) => (
        <div key={c.id} className="muted small">
          • {c.body}
          {/* Only on your own. Somebody else's is a 403 by name, and a
              button that always 403s is worse than no button. */}
          {c.author_id && c.author_id === session.profileId && (
            <button className="chip"
                    onClick={() => withdrawComment(c.id, p.id)}>
              {tr("wll.withdraw", lang)}
            </button>
          )}
        </div>
      ))}
      <div className="voice-row">
        <input value={draft} placeholder={tr("wll.comment.ph", lang)}
               onChange={(e) => setDraft(e.target.value)}
               onKeyDown={(e) => e.key === "Enter" && sendComment(p.id)} />
        <button onClick={() => sendComment(p.id)}>{tr("wll.send", lang)}</button>
      </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("wll.title", lang)}</h2>
        <span className="muted small">{tr("wll.pitch", lang)}</span>
      </header>

      <div className="card">
        <h3>{tr("wll.saysomething", lang)}</h3>
        {/* Blank boxes under plain labels. The composer wore a hint
            inside every field until a field report asked for them gone —
            the label above each box already says everything the ghost
            text repeated. */}
        <label>{tr("wll.post", lang)}
          <textarea rows={2} value={body}
                    onChange={(e) => setBody(e.target.value)} />
        </label>
        <div className="row">
          <label>{tr("wll.sharevideo", lang)}
            <input value={videoUrl}
                   onChange={(e) => setVideoUrl(e.target.value)} />
          </label>
          <label>{tr("wll.videotitle", lang)}
            <input value={videoTitle}
                   onChange={(e) => setVideoTitle(e.target.value)} />
          </label>
        </div>
        <label>{tr("wll.alt", lang)}
          <input value={mediaAlt}
                 onChange={(e) => setMediaAlt(e.target.value)} />
        </label>
        <label>{tr("wll.attach", lang)}
          <input type="file" multiple
                 accept="image/*,video/*,.pdf,.docx,.xlsx,.pptx,.zip,.txt,.csv,.md"
                 onChange={(e) => { pickFiles(e.target.files); e.target.value = ""; }} />
        </label>
        {uploads.length > 0 && (
          <div className="wp-uploads">
            {uploads.map((u) => u.kind === "image"
              ? <img key={u.id} src={getBase() + u.url} alt={u.alt || ""} />
              : u.kind === "video"
                ? <video key={u.id} src={getBase() + u.url} />
                : <span key={u.id} className="wp-file">
                    📄 {u.name || tr("wll.file", lang)}
                  </span>)}
            <button onClick={() => setUploads([])}>{tr("wll.clear", lang)}</button>
          </div>
        )}
        {platforms && (
          <p className="muted small">
            {fill(tr("wll.linksfrom", lang), { platforms })}
          </p>
        )}
        <button className="primary" disabled={busy || uploading || !body.trim()}
                onClick={publish}>
          {uploading ? tr("wll.uploading", lang) : tr("wll.post", lang)}
        </button>
      </div>

      {posts.length === 0 && (
        <div className="card">
          <p className="muted center">{tr("wll.emptyfeed", lang)}</p>
        </div>
      )}

      {mine.length > 0 && (
        <div className="muted small" style={{ marginTop: 18 }}>
          {tr("wll.yourwall", lang)}
        </div>
      )}
      {mine.map(renderPost)}

      {posts.length > 0 && (
        <div className="muted small" style={{ marginTop: 18 }}>
          {tr("wll.foryou", lang)}
        </div>
      )}
      {posts.map(renderPost)}

      {note && <div className="muted small">{note}</div>}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
