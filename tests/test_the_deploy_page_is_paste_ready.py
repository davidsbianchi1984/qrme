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

Both are the same failure: a correction written *about* a command instead of
*as* one. These guards hold the shape rather than the wording — the page is
free to be rewritten, and the commands have to stay runnable by the reader
they are addressed to.
"""

from pathlib import Path

import pytest

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


@pytest.mark.parametrize("host", ["sntheticprofiles.com", "jim-mini.com",
                                  "pdisystems.net"])
def test_every_product_is_checked_after_a_deploy(host):
    """All three, every time — a box carrying two versions reports the
    mismatch to whoever is using it rather than to whoever deployed it."""
    checks = "\n".join(_fenced("bash") + _fenced("powershell"))
    assert f"{host}/health" in checks, (
        f"nothing on the page checks {host} after a deploy")


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
