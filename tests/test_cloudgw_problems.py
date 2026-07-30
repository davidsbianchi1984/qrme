"""The error-report intake.

The consoles send a batch of failed operations at launch — no messages, no
ids, no paths that were not redacted first. This is the gateway's side, and
like the contribution screen next door, the tests that matter are about
*refusing*: a report with an extra key, a path that still has an id in it, a
`platform` string long enough to hide a sentence.

The asymmetry with `test_cloud_gateway.py` is deliberate. A refused
contribution costs somebody their donated work, so that screen is careful. A
refused error report costs one lost diagnostic, so this one is merciless: the
whole value of the collection is that nobody has to trust it, and the way to
be worth that is to accept exactly one shape and nothing else.
"""

import json

import pytest
from fastapi.testclient import TestClient

from cloudgw import problems
from cloudgw.api import create_app
from cloudgw.model import StubProvider
from cloudgw.store import NoVault


def report(**over) -> dict:
    body = {
        "source": "qrme",
        "app_version": "0.18.0",
        "platform": "Win32",
        "language": "en-GB",
        "problems": [{
            "op": "POST /profiles/{id}/chat",
            "status": 500,
            "count": 3,
            "day": "2026-07-30",
            "fingerprint": "1a2b3c4d",
        }],
    }
    body.update(over)
    return body


@pytest.fixture()
def aggregate():
    return problems.Aggregate()


@pytest.fixture()
def client(aggregate):
    return TestClient(create_app(provider=StubProvider(), vault=NoVault(),
                                 aggregate=aggregate))


def test_a_well_formed_report_is_accepted_and_counted(client, aggregate):
    res = client.post("/v1/problems", json=report())
    assert res.status_code == 202
    assert res.json() == {"accepted": True, "problems": 1, "failures": 3}
    assert aggregate.rows()[0]["count"] == 3


def test_counts_add_up_across_reports(client, aggregate):
    client.post("/v1/problems", json=report())
    client.post("/v1/problems", json=report())
    rows = aggregate.rows()
    assert len(rows) == 1, "the same operation on the same build is one row"
    assert rows[0]["count"] == 6


def test_the_worst_thing_is_first(client, aggregate):
    client.post("/v1/problems", json=report(problems=[
        {"op": "GET /profiles/{id}/feed", "status": 404, "count": 1,
         "day": "2026-07-30", "fingerprint": "aaaaaaaa"},
        {"op": "POST /profiles/{id}/chat", "status": 500, "count": 40,
         "day": "2026-07-30", "fingerprint": "bbbbbbbb"},
    ]))
    assert aggregate.rows()[0]["op"] == "POST /profiles/{id}/chat"


# ── the refusals ─────────────────────────────────────────────────────────────

def test_an_unredacted_id_is_refused_rather_than_redacted(client, aggregate):
    """The one that justifies the whole file.

    The gateway could fix this path itself — the pattern is right there. It
    does not, because then a build whose redaction had broken would keep
    working, and nobody would learn that every report from those users had
    arrived carrying a profile id.
    """
    res = client.post("/v1/problems", json=report(problems=[{
        "op": "POST /profiles/prf_0de08e794ed0/chat",
        "status": 500, "count": 1, "day": "2026-07-30",
        "fingerprint": "1a2b3c4d",
    }]))
    assert res.status_code == 422
    assert "prf_0de08e794ed0" in res.json()["detail"]
    assert "redaction is not working" in res.json()["detail"]
    assert aggregate.rows() == [], "a refused report leaves nothing behind"


@pytest.mark.parametrize("segment", [
    "usr_1",                                    # short ids are still ids
    "12345",
    "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",     # long enough to be a token
])
def test_every_shape_of_identifier_is_caught(client, segment):
    res = client.post("/v1/problems", json=report(problems=[{
        "op": f"GET /users/{segment}/captures", "status": 404, "count": 1,
        "day": "2026-07-30", "fingerprint": "1a2b3c4d",
    }]))
    assert res.status_code == 422, f"{segment!r} was accepted as a route name"


def test_a_message_field_is_refused(client):
    """The leak this intake exists to catch."""
    res = client.post("/v1/problems", json=report(problems=[{
        "op": "POST /profiles/{id}/chat", "status": 500, "count": 1,
        "day": "2026-07-30", "fingerprint": "1a2b3c4d",
        "message": "no device called 'Pixel Buds' on this account",
    }]))
    assert res.status_code == 422
    assert "message" in res.json()["detail"]


def test_an_unknown_top_level_key_is_refused_not_ignored(client):
    res = client.post("/v1/problems", json=report(notes="whatever"))
    assert res.status_code == 422
    assert "notes" in res.json()["detail"]


