"""The other end of the wire JIM's contact calls were never plugged into.

    asked     did JIM call anybody
    mattered  there was nothing at the other end of the wire

`jim/reachout.py` rings a trusted person, asks them to press 1, and then
talks — and every step of it was driven by tests standing in for a phone
company's webhooks, with `JIM_VOICE_URL` pointing at nothing on the box.
`docker/voice/server.py` is that something: the credential holder, the
translator, the two locks on every vendor door, the line machine that
speaks only what JIM hands it, and the second refusal under JIM's own for
any number that is an emergency short code.

These exercise the sidecar directly with both wires stubbed — the one
toward the phone house (`server._house_http`) and the one toward JIM
(`server._jim`) — the way the camera's tests drive `docker/film`. The
translation is the whole of what it does, and the translation is what
breaks when a house renames a field or JIM changes a word.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import importlib
import importlib.util
import json
import pathlib
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa
from fastapi.testclient import TestClient

REPO = pathlib.Path(__file__).resolve().parent.parent
VOICE = REPO / "docker" / "voice"
SERVER = VOICE / "server.py"

SECRET = "test-secret"
PUB = "https://x.test/voice"
TOKEN = "test-token"
ACCOUNT = "AC00000000000000000000000000a1b2"
FROM = "+15550001111"
TO = "+15551110000"
CALL = "rcl_7f3a"

OPENING = ("This is JIM calling on behalf of Ada about a fall with no "
           "answer. Press 1 to hear the message, or 2 to not be called this "
           "way again.")
TROUBLE = ("I am having trouble speaking right now. Please check on them. "
           "Goodbye.")
LINE_OPEN = {"say": OPENING, "then": "gather_digit", "language": "en",
             "again": "Please press 1 to hear the message, or 2 to not be "
                      "called this way again.",
             "close": "No choice was made. Goodbye.", "trouble": TROUBLE}
LINE_CONSENTED = {"say": "Thank you. I'll tell you what's happening, and you "
                         "can ask me anything.",
                  "then": "speak_first", "language": "en", "again": None,
                  "close": None, "trouble": TROUBLE}
LINE_DECLINED = {"say": "Understood. You will not be called this way again. "
                        "Goodbye.", "then": "hangup", "language": "en",
                 "again": None, "close": None, "trouble": TROUBLE}
LINE_NO_CHOICE = {"say": "No choice was made. Goodbye.", "then": "hangup",
                  "language": "en", "again": None, "close": None,
                  "trouble": TROUBLE}
SAID = "Ada fell in the kitchen and has not answered for ten minutes."
LINE_TALK = {"say": SAID, "then": "gather_speech", "language": "en",
             "again": "Are you still there? You can ask me anything, or hang "
                      "up when you are done.",
             "close": "Thank you. Please check on them. Goodbye.",
             "trouble": TROUBLE}
LINE_CLOSE = {"say": SAID + " Thank you. Please check on them. Goodbye.",
              "then": "hangup", "language": "en", "again": None,
              "close": None, "trouble": TROUBLE}

ENV = {
    "VOICE_PROVIDER": "twilio", "VOICE_SECRET": SECRET,
    "VOICE_PUBLIC_URL": PUB, "VOICE_FROM": FROM, "VOICE_ACCOUNT": ACCOUNT,
    "VOICE_TOKEN": TOKEN, "VOICE_JIM_URL": "http://jim.test:8200",
}


@pytest.fixture()
def voice(monkeypatch):
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)
    for name in ("VOICE_WEBHOOK_KEY", "VOICE_HOUSE_REF", "VOICE_TOKEN_FILE",
                 "VOICE_LANG_EN"):
        monkeypatch.delenv(name, raising=False)
    if str(VOICE) not in sys.path:
        sys.path.insert(0, str(VOICE))
    spec = importlib.util.spec_from_file_location("voice_server", SERVER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._LINES.clear()
    module._PROBES.clear()
    return module


@pytest.fixture()
def door(voice):
    return TestClient(voice.app)


@dataclass
class Sent:
    method: str
    url: str
    headers: dict
    body: bytes | None
    timeout: float

    @property
    def form(self) -> dict:
        return {k: v[0] for k, v in urllib.parse.parse_qs(
            (self.body or b"").decode(), keep_blank_values=True).items()}

    @property
    def json(self) -> dict:
        return json.loads(self.body or b"{}")


class FakeHouse:
    """A stand-in for `server._house_http`: records every request toward the
    internet and answers from a script keyed by a fragment of the URL."""

    def __init__(self, answer=(201, {"sid": "CA0123", "status": "queued"})):
        self.calls: list[Sent] = []
        self.script: dict = {}
        self.default = answer

    def __call__(self, method, url, *, headers=None, body=None, timeout=10.0):
        self.calls.append(Sent(method, url, dict(headers or {}), body, timeout))
        for key, answer in self.script.items():
            if key in url:
                return self._answer(answer)
        return self._answer(self.default)

    @staticmethod
    def _answer(answer):
        if callable(answer):
            answer = answer()
        status, body = answer
        return status, body if isinstance(body, str) else json.dumps(body)

    def sent(self, fragment: str) -> list[Sent]:
        return [s for s in self.calls if fragment in s.url]


@dataclass
class Asked:
    method: str
    path: str
    body: dict | None
    bearer: str | None
    timeout: float


class FakeJim:
    """A stand-in for `server._jim`: records every request toward JIM — with
    the bearer it carried — and answers each call-id door from a script."""

    def __init__(self, **script):
        self.calls: list[Asked] = []
        self.script = script

    def __call__(self, method, url, *, headers, data, timeout):
        path = urllib.parse.urlsplit(url).path
        body = json.loads(data) if data else None
        self.calls.append(Asked(method, path, body,
                                headers.get("Authorization"), timeout))
        answer = self.script.get(path.rsplit("/", 1)[-1])
        if answer is None:
            return 404, {"detail": "no such call"}
        if callable(answer):
            answer = answer(body)
        return answer

    def to(self, leg: str) -> list[Asked]:
        return [c for c in self.calls if c.path.endswith("/" + leg)]


def ok(line: dict, **more) -> tuple[int, dict]:
    return 200, {"status": "ringing", "call": {"id": CALL}, "line": line,
                 **more}


def sign_twilio(url: str, params: dict, token: str = TOKEN) -> str:
    tail = "".join(k + params[k] for k in sorted(params))
    return base64.b64encode(hmac.new(token.encode(), (url + tail).encode(),
                                     hashlib.sha1).digest()).decode()


def twilio_post(door, voice, leg, params, *, query="", call_id=CALL,
                house="twilio", sig=None, signed_base=PUB, token=TOKEN,
                headers=None, body=None):
    """One webhook as Twilio would send it: form-encoded, signed over the
    public URL plus the sorted fields, with the per-call sig on the URL."""
    sig = sig if sig is not None else voice._sig(SECRET, call_id)
    q = f"sig={sig}" + (f"&{query}" if query else "")
    path = f"/{house}/{call_id}/{leg}"
    signed_url = f"{signed_base}{path}?{q}"
    hdrs = {"Content-Type": "application/x-www-form-urlencoded",
            "X-Twilio-Signature": sign_twilio(signed_url, params, token)}
    hdrs.update(headers or {})
    return door.post(f"/voice{path}?{q}",
                     content=body if body is not None
                     else urllib.parse.urlencode(params), headers=hdrs)


def twiml(response) -> ET.Element:
    assert response.status_code == 200, response.text
    assert "xml" in response.headers["content-type"]
    root = ET.fromstring(response.text)
    assert root.tag == "Response"
    return root


def bearer(secret: str = SECRET) -> dict:
    return {"Authorization": f"Bearer {secret}"}


def order(**changes) -> dict:
    body = {"call_id": CALL, "to": TO, "opening": OPENING, "language": "en",
            "provider": "twilio",
            "limits": {"ring_seconds": 25, "max_call_seconds": 600,
                       "machine_detection": True}}
    body.update(changes)
    return body


# --------------------------------------------------------------------------- #
# 1. the table
# --------------------------------------------------------------------------- #

def _sibling_root() -> pathlib.Path | None:
    for candidate in (REPO.parent / "jim-mini", pathlib.Path("/workspace/jim-mini"),
                      REPO.parent / "JIM-mini"):
        if (candidate / "jim" / "dialer.py").exists():
            return candidate
    return None


def test_the_houses_are_the_providers_jim_offers(voice, monkeypatch):
    """The shelf and the adapter cannot disagree.

    A name in JIM's `dialer.PROVIDERS` with no row here is a provider the
    operator can pick that refuses — the camera's defect, one product over.
    Imported from the sibling checkout when it is on disk, as the camera
    test imports `qrme.filming`; skipped honestly when it is not.
    """
    root = _sibling_root()
    if root is None:
        pytest.skip("JIM-mini is not checked out beside this product")
    monkeypatch.syspath_prepend(str(root))
    sys.modules.pop("jim.dialer", None)
    dialer = importlib.import_module("jim.dialer")
    assert set(voice.HOUSES) == set(dialer.PROVIDERS)


def test_every_house_implements_the_whole_interface(voice):
    base = voice.House
    for name, row in voice.HOUSES.items():
        assert row.name == name
        for method in ("create_call", "verify", "parse", "render", "standing"):
            assert getattr(row, method) is not getattr(base, method), (
                f"{name} inherits the base's {method}, which refuses")
        assert callable(getattr(row, "lang"))
        assert row(voice._config(), lambda *a, **k: (200, "{}")).lang("en") \
            == "en-US"


def test_a_language_tag_can_be_corrected_without_a_rebuild(voice, monkeypatch):
    monkeypatch.setenv("VOICE_LANG_EN", "en-GB")
    assert voice.houses.lang_tag("en") == "en-GB"
    monkeypatch.setenv("VOICE_TWILIO_API", "https://relay.example/2010-04-01")
    row = voice.HOUSES["twilio"](voice._config(), lambda *a, **k: (200, "{}"))
    assert row.base == "https://relay.example/2010-04-01"


# --------------------------------------------------------------------------- #
# 2. the refusals, in sentences, before any house is asked
# --------------------------------------------------------------------------- #

def test_health_never_hands_back_the_token_or_the_account(door):
    got = door.get("/health").json()
    assert got["ok"] is True
    assert got["keyed"] is True and got["secret_set"] is True
    assert got["providers"] == ["plivo", "signalwire", "telnyx", "twilio",
                                "vonage"]
    assert got["public_url_well_formed"] is True
    for secret in (TOKEN, ACCOUNT, SECRET):
        assert secret not in repr(got)


def test_calls_with_no_secret_refuses_naming_it(voice, door, monkeypatch):
    house = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.delenv("VOICE_SECRET")
    got = door.post("/calls", json=order(), headers=bearer())
    assert got.status_code == 503
    assert "VOICE_SECRET" in got.json()["detail"]
    assert house.calls == []


def test_calls_with_no_bearer_is_401_and_a_wrong_one_403(voice, door,
                                                          monkeypatch):
    house = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", house)
    assert door.post("/calls", json=order()).status_code == 401
    assert door.post("/calls", json=order()).json()["detail"] == \
        "voice adapter token required"
    wrong = door.post("/calls", json=order(), headers=bearer("nope"))
    assert wrong.status_code == 403
    assert wrong.json()["detail"] == "invalid voice adapter token"
    assert house.calls == []


def test_an_unkeyed_adapter_names_voice_token(voice, door, monkeypatch):
    house = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.delenv("VOICE_TOKEN")
    got = door.post("/calls", json=order(), headers=bearer())
    assert got.status_code == 503
    assert "VOICE_TOKEN" in got.json()["detail"]
    assert house.calls == []


@pytest.mark.parametrize("variable,value,named", [
    ("VOICE_FROM", None, "JIM_VOICE_FROM"),
    ("VOICE_PUBLIC_URL", None, "JIM_VOICE_PUBLIC_URL"),
    ("VOICE_PUBLIC_URL", "https://x.test/phone", "must end in /voice"),
])
def test_a_missing_address_names_the_variable(voice, door, monkeypatch,
                                              variable, value, named):
    house = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", house)
    if value is None:
        monkeypatch.delenv(variable)
    else:
        monkeypatch.setenv(variable, value)
    got = door.post("/calls", json=order(), headers=bearer())
    assert got.status_code == 503
    assert named in got.json()["detail"]
    assert house.calls == []


def test_a_provider_mismatch_is_409(voice, door, monkeypatch):
    house = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setenv("VOICE_PROVIDER", "signalwire")
    got = door.post("/calls", json=order(provider="twilio"), headers=bearer())
    assert got.status_code == 409
    assert got.json()["detail"] == ("this adapter is keyed for signalwire, "
                                    "not twilio — set JIM_TELEPHONY_PROVIDER "
                                    "to match")
    assert house.calls == []


@pytest.mark.parametrize("house", ["twilio", "signalwire", "telnyx", "vonage",
                                   "plivo"])
@pytest.mark.parametrize("number", ["911", "+1911", "9-1-1", " 999 ", "112",
                                    "(1) 911", "00 112"])
def test_an_emergency_number_never_reaches_the_house(voice, door, monkeypatch,
                                                     house, number):
    """The lock under JIM's lock, for every row: the same digits JIM refuses
    are refused here before a house is asked, so the two containers cannot
    disagree about who this door rings."""
    stub = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", stub)
    monkeypatch.setenv("VOICE_PROVIDER", house)
    monkeypatch.setenv("VOICE_HOUSE_REF", "space")
    monkeypatch.setenv("VOICE_WEBHOOK_KEY", "k")
    got = door.post("/calls", json=order(to=number, provider=house),
                    headers=bearer())
    assert got.status_code == 422
    assert got.json()["detail"] == "this door does not ring emergency numbers"
    assert stub.calls == []


def test_the_emergency_rule_normalises_the_way_jim_does(voice):
    for bad in ("911", "+1911", "9-1-1", " 999 ", "112", "1-1-2", "+112",
                "000", "111", "119", "110", "122", "15", "17", "18", "1.1.2"):
        assert voice.is_emergency(bad), bad
    for fine in (TO, "5551110000", "+44 20 7946 0000", "00 44 20 7946 0000",
                 "9110000000"):
        assert not voice.is_emergency(fine), fine
    assert voice.normalize("(555) 111-0000") == "+15551110000"
    assert voice.normalize("00 44 20 7946 0000") == "+442079460000"


def test_a_channel_that_is_not_a_number_is_refused_in_words(voice, door,
                                                            monkeypatch):
    stub = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", stub)
    got = door.post("/calls", json=order(to="ada@example.org"),
                    headers=bearer())
    assert got.status_code == 422
    assert "not a phone number" in got.json()["detail"]
    assert stub.calls == []


# --------------------------------------------------------------------------- #
# 3. Twilio create-call
# --------------------------------------------------------------------------- #

def test_twilio_create_call_sends_what_the_house_expects(voice, door,
                                                         monkeypatch):
    house = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", house)
    got = door.post("/calls", json=order(), headers=bearer())
    assert got.status_code == 201, got.text
    assert got.json() == {"placed": True, "provider": "twilio",
                          "provider_call_id": "CA0123", "status": "queued"}
    [sent] = house.calls
    assert sent.method == "POST"
    assert sent.url == (f"https://api.twilio.com/2010-04-01/Accounts/"
                        f"{ACCOUNT}/Calls.json")
    assert sent.headers["Authorization"] == "Basic " + base64.b64encode(
        f"{ACCOUNT}:{TOKEN}".encode()).decode()
    assert sent.headers["Content-Type"] == "application/x-www-form-urlencoded"
    sig = voice._sig(SECRET, CALL)
    fields = sent.form
    assert fields["To"] == TO and fields["From"] == FROM
    assert fields["Url"] == f"{PUB}/twilio/{CALL}/answer?sig={sig}"
    assert fields["Method"] == "POST"
    assert fields["StatusCallback"] == f"{PUB}/twilio/{CALL}/status?sig={sig}"
    assert fields["StatusCallbackMethod"] == "POST"
    assert fields["StatusCallbackEvent"] == "completed"
    assert fields["Timeout"] == "25" and fields["TimeLimit"] == "600"
    assert fields["MachineDetection"] == "Enable"
    assert fields["MachineDetectionTimeout"] == "8"
    # The capability in the URL is the one this door will check on return.
    carried = urllib.parse.parse_qs(urllib.parse.urlsplit(fields["Url"]).query)
    assert hmac.compare_digest(carried["sig"][0], voice._sig(SECRET, CALL))
    assert len(carried["sig"][0]) == 32


def test_the_limits_jim_sends_reach_the_house(voice, door, monkeypatch):
    house = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", house)
    got = door.post("/calls", json=order(limits={
        "ring_seconds": 30, "max_call_seconds": 300,
        "machine_detection": False}), headers=bearer())
    assert got.status_code == 201
    fields = house.calls[0].form
    assert fields["Timeout"] == "30" and fields["TimeLimit"] == "300"
    assert "MachineDetection" not in fields


def test_a_400_from_the_house_becomes_422_quoting_it(voice, door, monkeypatch):
    house = FakeHouse((400, {"code": 21211, "message": "The 'To' number "
                             "+1555 is not a valid phone number.",
                             "status": 400}))
    monkeypatch.setattr(voice, "_house_http", house)
    got = door.post("/calls", json=order(), headers=bearer())
    assert got.status_code == 422
    assert got.json()["detail"] == ("the house refused this number: 21211 "
                                    "The 'To' number +1555 is not a valid "
                                    "phone number.")


def test_a_401_from_the_house_is_502(voice, door, monkeypatch):
    house = FakeHouse((401, {"code": 20003, "message": "Authenticate"}))
    monkeypatch.setattr(voice, "_house_http", house)
    got = door.post("/calls", json=order(), headers=bearer())
    assert got.status_code == 502
    assert got.json()["detail"].startswith("the house answered 401")
    assert TOKEN not in got.text


def test_an_unreachable_house_is_502(voice, door, monkeypatch):
    def down(*a, **k):
        raise voice.houses.Unreachable("[Errno -2] Name or service not known")
    monkeypatch.setattr(voice, "_house_http", down)
    got = door.post("/calls", json=order(), headers=bearer())
    assert got.status_code == 502
    assert got.json()["detail"] == ("the house could not be reached: [Errno "
                                    "-2] Name or service not known")


def test_a_201_without_a_sid_is_502(voice, door, monkeypatch):
    monkeypatch.setattr(voice, "_house_http", FakeHouse((201, {"status":
                                                               "queued"})))
    got = door.post("/calls", json=order(), headers=bearer())
    assert got.status_code == 502
    assert got.json()["detail"] == "the house answered without a call to follow"


def test_the_house_helper_redacts_nothing_because_it_carries_nothing(voice,
                                                                     monkeypatch):
    """The one urlopen toward the house raises with the reason and never
    with the request — the Authorization header is not in any message."""
    import urllib.error

    def refuse(req, timeout):
        raise urllib.error.URLError("connection refused")
    monkeypatch.setattr(voice.urllib.request, "urlopen", refuse)
    with pytest.raises(voice.houses.Unreachable) as raised:
        voice._house_http("GET", "https://api.twilio.com/x",
                          headers={"Authorization": f"Basic {TOKEN}"})
    assert "connection refused" in str(raised.value)
    assert TOKEN not in str(raised.value)


# --------------------------------------------------------------------------- #
# 4. signatures: the two locks on every vendor door
# --------------------------------------------------------------------------- #

def test_the_twilio_verifier_reproduces_the_documented_vector(voice):
    """Twilio's own published example: the token, URL and fields from its
    request-validation documentation and SDK tests, and the signature
    they say to expect."""
    token = "12345"
    url = "https://mycompany.com/myapp.php?foo=1&bar=2"
    params = {"CallSid": "CA1234567890ABCDE", "Caller": "+14158675309",
              "Digits": "1234", "From": "+14158675309", "To": "+18005551212"}
    cfg = voice.Config(provider="twilio", secret=SECRET, jim_url="",
                       public_url=PUB, from_=FROM, account=ACCOUNT,
                       token=token, webhook_key="", house_ref="")
    row = voice.HOUSES["twilio"](cfg, lambda *a, **k: (200, "{}"))
    body = urllib.parse.urlencode(params).encode()
    assert row.verify(url, {"x-twilio-signature":
                            "RSOYDt4T1cUTdK1PDd93/VVr8B8="}, body)
    assert not row.verify(url, {"x-twilio-signature":
                                "RSOYDt4T1cUTdK1PDd93/VVr8B8="},
                          body + b"&Digits=5")


def test_a_signature_over_the_public_url_passes(voice, door, monkeypatch):
    jim = FakeJim(event=lambda body: ok(LINE_OPEN))
    monkeypatch.setattr(voice, "_jim", jim)
    got = twilio_post(door, voice, "answer", {"CallSid": "CA0123",
                                              "CallStatus": "in-progress",
                                              "AnsweredBy": "human"})
    twiml(got)
    assert len(jim.calls) == 1


@pytest.mark.parametrize("wrong", ["body", "token", "host", "sig", "none"])
def test_a_forged_webhook_is_403_empty_and_jim_hears_nothing(voice, door,
                                                             monkeypatch,
                                                             wrong):
    """Five ways to forge, one answer: 403 with an empty body, logged, and
    nothing posted to JIM — a forged status callback cannot move the
    cascade. Including a Host-header URL: the signed URL is rebuilt from
    VOICE_PUBLIC_URL, so a spoofed forwarded header does not help."""
    jim = FakeJim(event=lambda body: ok(LINE_OPEN))
    monkeypatch.setattr(voice, "_jim", jim)
    params = {"CallSid": "CA0123", "CallStatus": "in-progress",
              "AnsweredBy": "human"}
    kwargs = {}
    if wrong == "body":
        kwargs["body"] = urllib.parse.urlencode({**params,
                                                 "AnsweredBy": "machine_start"})
    elif wrong == "token":
        kwargs["token"] = "other-token"
    elif wrong == "host":
        kwargs["signed_base"] = "https://evil.example/voice"
        kwargs["headers"] = {"Host": "evil.example",
                             "X-Forwarded-Host": "evil.example"}
    elif wrong == "sig":
        kwargs["sig"] = "0" * 32
    elif wrong == "none":
        kwargs["headers"] = {"X-Twilio-Signature": ""}
    got = twilio_post(door, voice, "answer", params, **kwargs)
    assert got.status_code == 403
    assert got.content == b""
    assert jim.calls == []


def test_the_sig_is_checked_before_the_house_is_consulted(voice, door,
                                                          monkeypatch):
    """A wrong sig with a perfectly valid vendor signature is still 403:
    the capability is the floor under every house's scheme."""
    jim = FakeJim(event=lambda body: ok(LINE_OPEN))
    monkeypatch.setattr(voice, "_jim", jim)
    seen = []
    real = voice.HOUSES["twilio"].verify

    def spy(self, *a, **k):
        seen.append(True)
        return real(self, *a, **k)
    monkeypatch.setattr(voice.HOUSES["twilio"], "verify", spy)
    got = twilio_post(door, voice, "answer", {"CallSid": "CA0123"},
                      sig=voice._sig("another-secret", CALL))
    assert got.status_code == 403 and got.content == b""
    assert seen == [] and jim.calls == []


