"""Friends lists between profiles, and the founder who comes as standard.

The founder's two profiles are **fixed** on every list — pinned, unremovable,
and in a set order. That is a product decision by the platform's owner, taken
after the removable version had been built, so the tests here pin the decision
rather than argue with it: the pins hold, an ordinary friend is still freely
removable, and the list says which rows are which so a client does not offer a
control that will fail.

The other half is keeping this apart from `relationships`, which is a different
table answering a different question. A bug that read one as the other would
look exactly like working code.
"""

import pytest

from qrme import db, friends, seed
from tests.test_capabilities import auth_header, make_profile


def _seeded(client):
    """Seed the collection, and hand back both founder profile ids in pinned
    order: the photographed one, then the rendered one."""
    out = seed.seed()
    return [out["founder_verified"], out["founder"]]


# -- the founder comes standard ---------------------------------------------

def test_a_new_profile_gets_both_founders_at_the_top(client):
    """Two profiles of the same man — the photograph and the AI rendering —
    in that fixed order."""
    live, rendered = _seeded(client)
    profile = make_profile(client, display_name="Newcomer")

    listed = client.get(f"/profiles/{profile['id']}/friends").json()
    assert listed["count"] == 2
    assert [f["profile_id"] for f in listed["friends"]] == [live, rendered]
    assert [f["position"] for f in listed["friends"]] == [1, 2]
    assert all(f["founder"] and f["pinned"] for f in listed["friends"])
    assert [f["handle"] for f in listed["friends"]] == list(
        friends.FOUNDER_HANDLES)


def test_the_founder_stays_first_however_many_friends_arrive(client):
    """Position is computed from `origin`, not stored. A stored column would be
    the thing that is wrong on the day the founder turns up third."""
    live, rendered = _seeded(client)
    profile = make_profile(client, display_name="Popular")
    others = [make_profile(client, display_name=f"Friend {i}")
              for i in range(3)]
    for other in others:
        r = client.post(f"/profiles/{profile['id']}/friends",
                        json={"friend_id": other["id"]},
                        headers=auth_header(profile))
        assert r.status_code == 200, r.text

    listed = client.get(f"/profiles/{profile['id']}/friends").json()
    assert listed["count"] == 5
    assert [f["profile_id"] for f in listed["friends"]][:2] == [live, rendered]
    assert [f["founder"] for f in listed["friends"]] == [
        True, True, False, False, False]


def test_the_founder_is_first_even_when_he_arrives_last(client):
    """The real ordering test. Everywhere else the founder is installed at
    creation, so he is also the *oldest* row and plain `created_at` ordering
    would look correct while testing nothing. Here he is seeded onto a
    deployment that already had profiles and friends, so his row is the
    newest — and he must still stand first."""
    a = make_profile(client, display_name="Early Adopter")
    b = make_profile(client, display_name="Their Friend")
    client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                headers=auth_header(a))
    assert client.get(f"/profiles/{a['id']}/friends").json()["count"] == 1

    live, rendered = _seeded(client)   # the founders appear only now

    listed = client.get(f"/profiles/{a['id']}/friends").json()
    assert listed["count"] == 3
    assert [f["profile_id"] for f in listed["friends"]] == [live, rendered,
                                                            b["id"]]
    assert listed["friends"][0]["position"] == 1


def test_the_backfill_restores_a_pin_that_was_cleared(client):
    """Unlike an ordinary un-friending, `removed` is not a state the pins are
    allowed to stay in — so a row cleared before they became fixed is repaired
    rather than respected."""
    live, rendered = _seeded(client)
    a = make_profile(client, display_name="Decided")
    db.connect().execute(
        "UPDATE friendships SET state='removed' WHERE profile_id=? AND"
        " friend_id=?", (a["id"], live))
    db.connect().commit()
    assert client.get(f"/profiles/{a['id']}/friends").json()["count"] == 1

    assert a["id"] in friends.backfill_founder()
    assert client.get(f"/profiles/{a['id']}/friends").json()["count"] == 2


