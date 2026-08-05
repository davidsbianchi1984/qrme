"""The keys, the till and the lifeline, on the phones.

Three more blocks off the per-shell doorless record — the account
(signup, sign-in, the emailed code, the reset, the OAuth doors), the
money (the price list, subscriptions, orders, proceeds and campaigns)
and the app's own status and help. What they share is that every one is
the frame around the product rather than the product: the key that gets
you in, the till that takes your money, and the line you pull when
neither works. Until this cut a phone could hold a profile in its hand
and still have to borrow a desktop to make an account, read a price, or
ask what a light means.

The rules these screens render rather than invent:

* **The address is proven before sign-in works.** Signup emails a code;
  the code mints the first session; an unverified address cannot sign
  in at all.
* **No button is an address oracle.** Resend and reset-request answer
  the same whether or not the address has an account.
* **A reset kills every old session.** Whoever prompted the reset, only
  the person holding the inbox stays signed in.
* **The price list is public** and generated from the same table the
  gate reads, so the page and the refusal cannot disagree.
* **Nothing bills on a timer.** Renewing charges a period explicitly
  and names the beneficiary every time.
* **A donor gives to the names on the proceeds list, not the
  platform** — and a campaign cannot open until those names exist.
* **Help writes nothing and is public on purpose** — every screen here
  can be somebody's first.
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import clientpaths  # noqa: E402

from qrme import mailer
from tests.test_capabilities import auth_header, make_profile

REPO = Path(__file__).resolve().parent.parent


def _capture_mail(monkeypatch):
    sent: list[dict] = []

    def fake_deliver(to, subject, body):
        sent.append({"to": to, "subject": subject, "body": body})
        return "smtp"

    monkeypatch.setattr(mailer, "deliver", fake_deliver)
    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    return sent


def _code_from(message: dict) -> str:
    m = re.search(r"code (?:is|in the app): (\d{6})", message["body"])
    assert m, message["body"]
    return m.group(1)


# -- the keys ---------------------------------------------------------------

def test_the_address_is_proven_before_sign_in_works(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    r = client.post("/signup", json={"email": "kay@example.test",
                                     "password": "hunter2-hunter2",
                                     "display_name": "Kay"})
    assert r.status_code == 201, r.text
    # The phone's screen shows how the code travelled, never the code.
    assert r.json()["code_delivery"] == "smtp"
    assert "code" not in r.json() or not str(
        r.json().get("code", "")).isdigit()
    # Unverified: the door does not open yet.
    assert client.post("/signin", json={
        "email": "kay@example.test",
        "password": "hunter2-hunter2"}).status_code == 403
    # The emailed code mints the first session.
    r = client.post("/verify-email", json={
        "email": "kay@example.test", "code": _code_from(sent[0])})
    assert r.status_code == 200, r.text
    assert r.json()["account_token"]
    # And now the password works.
    r = client.post("/signin", json={"email": "kay@example.test",
                                     "password": "hunter2-hunter2"})
    assert r.status_code == 200, r.text


def test_no_button_is_an_address_oracle(client, monkeypatch):
    _capture_mail(monkeypatch)
    # Resend and reset-request answer 200 for an address nobody holds —
    # the split is an address oracle, and these buttons sit on a public
    # screen.
    assert client.post("/verify-email/resend", json={
        "email": "nobody@example.test"}).status_code == 200
    assert client.post("/password/reset/request", json={
        "email": "nobody@example.test"}).status_code == 200
    # Unknown address and wrong password read identically.
    unknown = client.post("/signin", json={
        "email": "nobody@example.test", "password": "hunter2-hunter2"})
    assert unknown.status_code == 403


def test_a_reset_kills_every_old_session(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    client.post("/signup", json={"email": "ray@example.test",
                                 "password": "hunter2-hunter2"})
    old = client.post("/verify-email", json={
        "email": "ray@example.test",
        "code": _code_from(sent[0])}).json()["account_token"]
    # The old session works…
    assert client.get("/subscriptions", headers={
        "authorization": f"Bearer {old}"}).status_code == 200
    # …until the emailed reset code trades for a new password.
    client.post("/password/reset/request", json={
        "email": "ray@example.test"})
    r = client.post("/password/reset", json={
        "email": "ray@example.test", "code": _code_from(sent[-1]),
        "new_password": "hunter3-hunter3"})
    assert r.status_code == 200, r.text
    assert client.post("/signin", json={
        "email": "ray@example.test",
        "password": "hunter2-hunter2"}).status_code == 403
    assert client.post("/signin", json={
        "email": "ray@example.test",
        "password": "hunter3-hunter3"}).status_code == 200
    # Whoever held the old session is signed out with it.
    assert client.get("/subscriptions", headers={
        "authorization": f"Bearer {old}"}).status_code == 401


def test_the_oauth_doors_tell_the_truth(client):
    doors = client.get("/auth/oauth/providers",
                       headers={"authorization": ""}).json()["providers"]
    assert doors and all("configured" in d for d in doors)
    # An unconfigured or unknown door refuses rather than pretending.
    assert client.post("/auth/oauth/nobody/start",
                       json={}).status_code >= 400
    # A bogus claim is spent air.
    assert client.get("/auth/oauth/claim?state=not-a-state"
                      ).status_code == 403


# -- the till ---------------------------------------------------------------

def test_the_price_list_is_public_and_the_renewal_is_explicit(client):
    cat = client.get("/plans", headers={"authorization": ""}).json()
    names = [p["plan"] for p in cat["plans"]]
    assert "visitor" in names
    assert cat["billing"]
    # A subscription list needs a session; a bare renewal is refused by
    # name — nothing here bills on a timer.
    p = make_profile(client)
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    r = client.post(f"/profiles/{p['id']}/subscribe", json={},
                    headers=auth_header(q))
    assert r.status_code == 201, r.text
    subs = client.get("/subscriptions", headers=auth_header(q)).json()
    assert any(s["subject_id"] == p["id"] for s in subs["subscriptions"])
    r = client.post(f"/subscriptions/{subs['subscriptions'][0]['id']}/renew",
                    json={}, headers=auth_header(q))
    assert r.status_code == 422
    assert "beneficiary" in r.json()["detail"]
    # Orders: yours to read, nobody else's to guess at.
    orders = client.get("/orders", headers=auth_header(q)).json()
    assert orders["orders"] == []
    assert client.get("/orders", headers={"authorization": ""}
                      ).status_code == 401


def test_a_donor_gives_to_names_not_the_platform(client):
    p = make_profile(client)
    q = make_profile(client, owner_id="owner-2", display_name="Quinn")
    # A campaign cannot open until the money has somewhere to go.
    r = client.post(f"/profiles/{p['id']}/campaigns",
                    json={"title": "roof fund", "goal": 500},
                    headers=auth_header(p))
    assert r.status_code == 422
    assert "where the money goes" in r.json()["detail"]
    # The designation is the owner's pen…
    assert client.put(f"/profiles/{p['id']}/proceeds",
                      json={"designees": [{"name": "Ana", "kind": "loved_one",
                                           "share": 100}]},
                      headers=auth_header(q)).status_code == 403
    r = client.put(f"/profiles/{p['id']}/proceeds",
                   json={"designees": [{"name": "Ana", "kind": "loved_one",
                                        "share": 100}]},
                   headers=auth_header(p))
    assert r.status_code == 200, r.text
    # …and anyone's to read: the donor gives to these names.
    seen = client.get(f"/profiles/{p['id']}/proceeds",
                      headers={"authorization": ""}).json()
    assert [d["name"] for d in seen["proceeds_to"]] == ["Ana"]
    # Now the campaign opens, and its card is public.
    r = client.post(f"/profiles/{p['id']}/campaigns",
                    json={"title": "roof fund", "goal": 500},
                    headers=auth_header(p))
    assert r.status_code == 201, r.text
    rows = client.get(f"/profiles/{p['id']}/campaigns",
                      headers={"authorization": ""}).json()
    assert any(c["title"] == "roof fund" for c in rows)


# -- the lifeline -----------------------------------------------------------

def test_the_lifeline_answers_a_bare_get(client):
    cloud = client.get("/cloud/status", headers={"authorization": ""}).json()
    assert cloud["cloud"] in (True, False)
    assert cloud["fallback"]
    off = client.get("/offline/status", headers={"authorization": ""}).json()
    assert off["external_transmission_possible"] == (not off["offline"])
    lights = client.get("/agent/lights",
                        headers={"authorization": ""}).json()
    assert sorted(lights["order"]) == sorted(
        row["light"] for row in lights["legend"])


def test_help_is_public_and_writes_nothing(client):
    topics = client.get("/help/topics",
                        headers={"authorization": ""}).json()
    assert topics["topics"] and topics["disclosure"]
    r = client.post("/help", json={"question": "what is a beacon?"},
                    headers={"authorization": ""})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["answer"]
    # The one unlabelled thing on a page of disclosed synthetics it is
    # not: a generated answer says so.
    assert "ai" in body and "source" in body


def test_a_local_provider_is_registered_and_found_by_area(client):
    r = client.post("/providers", json={"name": "Dr. Field",
                                        "area": "healthcare"})
    assert r.status_code == 201, r.text
    rows = client.get("/providers?area=healthcare",
                      headers={"authorization": ""}).json()
    assert any(row["name"] == "Dr. Field" for row in rows)
    assert client.get("/providers?area=nothing_here",
                      headers={"authorization": ""}).json() == []


# -- the doors and their languages ------------------------------------------

def test_every_shell_has_doors_on_the_three_blocks(client):
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert ("POST", "/signup") in made, \
            f"{lang.name}: no account can begin here"
        assert ("POST", "/signin") in made, \
            f"{lang.name}: the key does not turn"
        assert ("POST", "/password/reset") in made, \
            f"{lang.name}: a forgotten password strands the account"
        assert ("GET", "/auth/oauth/providers") in made, \
            f"{lang.name}: the OAuth doors are invisible"
        assert ("GET", "/plans") in made, \
            f"{lang.name}: the price list is unreadable"
        assert ("GET", "/subscriptions") in made, \
            f"{lang.name}: what you pay for is unlisted"
        assert ("GET", "/profiles/x/proceeds") in made, \
            f"{lang.name}: where the money goes cannot be checked"
        assert ("GET", "/cloud/status") in made, \
            f"{lang.name}: the cloud posture is unstated"
        assert ("POST", "/help") in made, \
            f"{lang.name}: there is nobody to ask"


def test_the_three_blocks_speak_ten_languages_on_every_shell(client):
    """Every acct/till/life key the iOS table carries, complete on all
    three shells — the full-list rule, never a sample."""
    shells = {
        "ios": REPO / "native/ios/Sources/L10n.swift",
        "android": (REPO / "native/android/app/src/main/java/app/qrme/"
                           "studio/L10n.kt"),
        "windows": REPO / "native/windows/L10n.cs",
    }
    langs = ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")
    ios_src = shells["ios"].read_text(encoding="utf-8")
    keys = sorted(set(re.findall(
        r'"((?:acct|till|life)\.[a-z.]+)":', ios_src)))
    assert len(keys) >= 40, f"the iOS table lost rows: {len(keys)}"
    for shell, path in shells.items():
        src = path.read_text(encoding="utf-8")
        for key in keys:
            row = re.search(rf'"{re.escape(key)}"[^\n]*', src)
            assert row, f"{shell}: missing {key}"
            for lang in langs:
                assert f'"{lang}"' in row.group(0), \
                    f"{shell}: {key} missing {lang}"
