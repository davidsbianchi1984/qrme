import { useState } from "react";
import { useSession } from "./store";
import { Onboarding } from "./screens/Onboarding";
import { Home } from "./screens/Home";
import { Chat } from "./screens/Chat";
import { Discover } from "./screens/Discover";
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

type Tab = "home" | "chat" | "discover" | "friends" | "rooms" | "blend" | "simulate" | "campaigns" | "org" | "relationships" | "memory" | "settings";

const NAV: { id: Tab; label: string; icon: string }[] = [
  { id: "home", label: "Home", icon: "◎" },
  { id: "chat", label: "Chat", icon: "💬" },
  { id: "discover", label: "Discover", icon: "🛍" },
  { id: "friends", label: "Friends", icon: "👥" },
  { id: "rooms", label: "Rooms", icon: "🎧" },
  { id: "blend", label: "Blend", icon: "🫱🏽‍🫲🏻" },
  { id: "simulate", label: "What If", icon: "🔮" },
  { id: "campaigns", label: "Campaigns", icon: "🎗" },
  { id: "org", label: "Org", icon: "🏛" },
  { id: "relationships", label: "Relationships", icon: "👥" },
  { id: "memory", label: "Memory Vault", icon: "🔒" },
  { id: "settings", label: "Control", icon: "⚙" },
];

export function App() {
  const { session, signOut } = useSession();
  const [tab, setTab] = useState<Tab>("home");

  // No profile yet → onboarding owns the whole window.
  if (!session.profileId) return <Onboarding />;

  return (
    <div className="app">
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
              {n.label}
            </button>
          ))}
        </nav>
        <button className="signout" onClick={signOut}>
          Sign out
        </button>
      </aside>

      <main className="content">
        {tab === "home" && <Home go={setTab} />}
        {tab === "chat" && <Chat />}
        {tab === "discover" && <Discover />}
        {tab === "friends" && <Friends />}
        {tab === "rooms" && <Rooms />}
        {tab === "blend" && <Blend />}
        {tab === "simulate" && <Simulate />}
        {tab === "campaigns" && <Campaigns />}
        {tab === "org" && <Org />}
        {tab === "relationships" && <Relationships />}
        {tab === "memory" && <Memory />}
        {tab === "settings" && <Settings />}
      </main>

      {/* Outside the tab switch on purpose: it is part of the shell, so every
          screen has it without each screen having to remember. */}
      <Help />
    </div>
  );
}