def test_a_founder_profile_does_not_befriend_itself(client):
    """Each carries the other, but neither carries itself."""
    live, rendered = _seeded(client)
    for me, other in ((live, rendered), (rendered, live)):
        listed = client.get(f"/profiles/{me}/friends").json()
        assert [f["profile_id"] for f in listed["friends"]] == [other]


def test_install_is_silent_when_there_is_no_founder(client):
    """An unseeded deployment has none. Creating a profile must still work —
    a cosmetic default is not a reason for profile creation to fail."""
    assert friends.founder_ids() == []
    profile = make_profile(client, display_name="Early")
    assert client.get(f"/profiles/{profile['id']}/friends").json()["count"] == 0


# -- and can be shown the door ----------------------------------------------

def test_the_founder_pins_cannot_be_removed(client):
    """Fixed by product decision — the platform's owner asked for exactly this,
    after the removable version had been built and shown. Enforced in
    `unfriend`, the one function every removal path goes through, so a future
    caller cannot route around it by not knowing about it."""
    founders = _seeded(client)
    profile = make_profile(client, display_name="Independent")

    for fid in founders:
        r = client.delete(f"/profiles/{profile['id']}/friends/{fid}",
                          headers=auth_header(profile))
        assert r.status_code == 409, r.text
        assert "cannot be removed" in r.json()["detail"]
    assert client.get(f"/profiles/{profile['id']}/friends").json()["count"] == 2


def test_the_list_says_which_rows_are_pinned(client):
    """So a client renders those rows without a remove control, rather than
    offering one that 409s."""
    _seeded(client)
    profile = make_profile(client, display_name="Reader")
    other = make_profile(client, display_name="Chosen")
    client.post(f"/profiles/{profile['id']}/friends",
                json={"friend_id": other["id"]}, headers=auth_header(profile))

    entries = client.get(f"/profiles/{profile['id']}/friends").json()["friends"]
    assert [f["pinned"] for f in entries] == [True, True, False]


def test_an_ordinary_friend_is_still_removable(client):
    """The pin is the exception, not the new rule."""
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                headers=auth_header(a))
    r = client.delete(f"/profiles/{a['id']}/friends/{b['id']}",
                      headers=auth_header(a))
    assert r.status_code == 200 and r.json()["removed"] is True
    assert client.get(f"/profiles/{a['id']}/friends").json()["count"] == 2


def test_removing_an_ordinary_friend_sticks(client):
    """The tombstone machinery still earns its keep: the founder install runs
    on profile creation, and a deleted row would be recreated."""
    _seeded(client)
    a = make_profile(client, display_name="Firm")
    b = make_profile(client, display_name="Gone")
    client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                headers=auth_header(a))
    client.delete(f"/profiles/{a['id']}/friends/{b['id']}",
                  headers=auth_header(a))
    friends.install_founder(a["id"])
    listed = client.get(f"/profiles/{a['id']}/friends").json()
    assert b["id"] not in [f["profile_id"] for f in listed["friends"]]


# -- the ordinary verbs ------------------------------------------------------

def test_a_list_is_directed_not_mutual(client):
    """Befriending writes one row. A mutual edge would mean somebody else's
    action edits your list."""
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")

    client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                headers=auth_header(a))

    a_list = client.get(f"/profiles/{a['id']}/friends").json()["friends"]
    b_list = client.get(f"/profiles/{b['id']}/friends").json()["friends"]
    assert b["id"] in [f["profile_id"] for f in a_list]
    assert a["id"] not in [f["profile_id"] for f in b_list]
    assert [f for f in a_list if f["profile_id"] == b["id"]][0]["mutual"] is False


def test_mutual_is_reported_once_both_rows_exist(client):
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                headers=auth_header(a))
    client.post(f"/profiles/{b['id']}/friends", json={"friend_id": a["id"]},
                headers=auth_header(b))

    a_list = client.get(f"/profiles/{a['id']}/friends").json()["friends"]
    assert [f for f in a_list if f["profile_id"] == b["id"]][0]["mutual"] is True


