"""Anonymous, several, and exactly one verified.

The three rules interact, and the tests that matter are the ones about the
interaction rather than about each rule alone:

- anonymity has to survive the route that returns the profile, not only the
  four surfaces that render one;
- holding several profiles must not be a way to collect several badges;
- and the call that links a person's profiles to each other has to be the
  hardest thing here to read, because it is the tool for undoing every
  anonymity promise at once.
"""

import pytest

from qrme import db, identity, seed, verification
from tests.test_capabilities import auth_header, make_profile


def _anon(client):
    """No token at all. `make_profile` leaves the last owner's token on the
    client, so "send no headers" means "whoever was created last"."""
    return {"authorization": ""}


def _hidden(client, **extra):
    return make_profile(client, anonymous=True, **extra)


# -- anonymity is a property, not a label ------------------------------------

def test_an_anonymous_profile_does_not_return_its_name(client):
    """The defect this module was written around.

    `anonymous` was honoured by the front-page card, the landing page, the
    prompt and the watermark — every surface that *renders* a profile. The
    route that returns the profile handed over `display_name` in full, so the
    shortest way past anonymity was to ask for the profile.
    """
    p = _hidden(client, display_name="Wren Ashby")
    seen = client.get(f"/profiles/{p['id']}", headers=_anon(client)).json()
    assert seen["display_name"] == "anonymous persona"
    assert "Wren Ashby" not in str(seen)


def test_the_owner_still_sees_their_own_name(client):
    """Anonymity is a promise to readers, not a lock the owner is behind."""
    p = _hidden(client, display_name="Wren Ashby")
    mine = client.get(f"/profiles/{p['id']}", headers=auth_header(p)).json()
    assert mine["display_name"] == "Wren Ashby"


def test_two_anonymous_profiles_cannot_be_matched_to_each_other(client):
    """The worse half, because it does not undo one profile's anonymity — it
    undoes all of them at once. Both rows carry the same `owner_id`, and it
    used to be published, so anyone could read it off two profiles and know
    they were the same person."""
    a = _hidden(client, owner_id="owner-x", display_name="One")
    b = _hidden(client, owner_id="owner-x", display_name="Two")
    seen_a = client.get(f"/profiles/{a['id']}", headers=_anon(client)).json()
    seen_b = client.get(f"/profiles/{b['id']}", headers=_anon(client)).json()
    assert seen_a["owner_id"] is None and seen_b["owner_id"] is None


def test_a_named_profile_does_not_leak_the_account_either(client):
    """Withheld from everyone but the owner, on every profile — not only the
    anonymous ones. A named profile publishing the account is the other end of
    the same match: read it there, then find the anonymous ones beside it."""
    p = make_profile(client, owner_id="owner-y", display_name="Public Pat")
    seen = client.get(f"/profiles/{p['id']}", headers=_anon(client)).json()
    assert seen["display_name"] == "Public Pat"      # not anonymous, so shown
    assert seen["owner_id"] is None                  # still not this


def test_the_report_says_what_anonymity_cannot_do(client):
    """Both halves, because the dangerous reading of the word is the generous
    one and somebody deciding whether it is safe to post deserves the limit in
    the same breath as the promise."""
    p = _hidden(client)
    out = client.get(f"/profiles/{p['id']}/anonymity",
                     headers=auth_header(p)).json()
    assert out["anonymous"] is True
    assert out["withheld"] and out["not_withheld"]
    assert any("recognise" in s or "recognisable" in s
               for s in out["not_withheld"] + [out["note"]])


def test_anonymity_is_per_profile_not_per_account(client):
    """An account-wide switch would mean putting your name on the work profile
    puts it on the support-group one — the exact coupling several profiles
    exist to avoid."""
    a = make_profile(client, owner_id="owner-z", display_name="Work")
    b = _hidden(client, owner_id="owner-z", display_name="Not Work")
    client.put(f"/profiles/{a['id']}/anonymity", json={"anonymous": True},
               headers=auth_header(a))
    assert identity.is_anonymous(a["id"]) is True
    assert identity.is_anonymous(b["id"]) is True

    client.put(f"/profiles/{a['id']}/anonymity", json={"anonymous": False},
               headers=auth_header(a))
    assert identity.is_anonymous(a["id"]) is False
    assert identity.is_anonymous(b["id"]) is True     # untouched


