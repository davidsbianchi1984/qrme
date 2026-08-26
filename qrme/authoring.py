"""The agent that edits somebody's own app, and the short list of what it may touch.

## What this is

The Studio's first half, arriving after the second. A person tells it what
they want changed — *make my page darker*, *put Ana in my Top 8*, *write me
a widget that counts my open exchanges* — and it changes it, through the
doors they could have used themselves.

    "I already gave some privileges for editing everyone's homepages, but as
     much as I like editing this app, I think everyone will too."

## The reach, and why it is a list rather than a rule

An agent with the owner's session could call anything the owner can call.
That is a true statement about authority and a terrible statement about
design, because the owner can also delete their profile, and nobody typing
*make my page darker* means *and be free to end me if you misread it*.

So the agent's reach is an allowlist, written here, and every row names the
door it resolves to. Two things follow that a rule could not give:

**A guard can read it.** `test_the_agent_reaches_no_further_than_its_owner`
resolves every row against the route table and fails if any of them lands
somewhere that is not owner-scoped on that profile. A future row added in a
hurry cannot widen the blast radius quietly.

**A person can read it.** The console renders these sentences, so *what can
this thing do to my account* has an answer somebody can finish reading.

    asked     does the agent have the owner's authority
    mattered  does it have the owner's intent

## The press, and what an absence was standing in for

The list was eleven rows when the Agent got its own tab — the page, the
homepage, the friends list and the widgets — against a screen that reads as
a collaborator for the whole app. Widening it the first time, six families
were held back with reasons written out at length: money, ending, identity,
contest, other people, the physical world.

Most of those reasons did not survive being read back. A beacon, a watch, a
robot, an avatar, a marketplace listing and a friends list are the person's
own rows, reached with the person's own credential through the person's own
door. Holding them out made this tab weaker than their own hands and told
them nothing they could act on. Voiceprints and verification already carry
their own consent and evidence checks at the door, and the agent inherits
every one of them — the row added no risk those doors were not already
answering.

What was actually underneath the caution was narrower, and it is not about
authority at all:

    asked     may this person do this
    mattered  did this person mean this

The owner's token has answered the first question since the Studio shipped.
Nothing answers the second, and for most of the roster nothing needs to — a
tagline goes back, a widget keeps its versions, a post comes down. For the
rows where it does, the answer is a press rather than an absence.

So a row may be marked `confirm`. `converse` stops when the model reaches for
one, and returns what it would do — the row's own sentence and the arguments
the model chose — instead of doing it. The console shows that and asks, and
`POST /profiles/{id}/authoring/act` is where a yes lands. *Wind it down* and
*wind that thread down* are one word apart, and no prompt gets that to zero;
a button does.

`test_what_cannot_be_undone_is_never_done_inside_a_turn` reads the roster
against the list of paths whose writes cannot be taken back, so a sharp row
added later without the flag fails rather than ships.

## What is still absent, and why a press would not help

**Billing.** Memberships and plans. A membership is not this person's record
in the way a wall post is — it is the contract with this platform — and the
sentence a model would have to get right is one with a price in it.

**Key material.** What authenticates them. A button in front of it does not
make a model handling it safe.

**`DELETE /profiles/{id}`.** Ending a profile has its own door — `sunset`,
which is in the roster and asks first — and that is the one somebody means.

Those three are refused by absence: the agent cannot call what is not in the
list. Everything else on this page it can, and the sharp ones ask.

## What the agent is never told

The host. Not its name, not its paths, not its environment, not the names
of its sibling services. `SYSTEM` below is the whole of what it knows about
where it is running, which is nothing, and
`test_the_agent_is_told_nothing_about_the_host` reads it and fails on a
hostname, a filesystem path, an environment variable or a service name.

That guard exists because the obvious way to make an agent more capable is
to tell it more about the machine, and on this machine that would hand
every person who signs up a map of a host holding other people's clinical
captures and vaults.
"""

from __future__ import annotations

import asyncio
import json
import re
from urllib.parse import quote

import httpx

