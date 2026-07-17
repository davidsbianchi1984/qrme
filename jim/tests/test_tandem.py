"""JIM-mini in tandem with a real (separate) QRME instance.

JIM reaches QRME only through QRMEClient over the HTTP surface — no imports of
QRME internals. These tests prove the two products interoperate.
"""

from jim.tests.conftest import enroll

ADULT = {"birthdate": "1980-01-01"}


def _make_qrme_specialist(qrme, name, persona):
    r = qrme.post("/profiles", json={
        "owner_id": "clinic", "kind": "fictional", "display_name": name,
        "persona": persona, "verification": ADULT,
    })
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_health_reports_tandem(tandem):
    jim, _ = tandem
    assert jim.get("/health").json()["tandem"] is True


def test_guidance_delegated_to_qrme_specialist(tandem):
    jim, qrme = tandem
    profile_id = _make_qrme_specialist(
        qrme, "Anxiety Specialist", "A calm anxiety coach guiding breathing."
    )
    jim.post("/specialists", json={"condition": "anxiety", "mode": "tandem",
                                   "qrme_profile_id": profile_id})
    user = enroll(jim)

    body = jim.post(f"/monitor/{user}",
                    json={"heart_rate": 120, "respiratory_rate": 22,
                          "note": "my chest is tight"}).json()
    g = body["guidance"]
    assert g["source"] == "tandem"
    assert g["qrme_profile_id"] == profile_id
    assert g["delivered"] is True
    # The reply came back through QRME's own pipeline (approved by its moderation).
    assert g["qrme_status"] == "approved"
    assert g["content"]


def test_tandem_reply_is_remembered_in_qrme_memory(tandem):
    jim, qrme = tandem
    profile_id = _make_qrme_specialist(qrme, "Anxiety Specialist", "A calm coach.")
    jim.post("/specialists", json={"condition": "anxiety", "mode": "tandem",
                                   "qrme_profile_id": profile_id})
    user = enroll(jim)
    jim.post(f"/monitor/{user}", json={"heart_rate": 125, "respiratory_rate": 24})

    # JIM created a QRME interactor; that interactor now has memory in QRME.
    interactors = qrme.get("/profiles/" + profile_id)  # profile exists
    assert interactors.status_code == 200
    # Find the interactor JIM created and confirm the episode is stored.
    # (JIM's display_name default is "Jordan".)
    # Pull memory via the QRME interactor recorded on the tandem link.
    from jim import db as jim_db
    link = jim_db.connect().execute(
        "SELECT qrme_interactor_id FROM tandem_links WHERE user_id=?", (user,)
    ).fetchone()
    mem = qrme.get(f"/profiles/{profile_id}/memory/{link['qrme_interactor_id']}").json()
    roles = [m["role"] for m in mem]
    assert "interactor" in roles and "profile" in roles


def test_qrme_moderation_applies_to_tandem_guidance(tandem):
    jim, qrme = tandem
    # A specialist whose owner requires manual approval: replies are held.
    r = qrme.post("/profiles", json={
        "owner_id": "clinic", "kind": "fictional", "display_name": "Cautious Coach",
        "persona": "A careful coach.", "moderation_mode": "manual",
        "verification": ADULT,
    })
    profile_id = r.json()["id"]
    jim.post("/specialists", json={"condition": "anxiety", "mode": "tandem",
                                   "qrme_profile_id": profile_id})
    user = enroll(jim)
    g = jim.post(f"/monitor/{user}",
                 json={"heart_rate": 120, "respiratory_rate": 22}).json()["guidance"]
    # QRME held the reply; JIM surfaces that faithfully (content hidden).
    assert g["source"] == "tandem"
    assert g["qrme_status"] == "pending"
    assert g["content"] is None
    assert g["delivered"] is False
