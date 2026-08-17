import { useEffect, useState } from "react";
import { api, type Privilege } from "../api";
import { t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * What the agent may do, one row at a time.
 *
 * The product grew powers faster than it grew a place to see them. A profile
 * could go and study the open web, put a question to strangers, package a
 * history for a professional, run a job over vaulted material and reach
 * emergency services — and the only way to find out was to meet one
 * mid-conversation, or read a changelog.
 *
 * ## Two people read this screen
 *
 * The **owner** reads it to decide, and is the only one who can change it. A
 * **visitor** reads the same list to find out what this profile can actually
 * do for them, which is the half that was missing: somebody wondering whether
 * this one can hand their matter to a real professional should be able to
 * look instead of hoping it is offered.
 *
 * So the switches only appear with an owner token. Without one the rows are
 * still all here, off ones included — a roster that hides what has not been
 * chosen is a roster nobody can read anything from.
 *
 * ## What each row says
 *
 * *What it keeps* is the half these lists usually omit, and it is printed
 * beside every row rather than behind a link: "summarise your meetings" and
 * "summarise your meetings, and keep the recording" are different agreements.
 * The ones marked as reaching somebody who never chose this are marked on the
 * row, because that is the property that decides whether it may ever be on by
 * default — and none of them are.
 *
 * The sentences come from the server already in the reader's language; this
 * screen translates its own chrome and nothing else.
 */
export function Allowed() {
  const { session } = useSession();
  const lang = visitorLang();
  const me = session.profileId || "";
  const ownerToken = session.ownerToken || "";

  const [rows, setRows] = useState<Privilege[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState("");

  useEffect(() => {
    if (!me) return;
    api.privileges(me, ownerToken || undefined)
       .then(setRows).catch(setError);
  }, [me, ownerToken]);

  async function decide(name: string, on: boolean) {
    setError(null);
    setBusy(name);
    try {
      setRows(await api.allowPrivilege(me, name, on, ownerToken));
    } catch (e) {
      setError(e);
    } finally {
      setBusy("");
    }
  }

  return (
    <div className="screen">
      <h2>{tr("may.title", lang)}</h2>
      <p className="muted">{tr("may.lead", lang)}</p>
      <Refusal error={error} />
      {!ownerToken && <p className="small muted">{tr("may.visitor", lang)}</p>}

      {rows.map((row) => (
        <div className="card" key={row.name}>
          <h3>{row.may_do}</h3>
          <p className="small">
            <strong>{tr("may.keeps", lang)}</strong>{" "}
            {row.holds || tr("may.keeps.nothing", lang)}
          </p>
          {row.needs.length > 0 && (
            <p className="muted small">
              {tr("may.needs", lang)} {row.needs.join(" · ")}
            </p>
          )}
          {row.touches_others && (
            <p className="small"><strong>{tr("may.others", lang)}</strong></p>
          )}
          {/* Why a row is on before anybody touched it. Shown only where it
              applies: a reason printed under every row is a reason nobody
              reads under the one that needed it. */}
          {row.by_default && row.why && (
            <p className="muted small">{row.why}</p>
          )}
          <p className="small">
            {row.chosen ? tr("may.on", lang) : tr("may.off", lang)}
          </p>
          {ownerToken && (
            <button disabled={busy === row.name}
                    onClick={() => decide(row.name, !row.chosen)}>
              {row.chosen ? tr("may.turnoff", lang) : tr("may.turnon", lang)}
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
