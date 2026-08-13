import { useEffect, useState } from "react";
import { api, type CampaignOut, type Excursion, type LightLegend,
         type OrgOut, type PersonGrants, type PlaceGrants } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

/**
 * One named thing, and who may ask about it.
 *
 * Six reads that each answer about one particular thing, and they give six
 * different answers to *who is allowed* — each for a reason worth stating
 * rather than a default anybody inherited:
 *
 * | | who may ask |
 * |---|---|
 * | the light legend | anybody; it takes no id at all |
 * | a campaign | **anybody**, deliberately |
 * | an organization | signed in |
 * | an excursion | the profile's owner |
 * | somebody's lent skills | themselves |
 * | a place's lent skills | you, filtered to your own |
 *
 * The campaign is the interesting inversion: it is the **most public read in
 * the product**, and that is what makes it honest. It carries `proceeds_to`,
 * so the person about to give money can see exactly who receives it before
 * they do — a fundraising page that hid its split would be the ordinary kind
 * of dishonest. In the same spirit a campaign cannot exist until the
 * designation does: creating one before saying where the money goes is
 * refused with *say where the money goes first — designate loved ones or
 * organizations before asking anyone for it*.
 *
 * The place-grants read is narrower than its name suggests, and says so in a
 * `note` this screen renders verbatim. It was meant to answer "what can this
 * room see about itself", but there is no room-membership check to hang that
 * on, and without one it listed who is lending what to whom to anybody who
 * guessed an id. A short list here means *your* grants, not *no* grants, and
 * a screen that let somebody read it the other way would be misrepresenting
 * an access limit as an empty room.
 */
