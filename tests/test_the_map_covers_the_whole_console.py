"""Every screen this application has, known to the things that speak for it.

A synthetic profile is somebody's stand-in inside an application, and it knew
everything about the person it represents and nothing about the place it
lives. Asked *where do I change what you're allowed to do*, a mechanic
answered like a mechanic who had never seen the app — right for the character
and wrong for the moment. The agent had the same gap in a different shape: it
was told its eleven tools and nothing else, so a question about a screen it
cannot open got a shrug while the screen sat in the navigation bar.

    asked     can this profile do it
    mattered  can the console, and where is it

`tests/ui_screens.txt` already answers *does this surface have a drawing*.
This file answers the other half off the same list, so the two cannot drift:
a screen added without a row fails here, in the round that adds it.

## Why the shape is core / relevant / index

Sixty-eight doors is a manual, and the prompt this joins already carries a
persona, a relationship, a language directive and whatever the vault
remembers. So the turn carries the consent doors always, the doors this
message is about, and the *names* of the rest.

The index is the part most under test. It is what makes "I don't know how to
do that" wrong when the screen is in the navigation bar.

## And the two things it must not become

**Permission.** Naming a door is not opening one — the delegation policy
decides what may change, and the agent's prompt says outright that the map is
places to point at rather than doors to walk through. **A persona.** A
mechanic who can point at the Permissions tab is still a mechanic; a block
that turned every profile into a help desk would be a worse failure than the
one it fixes.
"""

from __future__ import annotations

import re
from pathlib import Path

from qrme import authoring, llm, persona, productmap

MANIFEST = Path(__file__).resolve().parent / "ui_screens.txt"


def _census() -> set[str]:
    out = set()
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            out.add(line.split()[0])
    return out


def test_every_surface_the_census_knows_has_a_row():
    """The failure this file exists for: a screen ships and nothing that
    speaks for the product ever hears about it."""
    missing = sorted(_census() - {d.surface for d in productmap.DOORS})
    assert not missing, (
        "these surfaces are in ui_screens.txt and not in productmap.DOORS: "
        f"{missing}\nGive each one a place, a line saying what it is for, "
        "and the words somebody would use to ask for it. A screen nothing "
        "can name is a screen every profile will decline to open.")


def test_the_map_names_no_surface_that_is_gone():
    """The other direction. A row for a screen that moved is a door a
    profile will send somebody to and they will not find."""
    stale = sorted({d.surface for d in productmap.DOORS} - _census())
    assert not stale, f"rows for surfaces no longer in the census: {stale}"


def test_no_surface_is_described_twice():
    seen = [d.surface for d in productmap.DOORS]
    dupes = sorted({s for s in seen if seen.count(s) > 1})
    assert not dupes, f"two rows for one surface: {dupes}"


def test_every_row_says_where_it_is_and_what_it_is_for():
    for d in productmap.DOORS:
        assert d.place.strip(), f"{d.surface} has no place"
        assert d.what.strip(), f"{d.surface} says nothing about what it is for"
        assert d.cues, (
            f"{d.surface} has no cues, so nothing a person says can ever "
            "reach it — it lives in the index and nowhere else")


def test_a_cue_is_something_a_person_could_actually_say():
    """Cues are matched against a lowercased message with a word boundary
    either side. A capital never fires, and a cue that opens or closes on a
    non-word character has no boundary to match on."""
    for d in productmap.DOORS:
        for cue in d.cues:
            assert cue == cue.lower(), (
                f"{d.surface}: cue {cue!r} has a capital and can never match")
            assert re.match(r"^\w", cue) and re.search(r"\w$", cue), (
                f"{d.surface}: cue {cue!r} begins or ends on a non-word "
                "character, so the word boundary around it cannot match")


def test_the_core_is_the_consent_doors():
    """What may this thing do on my behalf, who is allowed to know, how do I
    contest a profile that depicts me, and how do I reach a person. Getting
    those wrong is a harm rather than a disappointment."""
    always = {d.surface for d in productmap.DOORS if d.always}
    assert {"Allowed", "Delegate", "Identity", "Contest", "Matters"} <= always, (
        "a consent door is missing from the core; a profile that has to be "
        "reminded about them will not mention them on the turn that matters")
    assert always < {d.surface for d in productmap.DOORS}, (
        "every door is marked always, which is the manual-in-the-prompt this "
        "selection exists to avoid")
    core = productmap.core()
    for surface in always:
        row = next(d for d in productmap.DOORS if d.surface == surface)
        assert row.place in core, f"{surface} is marked always and is not in the core"


def test_the_map_says_it_is_not_permission():
    """The one sentence that keeps a signpost from reading as a key."""
    core = productmap.core()
    assert "not permission to act" in core, (
        "the map does not say that naming a door is not permission to open "
        "it — a delegation policy that lives elsewhere is the only thing "
        "deciding, and the prompt has to say so")
    assert "delegation policy" in core


def test_the_map_does_not_turn_a_profile_into_a_help_desk():
    """A mechanic who can point at the Permissions tab is still a mechanic.
    The instruction that keeps it that way is in the block itself, because
    that is the only place the model reads."""
    assert "Stay in character" in productmap.core()


