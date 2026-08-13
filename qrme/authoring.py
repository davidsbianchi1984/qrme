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

## What is deliberately absent

No deletion of the profile, no membership or billing change, no key
material, no moderation decisions, no messaging anybody else, and nothing
that touches another person's rows. Those are not oversights and each one
is refused by absence rather than by a check — the agent cannot call what
is not in the list.

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
TOOLS: tuple[dict, ...] = (
    {"name": "read_page", "writes": False,
     "route": ("GET", "/profiles/{profile_id}/page"),
     "says": "read your page as it stands"},
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

You act only through the tools you were given. Each one touches that
person's own records and nothing else — there is no tool that reaches
another profile, and you should not describe yourself as able to.

To use a tool, reply with one line and nothing else:

    CALL <tool name> {"argument": "value"}

Do not name whose profile it is — that is filled in for you, and a profile
named in your arguments is dropped. You will be handed the result as the
next message, and you may then call another tool or answer the person. One
call per reply. When you have nothing left to do, answer in plain words
with no CALL line at all.

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
        reply = provider.generate(SYSTEM, turns)
        wanted = wants_a_tool(reply)
        if wanted is None:
            return {"reply": reply.strip(), "steps": steps, "stopped": None}
        name, arguments = wanted
        try:
            result = call(name, arguments, app=app, profile_id=profile_id,
                          authorization=authorization)
        except AgentError as exc:
            # A refused call is a turn in the conversation, not the end of
            # one: the model asked for something it does not have, and being
            # told so is how it stops asking.
            steps.append({"tool": name, "status": None, "refused": str(exc)})
            turns += [{"role": "assistant", "content": reply},
                      {"role": "user", "content": f"REFUSED {str(exc)}"}]
            continue
        steps.append({"tool": name, "status": result["status"]})
        turns += [{"role": "assistant", "content": reply},
                  {"role": "user", "content": a_result_for_the_model(result)}]

    # Out of steps with no answer. Said plainly rather than dressed as one —
    # the screen shows what it did reach, and the person decides whether to
    # ask again.
    return {"reply": "", "steps": steps, "stopped": "agent.too_many_steps"}
