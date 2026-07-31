import { useEffect, useState } from "react";
import { api, type CampaignOut, type Excursion, type LightLegend,
         type OrgOut, type PersonGrants, type PlaceGrants } from "../api";
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
      <h2>One thing, named</h2>
      <p className="muted small">
        Six reads, six different answers to who is allowed to ask.
      </p>

      <Refusal error={error} onPlans={onPlans} />

      {lights && (
        <div className="card">
          <h3>What the lights mean</h3>
          <p className="muted small">{lights.question}</p>
          {/* Built from the mapping, not written beside it. A legend kept
              separately eventually describes a mapping the code does not
              have — and it is the legend people trust. */}
          {lights.legend.map((l) => (
            <p className="small" key={l.light}>
              <strong>{l.light}</strong> — {l.labels.join(", ")}
              <br />
              <span className="muted">from: {l.statuses.join(", ")}</span>
            </p>
          ))}
          <p className="muted small">
            No id, no token. It is the key the screens render, so anything
            that draws a light can ask what one means.
          </p>
        </div>
      )}

      <div className="card">
        <h3>A campaign</h3>
        <p className="muted small">
          The most public read here, on purpose. It carries who the money
          goes to, and the person about to give some is the one entitled to
          see that — a fundraising page that hid its split would be the
          ordinary kind of dishonest. A campaign cannot even be created
          before the designation exists.
        </p>
        <div className="row">
          <input value={campaignId}
                 onChange={(e) => setCampaignId(e.target.value)}
                 placeholder="a campaign id" style={{ flex: 1 }} />
          <button disabled={busy || !campaignId.trim()}
                  onClick={act(async () =>
                    setCampaign(await api.campaign(campaignId.trim())))}>
            Look it up
          </button>
        </div>
        {campaign && (
          <>
            <p className="small">
              <strong>{campaign.title}</strong>
              {campaign.cause && ` — ${campaign.cause}`}
              <br />
              {campaign.raised} of {campaign.goal} from{" "}
              {campaign.donors} {campaign.donors === 1 ? "donor" : "donors"} ·{" "}
              {campaign.status}
            </p>
            <h4>Where the money goes</h4>
            {(campaign.proceeds_to || []).map((d) => (
              <p className="small" key={d.id}>
                {d.name} — {d.share}% · {d.kind.replace(/_/g, " ")}
                {!d.has_account && (
                  <span className="muted"> · no account yet</span>
                )}
              </p>
            ))}
            <p className="muted small">{campaign.payment}</p>
          </>
        )}
      </div>

      <div className="card">
        <h3>An organization</h3>
        <div className="row">
          <input value={orgId} onChange={(e) => setOrgId(e.target.value)}
                 placeholder="an organization id" style={{ flex: 1 }} />
          <button disabled={busy || !orgId.trim() || !token}
                  onClick={act(async () =>
                    setOrg(await api.organization(orgId.trim(), token)))}>
            Look it up
          </button>
        </div>
        {org && (
          <>
            <p className="small"><strong>{org.name}</strong></p>
            {(org.departments || []).length === 0 && (
              <p className="muted small">No departments yet.</p>
            )}
            {(org.departments || []).map((d, i) => (
              <p className="small" key={i}>{JSON.stringify(d)}</p>
            ))}
          </>
        )}
      </div>

      <div className="card">
        <h3>An excursion</h3>
        <p className="muted small">
          A trip out to look something up. The owner's only, because it holds
          the brief that was sanitised before it went and the count of what
          was taken out of it.
        </p>
        <div className="row">
          <input value={excId} onChange={(e) => setExcId(e.target.value)}
                 placeholder="an excursion id" style={{ flex: 1 }} />
          <button disabled={busy || !excId.trim() || !token}
                  onClick={act(async () =>
                    setExcursion(await api.excursion(excId.trim(), token)))}>
            Look it up
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
                ? "This left the machine."
                : "Nothing left this machine."}
              {" "}
              {excursion.redactions === 0
                ? "Nothing was redacted from the brief."
                : `${excursion.redactions} private term`
                  + `${excursion.redactions === 1 ? "" : "s"} stripped from `
                  + "the brief before it went."}
            </p>
            <p className="small">{excursion.brief}</p>
            {excursion.findings && (
              <p className="muted small">{excursion.findings}</p>
            )}
            <p className="muted small">
              {excursion.learned
                ? "Folded back into the profile as a learned source."
                : "Not learned — the findings sit here until you let them in."}
            </p>
          </>
        )}
      </div>

      <div className="card">
        <h3>What you are lending and borrowing</h3>
        <button disabled={busy || !myself || !myToken}
                onClick={act(async () =>
                  setMine(await api.grantsForPerson(myself, myToken)))}>
          Show mine
        </button>
        {mine && <p className="small">{JSON.stringify(mine)}</p>}
        <p className="muted small">
          Yours only. The route says so in its own words — it acts on
          somebody's behalf, so it has to know it is them.
        </p>
      </div>

      <div className="card">
        <h3>…and in one place</h3>
        <div className="row">
          <select value={surface} onChange={(e) => setSurface(e.target.value)}>
            {["room", "profile", "org", "session"].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <input value={surfaceId}
                 onChange={(e) => setSurfaceId(e.target.value)}
                 placeholder="the place's id" style={{ flex: 1 }} />
          <button disabled={busy || !surfaceId.trim() || !myToken}
                  onClick={act(async () => setPlace(
                    await api.grantsInPlace(surface, surfaceId.trim(),
                                            myToken)))}>
            Look
          </button>
        </div>
        {place && (
          <>
            {place.grants.length === 0 && (
              <p className="muted small">None of yours here.</p>
            )}
            {place.grants.map((g, i) => (
              <p className="small" key={i}>{JSON.stringify(g)}</p>
            ))}
            {/* Verbatim. A short list here means *your* grants, not *no*
                grants, and reading it the other way turns an access limit
                into an empty room. */}
            <p className="muted small">{place.note}</p>
          </>
        )}
      </div>
    </div>
  );
}
