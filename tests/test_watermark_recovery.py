"""Extract and reconstruct — the other direction of the watermark.

From the field drawing: message *m* + sequence *S^N* + security key *K^D* →
watermark *W* → embed → **Attack** → extract *W'* → reconstruct *m'*. The
existing credential answers "does this content match *this* id", which needs
the id up front and fails on one edited character without saying who wrote
the text. These tests are the missing direction: text arrives alone, possibly
edited, and QRME names its author with the evidence for the claim.
"""

from qrme import watermark


def _stamp(profile_id, text):
    return watermark.stamp(profile_id, "post", text)


PASSAGE = (
    "The garden was my grandmother's before it was mine, and she kept the "
    "roses along the south fence because that is where the light lingers "
    "longest in the afternoon. She never wrote any of it down. I learned the "
    "pruning by standing beside her every March until my hands knew it."
)


def test_verbatim_text_recovers_its_author(client, profile_id):
    stamped = _stamp(profile_id, PASSAGE)
    out = watermark.recover(PASSAGE)
    assert out["recovered"] is True
    assert out["profile_id"] == profile_id
    assert out["watermark_id"] == stamped["watermark_id"]
    assert out["verbatim"] is True and out["state"] == "unaltered"
    assert out["similarity"] == 1.0


def test_an_edited_passage_is_still_traceable(client, profile_id):
    """The 'Attack' box: the text is changed and the mark must survive it."""
    _stamp(profile_id, PASSAGE)
    attacked = PASSAGE.replace("grandmother's", "grandma's").replace(
        "south fence", "south wall").replace("every March", "each spring")
    out = watermark.recover(attacked)
    assert out["recovered"] is True
    assert out["profile_id"] == profile_id
    # It says plainly that this is not the text it stamped.
    assert out["verbatim"] is False
    assert out["state"] == "altered but traceable"
    assert 0.25 <= out["similarity"] < 1.0
    # And the claim is checkable rather than asserted.
    assert out["matched_windows"] < out["stored_windows"]
    assert "checked by hand" in out["method"]


def test_unrelated_text_recovers_nobody(client, profile_id):
    _stamp(profile_id, PASSAGE)
    out = watermark.recover(
        "Quarterly logistics throughput improved after the depot reshuffle, "
        "and the northern route now clears in under six hours.")
    assert out["recovered"] is False


def test_a_shared_phrase_is_not_an_accusation(client, profile_id):
    """Ordinary phrases travel between unrelated texts, so a few matching
    windows must not be enough to name an author."""
    _stamp(profile_id, PASSAGE)
    out = watermark.recover(
        "That is where the light lingers longest in the afternoon, which is "
        "why the survey team scheduled the photography for four o'clock and "
        "brought the longer lens along with the tripod and the grey card.")
    assert out["recovered"] is False
    assert out["best_similarity"] < watermark.RECOVER_THRESHOLD


def test_the_key_is_what_makes_it_a_watermark(client, profile_id, monkeypatch):
    """Without the deployment's key nobody can compute matching windows — so
    a credential cannot be forged onto text QRME never wrote."""
    _stamp(profile_id, PASSAGE)
    assert watermark.recover(PASSAGE)["recovered"] is True

    monkeypatch.setenv("QRME_WATERMARK_KEY", "a-different-deployments-key")
    assert watermark.recover(PASSAGE)["recovered"] is False


def test_two_profiles_are_told_apart(client, profile_id):
    second = client.post("/profiles", json={
        "owner_id": "owner-1", "kind": "self", "display_name": "Ray",
        "persona": "A boatyard hand who notices the light.",
        "verification": {"birthdate": "1980-04-04"}, "plan": "pro",
    })
    assert second.status_code == 201, second.text
    second_profile_id = second.json()["id"]
    _stamp(profile_id, PASSAGE)
    other = ("The dock lights come on at seven and the herons leave together, "
             "which is the only clock the boatyard has ever needed.")
    _stamp(second_profile_id, other)
    assert watermark.recover(PASSAGE)["profile_id"] == profile_id
    assert watermark.recover(other)["profile_id"] == second_profile_id


def test_the_route_answers_without_a_credential_id(client, profile_id):
    _stamp(profile_id, PASSAGE)
    r = client.post("/watermarks/recover", json={"content": PASSAGE})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["recovered"] is True and body["profile_id"] == profile_id
    assert body["display"]["mark"]
    assert "not a real person" in body["disclosure"]

    empty = client.post("/watermarks/recover", json={"content": "   "}).json()
    assert empty["recovered"] is False


def test_the_index_is_not_reversible_to_the_text(client, profile_id):
    """The stored rows are keyed hashes, so the index cannot be read back as
    the original writing — a provenance store must not become a corpus."""
    from qrme import db
    _stamp(profile_id, PASSAGE)
    rows = db.connect().execute(
        "SELECT shingle FROM watermark_shingles").fetchall()
    assert rows
    stored = " ".join(r["shingle"] for r in rows)
    for word in ("grandmother", "roses", "pruning", "March"):
        assert word not in stored