def test_the_turn_never_carries_the_whole_manual():
    everything = " ".join(cue for d in productmap.DOORS for cue in d.cues)
    picked = productmap.selected(everything)
    assert len(picked) <= productmap.LIMIT, (
        f"{len(picked)} doors selected against a cap of {productmap.LIMIT}")
    block = productmap.block(everything)
    described = sum(1 for d in productmap.DOORS if d.what in block)
    assert described <= productmap.LIMIT + sum(
        1 for d in productmap.DOORS if d.always), (
        f"{described} doors arrived with their full description; the block "
        "is meant to be the core, the relevant ones, and names")


def test_what_somebody_says_reaches_the_screen_they_meant():
    for said, surface in [
            ("how do I book a session with you", "Desk"),
            ("can I get my money out", "Selling"),
            ("I want to change my avatar", "SkinPicker"),
            ("what do you remember about me", "Memory"),
            ("how much does this cost", "Plans"),
            ("can you speak spanish", "InWords"),
            ("where do I report a bug", "Problems"),
            ("I want to watch this video with you", "WatchParty"),
            ("do you have captions", "Access"),
            ("who is following me", "Audience")]:
        picked = [d.surface for d in productmap.selected(said)]
        assert surface in picked, (
            f"{said!r} did not reach {surface} — it reached {picked}")


def test_the_index_names_the_screens_this_message_did_not():
    idx = productmap.index()
    for surface in ("Desk", "Memory", "Access", "Studio", "Rooms"):
        row = next(d for d in productmap.DOORS if d.surface == surface)
        assert row.place in idx, f"{surface} is missing from the index"
    leaked = [d.surface for d in productmap.DOORS if d.what in idx]
    assert not leaked, (
        f"the index carries full descriptions for {leaked}; it is meant to "
        "be a table of contents")


# -- and that both conversations actually carry it ---------------------------

class Watched:
    """A provider that keeps the system prompt it was handed."""

    def __init__(self):
        self.prompts: list[str] = []

    def generate(self, system, messages):
        self.prompts.append(system)
        return "ok"


def test_every_synthetic_profile_carries_it(client, profile_id,
                                            interactor_id, monkeypatch):
    """In `build_system_prompt` rather than in the routes, so a profile
    created tomorrow has it without anybody remembering to add it."""
    seen = Watched()
    monkeypatch.setattr(llm, "provider_for_profile", lambda *a, **k: seen)
    r = client.post(f"/profiles/{profile_id}/chat",
                    json={"interactor_id": interactor_id,
                          "message": "where do I book a session with you?"})
    assert r.status_code == 200, r.text
    system = seen.prompts[0]
    # The screen they asked about, *described* — not merely named. Every
    # door's name is in the index on every turn, so asserting the name would
    # have passed with the route no longer passing the message at all, which
    # is exactly the sabotage that caught this test being too weak.
    desk = next(d for d in productmap.DOORS if d.surface == "Desk")
    assert desk.what in system, (
        "the screen they asked about arrived as a name in the index rather "
        "than described — the message is not reaching the selection")
    # The consent doors, whether or not they asked.
    assert "Permissions tab" in system
    # And every other screen, by name, so the next question already has an
    # answer.
    named = sum(1 for d in productmap.DOORS if d.place in system)
    assert named == len(productmap.DOORS), (
        f"only {named} of {len(productmap.DOORS)} doors reach the profile's "
        "prompt")


def test_a_brand_new_profile_has_it_too(client, monkeypatch):
    """The point of putting it where the prompt is built: nobody has to
    remember. A profile made this second is standing in the same building."""
    r = client.post("/profiles", json={
        "owner_id": "owner-new", "kind": "self",
        "display_name": "Wes",
        "persona": "A mechanic who fixes old trucks.",
        "verification": {"method": "self_attested", "birthdate": "1980-01-01"},
        "plan": "pro"})
    assert r.status_code == 201, r.text
    made = r.json()
    system = persona.build_system_prompt(
        dict(_row(client, made["id"])), None, None,
        said="what am I allowed to let you do?")
    assert "Permissions tab" in system
    assert "Delegation tab" in system


def _row(client, profile_id):
    from qrme import db
    return db.connect().execute(
        "SELECT * FROM profiles WHERE id=?", (profile_id,)).fetchone()


def test_the_agent_carries_it_and_is_told_it_is_not_a_tool_list():
    """The roster and the map answer different questions, and an agent that
    confused them would either refuse to name a screen or claim it can open
    one."""
    prompt = authoring.system_prompt("where do I change what you can do?")
    assert "Permissions tab" in prompt
    assert "You cannot open these; you can say where they are." in prompt, (
        "the agent is handed a map of screens with nothing separating it "
        "from the tools it may actually call")
    # The roster is still there and still first: what it may DO comes before
    # what the application HAS.
    for name in authoring.tool_names():
        assert name in prompt, f"the roster lost {name}"
    assert prompt.index("CALL <tool name>") < prompt.index("Permissions tab")
