import { useEffect, useState } from "react";
import { api } from "../api";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

export function Relationships({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
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
        <h2>Relationships</h2>
        <span className="muted small">people in {session.profile?.display_name}'s life</span>
      </header>

      <div className="tile wide">
        <div className="tile-label">Active relationships</div>
        <div className="tile-value">{count ?? "—"}</div>
        <div className="tile-sub">
          {session.profile?.display_name} acknowledges them truthfully if asked — disclosure by design
        </div>
      </div>

      <Refusal error={error} onPlans={onPlans} variant="inline" />

      <div className="card">
        <h3>Add a relationship</h3>
        <label>
          Name
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Sarah" />
        </label>
        <div className="row">
          <label>
            Type
            <select value={type} onChange={(e) => setType(e.target.value)}>
              {["family", "grandchild", "friend", "romantic_partner", "professional", "fan", "stranger"].map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </label>
          <label>
            Tone
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              {["warm", "friendly", "professional", "playful", "direct"].map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </label>
        </div>
        <button className="primary" onClick={add} disabled={busy}>
          {busy ? "Saving…" : "Save relationship"}
        </button>
      </div>
    </div>
  );
}
