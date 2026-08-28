"""The avatar registry: one face ledger, three roads in.

The owner's brief, in his own framing: seeding from the one already
built, prompt-to-generate, and picking from the curated list — provider
swappable, no surface ever calling one, takedowns as data operations.
Plus the two rules the brief did not carry and this estate will not
bend on: a synthetic face gets the AI mark burned into its bytes at
mint, and an authentic photograph never does.
"""

from __future__ import annotations

import io

from qrme import avatarreg, db, portraitist

from tests.test_capabilities import make_profile  # noqa: F401


def _png(color=(40, 90, 200)) -> bytes:
    from PIL import Image
    img = Image.new("RGB", (256, 256), color)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def _account(client, monkeypatch, email="ava@example.test"):
    from tests.test_accounts import _capture_mail, _code_from
    sent = _capture_mail(monkeypatch)
    client.post("/signup", json={"email": email,
                                 "password": "hunter2-hunter2",
                                 "display_name": "Ava"})
    r = client.post("/verify-email",
                    json={"email": email, "code": _code_from(sent[0])})
    assert r.status_code == 200, r.text
    return r.json()


# -- the mark rides the row --------------------------------------------------

def test_an_invented_face_is_marked_at_mint(client):
    raw = _png()
    row = avatarreg.mint(data=raw, source="curated_library",
                        provider="elevenlabs", likeness="invented")
    assert row["marked"] is True
    assert row["checksum"] is not None
    served = client.get(row["asset"])
    assert served.status_code == 200
    assert served.content != raw, "the mark was never burned"


def test_an_authentic_photograph_is_never_marked(client):
    row = avatarreg.mint(data=_png((90, 40, 20)), source="uploaded",
                        likeness="self", owner_account_id="acc_x")
    assert row["marked"] is False, (
        "a real face was stamped with the AI mark — a false statement in "
        "the exact direction the mark exists to prevent")


# -- the shelf ---------------------------------------------------------------

def test_the_operator_stocks_the_shelf_and_everyone_reads_it(client,
                                                             monkeypatch):
    monkeypatch.setenv("QRME_SIGNUP_KEY", "op-secret")
    no = client.post("/avatars/library", content=_png())
    assert no.status_code == 403, "anybody could stock the deployment shelf"
    ok = client.post("/avatars/library?provider=elevenlabs",
                     content=_png(), headers={"x-signup-key": "op-secret"})
    assert ok.status_code == 201, ok.text
    shelf = client.get("/avatars/library").json()
    assert any(r["id"] == ok.json()["id"] for r in shelf["shelf"])
    assert shelf["starters"], "the picker can empty — the starters are gone"


def test_a_personal_shelf_needs_its_own_token(client, monkeypatch):
    got = _account(client, monkeypatch)
    acc, tok = got["account_id"], got["account_token"]
    r = client.post(f"/accounts/{acc}/avatars?likeness=self",
                    content=_png(),
                    headers={"authorization": f"Bearer {tok}"})
    assert r.status_code == 201, r.text
    assert r.json()["marked"] is False
    stranger = client.get(f"/accounts/{acc}/avatars")
    assert stranger.status_code in (401, 403)
    mine = client.get(f"/accounts/{acc}/avatars",
                      headers={"authorization": f"Bearer {tok}"}).json()
    assert len(mine["shelf"]) == 1


# -- claim and takedown ------------------------------------------------------

def test_claim_points_the_profile_and_retire_reaches_every_claimant(
        client, profile_id):
    row = avatarreg.mint(data=_png(), source="curated_library",
                        likeness="invented")
    r = client.post(f"/profiles/{profile_id}/avatar/claim",
                    json={"registry_id": row["id"]})
    assert r.status_code == 200, r.text
    held = db.connect().execute(
        "SELECT avatar, avatar_ref FROM profiles WHERE id=?",
        (profile_id,)).fetchone()
    assert held["avatar_ref"] == row["id"] and held["avatar"] == row["asset"]

    gone = avatarreg.retire(row["id"], because="rights withdrawn")
    assert gone["status"] == "retired" and gone["retired_at"]
    held = db.connect().execute(
        "SELECT avatar, avatar_ref FROM profiles WHERE id=?",
        (profile_id,)).fetchone()
    assert held["avatar"] is None and held["avatar_ref"] is None, (
        "a withdrawn face is still on a profile — the takedown did not "
        "reach its claimants")


def test_a_disputed_face_refuses_new_claims(client, profile_id):
    row = avatarreg.mint(data=_png(), source="curated_library",
                        likeness="invented")
    avatarreg.dispute(row["id"])
    r = client.post(f"/profiles/{profile_id}/avatar/claim",
                    json={"registry_id": row["id"]})
    assert r.status_code == 409, "a contested face was handed out anyway"


# -- painted from words ------------------------------------------------------

def test_no_painting_key_refuses_in_a_sentence(client, monkeypatch):
    monkeypatch.delenv("QRME_IMAGE_KEY", raising=False)
    profile = make_profile(client, kind="fictional")
    r = client.post(f"/profiles/{profile['id']}/avatar/painted",
                    json={"direction": "kind eyes"})
    assert r.status_code == 503
    assert "no painting service" in r.json()["detail"]


