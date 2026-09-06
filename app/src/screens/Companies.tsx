import { useEffect, useState } from "react";
import { accountApi, api, Company, CompanySeat, Display, Embodiment,
         PoolRow, RegistryRow,
         getBase, InterviewQ, RobotCatalogue } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/* The kit, in the order the founder walks it: what the new hire sees
 * through, hears through, works with, and wears. Each rung opens the
 * next and the last one signs, because the request was not "put the
 * equipment in the builder" — it was that each builder leads into the
 * next until you hire and seat your new hire.
 *
 * Every one of these four doors already existed. What did not exist was
 * a way to reach them without walking out of the seat you were hiring
 * for: the screen lived in the employee file, the speaker in the
 * Workshop, the robot on the settings shelf, the face in the studio.
 * Nothing about the doors needed the founder to leave. Only the screens
 * did.
 */
const RUNGS = ["eyes", "ears", "hands", "body"] as const;

/** Has this rung been answered? `body` is the awkward one: a face can be
 *  a pick off the shelf or a sentence handed to the forge, and either
 *  one counts as answered. */
function filled(kit: Kit, rung: typeof RUNGS[number]): boolean {
  if (rung === "eyes") return !!kit.eyes;
  if (rung === "ears") return !!kit.ears;
  if (rung === "hands") return !!kit.hands;
  return !!kit.face || !!kit.painted.trim();
}

/** What a hire is kitted with, chosen before there is anybody to fit it
 *  to. A seat has no profile until it is signed, so none of the four
 *  doors can be pressed while the founder is standing here choosing —
 *  see `signAndSeat`, which signs first and fits second because that is
 *  the only order the world allows. */
