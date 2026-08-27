"""The audience layer: like, comment, share, subscribe.

Three properties get most of the attention here, because each is the one the
obvious implementation gets wrong:

* a like is a fact about a person, not a counter anyone can pump;
* a comment is authored text and goes through the same filter as a chat turn,
  with a blocked one visible to its author and nobody else;
* a rated target stays rated on every verb, not just the ones someone
  remembered.
"""


def _profile(client, **over):
    body = {"owner_id": "o1", "kind": "fictional", "display_name": "Rosa Vance",
            "persona": "A gardener who remembers every plot she planted.",
            "verification": {"birthdate": "1980-01-01",
                             "id_document": "passport",
                             "liveness_check": True}}
    body.update(over)
    return client.post("/profiles", json=body).json()


def _viewer(client, name="Ada", birthdate="1990-05-05"):
    made = client.post("/interactors", json={
        "display_name": name, "birthdate": birthdate, "verified": True}).json()
    return {"authorization": f"Bearer {made['token']}"}


def _rated_desk(client):
    return client.post("/desks", json={
        "owner_id": "perf", "display_name": "Vivienne Marlowe",
        "trade": "Performer", "attestor": "perf", "basis": "self, verified",
        "rated": True, "view_style": "stage"}).json()


# --- like -----------------------------------------------------------------

def test_liking_twice_is_still_one_like(client):
    """A counter column would let one account manufacture popularity by
    calling an endpoint in a loop, which makes every number meaningless
    rather than just this one."""
    prof = _profile(client)
    who = _viewer(client)

    first = client.post(f"/profiles/{prof['id']}/like", headers=who).json()
    assert first["likes"] == 1 and first["was_already_liked"] is False
    second = client.post(f"/profiles/{prof['id']}/like", headers=who).json()
    assert second["likes"] == 1 and second["was_already_liked"] is True


def test_two_people_are_two_likes(client):
    prof = _profile(client)
    client.post(f"/profiles/{prof['id']}/like", headers=_viewer(client, "Ada"))
    out = client.post(f"/profiles/{prof['id']}/like",
                      headers=_viewer(client, "Bo", "1991-02-02")).json()
    assert out["likes"] == 2


def test_a_like_can_be_taken_back(client):
    prof = _profile(client)
    who = _viewer(client)
    client.post(f"/profiles/{prof['id']}/like", headers=who)
    out = client.request("DELETE", f"/profiles/{prof['id']}/like", headers=who)
    assert out.json() == {"target_kind": "profile", "target_id": prof["id"],
                          "liked": False, "likes": 0}


def test_a_like_needs_a_liker(client):
    """The whole reason a like is stored per-person is that there is a person."""
    prof = _profile(client)
    assert client.post(f"/profiles/{prof['id']}/like").status_code == 401


def test_liking_something_that_does_not_exist_is_404(client):
    who = _viewer(client)
    assert client.post("/profiles/prf_nope/like",
                       headers=who).status_code == 404
    # An unknown resource kind is a missing route, not a bad body.
    assert client.post("/widgets/x/like", headers=who).status_code == 404


# --- comment --------------------------------------------------------------

def test_a_comment_goes_through_the_same_filter_as_a_chat_turn(client):
    """A comment box that skipped moderation would be the one unfiltered
    surface on the platform, and it would be found within a day."""
    prof = _profile(client)
    who = _viewer(client)

    out = client.post(f"/profiles/{prof['id']}/comments",
                      json={"body": "my ssn is 123-45-6789"},
                      headers=who).json()
    assert out["status"] == "blocked"
    assert out["visible"] is False
    assert out["flag_reason"]


def test_a_blocked_comment_is_visible_to_its_author_and_nobody_else(client):
    """An author who cannot see that their comment was held has no way to tell
    moderation from a bug, and will simply post it again."""
    prof = _profile(client)
    author = _viewer(client, "Ada")
    other = _viewer(client, "Bo", "1991-02-02")
    client.post(f"/profiles/{prof['id']}/comments",
                json={"body": "my ssn is 123-45-6789"}, headers=author)

    mine = client.get(f"/profiles/{prof['id']}/comments", headers=author)
    assert [c["status"] for c in mine.json()["comments"]] == ["blocked"]
    theirs = client.get(f"/profiles/{prof['id']}/comments", headers=other)
    assert theirs.json()["comments"] == []
    assert client.get(f"/profiles/{prof['id']}/comments").json()["comments"] == []


def test_a_blocked_comment_is_not_counted(client):
    prof = _profile(client)
    client.post(f"/profiles/{prof['id']}/comments",
                json={"body": "my ssn is 123-45-6789"},
                headers=_viewer(client, "Ada"))
    counts = client.get(f"/profiles/{prof['id']}/audience").json()
    assert counts["comments_count"] == 0