def test_a_real_persons_face_is_never_painted(client):
    profile = make_profile(client)     # kind=self
    r = client.post(f"/profiles/{profile['id']}/avatar/painted",
                    json={})
    assert r.status_code == 403
    assert "recorded grant" in r.json()["detail"]


def test_painted_lands_with_provenance_age_and_mark(client, monkeypatch):
    profile = make_profile(client, kind="fictional", base_age=30,
                           aging_enabled=True)
    seen = {}
    def fake_paint(prof, words=""):
        prompt = portraitist.describe(prof, words)
        seen["prompt"] = prompt
        return _png((10, 200, 120)), prompt, {"model": "fake"}
    monkeypatch.setattr(portraitist, "paint", fake_paint)
    r = client.post(f"/profiles/{profile['id']}/avatar/painted",
                    json={"direction": "a small smile"})
    assert r.status_code == 201, r.text
    assert "years old" in seen["prompt"], "the face did not age"
    assert "invented person" in seen["prompt"], (
        "the constraint that survives being pasted anywhere is gone")
    ref = db.connect().execute(
        "SELECT avatar_ref FROM profiles WHERE id=?",
        (profile["id"],)).fetchone()["avatar_ref"]
    row = avatarreg.row(ref)
    assert row["source"] == "prompted" and row["marked"] is True
    assert row["prompt_text"] and row["generation_params"]["model"] == "fake"


def test_the_wardrobe_opens_for_guests_until_the_owner_closes_it(
        client, monkeypatch):
    """The people a profile talks with get to dress it — by default.

    `guest_styling` starts on: a signed-in visitor can prompt a restyle.
    The owner's PATCH closes the wardrobe, and from then on the same
    visitor reads the refusal while the owner still paints. A caller with
    no token at all was never a guest — 401, switch or no switch."""
    from qrme import auth
    profile = make_profile(client, kind="fictional")
    owner = dict(client.headers)
    monkeypatch.setattr(
        portraitist, "paint",
        lambda prof, words="": (_png((5, 5, 5)), "p", {"model": "fake"}))

    assert client.get(f"/profiles/{profile['id']}").json()[
        "guest_styling"] is True, "the wardrobe did not start open"

    guest = {"authorization": f"Bearer {auth.issue('interactor', 'int_g')}"}
    r = client.post(f"/profiles/{profile['id']}/avatar/painted",
                    json={"direction": "a red scarf"}, headers=guest)
    assert r.status_code == 201, r.text

    nobody = client.post(f"/profiles/{profile['id']}/avatar/painted",
                         json={"direction": "a hat"},
                         headers={"authorization": ""})
    assert nobody.status_code == 401, (
        "an anonymous caller repainted somebody's avatar")

    closed = client.patch(f"/profiles/{profile['id']}",
                          json={"guest_styling": False}, headers=owner)
    assert closed.status_code == 200, closed.text
    assert closed.json()["guest_styling"] is False

    r = client.post(f"/profiles/{profile['id']}/avatar/painted",
                    json={"direction": "a red scarf"}, headers=guest)
    assert r.status_code == 403
    assert "wardrobe closed" in r.json()["detail"]

    r = client.post(f"/profiles/{profile['id']}/avatar/painted",
                    json={"direction": "a red scarf"}, headers=owner)
    assert r.status_code == 201, "closing the wardrobe locked the owner out"


def test_both_refusals_speak_ten_languages():
    from qrme import i18n
    for text in (
            "a real person's face is never painted from words — attach a "
            "photograph under a recorded grant instead",
            "no painting service is configured — the deployment has no "
            "image key"):
        for lang in ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"):
            assert i18n.tr_public(text, lang) != text, (
                f"{text[:40]}... is English in {lang}")


def test_a_face_carries_its_name(client, monkeypatch):
    """"Mine in particular, I made there — it should say David Bianchi."
    A label rides the row from the stock door to the shelf."""
    monkeypatch.setenv("QRME_SIGNUP_KEY", "op-secret")
    ok = client.post("/avatars/library?provider=elevenlabs"
                     "&label=David%20Bianchi",
                     content=_png((60, 60, 160)),
                     headers={"x-signup-key": "op-secret"})
    assert ok.status_code == 201, ok.text
    assert ok.json()["label"] == "David Bianchi"
    shelf = client.get("/avatars/library").json()["shelf"]
    assert any(r.get("label") == "David Bianchi" for r in shelf)


def test_the_market_names_many_companies_and_the_default_leads():
    """The same format the model keys took: many options, and the
    deployment's own — ElevenLabs — first on the owner's word."""
    from qrme import avatars
    keys = [m["key"] for m in avatars.MARKET]
    assert keys[0] == "elevenlabs", "the owner's provider no longer leads"
    for expected in ("ready_player_me", "roblox", "vroid_hub", "dicebear",
                     "gravatar", "heygen", "avaturn"):
        assert expected in keys, f"{expected} fell off the market"
    for m in avatars.MARKET:
        assert m["key"] and m["name"] and m["how"], (
            "a market row without its export instructions is a name with "
            "no road")