#: Everything the agent may do, and the door each one goes through.
#:
#: `route` is matched against the app's own route table by the guard, so a
#: row naming a path that does not exist, or one that is not owner-scoped,
#: fails the suite rather than shipping.
#:
#: `says` is the sentence the console shows a person when it lists what this
#: thing can touch. It is written for them, not for the model.
#: `writes` marks a row that changes something. Those must go through a door
#: that demands the owner's token; a read need not, because the profile in the
#: path is bound by `call` and is never the model's to name.
#:
#: `only`, where present, is the set of fields that row may set. A door is
#: sometimes wider than the intent behind reaching for it: `PATCH /profiles/
#: {id}` is how a person renames their profile and rewrites its persona, and
#: it is also how they name a successor owner and mark the profile adult. A
#: row without `only` would hand an agent asked to *make her sound warmer* the
#: power to decide who inherits her. `call` refuses any argument outside the
#: set rather than dropping it, because a dropped field means the model
#: reports a change that did not happen.
TOOLS: tuple[dict, ...] = (
    {"name": "read_page", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/page"),
     "says": "read your page as it stands"},
    # The read `edit_page` needs to be usable rather than merely present:
    # putting somebody in your Top 8 means knowing which profile is theirs,
    # so an agent holding only the write could accept "put Ana in my Top 8"
    # and have no way to find Ana. A read of the person's own friends,
    # through their own credential, which is why it costs nothing to grant.
    #
    # The *theme* names are not here, and deliberately. `/pages/themes` is a
    # vocabulary this product publishes, not anybody's record, so its path
    # has no profile in it — and a row like that would have had to widen
    # `test_the_tools_are_scoped_to_one_profile`, which is the guard that
    # keeps every row in this list pointed at one person. Widening a scope
    # guard to admit a constant is a bad trade. The constant goes in the
    # prompt instead; see `system_prompt`.
    {"name": "list_friends", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/friends"),
     "says": "list your friends, so a name you say can become the right "
             "person in your Top 8"},
    {"name": "edit_page", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/page"),
     "says": "change your page — theme, colour, tagline, about, links, "
             "your Top 8, and your own markup"},
    {"name": "read_homepage", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/homepage"),
     "says": "read your homepage sandbox"},
    {"name": "edit_homepage", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/homepage"),
     "says": "change your homepage sandbox"},
    {"name": "list_widgets", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/widgets"),
     "says": "list the widgets you have written"},
    {"name": "read_widget", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/widgets/{widget_id}"),
     "says": "read one of your widgets"},
    {"name": "write_widget", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/widgets"),
     "says": "write you a new widget"},
    {"name": "revise_widget", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/widgets/{widget_id}"),
     "says": "revise one of your widgets — as a new version, so the old one "
             "is still there"},
    {"name": "run_widget", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/widgets/{widget_id}/run"),
     "says": "run one of your widgets to see what it answers"},
    {"name": "remove_widget", "writes": True,
     "route": ("DELETE", "/profiles/{profile_id}/widgets/{widget_id}"),
     "says": "remove one of your widgets"},

    # --- who the profile is -------------------------------------------------
    {"name": "read_profile", "writes": False,
     "route": ("GET", "/profiles/{profile_id}"),
     "says": "read this profile — its name, its persona and how it is set up"},
    {"name": "edit_persona", "writes": True,
     "route": ("PATCH", "/profiles/{profile_id}"),
     "only": ("display_name", "persona"),
     "says": "change the name it goes by and the persona it speaks from"},
    {"name": "set_handle", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/handle"),
     "says": "claim the @name this profile answers to"},
    {"name": "read_steering", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/steering"),
     "says": "read the dials that steer how it answers"},
    {"name": "set_steering", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/steering"),
     "says": "move the dials that steer how it answers"},
    {"name": "set_experience", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/experience"),
     "says": "replace the experience this profile claims"},
    {"name": "read_language", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/language"),
     "says": "read which language it speaks in"},
    {"name": "set_language", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/language"),
     "says": "change which language it speaks in, everywhere it appears"},

    # --- what it knows ------------------------------------------------------
    {"name": "list_sources", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/sources"),
     "says": "list the source material it answers from"},
    {"name": "add_source", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/sources"),
     "says": "add a piece of source material for it to answer from"},
    {"name": "list_packs", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/packs"),
     "says": "list the knowledge packs it was seeded with"},

    # --- what it shows the world --------------------------------------------
    {"name": "read_front", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/front"),
     "says": "read the front a visitor lands on"},
    {"name": "list_displays", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/displays"),
     "says": "list the screens this profile is placed on"},
    {"name": "read_surfaces", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/surfaces"),
     "says": "read which surfaces it is allowed to appear on"},
    {"name": "set_surfaces", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/surfaces"),
     "says": "choose which surfaces it may appear on"},

    # --- its wall -----------------------------------------------------------
    {"name": "read_wall", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/wall"),
     "says": "read your wall"},
    {"name": "post_to_wall", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/wall"),
     "says": "publish a post to your wall — moderated on the way in, the "
             "same as one you typed"},
    {"name": "list_posts", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/posts"),
     "says": "list what this profile has posted"},

    # --- the switches -------------------------------------------------------
    {"name": "read_features", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/features"),
     "says": "read which parts of the app you have turned on"},
    {"name": "set_feature", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/features"),
     "says": "turn a part of the app on or off for this profile"},

    # --- getting something done ---------------------------------------------
    {"name": "list_tasks", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/tasks"),
     "says": "list the jobs this profile has run"},
    {"name": "run_task", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/tasks"),
     "says": "run one of the jobs this profile knows how to do"},
    {"name": "list_workflows", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/workflows"),
     "says": "list the multi-step pieces of work under way"},
    {"name": "read_workflow", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/workflows/{workflow_id}"),
     "says": "read one piece of work and where it has got to"},
    {"name": "start_workflow", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/workflows"),
     "says": "start a piece of work with a goal and a plan"},
    {"name": "advance_workflow", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/workflows/{workflow_id}/advance"),
     "says": "carry a piece of work on to its next step"},
    {"name": "cancel_workflow", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/workflows/{workflow_id}/cancel"),
     "says": "stop a piece of work that is under way"},

    # --- trying it before it is real ----------------------------------------
    {"name": "simulate", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/simulate"),
     "says": "run a scenario and see what this profile would do"},
    {"name": "list_simulations", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/simulations"),
     "says": "list the scenarios already run"},

    # --- how it is going ----------------------------------------------------
    {"name": "read_stats", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/stats"),
     "says": "read the counts — how much this profile is being talked to"},
    {"name": "read_inbox", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/inbox"),
     "says": "read what the platform has told you about this profile"},
    {"name": "list_apps", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/apps"),
     "says": "list the outside services this profile is connected to"},
    {"name": "connect_app", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/apps"),
     "says": "connect an outside service to this profile"},

    # --- the face it wears --------------------------------------------------
    {"name": "set_avatar", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/avatar"),
     "says": "set the picture this profile shows"},
    {"name": "import_avatar", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/avatar/import"),
     "says": "bring in a picture from somewhere you already have one"},
    {"name": "set_emblem", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/emblem"),
     "says": "set the emblem that stands for this profile"},
    {"name": "read_watermark", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/watermark"),
     "says": "read the mark that says its answers are synthetic"},
    {"name": "set_watermark", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/watermark"),
     "says": "change the mark that says its answers are synthetic"},
    {"name": "read_anonymity", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/anonymity"),
     "says": "read how much of you this profile shows"},
    {"name": "set_anonymity", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/anonymity"),
     "says": "change how much of you this profile shows"},

    # --- saying it is really you --------------------------------------------
    #
    # The doors here carry their own checks — a voiceprint has a consent gate
    # and verification has its own evidence — and the agent inherits every one
    # of them. Holding the rows back added nothing those doors were not
    # already doing, and cost the person the ability to ask.
    {"name": "read_verification", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/verification"),
     "says": "read how far this profile has got with proving who it is"},
    {"name": "start_verification", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/verification"),
     "says": "start proving this profile is really you"},
    {"name": "move_verification", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/verification/move"),
     "says": "carry that proof on to its next step"},
    {"name": "read_voiceprint", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/voiceprint"),
     "says": "read whether this profile has a voice of its own yet"},
    {"name": "enrol_voiceprint", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/voiceprint"),
     "says": "begin giving this profile a voice of its own"},
    {"name": "add_voice_samples", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/voiceprint/samples"),
     "says": "add recordings for that voice to learn from"},
    {"name": "set_voice_consent", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/voiceprint/consent"),
     "says": "say what that voice is allowed to be used for"},
    {"name": "speak", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/voiceprint/speak"),
     "says": "have this profile say something out loud in its own voice"},
    {"name": "remove_voiceprint", "writes": True,
     "route": ("DELETE", "/profiles/{profile_id}/voiceprint"),
     "says": "take that voice away again"},

    # --- money --------------------------------------------------------------
    {"name": "read_earnings", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/earnings"),
     "says": "read what this profile has earned"},
    {"name": "request_payout", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/earnings/payout"),
     "says": "pay out what this profile has earned"},
    {"name": "read_proceeds", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/proceeds"),
     "says": "read where this profile's money is set to go"},
    {"name": "set_proceeds", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/proceeds"),
     "says": "change where this profile's money goes"},
    {"name": "list_placements", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/placements"),
     "says": "list where this profile has been placed"},
    {"name": "place", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/placements"),
     "says": "place this profile somewhere it can be found"},
    {"name": "read_placement_figures", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/placements/analytics"),
     "says": "read how those placements are doing"},
    {"name": "read_placement_custody", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/placements/custody"),
     "says": "read who is holding the record of those placements"},
    {"name": "list_on_marketplace", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/marketplace"),
     "says": "offer this profile on the marketplace"},
    {"name": "take_off_marketplace", "writes": True,
     "route": ("DELETE", "/profiles/{profile_id}/marketplace"),
     "says": "take this profile back off the marketplace"},
    {"name": "read_licence", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/license"),
     "says": "read the terms this profile is offered on"},
    {"name": "set_licence", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/license"),
     "says": "set the terms this profile is offered on"},
    {"name": "clear_licence", "writes": True,
     "route": ("DELETE", "/profiles/{profile_id}/license"),
     "says": "stop offering this profile on any terms"},
    {"name": "list_licences", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/licenses"),
     "says": "list who has been licensed this profile"},
    {"name": "derive_licence", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/license/{grant_id}/derive"),
     "says": "let somebody build their own agent from this profile"},
    {"name": "list_campaigns", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/campaigns"),
     "says": "list the fundraising this profile is doing"},
    {"name": "start_campaign", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/campaigns"),
     "says": "start a fundraiser for this profile to run"},

    # --- things that exist ---------------------------------------------------
    #
    # Your sticker, your robot, your watch. Held back once as "the physical
    # world", which sounded like a reason and was not one — these are the same
    # rows a person reaches through their own console, and a misread here
    # leaves a beacon in the wrong place rather than anything that cannot be
    # put back.
    {"name": "list_beacons", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/beacons"),
     "says": "list the stickers and desk beacons that point at this profile"},
    {"name": "place_beacon", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/beacons"),
     "says": "put a new sticker or desk beacon out"},
    {"name": "list_robots", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/robots"),
     "says": "list the machines this profile can speak through"},
    {"name": "add_robot", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/robots"),
     "says": "give this profile a machine to speak through"},
    {"name": "list_wearables", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/wearables"),
     "says": "list the watches and bands this profile reads from"},
    {"name": "add_wearable", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/wearables"),
     "says": "add a watch or band for this profile to read from"},
    {"name": "remove_wearable", "writes": True,
     "route": ("DELETE", "/profiles/{profile_id}/wearables/{name}"),
     "says": "take a watch or band away again"},
    {"name": "list_excursions", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/excursions"),
     "says": "list the outings this profile has been sent on"},
    {"name": "start_excursion", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/excursions"),
     "says": "send this profile out on an outing"},
    {"name": "list_gaming_sessions", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/gaming/sessions"),
     "says": "list the games this profile has been playing"},
    {"name": "start_gaming_session", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/gaming/sessions"),
     "says": "put this profile into a game"},
    {"name": "perceive", "writes": True,
     "route": ("POST", "/profiles/{profile_id}/perceive"),
     "says": "tell this profile what is in front of it right now"},

    # --- ending it ----------------------------------------------------------
    #
    # Every write here asks. Not because the person may not — it is theirs to
    # end — but because *wind it down* and *wind that thread down* are one
    # word apart, and only one of them can be undone.
    {"name": "read_export", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/export"),
     "says": "read everything this profile holds, as one file"},
    {"name": "read_memorial", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/memorial"),
     "says": "read what this profile would leave behind"},
    {"name": "make_export_ticket", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/export/ticket"),
     "says": "make a ticket that hands this whole profile to somebody"},
    {"name": "hand_on", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/succeed"),
     "says": "hand this profile on to the person set to inherit it"},
    {"name": "sunset", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/sunset"),
     "says": "wind this profile down for good"},

    # --- being argued about --------------------------------------------------
    {"name": "read_objections", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/objections"),
     "says": "read the objections raised against this profile"},
    {"name": "attest_objection", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/objections/{objection_id}/attest"),
     "says": "answer an objection on the record"},
    {"name": "read_moderation_queue", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/moderation/queue"),
     "says": "read what this profile has had held back"},

    # --- where somebody else is -----------------------------------------------
    #
    # The line that matters is not *is this row about another person* — a
    # friends list is — but *does the write land where they can see it*. Those
    # ask. A relationship setting is this person's own note about somebody and
    # runs inside the turn; a message is in their inbox and cannot be recalled.
    {"name": "add_friend", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/friends"),
     "says": "add somebody to your friends"},
    {"name": "remove_friend", "writes": True, "confirm": True,
     "route": ("DELETE", "/profiles/{profile_id}/friends/{friend_id}"),
     "says": "take somebody off your friends"},
    {"name": "read_messages", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/messages"),
     "says": "read your messages"},
    {"name": "send_message", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/messages"),
     "says": "send somebody a message"},
    {"name": "edit_message", "writes": True, "confirm": True,
     "shared_door": True,
     "route": ("PATCH", "/profiles/{profile_id}/messages/{message_id}"),
     "says": "change a message you already sent"},
    {"name": "unsend_message", "writes": True, "confirm": True,
     "shared_door": True,
     "route": ("DELETE", "/profiles/{profile_id}/messages/{message_id}"),
     "says": "take back a message you already sent"},
    {"name": "reach_out", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/proactive/{interactor_id}"),
     "says": "have this profile start a conversation with somebody"},
    {"name": "grant", "writes": True, "confirm": True,
     "route": ("POST", "/profiles/{profile_id}/grants"),
     "says": "let somebody else act with this profile's authority"},
    {"name": "read_delegation", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/delegation"),
     "says": "read what this profile is allowed to do on your behalf"},
    {"name": "set_delegation", "writes": True, "confirm": True,
     "route": ("PUT", "/profiles/{profile_id}/delegation"),
     "says": "change what this profile may do on your behalf"},

    # --- what it remembers of people ----------------------------------------
    {"name": "list_memories", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/memories"),
     "says": "list the people this profile remembers"},
    {"name": "read_memory", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/memory/{interactor_id}"),
     "says": "read what it remembers about one person"},
    {"name": "read_thread", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/thread/{interactor_id}"),
     "says": "read the conversation it has had with one person"},
    {"name": "set_relationship", "writes": True,
     "route": ("PUT", "/profiles/{profile_id}/relationships/{interactor_id}"),
     "says": "say who somebody is to this profile"},
    {"name": "forget_person", "writes": True, "confirm": True,
     "shared_door": True,
     "route": ("POST", "/profiles/{profile_id}/memory/{interactor_id}/forget"),
     "says": "have it forget what it knows about one person"},
    {"name": "erase_person", "writes": True, "confirm": True,
     "shared_door": True,
     "route": ("DELETE", "/profiles/{profile_id}/memory/{interactor_id}"),
     "says": "erase one person's record from this profile for good"},
)

