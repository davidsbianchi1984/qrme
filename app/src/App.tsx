import { useState } from "react";
import { useSession } from "./store";
import { Onboarding } from "./screens/Onboarding";
import { Home } from "./screens/Home";
import { Chat } from "./screens/Chat";
import { Relationships } from "./screens/Relationships";
import { Memory } from "./screens/Memory";
import { Settings } from "./screens/Settings";

type Tab = "home" | "chat" | "relationships" | "memory" | "settings";

const NAV: { id: Tab; label: string; icon: string }[] = [
  { id: "home", label: "Home", icon: "◎" },
  { id: "chat", label: "Chat with Ava", icon: "💬" },
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
        {tab === "relationships" && <Relationships />}
        {tab === "memory" && <Memory />}
        {tab === "settings" && <Settings />}
      </main>
    </div>
  );
}
