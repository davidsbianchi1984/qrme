import { useState } from "react";
import { api } from "../api";
import { useSession } from "../store";

// Create-profile flow: POST /profiles, then register an interactor ("You") and
// set the owner relationship, so the app can chat straight away.
export function Onboarding() {
  const { setSession } = useSession();
  const [name, setName] = useState("Ava");
  const [persona, setPersona] = useState(
    "A warm, curious digital version of me — remembers what matters and speaks plainly.",
  );
  const [birthdate, setBirthdate] = useState("1990-06-01");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function create() {
    setBusy(true);
    setError(null);
    try {
      const profile = await api.createProfile({
        owner_id: "owner-desktop",
        kind: "self",
        display_name: name.trim() || "Ava",
        persona: persona.trim(),
        verification: { birthdate },
        purpose: "companion_coach",
      });
      const me = await api.createInteractor({ display_name: "You", birthdate });
      await api.setRelationship(profile.id, me.id, {
        relationship_type: "friend",
        nickname: "me",
        tone: "warm",
      }, profile.owner_token!);
      setSession({
        profileId: profile.id,
        ownerToken: profile.owner_token,
        profile,
        interactorId: me.id,
        interactorToken: me.token,
      });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="onboarding">
      <div className="onboard-card">
        <div className="orb big" />
        <h1>Your identity. Your AI.</h1>
        <p className="muted">
          Create a synthetic profile that thinks, remembers, and evolves with you.
          It runs against your local QRME API — your data stays in your vault.
        </p>

        <label>
          Profile name
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          Persona
          <textarea
            rows={3}
            value={persona}
            onChange={(e) => setPersona(e.target.value)}
          />
        </label>
        <label>
          Owner birthdate (age verification)
          <input
            type="date"
            value={birthdate}
            onChange={(e) => setBirthdate(e.target.value)}
          />
        </label>

        {error && <div className="error">⚠ {error}</div>}

        <button className="primary" disabled={busy} onClick={create}>
          {busy ? "Creating…" : "Create My Profile"}
        </button>
        <p className="hint">
          Start the backend first: <code>QRME_CORS_ORIGINS=* uvicorn qrme.api:app</code>
        </p>
      </div>
    </div>
  );
}