def test_a_call_id_nobody_minted_is_a_403_not_a_404(voice, door, monkeypatch):
    """The id is a capability against enumeration; its sig is the proof."""
    jim = FakeJim()
    monkeypatch.setattr(voice, "_jim", jim)
    got = twilio_post(door, voice, "status", {"CallStatus": "completed"},
                      call_id="rcl_guess", sig=voice._sig(SECRET, CALL))
    assert got.status_code == 403 and jim.calls == []


def test_plivo_hmac_sha256_with_a_nonce_verifies(voice, door, monkeypatch):
    monkeypatch.setenv("VOICE_PROVIDER", "plivo")
    jim = FakeJim(event=lambda body: ok(LINE_OPEN))
    monkeypatch.setattr(voice, "_jim", jim)
    sig = voice._sig(SECRET, CALL)
    path = f"/plivo/{CALL}/answer"
    nonce = "n0nce"
    # Plivo's published V2 signs the URL without its query string.
    bare = f"{PUB}{path}"
    good = base64.b64encode(hmac.new(TOKEN.encode(), (bare + nonce).encode(),
                                     hashlib.sha256).digest()).decode()
    body = urllib.parse.urlencode({"CallUUID": "u-1", "CallStatus":
                                   "in-progress"})
    got = door.post(f"/voice{path}?sig={sig}", content=body, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Plivo-Signature-V2": good, "X-Plivo-Signature-V2-Nonce": nonce})
    assert got.status_code == 200, got.text
    root = ET.fromstring(got.text)
    assert root.find("GetInput") is not None
    assert len(jim.calls) == 1
    # The full URL, as the design text names it, is accepted too.
    full = base64.b64encode(hmac.new(
        TOKEN.encode(), (f"{bare}?sig={sig}" + nonce).encode(),
        hashlib.sha256).digest()).decode()
    got = door.post(f"/voice{path}?sig={sig}", content=body, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Plivo-Signature-V2": full, "X-Plivo-Signature-V2-Nonce": nonce})
    assert got.status_code == 200
    # A different nonce, a wrong token: 403 empty, JIM hears nothing.
    for bad_nonce, bad_sig in (("other", good), (nonce, full[:-4] + "AAAA")):
        got = door.post(f"/voice{path}?sig={sig}", content=body, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Plivo-Signature-V2": bad_sig,
            "X-Plivo-Signature-V2-Nonce": bad_nonce})
        assert got.status_code == 403 and got.content == b""
    assert len(jim.calls) == 2


def test_telnyx_ed25519_verifies_and_refuses_a_stale_timestamp(voice, door,
                                                               monkeypatch):
    private = ed25519.Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    monkeypatch.setenv("VOICE_PROVIDER", "telnyx")
    monkeypatch.setenv("VOICE_HOUSE_REF", "app-1")
    monkeypatch.setenv("VOICE_WEBHOOK_KEY", base64.b64encode(public).decode())
    jim = FakeJim(event=lambda body: ok(LINE_OPEN))
    monkeypatch.setattr(voice, "_jim", jim)
    sig = voice._sig(SECRET, CALL)
    path = f"/telnyx/{CALL}/answer"
    body = urllib.parse.urlencode({"CallSid": "v3:abc", "AnsweredBy": "human"})

    def headers(stamp: int, signed: bytes) -> dict:
        mark = private.sign(f"{stamp}|".encode() + signed)
        return {"Content-Type": "application/x-www-form-urlencoded",
                "telnyx-signature-ed25519": base64.b64encode(mark).decode(),
                "telnyx-timestamp": str(stamp)}

    now = int(time.time())
    got = door.post(f"/voice{path}?sig={sig}", content=body,
                    headers=headers(now, body.encode()))
    assert got.status_code == 200, got.text
    assert ET.fromstring(got.text).find("Gather") is not None
    assert len(jim.calls) == 1
    stale = door.post(f"/voice{path}?sig={sig}", content=body,
                      headers=headers(now - 600, body.encode()))
    assert stale.status_code == 403 and stale.content == b""
    tampered = door.post(f"/voice{path}?sig={sig}", content=body + "&x=1",
                         headers=headers(now, body.encode()))
    assert tampered.status_code == 403 and tampered.content == b""
    other = ed25519.Ed25519PrivateKey.generate()
    mark = other.sign(f"{now}|".encode() + body.encode())
    wrong_key = door.post(f"/voice{path}?sig={sig}", content=body, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "telnyx-signature-ed25519": base64.b64encode(mark).decode(),
        "telnyx-timestamp": str(now)})
    assert wrong_key.status_code == 403
    assert len(jim.calls) == 1


