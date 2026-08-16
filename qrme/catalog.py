"""The connected-apps catalog — what a plug-in storefront has to offer.

Beyond the social platforms (``routers/social.py``), a synthetic profile and its
agents can connect to the AI-integrated **apps** on a person's devices — the same
surfaces Apple Intelligence, Google Gemini, Microsoft Copilot and Canva expose.
Each entry declares:

- ``provider`` / ``app`` — who and what;
- ``capabilities`` — the AI features that app offers;
- ``directions`` — how a connector uses it:
    * ``collect`` — pull context in (build the profile / inform the agent),
    * ``act``     — drive the app agentically (create an event, run a shortcut),
    * ``produce`` — generate output (images, movies, designs).

This is reference data — read-only — that the connect flow validates against.

## Device AI was the whole list, and a storefront is not a device

The first six providers are all somebody's *hardware*: Apple Intelligence,
Gemini, Copilot, Canva, glasses, consoles. That is a real list and it is not
the list a person expects when they open something called plug-ins. What
they expect is the services their day already runs through — the inbox, the
calendar, the drive, the tracker, the payment processor — none of which are
device AI and none of which were here.

    asked     which AI features can a connector drive
    mattered  which of the person's own services can it reach at all

So three more kinds, each its own provider rather than more rows under an
existing one, because the difference between them is what the connector is
*allowed to do* and that difference should be legible in the storefront:

- ``work``   — the services a day runs through; most are ``collect``+``act``.
- ``search`` — reading the open web. Its own kind because the composer's plus
  menu has had a *search the web* entry waiting on a row to open, and went
  without one rather than ship a control that opens nothing.
- ``scrape`` — public social pages, ``collect`` **only**. See that section's
  own comment for why the restriction is load-bearing rather than tidy.
"""

from __future__ import annotations