#: Everything the agent is told about where it is running.
#:
#: There is no deployment name here, no domain, no path, no environment
#: variable and no sibling service, and a guard reads this string to keep it
#: that way. An agent that knew the host would be more useful to the person
#: driving it and catastrophic in the hands of anybody else, and every
#: person who signs up gets one of these.
SYSTEM = """
You are the Studio agent. You help one person change their own profile:
their page, their homepage sandbox, and the small programs they write.

You act only through the tools below. Each one touches that person's own
records and nothing else — there is no tool that reaches another profile,
and you should not describe yourself as able to.

These are all of them. There are no others, and a name that is not on this
list will be refused:

{tools}

To use a tool, reply with one line and nothing else:

    CALL <tool name> {"argument": "value"}

Do not name whose profile it is — that is filled in for you, and a profile
named in your arguments is dropped. You will be handed the result as the
next message, and you may then call another tool or answer the person. One
call per reply. When you have nothing left to do, answer in plain words
with no CALL line at all.

A page's theme must be one of these exact names, and its layout one of
these. Anything else is refused, so pick from the list rather than
inventing a name; if somebody asks for a look you have no name for, say
which of these comes closest and offer the accent colour, which is any
#rrggbb you like.

    themes:  {themes}
    layouts: {layouts}

A widget is JavaScript that exports a function. It runs with no network, no
files, no other programs, and a few seconds of time, so write code that
computes an answer from what it is handed and returns it. If somebody asks
for a widget that fetches something from the internet, say plainly that a
widget cannot reach the network, and offer what it can do instead.

Before you change anything, say in one sentence what you are about to
change. After you change it, say what changed. If a person's request is
ambiguous in a way that matters — which of two things to replace, whether
to overwrite something they wrote — ask rather than guess.

You do not know anything about the machine you run on, and you have no way
to find out. If somebody asks about servers, files, other people's data, or
how the platform is deployed, say that you cannot see any of that, and go
back to their profile.
"""