export function Named({ onPlans }: { onPlans: () => void }) {
  const { session } = useSession();
  const lang = visitorLang();
  const token = session.ownerToken || "";
  const myself = session.interactorId || "";
  const myToken = session.interactorToken || token;

  const [lights, setLights] = useState<LightLegend | null>(null);
  const [campaignId, setCampaignId] = useState("");
  const [campaign, setCampaign] = useState<CampaignOut | null>(null);
  const [orgId, setOrgId] = useState("");
  const [org, setOrg] = useState<OrgOut | null>(null);
  const [excId, setExcId] = useState("");
  const [excursion, setExcursion] = useState<Excursion | null>(null);
  const [mine, setMine] = useState<PersonGrants | null>(null);
  const [place, setPlace] = useState<PlaceGrants | null>(null);
  const [surface, setSurface] = useState("room");
  const [surfaceId, setSurfaceId] = useState("");

  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.agentLights().then(setLights).catch(() => setLights(null));
  }, []);

  const act = (fn: () => Promise<unknown>) => async () => {
    setError(null); setBusy(true);
    try { await fn(); } catch (e) { setError(e); } finally { setBusy(false); }
  };

  return (
    <div className="screen">
      <h2>{tr("nmd.title", lang)}</h2>
      <p className="muted small">{tr("nmd.pitch", lang)}</p>

      <Refusal error={error} onPlans={onPlans} />

      <div className="card">
        <h3>{tr("nmd.campaign", lang)}</h3>
        <p className="muted small">{tr("nmd.mostpublic", lang)}</p>
        <div className="row">
          <input value={campaignId}
                 onChange={(e) => setCampaignId(e.target.value)}
                 placeholder={tr("nmd.campaign.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !campaignId.trim()}
                  onClick={act(async () =>
                    setCampaign(await api.campaign(campaignId.trim())))}>
            {tr("nmd.lookitup", lang)}
          </button>
        </div>
        {campaign && (
          <>
            <p className="small">
              <strong>{campaign.title}</strong>
              {campaign.cause && ` — ${campaign.cause}`}
              <br />
              {fill(tr("nmd.raised", lang), {
                raised: campaign.raised, goal: campaign.goal,
                status: campaign.status,
                donors: campaign.donors === 1
                  ? fill(tr("nmd.donor", lang), { n: campaign.donors })
                  : fill(tr("nmd.donors", lang), { n: campaign.donors }),
              })}
            </p>
            <h4>{tr("nmd.moneygoes", lang)}</h4>
            {(campaign.proceeds_to || []).map((d) => (
              <p className="small" key={d.id}>
                {d.name} — {d.share}% · {d.kind.replace(/_/g, " ")}
                {!d.has_account && (
                  <span className="muted"> · {tr("nmd.noaccount", lang)}</span>
                )}
              </p>
            ))}
            <p className="muted small">{campaign.payment}</p>
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("nmd.org", lang)}</h3>
        <div className="row">
          <input value={orgId} onChange={(e) => setOrgId(e.target.value)}
                 placeholder={tr("nmd.org.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !orgId.trim() || !token}
                  onClick={act(async () =>
                    setOrg(await api.organization(orgId.trim(), token)))}>
            {tr("nmd.lookitup", lang)}
          </button>
        </div>
        {org && (
          <>
            <p className="small"><strong>{org.name}</strong></p>
            {(org.departments || []).length === 0 && (
              <p className="muted small">{tr("nmd.nodepts", lang)}</p>
            )}
            {(org.departments || []).map((d, i) => (
              <p className="small" key={i}>{JSON.stringify(d)}</p>
            ))}
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("nmd.excursion", lang)}</h3>
        <p className="muted small">{tr("nmd.tripout", lang)}</p>
        <div className="row">
          <input value={excId} onChange={(e) => setExcId(e.target.value)}
                 placeholder={tr("nmd.excursion.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !excId.trim() || !token}
                  onClick={act(async () =>
                    setExcursion(await api.excursion(excId.trim(), token)))}>
            {tr("nmd.lookitup", lang)}
          </button>
        </div>
        {excursion && (
          <>
            <p className="small">
              <strong>{excursion.topic}</strong>
            </p>
            {/* The two numbers the feature rests on. Shown together because
                either alone is misleading: nothing left, or something left
                with this much taken out of it first. */}
            <p className="muted small">
              {excursion.left_host
                ? tr("nmd.leftmachine", lang)
                : tr("nmd.nothingleft", lang)}
              {" "}
              {excursion.redactions === 0
                ? tr("nmd.noredactions", lang)
                : fill(excursion.redactions === 1
                         ? tr("nmd.redacted.one", lang)
                         : tr("nmd.redacted.many", lang),
                       { n: excursion.redactions })}
            </p>
            <p className="small">{excursion.brief}</p>
            {excursion.findings && (
              <p className="muted small">{excursion.findings}</p>
            )}
            <p className="muted small">
              {excursion.learned
                ? tr("nmd.learned", lang)
                : tr("nmd.notlearned", lang)}
            </p>
          </>
        )}
      </div>

      <div className="card">
        <h3>{tr("nmd.lending", lang)}</h3>
        {/* This card used to answer with raw JSON — a field report read it
            and could not tell what was going on. A grant is a sentence:
            what, where, standing. */}
        <p className="muted small">{tr("nmd.lending.pitch", lang)}</p>
        <button disabled={busy || !myself || !myToken}
                onClick={act(async () =>
                  setMine(await api.grantsForPerson(myself, myToken)))}>
          {tr("nmd.showmine", lang)}
        </button>
        {mine && (
          <>
            {(mine.lending || []).length === 0
              && (mine.borrowing || []).length === 0 && (
              <p className="muted small">{tr("nmd.nogrants", lang)}</p>
            )}
            {(mine.lending || []).length > 0 && (
              <h4>{tr("nmd.lending.out", lang)}</h4>
            )}
            {(mine.lending || []).map((g, i) => <GrantRow g={g} key={i} />)}
            {(mine.borrowing || []).length > 0 && (
              <h4>{tr("nmd.borrowing", lang)}</h4>
            )}
            {(mine.borrowing || []).map((g, i) => <GrantRow g={g} key={i} />)}
          </>
        )}
        <p className="muted small">{tr("nmd.yoursonly", lang)}</p>
      </div>

      <div className="card">
        <h3>{tr("nmd.inoneplace", lang)}</h3>
        <div className="row">
          <select value={surface} onChange={(e) => setSurface(e.target.value)}>
            {["room", "profile", "org", "session"].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <input value={surfaceId}
                 onChange={(e) => setSurfaceId(e.target.value)}
                 placeholder={tr("nmd.place.ph", lang)} style={{ flex: 1 }} />
          <button disabled={busy || !surfaceId.trim() || !myToken}
                  onClick={act(async () => setPlace(
                    await api.grantsInPlace(surface, surfaceId.trim(),
                                            myToken)))}>
            {tr("nmd.look", lang)}
          </button>
        </div>
        {place && (
          <>
            {place.grants.length === 0 && (
              <p className="muted small">{tr("nmd.noneyours", lang)}</p>
            )}
            {place.grants.map((g, i) => <GrantRow g={g} key={i} />)}
            {/* Verbatim. A short list here means *your* grants, not *no*
                grants, and reading it the other way turns an access limit
                into an empty room. */}
            <p className="muted small">{place.note}</p>
          </>
        )}
      </div>

      {/* The status lights live at the bottom, with a sentence about why a
          legend is on a lookup screen at all — a field report met it at the
          top and wondered what lights had to do with looking things up. */}
      {lights && (
        <div className="card">
          <h3>{tr("nmd.lights", lang)}</h3>
          <p className="muted small">{tr("nmd.lights.why", lang)}</p>
          <p className="muted small">{lights.question}</p>
          {/* Built from the mapping, not written beside it. A legend kept
              separately eventually describes a mapping the code does not
              have — and it is the legend people trust. */}
          {lights.legend.map((l) => (
            <p className="small" key={l.light}>
              <strong>{l.light}</strong> — {l.labels.join(", ")}
              <br />
              <span className="muted">
                {fill(tr("nmd.from", lang), { list: l.statuses.join(", ") })}
              </span>
            </p>
          ))}
          <p className="muted small">{tr("nmd.noidnotoken", lang)}</p>
        </div>
      )}
    </div>
  );
}

/** One grant, as a sentence rather than as JSON: what is lent, where it is
 *  usable, and where it stands. */
function GrantRow({ g }: { g: unknown }) {
  const r = g as { title?: string; skill_kind?: string; means?: string;
                   where?: string; state?: string; used_count?: number };
  return (
    <p className="small">
      <strong>{r.title || (r.skill_kind || "").replace(/_/g, " ")}</strong>
      {r.means && <> — {r.means}</>}
      {r.where && <span className="muted"> · {r.where}</span>}
      {r.state && <span className="muted"> · {r.state}</span>}
      {typeof r.used_count === "number" && r.used_count > 0 && (
        <span className="muted"> · ×{r.used_count}</span>
      )}
    </p>
  );
}
