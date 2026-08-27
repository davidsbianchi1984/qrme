import { useEffect, useState } from "react";
import { api, CampaignOut, DesigneeOut } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
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

export function Campaigns({ onPlans }: {
  /** Where a plan refusal sends somebody. Threaded in from the shell
   *  rather than looked up here, so the tab id stays in one place. */
  onPlans: () => void;
}) {
  const { session } = useSession();
  const lang = visitorLang();
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
  const [error, setError] = useState<unknown>(null);

  function load() {
    if (!session.profileId) return;
    api.getProceeds(session.profileId)
      .then((p) => setProceeds(p.proceeds_to)).catch(() => setProceeds([]));
    api.listCampaigns(session.profileId)
      .then(setCampaignsList).catch(() => setCampaignsList([]));
  }
  useEffect(load, [session.profileId]);

  if (!session.profileId || !session.ownerToken) {
    return <div className="screen"><p className="muted center">{tr("cmp.signin", lang)}</p></div>;
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
    } catch (e) { setError(e); }
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
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  async function donate(campaignId: string) {
    const amount = Number(give[campaignId] || 0);
    setBusy(true); setError(null); setNote(null);
    try {
      const out = await api.donate(campaignId, {
        amount, giver_id: session.interactorId || undefined,
      });
      setNote(tr("cmp.split", lang) + " "
        + out.split.map((s) => `${s.name} $${s.amount.toFixed(2)}`).join(" · "));
      load();
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("cmp.title", lang)}</h2>
        <span className="muted small">{tr("cmp.pitch", lang)}</span>
      </header>

      <div className="card">
        <h3>{tr("cmp.proceeds", lang)}</h3>
        {!editing && proceeds.length === 0 && (
          <p className="muted small">{tr("cmp.nobody", lang)}</p>
        )}
        {!editing && proceeds.map((p) => (
          <div key={p.id} className="friend-row">
            <span className="tag">{p.share}%</span>
            <b>{p.name}</b>
            <span className="muted small">
              {p.kind === "loved_one" ? tr("cmp.lovedone", lang) : tr("cmp.organization", lang)}
            </span>
          </div>
        ))}
        {editing && (
          <>
            {drafts.map((d, i) => (
              <div key={i} className="row">
                <label>{tr("cmp.name", lang)}<input value={d.name}
                  onChange={(e) => setDrafts((x) => x.map((y, j) => j === i ? { ...y, name: e.target.value } : y))} /></label>
                <label>{tr("cmp.kind", lang)}
                  <select value={d.kind}
                    onChange={(e) => setDrafts((x) => x.map((y, j) => j === i ? { ...y, kind: e.target.value as DesigneeDraft["kind"] } : y))}>
                    <option value="loved_one">{tr("cmp.lovedone", lang)}</option>
                    <option value="organization">{tr("cmp.organization", lang)}</option>
                  </select>
                </label>
                <label>{tr("cmp.share", lang)}<input type="number" min={1} max={100} value={d.share} style={{ width: 64 }}
                  onChange={(e) => setDrafts((x) => x.map((y, j) => j === i ? { ...y, share: Number(e.target.value) || 0 } : y))} /></label>
              </div>
            ))}
            <div className="row">
              <button onClick={() => setDrafts((d) => [...d, { name: "", kind: "loved_one", share: 0 }])}>
                {tr("cmp.add", lang)}
              </button>
              <span className={"tag" + (totalShare === 100 ? "" : " rated")}>
                {fill(tr("cmp.of100", lang), { n: totalShare })}
              </span>
              <button className="primary" disabled={busy || totalShare !== 100} onClick={saveProceeds}>
                {tr("cmp.save", lang)}
              </button>
            </div>
          </>
        )}
        {!editing && (
          <button onClick={() => {
            setDrafts(proceeds.length
              ? proceeds.map((p) => ({ name: p.name, kind: p.kind as DesigneeDraft["kind"], share: p.share }))
              : drafts);
            setEditing(true);
          }}>{tr("cmp.editdesig", lang)}</button>
        )}
      </div>

      <div className="card">
        <h3>{tr("cmp.opencamp", lang)}</h3>
        <div className="row">
          <label>{tr("cmp.titlelabel", lang)}<input value={title} placeholder={tr("cmp.title.ph", lang)}
                             onChange={(e) => setTitle(e.target.value)} /></label>
          <label>{tr("cmp.goal", lang)}<input type="number" min={1} value={goal} style={{ width: 90 }}
                              onChange={(e) => setGoal(e.target.value)} /></label>
          <label>{tr("cmp.cause", lang)}<input value={cause} placeholder={tr("cmp.cause.ph", lang)}
                             onChange={(e) => setCause(e.target.value)} /></label>
          <button className="primary" disabled={busy || !title.trim()} onClick={createCampaign}>
            {tr("cmp.open", lang)}
          </button>
        </div>
      </div>

      {campaignsList.map((c) => (
        <div key={c.id} className="card">
          <h3>{c.title} {c.status === "closed" && <span className="tag">{tr("cmp.closed", lang)}</span>}</h3>
          {c.cause && <p className="muted small">{c.cause}</p>}
          {/* One sentence, not four fragments: a raised-of-goal line reads
              backwards in Japanese and Chinese, and the donor count is a
              separate string because most languages inflect it. */}
          <p>
            {fill(tr("cmp.raised", lang), {
              raised: <b>${c.raised.toFixed(2)}</b>,
              goal: `$${c.goal_amount.toFixed(2)}`,
            })}
            {" · "}
            {c.donors === 1
              ? fill(tr("cmp.donor", lang), { n: c.donors })
              : fill(tr("cmp.donors", lang), { n: c.donors })}
          </p>
          <p className="muted small">
            {fill(tr("cmp.goesto", lang), {
              names: c.proceeds_to.map((p) => `${p.name} (${p.share}%)`).join(" · "),
            })}
          </p>
          {c.status === "open" && (
            <div className="row">
              <label>{tr("cmp.give", lang)}<input type="number" min={1} value={give[c.id] || ""} style={{ width: 90 }}
                                  onChange={(e) => setGive((g) => ({ ...g, [c.id]: e.target.value }))} /></label>
              <button className="primary" disabled={busy} onClick={() => donate(c.id)}>
                {tr("cmp.donate", lang)}
              </button>
              <button disabled={busy}
                      onClick={() => api.closeCampaign(c.id, session.ownerToken!).then(load).catch((e) => setError(e))}>
                {tr("cmp.close", lang)}
              </button>
            </div>
          )}
        </div>
      ))}

      {note && <div className="muted small">{note}</div>}
      <Refusal error={error} onPlans={onPlans} variant="inline" />
    </div>
  );
}