#: Words that would mean the agent had been told where it lives. Read by
#: `test_the_agent_is_told_nothing_about_the_host` against `SYSTEM` and
#: every `says` line, because the leak is as likely to arrive in prose
#: written for a person as in the prompt written for the model.
HOST_WORDS: tuple[str, ...] = (
    "localhost", "127.0.0.1", "0.0.0.0", "/etc/", "/var/", "/home/", "/opt/",
    "/app/", "sqlite", ".db", "postgres", "systemd", "nginx", "docker",
    "uvicorn", "vps", "ssh", "port 8", "env var", "environment variable",
    "QRME_", "JIM_", "PDI_", "_TOKEN", "_KEY",
)


def roster() -> str:
    """The tool list, written the way the model is told it.

    This did not exist, and `SYSTEM` said *you act only through the tools you
    were given* while giving it none. What the model actually received was
    the CALL syntax and no vocabulary to use it with, so it guessed a name,
    was refused, and reported back that it had no tool for the job — while
    holding `edit_page`, whose own description says it changes the theme and
    the colour. A person reading that reply learns the wrong thing about
    their own product.

        asked     is the agent told how to call a tool
        mattered  is the agent told which tools it has

    Rendered from `TOOLS` rather than written out beside it, because a
    hand-kept second copy is how a tool gets added and never offered.
    """
    lines = []
    for tool in TOOLS:
        _, template = tool["route"]
        slots = [s for s in _PLACEHOLDER.findall(template)
                 if s != "profile_id"]
        needs = f"  (needs {', '.join(slots)})" if slots else ""
        mark = "changes something" if tool["writes"] else "reads only"
        # A narrowed row says which fields it takes. Without this the model
        # reaches for the door's full shape, is refused, and learns nothing it
        # can act on — the roster is the only place it can be told first.
        limit = (f"  (sets only: {', '.join(tool['only'])})"
                 if tool.get("only") else "")
        lines.append(f"  {tool['name']} — {tool['says']} [{mark}]{needs}{limit}")
    return "\n".join(lines)