# provider, app, label, capabilities, directions
_ROWS = [
    # ---- Apple Intelligence -------------------------------------------------
    ("apple", "photos", "Photos",
     ["semantic-search", "clean-up", "memory-movies", "spatial-reframe",
      "image-playground", "genmoji"], ["collect", "produce"]),
    ("apple", "calendar", "Calendar",
     ["nl-event", "suggested-reminders", "siri-actions"], ["collect", "act"]),
    ("apple", "mail", "Mail",
     ["thread-summary", "smart-reply", "priority", "order-tracking"], ["collect", "act"]),
    ("apple", "messages", "Messages",
     ["summaries", "smart-reply", "live-translation", "poll-suggestions",
      "context-suggestions", "backgrounds"], ["collect", "act"]),
    ("apple", "files", "Files", ["file-management"], ["collect", "act"]),
    ("apple", "notes", "Notes",
     ["transcription-summary", "intelligent-processing"], ["collect", "act"]),
    ("apple", "reminders", "Reminders",
     ["auto-categorize", "suggested", "nl-siri"], ["collect", "act"]),
    ("apple", "safari", "Safari",
     ["browsing-tools", "describe-extension"], ["collect", "act"]),
    ("apple", "shortcuts", "Shortcuts",
     ["intelligent-actions", "on-device-model"], ["act"]),
    ("apple", "passwords", "Passwords", ["weak-password-detect"], ["collect", "act"]),
    ("apple", "wallet", "Wallet", ["order-tracking"], ["collect"]),
    ("apple", "phone", "Phone & FaceTime",
     ["live-translation", "context-aware"], ["act"]),
    ("apple", "system", "System (Writing Tools · Siri · Visual Intelligence)",
     ["writing-tools", "siri", "visual-intelligence", "genmoji",
      "image-playground"], ["collect", "act", "produce"]),

    # ---- Google Gemini ------------------------------------------------------
    ("google", "photos", "Google Photos",
     ["nl-search", "personal-intelligence", "video-remix", "remix",
      "moods", "ask-photos"], ["collect", "produce"]),
    ("google", "calendar", "Google Calendar",
     ["nl-schedule", "live-automation"], ["collect", "act"]),
    ("google", "gmail", "Gmail",
     ["summaries", "smart-reply", "workspace-automation"], ["collect", "act"]),
    ("google", "keep", "Keep & Tasks",
     ["read-write", "multi-step"], ["collect", "act"]),
    ("google", "maps", "Maps",
     ["navigation", "location-tasks"], ["collect", "act"]),
    ("google", "chrome", "Chrome",
     ["sidebar-summary", "auto-browse"], ["collect", "act"]),
    ("google", "youtube", "YouTube",
     ["recommendations"], ["collect", "produce"]),
    ("google", "play_store", "Play Store",
     ["conversational-search", "install"], ["act"]),
    ("google", "gboard", "Gboard", ["typing-assist"], ["act"]),
    ("google", "files", "Files",
     ["file-handling", "appfunctions"], ["collect", "act"]),
    ("google", "system", "Gemini (agentic · Live · AppFunctions)",
     ["agentic-tasks", "gemini-live", "appfunctions", "autofill"],
     ["collect", "act", "produce"]),

    # ---- Microsoft Copilot --------------------------------------------------
    ("microsoft", "photos", "Photos",
     ["generative-erase", "restyle", "super-resolution", "relight",
      "auto-categorize", "semantic-search"], ["collect", "produce"]),
    ("microsoft", "file_explorer", "File Explorer",
     ["summarize", "extract", "nl-search", "ai-actions"], ["collect", "act"]),
    ("microsoft", "notepad", "Notepad", ["writing-tools"], ["act", "produce"]),
    ("microsoft", "paint", "Paint", ["cocreator", "image-gen"], ["produce"]),
    ("microsoft", "snipping_tool", "Snipping Tool", ["capture-ai"], ["collect"]),
    ("microsoft", "settings", "Settings", ["nl-settings"], ["act"]),
    ("microsoft", "m365", "Microsoft 365",
     ["drafting", "excel-analysis", "ppt-creation", "email-mgmt", "agents"],
     ["collect", "act", "produce"]),
    ("microsoft", "copilot", "Copilot (Vision · Recall · Click-to-Do)",
     ["vision", "voice", "recall", "click-to-do", "agents"],
     ["collect", "act", "produce"]),

    # ---- Canva Magic Studio -------------------------------------------------
    ("canva", "magic_studio", "Canva Magic Studio",
     ["magic-design", "magic-media", "magic-write", "magic-edit",
      "magic-switch", "magic-layers", "background-remover", "translate"],
     ["act", "produce"]),

    # ---- Smart glasses: capture the wearer's POV, render to the HUD --------
    # ``collect`` pulls the wearer's point of view (camera, audio, context)
    # in to inform the profile/agent; ``produce`` renders back to the lens —
    # a heads-up overlay, captions, or navigation the persona speaks/draws.
    ("glasses", "rayban_meta", "Ray-Ban Meta",
     ["capture-photo", "capture-video", "livestream", "pov-context",
      "voice", "hud-caption"], ["collect", "produce"]),
    ("glasses", "meta_display", "Meta Ray-Ban Display",
     ["capture-photo", "capture-video", "pov-context", "hud-overlay",
      "voice", "navigation-hud"], ["collect", "produce"]),
    ("glasses", "google_androidxr", "Google (Android XR)",
     ["capture-photo", "capture-video", "gemini-pov",
      "live-translation-hud", "navigation-hud"], ["collect", "produce"]),
    ("glasses", "xreal_air", "XREAL Air",
     ["capture-video", "ar-overlay", "spatial-display"],
     ["collect", "produce"]),

    # ---- Gaming consoles & platforms: capture play, produce highlights ----
    # The console connector captures the wearer's play (clips, screenshots,
    # session context) and produces highlights; agent-operated companions
    # play alongside through the gaming module (routers/gaming.py).
    ("gaming", "playstation", "PlayStation",
     ["capture-clip", "screenshot", "party-voice", "session-context",
      "highlight-reel"], ["collect", "produce"]),
    ("gaming", "xbox", "Xbox",
     ["capture-clip", "screenshot", "party-voice", "session-context",
      "highlight-reel"], ["collect", "produce"]),
    ("gaming", "nintendo", "Nintendo Switch",
     ["capture-clip", "screenshot", "session-context"],
     ["collect", "produce"]),
    ("gaming", "steam", "Steam (PC)",
     ["capture-clip", "screenshot", "voice", "session-context",
      "highlight-reel"], ["collect", "produce"]),
    ("gaming", "pc", "PC (cross-platform)",
     ["capture-clip", "screenshot", "voice", "session-context",
      "highlight-reel"], ["collect", "produce"]),
    # ---- Work and life: what a public plug-in directory actually lists ------
    #
    # Everything above is device AI — what Apple, Google and Microsoft put on
    # a person's own hardware. That is not what a plug-in directory shows
    # somebody, which is the services their day already runs through. A
    # storefront built on the rows above would have offered a person Genmoji
    # and not their inbox.
    ("work", "gmail", "Gmail", ["read", "send", "search", "labels"], ["collect", "act"]),
    ("work", "outlook", "Outlook Email", ["read", "send", "search", "rules"], ["collect", "act"]),
    ("work", "gcal", "Google Calendar", ["read", "schedule", "invite"], ["collect", "act"]),
    ("work", "outlook-cal", "Outlook Calendar", ["read", "schedule", "invite"], ["collect", "act"]),
    ("work", "drive", "Google Drive", ["docs", "sheets", "slides", "search"], ["collect", "act", "produce"]),
    ("work", "onedrive", "OneDrive", ["files", "search"], ["collect", "act"]),
    ("work", "dropbox", "Dropbox", ["files", "search"], ["collect", "act"]),
    ("work", "box", "Box", ["files", "search"], ["collect", "act"]),
    ("work", "notion", "Notion", ["pages", "databases", "search"], ["collect", "act", "produce"]),
    ("work", "confluence", "Confluence", ["pages", "search"], ["collect", "act"]),
    ("work", "slack", "Slack", ["read", "post", "search", "threads"], ["collect", "act"]),
    ("work", "teams", "Microsoft Teams", ["read", "post", "meetings"], ["collect", "act"]),
    ("work", "github", "GitHub", ["issues", "pull-requests", "ci", "publish"], ["collect", "act"]),
    ("work", "gitlab", "GitLab", ["issues", "merge-requests", "ci"], ["collect", "act"]),
    ("work", "jira", "Jira", ["issues", "boards", "search"], ["collect", "act"]),
    ("work", "linear", "Linear", ["issues", "cycles", "search"], ["collect", "act"]),
    ("work", "asana", "Asana", ["tasks", "projects"], ["collect", "act"]),
    ("work", "trello", "Trello", ["cards", "boards"], ["collect", "act"]),
    ("work", "monday", "monday.com", ["boards", "items"], ["collect", "act"]),
    ("work", "clickup", "ClickUp", ["tasks", "docs"], ["collect", "act"]),
    ("work", "airtable", "Airtable", ["bases", "records"], ["collect", "act"]),
    ("work", "hubspot", "HubSpot", ["contacts", "deals", "email"], ["collect", "act"]),
    ("work", "salesforce", "Salesforce", ["contacts", "opportunities"], ["collect", "act"]),
    ("work", "zendesk", "Zendesk", ["tickets", "search"], ["collect", "act"]),
    ("work", "intercom", "Intercom", ["conversations", "search"], ["collect", "act"]),
    ("work", "stripe", "Stripe", ["payments", "invoices", "customers"], ["collect", "act"]),
    ("work", "quickbooks", "QuickBooks", ["invoices", "expenses"], ["collect", "act"]),
    ("work", "xero", "Xero", ["invoices", "expenses"], ["collect", "act"]),
    ("work", "shopify", "Shopify", ["orders", "products", "customers"], ["collect", "act"]),
    ("work", "figma", "Figma", ["files", "comments", "export"], ["collect", "act", "produce"]),
    ("work", "granola", "Granola", ["meeting-notes", "context"], ["collect"]),
    ("work", "zoom", "Zoom", ["meetings", "recordings", "transcripts"], ["collect", "act"]),
    ("work", "calendly", "Calendly", ["availability", "booking"], ["collect", "act"]),
    ("work", "docusign", "DocuSign", ["envelopes", "signatures"], ["collect", "act"]),
    ("work", "twilio", "Twilio", ["sms", "voice"], ["act"]),
    ("work", "sendgrid", "SendGrid", ["email-send", "templates"], ["act"]),
    ("work", "spotify", "Spotify", ["library", "playlists", "playback"], ["collect", "act"]),
    ("work", "strava", "Strava", ["activities", "routes"], ["collect"]),
    ("work", "wikipedia", "Wikipedia", ["lookup", "citations"], ["collect"]),
    ("work", "arxiv", "arXiv", ["papers", "citations"], ["collect"]),
    ("work", "pubmed", "PubMed", ["papers", "citations"], ["collect"]),

    # ---- Reading the open web ----------------------------------------------
    #
    # Its own kind rather than four more `work` rows, because this is the one
    # a person means when they say *look it up* — and because the composer's
    # plus menu has had a "search the web" entry waiting on a row here, and
    # went without one rather than ship a control that opened nothing.
    ("search", "web", "Web search", ["query", "cite"], ["collect"]),
    ("search", "news", "News search", ["query", "cite", "recent"], ["collect"]),
    ("search", "scholar", "Scholarly search", ["query", "cite"], ["collect"]),
    ("search", "fetch", "Read a page", ["fetch", "extract", "cite"], ["collect"]),

    # ---- Social, read rather than posted to --------------------------------
    #
    # `routers/social.py` already connects a profile *to* a platform: it
    # publishes, through the same moderation pipeline as chat, and it verifies
    # a handle somebody pasted. This is the other half, and a different act —
    # reading a public page to learn from it, with no account on the far side
    # and nothing posted.
    #
    #     asked     can this profile appear on the platform
    #     mattered  can it read what is there
    #
    # Every row here is `collect` only, and that is load-bearing rather than
    # tidy: a scrape row that could `act` would be `social.py` again under a
    # different name, on a path with no moderation behind it. The platform
    # names match `social.py`'s `_HOST_PLATFORM` so the two halves cannot
    # drift into disagreeing about what a platform is called.
    ("scrape", "instagram", "Instagram", ["public-posts", "public-profile"], ["collect"]),
    ("scrape", "x", "X", ["public-posts", "public-profile"], ["collect"]),
    ("scrape", "tiktok", "TikTok", ["public-posts", "public-profile"], ["collect"]),
    ("scrape", "facebook", "Facebook", ["public-pages"], ["collect"]),
    ("scrape", "linkedin", "LinkedIn", ["public-profile", "public-posts"], ["collect"]),
    ("scrape", "youtube", "YouTube", ["public-videos", "transcripts"], ["collect"]),
    ("scrape", "reddit", "Reddit", ["public-threads", "subreddits"], ["collect"]),
    ("scrape", "threads", "Threads", ["public-posts"], ["collect"]),
    ("scrape", "mastodon", "Mastodon", ["public-posts"], ["collect"]),
    ("scrape", "twitch", "Twitch", ["public-streams", "clips"], ["collect"]),
    ("scrape", "pinterest", "Pinterest", ["public-boards"], ["collect"]),
    ("scrape", "snapchat", "Snapchat", ["public-stories"], ["collect"]),
    ("scrape", "roblox", "Roblox", ["public-profile", "public-games"], ["collect"]),
    ("scrape", "discord", "Discord", ["public-servers"], ["collect"]),
    ("scrape", "whatsapp", "WhatsApp", ["public-channels"], ["collect"]),
    ("scrape", "meta", "Meta", ["public-pages"], ["collect"]),
]

