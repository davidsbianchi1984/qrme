"""Ability is not a gate — and the statement that says so is checked here.

The accessibility statement (README, console Access screen, terms) makes
claims about behavior: reports need no account and keep no name, the
reports are read by somebody standing for the deployment, every image in
the console says what it shows, and the known gaps live in a ledger that
only shrinks. A statement is marketing until a test fails when it stops
being true. These are those tests.

The same four questions are asked in all three products — the guard
travels, per ``shared_guards.txt`` — with each suite answering for its own
console, its own routes and its own ledger.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONSOLE = REPO / "app" / "src"
BACKLOG = Path(__file__).resolve().parent / "a11y_backlog.txt"


def test_a_report_needs_no_account_and_keeps_no_name(client):
    """The door is tokenless and the table cannot hold an identity.

    Not "does not": *cannot*. The feedback table next door records
    role:subject when the caller is authenticated; this one has no such
    column to fill, so linking a report to a person is impossible at the
    schema, which is the only place a privacy promise survives a busy
    contributor with a helpful idea.
    """
    sent = client.post("/access/reports", json={
        "doing": "sign up", "wall": "the form needed a mouse", "lang": "fr"})
    assert sent.status_code == 201
    body = sent.json()
    assert body["status"] == "received"

    from qrme import db
    columns = {row["name"] for row in
               db.connect().execute("PRAGMA table_info(access_reports)")}
    forbidden = {"submitter", "owner_id", "subject_id", "account",
                 "email", "user_id", "interactor_id"}
    assert not (columns & forbidden), (
        f"access_reports gained an identity column: {columns & forbidden}")

    # The words arrive whole, in the language they were written in.
    seen = client.get("/access/reports").json()
    mine = [r for r in seen["reports"] if r["id"] == body["id"]]
    assert mine and mine[0]["wall"] == "the form needed a mouse"
    assert mine[0]["lang"] == "fr"


def test_the_reports_are_for_the_deployments_steward_alone(client, monkeypatch):
    """Reading is held by the reviewer role — the deployment's, not a
    profile's — and fails closed the way objection review does."""
    monkeypatch.setenv("QRME_ADMIN_TOKEN", "steward-token")
    assert client.get("/access/reports").status_code == 401
    assert client.get(
        "/access/reports",
        headers={"Authorization": "Bearer guess"}).status_code == 403
    assert client.get(
        "/access/reports",
        headers={"Authorization": "Bearer steward-token"}).status_code == 200


def test_every_console_image_says_what_it_shows():
    """No ``<img>`` without an ``alt`` — the statement claims described
    images, so an undescribed one is a failing test, not a style nit.

    ``alt=""`` passes: an explicitly empty description is a decision — the
    wall's upload form asks for one, so an empty alt is an uploader who
    chose to leave it blank; a missing attribute is the absence of one.
    """
    naked = []
    for path in CONSOLE.rglob("*.tsx"):
        src = path.read_text(encoding="utf-8")
        for tag in re.finditer(r"<img\b[^>]*?/?>", src, re.S):
            if "alt=" not in tag.group(0):
                line = src[: tag.start()].count("\n") + 1
                naked.append(f"{path.relative_to(REPO)}:{line}")
    assert not naked, (
        "console images with no description:\n    " + "\n    ".join(naked))


def test_the_a11y_backlog_only_shrinks():
    """The ledger of known gaps: rows never exceed the recorded ceiling,
    and every row is a sentence about a person, not a component name.

    Raising the ceiling is a deliberate edit to this file's header — the
    move a newly accepted report makes — and shows up in a diff. What this
    guard forbids is the quiet version: a gap slipping in with no ceiling
    change, which is how backlogs refill.
    """
    text = BACKLOG.read_text(encoding="utf-8")
    ceiling_match = re.search(r"^# ceiling: (\d+)$", text, re.M)
    assert ceiling_match, "a11y_backlog.txt lost its ceiling header"
    ceiling = int(ceiling_match.group(1))
    rows = [line for line in text.splitlines()
            if line.strip() and not line.startswith("#")]
    assert len(rows) <= ceiling, (
        f"{len(rows)} known gaps against a ceiling of {ceiling} — a gap was "
        "added without raising the ceiling in the same deliberate edit")
    for row in rows:
        assert ": " in row, f"a backlog row names no surface: {row!r}"