type Kit = {
  seatId: string;
  eyes: { kind: string; label: string } | null;
  ears: { kind: string; name: string } | null;
  hands: { model: string; label: string } | null;
  face: { id: string; label: string } | null;
  /** A face described in words when the shelf has none that fits. Held
   *  as text rather than as a fifth `| null` because the forge is given
   *  a sentence, and an empty one means the founder did not write it. */
  painted: string;
};

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

  // The pool, browsable. `poolOpen` is the panel; `poolQ` is what was
  // typed and `poolFam` the heading being walked. Nothing here opens a
  // seat on its own — picking a position fills the title box, and the
  // founder still presses to open it.
  const [poolOpen, setPoolOpen] = useState(false);
  const [poolQ, setPoolQ] = useState("");
  const [poolFam, setPoolFam] = useState("");
  const [families, setFamilies] = useState<string[]>([]);
  const [pool, setPool] = useState<PoolRow[]>([]);
  const [poolTotal, setPoolTotal] = useState(0);

  // What the study downloaded for a seat, under review before signing.
  const [study, setStudy] = useState<{
    seatId: string; found: boolean; knownAs: string | null;
    skills: string[]; connections: string[]; tailored: number;
    knowledge: string; studiedBy: string | null;
  } | null>(null);
  const [addSkill, setAddSkill] = useState("");
  const [addConn, setAddConn] = useState("");

  // The kit under assembly, and which rung of it is open. One rung at a
  // time, in order: the founder asked for a ladder, not a wall of forms.
  const [kit, setKit] = useState<Kit | null>(null);
  const [rung, setRung] = useState<typeof RUNGS[number] | "">("");
  const [faces, setFaces] = useState<RegistryRow[]>([]);
  // The rungs keep their own boxes rather than borrowing the employee
  // file's screen placer below: two open panels sharing one input is a
  // bug that only shows up when somebody has both open.
  const [eyeKind, setEyeKind] = useState("");
  const [eyeLabel, setEyeLabel] = useState("");
  const [earKind, setEarKind] = useState("speaker");
  const [earName, setEarName] = useState("");

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

  // The four catalogues behind the ladder. All four doors are public —
  // no profile, no key — which is exactly what lets the founder kit out
  // a hire who has not been signed yet. `loadFile` fetches three of the
  // same four for an employee who already exists; this one adds the
  // face shelf and takes no token, and the two are kept apart because
  // one of them is allowed to run before there is anybody there.
  const loadKit = async () => {
    const [catalogue, vocab, shelfOfFaces] = await Promise.all([
      api.robotCatalogue(),
      api.displayCatalog(),
      api.avatarShelf(),
    ]);
    setShelf(catalogue);
    setKinds(vocab.kinds.map((k) => ({ kind: k.kind, means: k.means })));
    if (vocab.kinds.length) {
      setEyeKind((prev) => prev || vocab.kinds[0].kind);
    }
    setFaces(shelfOfFaces.shelf);
  };

  // Open the ladder at its first rung. Pressed from the study's Keep,
  // so reading what the job needs is what leads into equipping for it.
  const startKit = async (seatId: string) => {
    setKit({ seatId, eyes: null, ears: null, hands: null,
             face: null, painted: "" });
    setRung(RUNGS[0]);
    await loadKit();
  };

  // Sign, then fit. The order is forced rather than chosen: the hire is
  // what creates the profile, and until there is a profile there is
  // nothing to hang a screen, a speaker, a robot or a face on. That has
  // a consequence this screen must not hide — a fitting can fail after
  // the hire already stands — so each piece is caught by name and what
  // did not go on is reported, instead of one failed fitting coming
  // back looking like a failed hire.
  const signAndSeat = async (
    companyId: string, seatId: string,
    rows: { question: string; answer: string }[],
  ) => {
    const hired = await api.hireSeat(companyId, seatId, {
      answers: rows.filter((r) => r.answer.trim())
        .map((r) => ({ question: r.question, answer: r.answer.trim() })),
    }, token);
    const chosen = kit?.seatId === seatId ? kit : null;
    setInterview(null); setStudy(null); setKit(null); setRung("");
    if (!chosen) return;

    const key = await employeeKey(hired.profile_id);
    const missed: string[] = [];
    const fit = async (what: string, go: () => Promise<unknown>) => {
      try { await go(); } catch { missed.push(what); }
    };
    if (chosen.eyes) {
      const eyes = chosen.eyes;
      await fit(tr("com.kit.eyes", lang), () => api.placeDisplay(
        hired.profile_id, { kind: eyes.kind, label: eyes.label }, key));
    }
    if (chosen.ears) {
      const ears = chosen.ears;
      // `has_llm` is false and stays false: a speaker in a room and an
      // earpiece on a person both relay to this host. Claiming a model
      // rides on the hardware would be a claim about the hardware.
      await fit(tr("com.kit.ears", lang), () => api.addEmbodiment(
        hired.profile_id,
        { name: ears.name, kind: ears.kind, has_llm: false }, key));
    }
    if (chosen.hands) {
      const hands = chosen.hands;
      await fit(tr("com.kit.hands", lang), () => api.bindRobot(
        hired.profile_id, { model: hands.model, name: hands.label }, key));
    }
    if (chosen.face) {
      const face = chosen.face;
      await fit(tr("com.kit.body", lang), () => api.claimFace(
        hired.profile_id, face.id, key));
    } else if (chosen.painted.trim()) {
      const words = chosen.painted.trim();
      await fit(tr("com.kit.body", lang), () => api.paintFace(
        hired.profile_id, words, key));
    }
    if (missed.length) {
      // Plain substitution, not `fill`: `fill` returns nodes for a
      // button's children, and the refusal banner takes a string.
      setError(tr("com.kit.partly", lang)
        .replace("{what}", missed.join(", ")));
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

          {/* The pool, browsable. The Builder used to offer three canned
              seats when the study did not parse; the app carries the
              positions now, so the founder can go and look. Typing your
              own stays exactly as good — this is a way in, never a wall. */}
          <div className="row">
            <button disabled={busy} data-go="browse"
                    onClick={act(async () => {
                      const next = !poolOpen;
                      setPoolOpen(next);
                      if (next && !families.length) {
                        const f = await api.occupationFamilies(token);
                        setFamilies(f.families);
                      }
                      if (next) {
                        const r = await api.browseOccupations(
                          poolQ, poolFam, token);
                        setPool(r.positions); setPoolTotal(r.total);
                      }
                    })}>
              {/* Each branch says its own key: a key chosen inside the
                  call renders fine and is invisible to the localizer
                  audit, which is how translated strings go unread. */}
              {poolOpen ? tr("com.browse.close", lang)
                        : tr("com.browse", lang)}
            </button>
            {poolOpen && poolTotal > 0 && (
              <span className="muted small">
                {poolTotal.toLocaleString()} {tr("com.browse.count", lang)}
              </span>
            )}
          </div>

          {poolOpen && (
            <div className="com-pool" data-screen="212">
              <div className="row">
                <input value={poolQ} style={{ flex: 2 }}
                       placeholder={tr("com.browse.ask", lang)}
                       onChange={(e) => setPoolQ(e.target.value)}
                       onKeyDown={(e) => {
                         if (e.key === "Enter") {
                           act(async () => {
                             const r = await api.browseOccupations(
                               poolQ, poolFam, token);
                             setPool(r.positions);
                           })();
                         }
                       }} />
                <select value={poolFam} style={{ flex: 1 }}
                        onChange={(e) => {
                          // `act` wraps a no-argument thunk, so the
                          // chosen heading is read off the event before
                          // the request is handed over.
                          const fam = e.target.value;
                          setPoolFam(fam);
                          act(async () => {
                            const r = await api.browseOccupations(
                              poolQ, fam, token);
                            setPool(r.positions);
                          })();
                        }}>
                  <option value="">{tr("com.browse.all", lang)}</option>
                  {families.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>
              {!pool.length && (
                <p className="muted small">{tr("com.browse.none", lang)}</p>
              )}
              {pool.map((r) => (
                <div key={r.title} className="com-pool-row">
                  <div className="row">
                    <b style={{ flex: 1 }}>{r.title}</b>
                    <span className="muted small">{r.family}</span>
                    <button disabled={busy}
                            onClick={() => {
                              setTitle(r.title);
                              if (!department.trim()) setDepartment(r.family);
                            }}>
                      {tr("com.seat.add", lang)}
                    </button>
                  </div>
                  {/* What the seat would need, before it is opened. The
                      knowledge is the deferred half and arrives on the
                      Download knowledge press. */}
                  <p className="muted small">{r.skills.slice(0, 6).join(" · ")}</p>
                </div>
              ))}
            </div>
          )}

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
                <button disabled={busy} data-go="interview"
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
                  {/* Download knowledge. The study already ran, silently,
                      inside the draft — the platform knew the trade and
                      the founder was never shown it, so a seat was signed
                      against an understanding nobody had read. This is
                      that step made a step: press it, read what came
                      back, change what is wrong, then sign. */}
                  {study?.seatId !== s.id && (
                    <button disabled={busy} data-go="study"
                            onClick={act(async () => {
                              const found = await api.studySeat(
                                open.id, s.id, token);
                              setStudy({
                                seatId: s.id, found: found.found,
                                knownAs: found.known_as,
                                skills: found.skills,
                                connections: found.connections,
                                tailored: found.tailored,
                                knowledge: found.knowledge,
                                studiedBy: found.studied_by,
                              });
                            })}>
                      {busy ? tr("com.study.busy", lang)
                            : tr("com.study", lang)}
                    </button>
                  )}

                  {study?.seatId === s.id && (
                    <div className="com-study" data-screen="213">
                      {!study.found && (
                        <p className="muted small">
                          {tr("com.study.unknown", lang)}
                        </p>
                      )}
                      {study.found && study.knownAs
                        && study.knownAs !== s.title && (
                        <p className="muted small">{study.knownAs}</p>
                      )}

                      {/* Where these came from. Six generic skills look
                          the same whether the study found nothing
                          specific or was never reachable to be asked,
                          and those are different things to be told. */}
                      <p className="muted small">
                        {study.tailored > 0
                          ? fill(tr("com.study.tailored", lang),
                                 { n: String(study.tailored) })
                          : tr("com.study.family", lang)}
                      </p>

                      <b className="small">{tr("com.study.skills", lang)}</b>
                      {study.skills.map((k, i) => (
                        <div key={k + i} className="com-line">
                          <span style={{ flex: 1 }}>{k}</span>
                          <button className="muted small"
                                  onClick={() => setStudy({
                                    ...study,
                                    skills: study.skills.filter(
                                      (_, j) => j !== i) })}>
                            {tr("com.study.drop", lang)}
                          </button>
                        </div>
                      ))}
                      <div className="com-add">
                        <input value={addSkill}
                               placeholder={tr("com.study.add", lang)}
                               onChange={(e) => setAddSkill(e.target.value)} />
                        <button disabled={!addSkill.trim()}
                                onClick={() => {
                                  setStudy({ ...study,
                                    skills: [...study.skills,
                                             addSkill.trim()] });
                                  setAddSkill("");
                                }}>
                          {tr("com.study.add", lang)}
                        </button>
                      </div>

                      <b className="small">{tr("com.study.conns", lang)}</b>
                      {study.connections.map((c, i) => (
                        <div key={c + i} className="com-line">
                          <span style={{ flex: 1 }}>{c}</span>
                          <button className="muted small"
                                  onClick={() => setStudy({
                                    ...study,
                                    connections: study.connections.filter(
                                      (_, j) => j !== i) })}>
                            {tr("com.study.drop", lang)}
                          </button>
                        </div>
                      ))}
                      <div className="com-add">
                        <input value={addConn}
                               placeholder={tr("com.study.add", lang)}
                               onChange={(e) => setAddConn(e.target.value)} />
                        <button disabled={!addConn.trim()}
                                onClick={() => {
                                  setStudy({ ...study,
                                    connections: [...study.connections,
                                                  addConn.trim()] });
                                  setAddConn("");
                                }}>
                          {tr("com.study.add", lang)}
                        </button>
                      </div>

                      <b className="small">
                        {tr("com.study.knowledge", lang)}
                      </b>
                      <p className="muted small com-study-text">
                        {study.knowledge}
                      </p>
                      {/* Who answered, by name, so a real study is
                          telling apart from the local fallback standing
                          in for one. */}
                      {study.studiedBy && (
                        <p className="muted small">
                          {tr("com.study.by", lang)}: {study.studiedBy}
                        </p>
                      )}

                      {/* Keeping the study is what opens the kit. The
                          founder has just read what the job needs;
                          that is the moment to decide what the person
                          doing it works with. */}
                      <button disabled={busy} data-go="keep"
                              onClick={act(async () => {
                                await api.keepStudy(open.id, s.id, {
                                  skills: study.skills,
                                  connections: study.connections,
                                }, token);
                                await startKit(s.id);
                              })}>
                        {tr("com.study.keep", lang)}
                      </button>
                    </div>
                  )}

                  {/* The kit, one rung at a time, and the ladder ends
                      at the signature. Every door here already worked;
                      what did not work was reaching them without
                      leaving the seat you were hiring for. */}
                  {kit?.seatId === s.id && (
                    <div className="com-kit" data-screen="217">
                      <ol className="com-rungs">
                        {RUNGS.map((r) => (
                          <li key={r}
                              className={r === rung ? "at"
                                : filled(kit, r) ? "done" : ""}>
                            {tr(`com.kit.${r}`, lang)}
                          </li>
                        ))}
                      </ol>

                      {/* Eyes: a screen this one stands on, and the
                          vocabulary says who walks past each kind
                          rather than leaving the founder to guess from
                          a word like "wall". */}
                      {rung === "eyes" && (
                        <div className="com-rung">
                          <p className="muted small">
                            {tr("com.kit.eyes.pitch", lang)}
                          </p>
                          <div className="com-add">
                            <select value={eyeKind}
                                    onChange={(e) =>
                                      setEyeKind(e.target.value)}>
                              {kinds.map((k) => (
                                <option key={k.kind} value={k.kind}>
                                  {k.kind}
                                </option>
                              ))}
                            </select>
                            <input value={eyeLabel}
                                   placeholder={
                                     tr("com.work.screen.label", lang)}
                                   onChange={(e) =>
                                     setEyeLabel(e.target.value)} />
                          </div>
                          <p className="muted small">
                            {kinds.find((k) => k.kind === eyeKind)?.means}
                          </p>
                          <div className="com-add">
                            <button disabled={!eyeLabel.trim()}
                                    onClick={() => {
                                      setKit({ ...kit, eyes: {
                                        kind: eyeKind,
                                        label: eyeLabel.trim() } });
                                      setRung("ears");
                                    }}>
                              {fill(tr("com.kit.next", lang),
                                    { next: tr("com.kit.ears", lang) })}
                            </button>
                            <button className="muted small"
                                    data-go="pass"
                                    onClick={() => setRung("ears")}>
                              {tr("com.kit.skip", lang)}
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Ears: two of the server's six embodiment kinds
                          — the two that hear. The other four are a
                          screen, a body, or "other", and offering them
                          here would 422 on the way out. */}
                      {rung === "ears" && (
                        <div className="com-rung">
                          <p className="muted small">
                            {tr("com.kit.ears.pitch", lang)}
                          </p>
                          <div className="com-add">
                            <select value={earKind}
                                    onChange={(e) =>
                                      setEarKind(e.target.value)}>
                              {["speaker", "earpiece"].map((k) => (
                                <option key={k} value={k}>{k}</option>
                              ))}
                            </select>
                            <input value={earName}
                                   placeholder={
                                     tr("com.kit.ears.name", lang)}
                                   onChange={(e) =>
                                     setEarName(e.target.value)} />
                          </div>
                          <div className="com-add">
                            <button disabled={!earName.trim()}
                                    onClick={() => {
                                      setKit({ ...kit, ears: {
                                        kind: earKind,
                                        name: earName.trim() } });
                                      setRung("hands");
                                    }}>
                              {fill(tr("com.kit.next", lang),
                                    { next: tr("com.kit.hands", lang) })}
                            </button>
                            <button className="muted small"
                                    data-go="pass"
                                    onClick={() => setRung("hands")}>
                              {tr("com.kit.skip", lang)}
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Hands: the same shelf the employee file
                          carries, choosing rather than binding —
                          there is nobody to bind to until the
                          signature. An announced machine renders
                          un-pickable rather than hidden, for the
                          reason qrme/robotics.py gives. */}
                      {rung === "hands" && (
                        <div className="com-rung">
                          <p className="muted small">
                            {tr("com.kit.hands.pitch", lang)}
                          </p>
                          <div className="com-scroll">
                          {shelf && Object.entries(shelf.by_maker).map(
                            ([maker, models]) => (
                            <div key={maker} className="com-shelf">
                              <span className="muted small">{maker}</span>
                              {models.map((m) => (
                                <span key={m.model} className="row">
                                  <b>{m.label}</b>
                                  <span className={
                                          "com-avail " + m.availability}>
                                    {tr(`com.avail.${m.availability}`,
                                        lang)}
                                  </span>
                                  <button className="muted small"
                                          disabled={!m.bindable}
                                          onClick={() => setKit({
                                            ...kit,
                                            hands: { model: m.model,
                                                     label: m.label } })}>
                                    {kit.hands?.model === m.model
                                      ? tr("com.kit.picked", lang)
                                      : tr("com.kit.pick", lang)}
                                  </button>
                                </span>
                              ))}
                            </div>
                          ))}
                          </div>
                          <div className="com-add">
                            <button disabled={!kit.hands}
                                    onClick={() => setRung("body")}>
                              {fill(tr("com.kit.next", lang),
                                    { next: tr("com.kit.body", lang) })}
                            </button>
                            <button className="muted small"
                                    data-go="pass"
                                    onClick={() => setRung("body")}>
                              {tr("com.kit.skip", lang)}
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Body: a face off the registry, or a sentence
                          the forge paints one from. The shelf can be
                          empty on a fresh deployment, which is why the
                          words are not the fallback but the other
                          half of the rung. */}
                      {rung === "body" && (
                        <div className="com-rung">
                          <p className="muted small">
                            {tr("com.kit.body.pitch", lang)}
                          </p>
                          <div className="com-scroll">
                          {faces.map((f) => (
                            <div key={f.id} className="com-line">
                              <span>{f.label || f.provider}</span>
                              <button className="muted small"
                                      onClick={() => setKit({
                                        ...kit, painted: "",
                                        face: { id: f.id,
                                                label: f.label
                                                  || f.provider } })}>
                                {kit.face?.id === f.id
                                  ? tr("com.kit.picked", lang)
                                  : tr("com.kit.pick", lang)}
                              </button>
                            </div>
                          ))}
                          </div>
                          <div className="com-add">
                            <input value={kit.painted}
                                   placeholder={
                                     tr("com.kit.body.words", lang)}
                                   onChange={(e) => setKit({
                                     ...kit, face: null,
                                     painted: e.target.value })} />
                          </div>
                          {/* The last rung is the signature. This is
                              the whole point of the ladder: the
                              founder never leaves the seat, and the
                              walk ends with somebody sitting in it. */}
                          <button disabled={busy}
                                  onClick={act(async () => {
                                    await signAndSeat(open.id, s.id,
                                                      interview.rows);
                                  })}>
                            {tr("com.kit.seat", lang)}
                          </button>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Signing is hiring. It waits for the study now: a
                      seat signed before anybody read what the job needs
                      is the thing this whole step exists to stop. While
                      the ladder is open the signature lives on its last
                      rung instead, so there is one of this button and
                      never two. */}
                  {kit?.seatId !== s.id && (
                    <button disabled={busy || study?.seatId !== s.id}
                            onClick={act(async () => {
                              await signAndSeat(open.id, s.id,
                                                interview.rows);
                            })}>
                      {tr("com.sign", lang)}
                    </button>
                  )}
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