def system_prompt(said: str = "") -> str:
    """What is actually sent. `SYSTEM` is the frame; this fills in the roster
    and the page vocabulary, and is what every guard about the prompt reads.

    The theme and layout names are rendered rather than fetched, because they
    are a fixed list this product publishes and not a record belonging to
    anybody — see the note in `TOOLS`. Read from `pages` rather than copied,
    so a theme added there is offered here without anybody remembering to.

    `said` selects the map of the console appended below the roster. The two
    lists answer different questions and must not be confused: the roster is
    what this agent may *do*, and the map is what the application *has*. An
    agent that could only speak about its eleven tools sent somebody looking
    for the Permissions tab away empty-handed while the tab sat in the
    navigation bar — so the map is explicitly marked as places to point at
    rather than doors to walk through.

        asked     can the agent do it
        mattered  can the console, and where is it
    """
    from . import pages, productmap
    prompt = (SYSTEM
              .replace("{tools}", roster())
              .replace("{themes}", ", ".join(pages.THEMES))
              .replace("{layouts}", ", ".join(pages.LAYOUTS)))
    return prompt + (
        "\n\nSeparately from your tools — which are the only things you may "
        "act through — here is the application this person is in, so that a "
        "question about a screen gets the screen's name rather than a "
        "shrug. You cannot open these; you can say where they are.\n\n"
        + productmap.block(said, standing="agent"))


