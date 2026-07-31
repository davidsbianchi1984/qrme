import { useEffect, useState } from "react";
import { api, uploadMedia, type CreativeWork, type Proofread,
         type ReviewsView, type ThreadView, type TriageResult,
         type UploadedMedia, type WatermarkVerdict,
         type WearableView } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The profile working for its owner, and what it leaves behind.
 *
 * Triage a pile, fix a piece of writing, compose something to keep, pair the
 * wearables the watch faces run on, read what people who actually talked to it
 * said, correct something you said yourself — and check any mark.
 *
 * Four things this screen refuses to smooth over:
 *
 * - **triage shows its reasons.** Each kept item comes back with the score it
 *   scored and why it survived, because the ranking is deliberately
 *   transparent. A pile sorted by a number nobody can see is a pile somebody
 *   has to re-check by hand, which is the work triage was supposed to do;
 * - **a room-facing microphone is refused with a paragraph, not a shrug.** The
 *   backend's sentence is rendered verbatim: a smart speaker *hears whoever
 *   walks into the room, and they did not pair it, were not asked, and may
 *   have a right not to be recorded*. That is an argument, and the console
 *   does not get to summarise somebody's argument into "unsupported device";
 * - **`answers_stale_text` is drawn.** A reply written before the message
 *   above it was edited is marked as answering an older question, rather than
 *   the conversation quietly rewriting itself;
 * - **`valid` and `content_match` are asked separately.** They can disagree —
 *   a real credential whose content has since been altered comes back
 *   `valid: true, content_match: false`. A screen reporting `valid` alone
 *   would call something genuine at the exact moment the server said it had
 *   been changed, which is the one failure a provenance check must not have.
 */