def test_only_the_owner_can_read_or_change_anonymity(client):
    a = _hidden(client, owner_id="owner-a", display_name="Mine")
    b = make_profile(client, owner_id="owner-b", display_name="Yours")
    assert client.get(f"/profiles/{a['id']}/anonymity",
                      headers=auth_header(b)).status_code == 403
    assert client.put(f"/profiles/{a['id']}/anonymity",
                      json={"anonymous": False},
                      headers=auth_header(b)).status_code == 403
    assert client.get(f"/profiles/{a['id']}/anonymity",
                      headers=_anon(client)).status_code == 401


# -- several profiles, one badge ---------------------------------------------

def test_a_person_may_hold_as_many_profiles_as_they_like(client):
    a = make_profile(client, owner_id="owner-m", display_name="One")
    make_profile(client, owner_id="owner-m", display_name="Two")
    make_profile(client, owner_id="owner-m", display_name="Three")
    out = client.get(f"/profiles/{a['id']}/siblings",
                     headers=auth_header(a)).json()
    assert out["count"] == 3
    assert out["verified_profile"] is None


def test_the_second_badge_is_refused(client):
    """The rule. The badge says *this is that particular real person* — said
    of two profiles at once it is either false of one of them, or a claim that
    one human being is two authenticated people, which is the primitive
    verification exists to deny everybody else."""
    a = make_profile(client, owner_id="owner-n", display_name="Day")
    b = make_profile(client, owner_id="owner-n", display_name="Night")

    first = client.post(f"/profiles/{a['id']}/verification",
                        json={"level": "self_asserted"}, headers=auth_header(a))
    assert first.status_code == 201

    second = client.post(f"/profiles/{b['id']}/verification",
                         json={"level": "self_asserted"}, headers=auth_header(b))
    assert second.status_code == 409
    assert "two people" in second.json()["detail"]
    assert identity.verified_profile("owner-n") == a["id"]


def test_the_badge_moves_rather_than_multiplies(client):
    """One at a time, not one forever. A rule somebody could only satisfy by
    deleting a profile is a rule they would answer by lying instead."""
    a = make_profile(client, owner_id="owner-o", display_name="Old face")
    b = make_profile(client, owner_id="owner-o", display_name="New face")
    client.post(f"/profiles/{a['id']}/verification",
                json={"level": "document", "attestor": "Notary Reyes",
                      "ref": "case-88"}, headers=auth_header(a))
    before = verification.status(a["id"])["checked_at"]

    moved = client.post(f"/profiles/{b['id']}/verification/move",
                        headers=auth_header(b)).json()
    assert moved["moved"] is True and moved["verified_profile"] == b["id"]
    assert verification.status(a["id"])["verified"] is False
    assert verification.status(b["id"])["level"] == "document"
    # And it is still one badge, not two.
    assert identity.verified_profile("owner-o") == b["id"]
    # The check itself did not become fresher by changing seats.
    assert verification.status(b["id"])["checked_at"] == before


def test_you_cannot_move_a_badge_onto_somebody_elses_profile(client):
    a = make_profile(client, owner_id="owner-p", display_name="Mine")
    b = make_profile(client, owner_id="owner-q", display_name="Theirs")
    client.post(f"/profiles/{a['id']}/verification",
                json={"level": "self_asserted"}, headers=auth_header(a))
    r = client.post(f"/profiles/{b['id']}/verification/move",
                    headers=auth_header(a))
    assert r.status_code == 403


def test_an_invented_person_never_uses_up_the_one(client):
    """`fictional` is unverifiable, not unverified — a distinction
    `verification.status` already draws. Getting it backwards here would let
    an invented character lock a real person out of their own badge."""
    made_up = make_profile(client, owner_id="owner-r", kind="fictional",
                           display_name="Captain Nobody")
    real = make_profile(client, owner_id="owner-r", display_name="Real Person")

    assert client.post(f"/profiles/{made_up['id']}/verification",
                       json={"level": "self_asserted"},
                       headers=auth_header(made_up)).status_code == 409
    assert client.post(f"/profiles/{real['id']}/verification",
                       json={"level": "self_asserted"},
                       headers=auth_header(real)).status_code == 201