def test_you_can_withdraw_your_own_comment_only(client):
    prof = _profile(client)
    author = _viewer(client, "Ada")
    other = _viewer(client, "Bo", "1991-02-02")
    made = client.post(f"/profiles/{prof['id']}/comments",
                       json={"body": "Lovely garden"}, headers=author).json()

    assert client.request("DELETE", f"/comments/{made['id']}",
                          headers=other).status_code == 403
    assert client.request("DELETE", f"/comments/{made['id']}",
                          headers=author).status_code == 200


def test_an_empty_comment_is_refused(client):
    prof = _profile(client)
    assert client.post(f"/profiles/{prof['id']}/comments", json={"body": "   "},
                       headers=_viewer(client)).status_code == 422


# --- share ----------------------------------------------------------------

def test_a_stranger_can_share_without_an_account(client):
    """Someone who scanned a sticker is the person most likely to pass it on,
    and has no account."""
    prof = _profile(client)
    out = client.post(f"/profiles/{prof['id']}/share", json={})
    assert out.status_code == 201
    assert out.json()["url"] == f"/summon?ref={prof['id']}"
    assert out.json()["shares"] == 1


def test_sharing_a_rated_target_is_allowed_because_the_gate_is_at_the_far_end(
        client):
    """Refusing the sharer would be gate theatre — the link they would have
    sent lands on the age wall regardless of who sent it."""
    desk = _rated_desk(client)
    out = client.post(f"/desks/{desk['desk_id']}/share", json={})
    assert out.status_code == 201
    assert out.json()["url"] == f"/desks/{desk['desk_id']}"
    # And the destination is what actually refuses.
    assert client.get(f"/desks/{desk['desk_id']}").json()["age_wall"] is True


def test_shares_record_who_when_there_is_a_who(client):
    """"Shared 40 times" and "shared 40 times by one account" are different
    facts, and only one of them is worth anything."""
    prof = _profile(client)
    client.post(f"/profiles/{prof['id']}/share", json={},
                headers=_viewer(client))
    client.post(f"/profiles/{prof['id']}/share", json={})
    from qrme import db
    rows = db.connect().execute(
        "SELECT actor_id FROM shares WHERE target_id=?", (prof["id"],)
    ).fetchall()
    assert sorted(r["actor_id"] is None for r in rows) == [False, True]


# --- subscribe ------------------------------------------------------------

def test_a_free_follow_costs_nothing_and_credits_nobody(client):
    prof = _profile(client)
    out = client.post(f"/profiles/{prof['id']}/subscribe",
                      json={"tier": "follow"}, headers=_viewer(client)).json()
    assert out["tier"] == "follow" and out["price"] == 0
    assert out["periods"] == 0
    assert "charged" not in out


def test_a_paid_subscription_needs_the_price_confirmed(client):
    """A subscription a viewer did not mean to start keeps costing them, which
    is strictly worse than a single purchase they did not mean to make."""
    prof = _profile(client)
    who = _viewer(client)
    base = {"tier": "paid", "price": 5.0, "beneficiary": "o1"}

    assert client.post(f"/profiles/{prof['id']}/subscribe", json=base,
                       headers=who).status_code == 422
    wrong = dict(base, accept_price=1.0)
    assert client.post(f"/profiles/{prof['id']}/subscribe", json=wrong,
                       headers=who).status_code == 422
    right = dict(base, accept_price=5.0)
    assert client.post(f"/profiles/{prof['id']}/subscribe", json=right,
                       headers=who).status_code == 201


def test_a_paid_subscription_lands_on_the_creators_statement(client):
    """Simulated billing, but a real row on the same statement as pack sales
    and licence fees, settling through the same payout sweep."""
    prof = _profile(client)
    client.post(f"/profiles/{prof['id']}/subscribe",
                json={"tier": "paid", "price": 5.0, "beneficiary": "o1",
                      "accept_price": 5.0}, headers=_viewer(client))

    owner = {"authorization": f"Bearer {prof['owner_token']}"}
    earnings = client.get(f"/profiles/{prof['id']}/earnings",
                          headers=owner).json()
    assert earnings["totals"]["by_kind"]["subscription"] == 5.0
    assert earnings["totals"]["accrued"] == 5.0


def test_a_paid_subscription_must_credit_someone(client):
    prof = _profile(client)
    out = client.post(f"/profiles/{prof['id']}/subscribe",
                      json={"tier": "paid", "price": 5.0, "accept_price": 5.0},
                      headers=_viewer(client))
    assert out.status_code == 422
    assert "beneficiary" in out.json()["detail"]


def test_a_free_tier_priced_above_zero_is_refused(client):
    prof = _profile(client)
    out = client.post(f"/profiles/{prof['id']}/subscribe",
                      json={"tier": "paid", "price": 0.0, "beneficiary": "o1",
                            "accept_price": 0.0}, headers=_viewer(client))
    assert out.status_code == 422


