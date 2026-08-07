import { useEffect, useState } from "react";
import { api, type Solitude as Shape,
         type SolitudeReferral } from "../api";
import { fill, t as tr, visitorLang } from "../l10n";
import { Refusal } from "../Refusal";
import { useSession } from "../store";

// The other half of the multiplicity disclosure. The Attention card on a
// profile says how divided *its* attention is; this says how one-sided yours
// has been, from counts in your own logs.
//
// Three things this screen deliberately does not do, each of which the
// obvious design would:
//
//   * it does not open itself, and nothing routes here on its own — a screen
//     that appeared when the ratio crossed a line would be the notification
//     the backend refuses to send, moved into the client;
//   * it does not editorialise. The numbers and the backend's own note are
//     shown as given. A line here reading "that's a lot" would be the
//     diagnosis `solitude.py` declines to make, added by the front end;
//   * it does not pre-select the offer. Take and Not now are the same size
//     and neither is focused, because a default is a thumb on the scale of a
//     consent.
export function Solitude() {
  const { session } = useSession();
  const lang = visitorLang();
  const [shape, setShape] = useState<Shape | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const [referral, setReferral] = useState<SolitudeReferral | null>(null);
  const who = session.interactorId;

  useEffect(() => {
    if (!who) return;
    api.solitude(who).then(setShape).catch(setError);
  }, [who]);

  async function decide(accept: boolean) {
    if (!who) return;
    setBusy(true); setError(null);
    try {
      await api.solitudeHandoff(who, accept);
      setShape(await api.solitude(who));
    } catch (e) { setError(e); }
    finally { setBusy(false); }
  }

  if (!who) {
    return (
      <div className="screen">
        <header className="screen-head">
          <h2>{tr("sol.title", lang)}</h2>
        </header>
        <p className="muted center">{tr("sol.signin", lang)}</p>
      </div>
    );
  }

  const offer = shape?.offer;
  return (
    <div className="screen">
      <header className="screen-head">
        <h2>{tr("sol.title", lang)}</h2>
        <span className="muted small">{tr("sol.pitch", lang)}</span>
      </header>

      {error ? <Refusal error={error} /> : null}

      {shape && (
        <>
          <div className="card">
            <h3>{tr("sol.counts", lang)}</h3>
            <p className="muted small">
              {fill(tr("sol.window", lang), { days: String(shape.window_days) })}
            </p>
            <div className="friend-row">
              <span>{tr("sol.toprofiles", lang)}</span>
              <b>{shape.turns.to_profiles}</b>
            </div>
            <div className="friend-row">
              <span>{tr("sol.topeople", lang)}</span>
              <b>{shape.turns.to_people}</b>
            </div>
            {/* The backend's own sentence, shown rather than paraphrased.
                Rewording it here is how a count becomes a verdict. */}
            <p className="muted small">{shape.note}</p>
            {!shape.enough_to_say && (
              <p className="muted small">{tr("sol.tooearly", lang)}</p>
            )}
          </div>

          {offer?.state === "available" && (
            <div className="card">
              <h3>{tr("sol.door", lang)}</h3>
              <p className="muted small">{offer.why}</p>
              <p className="muted small">
                <b>{tr("sol.carries", lang)}</b> {(offer.carries ?? []).join(", ")}
              </p>
              <p className="muted small">
                <b>{tr("sol.notcarries", lang)}</b>{" "}
                {(offer.does_not_carry ?? []).join(", ")}
              </p>
              <div className="row">
                <button disabled={busy} onClick={() => decide(true)}>
                  {tr("sol.take", lang)}
                </button>
                <button disabled={busy} onClick={() => decide(false)}>
                  {tr("sol.notnow", lang)}
                </button>
              </div>
            </div>
          )}

          {offer?.state === "declined" && (
            <div className="card">
              <p className="muted small">{tr("sol.declined", lang)}</p>
            </div>
          )}

          {offer?.state === "accepted" && (
            <div className="card">
              <h3>{tr("sol.accepted", lang)}</h3>
              <p className="muted small">{tr("sol.accepted.sub", lang)}</p>
              {/* Shown in full, field by field. A referral somebody is told
                  about but cannot look at is a referral they did not really
                  consent to, and a button that fetched it and displayed
                  nothing would be that with extra steps. */}
              {referral ? (
                <>
                  <div className="friend-row">
                    <span>{tr("sol.ref", lang)}</span><b>{referral.ref}</b>
                  </div>
                  <div className="friend-row">
                    <span>{tr("sol.window.label", lang)}</span>
                    <b>{referral.window_days}</b>
                  </div>
                  <div className="friend-row">
                    <span>{tr("sol.toprofiles", lang)}</span>
                    <b>{referral.turns.to_profiles}</b>
                  </div>
                  <div className="friend-row">
                    <span>{tr("sol.topeople", lang)}</span>
                    <b>{referral.turns.to_people}</b>
                  </div>
                  <p className="muted small">{tr("sol.thatisall", lang)}</p>
                </>
              ) : (
                <button onClick={() => api.solitudeReferral(who)
                  .then(setReferral).catch(setError)}>
                  {tr("sol.showreferral", lang)}
                </button>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