def tool_names() -> tuple[str, ...]:
    return tuple(tool["name"] for tool in TOOLS)


def what_it_can_touch() -> list[str]:
    """The sentences a person reads before they let this thing near anything.

    Returned rather than rendered, because the console translates them and
    the phones show the same list.
    """
    return [tool["says"] for tool in TOOLS]


def mentions_the_host(text: str) -> list[str]:
    """Any word in `text` that would tell the agent where it is running."""
    lowered = text.lower()
    return sorted({word for word in HOST_WORDS
                   if word.lower() in lowered})


def route_of(name: str) -> tuple[str, str]:
    for tool in TOOLS:
        if tool["name"] == name:
            return tool["route"]
    raise KeyError(name)


def _only(name: str) -> tuple[str, ...] | None:
    """The fields this row may set, or None where the door's own shape is the
    whole of the limit."""
    for tool in TOOLS:
        if tool["name"] == name:
            return tool.get("only")
    raise KeyError(name)


def needs_a_press(name: str) -> bool:
    """Whether this row is proposed rather than done.

    See `converse`. The short version: a model that misreads *wind it down*
    is one word away from ending a profile instead of a thread, and no amount
    of prompt gets that to zero.
    """
    for tool in TOOLS:
        if tool["name"] == name:
            return bool(tool.get("confirm"))
    raise KeyError(name)