def test_a_long_platform_string_cannot_smuggle_a_sentence(client):
    res = client.post("/v1/problems",
                      json=report(platform="Win32 " + "x" * 200))
    assert res.status_code == 422
    assert "platform" in res.json()["detail"]


def test_a_newline_in_a_short_field_is_refused(client):
    """Where a stack trace would arrive if one ever did."""
    res = client.post("/v1/problems",
                      json=report(app_version="0.18.0\nTraceback…"))
    assert res.status_code == 422


@pytest.mark.parametrize("field,value", [
    ("app_version", "0.18.0\n"),
    ("platform", "Win32\n"),
])
def test_even_a_trailing_newline_is_refused(client, field, value):
    """The case every one of these patterns originally let through.

    Python's `$` matches before a trailing newline as well as at the end of
    the string, so `^…$` accepted "Win32\\n" while the error message beside it
    said newlines were not allowed. Harmless in itself — one invisible
    character — but a validator that is wrong about its own rule is not one to
    keep trusting, and the fix (`\\Z`) is a character. Kept as a test because
    the next person writing a pattern here will reach for `$` too.
    """
    assert client.post("/v1/problems",
                       json=report(**{field: value})).status_code == 422


def test_a_trailing_newline_in_the_operation_is_refused(client):
    assert client.post("/v1/problems", json=report(problems=[{
        "op": "GET /health\n", "status": 500, "count": 1,
        "day": "2026-07-30", "fingerprint": "1a2b3c4d",
    }])).status_code == 422


def test_a_time_of_day_is_refused(client):
    """A day is the finest time this keeps, on purpose: a timestamp to the
    second is a record of when somebody was using their computer."""
    res = client.post("/v1/problems", json=report(problems=[{
        "op": "POST /profiles/{id}/chat", "status": 500, "count": 1,
        "day": "2026-07-30T14:23:11Z", "fingerprint": "1a2b3c4d",
    }]))
    assert res.status_code == 422
    assert "movement record" in res.json()["detail"]


def test_a_batch_larger_than_the_console_could_hold_is_refused(client):
    res = client.post("/v1/problems", json=report(problems=[
        {"op": "GET /health", "status": 500, "count": 1,
         "day": "2026-07-30", "fingerprint": f"{i:08x}"}
        for i in range(problems.MAX_PROBLEMS + 1)
    ]))
    assert res.status_code == 422


def test_a_foreign_source_is_refused(client):
    assert client.post("/v1/problems",
                       json=report(source="somebody-elses-app")).status_code == 422


# ── what is kept, and what is not ────────────────────────────────────────────

def test_the_language_is_validated_and_then_not_kept(client, aggregate):
    """The gateway keeps less than it is given.

    Every dimension in the key narrows a row towards one install. Platform and
    version are what triage actually needs; locale is not, so it is checked on
    the way in and then dropped. The console shows the user everything that
    leaves their machine — this is the part where less of it survives.
    """
    client.post("/v1/problems", json=report(language="pt-BR"))
    row = aggregate.rows()[0]
    assert "language" not in row
    assert "pt-BR" not in json.dumps(row)


def test_nothing_records_that_a_particular_install_reported(client, aggregate):
    """No row can be traced to a device, a session, or a moment finer than a
    day — which is what makes a plain unencrypted counter file defensible
    where an unencrypted contribution store would not be."""
    client.post("/v1/problems", json=report())
    row = aggregate.rows()[0]
    assert set(row) == {"source", "app_version", "platform", "op", "status",
                        "count", "first_day", "last_day"}


def test_the_counters_survive_a_restart(tmp_path):
    path = tmp_path / "problems.json"
    first = problems.Aggregate(path)
    first.add(problems.screen(report()))
    assert problems.Aggregate(path).rows()[0]["count"] == 3


def test_a_corrupt_counter_file_does_not_take_the_gateway_down(tmp_path):
    path = tmp_path / "problems.json"
    path.write_text("{ this is not json", "utf-8")
    assert problems.Aggregate(path).rows() == []


def test_a_file_that_parses_but_is_not_counters_is_ignored(tmp_path):
    """The case the test above missed, found by tripping over it.

    Unparseable JSON was handled from the start. *Parseable* JSON of the wrong
    shape was not — and it is the likelier accident: a half-written file that
    happens to close its braces, an older format, or `CLOUDGW_PROBLEMS_PATH`
    pointed at a file that was already there. The aggregate adopted whatever
    it found, and `GET /v1/problems` then died with a 500 sorting values that
    had no `count`.

    Which is how it was found: a scratch file of unrelated JSON got reused as
    a counter path while driving the client, and the read blew up. A test
    written from imagination would have reached for `"{ this is not json"`
    again and stayed green.
    """
    path = tmp_path / "problems.json"
    path.write_text(json.dumps({
        "title": "some other tool's file",
        "body": "prose, not a counter",
    }), "utf-8")
    agg = problems.Aggregate(path)
    assert agg.rows() == []

    # And it still works afterwards rather than being poisoned by the file.
    agg.add(problems.screen(report()))
    assert agg.rows()[0]["count"] == 3


