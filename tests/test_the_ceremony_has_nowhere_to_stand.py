"""A relying party id is a domain, and `127.0.0.1` is not one.

## The finding

`docs/signatures.md` is careful about the hard part: a passkey assertion
verifies, `evaluatePolicy` does not, and the ceremony must run on the relying
party's own origin because WebAuthn refuses a mismatched `rpId`. Every client
in this repo follows that. The Windows shell embeds a WebView2 pointed at
`/signatures/ceremony`; the console opens the same page in a window.

Both of them fetch it from `http://127.0.0.1:8000`, which is the default base
address in `native/windows/ApiClient.cs` and the desktop console's own
backend. And `QRME_RP_ID` defaults to `qrme.app`.

Neither of those can run a ceremony:

* **`rp.id` must be a domain.** `127.0.0.1` is an IP literal. The browser
  rejects the call outright — there is no relying party id it could default
  to, and none it will accept.
* **`rp.id` must equal the origin's host or be a parent of it.** `qrme.app`
  is neither, from a loopback origin.

So the button on `SignaturesPage` had never worked from a default install,
and could not, and nothing in the repo said so. The audit's shape again, one
layer under the ceremony:

    asked     does the ceremony run on the relying party's own origin
    mattered  can that origin be a relying party at all

The page is rendered inside an embedded WebView with no developer console, so
the browser's own refusal arrives as `Fail(...)` with a DOMException string —
which reads like the credential was declined rather than like the address was
wrong. That is why the check below answers in HTML on the page itself, naming
the environment variable to change.

`localhost` is the way out for a loopback field test: it is a domain, it
resolves to the same backend, and it is a secure context without a
certificate. Both clients now rewrite the host, and `QRME_RP_ID=localhost`
makes the pair match.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from fastapi.testclient import TestClient

from qrme.routers.signatures import rp_id_problem


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("QRME_DB", str(tmp_path / "qrme.db"))
    from qrme.api import app
    return TestClient(app)


# (host, rp_id, is a problem, what the message must name)
CASES = (
    ("127.0.0.1", "qrme.app", True, "IP-address origin"),
    ("127.0.0.1", "localhost", True, "IP-address origin"),
    ("::1", "localhost", True, "IP-address origin"),
    ("localhost", "qrme.app", True, "QRME_RP_ID"),
    ("localhost", "localhost", False, ""),
    ("qrme.app", "qrme.app", False, ""),
    ("www.qrme.app", "qrme.app", False, ""),
    # The suffix rule is on labels, not characters: `notqrme.app` ends with
    # the string `qrme.app` and is a different site.
    ("notqrme.app", "qrme.app", True, "QRME_RP_ID"),
    ("", "qrme.app", True, "Host header"),
)


@pytest.mark.parametrize("host,rp_id,is_problem,names", CASES)
def test_the_pairs_that_can_and_cannot_sign(host, rp_id, is_problem, names):
    problem = rp_id_problem(host, rp_id)
    if is_problem:
        assert problem, f"{host!r} with rp_id {rp_id!r} should be refused"
        assert names in problem, (
            f"the refusal for {host!r}/{rp_id!r} does not name {names!r}, so "
            f"it does not tell anybody what to change:\n  {problem}")
    else:
        assert problem is None, (
            f"{host!r} with rp_id {rp_id!r} is a legitimate pairing and was "
            f"refused:\n  {problem}")


def test_the_page_refuses_where_the_operator_can_read_it(client, monkeypatch):
    """A JSON 422 inside an embedded WebView is a blank panel.

    The Windows shell shows the page. So the answer has to be a page.
    """
    monkeypatch.setenv("QRME_RP_ID", "qrme.app")
    got = client.get("/signatures/ceremony?mode=enroll&challenge=abc",
                     headers={"host": "127.0.0.1:8000"})
    assert got.status_code == 421, (
        "a ceremony fetched from an origin that cannot be a relying party "
        "should be refused; it was served, and the browser will refuse it "
        "instead with a message nobody can act on")
    assert "text/html" in got.headers["content-type"]
    assert "IP-address origin" in got.text
    assert "localhost" in got.text
    assert "navigator.credentials" not in got.text, (
        "the refusal still shipped the ceremony script — the page would try "
        "to run and fail in the browser anyway")


def test_a_matching_origin_still_gets_the_ceremony(client, monkeypatch):
    """A guard on the guard. A check that refused everything would satisfy
    the test above and break signing on every deployment."""
    monkeypatch.setenv("QRME_RP_ID", "localhost")
    got = client.get("/signatures/ceremony?mode=enroll&challenge=abc",
                     headers={"host": "localhost:8000"})
    assert got.status_code == 200, got.text
    assert "navigator.credentials" in got.text
    assert '"localhost"' in got.text, (
        "the page renders but does not carry the rp id into the call")


def test_the_windows_shell_does_not_send_the_webview_to_an_ip():
    """The client half. The backend can only refuse; the client is what
    decides which origin the WebView is pointed at in the first place."""
    source = (REPO / "native" / "windows" / "ApiClient.cs").read_text(
        encoding="utf-8")
    body = source[source.index("public string CeremonyUrl"):]
    body = body[:body.index("\n    public ")]
    code = re.sub(r"///[^\n]*", "", body)
    assert "localhost" in code, (
        "CeremonyUrl still navigates to whatever the base address is. The "
        "default base address is http://127.0.0.1:8000, and WebAuthn cannot "
        "use an IP-address origin, so Register and Sign fail before Windows "
        "Hello is ever shown.")
    assert "127.0.0.1" in code, (
        "the rewrite no longer names the loopback address it is rewriting")


def test_the_console_does_not_open_the_ceremony_on_an_ip():
    """The same fix on the other client that opens this page. The union of
    the two would have hidden whichever one was left behind."""
    source = (REPO / "app" / "src" / "api.ts").read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)
    opener = code[code.index("export function openCeremony"):]
    opener = opener[:opener.index("export function ceremonyOrigin")]
    assert "ceremonyOrigin(" in opener, (
        "openCeremony still uses getBase() directly, so the desktop console "
        "opens the ceremony on http://127.0.0.1 and the browser refuses it "
        "before any authenticator is reached")
    rewrite = code[code.index("export function ceremonyOrigin"):]
    # Backslashes out: the address is inside a regex literal, where it is
    # written `127\.0\.0\.1`. Searching the raw source for `127.0.0.1` finds
    # nothing and would have reported this rewrite missing while it was
    # sitting there — the same shape as everything else in this audit, in the
    # guard rather than the code.
    assert "localhost" in rewrite
    assert "127.0.0.1" in rewrite.replace("\\", ""), (
        "the rewrite no longer names the loopback address it is rewriting")


def test_the_field_test_document_exists_and_names_the_setting():
    """The refusal page points at this file. A pointer to a document that is
    not there is worse than no pointer."""
    doc = REPO / "docs" / "windows-hello-field-test.md"
    assert doc.exists(), (
        "the ceremony's refusal page tells the reader to see "
        "docs/windows-hello-field-test.md")
    text = doc.read_text(encoding="utf-8")
    for needed in ("QRME_RP_ID", "QRME_RP_ORIGINS", "localhost"):
        assert needed in text, (
            f"the field-test checklist does not mention {needed}, which is "
            "the setting the refusal tells the operator to change")
