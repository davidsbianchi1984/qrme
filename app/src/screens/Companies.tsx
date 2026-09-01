import { useEffect, useState } from "react";
import { api, Company, CompanySeat, InterviewQ } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/* The Company Builder: found, draft, interview, hire, oversee.
 *
 *     asked     start a digital company and fill positions with
 *               synthetic profiles trained for each — any industry,
 *               any title, one employee at a time, each controlled
 *               individually under the company folder
 *     mattered  the interview IS the training, and signing it IS the
 *               hire
 *
 * The screen walks the founder's order: a company list (the folders),
 * a roster per company (the org chart of filled and open seats), and
 * per open seat the drafted interview — the platform writes questions
 * in the role's own vocabulary, the founder edits every answer, and
 * the sign button does the rest. A hired employee's name links to the
 * owner controls that already exist; this screen adds none of its own,
 * because oversight is ownership.
 */
export function Companies({ onOpenProfile }: {
  onOpenProfile?: (profileId: string) => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const token = session.ownerToken || "";
  const [list, setList] = useState<Company[]>([]);
  const [open, setOpen] = useState<Company | null>(null);
  const [seats, setSeats] = useState<CompanySeat[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Founding.
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [headcount, setHeadcount] = useState(5);

  // Open for business.
  const [tagline, setTagline] = useState("");

  // Drafting a seat.
  const [title, setTitle] = useState("");
  const [department, setDepartment] = useState("");

  // The interview under edit, per seat.
  const [interview, setInterview] = useState<{
    seatId: string; rows: { question: string; answer: string }[];
  } | null>(null);

  const refresh = async () => {
    setList(await api.companies(token));
    if (open) {
      const full = await api.companyRoster(open.id, token);
      setSeats(full.seats);
    }
  };
  useEffect(() => { void refresh().catch((e) => setError(String(e))); },
            [open?.id]);

  const act = (fn: () => Promise<void>) => async () => {
    setBusy(true); setError(null);
    try { await fn(); await refresh(); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>{tr("com.title", lang)}</h2>
      <p className="muted small">{tr("com.pitch", lang)}</p>
      {error && <Refusal error={error} variant="inline" />}

      {!open && (
        <>
          <div className="card">
            <h3>{tr("com.found", lang)}</h3>
            <div className="row">
              <input value={name} onChange={(e) => setName(e.target.value)}
                     placeholder={tr("com.name", lang)} style={{ flex: 1 }} />
              {/* Any industry on Earth — a text box, not a menu. */}
              <input value={industry}
                     onChange={(e) => setIndustry(e.target.value)}
                     placeholder={tr("com.industry", lang)}
                     style={{ flex: 1 }} />
            </div>
            <div className="row">
              <label className="muted small">
                {fill(tr("com.headcount", lang),
                      { n: String(headcount) })}
              </label>
              <input type="range" min={1} max={50} value={headcount}
                     onChange={(e) => setHeadcount(Number(e.target.value))} />
              <button disabled={busy || !name.trim() || !industry.trim()}
                      onClick={act(async () => {
                        await api.foundCompany(
                          { name: name.trim(), industry: industry.trim(),
                            headcount }, token);
                        setName(""); setIndustry("");
                      })}>
                {tr("com.found.go", lang)}
              </button>
            </div>
          </div>

          {list.map((c) => (
            <button key={c.id} className="card com-row"
                    onClick={() => setOpen(c)}>
              <b>{c.name}</b>
              <span className="muted small"> — {c.industry}</span>
            </button>
          ))}
        </>
      )}

      {open && (
        <>
          <button className="muted small" onClick={() => setOpen(null)}>
            {tr("com.back", lang)}
          </button>
          <h3>{open.name}</h3>

          {/* The marketplace door. Publishing is an edit on the shop
              rail, so the button is safe to press again; closing takes
              the sign down and dissolves nothing. */}
          <div className="row">
            {!open.shop_id && (
              <>
                <input value={tagline}
                       onChange={(e) => setTagline(e.target.value)}
                       placeholder={tr("com.tagline", lang)}
                       style={{ flex: 1 }} />
                <button disabled={busy ||
                          !seats.some((s) => s.status === "hired")}
                        onClick={act(async () => {
                          await api.publishCompany(open.id,
                            { tagline: tagline.trim() || null }, token);
                          setOpen({ ...open, shop_id: "pending" });
                          setTagline("");
                        })}>
                  {tr("com.publish", lang)}
                </button>
              </>
            )}
            {open.shop_id && (
              <>
                <span className="com-status hired">
                  {tr("com.published", lang)}
                </span>
                <button className="muted small" disabled={busy}
                        onClick={act(async () => {
                          await api.unpublishCompany(open.id, token);
                          setOpen({ ...open, shop_id: null });
                        })}>
                  {tr("com.unpublish", lang)}
                </button>
              </>
            )}
          </div>

          <div className="row">
            <input value={title} onChange={(e) => setTitle(e.target.value)}
                   placeholder={tr("com.seat.title", lang)}
                   style={{ flex: 1 }} />
            <input value={department}
                   onChange={(e) => setDepartment(e.target.value)}
                   placeholder={tr("com.seat.dept", lang)}
                   style={{ flex: 1 }} />
            <button disabled={busy || !title.trim() || !department.trim()}
                    onClick={act(async () => {
                      await api.addSeat(open.id,
                        { title: title.trim(),
                          department: department.trim() }, token);
                      setTitle(""); setDepartment("");
                    })}>
              {tr("com.seat.add", lang)}
            </button>
          </div>

          {seats.map((s) => (
            <div key={s.id} className="card">
              <div className="row">
                <b>{s.title}</b>
                <span className="muted small">{s.department}</span>
                <span className={"com-status " + s.status}>
                  {tr(`com.status.${s.status}`, lang)}
                </span>
              </div>

              {s.status === "hired" && s.profile_id && (
                <button className="muted small"
                        onClick={() => onOpenProfile?.(s.profile_id!)}>
                  {tr("com.oversee", lang)}
                </button>
              )}

              {s.status === "open" && interview?.seatId !== s.id && (
                <button disabled={busy}
                        onClick={act(async () => {
                          const qs = await api.draftInterview(
                            open.id, s.id, token);
                          setInterview({
                            seatId: s.id,
                            rows: qs.questions.map((q: InterviewQ) => ({
                              question: q.question,
                              answer: q.suggested || "" })),
                          });
                        })}>
                  {tr("com.interview", lang)}
                </button>
              )}

              {interview?.seatId === s.id && (
                <div className="com-interview">
                  {interview.rows.map((row, i) => (
                    <label key={i} className="com-q">
                      <span className="muted small">{row.question}</span>
                      <textarea value={row.answer}
                                onChange={(e) => {
                                  const rows = interview.rows.slice();
                                  rows[i] = { ...row,
                                              answer: e.target.value };
                                  setInterview({ ...interview, rows });
                                }} />
                    </label>
                  ))}
                  {/* Signing is hiring — the whole builder in one press. */}
                  <button disabled={busy}
                          onClick={act(async () => {
                            await api.hireSeat(open.id, s.id, {
                              answers: interview.rows
                                .filter((r) => r.answer.trim())
                                .map((r) => ({ question: r.question,
                                               answer: r.answer.trim() })),
                            }, token);
                            setInterview(null);
                          })}>
                    {tr("com.sign", lang)}
                  </button>
                </div>
              )}

              {s.status === "hired" && (
                <button className="muted small" disabled={busy}
                        onClick={act(async () => {
                          await api.retireSeat(open.id, s.id, token);
                        })}>
                  {tr("com.retire", lang)}
                </button>
              )}
            </div>
          ))}
        </>
      )}
    </div>
  );
}