def test_the_wall_upload_asks_and_the_picture_answers(client):
    """A struck backlog row, held shut: the upload form asks what the file
    shows, the words ride to the server, and every read of that media —
    the upload receipt, the post, the feed hydration — carries them back
    as the image's alt."""
    from tests.test_capabilities import auth_header, make_profile
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64

    me = make_profile(client, display_name="Describer")
    up = client.post(
        f"/profiles/{me['id']}/media?alt=my%20dog%20asleep%20on%20the%20porch",
        content=png, headers=auth_header(me))
    assert up.status_code == 201, up.text
    picture = up.json()
    assert picture["alt"] == "my dog asleep on the porch"

    r = client.post(f"/profiles/{me['id']}/wall",
                    json={"body": "Sunday.", "media_ids": [picture["id"]]},
                    headers=auth_header(me))
    assert r.status_code == 201, r.text
    assert r.json()["media"][0]["alt"] == "my dog asleep on the porch"
    posts = client.get(f"/profiles/{me['id']}/wall").json()["posts"]
    assert posts[0]["media"][0]["alt"] == "my dog asleep on the porch"

    # And the console form actually asks — the question is wired into the
    # composer, not only accepted by the route.
    wall_src = (CONSOLE / "screens" / "Wall.tsx").read_text(encoding="utf-8")
    assert 'tr("wll.alt"' in wall_src and "mediaAlt" in wall_src, (
        "the wall composer no longer asks what an upload shows")


def test_the_chat_tells_the_screen_reader():
    """A struck backlog row, held shut: the conversation log is an
    aria-live region, so a screen reader hears the reply arrive instead
    of sitting in silence wondering whether anything happened."""
    chat_src = (CONSOLE / "screens" / "Chat.tsx").read_text(encoding="utf-8")
    assert 'aria-live=' in chat_src and 'role="log"' in chat_src, (
        "Chat.tsx lost its aria-live log region")


def test_the_shells_carry_the_statement():
    """A struck backlog row, held shut: the phones and the desktop carry
    the same per-need statement the console makes — every named need, in
    every supported language — not just the report form under a lead."""
    needs = ["title", "blind", "deaf", "mute", "motor", "cognitive",
             "dyslexia", "motion", "more"]
    langs = ["en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"]
    l10n_files = [
        REPO / "native" / "ios" / "Sources" / "L10n.swift",
        REPO / "native" / "android" / "app" / "src" / "main" / "java"
             / "app" / "qrme" / "studio" / "L10n.kt",
        REPO / "native" / "windows" / "L10n.cs",
    ]
    for path in l10n_files:
        src = path.read_text(encoding="utf-8")
        for need in needs:
            key_line = next((line for line in src.splitlines()
                             if f"ns.acc.needs.{need}" in line), None)
            assert key_line, f"{path.name} lacks ns.acc.needs.{need}"
            for lang in langs:
                assert f'"{lang}"' in key_line, (
                    f"{path.name} ns.acc.needs.{need} lacks {lang}")
    views = [
        REPO / "native" / "ios" / "Sources" / "Views" / "AccessView.swift",
        REPO / "native" / "android" / "app" / "src" / "main" / "java"
             / "app" / "qrme" / "studio" / "ui" / "Screens.kt",
        REPO / "native" / "windows" / "Views" / "SettingsPage.xaml.cs",
    ]
    for path in views:
        src = path.read_text(encoding="utf-8")
        assert "ns.acc.needs.title" in src and "ns.acc.needs.more" in src, (
            f"{path.name} shows the form without the statement")
        for need in ["blind", "deaf", "mute", "motor", "cognitive",
                     "dyslexia", "motion"]:
            assert need in src, f"{path.name} dropped the need {need!r}"