def test_befriending_twice_is_idempotent(client):
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    for _ in range(2):
        client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                    headers=auth_header(a))
    listed = client.get(f"/profiles/{a['id']}/friends").json()
    assert [f["profile_id"] for f in listed["friends"]].count(b["id"]) == 1


def test_a_profile_cannot_befriend_itself(client):
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    r = client.post(f"/profiles/{a['id']}/friends", json={"friend_id": a["id"]},
                    headers=auth_header(a))
    assert r.status_code == 422
    assert "own friend" in r.json()["detail"]


def test_only_the_owner_edits_the_list(client):
    _seeded(client)
    a = make_profile(client, display_name="Ada")
    b = make_profile(client, display_name="Bo")
    # b's owner token, aimed at a's list.
    r = client.post(f"/profiles/{a['id']}/friends", json={"friend_id": b["id"]},
                    headers=auth_header(b))
    assert r.status_code in (401, 403)


# -- the friends list is not the relationships table -------------------------

def test_friendships_and_relationships_are_separate_tables(client):
    """`relationships` records how a profile treats an *interactor*. Reading
    one as the other would look like working code."""
    _seeded(client)
    profile = make_profile(client, display_name="Distinct")
    conn = db.connect()
    assert conn.execute(
        "SELECT COUNT(*) AS n FROM relationships WHERE profile_id=?",
        (profile["id"],)).fetchone()["n"] == 0
    assert conn.execute(
        "SELECT COUNT(*) AS n FROM friendships WHERE profile_id=?",
        (profile["id"],)).fetchone()["n"] == 2


# -- the founder profile itself ---------------------------------------------

def test_the_rendered_founder_is_marked_like_the_other_thirty_four(client):
    """An AI rendering of a real face is exactly the case the mark exists
    for, so it gets the same treatment as the other 34 rather than a
    gentler one — and the treatment is now a label drawn on the sphere
    rather than pixels burned into the portrait, because every surface
    here draws a face as a circle and a circle crops a square's corner.

    `asset_marked: False` is what tells each of those surfaces to draw
    its own badge. The claim that matters is unchanged: this face is a
    real person's likeness, it is synthetic, and the grant is revocable."""
    live, rendered = _seeded(client)
    avatar = client.get(f"/profiles/{rendered}/avatar").json()
    assert avatar["asset"] == f"/portraits/{seed.FOUNDER_HANDLE}.webp"
    assert avatar["asset_marked"] is False
    assert avatar["likeness"]["real_person"] is True
    assert avatar["likeness"]["revocable"] is True


def test_the_photograph_is_not_marked_ai_but_the_profile_still_is(client):
    """Two different claims, and they must not be run together.

    The picture is authentic, so burning *AI-generated synthetic media* into it
    would be a false statement in the opposite direction from the one the mark
    exists to prevent. The profile is synthetic, so it still carries the
    watermark — `asset_marked: False` is the signal every surface uses to
    composite it.
    """
    live, rendered = _seeded(client)
    avatar = client.get(f"/profiles/{live}/avatar").json()
    assert avatar["asset"] == f"/photos/{seed.VERIFIED_HANDLE}.webp"
    assert avatar["asset_marked"] is False
    assert avatar["watermark"]                      # the profile is still labelled
    assert avatar["likeness"]["real_person"] is True


def test_no_photograph_is_ever_reported_as_carrying_the_mark(client):
    """The guard, stated once. If a photograph were served from the burned
    tree, `asset_is_marked` would say True and every surface would skip its
    badge — leaving an unlabelled synthetic profile behind a real face."""
    from qrme import avatars
    assert avatars.asset_is_marked("/photos/anything.webp") is False
    assert avatars.asset_is_marked(None) is False
    for path in avatars.photos_dir().glob("*.webp"):
        assert avatars.asset_is_marked(f"/photos/{path.name}") is False