def test_renewing_charges_the_next_period_and_nothing_charges_on_a_timer(
        client):
    """Explicit renewal: a deployment left running does not accrue charges
    nobody authorised and nobody saw."""
    prof = _profile(client)
    who = _viewer(client)
    sub = client.post(f"/profiles/{prof['id']}/subscribe",
                      json={"tier": "paid", "price": 5.0, "beneficiary": "o1",
                            "accept_price": 5.0}, headers=who).json()
    assert sub["periods"] == 1

    again = client.post(f"/subscriptions/{sub['id']}/renew",
                        json={"beneficiary": "o1"}, headers=who).json()
    assert again["periods"] == 2
    owner = {"authorization": f"Bearer {prof['owner_token']}"}
    assert client.get(f"/profiles/{prof['id']}/earnings",
                      headers=owner).json()["totals"]["accrued"] == 10.0


def test_a_cancelled_subscription_keeps_its_row_and_stops_renewing(client):
    """A lapsed subscriber stays distinguishable from someone who was never
    there — and nothing further is charged."""
    prof = _profile(client)
    who = _viewer(client)
    sub = client.post(f"/profiles/{prof['id']}/subscribe",
                      json={"tier": "paid", "price": 5.0, "beneficiary": "o1",
                            "accept_price": 5.0}, headers=who).json()
    cancelled = client.request("DELETE", f"/profiles/{prof['id']}/subscribe",
                               headers=who).json()
    assert cancelled["status"] == "cancelled"
    assert cancelled["periods"] == 1

    refused = client.post(f"/subscriptions/{sub['id']}/renew",
                          json={"beneficiary": "o1"}, headers=who)
    assert refused.status_code == 422
    assert client.get(f"/profiles/{prof['id']}/subscribers").json()[
        "subscribers"] == []


def test_resubscribing_reuses_the_same_row(client):
    prof = _profile(client)
    who = _viewer(client)
    first = client.post(f"/profiles/{prof['id']}/subscribe",
                        json={"tier": "follow"}, headers=who).json()
    client.request("DELETE", f"/profiles/{prof['id']}/subscribe", headers=who)
    again = client.post(f"/profiles/{prof['id']}/subscribe",
                        json={"tier": "follow"}, headers=who).json()
    assert again["id"] == first["id"]
    assert again["status"] == "active" and again["cancelled_at"] is None


def test_a_message_cannot_be_subscribed_to(client):
    """Subscribing means "tell me when there is more from them", and a message
    does not produce more."""
    prof = _profile(client)
    out = client.post(f"/messages/{prof['id']}/subscribe",
                      json={"tier": "follow"}, headers=_viewer(client))
    assert out.status_code == 422
    assert "subscribe" in out.json()["detail"]


def test_a_subscription_says_its_billing_is_simulated(client):
    """Implying a payment processor that does not exist is the kind of claim
    that gets believed."""
    prof = _profile(client)
    out = client.post(f"/profiles/{prof['id']}/subscribe",
                      json={"tier": "follow"}, headers=_viewer(client)).json()
    assert "simulated" in out["billing"]


# --- the rated gate, on every verb ---------------------------------------

def test_every_verb_on_a_rated_desk_needs_a_verified_adult(client):
    """Checked as a set rather than one endpoint at a time: a gate that was
    remembered on three of four surfaces is the one that gets found."""
    desk = _rated_desk(client)
    did = desk["desk_id"]
    minor = _viewer(client, "Kid", "2015-01-01")
    adult = _viewer(client, "Ada", "1990-01-01")

    for call in (
            lambda h: client.post(f"/desks/{did}/like", headers=h),
            lambda h: client.post(f"/desks/{did}/comments",
                                  json={"body": "hi"}, headers=h),
            lambda h: client.post(f"/desks/{did}/subscribe",
                                  json={"tier": "follow"}, headers=h),
            lambda h: client.get(f"/desks/{did}/audience", headers=h),
            lambda h: client.get(f"/desks/{did}/comments", headers=h)):
        assert call(None).status_code == 403, "no token must not pass"
        assert call(minor).status_code == 403, "a minor must not pass"
        assert call(adult).status_code in (200, 201), "an adult must pass"


# --- the numbers under the buttons ---------------------------------------

def test_the_audience_call_answers_everything_a_client_renders(client):
    """One request, because a client rendering four buttons should not need
    four round trips to know their state."""
    prof = _profile(client)
    who = _viewer(client)
    client.post(f"/profiles/{prof['id']}/like", headers=who)
    client.post(f"/profiles/{prof['id']}/comments", json={"body": "Lovely"},
                headers=who)
    client.post(f"/profiles/{prof['id']}/share", json={}, headers=who)
    client.post(f"/profiles/{prof['id']}/subscribe", json={"tier": "follow"},
                headers=who)

    out = client.get(f"/profiles/{prof['id']}/audience", headers=who).json()
    assert out == {"likes": 1, "comments_count": 1, "shares": 1,
                   "subscribers_count": 1,
                   "you_liked": True, "your_subscription": "follow"}


def test_the_audience_call_is_public_but_personal_state_needs_a_token(client):
    prof = _profile(client)
    client.post(f"/profiles/{prof['id']}/like", headers=_viewer(client))
    anon = client.get(f"/profiles/{prof['id']}/audience").json()
    assert anon["likes"] == 1
    assert "you_liked" not in anon
