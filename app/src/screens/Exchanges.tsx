import { useEffect, useState } from "react";
import { api, type Exchange, type ExchangeVocabulary } from "../api";
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
      landed(x, "Draft opened. Nothing can move until both of you sign.");
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
        ? "The manifest changed, so both signatures were cleared. Sign again."
        : undefined);
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
      <h2>Exchanges</h2>
      <p className="muted small">
        A document before it is a transfer. Both sides sign the same manifest,
        and only then does anything move.
      </p>

      <Refusal error={error} onPlans={onPlans} />
      {note && <div className="card"><p className="small">{note}</p></div>}

      {vocab && (
        <div className="card">
          <h3>How this works</h3>
          {/* The backend's own five rules. Quoted, because a paraphrase here
              could drift from what the code actually enforces. */}
          <ul className="small">
            {vocab.rules.map((r) => <li key={r}>{r}</li>)}
          </ul>
        </div>
      )}

      <div className="card">
        <h3>Propose one</h3>
        <div className="row">
          <input value={guest} onChange={(e) => setGuest(e.target.value)}
                 placeholder="the other party's id" />
          <select value={industry} onChange={(e) => setIndustry(e.target.value)}>
            {vocab?.industries.map((i) => <option key={i} value={i}>{i}</option>)}
          </select>
          <input value={fee} onChange={(e) => setFee(e.target.value)}
                 style={{ width: 90 }} placeholder="fee" />
        </div>
        <div className="row">
          <input value={work} onChange={(e) => setWork(e.target.value)}
                 style={{ flex: 1 }}
                 placeholder="what the work is, in one sentence" />
          <button disabled={!me || !token || !guest.trim() || !work.trim()}
                  onClick={propose}>Propose</button>
        </div>
      </div>

      <div className="card">
        <h3>Yours</h3>
        {mine.length === 0 && <p className="muted small">Nothing yet.</p>}
        {mine.map((x) => (
          <div key={x.id} className="row">
            <div style={{ flex: 1 }}>
              <strong>{x.work}</strong>
              <div className="muted small">
                {x.industry} · {x.state} · {x.items.length} item
                {x.items.length === 1 ? "" : "s"}
                {x.unsigned.length > 0 && <> · {x.unsigned.length} still to sign</>}
              </div>
            </div>
            <button onClick={() => setOpen(x)}>Open</button>
          </div>
        ))}
      </div>

      {open && (
        <>
          <div className="card">
            <h3>{open.work}</h3>
            <p className="muted small">
              {open.industry} · {open.state} · fee {open.fee.toFixed(2)} —{" "}
              {open.fee_note}
            </p>
            {open.includes.length > 0 && (
              <p className="small">Included: {open.includes.join(", ")}</p>
            )}
            {/* Stated because an absent exclusion reads as an inclusion to
                whoever paid. */}
            {open.excludes.length > 0 && (
              <p className="small">Not included: {open.excludes.join(", ")}</p>
            )}
            <p className="muted small">
              This grants {open.grants}. It does not grant {open.does_not_grant}.
            </p>
          </div>

          <div className="card">
            <h3>The manifest</h3>
            {open.items.length === 0 && (
              <p className="muted small">Nothing listed yet.</p>
            )}
            {open.items.map((it) => (
              <div key={it.id} className="row">
                <div style={{ flex: 1 }}>
                  <strong>{it.name}</strong>
                  {it.runs && <span className="chip"> runs</span>}
                  <div className="muted small">
                    {it.direction === "host_to_guest" ? "host → guest" : "guest → host"}
                    {" · "}{it.kind}{it.bytes > 0 && <> · {it.bytes} bytes</>}
                    {it.accepted_at && <> · accepted</>}
                  </div>
                </div>
                {/* Accepting is the receiving side's own act, one item at a
                    time — consent to an agreement is not consent to a file
                    landing on your disk. */}
                {!it.accepted_at && it.direction !== mySide && (
                  <button
                    disabled={!open.channel.open}
                    onClick={act(() => api.acceptExchangeItem(open.id, it.id, me, token),
                                 "Accepted. That one item, and nothing else.")}>
                    Accept
                  </button>
                )}
                {open.state === "draft" && (
                  <button onClick={act(
                    () => api.removeExchangeItem(open.id, it.id, token))}>
                    Remove
                  </button>
                )}
              </div>
            ))}

            {open.state === "draft" && (
              <div className="row">
                <input value={itemName} onChange={(e) => setItemName(e.target.value)}
                       placeholder="what crosses" style={{ flex: 1 }} />
                <select value={itemKind}
                        onChange={(e) => setItemKind(e.target.value)}>
                  {vocab?.kinds.map((k) => (
                    <option key={k.key} value={k.key}>{k.key}</option>
                  ))}
                </select>
                <select value={direction}
                        onChange={(e) => setDirection(e.target.value)}>
                  <option value="host_to_guest">host → guest</option>
                  <option value="guest_to_host">guest → host</option>
                </select>
                <button disabled={!itemName.trim()} onClick={addItem}>Add</button>
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
            <h3>Signatures</h3>
            <p className="muted small">
              Against fingerprint <code>{open.fingerprint.slice(0, 16)}…</code> —
              change the manifest and this changes, so the old signatures match
              nothing.
            </p>
            {open.signatures.map((s) => (
              <p key={s.party_id} className="small">
                {s.party_id === me ? "you" : s.party_id} signed {s.signed_at}
                {/* The server's own verdict on whether that signature still
                    applies, rather than this screen comparing hashes and
                    hoping it got it right. */}
                {!s.matches_current && (
                  <strong> — against an older manifest, not this one</strong>
                )}
              </p>
            ))}
            {open.unsigned.length > 0 && (
              <p className="muted small">
                Waiting on: {open.unsigned.map((p) => p === me ? "you" : p).join(", ")}
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
                                   "Signed — this manifest, and nothing it becomes later.")}>
                Sign
              </button>
              <button onClick={act(() => api.reopenExchange(open.id, me, token),
                                   "Reopened. Both signatures cleared.")}>
                Reopen to edit
              </button>
              <button onClick={act(() => api.withdrawExchange(open.id, me, token),
                                   "Withdrawn.")}>
                Withdraw
              </button>
            </div>
          </div>

          <div className="card">
            <h3>Can anything move?</h3>
            {/* Two shapes, and the difference is the whole feature. */}
            {open.channel.open ? (
              <>
                <p className="small">Yes — {open.channel.items.length} item
                  {open.channel.items.length === 1 ? "" : "s"} available.</p>
                <p className="muted small">{open.channel.note}</p>
              </>
            ) : (
              <>
                <p className="small">No — {open.channel.reason}.</p>
                <p className="muted small">
                  Unsigned: {open.channel.unsigned
                    .map((p) => p === me ? "you" : p).join(", ")}
                </p>
              </>
            )}
            <button onClick={async () => {
              setError(null);
              try {
                const c = await api.exchangeChannel(open.id, token);
                setNote(c.open ? c.note : c.reason);
              } catch (e) { fail(e); }
            }}>Ask again</button>
          </div>
        </>
      )}
    </div>
  );
}
