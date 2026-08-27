import { useEffect, useState } from "react";
import { api, type Exchange, type ExchangeVocabulary } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * The agreement two people sign before work changes hands.
 *
 * Ten routes, no caller. The whole module existed — propose, list what
 * crosses, sign, open the channel, accept item by item — and there was no way
 * to reach any of it from the console.
 *
 * The screen is arranged around the rule the backend turns on: **any change to
 * the manifest voids both signatures.** That rule is only worth anything if a
 * person can see it happen, so every call here re-renders the whole agreement
 * from the reply rather than patching what was already on screen. Add an item
 * to a signed exchange and the state falls back to `draft` and both signatures
 * vanish — visibly, in front of you, which is the point. A screen that
 * optimistically appended a row would show a signed agreement that the server
 * had already un-signed.
 *
 * Two more things are shown rather than paraphrased:
 *
 * - `runs_warning`, the server's own sentence about an item that executes. It
 *   appears next to the signing button, not buried in the manifest, because
 *   the moment to read it is before you agree rather than after;
 * - `does_not_grant`, which states that an exchange opens no session and
 *   reaches nothing unlisted. People asked to sign something want to know what
 *   they are *not* signing, and the backend answers that in its own words.
 */
export function Exchanges({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.interactorId || "";
  const token = session.interactorToken || "";

  const [vocab, setVocab] = useState<ExchangeVocabulary | null>(null);
  const [mine, setMine] = useState<Exchange[]>([]);
  const [open, setOpen] = useState<Exchange | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [note, setNote] = useState<string | null>(null);

  // A new proposal.
  const [guest, setGuest] = useState("");
  const [work, setWork] = useState("");
  const [industry, setIndustry] = useState("software");
  const [fee, setFee] = useState("0");

  // A new line on the manifest.
  const [itemName, setItemName] = useState("");
  const [itemKind, setItemKind] = useState("document");
  const [direction, setDirection] = useState("host_to_guest");

  const fail = (e: unknown) => setError(e);

  useEffect(() => { api.exchangeVocabulary().then(setVocab).catch(fail); }, []);

  useEffect(() => {
    if (!me || !token) return;
    api.myExchanges(me, token).then((r) => setMine(r.exchanges)).catch(fail);
  }, [me, token]);

  // One place to land every reply, because every one of these routes returns
  // the whole agreement and the whole agreement is what may have changed.
  function landed(x: Exchange, said?: string) {
    setOpen(x);
    setMine((rows) => rows.map((r) => (r.id === x.id ? x : r)));
    setError(null);
    if (said) setNote(said);
  }

  async function propose() {
    setError(null); setNote(null);
    try {
      const x = await api.proposeExchange({
        host_id: me, guest_id: guest.trim(), work: work.trim(),
        industry, fee: Number(fee) || 0,
      }, token);
      setMine((rows) => [x, ...rows]);
      landed(x, tr("exc.opened.said", lang));
      setWork("");
    } catch (e) { fail(e); }
  }

  async function addItem() {
    if (!open) return;
    setError(null); setNote(null);
    try {
      const before = open.signatures.length;
      const x = await api.addExchangeItem(open.id, {
        direction, name: itemName.trim(), kind: itemKind,
      }, token);
      landed(x, before > 0 && x.signatures.length === 0
        ? tr("exc.cleared.said", lang) : undefined);
      setItemName("");
    } catch (e) { fail(e); }
  }

  const act = (fn: () => Promise<Exchange>, said?: string) => async () => {
    setError(null); setNote(null);
    try { landed(await fn(), said); } catch (e) { fail(e); }
  };

  const iAmHost = open ? open.host_id === me : false;
  const mySide = iAmHost ? "host_to_guest" : "guest_to_host";
  const iSigned = open ? !open.unsigned.includes(me) : false;

  return (
    <div className="screen">
      <h2>{tr("exc.title", lang)}</h2>
      <p className="muted small">{tr("exc.lead", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {vocab && (
        <div className="card">
          <h3>{tr("exc.how", lang)}</h3>
          {/* The backend's own five rules. Quoted, because a paraphrase here
              could drift from what the code actually enforces. */}
          <ul className="small">
            {vocab.rules.map((r) => <li key={r}>{r}</li>)}
          </ul>
        </div>
      )}

      <div className="card">
        <h3>{tr("exc.propose", lang)}</h3>
        <div className="row">
          <input value={guest} onChange={(e) => setGuest(e.target.value)}
                 placeholder={tr("exc.guest.ph", lang)} />
          <select value={industry} onChange={(e) => setIndustry(e.target.value)}>
            {vocab?.industries.map((i) => <option key={i} value={i}>{i}</option>)}
          </select>
          <input value={fee} onChange={(e) => setFee(e.target.value)}
                 style={{ width: 90 }} placeholder={tr("exc.fee.ph", lang)} />
        </div>
        <div className="row">
          <input value={work} onChange={(e) => setWork(e.target.value)}
                 style={{ flex: 1 }}
                 placeholder={tr("exc.work.ph", lang)} />
          <button disabled={!me || !token || !guest.trim() || !work.trim()}
                  onClick={propose}>{tr("exc.propose.go", lang)}</button>
        </div>
      </div>

      <div className="card">
        <h3>{tr("exc.yours", lang)}</h3>
        {mine.length === 0 &&
          <p className="muted small">{tr("exc.none", lang)}</p>}
        {mine.map((x) => (
          <div key={x.id} className="row">
            <div style={{ flex: 1 }}>
              <strong>{x.work}</strong>
              <div className="muted small">
                {fill(tr("exc.row", lang), {
                  ind: x.industry, state: x.state, n: x.deal_items.length,
                  s: x.deal_items.length === 1 ? "" : "s",
                })}
                {x.unsigned.length > 0 && <>{" "}
                  {fill(tr("exc.row.tosign", lang), { n: x.unsigned.length })}
                </>}
              </div>
            </div>
            <button onClick={() => setOpen(x)}>{tr("exc.open", lang)}</button>
          </div>
        ))}
      </div>

      {open && (
        <>
          <div className="card">
            <h3>{open.work}</h3>
            <p className="muted small">
              {fill(tr("exc.detail", lang), {
                ind: open.industry, state: open.state,
                fee: open.fee.toFixed(2), note: open.fee_note,
              })}
            </p>
            {open.includes.length > 0 && (
              <p className="small">{fill(tr("exc.included", lang),
                { list: open.includes.join(", ") })}</p>
            )}
            {/* Stated because an absent exclusion reads as an inclusion to
                whoever paid. */}
            {open.excludes.length > 0 && (
              <p className="small">{fill(tr("exc.notincluded", lang),
                { list: open.excludes.join(", ") })}</p>
            )}
            <p className="muted small">
              {fill(tr("exc.grants", lang),
                { a: open.grants, b: open.does_not_grant })}
            </p>
          </div>

          <div className="card">
            <h3>{tr("exc.manifest", lang)}</h3>
            {open.deal_items.length === 0 && (
              <p className="muted small">{tr("exc.manifest.none", lang)}</p>
            )}
            {open.deal_items.map((it) => (
              <div key={it.id} className="row">
                <div style={{ flex: 1 }}>
                  <strong>{it.name}</strong>
                  {it.runs &&
                    <span className="chip"> {tr("exc.runs", lang)}</span>}
                  <div className="muted small">
                    {fill(tr("exc.item.line", lang), {
                      dir: it.direction === "host_to_guest"
                        ? tr("exc.h2g", lang) : tr("exc.g2h", lang),
                      kind: it.kind,
                    })}
                    {it.bytes > 0 && <>{" "}
                      {fill(tr("exc.item.bytes", lang), { n: it.bytes })}</>}
                    {it.accepted_at &&
                      <> {tr("exc.item.accepted", lang)}</>}
                  </div>
                </div>
                {/* Accepting is the receiving side's own act, one item at a
                    time — consent to an agreement is not consent to a file
                    landing on your disk. */}
                {!it.accepted_at && it.direction !== mySide && (
                  <button
                    disabled={!open.channel.open}
                    onClick={act(() => api.acceptExchangeItem(open.id, it.id, me, token),
                                 tr("exc.accepted.said", lang))}>
                    {tr("exc.accept", lang)}
                  </button>
                )}
                {open.state === "draft" && (
                  <button onClick={act(
                    () => api.removeExchangeItem(open.id, it.id, token))}>
                    {tr("exc.remove", lang)}
                  </button>
                )}
              </div>
            ))}

            {open.state === "draft" && (
              <div className="row">
                <input value={itemName} onChange={(e) => setItemName(e.target.value)}
                       placeholder={tr("exc.item.ph", lang)} style={{ flex: 1 }} />
                <select value={itemKind}
                        onChange={(e) => setItemKind(e.target.value)}>
                  {vocab?.kinds.map((k) => (
                    <option key={k.key} value={k.key}>{k.key}</option>
                  ))}
                </select>
                <select value={direction}
                        onChange={(e) => setDirection(e.target.value)}>
                  <option value="host_to_guest">{tr("exc.h2g", lang)}</option>
                  <option value="guest_to_host">{tr("exc.g2h", lang)}</option>
                </select>
                <button disabled={!itemName.trim()} onClick={addItem}>
                  {tr("exc.add", lang)}
                </button>
              </div>
            )}
            {/* The chosen kind's own meaning, including whether it runs. */}
            {vocab && open.state === "draft" && (
              <p className="muted small">
                {vocab.kinds.find((k) => k.key === itemKind)?.means}
              </p>
            )}
          </div>

          <div className="card">
            <h3>{tr("exc.sigs", lang)}</h3>
            <p className="muted small">
              {fill(tr("exc.sigs.against", lang),
                { fp: <code>{open.fingerprint.slice(0, 16)}…</code> })}
            </p>
            {open.signatures.map((s) => (
              <p key={s.party_id} className="small">
                {fill(tr("exc.sig.line", lang), {
                  who: s.party_id === me ? tr("exc.you", lang) : s.party_id,
                  when: s.signed_at,
                })}
                {/* The server's own verdict on whether that signature still
                    applies, rather than this screen comparing hashes and
                    hoping it got it right. */}
                {!s.matches_current && (
                  <strong> {tr("exc.sig.stale", lang)}</strong>
                )}
              </p>
            ))}
            {open.unsigned.length > 0 && (
              <p className="muted small">
                {fill(tr("exc.waiting", lang), {
                  who: open.unsigned
                    .map((p) => p === me ? tr("exc.you", lang) : p)
                    .join(", "),
                })}
              </p>
            )}

            {/* Next to the button, not buried in the manifest: the moment to
                read this is before agreeing. */}
            {open.runs_warning && (
              <div className="card error">
                <p className="small">
                  <strong>{open.runs_on_your_machine.join(", ")}</strong> —{" "}
                  {open.runs_warning}
                </p>
              </div>
            )}

            <div className="row">
              <button disabled={iSigned || open.state === "withdrawn"}
                      onClick={act(() => api.signExchange(open.id, me, token),
                                   tr("exc.signed.said", lang))}>
                {tr("exc.sign", lang)}
              </button>
              <button onClick={act(() => api.reopenExchange(open.id, me, token),
                                   tr("exc.reopened.said", lang))}>
                {tr("exc.reopen", lang)}
              </button>
              <button onClick={act(() => api.withdrawExchange(open.id, me, token),
                                   tr("exc.withdrawn.said", lang))}>
                {tr("exc.withdraw", lang)}
              </button>
            </div>
          </div>

          <div className="card">
            <h3>{tr("exc.move", lang)}</h3>
            {/* Two shapes, and the difference is the whole feature. */}
            {open.channel.open ? (
              <>
                <p className="small">{fill(tr("exc.move.yes", lang), {
                  n: open.channel.deal_items.length,
                  s: open.channel.deal_items.length === 1 ? "" : "s",
                })}</p>
                <p className="muted small">{open.channel.note}</p>
              </>
            ) : (
              <>
                <p className="small">{fill(tr("exc.move.no", lang),
                  { reason: open.channel.reason })}</p>
                <p className="muted small">
                  {fill(tr("exc.unsigned", lang), {
                    who: open.channel.unsigned
                      .map((p) => p === me ? tr("exc.you", lang) : p)
                      .join(", "),
                  })}
                </p>
              </>
            )}
            <button onClick={async () => {
              setError(null);
              try {
                const c = await api.exchangeChannel(open.id, token);
                setNote(c.open ? c.note : c.reason);
              } catch (e) { fail(e); }
            }}>{tr("exc.askagain", lang)}</button>
          </div>
        </>
      )}
    </div>
  );
}
