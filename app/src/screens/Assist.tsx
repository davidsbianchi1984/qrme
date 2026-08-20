import { useEffect, useState } from "react";
import { api, uploadMedia, type CreativeWork, type Proofread,
         type ReviewsView, type ThreadView, type TriageResult,
         type UploadedMedia, type WatermarkVerdict,
         type WearableView } from "../api";
import { Refusal } from "../Refusal";
import { fill, t as tr } from "../l10n";
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
  // Which device row's ⓘ is open — the detail lives behind it, the way
  // the phone's own Bluetooth page does it.
  const [detail, setDetail] = useState<string | null>(null);

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

  // The screen follows the profile's language, the way the chrome does.
  const [lang, setLang] = useState<string>("en");
  useEffect(() => {
    if (!me) return;
    api.getLanguage(me).then((r) => setLang(r.language || "en"))
      .catch(() => setLang("en"));
  }, [me]);

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
      <h2>{tr("asst.title", lang)}</h2>
      <p className="muted small">{tr("asst.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      <div className="card">
        <h3>{tr("asst.pile", lang)}</h3>
        <p className="muted small">{tr("asst.pile.lead", lang)}</p>
        <textarea value={pile} onChange={(e) => setPile(e.target.value)}
                  rows={4} placeholder={tr("asst.pile.ph", lang)} />
        <div className="row">
          <input value={criteria} onChange={(e) => setCriteria(e.target.value)}
                 placeholder={tr("asst.pile.best", lang)} style={{ flex: 1 }} />
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
                  })}>{tr("asst.pile.go", lang)}</button>
        </div>
        {triaged && (
          <>
            <p className="small">
              {fill(tr("asst.tally", lang),
                    { reviewed: triaged.reviewed,
                      kept: triaged.kept.length })}
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
                {fill(tr("asst.aside", lang),
                      { n: triaged.discarded_ids.length })}
              </p>
            )}
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("asst.fix", lang)}</h3>
        <textarea value={draft} onChange={(e) => setDraft(e.target.value)}
                  rows={3} placeholder={tr("asst.fix.ph", lang)} />
        <button disabled={busy || !token || !draft.trim()}
                onClick={act(async () =>
                  setFixed(await api.proofread(me, draft.trim(), token)))}>
          {tr("asst.fix.go", lang)}
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
        <h3>{tr("asst.make", lang)}</h3>
        <div className="row">
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            {["note", "poem", "lyric", "music"].map((k) => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>
          <input value={moment} onChange={(e) => setMoment(e.target.value)}
                 placeholder={tr("asst.make.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !token || !moment.trim()}
                  onClick={act(async () => {
                    await api.compose(me, { kind, moment: moment.trim() },
                                      token);
                    setMoment("");
                  }, "Made, and kept.")}>{tr("asst.make.go", lang)}</button>
        </div>
        {works.length === 0 && <p className="muted small">{tr("asst.make.none", lang)}</p>}
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
                {tr("asst.make.check", lang)}
              </button>
            </p>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>{tr("asst.mark", lang)}</h3>
        <p className="muted small">{tr("asst.mark.lead", lang)}</p>
        <div className="row">
          <input value={markId} onChange={(e) => setMarkId(e.target.value)}
                 placeholder={tr("asst.mark.id", lang)} style={{ flex: 1 }} />
        </div>
        <textarea value={markContent}
                  onChange={(e) => setMarkContent(e.target.value)}
                  rows={2} placeholder={tr("asst.mark.content", lang)} />
        <button disabled={busy || !markId.trim()}
                onClick={act(async () => setVerdict(
                  await api.verifyWatermark(markId.trim(), markContent)))}>
          {tr("asst.mark.go", lang)}
        </button>
        {verdict && (
          <>
            <p className="small">
              <strong>{verdict.display.line}</strong> —{" "}
              {fill(tr("asst.mark.issued", lang),
                    { date: verdict.issued_at.slice(0, 10),
                      kind: verdict.kind })}
            </p>
            {/* Both answers, always, and the mismatch loudest. Reporting
                `valid` alone would call this genuine at the moment the
                server said it had been altered. */}
            {verdict.content_match ? (
              <p className="small">
                {tr("asst.mark.match", lang)}
              </p>
            ) : (
              <div className="error">
                <p className="small">
                  {verdict.note
                    || tr("asst.mark.mismatch", lang)}
                </p>
              </div>
            )}
            <p className="muted small">{verdict.disclosure}</p>
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("asst.worn", lang)}</h3>
        <label className="small">
          <input type="checkbox" checked={showRevoked}
                 onChange={(e) => setShowRevoked(e.target.checked)} />
          {" "}{tr("asst.worn.revoked", lang)}
        </label>
        {/* The shape the phone's own Bluetooth page taught everybody: a
            "My devices" group of rows — name, status word on the right,
            an ⓘ that opens the detail — and an "Other devices" section
            under it for the scan and the manual add. A field report held
            the two screens side by side and asked why this one was prose. */}
        <h4>{tr("asst.worn.my", lang)}</h4>
        {(devices?.wearables ?? []).length === 0 && (
          <p className="muted small">{tr("asst.worn.none", lang)}</p>
        )}
        <div className="dev-list">
          {devices?.wearables.map((w) => (
            <div key={w.id}>
              <div className="dev-row">
                <strong style={{ flex: 1 }}>{w.name}</strong>
                <span className={w.paired ? "" : "muted"}>
                  {w.paired ? tr("asst.worn.connected", lang)
                            : tr("asst.worn.notconn", lang)}
                </span>
                <button className="chip"
                        aria-label={tr("asst.worn.details", lang)}
                        aria-expanded={detail === w.id}
                        onClick={() => setDetail(
                          detail === w.id ? null : w.id)}>ⓘ</button>
              </div>
              {detail === w.id && (
                <p className="muted small">
                  {fill(tr("asst.worn.over", lang),
                        { kind: w.kind, transport: w.transport })}
                  {w.paired
                    ? <> · {fill(tr("asst.worn.showing", lang),
                                 { faces: w.faces.join(", ") })}{" "}
                        <button className="chip" disabled={busy}
                                onClick={act(() =>
                                  api.unpairWearable(me, w.name, token),
                                  "Unpaired.")}>{
                                  tr("asst.worn.unpair", lang)}</button></>
                    : <> · {tr("asst.worn.unpaired", lang)}</>}
                </p>
              )}
            </div>
          ))}
        </div>
        <h4>{tr("asst.worn.other", lang)}</h4>
        <div className="row">
          <input value={deviceName}
                 onChange={(e) => setDeviceName(e.target.value)}
                 placeholder={tr("asst.worn.name", lang)} style={{ flex: 1 }} />
          {/* A watch is a thing in the room, not a name you remember how to
              spell — a field report expected to pick it from a scan. The
              chooser is the browser's own; all that comes back is the name,
              which is all the pairing record wants. Typing stays open for
              browsers without Web Bluetooth. */}
          <button className="chip" disabled={busy}
                  onClick={act(async () => {
                    const bt = (navigator as unknown as {
                      bluetooth?: { requestDevice(o: object):
                        Promise<{ name?: string }> };
                    }).bluetooth;
                    if (!bt) throw new Error(tr("asst.worn.nobt", lang));
                    // Dismissing the chooser is a decision, not an error.
                    const dev = await bt
                      .requestDevice({ acceptAllDevices: true })
                      .catch(() => null);
                    if (dev?.name) setDeviceName(dev.name);
                  })}>{tr("asst.worn.scan", lang)}</button>
          <select value={deviceKind}
                  onChange={(e) => setDeviceKind(e.target.value)}>
            {Object.entries(devices?.kinds_worn || {}).map(([k, where]) => (
              <option key={k} value={k}>{k.replace(/_/g, " ")} — {where}</option>
            ))}
          </select>
          <button disabled={busy || !token || !deviceName.trim()}
                  onClick={act(async () => {
                    await api.pairWearable(
                      me, { name: deviceName.trim(), kind: deviceKind }, token);
                    setDeviceName("");
                  }, "Paired.")}>{tr("asst.worn.pair", lang)}</button>
        </div>
        {devices && Object.keys(devices.refusal_reasons).length > 0 && (
          <>
            <h4>{tr("asst.worn.refused", lang)}</h4>
            {/* Verbatim, each of them. The argument is about the people who
                walk into the room, and it is not the console's to shorten. */}
            {Object.entries(devices.refusal_reasons).map(([k, why]) => (
              <p className="muted small" key={k}>{why}</p>
            ))}
          </>
        )}
      </div>

      {reviews && (
        <div className="card">
          <h3>{tr("asst.said", lang)}</h3>
          {reviews.rating.count === 0 ? (
            <p className="muted small">{reviews.rating.note}</p>
          ) : (
            <p className="small">
              {fill(tr("asst.said.from", lang),
                    { avg: reviews.rating.average?.toFixed(1),
                      count: reviews.rating.count })}
            </p>
          )}
          {reviews.reviews.map((r) => (
            <p className="small" key={r.id}>
              {"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}{" "}
              {r.body}
              {r.edited && <span className="muted"> ·{" "}
                {tr("asst.said.edited", lang)}</span>}
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
                     placeholder={tr("asst.said.ph", lang)} style={{ flex: 1 }} />
              <button disabled={busy}
                      onClick={act(async () => {
                        await api.leaveReview(me, {
                          interactor_id: interactor, rating,
                          body: reviewBody.trim() || undefined },
                          interactorToken);
                        setReviewBody("");
                      }, "Left.")}>{
                      tr("asst.said.leave", lang)}</button>
            </div>
          )}
          {/* The refusal it gives is a good one and worth saying up front. */}
          <p className="muted small">{tr("asst.said.rule", lang)}</p>
        </div>
      )}

      {thread && (
        <div className="card">
          <h3>{tr("asst.you", lang)}</h3>
          <p className="muted small">{tr("asst.you.lead", lang)}</p>
          {thread.messages.map((m) => (
            <div key={m.id}>
              <p className="small">
                <strong>{m.role === "profile" ? tr("asst.who.it", lang) : tr("asst.who.you", lang)}</strong>:{" "}
                {m.content}
                {m.edited && (
                  <span className="muted"> · {m.edit_count > 1
                    ? fill(tr("asst.you.times", lang),
                           { n: m.edit_count })
                    : tr("asst.said.edited", lang)}</span>
                )}
              </p>
              {/* Marked rather than hidden. A conversation that quietly
                  rewrote itself would be worse than one that admits the
                  answer is to an older question. */}
              {m.answers_stale_text && (
                <p className="muted small">
                  {tr("asst.you.stale", lang)}
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
                            }, "Corrected.")}>{
                            tr("asst.you.save", lang)}</button>
                    <button onClick={() => setEditing("")}>{tr("asst.you.cancel", lang)}</button>
                  </div>
                ) : (
                  <div className="row">
                    <button className="chip"
                            onClick={() => { setEditing(m.id);
                                             setEditText(m.content); }}>
                      {tr("asst.you.correct", lang)}
                    </button>
                    <button className="chip" disabled={busy}
                            onClick={act(async () => {
                              await api.retractMessage(me, m.id, interactor,
                                                       interactorToken);
                              setThread(await api.thread(me, interactor,
                                                         interactorToken));
                            }, "Taken back.")}>{
                            tr("asst.you.retract", lang)}</button>
                  </div>
                )
              )}
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <h3>{tr("asst.media", lang)}</h3>
        <p className="muted small">{tr("asst.media.lead", lang)}</p>
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
            {fill(tr("asst.media.bytes", lang),
                  { name: uploaded.name || uploaded.kind,
                    n: uploaded.bytes })} ·{" "}
            <a href={uploaded.url} target="_blank" rel="noreferrer">{
              tr("asst.media.open", lang)}</a>
            <span className="muted">
              {uploaded.ai_marked
                ? tr("asst.media.aimarked", lang)
                : tr("asst.media.notaimarked", lang)}
            </span>
          </p>
        )}
      </div>
    </div>
  );
}
