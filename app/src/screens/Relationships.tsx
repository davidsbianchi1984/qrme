import { useEffect, useState } from "react";
import { api } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

export function Relationships({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [name, setName] = useState("");
  const [type, setType] = useState("friend");
  const [tone, setTone] = useState("warm");
  const [busy, setBusy] = useState(false);

  async function load() {
    if (!session.profileId) return;
    try {
      const t = await api.transparency(session.profileId);
      setCount(t.active_relationships);
    } catch (e) {
      setError(e);
    }
  }
  useEffect(() => {
    load();
  }, [session.profileId]);

  async function add() {
    if (!name.trim() || !session.profileId) return;
    setBusy(true);
    setError(null);
    try {
      const person = await api.createInteractor({ display_name: name.trim() });
      await api.setRelationship(session.profileId, person.id, {
        relationship_type: type,
        tone,
      }, session.ownerToken!);
      setName("");
      await load();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("rel.title", lang)}</h2>
        <span className="muted small">
          {fill(tr("rel.peoplein", lang),
                { name: session.profile?.display_name })}
        </span>
      </header>

      <div className="tile wide">
        <div className="tile-label">{tr("rel.active", lang)}</div>
        <div className="tile-value">{count ?? "—"}</div>
        <div className="tile-sub">
          {fill(tr("rel.acknowledges", lang),
                { name: session.profile?.display_name })}
        </div>
      </div>

      <Refusal error={error} onPlans={onPlans} variant="inline" />

      <div className="card">
        <h3>{tr("rel.add", lang)}</h3>
        <label>
          {tr("rel.name", lang)}
          <input value={name} onChange={(e) => setName(e.target.value)}
                 placeholder={tr("rel.name.ph", lang)} />
        </label>
        {/* The option carried no `value`, so its text was the value sent to
            the API. Translating the label alone would have posted the
            Spanish word as a relationship type. The enum moves to `value`
            and only the word somebody reads is looked up. */}
        <div className="row">
          <label>
            {tr("rel.type", lang)}
            <select value={type} onChange={(e) => setType(e.target.value)}>
              {["family", "grandchild", "friend", "romantic_partner",
                "professional", "fan", "stranger"].map((t) => (
                <option key={t} value={t}>{tr(`rel.t.${t}`, lang)}</option>
              ))}
            </select>
          </label>
          <label>
            {tr("rel.tone", lang)}
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              {["warm", "friendly", "professional", "playful", "direct"].map((t) => (
                <option key={t} value={t}>{tr(`rel.n.${t}`, lang)}</option>
              ))}
            </select>
          </label>
        </div>
        <button className="primary" onClick={add} disabled={busy}>
          {busy ? tr("rel.saving", lang) : tr("rel.save", lang)}
        </button>
      </div>
    </div>
  );
}