def _hs256(secret: str, claims: dict) -> str:
    b64 = voice_b64url
    head = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = b64(json.dumps(claims).encode())
    mark = hmac.new(secret.encode(), f"{head}.{body}".encode(),
                    hashlib.sha256).digest()
    return f"{head}.{body}.{b64(mark)}"


def voice_b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def test_vonage_hs256_jwt_with_a_payload_hash_verifies(voice, door,
                                                       monkeypatch):
    monkeypatch.setenv("VOICE_PROVIDER", "vonage")
    monkeypatch.setenv("VOICE_WEBHOOK_KEY", "signature-secret")
    jim = FakeJim(event=lambda body: ok(LINE_OPEN))
    monkeypatch.setattr(voice, "_jim", jim)
    sig = voice._sig(SECRET, CALL)
    path = f"/vonage/{CALL}/answer"
    body = json.dumps({"from": "15550001111", "to": "15551110000",
                       "uuid": "u-1", "conversation_uuid": "c-1"}).encode()

    def token(secret: str, signed: bytes) -> str:
        return _hs256(secret, {"iat": int(time.time()), "jti": "j-1",
                               "payload_hash":
                               hashlib.sha256(signed).hexdigest()})

    got = door.post(f"/voice{path}?sig={sig}", content=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token('signature-secret', body)}"})
    assert got.status_code == 200, got.text
    ncco = got.json()
    assert ncco[0]["action"] == "talk" and ncco[0]["text"] == OPENING
    assert ncco[1]["action"] == "input" and ncco[1]["type"] == ["dtmf"]
    assert len(jim.calls) == 1
    wrong_hash = door.post(f"/voice{path}?sig={sig}", content=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token('signature-secret', body + b' ')}"})
    assert wrong_hash.status_code == 403 and wrong_hash.content == b""
    wrong_secret = door.post(f"/voice{path}?sig={sig}", content=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token('other', body)}"})
    assert wrong_secret.status_code == 403 and wrong_secret.content == b""
    no_key_alg = _hs256("signature-secret", {"payload_hash": "x"}).replace(
        voice_b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()),
        voice_b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode()))
    none_alg = door.post(f"/voice{path}?sig={sig}", content=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {no_key_alg}"})
    assert none_alg.status_code == 403
    assert len(jim.calls) == 1


def test_a_house_with_no_webhook_key_cannot_be_talked_into_trusting(voice,
                                                                    door,
                                                                    monkeypatch):
    """No off-switch: a Telnyx or Vonage row with nothing to verify with
    refuses every webhook rather than waving them through."""
    monkeypatch.setenv("VOICE_PROVIDER", "vonage")
    monkeypatch.delenv("VOICE_WEBHOOK_KEY", raising=False)
    jim = FakeJim(event=lambda body: ok(LINE_OPEN))
    monkeypatch.setattr(voice, "_jim", jim)
    sig = voice._sig(SECRET, CALL)
    got = door.post(f"/voice/vonage/{CALL}/answer?sig={sig}", content=b"{}",
                    headers={"Content-Type": "application/json"})
    assert got.status_code == 403 and jim.calls == []


# --------------------------------------------------------------------------- #
# 5. the line machine, driven through the Twilio renderer
# --------------------------------------------------------------------------- #

def _say_text(root: ET.Element, within: str | None = None) -> str | None:
    node = root.find(within) if within else root
    say = node.find("Say") if node is not None else None
    return say.text if say is not None else None


def test_a_person_answering_hears_the_opening_and_a_keypad(voice, door,
                                                           monkeypatch):
    jim = FakeJim(event=lambda body: ok(LINE_OPEN, decided="noted"))
    monkeypatch.setattr(voice, "_jim", jim)
    got = twilio_post(door, voice, "answer", {
        "CallSid": "CA0123", "CallStatus": "in-progress",
        "AnsweredBy": "human"})
    root = twiml(got)
    [asked] = jim.calls
    assert asked.method == "POST"
    assert asked.path == f"/reachout/call/{CALL}/event"
    assert asked.body == {"event": "answered", "seconds": 0,
                          "detail": "CallStatus=in-progress;AnsweredBy=human"}
    assert asked.bearer == f"Bearer {SECRET}"
    assert asked.timeout == voice.JIM_TIMEOUT == 5.0
    gather = root.find("Gather")
    assert gather is not None
    assert gather.get("input") == "dtmf" and gather.get("numDigits") == "1"
    assert gather.get("timeout") == "7"
    assert gather.get("actionOnEmptyResult") == "true"
    assert gather.get("method") == "POST"
    assert gather.get("action") == (f"{PUB}/twilio/{CALL}/gather?sig="
                                    f"{voice._sig(SECRET, CALL)}&try=1")
    assert _say_text(root, "Gather") == OPENING
    assert gather.find("Say").get("language") == "en-US"
    assert voice._recall(CALL) is not None


def test_a_machine_answering_is_hung_up_on_before_a_word(voice, door,
                                                         monkeypatch):
    jim = FakeJim(event=lambda body: (200, {"status": "unreached",
                                            "decided": "unreached",
                                            "line": None}))
    monkeypatch.setattr(voice, "_jim", jim)
    got = twilio_post(door, voice, "answer", {
        "CallSid": "CA0123", "CallStatus": "in-progress",
        "AnsweredBy": "machine_start"})
    root = twiml(got)
    assert root.find("Hangup") is not None
    assert root.find("Say") is None and root.find("Gather") is None
    [asked] = jim.calls
    assert asked.body["event"] == "voicemail"
    assert "AnsweredBy=machine_start" in asked.body["detail"]
    assert asked.bearer == f"Bearer {SECRET}"


def test_jim_unreachable_at_the_answer_hangs_up_without_a_word(voice, door,
                                                               monkeypatch):
    """No line yet to draw a trouble phrase from; the status callback still
    decides the leg."""
    jim = FakeJim(event=lambda body: (0, {"detail": "JIM could not be "
                                                    "reached: timed out"}))
    monkeypatch.setattr(voice, "_jim", jim)
    root = twiml(twilio_post(door, voice, "answer", {"AnsweredBy": "human"}))
    assert root.find("Hangup") is not None and root.find("Say") is None


def test_an_empty_first_gather_reprompts_from_memory(voice, door, monkeypatch):
    jim = FakeJim()
    monkeypatch.setattr(voice, "_jim", jim)
    voice._remember(CALL, LINE_OPEN)
    root = twiml(twilio_post(door, voice, "gather", {"Digits": ""},
                             query="try=1"))
    gather = root.find("Gather")
    assert gather.get("action").endswith("&try=2")
    assert gather.get("input") == "dtmf"
    assert _say_text(root, "Gather") == LINE_OPEN["again"]
    assert jim.calls == []


def test_an_empty_second_gather_sends_no_choice_to_jim(voice, door,
                                                       monkeypatch):
    jim = FakeJim(consent=lambda body: (200, {"status": "calling",
                                              "line": LINE_NO_CHOICE}))
    monkeypatch.setattr(voice, "_jim", jim)
    voice._remember(CALL, LINE_OPEN)
    root = twiml(twilio_post(door, voice, "gather", {"Digits": ""},
                             query="try=2"))
    [asked] = jim.calls
    assert asked.path == f"/reachout/call/{CALL}/consent"
    assert asked.body == {"digit": ""}
    assert _say_text(root) == LINE_NO_CHOICE["say"]
    assert root.find("Hangup") is not None
    assert root.find("Gather") is None


def test_a_wrong_key_twice_goes_to_jim_as_pressed(voice, door, monkeypatch):
    jim = FakeJim(consent=lambda body: (200, {"line": LINE_NO_CHOICE}))
    monkeypatch.setattr(voice, "_jim", jim)
    voice._remember(CALL, LINE_OPEN)
    first = twiml(twilio_post(door, voice, "gather", {"Digits": "5"},
                              query="try=1"))
    assert first.find("Gather").get("action").endswith("&try=2")
    assert jim.calls == []
    twiml(twilio_post(door, voice, "gather", {"Digits": "7"}, query="try=2"))
    assert jim.calls[0].body == {"digit": "7"}


def test_pressing_1_consents_and_redirects_into_the_conversation(voice, door,
                                                                 monkeypatch):
    jim = FakeJim(consent=lambda body: (200, {"status": "consented",
                                              "say": LINE_CONSENTED["say"],
                                              "line": LINE_CONSENTED}))
    monkeypatch.setattr(voice, "_jim", jim)
    root = twiml(twilio_post(door, voice, "gather", {"Digits": "1"},
                             query="try=1"))
    [asked] = jim.calls
    assert asked.path == f"/reachout/call/{CALL}/consent"
    assert asked.body == {"digit": "1"}
    assert asked.bearer == f"Bearer {SECRET}"
    assert _say_text(root) == LINE_CONSENTED["say"]
    redirect = root.find("Redirect")
    assert redirect.get("method") == "POST"
    assert redirect.text == (f"{PUB}/twilio/{CALL}/speech?sig="
                             f"{voice._sig(SECRET, CALL)}&first=1&turn=0")
    assert root.find("Hangup") is None


def test_pressing_2_declines_and_hangs_up(voice, door, monkeypatch):
    jim = FakeJim(consent=lambda body: (200, {"status": "calling",
                                              "line": LINE_DECLINED}))
    monkeypatch.setattr(voice, "_jim", jim)
    root = twiml(twilio_post(door, voice, "gather", {"Digits": "2"},
                             query="try=1"))
    assert jim.calls[0].body == {"digit": "2"}
    assert _say_text(root) == LINE_DECLINED["say"]
    assert root.find("Hangup") is not None


def test_the_first_speech_leg_asks_jim_to_speak_first(voice, door,
                                                      monkeypatch):
    jim = FakeJim(say=lambda body: (200, {"status": "talking", "said": SAID,
                                          "line": LINE_TALK}))
    monkeypatch.setattr(voice, "_jim", jim)
    root = twiml(twilio_post(door, voice, "speech", {"CallSid": "CA0123"},
                             query="first=1&turn=0"))
    [asked] = jim.calls
    assert asked.path == f"/reachout/call/{CALL}/say"
    assert asked.body == {"heard": ""}
    assert asked.timeout == voice.SAY_TIMEOUT == 12.0
    assert asked.bearer == f"Bearer {SECRET}"
    assert _say_text(root) == SAID
    gather = root.find("Gather")
    assert gather.get("input") == "speech"
    assert gather.get("speechTimeout") == "auto"
    assert gather.get("timeout") == "6"
    assert gather.get("language") == "en-US"
    assert gather.get("actionOnEmptyResult") == "true"
    assert gather.get("action") == (f"{PUB}/twilio/{CALL}/speech?sig="
                                    f"{voice._sig(SECRET, CALL)}"
                                    f"&silence=0&turn=1")


def test_a_spoken_answer_reaches_jim_as_heard(voice, door, monkeypatch):
    jim = FakeJim(say=lambda body: (200, {"line": LINE_TALK}))
    monkeypatch.setattr(voice, "_jim", jim)
    root = twiml(twilio_post(door, voice, "speech", {
        "SpeechResult": "What happened to her?", "Confidence": "0.91"},
        query="silence=0&turn=1"))
    assert jim.calls[0].body == {"heard": "What happened to her?"}
    assert root.find("Gather").get("action").endswith("&silence=0&turn=2")


def test_a_first_silence_prompts_from_memory_and_a_second_closes(voice, door,
                                                                 monkeypatch):
    jim = FakeJim()
    monkeypatch.setattr(voice, "_jim", jim)
    voice._remember(CALL, LINE_TALK)
    root = twiml(twilio_post(door, voice, "speech", {"SpeechResult": ""},
                             query="silence=0&turn=1"))
    assert _say_text(root) == LINE_TALK["again"]
    assert root.find("Gather").get("action").endswith("&silence=1&turn=1")
    assert jim.calls == []
    root = twiml(twilio_post(door, voice, "speech", {"SpeechResult": ""},
                             query="silence=1&turn=1"))
    assert _say_text(root) == LINE_TALK["close"]
    assert root.find("Hangup") is not None
    assert root.find("Gather") is None
    assert jim.calls == []


def test_jims_closing_line_hangs_up(voice, door, monkeypatch):
    jim = FakeJim(say=lambda body: (200, {"line": LINE_CLOSE}))
    monkeypatch.setattr(voice, "_jim", jim)
    root = twiml(twilio_post(door, voice, "speech", {"SpeechResult": "Thanks"},
                             query="silence=0&turn=11"))
    assert _say_text(root) == LINE_CLOSE["say"]
    assert root.find("Hangup") is not None and root.find("Gather") is None


@pytest.mark.parametrize("answer", [
    (409, {"detail": "this call is not in a conversation"}),
    (500, {"detail": "boom"}),
    (0, {"detail": "JIM could not be reached: timed out"}),
])
def test_jim_refusing_or_silent_speaks_the_trouble_line(voice, door,
                                                        monkeypatch, answer):
    jim = FakeJim(say=lambda body: answer)
    monkeypatch.setattr(voice, "_jim", jim)
    voice._remember(CALL, LINE_TALK)
    root = twiml(twilio_post(door, voice, "speech", {"SpeechResult": "Hello?"},
                             query="silence=0&turn=2"))
    assert _say_text(root) == TROUBLE
    assert root.find("Hangup") is not None
    assert root.find("Gather") is None


def test_trouble_with_nothing_remembered_is_a_bare_hangup(voice, door,
                                                          monkeypatch):
    jim = FakeJim(say=lambda body: (409, {"detail": "not in a conversation"}))
    monkeypatch.setattr(voice, "_jim", jim)
    root = twiml(twilio_post(door, voice, "speech", {"SpeechResult": "Hello?"},
                             query="silence=0&turn=2"))
    assert root.find("Say") is None and root.find("Hangup") is not None


def test_a_status_callback_tells_jim_how_it_ended_and_answers_204(voice, door,
                                                                  monkeypatch):
    jim = FakeJim(event=lambda body: (200, {"status": "reached",
                                            "decided": "reached",
                                            "line": None}))
    monkeypatch.setattr(voice, "_jim", jim)
    voice._remember(CALL, LINE_TALK)
    got = twilio_post(door, voice, "status", {
        "CallSid": "CA0123", "CallStatus": "completed", "CallDuration": "42",
        "AnsweredBy": "human", "SipResponseCode": "200"})
    assert got.status_code == 204 and got.content == b""
    [asked] = jim.calls
    assert asked.path == f"/reachout/call/{CALL}/event"
    assert asked.body == {"event": "completed", "seconds": 42,
                          "detail": "CallStatus=completed;AnsweredBy=human;"
                                    "SipResponseCode=200"}
    assert asked.bearer == f"Bearer {SECRET}"
    assert voice._recall(CALL) is None


@pytest.mark.parametrize("word", ["busy", "no-answer", "failed", "canceled"])
def test_every_terminal_status_reaches_jim_in_its_own_word(voice, door,
                                                           monkeypatch, word):
    jim = FakeJim(event=lambda body: (200, {"decided": "unreached"}))
    monkeypatch.setattr(voice, "_jim", jim)
    got = twilio_post(door, voice, "status", {"CallStatus": word,
                                              "SipResponseCode": "486"})
    assert got.status_code == 204
    assert jim.calls[0].body == {"event": word, "seconds": 0,
                                 "detail": f"CallStatus={word};"
                                           "SipResponseCode=486"}


def test_a_status_callback_is_204_whatever_jim_said(voice, door, monkeypatch):
    """A 5xx would only make the house retry into an idempotent door."""
    for answer in ((500, {}), (403, {"detail": "invalid voice adapter "
                                               "token"}), (0, {})):
        jim = FakeJim(event=lambda body, a=answer: a)
        monkeypatch.setattr(voice, "_jim", jim)
        got = twilio_post(door, voice, "status", {"CallStatus": "completed"})
        assert got.status_code == 204
        assert len(jim.calls) == 1


def test_a_non_terminal_status_posts_nothing(voice, door, monkeypatch):
    jim = FakeJim()
    monkeypatch.setattr(voice, "_jim", jim)
    for noise in ("initiated", "ringing", "in-progress", "queued"):
        got = twilio_post(door, voice, "status", {"CallStatus": noise})
        assert got.status_code == 204
    assert jim.calls == []


def test_jim_refusing_the_secret_still_leaves_the_house_valid_markup(
        voice, door, monkeypatch):
    """JIM answering 401/403 at any door is logged and the house still gets
    markup it can play — a trouble line or a hangup, never a 500."""
    refused = (403, {"detail": "invalid voice adapter token"})
    jim = FakeJim(event=lambda b: refused, consent=lambda b: refused,
                  say=lambda b: refused)
    monkeypatch.setattr(voice, "_jim", jim)
    root = twiml(twilio_post(door, voice, "answer", {"AnsweredBy": "human"}))
    assert root.find("Hangup") is not None and root.find("Say") is None
    voice._remember(CALL, LINE_OPEN)
    root = twiml(twilio_post(door, voice, "gather", {"Digits": "1"},
                             query="try=1"))
    assert _say_text(root) == TROUBLE and root.find("Hangup") is not None
    root = twiml(twilio_post(door, voice, "speech", {"SpeechResult": "Hi"},
                             query="silence=0&turn=1"))
    assert _say_text(root) == TROUBLE and root.find("Hangup") is not None
    assert all(c.bearer == f"Bearer {SECRET}" for c in jim.calls)


def test_restart_amnesia_asks_jim_instead_of_speaking_from_memory(voice, door,
                                                                  monkeypatch):
    """Identity and counters ride the URL and every text comes from JIM, so
    a voice container restarted between answer and gather costs one
    re-prompt and never the leg."""
    jim = FakeJim(event=lambda b: ok(LINE_OPEN),
                  consent=lambda b: (200, {"line": LINE_NO_CHOICE}),
                  say=lambda b: (200, {"line": LINE_TALK}))
    monkeypatch.setattr(voice, "_jim", jim)
    twiml(twilio_post(door, voice, "answer", {"AnsweredBy": "human"}))
    voice._LINES.clear()
    root = twiml(twilio_post(door, voice, "gather", {"Digits": ""},
                             query="try=1"))
    assert jim.calls[-1].path.endswith("/consent")
    assert jim.calls[-1].body == {"digit": ""}
    assert _say_text(root) == LINE_NO_CHOICE["say"]
    voice._LINES.clear()
    root = twiml(twilio_post(door, voice, "speech", {"SpeechResult": ""},
                             query="silence=0&turn=1"))
    assert jim.calls[-1].path.endswith("/say")
    assert jim.calls[-1].body == {"heard": ""}
    assert root.find("Gather").get("input") == "speech"


def test_the_whole_call_carries_the_bearer_on_every_request(voice, door,
                                                            monkeypatch):
    jim = FakeJim(event=lambda b: ok(LINE_OPEN) if b["event"] == "answered"
                  else (200, {"decided": "reached", "line": None}),
                  consent=lambda b: (200, {"line": LINE_CONSENTED}),
                  say=lambda b: (200, {"line": LINE_TALK}))
    monkeypatch.setattr(voice, "_jim", jim)
    twiml(twilio_post(door, voice, "answer", {"AnsweredBy": "human"}))
    twiml(twilio_post(door, voice, "gather", {"Digits": "1"}, query="try=1"))
    twiml(twilio_post(door, voice, "speech", {}, query="first=1&turn=0"))
    twiml(twilio_post(door, voice, "speech", {"SpeechResult": "Is she ok?"},
                      query="silence=0&turn=1"))
    assert twilio_post(door, voice, "status", {
        "CallStatus": "completed", "CallDuration": "61"}).status_code == 204
    assert [c.path.rsplit("/", 1)[-1] for c in jim.calls] == [
        "event", "consent", "say", "say", "event"]
    assert all(c.bearer == f"Bearer {SECRET}" for c in jim.calls)
    assert all(c.path.startswith(f"/reachout/call/{CALL}/")
               for c in jim.calls)


def test_the_jim_helper_sends_the_bearer_and_never_takes_the_url_from_a_request(
        voice, monkeypatch):
    seen = {}

    def fake(method, url, *, headers, data, timeout):
        seen.update(method=method, url=url, headers=headers, data=data,
                    timeout=timeout)
        return 404, {"detail": "no such call"}
    monkeypatch.setattr(voice, "_jim", fake)
    status, body = voice._ask("POST", f"/reachout/call/{CALL}/say",
                              {"heard": "x"}, timeout=voice.SAY_TIMEOUT)
    assert status == 404 and body == {"detail": "no such call"}
    assert seen["url"] == f"http://jim.test:8200/reachout/call/{CALL}/say"
    assert seen["headers"]["Authorization"] == f"Bearer {SECRET}"
    assert seen["timeout"] == 12.0
    assert json.loads(seen["data"]) == {"heard": "x"}


# --------------------------------------------------------------------------- #
# 6. the other four houses
# --------------------------------------------------------------------------- #

def test_signalwire_create_call_speaks_from_its_own_space(voice, door,
                                                          monkeypatch):
    house = FakeHouse((201, {"sid": "sw-1", "status": "queued"}))
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setenv("VOICE_PROVIDER", "signalwire")
    monkeypatch.setenv("VOICE_HOUSE_REF", "myspace")
    got = door.post("/calls", json=order(provider="signalwire"),
                    headers=bearer())
    assert got.status_code == 201, got.text
    assert got.json()["provider_call_id"] == "sw-1"
    assert got.json()["provider"] == "signalwire"
    [sent] = house.calls
    assert sent.url == (f"https://myspace.signalwire.com/api/laml/2010-04-01/"
                        f"Accounts/{ACCOUNT}/Calls.json")
    assert sent.headers["Authorization"].startswith("Basic ")
    assert sent.form["Url"].startswith(f"{PUB}/signalwire/{CALL}/answer?sig=")
    assert sent.form["StatusCallbackEvent"] == "completed"


def test_signalwire_without_a_space_names_house_ref(voice, door, monkeypatch):
    monkeypatch.setattr(voice, "_house_http", FakeHouse())
    monkeypatch.setenv("VOICE_PROVIDER", "signalwire")
    got = door.post("/calls", json=order(provider="signalwire"),
                    headers=bearer())
    assert got.status_code == 503 and "JIM_VOICE_HOUSE_REF" in got.text


def test_telnyx_create_call_posts_texml_json_under_a_bearer(voice, door,
                                                            monkeypatch):
    house = FakeHouse((200, {"data": {"sid": "v3:abc", "status": "queued"}}))
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setenv("VOICE_PROVIDER", "telnyx")
    monkeypatch.setenv("VOICE_HOUSE_REF", "app-1")
    monkeypatch.setenv("VOICE_WEBHOOK_KEY", "cHVibGlj")
    monkeypatch.delenv("VOICE_ACCOUNT")
    got = door.post("/calls", json=order(provider="telnyx"), headers=bearer())
    assert got.status_code == 201, got.text
    assert got.json()["provider_call_id"] == "v3:abc"
    [sent] = house.calls
    assert sent.url == "https://api.telnyx.com/v2/texml/calls/app-1"
    assert sent.headers["Authorization"] == f"Bearer {TOKEN}"
    assert sent.headers["Content-Type"] == "application/json"
    body = sent.json
    assert body["To"] == TO and body["From"] == FROM
    assert body["Url"] == (f"{PUB}/telnyx/{CALL}/answer?sig="
                           f"{voice._sig(SECRET, CALL)}")
    assert body["StatusCallback"].startswith(f"{PUB}/telnyx/{CALL}/status?sig=")
    assert body["StatusCallbackEvent"] == "completed"
    assert body["Timeout"] == 25 and body["TimeLimit"] == 600
    assert body["MachineDetection"] == "Enable"


def test_telnyx_without_a_public_key_is_unkeyed(voice, door, monkeypatch):
    monkeypatch.setattr(voice, "_house_http", FakeHouse())
    monkeypatch.setenv("VOICE_PROVIDER", "telnyx")
    monkeypatch.setenv("VOICE_HOUSE_REF", "app-1")
    got = door.post("/calls", json=order(provider="telnyx"), headers=bearer())
    assert got.status_code == 503 and "JIM_VOICE_WEBHOOK_KEY" in got.text


def test_plivo_create_call_posts_json_under_basic_auth(voice, door,
                                                       monkeypatch):
    house = FakeHouse((201, {"request_uuid": "req-1", "message": "call fired"}))
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setenv("VOICE_PROVIDER", "plivo")
    got = door.post("/calls", json=order(provider="plivo"), headers=bearer())
    assert got.status_code == 201, got.text
    assert got.json()["provider_call_id"] == "req-1"
    [sent] = house.calls
    assert sent.url == f"https://api.plivo.com/v1/Account/{ACCOUNT}/Call/"
    assert sent.headers["Authorization"] == "Basic " + base64.b64encode(
        f"{ACCOUNT}:{TOKEN}".encode()).decode()
    body = sent.json
    assert body["to"] == "15551110000" and body["from"] == "15550001111"
    assert body["answer_url"] == (f"{PUB}/plivo/{CALL}/answer?sig="
                                  f"{voice._sig(SECRET, CALL)}")
    assert body["answer_method"] == "POST"
    assert body["hangup_url"].startswith(f"{PUB}/plivo/{CALL}/status?sig=")
    assert body["ring_timeout"] == 25 and body["time_limit"] == 600
    assert body["machine_detection"] == "hangup"


def _rsa_pem() -> tuple[str, rsa.RSAPublicKey]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM,
                            serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()
    return pem, key.public_key()


def test_vonage_create_call_mints_an_rs256_jwt(voice, door, monkeypatch):
    pem, public = _rsa_pem()
    house = FakeHouse((201, {"uuid": "u-1", "status": "started",
                             "direction": "outbound"}))
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setenv("VOICE_PROVIDER", "vonage")
    monkeypatch.setenv("VOICE_TOKEN", pem)
    monkeypatch.setenv("VOICE_WEBHOOK_KEY", "signature-secret")
    got = door.post("/calls", json=order(provider="vonage"), headers=bearer())
    assert got.status_code == 201, got.text
    assert got.json()["provider_call_id"] == "u-1"
    [sent] = house.calls
    assert sent.url == "https://api.nexmo.com/v1/calls"
    auth = sent.headers["Authorization"]
    assert auth.startswith("Bearer ")
    head, claims, mark = auth[7:].split(".")
    assert json.loads(voice.houses.b64url_decode(head))["alg"] == "RS256"
    public.verify(voice.houses.b64url_decode(mark),
                  f"{head}.{claims}".encode(), padding.PKCS1v15(),
                  hashes.SHA256())
    said = json.loads(voice.houses.b64url_decode(claims))
    assert said["application_id"] == ACCOUNT
    assert said["exp"] > said["iat"] and said["jti"]
    body = sent.json
    assert body["to"] == [{"type": "phone", "number": "15551110000"}]
    assert body["from"] == {"type": "phone", "number": "15550001111"}
    assert body["answer_url"] == [f"{PUB}/vonage/{CALL}/answer?sig="
                                  f"{voice._sig(SECRET, CALL)}"]
    assert body["answer_method"] == "POST"
    assert body["event_url"][0].startswith(f"{PUB}/vonage/{CALL}/status?sig=")
    assert body["event_method"] == "POST"
    assert body["ringing_timer"] == 25 and body["length_timer"] == 600
    assert body["machine_detection"] == "hangup"
    assert pem not in got.text


def test_a_vonage_token_that_is_not_a_pem_names_the_variable(voice, door,
                                                             monkeypatch):
    house = FakeHouse()
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setenv("VOICE_PROVIDER", "vonage")
    monkeypatch.setenv("VOICE_WEBHOOK_KEY", "signature-secret")
    got = door.post("/calls", json=order(provider="vonage"), headers=bearer())
    assert got.status_code == 503
    assert "JIM_VOICE_TOKEN" in got.json()["detail"]
    assert house.calls == []


def test_the_token_can_be_read_from_a_file(voice, monkeypatch, tmp_path):
    monkeypatch.delenv("VOICE_TOKEN")
    path = tmp_path / "private.key"
    path.write_text("-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----\n")
    monkeypatch.setenv("VOICE_TOKEN_FILE", str(path))
    assert voice._config().token.startswith("-----BEGIN PRIVATE KEY-----")
    assert voice.health()["keyed"] is True


def _rows(voice, monkeypatch):
    pem, _ = _rsa_pem()
    monkeypatch.setenv("VOICE_HOUSE_REF", "space")
    monkeypatch.setenv("VOICE_WEBHOOK_KEY", "k")
    for name, cls in voice.HOUSES.items():
        monkeypatch.setenv("VOICE_TOKEN", pem if name == "vonage" else TOKEN)
        yield name, cls(voice._config(), lambda *a, **k: (200, "{}"))


def _prompt(name: str, node) -> str | None:
    """What the person hears, wherever this house's markup puts it."""
    if isinstance(node, list):
        talk = [n for n in node if n.get("action") == "talk"]
        return talk[0]["text"] if talk else None
    for tag in ("Say", "Speak"):
        found = node.find(f".//{tag}")
        if found is not None:
            return found.text
    return None


def _next(name: str, node, then: str) -> str:
    """Where this house will post next, for a `then` word."""
    if isinstance(node, list):
        last = node[-1]
        return last["eventUrl"][0]
    if then in ("gather_digit", "gather_speech"):
        tag = "GetInput" if name == "plivo" else "Gather"
        return node.find(tag).get("action")
    return node.find("Redirect").text


@pytest.mark.parametrize("then,counters,line", [
    ("gather_digit", {"try": 1}, LINE_OPEN),
    ("speak_first", {"first": 1, "turn": 0}, LINE_CONSENTED),
    ("gather_speech", {"silence": 0, "turn": 3}, LINE_TALK),
    ("hangup", {}, LINE_DECLINED),
])
def test_every_house_renders_the_same_line_its_own_way(voice, monkeypatch,
                                                       then, counters, line):
    """The same line fixtures rendered five ways and parsed back: the
    person hears the same words, and the house posts to the same door
    with the same counters, whatever the dialect."""
    urls = voice._urls(voice._config(), "x", CALL)
    for name, row in _rows(voice, monkeypatch):
        got = row.render({**line, "then": then}, urls, counters)
        if name == "vonage":
            assert "json" in got.media_type
            node = json.loads(got.body)
            assert isinstance(node, list)
        else:
            assert "xml" in got.media_type
            node = ET.fromstring(got.body)
            assert node.tag == "Response"
        assert _prompt(name, node) == line["say"], name
        if then == "hangup":
            if name == "vonage":
                assert [n["action"] for n in node] == ["talk"]
            else:
                assert node.find("Hangup") is not None, name
                assert node.find("Gather") is None and \
                    node.find("GetInput") is None
            continue
        url = _next(name, node, then)
        assert url.startswith(f"{PUB}/x/{CALL}/"), (name, url)
        assert f"sig={voice._sig(SECRET, CALL)}" in url
        if then == "gather_digit":
            assert "/gather?" in url and url.endswith("&try=1")
            if name == "vonage":
                assert node[-1]["type"] == ["dtmf"]
                assert node[-1]["dtmf"] == {"maxDigits": 1, "timeOut": 7}
            elif name == "plivo":
                assert node.find("GetInput").get("inputType") == "dtmf"
                assert node.find("GetInput").get("numDigits") == "1"
            else:
                assert node.find("Gather").get("input") == "dtmf"
                assert node.find("Gather").get("actionOnEmptyResult") == "true"
        elif then == "speak_first":
            assert "/speech?" in url and url.endswith("&first=1&turn=0")
            if name == "vonage":
                assert node[-1]["action"] == "notify"
        elif then == "gather_speech":
            assert "/speech?" in url and url.endswith("&silence=0&turn=3")
            if name == "vonage":
                assert node[-1]["type"] == ["speech"]
                assert node[-1]["speech"]["language"] == "en-US"
            elif name == "plivo":
                assert node.find("GetInput").get("inputType") == "speech"
            else:
                assert node.find("Gather").get("input") == "speech"


def test_a_line_with_markup_in_it_stays_words(voice, monkeypatch):
    urls = voice._urls(voice._config(), "x", CALL)
    for name, row in _rows(voice, monkeypatch):
        if name == "vonage":
            continue
        got = row.render({"say": "Ada <fell> & \"hurt\"", "then": "hangup",
                          "language": "en"}, urls, {})
        assert _prompt(name, ET.fromstring(got.body)) == 'Ada <fell> & "hurt"'


@pytest.mark.parametrize("house,body,expected,seconds", [
    ("twilio", {"CallStatus": "completed", "CallDuration": "42"},
     "completed", 42),
    ("twilio", {"CallStatus": "busy"}, "busy", 0),
    ("twilio", {"CallStatus": "no-answer"}, "no-answer", 0),
    ("twilio", {"CallStatus": "failed"}, "failed", 0),
    ("twilio", {"CallStatus": "canceled"}, "canceled", 0),
    ("twilio", {"CallStatus": "ringing"}, None, 0),
    ("signalwire", {"CallStatus": "no-answer"}, "no-answer", 0),
    ("telnyx", {"CallStatus": "completed", "CallDuration": "7"},
     "completed", 7),
    ("plivo", {"CallStatus": "completed", "Duration": "12"}, "completed", 12),
    ("plivo", {"CallStatus": "timeout"}, "no-answer", 0),
    ("plivo", {"CallStatus": "no-answer"}, "no-answer", 0),
    ("plivo", {"CallStatus": "cancel"}, "canceled", 0),
    ("plivo", {"CallStatus": "busy"}, "busy", 0),
    ("plivo", {"CallStatus": "failed"}, "failed", 0),
    ("plivo", {"CallStatus": "completed", "Machine": "true"}, "voicemail", 0),
    ("plivo", {"CallStatus": "in-progress"}, None, 0),
    ("vonage", {"status": "completed", "duration": "42"}, "completed", 42),
    ("vonage", {"status": "unanswered"}, "no-answer", 0),
    ("vonage", {"status": "timeout"}, "no-answer", 0),
    ("vonage", {"status": "rejected"}, "busy", 0),
    ("vonage", {"status": "busy"}, "busy", 0),
    ("vonage", {"status": "failed"}, "failed", 0),
    ("vonage", {"status": "cancelled"}, "canceled", 0),
    ("vonage", {"status": "machine"}, "voicemail", 0),
    ("vonage", {"status": "answered"}, None, 0),
    ("vonage", {"status": "ringing"}, None, 0),
])
def test_each_house_maps_its_terminal_words_onto_jims_six(voice, monkeypatch,
                                                          house, body,
                                                          expected, seconds):
    rows = dict(_rows(voice, monkeypatch))
    raw = (json.dumps(body).encode() if house == "vonage"
           else urllib.parse.urlencode(body).encode())
    ev = rows[house].parse({}, raw)
    assert ev.status == expected
    assert ev.seconds == seconds
    assert ev.status is None or ev.status in voice.houses.TERMINAL


def test_each_house_reads_the_keypad_and_the_speech_from_its_own_field(
        voice, monkeypatch):
    rows = dict(_rows(voice, monkeypatch))
    form = urllib.parse.urlencode
    assert rows["twilio"].parse({}, form({"Digits": "1"}).encode()).digit == "1"
    assert rows["twilio"].parse({}, form({"Digits": ""}).encode()).digit == ""
    assert rows["twilio"].parse({}, form({"SpeechResult": "hi"}).encode()) \
        .speech == "hi"
    assert rows["telnyx"].parse({}, form({"Digits": "2"}).encode()).digit == "2"
    assert rows["plivo"].parse({}, form({"Digits": "1"}).encode()).digit == "1"
    assert rows["plivo"].parse({}, form({"Speech": "hi"}).encode()).speech \
        == "hi"
    assert rows["vonage"].parse({}, json.dumps(
        {"dtmf": {"digits": "1", "timed_out": False}}).encode()).digit == "1"
    assert rows["vonage"].parse({}, json.dumps(
        {"dtmf": {"digits": "", "timed_out": True}}).encode()).digit == ""
    assert rows["vonage"].parse({}, json.dumps(
        {"speech": {"results": [{"text": "hi", "confidence": "0.9"}]}})
        .encode()).speech == "hi"
    assert rows["vonage"].parse({}, json.dumps(
        {"speech": {"timeout_reason": "end_on_silence_timeout"}})
        .encode()).speech == ""
    machine = rows["twilio"].parse({}, form({"AnsweredBy": "machine_end_beep"})
                                   .encode())
    assert machine.answered_by == "machine_end_beep"
    assert rows["plivo"].parse({}, form({"Machine": "true"}).encode()) \
        .answered_by == "machine"


# --------------------------------------------------------------------------- #
# 7. standing: the proof, not the promise
# --------------------------------------------------------------------------- #

def _ready_house() -> FakeHouse:
    house = FakeHouse()
    house.script = {"/Accounts/": (200, {"sid": ACCOUNT, "status": "active"}),
                    "/ping": (200, {"ok": True, "voice": True})}
    return house


def test_standing_with_a_house_that_answers_is_ready(voice, door, monkeypatch):
    house = _ready_house()
    monkeypatch.setattr(voice, "_house_http", house)
    jim = FakeJim()
    monkeypatch.setattr(voice, "_jim", jim)
    got = door.get("/standing", headers=bearer())
    assert got.status_code == 200, got.text
    body = got.json()
    assert body["word"] == "ready"
    assert body["provider"] == "twilio"
    assert body["authenticated"] is True
    assert body["from_number"] is True
    assert body["webhooks"] is True
    assert body["jim_secret_accepted"] is True
    assert body["fix"] is None
    assert "...a1b2" in body["detail"] and " at 20" in body["detail"]
    assert body["checked_at"].endswith("Z")
    for secret in (ACCOUNT, TOKEN, SECRET):
        assert secret not in repr(body)
    [probe] = jim.calls
    assert probe.path == "/reachout/call/rcl_probe/event"
    assert probe.method == "POST"
    assert probe.bearer == f"Bearer {SECRET}"
    assert probe.timeout == 3.0
    assert probe.body["event"] in voice.houses.TERMINAL
    [ping] = house.sent("/ping")
    assert ping.url == f"{PUB}/ping" and ping.timeout == 3.0
    [auth] = house.sent("/Accounts/")
    assert auth.timeout == 3.0 and auth.headers["Authorization"]


def test_standing_needs_the_bearer(voice, door, monkeypatch):
    monkeypatch.setattr(voice, "_house_http", _ready_house())
    monkeypatch.setattr(voice, "_jim", FakeJim())
    assert door.get("/standing").status_code == 401
    assert door.get("/standing", headers=bearer("nope")).status_code == 403


def test_a_401_from_the_house_is_refused(voice, door, monkeypatch):
    house = _ready_house()
    house.script["/Accounts/"] = (401, {"message": "Authenticate"})
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setattr(voice, "_jim", FakeJim())
    body = door.get("/standing", headers=bearer()).json()
    assert body["word"] == "refused"
    assert body["authenticated"] is False
    assert body["fix"] == "the house answered 401 — the auth token is wrong"
    assert body["webhooks"] is None


def test_an_unreachable_house_is_house_unreachable(voice, door, monkeypatch):
    house = _ready_house()

    def down():
        raise voice.houses.Unreachable("[Errno 111] Connection refused")
    house.script["/Accounts/"] = down
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setattr(voice, "_jim", FakeJim())
    body = door.get("/standing", headers=bearer()).json()
    assert body["word"] == "house_unreachable"
    assert body["fix"] == ("the house could not be reached: [Errno 111] "
                           "Connection refused")


def test_a_public_ping_that_fails_is_webhooks_unreachable(voice, door,
                                                          monkeypatch):
    for failing in ((502, ""), (200, {"ok": True}),
                    lambda: (_ for _ in ()).throw(
                        voice.houses.Unreachable("Name or service not known"))):
        voice._PROBES.clear()
        house = _ready_house()
        house.script["/ping"] = failing
        monkeypatch.setattr(voice, "_house_http", house)
        monkeypatch.setattr(voice, "_jim", FakeJim())
        body = door.get("/standing", headers=bearer()).json()
        assert body["word"] == "webhooks_unreachable"
        assert body["authenticated"] is True
        assert body["webhooks"] is False
        assert "Caddy /voice route" in body["fix"]
        assert "JIM_VOICE_PUBLIC_URL" in body["fix"]


@pytest.mark.parametrize("answer,accepted", [
    ((404, {"detail": "no such call"}), True),
    ((401, {"detail": "voice adapter token required"}), False),
    ((403, {"detail": "invalid voice adapter token"}), False),
    ((503, {"detail": "no JIM_VOICE_SECRET configured"}), False),
    ((0, {"detail": "JIM could not be reached: refused"}), None),
])
def test_the_jim_probe_says_whether_the_secrets_match(voice, door,
                                                      monkeypatch, answer,
                                                      accepted):
    monkeypatch.setattr(voice, "_house_http", _ready_house())
    monkeypatch.setattr(voice, "_jim", FakeJim(event=lambda b: answer))
    body = door.get("/standing", headers=bearer()).json()
    assert body["jim_secret_accepted"] is accepted
    assert body["word"] == "ready"


def test_unkeyed_standing_never_touches_the_house(voice, door, monkeypatch):
    house = _ready_house()
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setattr(voice, "_jim", FakeJim())
    monkeypatch.delenv("VOICE_TOKEN")
    body = door.get("/standing", headers=bearer()).json()
    assert body["word"] == "unkeyed"
    assert body["authenticated"] is None
    assert body["fix"] == ("set VOICE_TOKEN on the voice container "
                           "(JIM_VOICE_TOKEN in .env)")
    assert house.calls == []


@pytest.mark.parametrize("variable,value,fix", [
    ("VOICE_FROM", None, "set JIM_VOICE_FROM"),
    ("VOICE_PUBLIC_URL", None,
     "set JIM_VOICE_PUBLIC_URL to https://<jim host>/voice"),
    ("VOICE_PUBLIC_URL", "https://x.test/",
     "set JIM_VOICE_PUBLIC_URL to https://<jim host>/voice"),
])
def test_a_missing_address_is_unaddressed(voice, door, monkeypatch, variable,
                                          value, fix):
    house = _ready_house()
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setattr(voice, "_jim", FakeJim())
    if value is None:
        monkeypatch.delenv(variable)
    else:
        monkeypatch.setenv(variable, value)
    body = door.get("/standing", headers=bearer()).json()
    assert body["word"] == "unaddressed"
    assert body["fix"] == fix
    assert body["from_number"] is (variable != "VOICE_FROM")
    assert house.calls == []


def test_a_provider_nobody_knows_is_mismatched(voice, door, monkeypatch):
    house = _ready_house()
    monkeypatch.setattr(voice, "_house_http", house)
    monkeypatch.setattr(voice, "_jim", FakeJim())
    monkeypatch.setenv("VOICE_PROVIDER", "bolex")
    body = door.get("/standing", headers=bearer()).json()
    assert body["word"] == "mismatched"
    assert "JIM_TELEPHONY_PROVIDER" in body["fix"]
    assert house.calls == []
    asked = door.get("/standing?provider=signalwire", headers=bearer()).json()
    assert asked["word"] == "mismatched"


def test_two_reads_within_a_minute_make_one_house_call(voice, door,
                                                       monkeypatch):
    house = _ready_house()
    monkeypatch.setattr(voice, "_house_http", house)
    jim = FakeJim()
    monkeypatch.setattr(voice, "_jim", jim)
    first = door.get("/standing", headers=bearer()).json()
    second = door.get("/standing", headers=bearer()).json()
    assert first["word"] == second["word"] == "ready"
    assert len(house.sent("/Accounts/")) == 1
    assert len(house.sent("/ping")) == 1
    assert len(jim.calls) == 1
    forced = door.get("/standing?force=1", headers=bearer()).json()
    assert forced["word"] == "ready"
    assert len(house.sent("/Accounts/")) == 2
    assert len(jim.calls) == 2


def test_standing_never_looks_like_a_transport_fault(voice, door,
                                                     monkeypatch):
    """Every word is a 200; only a bad bearer refuses."""
    def explode(*a, **k):
        raise RuntimeError("the house's answer was not what anybody expected")
    monkeypatch.setattr(voice, "_house_http", explode)
    monkeypatch.setattr(voice, "_jim", FakeJim())
    monkeypatch.delenv("VOICE_TOKEN")
    assert door.get("/standing", headers=bearer()).status_code == 200


def test_the_public_ping_is_open_and_says_voice(door):
    assert door.get("/voice/ping").json() == {"ok": True, "voice": True}
    # The JIM-facing doors are not under /voice — nothing there to publish.
    assert door.post("/voice/calls").status_code == 404
    assert door.get("/voice/standing").status_code == 404
