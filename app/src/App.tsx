import { useEffect, useState } from "react";
import { api } from "./api";
import { t } from "./l10n";
import { useSession } from "./store";
import { Onboarding } from "./screens/Onboarding";
import { Public, type Pane as PublicPane } from "./screens/Public";
import { Home } from "./screens/Home";
import { Chat } from "./screens/Chat";
import { Delegate } from "./screens/Delegate";
import { Desk } from "./screens/Desk";
import { Discover } from "./screens/Discover";
import { Market } from "./screens/Market";
import { Shops } from "./screens/Shops";
import { Corner } from "./screens/Corner";
import { Exchanges } from "./screens/Exchanges";
import { Identity } from "./screens/Identity";
import { Presence } from "./screens/Presence";
import { Live } from "./screens/Live";
import { Contest } from "./screens/Contest";
import { Guide } from "./screens/Guide";
import { Placements } from "./screens/Placements";
import { Plans } from "./screens/Plans";
import { Robots } from "./screens/Robots";
import { Workshop } from "./screens/Workshop";
import { Assist } from "./screens/Assist";
import { Referrals } from "./screens/Referrals";
import { Lobby } from "./screens/Lobby";
import { Audience } from "./screens/Audience";
import { Beacons } from "./screens/Beacons";
import { Leaving } from "./screens/Leaving";
import { Selling } from "./screens/Selling";
import { Inside } from "./screens/Inside";
import { Signing } from "./screens/Signing";
import { Visiting } from "./screens/Visiting";
import { Stranger } from "./screens/Stranger";
import { TheMark } from "./screens/TheMark";
import { InWords } from "./screens/InWords";
import { Remainder } from "./screens/Remainder";
import { Named } from "./screens/Named";
import { Passing } from "./screens/Passing";
import { Reaching } from "./screens/Reaching";
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

type Tab = "home" | "chat" | "discover" | "market" | "shop" | "corner" | "wall" | "friends" | "rooms" | "blend" | "simulate" | "campaigns" | "org" | "relationships" | "memory" | "voice" | "delegate" | "desk" | "exchanges" | "grants" | "party" | "identity" | "presence" | "live" | "contest" | "guide" | "workshop" | "assist" | "referrals" | "lobby" | "audience" | "beacons" | "reaching" | "leaving" | "selling" | "inside" | "signing" | "visiting" | "stranger" | "themark" | "inwords" | "remainder" | "named" | "passing" | "robots" | "placements" | "plans" | "settings";

const NAV: { id: Tab; label: string; icon: string }[] = [
  { id: "home", label: "Home", icon: "◎" },
  { id: "guide", label: "Show me around", icon: "🧭" },
  { id: "chat", label: "Chat", icon: "💬" },
  { id: "discover", label: "Discover", icon: "🛍" },
  { id: "market", label: "Marketplace", icon: "🏷" },
  { id: "shop", label: "Shops", icon: "🛒" },
  { id: "corner", label: "Your corner", icon: "🏠" },
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
  { id: "live", label: "What is live", icon: "🎥" },
  { id: "contest", label: "Contest a profile", icon: "⚖" },
  { id: "exchanges", label: "Exchanges", icon: "📝" },
  { id: "grants", label: "Lent skills", icon: "🪄" },
  { id: "party", label: "Watch together", icon: "🍿" },
  { id: "voice", label: "Voice", icon: "🎙" },
  { id: "workshop", label: "What it is made of", icon: "🧩" },
  { id: "assist", label: "What it can do for you", icon: "🛠" },
  { id: "referrals", label: "Somebody qualified", icon: "🩺" },
  { id: "lobby", label: "In the game", icon: "🎮" },
  { id: "audience", label: "Who follows", icon: "💛" },
  { id: "beacons", label: "Where people find you", icon: "🔳" },
  { id: "reaching", label: "Reaching out", icon: "🌙" },
  { id: "leaving", label: "What leaves", icon: "📤" },
  { id: "selling", label: "What you are owed", icon: "💰" },
  { id: "inside", label: "Inside a room", icon: "🚪" },
  { id: "signing", label: "Signing", icon: "🖋" },
  { id: "visiting", label: "Visiting", icon: "🔔" },
  { id: "stranger", label: "Strangers", icon: "🎭" },
  { id: "themark", label: "The mark", icon: "✦" },
  { id: "inwords", label: "In its words", icon: "🗣" },
  { id: "remainder", label: "Everything else", icon: "🧩" },
  { id: "named", label: "One thing, named", icon: "🔎" },
  { id: "passing", label: "Beginning and passing on", icon: "🕊" },
  { id: "robots", label: "Bodies", icon: "🤖" },
  { id: "placements", label: "Where it is marketed", icon: "📌" },
  { id: "plans", label: "Plans", icon: "🎟" },
  { id: "settings", label: "Control", icon: "⚙" },
];

