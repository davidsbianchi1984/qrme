import { useEffect, useState } from "react";
import { api, CampaignOut, DesigneeOut } from "../api";
import { useSession } from "../store";

// Crowdfunding with proceeds routed where the user said (spec [0020],
// example two). Two honesty rules shape the screen: the designation is
// edited before any campaign can exist, and every campaign card shows the
// names the money goes to — a donor gives to people, not to a platform.
interface DesigneeDraft {
  name: string;
  kind: "loved_one" | "organization";
  share: number;
}

export function Campaigns() {
  const { session } = useSession();
  const [proceeds, setProceeds] = useState<DesigneeOut[]>([]);
  const [drafts, setDrafts] = useState<DesigneeDraft[]>([
    { name: "", kind: "loved_one", share: 100 },
  ]);
  const [editing, setEditing] = useState(false);
  const [campaignsList, setCampaignsList] = useState<CampaignOut[]>([]);
  const [title, setTitle] = useState("");
  const [goal, setGoal] = useState("500");
  const [cause, setCause] = useState("");
  const [give, setGive] = useState<Record<string, string>>({});
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function load() {
    if (!session.profileId) return;
    api.getProceeds(session.profileId)
      .then((p) => setProceeds(p.proceeds_to)).catch(() => setProceeds([]));
    api.listCampaigns(session.profileId)
      .then(setCampaignsList).catch(() => setCampaignsList([]));
  }
  useEffect(load, [session.profileId]);

  if (!session.profileId || !session.ownerToken) {
    return <div className="screen"><p className="muted center">Sign in first.</p></div>;
  }

  const totalShare = drafts.reduce((s, d) => s + (d.share || 0), 0);

  async function saveProceeds() {
    setBusy(true); setError(null);
    try {
      const saved = await api.setProceeds(
        session.profileId!,
        drafts.filter((d) => d.name.trim()).map((d) => ({
          name: d.name.trim(), kind: d.kind, share: d.share,
        })),
        session.ownerToken!,
      );
      setProceeds(saved.proceeds_to);
      setEditing(false);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function createCampaign() {
    setBusy(true); setError(null);
    try {
      await api.createCampaign(session.profileId!, {
        title: title.trim(), goal: Number(goal) || 0,
        cause: cause.trim() || undefined,
      }, session.ownerToken!);
      setTitle(""); setCause(""); load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  async function donate(campaignId: string) {
    const amount = Number(give[campaignId] || 0);
    setBusy(true); setError(null); setNote(null);
    try {
      const out = await api.donate(campaignId, {
        amount, giver_id: session.interactorId || undefined,
      });
      setNote("Split: " + out.split.map((s) => `${s.name} $${s.amount.toFixed(2)}`).join(" · "));
      load();
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>Where the Money Goes</h2>
        <span className="muted small">crowdfunding, routed by you — donors always see the names</span>
      </header>

      <div className="card">
        <h3>Proceeds go to</h3>
        {!editing && proceeds.length === 0 && (
          <p className="muted small">
            Nobody designated yet — a campaign cannot exist until you say
            where its money goes.
          </p>
        )}
        {!editing && proceeds.map((p) => (
          <div key={p.id} className="friend-row">
            <span className="tag">{p.share}%</span>
            <b>{p.name}</b>
            <span className="muted small">{p.kind === "loved_one" ? "loved one" : "organization"}</span>
          </div>
        ))}
        {editing && (
          <>
            {drafts.map((d, i) => (
              <div key={i} className="row">
                <label>Name<input value={d.name}
                  onChange={(e) => setDrafts((x) => x.map((y, j) => j === i ? { ...y, name: e.target.value } : y))} /></label>
                <label>Kind
                  <select value={d.kind}
                    onChange={(e) => setDrafts((x) => x.map((y, j) => j === i ? { ...y, kind: e.target.value as DesigneeDraft["kind"] } : y))}>
                    <option value="loved_one">loved one</option>
                    <option value="organization">organization</option>
                  </select>
                </label>
                <label>Share %<input type="number" min={1} max={100} value={d.share} style={{ width: 64 }}
                  onChange={(e) => setDrafts((x) => x.map((y, j) => j === i ? { ...y, share: Number(e.target.value) || 0 } : y))} /></label>
              </div>
            ))}
            <div className="row">
              <button onClick={() => setDrafts((d) => [...d, { name: "", kind: "loved_one", share: 0 }])}>+ Add</button>
              <span className={"tag" + (totalShare === 100 ? "" : " rated")}>{totalShare}% of 100</span>
              <button className="primary" disabled={busy || totalShare !== 100} onClick={saveProceeds}>Save</button>
            </div>
          </>
        )}
        {!editing && (
          <button onClick={() => {
            setDrafts(proceeds.length
              ? proceeds.map((p) => ({ name: p.name, kind: p.kind as DesigneeDraft["kind"], share: p.share }))
              : drafts);
            setEditing(true);
          }}>Edit designation</button>
        )}
      </div>

      <div className="card">
        <h3>Open a campaign</h3>
        <div className="row">
          <label>Title<input value={title} placeholder="Keep the garden going"
                             onChange={(e) => setTitle(e.target.value)} /></label>
          <label>Goal $<input type="number" min={1} value={goal} style={{ width: 90 }}
                              onChange={(e) => setGoal(e.target.value)} /></label>
          <label>Cause<input value={cause} placeholder="what it's for"
                             onChange={(e) => setCause(e.target.value)} /></label>
          <button className="primary" disabled={busy || !title.trim()} onClick={createCampaign}>Open</button>
        </div>
      </div>

      {campaignsList.map((c) => (
        <div key={c.id} className="card">
          <h3>{c.title} {c.status === "closed" && <span className="tag">closed</span>}</h3>
          {c.cause && <p className="muted small">{c.cause}</p>}
          <p><b>${c.raised.toFixed(2)}</b> of ${c.goal.toFixed(2)} · {c.donors} donor{c.donors === 1 ? "" : "s"}</p>
          <p className="muted small">
            goes to: {c.proceeds_to.map((p) => `${p.name} (${p.share}%)`).join(" · ")}
          </p>
          {c.status === "open" && (
            <div className="row">
              <label>Give $<input type="number" min={1} value={give[c.id] || ""} style={{ width: 90 }}
                                  onChange={(e) => setGive((g) => ({ ...g, [c.id]: e.target.value }))} /></label>
              <button className="primary" disabled={busy} onClick={() => donate(c.id)}>Donate</button>
              <button disabled={busy}
                      onClick={() => api.closeCampaign(c.id, session.ownerToken!).then(load).catch((e) => setError((e as Error).message))}>
                Close
              </button>
            </div>
          )}
        </div>
      ))}

      {note && <div className="muted small">{note}</div>}
      {error && <div className="error">⚠ {error}</div>}
    </div>
  );
}
