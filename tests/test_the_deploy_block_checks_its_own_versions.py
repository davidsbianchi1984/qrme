"""The deploy block ends by asking the three names what version they answer.

`docs/beta-deploy.md` § 7 checks the three public names from your own
machine, in one of two shells, and says which shell is which. That check
has been performed wrong three times running — the PowerShell three pasted
at a `root@ubuntu` prompt from a Windows handheld — and each time the deploy
had gone perfectly and the screen said `command not found` three times.

    asked     does the page say which shell
    mattered  is there a check with no shell to choose

`docker/beta-versions.sh` is that check. It runs where the deploy block
already put the reader, reads the three names from the same `.env` the
compose line uses, and compares what each answers with the version in this
checkout's `pyproject.toml` — which is the question the from-outside check
was actually catching: did the pull fetch the thing you are releasing. The
from-outside check stays, for reachability. This one goes in the block.

These guards hold three things: that the line is in the block, after the
`up`; that the script does what the page says it does, run against a
server that answers; and that a disagreement is an exit status, not a
number somebody has to notice.
"""

import http.server
import json
import re
import subprocess
import threading
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PAGE = REPO / "docs" / "beta-deploy.md"
SCRIPT = REPO / "docker" / "beta-versions.sh"
PYPROJECT = REPO / "pyproject.toml"


def _deploy_block() -> list[str]:
    text = PAGE.read_text(encoding="utf-8")
    start = text.index("## 7. Updating a running beta")
    section = text[start:text.index("\n## ", start + 1)]
    block = next(b for b in re.findall(r"```bash\n(.*?)```", section, re.S)
                 if "docker compose" in b and "up -d --build" in b)
    return [ln.strip() for ln in block.splitlines() if ln.strip()]


def test_the_deploy_block_ends_by_checking_the_versions():
    lines = _deploy_block()
    up = next(i for i, ln in enumerate(lines) if "up -d --build" in ln)
    check = next((i for i, ln in enumerate(lines) if "beta-versions.sh" in ln),
                 None)
    assert check is not None, (
        "the deploy block no longer checks what the names answer. The "
        "from-outside check has been run in the wrong shell three times; "
        "this is the one with no shell to choose")
    assert check > up, "the versions are checked before the containers are up"


def test_the_script_does_not_make_the_deploy_block_a_check_block():
    """The deploy block starts with `ssh`; a check block may not.

    `test_the_deploy_page_is_paste_ready` finds check blocks by the string
    `/health`, so a script called `health.sh` under `docker/` would turn
    the deploy block into one and fail two guards at once. The name is part
    of the contract.
    """
    for ln in _deploy_block():
        assert "/health" not in ln


def _version() -> str:
    return re.search(r'^version = "([^"]+)"', PYPROJECT.read_text(), re.M).group(1)


class _Health(http.server.BaseHTTPRequestHandler):
    versions: dict[int, str] = {}

    def do_GET(self):  # noqa: N802
        v = self.versions[self.server.server_port]
        body = json.dumps({"status": "ok", "version": v}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


@pytest.fixture
def three_names(tmp_path):
    """Three local servers standing in for the three names, and an env
    file naming them the way /srv/qrme/.env does."""
    servers = []

    def stand_up(version):
        srv = http.server.HTTPServer(("127.0.0.1", 0), _Health)
        _Health.versions[srv.server_port] = version
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers.append(srv)
        return f"http://127.0.0.1:{srv.server_port}"

    def make(qrme, jim, pdi):
        env = tmp_path / ".env"
        env.write_text(
            "QRME_MASTER_KEY=not-for-the-shell\n"
            f"QRME_PUBLIC_URL={stand_up(qrme)}\n"
            f"JIM_PUBLIC_URL={stand_up(jim)}/\n"   # a trailing slash, as typed
            f"PDI_PUBLIC_URL={stand_up(pdi)}\n")
        return env

    yield make
    for s in servers:
        s.shutdown()


def _run(env):
    return subprocess.run(["sh", str(SCRIPT), str(env)],
                          capture_output=True, text=True, timeout=60)


def test_three_names_answering_this_checkout_is_a_clean_exit(three_names):
    v = _version()
    r = _run(three_names(v, v, v))
    assert r.returncode == 0, r.stdout + r.stderr
    assert f"all three answer {v}" in r.stdout
    for name in ("QRME", "JIM", "PDI"):
        assert re.search(rf"^{name}\s+127\.0\.0\.1:\d+\s+{re.escape(v)}$",
                         r.stdout, re.M), r.stdout


def test_one_name_on_the_old_version_is_a_failure_that_names_it(three_names):
    """The branch drift, as it would have looked on the deploy that caused
    it: one name still answering the previous release."""
    v = _version()
    r = _run(three_names(v, v, "2.5.0"))
    assert r.returncode == 1
    assert re.search(rf"^PDI\s+\S+\s+2\.5\.0\s+<- this checkout is {re.escape(v)}$",
                     r.stdout, re.M), r.stdout
    assert "did not rebuild" in r.stderr
    assert "all three answer" not in r.stdout


def test_a_name_that_does_not_answer_is_a_failure_and_not_a_hang(three_names, tmp_path):
    v = _version()
    env = three_names(v, v, v)
    text = env.read_text().replace("PDI_PUBLIC_URL=http://127.0.0.1:",
                                   "PDI_PUBLIC_URL=http://127.0.0.1:1/")
    # port 1 refuses; the line says so and the run goes on to its verdict
    env.write_text(re.sub(r"PDI_PUBLIC_URL=.*", "PDI_PUBLIC_URL=http://127.0.0.1:1", text))
    r = _run(env)
    assert r.returncode == 1
    assert re.search(r"^PDI\s+127\.0\.0\.1:1\s+unreachable:", r.stdout, re.M), r.stdout


def test_the_script_never_sources_the_env_file():
    """`.env` holds the master key. The script reads three lines from it
    with sed; it must not `.` or `source` the file into its own shell."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert text.startswith("#!/bin/sh")
    assert SCRIPT.stat().st_mode & 0o111, "the script is not executable"
    for ln in text.splitlines():
        code = ln.split("#", 1)[0].strip()
        assert not re.match(r"^(\.|source)\s", code), ln
    assert "QRME_PUBLIC_URL" in text and "JIM_PUBLIC_URL" in text and "PDI_PUBLIC_URL" in text