def test_both_founder_profiles_are_grounded(client):
    """0.3.1 established that a profile with no source material answers from
    tone alone. The two profiles every new account meets first must not
    reintroduce it."""
    for pid in _seeded(client):
        rows = db.connect().execute(
            "SELECT title FROM source_items WHERE profile_id=?",
            (pid,)).fetchall()
        assert len(rows) == len(seed.FOUNDER_SOURCES)
        assert db.connect().execute(
            "SELECT COUNT(*) AS n FROM source_items WHERE profile_id=? AND"
            " pack_id IS NOT NULL", (pid,)).fetchone()["n"] == 0


def test_neither_founder_is_in_the_fictional_starter_collection(client):
    """`seed.py`'s docstring promises every starter is fictional, and
    `avatars.BRIEFS` promises every brief describes an invented person. A real
    person in either list would quietly make a documented claim false."""
    from qrme import avatars
    handles = [h for h, *_ in seed.STARTERS + seed.RATED]
    for handle in friends.FOUNDER_HANDLES:
        assert handle not in handles
        assert handle not in avatars.BRIEFS


def test_the_founder_handles_agree_with_the_seed(client):
    """Two modules name the same person twice over. If they drift, every new
    profile gets a short list and nothing else complains."""
    assert set(friends.FOUNDER_HANDLES) == {seed.FOUNDER_HANDLE,
                                            seed.VERIFIED_HANDLE}


# -- verified means something, or it means nothing ---------------------------

def test_the_verified_profile_carries_a_level_not_just_a_word(client):
    """A badge with nothing behind it is a credential the platform minted for
    itself. The level and its plain-English meaning travel with the word, so no
    surface can show one without the other."""
    from qrme import verification
    verified, rendered = _seeded(client)
    v = client.get(f"/profiles/{verified}/verification").json()
    assert v["verified"] is True
    assert v["real_person"] is True
    assert v["level"] in verification.PROOFING_LEVELS
    assert v["means"] == verification.MEANING[v["level"]]
    assert v["attestor"]


def test_self_asserted_says_so_in_the_badge(client):
    """It is the bottom rung, and nobody has checked a document. Saying that
    beside the word is the difference between a badge and a claim."""
    verified, rendered = _seeded(client)
    v = client.get(f"/profiles/{verified}/verification").json()
    assert v["level"] == "self_asserted"
    assert v["rank"] == 0
    assert "not that a document was checked" in v["caveat"]


def test_a_level_above_self_asserted_needs_a_named_attestor(client):
    """The same rule `signatures.enroll` applies, for the same reason: who
    checked belongs in the record, not in a footnote."""
    from qrme import verification
    verified, _ = _seeded(client)
    with pytest.raises(verification.VerificationError) as exc:
        verification.verify(verified, "document")
    assert "requires an attestor" in str(exc.value)

    ok = verification.verify(verified, "document", attestor="A notary",
                             method="passport")
    assert ok["rank"] == 2 and ok["caveat"] is None


def test_an_invented_profile_has_nobody_to_verify(client):
    """`fictional` is not unverified — it is a different answer. Reporting it
    as 'not verified' would imply somebody failed a check."""
    from qrme import db, verification
    _seeded(client)
    starter = db.connect().execute(
        "SELECT profile_id FROM handles WHERE handle='marcus_bell'").fetchone()
    v = verification.status(starter["profile_id"])
    assert v["verified"] is False and v["real_person"] is False
    assert "nobody to verify" in v["note"]


def test_an_unchecked_real_person_is_not_reported_as_verified(client):
    """The default for a real-person profile is no badge at all."""
    from qrme import verification
    _seeded(client)
    mine = make_profile(client, display_name="Nobody Checked")
    v = verification.status(mine["id"])
    assert v["verified"] is False and v["real_person"] is True