_PROVIDER_LABEL = {
    "apple": "Apple Intelligence",
    "google": "Google Gemini",
    "microsoft": "Microsoft Copilot",
    "canva": "Canva Magic Studio",
    "glasses": "Smart Glasses",
    "gaming": "Gaming Consoles & Platforms",
    "work": "Work & life",
    "search": "Reading the open web",
    "scrape": "Social, read not posted to",
}

# ---------------------------------------------------------------------------
# What a connector needs before it can reach the far side
#
# A storefront draws a lock beside some rows and a plus beside others, and the
# lock has to mean something. Here it means exactly one thing: **this
# connector cannot reach the service until somebody gives it a credential.**
#
#     asked     which apps can this profile connect
#     mattered  which of them can actually reach anything once connected
#
# Three postures, and the third is the honest one for most of the board:
#
#   nothing   Public. Anyone with a browser could read it, so the connector
#             needs no account and holds no secret — the scrape rows, reading
#             a page, and the open reference sources.
#   sign-in   The person's own account on the far side. A Gmail connector
#             without the person's Google account is a name and no inbox.
#   key       An operator credential — a search API, an SMS gateway. Not the
#             person's to give; the deployment either holds it or does not.
#
# This is declared per provider with per-app exceptions, because the credential
# is a property of who is on the other end rather than of the individual app,
# and a per-row sixth field would be a hundred more places for the answer to
# drift. `routers/apps.py` turns it into the refusal a person actually meets.
_NEEDS_PROVIDER = {
    "apple": "sign-in", "google": "sign-in", "microsoft": "sign-in",
    "canva": "sign-in", "glasses": "sign-in", "gaming": "sign-in",
    "work": "sign-in", "search": "key", "scrape": "nothing",
}