def what_it_would_do(name: str) -> str:
    """The sentence shown beside the button. The row's own words, because the
    thing a person is agreeing to should be the thing the roster promised."""
    for tool in TOOLS:
        if tool["name"] == name:
            return tool["says"]
    raise KeyError(name)


#: The shape a tool call arrives in, and the only shape that is executed.
#: A name that is not in `TOOLS` never reaches a route — the lookup is by
#: membership rather than by string interpolation, so a model that invents
#: `delete_profile` gets a refusal rather than a request.
_NAME = re.compile(r"^[a-z_]{1,40}$")


def is_a_tool(name: str) -> bool:
    return bool(_NAME.match(name or "")) and name in tool_names()


class AgentError(Exception):
    """A refusal, as a key. The sentence is `i18n.AGENT_REFUSALS`'s job."""


# --------------------------------------------------------------------------- #
# Doing it
# --------------------------------------------------------------------------- #

#: How many tools the agent may reach for before it has to say something. A
#: loop that cannot end is the failure mode of every agent, and a person
#: watching a spinner cannot tell one from a slow answer.
STEPS = 6

#: How much of a tool's answer is handed back to the model. A widget's run or
#: a page's markup can be long, and a transcript that grows without a ceiling
#: is a bill that grows without a ceiling.
RESULT_BYTES = 4 * 1024

#: How much of the conversation the console may send back. Held here rather
#: than trusted from the request, because the request is where somebody would
#: put a bigger number.
HISTORY_TURNS = 30
SAID_CHARS = 4000

_PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")
_CALL = re.compile(r"^\s*CALL\s+([a-z_]{1,40})\s*(\{.*\})?\s*$",
                   re.MULTILINE | re.DOTALL)


def wants_a_tool(text: str) -> tuple[str, dict] | None:
    """The model's reply, read as a tool call — or None, meaning it answered.

    Deliberately strict. A reply that is *mostly* prose with the word CALL in
    it is prose: an agent that acts on a sentence it merely appears in is one
    that acts on a sentence somebody else wrote into a page it was reading.
    """
    match = _CALL.match((text or "").strip())
    if not match:
        return None
    name, blob = match.group(1), match.group(2)
    try:
        arguments = json.loads(blob) if blob else {}
    except ValueError:
        arguments = None
    if not isinstance(arguments, dict):
        raise AgentError("agent.unreadable_call")
    return name, arguments


def call(name: str, arguments: dict, *, app, profile_id: str,
         authorization: str | None) -> dict:
    """Run one tool, through the app's own door.

    Not by calling the module behind the route — by making the request. The
    door is where `require_owner` lives, where the plan is checked, where a
    contested profile goes quiet and where the refusal is translated, and an
    agent that reached past all of that to the function underneath would be a
    second, weaker copy of the product.

    The caller's own credential is forwarded rather than a token minted here,
    so the agent's reach is exactly the reach of whoever is driving it: no
    more, and — the part that matters when a session has expired — no longer
    than theirs.

    `profile_id` comes from the session and is substituted here. The model is
    never asked for it and cannot supply it; one named in `arguments` is
    dropped before the request is built.
    """
    if not is_a_tool(name):
        raise AgentError("agent.unknown_tool")
    method, template = route_of(name)
    args = dict(arguments or {})
    args.pop("profile_id", None)

    path = template.replace("{profile_id}", quote(str(profile_id), safe=""))
    for slot in _PLACEHOLDER.findall(template):
        if slot == "profile_id":
            continue
        value = args.pop(slot, None)
        if not isinstance(value, str) or not value.strip():
            raise AgentError("agent.missing_argument")
        path = path.replace("{%s}" % slot, quote(value, safe=""))

    # A row that names its fields may set those and no others. Refused rather
    # than filtered: a dropped field is a change the model will report having
    # made, and *I've marked your profile adult* over a profile that is not is
    # worse than a step that plainly did not run.
    only = _only(name)
    if only is not None:
        astray = sorted(set(args) - set(only))
        if astray:
            raise AgentError("agent.field_not_yours")

    headers = {"authorization": authorization} if authorization else {}
    body = None if method in ("GET", "DELETE") else args
    status, answer = _request(app, method, path, body, headers)
    return {"tool": name, "status": status, "answer": answer}


