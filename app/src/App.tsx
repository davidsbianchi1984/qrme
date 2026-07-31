import { useEffect, useState } from "react";
import { api } from "./api";
import { t } from "./l10n";
import { useSession } from "./store";
import { Onboarding } from "./screens/Onboarding";
import { Home } from "./screens/Home";
import { Chat } from "./screens/Chat";
import { Delegate } from "./screens/Delegate";
import { Desk } from "./screens/Desk";
import { Discover } from "./screens/Discover";
import { Market } from "./screens/Market";
import { Exchanges } from "./screens/Exchanges";
import { Identity } from "./screens/Identity";
import { Presence } from "./screens/Presence";
import { Grants } from "./screens/Grants";
import { WatchParty } from "./screens/WatchParty";
import { Voice } from "./screens/Voice";
import { Wall } from "./screens/Wall";
import { Friends } from "./screens/Friends";
import { Rooms } from "./screens/Rooms";
import { Blend } from "./screens/Blend";
import { Simulate } from "./screens/Simulate";
import { Campaigns } from "./screens/Campaigns";
import { Org } from "./screens/Org";
import { Relationships } from "./screens/Relationships";
import { Memory } from "./screens/Memory";
import { Settings } from "./screens/Settings";
import { Help } from "./Help";
import { ProblemNotice } from "./ProblemNotice";
import { VersionGuard } from "./VersionGuard";
import { WatchLights } from "./WatchLights";

type Tab = "home" | "chat" | "discover" | "market" | "wall" | "friends" | "rooms" | "blend" | "simulate" | "campaigns" | "org" | "relationships" | "memory" | "voice" | "delegate" | "desk" | "exchanges" | "grants" | "party" | "identity" | "presence" | "settings";

const NAV: { id: Tab; label: string; icon: string }[] = [
  { id: "home", label: "Home", icon: "◎" },
  { id: "chat", label: "Chat", icon: "💬" },
  { id: "discover", label: "Discover", icon: "🛍" },
  { id: "market", label: "Marketplace", icon: "🏷" },
  { id: "wall", label: "Wall", icon: "🧱" },
  { id: "friends", label: "Friends", icon: "👥" },
  { id: "rooms", label: "Rooms", icon: "🎧" },
  { id: "blend", label: "Blend", icon: "🫱🏽‍🫲🏻" },
  { id: "simulate", label: "What If", icon: "🔮" },
  { id: "campaigns", label: "Campaigns", icon: "🎗" },
  { id: "org", label: "Org", icon: "🏛" },
  { id: "relationships", label: "Relationships", icon: "👥" },
  { id: "memory", label: "Memory Vault", icon: "🔒" },
  { id: "delegate", label: "Delegation", icon: "🤝" },
  { id: "desk", label: "Desk", icon: "🛎" },
  { id: "identity", label: "Identity", icon: "🪪" },
  { id: "presence", label: "Where it is seen", icon: "🖼" },
  { id: "exchanges", label: "Exchanges", icon: "📝" },
  { id: "grants", label: "Lent skills", icon: "🪄" },
  { id: "party", label: "Watch together", icon: "🍿" },
  { id: "voice", label: "Voice", icon: "🎙" },
  { id: "settings", label: "Control", icon: "⚙" },
];

export function App() {
  const { session, signOut } = useSession();
  const [tab, setTab] = useState<Tab>("home");
  // The chrome follows the profile's language (server-side setting; the
  // content always did — this closes the frame around it).
  const [lang, setLang] = useState<string>("en");
  useEffect(() => {
    if (!session.profileId) return;
    api.getLanguage(session.profileId)
      .then((r) => setLang(r.language || "en"))
      .catch(() => setLang("en"));
  }, [session.profileId]);

  // No profile yet → onboarding owns the whole window.
  // The guard wraps onboarding too: a mismatched backend at sign-up is
  // the same trap, one screen earlier.
  if (!session.profileId) return <><VersionGuard /><Onboarding /></>;

  return (
    <div className="app">
      <VersionGuard />
      <aside className="sidebar">
        <div className="brand">
          <span className="orb" />
          <div>
            <div className="brand-name">QRME</div>
            <div className="brand-sub">Your identity. Your AI.</div>
          </div>
        </div>
        <nav>
          {NAV.map((n) => (
            <button
              key={n.id}
              className={"nav-item" + (tab === n.id ? " active" : "")}
              onClick={() => setTab(n.id)}
            >
              <span className="nav-icon">{n.icon}</span>
              {t(`nav.${n.id}`, lang)}
            </button>
          ))}
        </nav>
        <button className="signout" onClick={signOut}>
          {t("signout", lang)}
        </button>
      </aside>

      <main className="content">
        <ProblemNotice />
        {tab === "home" && <Home go={setTab} />}
        {tab === "chat" && <Chat />}
        {tab === "discover" && <Discover />}
        {tab === "market" && <Market />}
        {tab === "wall" && <Wall />}
        {tab === "friends" && <Friends />}
        {tab === "rooms" && <Rooms />}
        {tab === "blend" && <Blend />}
        {tab === "simulate" && <Simulate />}
        {tab === "campaigns" && <Campaigns />}
        {tab === "org" && <Org />}
        {tab === "relationships" && <Relationships />}
        {tab === "memory" && <Memory />}
        {tab === "delegate" && <Delegate />}
        {tab === "desk" && <Desk />}
        {tab === "identity" && <Identity />}
        {tab === "presence" && <Presence />}
        {tab === "exchanges" && <Exchanges />}
        {tab === "grants" && <Grants />}
        {tab === "party" && <WatchParty />}
        {tab === "voice" && <Voice />}
        {tab === "settings" && <Settings />}
      </main>

      {/* Outside the tab switch on purpose: it is part of the shell, so every
          screen has it without each screen having to remember. */}
      <Help />
      {/* Same reason: the agent task lights are on every screen, watch-sized,
          minimizable to a dot when they're in the way. */}
      <WatchLights />
    </div>
  );
}
