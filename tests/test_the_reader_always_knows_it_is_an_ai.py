"""A conversation names what it is talking to.

`watermark.design()` builds the profile's label as `AI · {name}` and forces
the designation in front even of a label an owner customised — the module
says so in its own words: *the AI designation is invariant*. The rule is
enforced on the server, where an owner cannot design it away.

The console walked around it by never asking. Every conversation surface
rendered `display_name` straight out of the profile, so the header of a chat
with a synthetic profile read "Chat with David Bianchi" and said nothing
about what it was — on the product whose entire subject is that distinction.

    asked     does the profile carry a designation
    mattered  does the screen naming it use one

## What this covers, and what it does not

The three surfaces that name the profile you are *in a conversation with*:
the header, the empty-state greeting, and the talk overlay's caption.

It does not cover the estate. `display_name` is rendered in 89 places across
the console's screens, and whether each of those is a conversation, a
listing, an owner's own management view, or a real person's account is a
question per site rather than a sweep. That count is written here rather
than left implied, because a guard over three surfaces that reads as though
it covers the product is worse than no guard: the next person to ask "is the
designation shown" would find a passing test and stop.
"""

import re
from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


ROOT = _repo()
CHAT = (ROOT / "app/src/screens/Chat.tsx").read_text(encoding="utf-8")


def test_the_server_still_forces_the_designation():
    """The console leans on this. If the rule moved, the console's use of
    `label` becomes a name with nothing in front of it, silently."""
    wm = (ROOT / "qrme/watermark.py").read_text(encoding="utf-8")
    assert 'f"AI · {name}"' in wm, "the default label no longer declares AI"
    assert '"ai" not in label.lower()' in wm, (
        "a custom label is no longer forced to carry the designation, so a "
        "profile could be labelled anything and the console would show it")


def test_the_conversation_names_the_profile_with_its_designation():
    """The three surfaces somebody reads while talking to it."""
    assert "const shownName" in CHAT, (
        "the chat screen has no designated name to render")
    assert "talkAvatar?.watermark?.label" in CHAT, (
        "the name is not taken from the server's watermark, so a customised "
        "designation would not reach this screen")
    for surface in ('tr("chat.with", lang), { name: shownName }',
                    'tr("chat.sayhello", lang), { name: shownName }',
                    '<div className="talk-name">{shownName}</div>'):
        assert surface in CHAT, f"this surface still names it bare: {surface}"


def test_the_designation_does_not_wait_for_the_microphone():
    """It was fetched inside `openTalk`, so a reader who never pressed the
    microphone never saw it."""
    m = re.search(r"function openTalk\(\) \{(.*?)\n  \}", CHAT, re.S)
    assert m, "no openTalk to read"
    assert "api.avatar(" not in m.group(1), (
        "the watermark is still fetched only when the talk overlay opens — "
        "the header needs it from the moment the conversation does")
    assert re.search(r"useEffect\(\(\) => \{\s*if \(!session\.profileId\) return;"
                     r"\s*api\.avatar\(", CHAT), (
        "nothing fetches the avatar when the conversation opens")
