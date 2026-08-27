"""Lending a skill to somebody in a place you are both already in.

The whole feature is the word *both*, and the tests are about the shape that
takes: two to open, one to close, nothing copied, and a log the lender can
actually read.
"""

import pytest

from qrme import exchange, sharing, watchparty
from tests.test_capabilities import auth_header, make_profile


LENDER, BORROWER, OTHER = "per_a", "per_b", "per_c"


def _offered(surface="room", surface_id="rm_1"):
    return sharing.offer(LENDER, BORROWER, surface, surface_id,
                         "pack", "pk_finance", "Finance Field Pack",
                         note="ask it anything about annuities")


# -- two to open --------------------------------------------------------------

def test_an_offer_is_not_a_grant(client):
    g = _offered()
    assert g["state"] == "offered"
    assert g["active"] is False
    with pytest.raises(sharing.SharingError):
        sharing.use(g["id"], BORROWER, "what about annuities")


def test_accepting_is_the_second_half_of_the_consent(client):
    g = _offered()
    sharing.accept(g["id"], BORROWER)
    assert sharing.get(g["id"])["active"] is True
    assert sharing.use(g["id"], BORROWER, "annuities?")["skill_ref"] == "pk_finance"


def test_only_the_person_it_was_offered_to_can_accept(client):
    """Otherwise the lender could accept on the borrower's behalf, which makes
    the second consent decorative."""
    g = _offered()
    with pytest.raises(sharing.SharingError):
        sharing.accept(g["id"], LENDER)
    with pytest.raises(sharing.SharingError):
        sharing.accept(g["id"], OTHER)


def test_a_declined_offer_does_not_become_a_grant(client):
    g = _offered()
    sharing.decline(g["id"], BORROWER)
    with pytest.raises(sharing.SharingError):
        sharing.accept(g["id"], BORROWER)


def test_you_cannot_lend_to_yourself(client):
    with pytest.raises(sharing.SharingError):
        sharing.offer(LENDER, LENDER, "room", "rm_1", "pack", "pk_x", "Mine")


# -- one to close -------------------------------------------------------------

def test_the_lender_alone_can_end_it(client):
    g = _offered()
    sharing.accept(g["id"], BORROWER)
    sharing.close(g["id"], LENDER, "changed my mind")
    assert sharing.get(g["id"])["state"] == "closed"


def test_the_borrower_alone_can_end_it_too(client):
    """Symmetric to start, asymmetric to stop. A consent model that needs both
    sides to *stop* cannot be withdrawn under pressure, which is when
    withdrawal matters."""
    g = _offered()
    sharing.accept(g["id"], BORROWER)
    sharing.close(g["id"], BORROWER)
    assert sharing.get(g["id"])["state"] == "closed"


def test_closing_stops_the_next_use_not_only_new_grants(client):
    """Checked at the moment of use rather than at the moment of grant."""
    g = _offered()
    sharing.accept(g["id"], BORROWER)
    sharing.use(g["id"], BORROWER, "first question")
    sharing.close(g["id"], LENDER)
    with pytest.raises(sharing.SharingError) as err:
        sharing.use(g["id"], BORROWER, "second question")
    assert "closed" in str(err.value)


def test_a_bystander_cannot_close_it(client):
    g = _offered()
    sharing.accept(g["id"], BORROWER)
    with pytest.raises(sharing.SharingError):
        sharing.close(g["id"], OTHER)


def test_the_record_says_who_ended_it(client):
    """"I ended it" and "they ended it" are different facts to both people."""
    g = _offered()
    sharing.accept(g["id"], BORROWER)
    sharing.close(g["id"], BORROWER, "got what I needed")
    after = sharing.get(g["id"])
    assert after["closed_by"] == BORROWER
    assert after["close_reason"] == "got what I needed"


# -- used, never handed over --------------------------------------------------

def test_nothing_is_transferred(client):
    """Packs here are bought and licensed. A lending feature that duplicated
    them would be a piracy tool with a consent dialog on the front."""
    g = _offered()
    sharing.accept(g["id"], BORROWER)
    used = sharing.use(g["id"], BORROWER, "annuities?")
    assert used["copied"] is False
    assert "nothing was installed on your account" in used["note"]
    assert sharing.get(g["id"])["transfers_anything"] is False


def test_a_borrower_cannot_use_a_grant_that_is_not_theirs(client):
    g = _offered()
    sharing.accept(g["id"], BORROWER)
    with pytest.raises(sharing.SharingError):
        sharing.use(g["id"], OTHER, "let me in")