def test_the_same_evidence_cannot_verify_two_accounts(client):
    """The part of "one person, one badge" that survives somebody opening a
    second account. If the same attestor vouched for the same reference, the
    two profiles are the same human however many accounts stand between."""
    a = make_profile(client, owner_id="owner-s", display_name="First")
    b = make_profile(client, owner_id="owner-t", display_name="Second")
    client.post(f"/profiles/{a['id']}/verification",
                json={"level": "document", "attestor": "Notary Reyes",
                      "ref": "passport-hash-1"}, headers=auth_header(a))
    r = client.post(f"/profiles/{b['id']}/verification",
                    json={"level": "document", "attestor": "Notary Reyes",
                          "ref": "passport-hash-1"}, headers=auth_header(b))
    assert r.status_code == 409
    assert "another account" in r.json()["detail"]


def test_self_asserted_carries_no_evidence_so_it_cannot_be_matched(client):
    """A real limit of the cross-account check, stated rather than papered
    over: there is nothing on the bottom rung that could tell two people from
    one. It is why the rung exists and why the badge carries its caveat."""
    assert identity.same_identity_elsewhere(None, None, "owner-u") is None
    assert identity.same_identity_elsewhere("Notary", None, "owner-u") is None


# -- the roster is the dangerous one -----------------------------------------

def test_the_roster_answers_only_to_the_owner(client):
    """One call links a person's profiles to each other, which is exactly how
    you strip the anonymity off all of them at once. Every anonymity promise
    in this module is worth what this check is worth — so both cases, and the
    signed-in stranger is the one that matters."""
    mine = make_profile(client, owner_id="owner-v", display_name="Mine")
    _hidden(client, owner_id="owner-v", display_name="My quiet one")
    stranger = make_profile(client, owner_id="owner-w", display_name="Nosy")

    assert client.get(f"/profiles/{mine['id']}/siblings",
                      headers=auth_header(stranger)).status_code == 403
    assert client.get(f"/profiles/{mine['id']}/siblings",
                      headers=_anon(client)).status_code == 401

    ours = client.get(f"/profiles/{mine['id']}/siblings",
                      headers=auth_header(mine)).json()
    assert {p["display_name"] for p in ours["profiles"]} == {"Mine",
                                                             "My quiet one"}


def test_no_route_takes_an_owner_id_from_the_path(client):
    """The roster is reached through a profile whose token the caller holds,
    and the account is derived from it. A route keyed on `owner_id` would hand
    the roster to anybody who learned one — and an `owner_id` is a string
    somebody chooses, not a secret."""
    from fastapi.routing import APIRoute

    from qrme.api import create_app

    def walk(routes):
        for r in routes:
            if isinstance(r, APIRoute):
                yield r
            inner = getattr(r, "original_router", None)
            if inner is not None:
                yield from walk(inner.routes)

    bad = [r.path for r in walk(create_app().routes)
           if "{owner_id}" in r.path]
    assert not bad, f"routes keyed on an owner_id: {bad}"


# -- the badge a reader sees --------------------------------------------------

def test_an_anonymous_profiles_badge_withholds_who_checked(client):
    """"Verified by Dr Okafor of St Mary's" narrows an anonymous author to a
    city and a workplace, which is most of the way to a name. The badge would
    otherwise undo the anonymity it sits beside."""
    p = _hidden(client, display_name="Wren Ashby")
    client.post(f"/profiles/{p['id']}/verification",
                json={"level": "document", "attestor": "Dr Okafor, St Mary's",
                      "ref": "case-12"}, headers=auth_header(p))

    shown = client.get(f"/profiles/{p['id']}/badge").json()
    assert shown["verified"] is True and shown["level"] == "document"
    assert shown["attestor_withheld"] is True
    assert "Okafor" not in str(shown)


def test_a_named_profiles_badge_still_names_the_attestor(client):
    """Who checked belongs in the record — the rule `signatures.enroll`
    applies. Withholding it is the anonymous case, not the general one."""
    p = make_profile(client, display_name="Public Pat")
    client.post(f"/profiles/{p['id']}/verification",
                json={"level": "document", "attestor": "Dr Okafor",
                      "ref": "case-12"}, headers=auth_header(p))
    shown = client.get(f"/profiles/{p['id']}/badge").json()
    assert shown["attestor"] == "Dr Okafor"


def test_the_badge_still_says_a_real_person_is_there(client):
    """The part worth keeping when the name is withheld, and the whole reason
    an anonymous profile would want one: the difference between a pseudonym
    and a bot."""
    p = _hidden(client)
    client.post(f"/profiles/{p['id']}/verification",
                json={"level": "in_person", "attestor": "Someone",
                      "ref": "r-1"}, headers=auth_header(p))
    shown = client.get(f"/profiles/{p['id']}/badge").json()
    assert shown["real_person"] is True and shown["verified"] is True