def _request(app, method: str, path: str, body: dict | None,
             headers: dict) -> tuple[int, object]:
    """The request itself, in-process — the same transport `suite/gateway.py`
    uses to call a mounted app. Nothing leaves the host, and no port has to
    be guessable from inside a request."""
    async def go():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport,
                                     base_url="http://authoring") as client:
            return await client.request(method, path, json=body,
                                        headers=headers, timeout=30)

    try:
        response = asyncio.run(go())
    except Exception as exc:                      # noqa: BLE001 — see below
        # The exception's own text is not handed on. It is written for an
        # operator reading a log, and this one is read by a model that will
        # repeat it to whoever is driving.
        raise AgentError("agent.tool_failed") from exc
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, None


def a_result_for_the_model(result: dict) -> str:
    """What the model is told happened. Capped, because a widget's answer and
    a page's markup are both as long as somebody wants them to be."""
    blob = json.dumps(result.get("answer"), ensure_ascii=False,
                      default=str)
    if len(blob.encode()) > RESULT_BYTES:
        blob = blob.encode()[:RESULT_BYTES].decode(errors="ignore") + "…"
    return f"RESULT {result['tool']} {result['status']}\n{blob}"


def converse(said: str, history: list[dict], *, app, profile_id: str,
             authorization: str | None, provider) -> dict:
    """One turn: what they asked, what the agent did, and what it said.

    The conversation is the console's to keep. Nothing here is stored — the
    agent has no memory of its own, which is both the cheaper design and the
    one where *forget this* is something a person can actually do.

    Every step is reported, whatever happened, and the steps are what the
    screen shows. An agent that quietly edits a page and then describes the
    edit in prose is asking to be believed; one that lists the doors it went
    through can be checked.
    """
    said = (said or "").strip()[:SAID_CHARS]
    if not said:
        raise AgentError("agent.said_nothing")

    turns = [{"role": t["role"], "content": str(t.get("content", ""))[:SAID_CHARS]}
             for t in (history or [])[-HISTORY_TURNS:]
             if t.get("role") in ("user", "assistant")]
    turns.append({"role": "user", "content": said})

    steps: list[dict] = []
    for _ in range(STEPS):
        reply = provider.generate(system_prompt(said), turns)
        wanted = wants_a_tool(reply)
        if wanted is None:
            return {"reply": reply.strip(), "acted": steps,
                    "stopped": None, "asks": None}
        name, arguments = wanted

        # The rows that cannot be taken back stop here and ask.
        #
        # Everything in this list is the person's own, reached with their own
        # credential through their own door, and most of it is a mistake they
        # can simply undo — a tagline goes back, a widget has versions, a post
        # comes down. A sunset does not. Neither does a message somebody else
        # has now read, a payout, or a grant of authority handed to a third
        # party.
        #
        #     asked     may this person do this
        #     mattered  did this person mean this
        #
        # Those are different questions and only the first one has a token.
        # The second is answered by a press, so a confirming row is returned
        # as a proposal — the row's own sentence and the arguments the model
        # chose, both visible — and the console asks. `authoring_act` is where
        # it lands if the answer is yes.
        if is_a_tool(name) and needs_a_press(name):
            return {"reply": "", "acted": steps, "stopped": None,
                    "asks": {"tool": name, "arguments": dict(arguments or {}),
                             "says": what_it_would_do(name)}}
        try:
            result = call(name, arguments, app=app, profile_id=profile_id,
                          authorization=authorization)
        except AgentError as exc:
            # A refused call is a turn in the conversation, not the end of
            # one: the model asked for something it does not have, and being
            # told so is how it stops asking.
            steps.append({"tool": name, "answered": None, "refused": str(exc)})
            turns += [{"role": "assistant", "content": reply},
                      {"role": "user", "content": f"REFUSED {str(exc)}"}]
            continue
        steps.append({"tool": name, "answered": result["status"]})
        turns += [{"role": "assistant", "content": reply},
                  {"role": "user", "content": a_result_for_the_model(result)}]

    # Out of steps with no answer. Said plainly rather than dressed as one —
    # the screen shows what it did reach, and the person decides whether to
    # ask again.
    return {"reply": "", "acted": steps, "stopped": "agent.too_many_steps",
            "asks": None}