# -- it lives in one place ----------------------------------------------------

def test_a_skill_lent_in_one_place_cannot_be_used_in_another(client):
    """Lending your expertise in a watch party does not follow the borrower
    into a private message."""
    g = _offered(surface="party", surface_id="wpt_1")
    sharing.accept(g["id"], BORROWER)
    with pytest.raises(sharing.SharingError) as err:
        sharing.use(g["id"], BORROWER, "over here", surface_id="rm_9")
    assert "cannot be used in another" in str(err.value)


def test_every_surface_can_carry_a_grant(client):
    """Rooms, lives, watch parties, connections, and an agreed piece of work —
    the same mechanism in all of them rather than five near-copies."""
    for i, surface in enumerate(sharing.SURFACES):
        g = sharing.offer(LENDER, BORROWER, surface, f"sfc_{i}",
                          "profession", "cfp", "Certified Planner")
        assert g["surface"] == surface
    with pytest.raises(sharing.SharingError):
        sharing.offer(LENDER, BORROWER, "everywhere", "x", "pack", "p", "T")


def test_ending_the_place_ends_what_was_lent_in_it(client):
    """A permission must not outlive the conversation that justified it."""
    g = _offered(surface="party", surface_id="wpt_7")
    sharing.accept(g["id"], BORROWER)
    assert sharing.close_surface("party", "wpt_7") == 1
    assert sharing.get(g["id"])["state"] == "closed"
    assert "the place it was lent in ended" in \
        sharing.get(g["id"])["close_reason"]


def test_ending_a_watch_party_closes_its_grants(client):
    """Wired at the point the party ends rather than left to a caller to
    remember — the thing forgotten would be a live permission."""
    me = make_profile(client, display_name="Poster")
    post = client.post(f"/profiles/{me['id']}/wall",
                       json={"body": "Look.",
                             "video_url": "https://youtu.be/dQw4w9WgXcQ"},
                       headers=auth_header(me)).json()
    party = watchparty.start(post["id"], LENDER)
    g = sharing.offer(LENDER, BORROWER, "party", party["id"], "pack",
                      "pk_finance", "Finance Field Pack")
    sharing.accept(g["id"], BORROWER)

    ended = watchparty.end(party["id"], LENDER)
    assert ended["grants_closed"] == 1
    assert sharing.get(g["id"])["state"] == "closed"


def test_withdrawing_an_exchange_closes_its_grants(client):
    """Walking away from the agreement while the other side still holds your
    skill is the half-withdrawal nobody means."""
    x = exchange.propose(LENDER, BORROWER, "Build it", "software")
    g = sharing.offer(LENDER, BORROWER, "exchange", x["id"], "workflow",
                      "wf_review", "The review workflow")
    sharing.accept(g["id"], BORROWER)
    exchange.withdraw(x["id"], LENDER)
    assert sharing.get(g["id"])["state"] == "closed"


# -- the lender can see what was done -----------------------------------------

def test_every_use_is_written_down(client):
    """"Both parties choose" is a slogan unless the lender can see what was
    done with it."""
    g = _offered()
    sharing.accept(g["id"], BORROWER)
    sharing.use(g["id"], BORROWER, "annuity for a 62-year-old")
    sharing.use(g["id"], BORROWER, "rollover rules")
    log = sharing.uses(g["id"])
    assert [u["what"] for u in log] == ["rollover rules",
                                        "annuity for a 62-year-old"]
    assert sharing.get(g["id"])["used_count"] == 2


def test_a_room_can_see_what_is_lent_inside_it(client):
    g = _offered(surface="room", surface_id="rm_44")
    sharing.accept(g["id"], BORROWER)
    inside = sharing.in_surface("room", "rm_44")
    assert [x["id"] for x in inside] == [g["id"]]


def test_a_person_sees_both_sides_of_their_lending(client):
    a = _offered()
    b = sharing.offer(BORROWER, LENDER, "room", "rm_2", "language",
                      "en-pt", "English ⟷ Portuguese")
    mine = sharing.for_person(LENDER)
    assert [x["id"] for x in mine["lending"]] == [a["id"]]
    assert [x["id"] for x in mine["borrowing"]] == [b["id"]]


def test_the_route_publishes_its_own_terms(client):
    r = client.get("/skill-grants/vocabulary").json()
    assert "two people open a grant; either one alone closes it" in r["ground_rules"]
    assert {s["key"] for s in r["surfaces"]} == set(sharing.SURFACES)
