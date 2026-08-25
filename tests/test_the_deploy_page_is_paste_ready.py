"""The commands on the deploy page, checked as commands rather than as prose.

`docs/beta-deploy.md` is the page somebody follows while standing at a
terminal, usually at the end of a release and often on a phone. It has now
been wrong twice in the same way — not wrong about *what* to do, but wrong in
a shape that turns a correct instruction into an error.

    asked     does the page have the commands
    mattered  can they be pasted by the person reading it

**The room.** The section opened by warning that `/srv/qrme` is on the host
and not on a laptop, with `ssh root@your-host` in a fenced block of its own
above the deploy. A block of its own is a block you can skip: what gets
pasted is the thing that looks like the procedure. Somebody pasted the four
lines below it into PowerShell on a handheld and got two failures that each
read like a broken deploy.

**The Windows form.** The page then said *on PowerShell, add `.exe` to each*
— true, and attached to three lines that also carry `; echo`. `echo` there is
`Write-Output`, which at the end of a pipeline with nothing feeding it stops
and prompts for input. So following the instruction exactly still produced an
error naming a cmdlet nobody typed, after a deploy that had gone perfectly.

**The room again, one step later.** The check that follows the deploy runs
from your own machine, and the line that gets you there was a sentence
between the two blocks — *then `exit`, and check from your own machine* —
with a paragraph under them explaining why it mattered. Both were true and
neither was run: the three checks went in on the host, which is the one place
they prove nothing, because they answer from inside the network they exist to
test from outside.

**The alternative that was laid out as a sequence.** The Windows block read
*on Windows, use these instead* and sat where the next step goes, so a reader
working down the page ran the Unix three, saw three health objects, and then
ran the Windows three in the same shell — `curl.exe: command not found`,
three times, after a deploy that had gone perfectly.

All four are the same failure: a correction written *about* a command instead
of *as* one, or a choice written where a step belongs. These guards hold the
shape rather than the wording — the page is free to be rewritten, and the
commands have to stay runnable by the reader they are addressed to.
"""

from pathlib import Path

import pytest

from . import ratchets

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "beta-deploy.md"


def _updating() -> str:
    """The *Updating a running beta* section, and only it.

    Sections 0-6 stand the beta up and are written for somebody already on
    the box — they say so in their own way, and repeating `ssh` at the top of
    each of their blocks would be noise. This section is the one a person
    comes back to months later, from wherever they happen to be sitting.
    """
    text = PAGE.read_text(encoding="utf-8")
    start = text.index("## 7. Updating a running beta")
    end = text.index("\n## ", start + 1)
    return text[start:end]


def _fenced(language: str) -> list[str]:
    """Every fenced block in the update section opened with this language."""
    blocks, current = [], None
    for line in _updating().splitlines():
        if current is not None:
            if line.startswith("```"):
                blocks.append("\n".join(current))
                current = None
            else:
                current.append(line)
        elif line.strip() == f"```{language}":
            current = []
    return blocks


def test_the_page_is_here_at_all():
    """A guard on the guards: every check below passes on a missing file."""
    assert PAGE.exists(), "docs/beta-deploy.md is the page these guards read"


def test_the_deploy_block_carries_the_step_that_changes_machine():
    """`ssh` in a block of its own is a step a reader skips.

    The deploy is the only place in this page where the machine changes, so
    the line that changes it belongs inside the block somebody copies — not
    above it, however clearly the paragraph explains itself.
    """
    deploys = [b for b in _fenced("bash") if "docker compose" in b]
    assert deploys, "the update section has no deploy block any more"
    for block in deploys:
        assert "ssh " in block, (
            "the deploy block does not say which machine to be on. It has "
            "been pasted into a laptop shell twice; the `ssh` belongs in the "
            "block rather than in the paragraph above it")


def _checks() -> list[str]:
    """Every block that checks what a deployed name answers.

    Found by what they do rather than by which language opened them, because
    there is one of these per shell and the point of the guards below is that
    each one stands on its own.
    """
    return [b for b in _fenced("bash") + _fenced("powershell")
            if "/health" in b]


@pytest.mark.parametrize("host", ["sntheticprofiles.com", "jim-mini.com",
                                  "pdisystems.net"])
