import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import { t, visitorLang } from "./l10n";
import { useSession } from "./store";
import { Onboarding } from "./screens/Onboarding";
import { Public, type Pane as PublicPane } from "./screens/Public";
import { Home } from "./screens/Home";
import { Profile } from "./screens/Profile";
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
import { Allowed } from "./screens/Allowed";
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
import { Feed } from "./screens/Feed";
import { Friends } from "./screens/Friends";
import { Rooms } from "./screens/Rooms";
import { Blend } from "./screens/Blend";
import { Solitude } from "./screens/Solitude";
import { Simulate } from "./screens/Simulate";
import { Campaigns } from "./screens/Campaigns";
import { Org } from "./screens/Org";
import { Relationships } from "./screens/Relationships";
import { Memory } from "./screens/Memory";
import { Agent } from "./screens/Agent";
import { Studio } from "./screens/Studio";
import { Plugins } from "./screens/Plugins";
import { Settings } from "./screens/Settings";
import { Access } from "./screens/Access";
import { Matters } from "./screens/Matters";
import { Help } from "./Help";
import { ProblemNotice } from "./ProblemNotice";
import { Footsteps } from "./Footsteps";
import { VersionGuard } from "./VersionGuard";
import { WatchLights } from "./WatchLights";

// `profile` is deliberately not in NAV: somebody else's homepage is a place
// you are taken to by pressing their face, not a standing destination — the
// same reason `passing` is reachable and unlisted.
type Tab = "profile" | "home" | "agent" | "feed" | "chat" | "discover" | "market" | "shop" | "corner" | "wall" | "friends" | "rooms" | "blend" | "solitude" | "simulate" | "campaigns" | "org" | "relationships" | "memory" | "studio" | "voice" | "delegate" | "desk" | "exchanges" | "grants" | "party" | "identity" | "presence" | "live" | "contest" | "guide" | "workshop" | "assist" | "referrals" | "lobby" | "audience" | "beacons" | "reaching" | "leaving" | "selling" | "inside" | "signing" | "visiting" | "allowed" | "stranger" | "themark" | "inwords" | "remainder" | "plugins" | "named" | "passing" | "robots" | "placements" | "plans" | "access" | "matters" | "settings";