def test_a_partly_valid_counter_file_keeps_the_valid_rows(tmp_path):
    """Salvage rather than discard. A single malformed row should not throw
    away months of real counts sitting beside it in the same file."""
    good = {"source": "qrme", "app_version": "0.18.0", "platform": "Win32",
            "op": "GET /health", "status": 500, "count": 9,
            "first_day": "2026-07-01", "last_day": "2026-07-30"}
    path = tmp_path / "problems.json"
    path.write_text(json.dumps({"good": good, "bad": "not a row",
                                "alsobad": {"op": "GET /x"}}), "utf-8")
    rows = problems.Aggregate(path).rows()
    assert len(rows) == 1 and rows[0]["count"] == 9


# ── the preflight ────────────────────────────────────────────────────────────

def test_a_browser_preflight_from_a_desktop_console_succeeds(client):
    """The check that nearly did not get written, and would have killed this.

    The sender posts JSON with an `authorization` header, which makes it a
    non-simple request: the browser sends `OPTIONS` first and refuses to make
    the real call unless that is answered. Without CORS the gateway would 405
    the preflight, every report would fail, and the sender swallows failures —
    so the feature would be dead in the field with nothing to show for it. No
    test here asserts on a browser, so this asserts on the preflight.

    `Origin: null` is not a placeholder. It is what an Electron renderer
    actually sends, because it loads the console from `file://` — which is
    also why there is no origin allowlist to write.
    """
    res = client.options("/v1/problems", headers={
        "Origin": "null",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,authorization",
    })
    assert res.status_code == 200, (
        "the preflight was refused, so no console will ever deliver a report")
    assert res.headers["access-control-allow-origin"] == "*"


def test_the_preflight_does_not_hand_out_ambient_authority(client):
    """Wide origins are only safe while credentials stay off.

    Allowing `*` costs nothing here because every endpoint needs a bearer
    presented explicitly — but the moment cookies were allowed to ride along,
    `*` would mean any page could spend this gateway's model budget using
    somebody else's browser. The two settings have to move together, so the
    test names the pair rather than either alone.
    """
    res = client.options("/v1/problems", headers={
        "Origin": "https://somebody-elses-site.example",
        "Access-Control-Request-Method": "POST",
    })
    assert res.headers.get("access-control-allow-credentials") != "true", (
        "credentials are allowed alongside a wildcard origin")


# ── who may read it ──────────────────────────────────────────────────────────

def test_the_token_that_posts_may_not_read(monkeypatch):
    """The intake token ships inside every installer, so it is public the
    moment somebody unzips one. Reading the aggregate is a live map of what
    fails on every build, and that stays with named callers."""
    monkeypatch.setenv("CLOUDGW_TOKENS", "consoles:shipped-token,dave:my-token")
    monkeypatch.setenv("CLOUDGW_PROBLEM_READERS", "dave")
    app = TestClient(create_app(provider=StubProvider(), vault=NoVault(),
                                aggregate=problems.Aggregate()))

    posting = {"Authorization": "Bearer shipped-token"}
    assert app.post("/v1/problems", json=report(), headers=posting).status_code == 202
    assert app.get("/v1/problems", headers=posting).status_code == 403

    reading = {"Authorization": "Bearer my-token"}
    assert app.get("/v1/problems", headers=reading).json()["rows"][0]["count"] == 3


def test_an_unconfigured_reader_list_means_nobody_but_the_developer(monkeypatch):
    """Fail closed, like every other gate on this gateway: an operator who has
    not decided yet gets 'no', not 'everyone'."""
    monkeypatch.setenv("CLOUDGW_TOKENS", "consoles:shipped-token")
    monkeypatch.delenv("CLOUDGW_PROBLEM_READERS", raising=False)
    app = TestClient(create_app(provider=StubProvider(), vault=NoVault(),
                                aggregate=problems.Aggregate()))
    assert app.get("/v1/problems",
                   headers={"Authorization": "Bearer shipped-token"}).status_code == 403


def test_an_unauthenticated_report_is_refused_when_tokens_are_configured(monkeypatch):
    monkeypatch.setenv("CLOUDGW_TOKENS", "consoles:shipped-token")
    app = TestClient(create_app(provider=StubProvider(), vault=NoVault(),
                                aggregate=problems.Aggregate()))
    assert app.post("/v1/problems", json=report()).status_code == 401