def test_every_product_is_checked_after_a_deploy(host):
    """All three, every time — a box carrying two versions reports the
    mismatch to whoever is using it rather than to whoever deployed it.

    In **every** check block rather than across them added together. One
    block per shell, and a reader runs one of them: three hosts spread over
    two blocks is a check nobody actually performs.
    """
    blocks = _checks()
    assert blocks, "the update section has no check block any more"
    for block in blocks:
        assert f"{host}/health" in block, (
            f"a check block does not reach {host}. Each one is run on its "
            "own, so each one has to check all three")


def test_no_check_block_changes_machine_inside_itself():
    """`exit` in the block is a step a reader *cannot* run.

    This guard is the inverse of the one it replaces, and the reversal is the
    lesson. The first version held that `exit` must be the **first line** of
    each check block, by analogy with the `ssh` at the top of the deploy
    block. The analogy is false. `ssh host` followed by more lines works
    because ssh takes the rest as standard input; `exit` followed by more
    lines does not, because the shell tears down and the rest of the paste
    goes into a closing session. It echoes and is lost.

    So the page said to do something that could not be done, and the checks
    silently never ran after a deploy that had gone perfectly — worse than
    the sentence everybody skipped, because a skipped step leaves a prompt
    you can still type into.

    A block somebody pastes must therefore contain **no change of machine at
    all**. Getting to your own machine is a new window, and that is prose
    because it is not a command.
    """
    for block in _checks():
        for line in (l.strip() for l in block.splitlines() if l.strip()):
            assert line != "exit", (
                "a check block starts by closing the connection, so every "
                "line under it is pasted into a dying session and never "
                "runs. Leaving the host is a new window, not a line in the "
                "block")
            assert not line.startswith("ssh "), (
                "a check block opens a connection to the host, which is the "
                "one place these three commands cannot tell you what a "
                "visitor gets")


def test_the_page_says_how_to_get_to_your_own_machine():
    """Prose, but it has to be there.

    The command form was tried twice and failed twice, so what is left is an
    instruction — and this holds that it did not vanish along with the `exit`
    that replaced it, which is exactly how the step went missing the first
    time.

    The phrase checked is the **imperative**, not the bare words. The first
    version of this guard accepted "new window", which the paragraphs
    explaining *why* it is a new window also contain, so deleting the
    instruction left the guard green. That is the second time in two days a
    guard on this page has matched its own surrounding prose — the other
    took the word `either`, four paragraphs from an unrelated sentence. A
    guard that can be satisfied by the explanation of a rule is not checking
    the rule.
    """
    said = _updating().lower()
    assert "open a new terminal window" in said, (
        "nothing tells the reader how to get off the host. That step has "
        "been lost once already, and the checks then ran on the box")


def test_the_two_shells_are_a_choice_and_not_a_sequence():
    """Two blocks doing the same work for different machines.

    An alternative laid out as a sequence is read as a sequence — that is
    what put PowerShell's three lines into a bash prompt. The page has to say
    that one of them is the one to run, and the guard accepts any of the
    words somebody might write it in rather than pinning the sentence.

    The accepted phrasings all name the count, which is what makes them
    unmistakable. The first version of this guard also took `either`, and
    passed on a page carrying no marker at all: § 7 already says `docker` is
    usually not installed *there either*, four paragraphs up. A guard whose
    word can arrive by accident is a guard that reports on the prose rather
    than on the shape.
    """
    blocks = _checks()
    assert len(blocks) >= ratchets.floor("deploy.check_blocks"), (
        "one check block, so there is no choice to mark — if the Windows "
        "form has gone, `test_the_windows_lines_are_lines_a_windows_reader_"
        "can_paste` is the guard that says why it has to come back")
    said = _updating().lower()
    assert any(w in said for w in ("not both", "one of the two",
                                   "one of these two", "one of the following "
                                   "two")), (
        "nothing on the page says these blocks are alternatives. Laid out as "
        "consecutive steps, both get run: the second one was, in a shell "
        "that has no `curl.exe`, after a deploy that had gone perfectly")