// `art` is the one tab whose mark is a picture rather than a glyph. Kept as a
// second, optional field rather than widening `icon` to a node: the nav guards
// parse this table as text for `id:`, `label:` and the icon, and a shape they
// cannot read is a shape that stops being checked.
const NAV: { id: Tab; label: string; icon: string; art?: string;
             group?: string }[] = [
  { id: "home", label: "Home", icon: "◎" },
  { id: "agent", label: "Agent", icon: "✦", art: "agent.png" },
  { id: "feed", label: "Feed", icon: "▶" },
  { id: "guide", label: "Tour", icon: "🧭" },
  { id: "chat", label: "Chat", icon: "💬" },
  { id: "discover", label: "Discover", icon: "🛍", group: "community" },
  { id: "market", label: "Marketplace", icon: "🏷", group: "community" },
  { id: "shop", label: "Shops", icon: "🛒", group: "community" },
  { id: "corner", label: "My Space", icon: "🏠", group: "profile" },
  { id: "wall", label: "Wall", icon: "🧱", group: "profile" },
  { id: "friends", label: "Friends", icon: "👥", group: "community" },
  { id: "rooms", label: "Rooms", icon: "🎧", group: "community" },
  { id: "blend", label: "Blend", icon: "🫱🏽‍🫲🏻", group: "create" },
  { id: "solitude", label: "My Attention", icon: "🪞", group: "profile" },
  { id: "simulate", label: "What If", icon: "🔮", group: "create" },
  { id: "campaigns", label: "Campaigns", icon: "🎗", group: "business" },
  { id: "org", label: "Org", icon: "🏛", group: "business" },
  { id: "relationships", label: "Relationships", icon: "👥", group: "profile" },
  { id: "memory", label: "Memory Vault", icon: "🔒", group: "profile" },
  { id: "studio", label: "Widgets", icon: "🛠", group: "create" },
  { id: "delegate", label: "Delegation", icon: "🤝", group: "business" },
  { id: "desk", label: "Desk", icon: "🛎", group: "business" },
  { id: "identity", label: "Identity", icon: "🪪", group: "profile" },
  { id: "presence", label: "Presence", icon: "🖼", group: "profile" },
  { id: "live", label: "Live Now", icon: "🎥", group: "trust" },
  { id: "contest", label: "Disputes", icon: "⚖", group: "trust" },
  { id: "exchanges", label: "Exchanges", icon: "📝", group: "business" },
  { id: "grants", label: "Skill Lending", icon: "🪄", group: "business" },
  { id: "party", label: "Watch Party", icon: "🍿", group: "community" },
  { id: "voice", label: "Voice", icon: "🎙", group: "profile" },
  { id: "workshop", label: "Profile Builder", icon: "🧩", group: "profile" },
  { id: "assist", label: "Tasks", icon: "🛠", group: "create" },
  { id: "referrals", label: "Referrals", icon: "🩺", group: "business" },
  { id: "lobby", label: "Gaming", icon: "🎮", group: "business" },
  { id: "audience", label: "Audience", icon: "💛", group: "community" },
  { id: "beacons", label: "Beacons", icon: "🔳", group: "trust" },
  { id: "reaching", label: "Outreach", icon: "🌙", group: "trust" },
  { id: "leaving", label: "Exports & Licensing", icon: "📤", group: "business" },
  { id: "selling", label: "Earnings", icon: "💰", group: "business" },
  { id: "inside", label: "Room", icon: "🚪", group: "community" },
  { id: "signing", label: "Signing", icon: "🖋", group: "trust" },
  { id: "visiting", label: "Visits", icon: "🔔", group: "community" },
  { id: "allowed", label: "Permissions", icon: "🔑", group: "trust" },
  { id: "stranger", label: "Guest Access", icon: "🎭", group: "community" },
  { id: "themark", label: "Watermark", icon: "✦", group: "trust" },
  { id: "inwords", label: "Language & Name", icon: "🗣", group: "profile" },
  { id: "remainder", label: "More Tools", icon: "🧩", group: "system" },
  { id: "plugins", label: "Plug-ins", icon: "🔌", group: "system" },
  { id: "named", label: "Lookup", icon: "🔎", group: "create" },
  { id: "robots", label: "Robots & Devices", icon: "🤖", group: "business" },
  { id: "placements", label: "Ad Placements", icon: "📌", group: "business" },
  { id: "plans", label: "Plans & Billing", icon: "🎟", group: "system" },
  { id: "access", label: "Accessibility", icon: "♿", group: "trust" },
  { id: "matters", label: "Support", icon: "🛟", group: "trust" },
  { id: "settings", label: "Settings", icon: "⚙", group: "system" },
];

/** The drawer's sections, in the order they stack. Derived order
 *  lives here rather than in the table so a tab moved between
 *  groups is one field, not a reshuffle. */
const NAV_GROUPS = ["community", "profile", "create", "business",
                    "trust", "system"];