def test_the_friends_list_carries_the_verification_record(client):
    """A friends list is exactly where somebody decides whether a face is a
    real person, so the level rides with the row."""
    verified, rendered = _seeded(client)
    profile = make_profile(client, display_name="Reader")
    entries = client.get(f"/profiles/{profile['id']}/friends").json()["friends"]
    assert entries[0]["verification"]["verified"] is True
    assert entries[0]["verification"]["level"] == "self_asserted"


# -- the founder actually knows things ---------------------------------------

def test_both_founder_profiles_carry_the_domain_knowledge(client):
    """The platform reasoning was there from the start; the man's own subject
    was not, which left the profile every account meets first unable to answer
    the thing it is most likely to be asked about."""
    from qrme import db
    for pid in _seeded(client):
        titles = [r["title"] for r in db.connect().execute(
            "SELECT title FROM source_items WHERE profile_id=? AND"
            " pack_id IS NULL", (pid,)).fetchall()]
        assert any("Private Data Infrastructure" in t for t in titles)
        assert any("Envelope encryption" in t for t in titles)
        assert len(titles) == len(seed.FOUNDER_SOURCES)


def test_only_the_ai_half_carries_the_knowledge_packs(client):
    """The asymmetry is the honest way round. The photographed profile is the
    man; loading it with four industry libraries would be claiming he has them
    memorised. The rendered one is openly a synthetic expert, which is what a
    pack is for.

    Packs arrive on the seed re-run once the library is published — the same
    repair path the portraits and the starters' grounding take."""
    from qrme import db
    verified, rendered = _seeded(client)
    client.post("/packs/seed")
    seed.seed()

    def packs_on(pid):
        return db.connect().execute(
            "SELECT COUNT(*) AS n FROM pack_installs WHERE profile_id=?",
            (pid,)).fetchone()["n"]

    assert packs_on(rendered) == len(seed.FOUNDER_AI_PACKS)
    assert packs_on(verified) == 0


def test_both_founder_profiles_carry_skills_and_a_cv(client):
    """Experience on a real person is a credential, which is why
    `set_experience` refuses it without a rights basis — so the basis has to be
    recorded before the CV, and a missing one would fail here rather than
    silently leave the page empty."""
    from qrme import frontpage
    for pid in _seeded(client):
        page = frontpage.front_page(pid)
        assert page["skills"] == seed.FOUNDER_SKILLS
        assert [e["title"] for e in page["experience"]] == [
            e["title"] for e in seed.FOUNDER_EXPERIENCE]


def test_only_the_photographed_founder_profile_is_verified(client):
    """One person, one badge — and the founder is the case that shows why.

    Both profiles are the same human being, so this used to have the platform
    asserting that David Bianchi was two verified people, on the deployment
    that ships as the worked example of the rule. The badge belongs to the
    photographed half, because a real person whose picture is authentic is
    exactly what the badge is a claim about; the rendered half carries the AI
    mark instead, which is the claim that is true of it.
    """
    from qrme import db, identity, verification
    live, rendered = _seeded(client)

    assert verification.status(live)["verified"] is True
    assert verification.status(rendered)["verified"] is False

    owner = db.connect().execute("SELECT owner_id FROM profiles WHERE id=?",
                                 (live,)).fetchone()["owner_id"]
    assert identity.verified_profile(owner) == live

    # And the rendered half cannot take a second one while the first stands.
    assert identity.can_verify(rendered)["can_verify"] is False


def test_the_cv_needs_the_rights_basis_that_was_recorded(client):
    """Mutation guard in test form: strip the basis and the CV becomes
    impossible to set, which is the rule doing its job."""
    from qrme import db, frontpage
    verified, _ = _seeded(client)
    db.connect().execute(
        "UPDATE profiles SET consent_basis=NULL WHERE id=?", (verified,))
    db.connect().commit()
    with pytest.raises(frontpage.FrontPageError):
        frontpage.set_experience(verified, list(seed.FOUNDER_EXPERIENCE))