def test_the_windows_lines_are_lines_a_windows_reader_can_paste():
    """Written out, not described.

    `curl` in PowerShell is `Invoke-WebRequest`: no `-s`, and `https:` read as
    a drive letter. `echo` is `Write-Output`, which prompts for input when
    nothing feeds it. A page that says *add `.exe`* beside lines carrying
    `; echo` has corrected one of those and left the other.
    """
    blocks = _fenced("powershell")
    assert blocks, (
        "the page has no PowerShell block. The Windows form was a sentence "
        "about the Unix lines for two releases, and following it exactly "
        "still failed")
    for block in blocks:
        for line in (l.strip() for l in block.splitlines() if l.strip()):
            assert "; echo" not in line, (
                f"`{line}` ends in PowerShell's `Write-Output` with nothing "
                "feeding it, which stops and prompts for input")
            if "curl" in line:
                assert "curl.exe" in line, (
                    f"`{line}` reaches PowerShell's `Invoke-WebRequest` "
                    "alias, which has no `-s` and reads `https:` as a drive")


def _blocks_on_the_whole_page() -> list[str]:
    """Every fenced block on the page, in any shell.

    The guards above scope themselves to § 7 on purpose — sections 0-6 are
    written for somebody already standing on the box. The two below cannot,
    because what they hold went wrong in § 3 and § 4: a command is either
    runnable where the page put you or it is not, and which section it sits
    in has no bearing on that.
    """
    blocks, current = [], None
    for line in PAGE.read_text(encoding="utf-8").splitlines():
        if current is not None:
            if line.startswith("```"):
                blocks.append("\n".join(current))
                current = None
            else:
                current.append(line)
        elif line.startswith("```") and line.strip() != "```":
            current = []
    return blocks


def _compose_lines() -> list[str]:
    """Every line on the page that drives this stack's compose file."""
    return [line.strip()
            for block in _blocks_on_the_whole_page()
            for line in block.splitlines()
            if "docker compose" in line and "beta-compose.yml" in line]


def test_every_compose_command_carries_the_file_that_fills_it():
    """`--env-file .env` on all of them, not only on the one that builds.

    Compose interpolates the whole file before it does anything, so `ps` and
    `logs` need the values exactly as much as `up` does — and it cannot find
    them by itself, because `.env` is at `/srv/qrme/.env` while compose looks
    beside the compose file it was handed, in `docker/`.

        asked     does the page have the commands
        mattered  do they run in the directory the page put you in

    § 2 makes every variable `${VAR:?}` deliberately, so the flag going
    missing does not degrade anything quietly — it returns ten lines naming
    ten missing variables. On `up` that reads as the guard it is. On a
    read-only subcommand against a stack that is already up and answering, it
    reads as a broken deploy, which is how this was found: `ps` was run to
    check a container's state after a deploy that had gone perfectly, and the
    page's own line could not run.

    Four of the six compose commands here were missing it. They had never
    been typed — the deploy line was the one anybody used — which is the
    same shape as every other drift on this page: correct prose around a
    command nobody had run in the room it is addressed to.
    """
    lines = _compose_lines()
    assert lines, "no compose commands on the page any more"
    for line in lines:
        assert "--env-file" in line, (
            f"`{line}` does not say where the values are. Compose "
            "interpolates the whole file for every subcommand and looks for "
            "`.env` beside the compose file rather than in `/srv/qrme`, so "
            "this stops with ten missing variables and reads like a broken "
            "deploy")


def test_no_command_in_a_block_is_written_with_an_ellipsis():
    """An elided command is a described command.

    This page has twice shipped an instruction *about* a command instead of
    the command — *add `.exe` to each*, and *then `exit`* — and both were
    followed exactly and still failed. `docker compose ... restart caddy` is
    the same shape one turn further on, and the part the ellipsis swallowed
    was the flag without which it does not run.

    Fenced blocks only. The prose is free to name the abbreviation it is
    warning against, and § 4 now does; a guard that could not tell those
    apart would forbid the page from explaining itself.
    """
    for block in _blocks_on_the_whole_page():
        for line in (l.strip() for l in block.splitlines() if l.strip()):
            assert "..." not in line, (
                f"`{line}` is a command with a hole in it. Whoever reads it "
                "has to know what the ellipsis stood for, and the reader "
                "this page is addressed to is looking at it because they do "
                "not")