#: Rows whose posture is not their provider's. All of them are public sources
#: that happen to sit in a family of private ones, or gateways that take an
#: operator key inside a family of personal accounts.
_NEEDS_APP = {
    ("search", "fetch"): "nothing",       # reading a page anyone can read
    ("work", "wikipedia"): "nothing",
    ("work", "arxiv"): "nothing",
    ("work", "pubmed"): "nothing",
    ("work", "twilio"): "key",            # the operator's gateway, not yours
    ("work", "sendgrid"): "key",
}

NEEDS = ("nothing", "sign-in", "key")


def needs(provider: str, app: str) -> str:
    """What this connector must be given before it can reach anything."""
    return _NEEDS_APP.get((provider, app),
                          _NEEDS_PROVIDER.get(provider, "sign-in"))


CONNECTORS = [
    {"provider": p, "app": a, "label": lbl, "capabilities": caps,
     "directions": dirs, "needs": needs(p, a)}
    for (p, a, lbl, caps, dirs) in _ROWS
]

# Fast lookup for validation: (provider, app) -> entry.
BY_KEY = {(c["provider"], c["app"]): c for c in CONNECTORS}


def catalog() -> dict:
    """The full catalog, grouped by provider (for the connect picker)."""
    groups: dict[str, dict] = {}
    for c in CONNECTORS:
        g = groups.setdefault(c["provider"], {
            "provider": c["provider"],
            "label": _PROVIDER_LABEL[c["provider"]],
            "apps": [],
        })
        g["apps"].append({"app": c["app"], "label": c["label"],
                          "capabilities": c["capabilities"],
                          "directions": c["directions"], "needs": c["needs"]})
    return {"providers": list(groups.values()),
            "app_count": len(CONNECTORS),
            "provider_count": len(groups)}