export function App() {
  const { session, signOut } = useSession();
  const [tab, setTab] = useState<Tab>("home");
  // The two doors that open before a profile exists. Null is the sign-in
  // screen; the state lives here rather than inside Onboarding so the hash
  // link and the in-page link land in the same place.
  const [publicDoor, setPublicDoor] = useState<PublicPane | null>(null);
  // Threaded into every screen that can be refused. A plan gate
  // names a plan, so the refusal has to be able to reach one.
  const toPlans = () => setTab("plans");
  // The chrome follows the profile's language (server-side setting; the
  // content always did — this closes the frame around it).
  const [lang, setLang] = useState<string>("en");
  useEffect(() => {
    if (!session.profileId) return;
    api.getLanguage(session.profileId)
      .then((r) => setLang(r.language || "en"))
      .catch(() => setLang("en"));
  }, [session.profileId]);

  // No profile yet → onboarding owns the whole window, *except* for the two
  // things QRME's backend deliberately lets a stranger do.
  //
  // `open_objection` says it in its own docstring — "public: the objecting
  // party need not own an account" — and Contest.tsx said it in the copy a
  // person reads. Both were true of the route and false of the app: this
  // early return handed the entire window to sign-up, so the one surface a
  // person with no account could reach was the one asking them to make one.
  // The person that route exists for is by construction the person without
  // an account: they have found a synthetic profile of themselves.
  //
  // Read once at mount rather than routed, so a link in a takedown notice or
  // a moderation reply can point at the form instead of the sign-up page.
  if (!session.profileId) {
    const door = publicDoor
      ?? (window.location.hash === "#object" ? "object"
        : window.location.hash === "#mark" ? "mark" : null);
    return (
      <>
        <VersionGuard />
        {door
          ? <Public start={door} onBack={() => {
              setPublicDoor(null);
              if (window.location.hash) window.location.hash = "";
            }} />
          : <Onboarding onPublic={setPublicDoor} />}
      </>
    );
  }

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
        {tab === "chat" && <Chat onPlans={toPlans} />}
        {tab === "discover" && <Discover onPlans={toPlans} />}
        {tab === "market" && <Market onPlans={toPlans} />}
        {tab === "shop" && <Shops onPlans={toPlans} />}
        {tab === "corner" && <Corner onPlans={toPlans} />}
        {tab === "wall" && <Wall onPlans={toPlans} />}
        {tab === "friends" && <Friends onPlans={toPlans} />}
        {tab === "rooms" && <Rooms onPlans={toPlans} />}
        {tab === "blend" && <Blend onPlans={toPlans} />}
        {tab === "simulate" && <Simulate onPlans={toPlans} />}
        {tab === "campaigns" && <Campaigns onPlans={toPlans} />}
        {tab === "org" && <Org onPlans={toPlans} />}
        {tab === "relationships" && <Relationships onPlans={toPlans} />}
        {tab === "memory" && <Memory onPlans={toPlans} />}
        {tab === "delegate" && <Delegate onPlans={toPlans} />}
        {tab === "desk" && <Desk onPlans={toPlans} />}
        {tab === "identity" && <Identity onPlans={toPlans} />}
        {tab === "presence" && <Presence onPlans={toPlans} />}
        {tab === "live" && <Live onPlans={toPlans} />}
        {tab === "contest" && <Contest onPlans={toPlans} />}
        {tab === "guide" && <Guide onPlans={toPlans} />}
        {tab === "exchanges" && <Exchanges onPlans={toPlans} />}
        {tab === "grants" && <Grants onPlans={toPlans} />}
        {tab === "party" && <WatchParty onPlans={toPlans} />}
        {tab === "voice" && <Voice onPlans={toPlans} />}
        {tab === "workshop" && <Workshop onPlans={toPlans} />}
        {tab === "assist" && <Assist onPlans={toPlans} />}
        {tab === "referrals" && <Referrals onPlans={toPlans} />}
        {tab === "lobby" && <Lobby onPlans={toPlans} />}
        {tab === "audience" && <Audience onPlans={toPlans} />}
        {tab === "beacons" && <Beacons onPlans={toPlans} />}
        {tab === "reaching" && <Reaching onPlans={toPlans} />}
        {tab === "leaving" && <Leaving onPlans={toPlans} />}
        {tab === "selling" && <Selling onPlans={toPlans} />}
        {tab === "inside" && <Inside onPlans={toPlans} />}
        {tab === "signing" && <Signing />}
        {tab === "visiting" && <Visiting />}
        {tab === "stranger" && <Stranger />}
        {tab === "themark" && <TheMark />}
        {tab === "inwords" && <InWords />}
        {tab === "remainder" && <Remainder />}
        {tab === "named" && <Named onPlans={toPlans} />}
        {tab === "passing" && <Passing onPlans={toPlans} />}
        {tab === "robots" && <Robots onPlans={toPlans} />}
        {tab === "placements" && <Placements onPlans={toPlans} />}
        {tab === "plans" && <Plans />}
        {tab === "settings" && <Settings onPlans={toPlans} />}
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