export function Assist({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const me = session.profileId || "";
  const token = session.ownerToken || "";
  const interactor = session.interactorId || "";
  const interactorToken = session.interactorToken || token;

  const [pile, setPile] = useState("");
  const [keep, setKeep] = useState(3);
  const [criteria, setCriteria] = useState("");
  const [triaged, setTriaged] = useState<TriageResult | null>(null);

  const [draft, setDraft] = useState("");
  const [fixed, setFixed] = useState<Proofread | null>(null);

  const [moment, setMoment] = useState("");
  const [kind, setKind] = useState("note");
  const [works, setWorks] = useState<CreativeWork[]>([]);

  const [devices, setDevices] = useState<WearableView | null>(null);
  const [deviceName, setDeviceName] = useState("");
  const [deviceKind, setDeviceKind] = useState("watch");
  const [showRevoked, setShowRevoked] = useState(false);

  const [reviews, setReviews] = useState<ReviewsView | null>(null);
  const [rating, setRating] = useState(5);
  const [reviewBody, setReviewBody] = useState("");

  const [thread, setThread] = useState<ThreadView | null>(null);
  const [editing, setEditing] = useState<string>("");
  const [editText, setEditText] = useState("");

  const [uploaded, setUploaded] = useState<UploadedMedia | null>(null);

  const [markId, setMarkId] = useState("");
  const [markContent, setMarkContent] = useState("");
  const [verdict, setVerdict] = useState<WatermarkVerdict | null>(null);

  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fail = (e: unknown) => setError(e);

  function load() {
    if (!me) return;
    api.reviews(me).then(setReviews).catch(() => setReviews(null));
    if (!token) return;
    api.works(me, token).then(setWorks).catch(() => setWorks([]));
    api.wearables(me, token, showRevoked).then(setDevices)
      .catch(() => setDevices(null));
  }
  useEffect(load, [me, token, showRevoked]);

  useEffect(() => {
    if (!me || !interactor || !interactorToken) return;
    api.thread(me, interactor, interactorToken).then(setThread)
      .catch(() => setThread(null));
  }, [me, interactor, interactorToken]);

  const act = (fn: () => Promise<unknown>, said?: string) => async () => {
    setError(null); setNote(null); setBusy(true);
    try { await fn(); if (said) setNote(said); load(); }
    catch (e) { fail(e); } finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>What it can do for you</h2>
      <p className="muted small">
        Sort a pile, fix a draft, make something worth keeping — and every
        generated thing carries a mark you can check.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>Sort a pile</h3>
        <p className="muted small">
          One item per line. You get back the best few <em>with the reason
          each one survived</em> — the ranking is meant to be arguable.
        </p>
        <textarea value={pile} onChange={(e) => setPile(e.target.value)}
                  rows={4} placeholder="one candidate per line" />
        <div className="row">
          <input value={criteria} onChange={(e) => setCriteria(e.target.value)}
                 placeholder="what best means to you" style={{ flex: 1 }} />
          <input type="number" min={1} value={keep}
                 onChange={(e) => setKeep(Number(e.target.value))}
                 style={{ width: 80 }} />
          <button disabled={busy || !token || !pile.trim()}
                  onClick={act(async () => {
                    const items = pile.split("\n").map((t) => t.trim())
                      .filter(Boolean)
                      .map((text, i) => ({ id: `i${i + 1}`, text }));
                    setTriaged(await api.triage(
                      me, { items, keep: Math.min(keep, items.length),
                            criteria: criteria.trim() || undefined }, token));
                  })}>Sort it</button>
        </div>
        {triaged && (
          <>
            <p className="small">
              {triaged.reviewed} looked at, {triaged.kept.length} kept.
            </p>
            {triaged.kept.map((k) => (
              <p className="small" key={k.id}>
                <strong>{k.preview}</strong>
                {/* The reason, not just the rank. */}
                <br /><span className="muted">{k.reason}</span>
              </p>
            ))}
            {triaged.discarded_ids.length > 0 && (
              <p className="muted small">
                Set aside: {triaged.discarded_ids.length}.
              </p>
            )}
          </>
        )}
      </div>

      <div className="card">
        <h3>Fix a draft</h3>
        <textarea value={draft} onChange={(e) => setDraft(e.target.value)}
                  rows={3} placeholder="paste something you wrote" />
        <button disabled={busy || !token || !draft.trim()}
                onClick={act(async () =>
                  setFixed(await api.proofread(me, draft.trim(), token)))}>
          Proofread
        </button>
        {fixed && (
          <>
            <p className="small">{fixed.edited}</p>
            {fixed.suggestions.length > 0 && (
              <p className="muted small">
                {fixed.suggestions.join(" · ")}
              </p>
            )}
            {/* Marked, like everything else generated here. */}
            <p className="muted small">
              {fixed.watermark.display.line} — {fixed.watermark.disclosure}
            </p>
          </>
        )}
      </div>

      <div className="card">
        <h3>Make something to keep</h3>
        <div className="row">
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            {["note", "poem", "lyric", "music"].map((k) => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>
          <input value={moment} onChange={(e) => setMoment(e.target.value)}
                 placeholder="the moment to capture" style={{ flex: 1 }} />
          <button disabled={busy || !token || !moment.trim()}
                  onClick={act(async () => {
                    await api.compose(me, { kind, moment: moment.trim() },
                                      token);
                    setMoment("");
                  }, "Made, and kept.")}>Compose</button>
        </div>
        {works.length === 0 && <p className="muted small">Nothing kept yet.</p>}
        {works.map((w) => (
          <div key={w.id}>
            <p className="small">
              <strong>{w.kind}</strong> · {w.moment}
            </p>
            <p className="small">{w.content}</p>
            <p className="muted small">
              {w.watermark.display.line} ·{" "}
              <button className="chip"
                      onClick={() => { setMarkId(w.watermark.watermark_id);
                                       setMarkContent(w.content); }}>
                check this mark
              </button>
            </p>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Check a mark</h3>
        <p className="muted small">
          Two questions, and they are not the same one: was this credential
          issued here, and is this the content it was issued for.
        </p>
        <div className="row">
          <input value={markId} onChange={(e) => setMarkId(e.target.value)}
                 placeholder="a watermark id" style={{ flex: 1 }} />
        </div>
        <textarea value={markContent}
                  onChange={(e) => setMarkContent(e.target.value)}
                  rows={2} placeholder="the content to check against it" />
        <button disabled={busy || !markId.trim()}
                onClick={act(async () => setVerdict(
                  await api.verifyWatermark(markId.trim(), markContent)))}>
          Check it
        </button>
        {verdict && (
          <>
            <p className="small">
              <strong>{verdict.display.line}</strong> — issued{" "}
              {verdict.issued_at.slice(0, 10)} for a {verdict.kind}.
            </p>
            {/* Both answers, always, and the mismatch loudest. Reporting
                `valid` alone would call this genuine at the moment the
                server said it had been altered. */}
            {verdict.content_match ? (
              <p className="small">
                This is the content the credential was issued for.
              </p>
            ) : (
              <div className="error">
                <p className="small">
                  {verdict.note
                    || "this content does not match the credential"}
                </p>
              </div>
            )}
            <p className="muted small">{verdict.disclosure}</p>
          </>
        )}
      </div>

      <div className="card">
        <h3>What it is worn on</h3>
        <label className="small">
          <input type="checkbox" checked={showRevoked}
                 onChange={(e) => setShowRevoked(e.target.checked)} />
          {" "}include ones you have unpaired — the row stays, with the date
        </label>
        {devices?.wearables.filter((w) => w.paired).length === 0 && (
          <p className="muted small">Nothing paired.</p>
        )}
        {devices?.wearables.map((w) => (
          <p className="small" key={w.id}>
            <strong>{w.name}</strong> — {w.kind} over {w.transport}
            {w.paired
              ? <> · showing {w.faces.join(", ")}{" "}
                  <button className="chip" disabled={busy}
                          onClick={act(() =>
                            api.unpairWearable(me, w.name, token),
                            "Unpaired.")}>unpair</button></>
              : <span className="muted"> · unpaired</span>}
          </p>
        ))}
        <div className="row">
          <input value={deviceName}
                 onChange={(e) => setDeviceName(e.target.value)}
                 placeholder="what you call it" style={{ flex: 1 }} />
          <select value={deviceKind}
                  onChange={(e) => setDeviceKind(e.target.value)}>
            {Object.entries(devices?.kinds || {}).map(([k, where]) => (
              <option key={k} value={k}>{k.replace(/_/g, " ")} — {where}</option>
            ))}
          </select>
          <button disabled={busy || !token || !deviceName.trim()}
                  onClick={act(async () => {
                    await api.pairWearable(
                      me, { name: deviceName.trim(), kind: deviceKind }, token);
                    setDeviceName("");
                  }, "Paired.")}>Pair</button>
        </div>
        {devices && Object.keys(devices.refused).length > 0 && (
          <>
            <h4>What will not be paired</h4>
            {/* Verbatim, each of them. The argument is about the people who
                walk into the room, and it is not the console's to shorten. */}
            {Object.entries(devices.refused).map(([k, why]) => (
              <p className="muted small" key={k}>{why}</p>
            ))}
          </>
        )}
      </div>

      {reviews && (
        <div className="card">
          <h3>What people said</h3>
          {reviews.rating.count === 0 ? (
            <p className="muted small">{reviews.rating.note}</p>
          ) : (
            <p className="small">
              {reviews.rating.average?.toFixed(1)} from{" "}
              {reviews.rating.count} review
              {reviews.rating.count === 1 ? "" : "s"}
            </p>
          )}
          {reviews.reviews.map((r) => (
            <p className="small" key={r.id}>
              {"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}{" "}
              {r.body}
              {r.edited && <span className="muted"> · edited</span>}
            </p>
          ))}
          {interactor && (
            <div className="row">
              <select value={rating}
                      onChange={(e) => setRating(Number(e.target.value))}>
                {[5, 4, 3, 2, 1].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
              <input value={reviewBody}
                     onChange={(e) => setReviewBody(e.target.value)}
                     placeholder="what you thought" style={{ flex: 1 }} />
              <button disabled={busy}
                      onClick={act(async () => {
                        await api.leaveReview(me, {
                          interactor_id: interactor, rating,
                          body: reviewBody.trim() || undefined },
                          interactorToken);
                        setReviewBody("");
                      }, "Left.")}>Leave a review</button>
            </div>
          )}
          {/* The refusal it gives is a good one and worth saying up front. */}
          <p className="muted small">
            A review comes from somebody who actually talked to it — one per
            person, edited rather than stacked.
          </p>
        </div>
      )}

      {thread && (
        <div className="card">
          <h3>Something you said</h3>
          <p className="muted small">
            You can correct or retract your own turn. The correction carries
            forward: the next reply reasons from what you meant.
          </p>
          {thread.messages.map((m) => (
            <div key={m.id}>
              <p className="small">
                <strong>{m.role === "profile" ? "it" : "you"}</strong>:{" "}
                {m.content}
                {m.edited && (
                  <span className="muted"> · edited{m.edit_count > 1
                    ? ` ${m.edit_count} times` : ""}</span>
                )}
              </p>
              {/* Marked rather than hidden. A conversation that quietly
                  rewrote itself would be worse than one that admits the
                  answer is to an older question. */}
              {m.answers_stale_text && (
                <p className="muted small">
                  ↑ written before the message above it was changed, so it
                  answers the older wording.
                </p>
              )}
              {m.role !== "profile" && interactor && (
                editing === m.id ? (
                  <div className="row">
                    <input value={editText}
                           onChange={(e) => setEditText(e.target.value)}
                           style={{ flex: 1 }} />
                    <button disabled={busy || !editText.trim()}
                            onClick={act(async () => {
                              await api.editMessage(me, m.id, interactor,
                                editText.trim(), interactorToken);
                              setEditing("");
                              setThread(await api.thread(me, interactor,
                                                         interactorToken));
                            }, "Corrected.")}>Save</button>
                    <button onClick={() => setEditing("")}>Cancel</button>
                  </div>
                ) : (
                  <div className="row">
                    <button className="chip"
                            onClick={() => { setEditing(m.id);
                                             setEditText(m.content); }}>
                      correct it
                    </button>
                    <button className="chip" disabled={busy}
                            onClick={act(async () => {
                              await api.retractMessage(me, m.id, interactor,
                                                       interactorToken);
                              setThread(await api.thread(me, interactor,
                                                         interactorToken));
                            }, "Taken back.")}>take it back</button>
                  </div>
                )
              )}
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h3>Add a photo or a document</h3>
        <p className="muted small">
          The kind is read from the bytes rather than the file name, and
          nothing you took yourself is AI-marked.
        </p>
        <input type="file" disabled={busy || !token}
               onChange={async (e) => {
                 const file = e.target.files?.[0];
                 if (!file) return;
                 setError(null); setNote(null); setBusy(true);
                 try { setUploaded(await uploadMedia(me, file, token)); }
                 catch (err) { fail(err); } finally { setBusy(false); }
               }} />
        {uploaded && (
          <p className="small">
            {uploaded.name || uploaded.kind} — {uploaded.bytes} bytes ·{" "}
            <a href={uploaded.url} target="_blank" rel="noreferrer">open</a>
            <span className="muted">
              {uploaded.ai_marked
                ? " · marked as AI-generated"
                : " · not AI-marked, because you made it"}
            </span>
          </p>
        )}
      </div>
    </div>
  );
}
