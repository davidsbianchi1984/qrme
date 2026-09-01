import { useEffect, useState } from "react";
import { accountApi, api, Company, CompanySeat, Display, Embodiment,
         getBase, InterviewQ, RobotCatalogue } from "../api";
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

  // The staffing plan: the founder's words about what the store is
  // meant to be, and what the platform's study predicts it needs.
  const [meantToBe, setMeantToBe] = useState("");
  const [suggested, setSuggested] = useState<
    { title: string; department: string; why: string }[] | null>(null);

  // Bring your own: which seat is choosing from the held profiles.
  const [assigning, setAssigning] = useState<string | null>(null);
  const [held, setHeld] = useState<{ id: string; display_name: string }[]>([]);

  // Drafting a seat.
  const [title, setTitle] = useState("");
  const [department, setDepartment] = useState("");

  // The interview under edit, per seat.
  const [interview, setInterview] = useState<{
    seatId: string; rows: { question: string; answer: string }[];
  } | null>(null);

  // The employee file, in place. Which hired seat's file is open; the
  // minted keys that open that employee's own doors (one per profile,
  // fetched on first use); and what those doors answered.
  const [fileFor, setFileFor] = useState<string | null>(null);
  const [keys, setKeys] = useState<Record<string, string>>({});
  const [forms, setForms] = useState<Embodiment[]>([]);
  const [screens, setScreens] = useState<Display[]>([]);
  const [shelf, setShelf] = useState<RobotCatalogue | null>(null);
  const [kinds, setKinds] = useState<{ kind: string; means: string }[]>([]);
  const [screenKind, setScreenKind] = useState("");
  const [screenLabel, setScreenLabel] = useState("");
  const [handoff, setHandoff] = useState<{
    ticket: string; url: string; qr_svg: string; expires_at: string;
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

  // The employee's own doors — bodies, screens, the handoff — take that
  // profile's owner key, not the founder's session. The account mints one
  // on demand; minting is additive, so every key already out there stands.
  const employeeKey = async (profileId: string): Promise<string> => {
    if (keys[profileId]) return keys[profileId];
    const minted = await accountApi.mintOwnerToken(
      session.accountId!, profileId, session.accountToken!);
    setKeys((k) => ({ ...k, [profileId]: minted.owner_token }));
    return minted.owner_token;
  };

  const loadFile = async (profileId: string) => {
    const key = await employeeKey(profileId);
    const [bodies, myScreens, catalogue, vocab] = await Promise.all([
      api.embodiments(profileId, key),
      api.myDisplays(profileId, key),
      api.robotCatalogue(),
      api.displayCatalog(),
    ]);
    setForms(bodies);
    setScreens(myScreens.displays.filter((d) => d.live));
    setShelf(catalogue);
    setKinds(vocab.kinds.map((k) => ({ kind: k.kind, means: k.means })));
    if (vocab.kinds.length) {
      setScreenKind((prev) => prev || vocab.kinds[0].kind);
    }
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

          {/* The staffing plan. The platform studies what the founder
              says the store is meant to be and predicts the roster a
              fully functioning one carries — suggestions, never walls,
              and never deeds: only the founder's press opens a seat. */}
          <div className="card">
            <div className="row">
              <input value={meantToBe}
                     onChange={(e) => setMeantToBe(e.target.value)}
                     placeholder={tr("com.plan.ask", lang)}
                     style={{ flex: 1 }} />
              <button disabled={busy}
                      onClick={act(async () => {
                        const out = await api.planCompany(open.id,
                          { description: meantToBe.trim() || null }, token);
                        setSuggested(out.suggestions);
                      })}>
                {tr("com.plan.go", lang)}
              </button>
            </div>
            {suggested && suggested.map((s, i) => (
              <div key={i} className="row">
                <b>{s.title}</b>
                <span className="muted small">{s.department}</span>
                <span className="muted small" style={{ flex: 1 }}>
                  {s.why}
                </span>
                <button disabled={busy}
                        onClick={act(async () => {
                          await api.addSeat(open.id,
                            { title: s.title, department: s.department },
                            token);
                          setSuggested(suggested.filter((_, j) => j !== i));
                        })}>
                  {tr("com.seat.add", lang)}
                </button>
              </div>
            ))}
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

              {/* The employee file, in place: where they work and how to
                  hand them out — no other menu involved, because the
                  founder is standing here in front of the seat. */}
              {s.status === "hired" && s.profile_id && fileFor !== s.id && (
                <button className="muted small" disabled={busy}
                        onClick={act(async () => {
                          await loadFile(s.profile_id!);
                          setHandoff(null);
                          setFileFor(s.id);
                        })}>
                  {tr("com.file", lang)}
                </button>
              )}
              {fileFor === s.id && s.profile_id && (
                <div className="com-file">
                  <h4>{tr("com.work.title", lang)}</h4>
                  {forms.length === 0 && screens.length === 0 && (
                    <p className="muted small">{tr("com.work.none", lang)}</p>
                  )}
                  {forms.map((f) => (
                    <div key={f.name} className="row">
                      <b>{f.name}</b>
                      <span className="muted small">{f.kind}</span>
                    </div>
                  ))}
                  {screens.map((d) => (
                    <div key={d.id} className="row">
                      <b>{d.label}</b>
                      <span className="muted small">{d.kind}</span>
                    </div>
                  ))}

                  {/* The robot shelf, the whole catalogue in place. An
                      announced body renders un-bindable rather than
                      hidden — see qrme/robotics.py on why hiding a
                      published machine would be the worse lie. */}
                  <p className="muted small">{tr("com.work.shelf", lang)}</p>
                  {shelf && Object.entries(shelf.by_maker).map(
                    ([maker, models]) => (
                    <div key={maker} className="com-shelf">
                      <span className="muted small">{maker}</span>
                      {models.map((m) => (
                        <span key={m.model} className="row">
                          <b>{m.label}</b>
                          <span className={"com-avail " + m.availability}>
                            {tr(`com.avail.${m.availability}`, lang)}
                          </span>
                          <button className="muted small"
                                  disabled={busy || !m.bindable}
                                  onClick={act(async () => {
                                    const key =
                                      await employeeKey(s.profile_id!);
                                    await api.bindRobot(s.profile_id!,
                                      { model: m.model, name: m.label },
                                      key);
                                    await loadFile(s.profile_id!);
                                  })}>
                            {tr("com.work.bind", lang)}
                          </button>
                        </span>
                      ))}
                    </div>
                  ))}

                  <div className="row">
                    <select value={screenKind}
                            onChange={(e) => setScreenKind(e.target.value)}>
                      {kinds.map((k) => (
                        <option key={k.kind} value={k.kind}>{k.kind}</option>
                      ))}
                    </select>
                    <input value={screenLabel}
                           onChange={(e) => setScreenLabel(e.target.value)}
                           placeholder={tr("com.work.screen.label", lang)}
                           style={{ flex: 1 }} />
                    <button className="muted small"
                            disabled={busy || !screenLabel.trim()}
                            onClick={act(async () => {
                              const key = await employeeKey(s.profile_id!);
                              await api.placeDisplay(s.profile_id!,
                                { kind: screenKind,
                                  label: screenLabel.trim() }, key);
                              setScreenLabel("");
                              await loadFile(s.profile_id!);
                            })}>
                      {tr("com.work.screen", lang)}
                    </button>
                  </div>

                  {/* The nearby-device road: the studio's own address as
                      a code a camera can read — same network, no store. */}
                  <div className="row">
                    <img className="com-qr" alt=""
                         src={getBase() + "/pair/qr.svg"} />
                    <span className="muted small">
                      {tr("com.work.pair", lang)}
                    </span>
                  </div>

                  {/* Hand them out: the employee as a thing you can give
                      somebody — a code to type, a code to scan, a link, a
                      file. The handoff ticket is the whole authority; the
                      founder's key never rides in any of them. */}
                  <h4>{tr("com.hand.title", lang)}</h4>
                  <div className="row">
                    <button className="muted small" disabled={busy}
                            onClick={act(async () => {
                              const key = await employeeKey(s.profile_id!);
                              setHandoff(await api.exportTicket(
                                s.profile_id!, key));
                            })}>
                      {tr("com.hand.mint", lang)}
                    </button>
                    <button className="muted small" disabled={busy}
                            onClick={act(async () => {
                              const key = await employeeKey(s.profile_id!);
                              const bundle = await api.exportProfile(
                                s.profile_id!, key);
                              const blob = new Blob(
                                [JSON.stringify(bundle, null, 2)],
                                { type: "application/json" });
                              const a = document.createElement("a");
                              a.href = URL.createObjectURL(blob);
                              a.download = `${s.title}.qrme.json`;
                              a.click();
                              URL.revokeObjectURL(a.href);
                            })}>
                      {tr("com.hand.download", lang)}
                    </button>
                  </div>
                  {handoff && (
                    <div className="com-handoff">
                      <img className="com-qr" alt=""
                           src={getBase() + handoff.qr_svg} />
                      <div>
                        <p className="small">
                          <b>{tr("com.hand.code", lang)}</b>{" "}
                          <code>{handoff.ticket}</code>
                        </p>
                        <p className="small">
                          <b>{tr("com.hand.link", lang)}</b>{" "}
                          <code>{getBase() + handoff.url}</code>
                        </p>
                        <p className="muted small">
                          {tr("com.hand.note", lang)}
                        </p>
                      </div>
                    </div>
                  )}
                  <button className="muted small"
                          onClick={() => setFileFor(null)}>
                    {tr("com.file.close", lang)}
                  </button>
                </div>
              )}

              {/* Bring your own: the founder's existing or blended
                  profile takes the seat — the Blend screen builds
                  hybrids, this door seats them. */}
              {s.status === "open" && assigning !== s.id && (
                <button className="muted small" disabled={busy}
                        onClick={act(async () => {
                          const mine = await accountApi.heldProfiles(
                            session.accountId!, session.accountToken!);
                          setHeld(mine.profiles.map((p) => ({
                            id: p.profile_id, display_name: p.display_name })));
                          setAssigning(s.id);
                        })}>
                  {tr("com.bring", lang)}
                </button>
              )}
              {assigning === s.id && held.map((h) => (
                <button key={h.id} className="muted small" disabled={busy}
                        onClick={act(async () => {
                          await api.assignSeat(open.id, s.id,
                            { profile_id: h.id }, token);
                          setAssigning(null);
                        })}>
                  {h.display_name}
                </button>
              ))}
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