export function App() {
  const { session, signOut } = useSession();
  const [tab, setTab] = useState<Tab>("home");
  // The scroll container. Every tab change lands at the top of the new
  // screen — a field report opened menus "pinned in the middle somewhere",
  // because the pane kept the previous screen's scroll position.
  const contentRef = useRef<HTMLElement | null>(null);
  useEffect(() => { contentRef.current?.scrollTo(0, 0); }, [tab]);
  // The two doors that open before a profile exists. Null is the sign-in
  // screen; the state lives here rather than inside Onboarding so the hash
  // link and the in-page link land in the same place.
  const [publicDoor, setPublicDoor] = useState<PublicPane | null>(null);
  // Threaded into every screen that can be refused. A plan gate
  // names a plan, so the refusal has to be able to reach one.
  const toPlans = () => setTab("plans");
  // A join on the Rooms screen lands the person Inside, on that room.
  const [insideRoom, setInsideRoom] = useState("");
  // Whose homepage is open, and where pressing Back should return to. The
  // trail is a stack rather than a single id because their Top 8 is eight
  // more doors: walking friend-to-friend and pressing Back should retrace
  // the walk, not drop you at whichever screen started it.
  const [visitingId, setVisitingId] = useState("");
  // The menu: a drawer on a phone, opened from the top-left — the owner's
  // asked-for shape — and a grouped sidebar on a desktop. Which sections
  // stand open is state, and the active tab's own section opens itself.
  const [menuOpen, setMenuOpen] = useState(false);
  const [openGroups, setOpenGroups] = useState<Set<string>>(new Set());
  useEffect(() => {
    const g = NAV.find((n) => n.id === tab)?.group;
    if (g) setOpenGroups((prev) =>
      prev.has(g) ? prev : new Set(prev).add(g));
  }, [tab]);
  const toggleGroup = (g: string) => setOpenGroups((prev) => {
    const next = new Set(prev);
    if (next.has(g)) next.delete(g); else next.add(g);
    return next;
  });
  // Read only through its own updater — the trail is history, never render
  // state, so nothing below needs to see it.
  const [, setVisitTrail] = useState<{ tab: Tab; id: string }[]>([]);
  const visitProfile = (id: string) => {
    // Where you were, not merely which tab — otherwise stepping from one
    // homepage to another and pressing Back lands on "profile" again, which
    // is the page you are already standing on.
    setVisitTrail((trail) => [...trail, { tab, id: visitingId }]);
    setVisitingId(id);
    setTab("profile");
  };
  const leaveProfile = () => {
    setVisitTrail((trail) => {
      const back = trail[trail.length - 1];
      setVisitingId(back?.id ?? "");
      setTab(back?.tab ?? "home");
      return trail.slice(0, -1);
    });
  };
  // A party joined from a feed card. The join succeeded where the person was
  // — the feed — and the room is on another tab; this is how they land in it
  // instead of having joined invisibly.
  const [openParty, setOpenParty] = useState("");
  // The chrome follows the profile's language (server-side setting; the
  // content always did — this closes the frame around it).
  const [lang, setLang] = useState<string>("en");
  useEffect(() => {
    if (!session.profileId) return;
    api.getLanguage(session.profileId)
      .then((r) => setLang(r.language || "en"))
      .catch(() => setLang("en"));
  }, [session.profileId]);
  // The document's own language attribute, so a screen reader pronounces
  // the page in the language it is actually written in. index.html ships
  // lang="en" and that was the end of the story; the app renders Spanish
  // under an English tag and every synthesized voice read it wrong.
  useEffect(() => {
    document.documentElement.lang = session.profileId ? lang : visitorLang();
  }, [lang, session.profileId]);

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
        : window.location.hash === "#mark" ? "mark"
        : window.location.hash === "#access" ? "access" : null);
    return (
      <>
        <VersionGuard />
        <Footsteps />
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
      <Footsteps />
      <button className="menu-fab" aria-label={t("nav.menu", lang)}
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen(!menuOpen)}>☰</button>
      {menuOpen && (
        <button className="menu-scrim" aria-label={t("nav.menu", lang)}
                onClick={() => setMenuOpen(false)} />
      )}
      <aside className={"sidebar" + (menuOpen ? " open" : "")}>
        <div className="brand">
          <span className="orb" />
          <div>
            <div className="brand-name">QRME</div>
            <div className="brand-sub">Your identity. Your AI.</div>
          </div>
        </div>
        <nav>
          {NAV.filter((n) => !n.group).map((n) => (
            <button
              key={n.id}
              className={"nav-item" + (tab === n.id ? " active" : "")}
              onClick={() => { setTab(n.id); setMenuOpen(false); }}
            >
              <span className={"nav-icon" + (n.art ? " nav-art" : "")}>
                {n.art ? <img src={n.art} alt="" /> : n.icon}
              </span>
              {t(`nav.${n.id}`, lang)}
            </button>
          ))}
          {NAV_GROUPS.map((g) => (
            <div key={g} className="nav-group">
              <button className={"nav-group-head"
                                 + (openGroups.has(g) ? " open" : "")}
                      aria-expanded={openGroups.has(g)}
                      onClick={() => toggleGroup(g)}>
                <span className="nav-caret" aria-hidden="true">
                  {openGroups.has(g) ? "▾" : "▸"}
                </span>
                {t(`navgrp.${g}`, lang)}
              </button>
              {openGroups.has(g) && NAV.filter((n) => n.group === g)
                .map((n) => (
                  <button
                    key={n.id}
                    className={"nav-item" + (tab === n.id ? " active" : "")}
                    onClick={() => { setTab(n.id); setMenuOpen(false); }}
                  >
                    <span className={"nav-icon" + (n.art ? " nav-art" : "")}>
                      {n.art ? <img src={n.art} alt="" /> : n.icon}
                    </span>
                    {t(`nav.${n.id}`, lang)}
                  </button>
                ))}
            </div>
          ))}
        </nav>
        <button className="signout" onClick={signOut}>
          {t("signout", lang)}
        </button>
      </aside>

      <main className="content" ref={contentRef}>
        <ProblemNotice />
        {tab === "home" && <Home go={setTab} onVisit={visitProfile}
                 onInside={(id) => { setInsideRoom(id); setTab("inside"); }} />}
        {tab === "profile" && (
          <Profile profileId={visitingId} onBack={leaveProfile}
                   onPlans={toPlans} onVisit={visitProfile}
                   onInside={(id) => { setInsideRoom(id); setTab("inside"); }} />
        )}
        {tab === "chat" && <Chat onPlans={toPlans} />}
        {tab === "discover" && <Discover onPlans={toPlans} onVisit={visitProfile} />}
        {tab === "market" && <Market onPlans={toPlans} />}
        {tab === "shop" && <Shops onPlans={toPlans} />}
        {tab === "corner" && <Corner onPlans={toPlans} />}
        {tab === "wall" && <Wall onPlans={toPlans} />}
        {tab === "feed" && <Feed onPlans={() => setTab("plans")}
          onParty={(id) => { setOpenParty(id); setTab("party"); }} />}
        {tab === "friends" && <Friends onPlans={toPlans} onVisit={visitProfile} />}
        {tab === "rooms" && <Rooms onPlans={toPlans} onInside={(id) => { setInsideRoom(id); setTab("inside"); }} />}
        {tab === "blend" && <Blend onPlans={toPlans} />}
        {tab === "solitude" && <Solitude />}
        {tab === "simulate" && <Simulate onPlans={toPlans} />}
        {tab === "campaigns" && <Campaigns onPlans={toPlans} />}
        {tab === "org" && <Org onPlans={toPlans} />}
        {tab === "relationships" && <Relationships onPlans={toPlans} />}
        {tab === "memory" && <Memory onPlans={toPlans} />}
        {tab === "agent" && <Agent onPlans={toPlans}
                                  go={(id) => setTab(id as Tab)} />}
        {tab === "studio" && <Studio onPlans={toPlans} />}
        {tab === "delegate" && <Delegate onPlans={toPlans} />}
        {tab === "desk" && <Desk onPlans={toPlans} />}
        {/* Beginning and passing on left the sidebar deliberately: it is not
            a place anybody visits daily, it is an option taken from Identity
            when pre-building an account or deciding how it ends. */}
        {tab === "identity" && <Identity onPlans={toPlans} onPassing={() => setTab("passing")} />}
        {tab === "presence" && <Presence onPlans={toPlans} />}
        {tab === "live" && <Live onPlans={toPlans} />}
        {tab === "contest" && <Contest onPlans={toPlans} />}
        {tab === "guide" && <Guide onPlans={toPlans} />}
        {tab === "exchanges" && <Exchanges onPlans={toPlans} />}
        {tab === "grants" && <Grants onPlans={toPlans} />}
        {tab === "party" && <WatchParty onPlans={toPlans} start={openParty} />}
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
        {tab === "inside" && <Inside onPlans={toPlans} start={insideRoom} />}
        {tab === "signing" && <Signing />}
        {tab === "visiting" && <Visiting />}
        {tab === "allowed" && <Allowed />}
        {tab === "stranger" && <Stranger />}
        {tab === "themark" && <TheMark />}
        {tab === "inwords" && <InWords />}
        {tab === "remainder" && <Remainder />}
        {tab === "plugins" && <Plugins onPlans={toPlans} />}
        {tab === "named" && <Named onPlans={toPlans} />}
        {tab === "passing" && <Passing onPlans={toPlans} />}
        {tab === "robots" && <Robots onPlans={toPlans} />}
        {tab === "placements" && <Placements onPlans={toPlans} />}
        {tab === "plans" && <Plans />}
        {tab === "access" && <Access />}
        {tab === "matters" && <Matters />}
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