# -- the door ----------------------------------------------------------------

def test_the_rule_cannot_be_walked_around_by_the_http_surface(client):
    """`verification.verify` still records whatever it is given — it is the
    storage layer and knows nothing about accounts. So the check lives in
    `identity.verify`, and this asserts no route reaches past it to the one
    underneath."""
    import inspect

    from qrme.routers import friends as friends_router
    from qrme.routers import identity as identity_router

    for module in (identity_router, friends_router):
        src = inspect.getsource(module)
        assert "verification.verify(" not in src, (
            f"{module.__name__} calls the storage layer directly, which "
            "skips the one-badge rule")


def test_the_vocabulary_states_all_three_rules(client):
    out = client.get("/identity/vocabulary").json()
    joined = " ".join(out["rules"])
    assert "as many profiles" in joined
    assert "at most one" in joined
    assert "moves" in joined


# -- the silhouette -----------------------------------------------------------

def test_an_anonymous_profile_gets_the_silhouette_not_its_own_face(client):
    """A picture is the strongest identifier on a page, and the flag never
    touched it. A profile that had set a portrait of its own face went on
    serving that face while its name was being withheld."""
    from qrme import avatars

    p = _hidden(client, display_name="Wren Ashby")
    db.connect().execute("UPDATE profiles SET avatar=? WHERE id=?",
                         ("/photos/wren.webp", p["id"]))
    db.connect().commit()

    art = avatars.render(p["id"])
    assert art["asset"] == avatars.SILHOUETTE
    assert art["silhouette"] is True
    assert "wren" not in art["asset"].lower()


def test_everybody_anonymous_gets_the_same_one(client):
    """Sameness is the feature. A per-profile silhouette — tinted, initialled,
    or generated from the id — would be a stable mark following one person
    across every surface, which is what an anonymous profile is trying not to
    have. Two of them must be indistinguishable at a glance, whether or not
    they are the same person."""
    from qrme import avatars

    a = _hidden(client, owner_id="owner-sil-1", display_name="One")
    b = _hidden(client, owner_id="owner-sil-2", display_name="Two")
    c3 = _hidden(client, owner_id="owner-sil-1", display_name="Three")

    faces = {avatars.render(p["id"])["asset"] for p in (a, b, c3)}
    assert len(faces) == 1


def test_a_hidden_profile_never_falls_back_to_initials(client):
    """The other leak, and the sneakier one: no portrait meant initials drawn
    from the display name, so hiding the name produced a monogram of it."""
    from qrme import avatars

    p = _hidden(client, display_name="Wren Ashby")
    art = avatars.render(p["id"])
    assert art["placeholder"] is False
    assert art["asset"] == avatars.SILHOUETTE


def test_a_named_profile_keeps_its_own_face(client):
    """The substitution is anonymity's, not a general downgrade."""
    from qrme import avatars

    p = make_profile(client, display_name="Public Pat")
    db.connect().execute("UPDATE profiles SET avatar=? WHERE id=?",
                         ("/photos/pat.webp", p["id"]))
    db.connect().commit()
    art = avatars.render(p["id"])
    assert art["asset"] == "/photos/pat.webp"
    assert art["silhouette"] is False


def test_the_silhouette_is_not_burned_with_the_ai_mark(client):
    """It depicts nobody and nothing generated it, so stamping *AI-generated
    synthetic media* on it would be a false statement in the same direction
    the founder's photograph avoids — and it is not a photograph either. A
    third kind of asset, and `asset_is_marked` says so."""
    from qrme import avatars
    assert avatars.asset_is_marked(avatars.SILHOUETTE) is False


def test_the_silhouette_file_ships_with_the_package(client):
    """A route serving a file that is not installed is a broken image on every
    anonymous profile."""
    from qrme import avatars
    assert (avatars.figures_dir() / "silhouette.svg").is_file()


def test_the_report_says_the_picture_is_withheld_too(client):
    """It used to list the picture under what anonymity does *not* cover,
    which stopped being true the moment the silhouette landed. A limits list
    that is out of date is worse than none — people plan around it."""
    p = _hidden(client)
    out = client.get(f"/profiles/{p['id']}/anonymity",
                     headers=auth_header(p)).json()
    assert any("silhouette" in s for s in out["withheld"])
    assert not any("picture" in s for s in out["not_withheld"])
