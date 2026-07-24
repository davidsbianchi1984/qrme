"""Help us improve: product feedback anyone can send; submitters see their
own plus the public tally, never anyone else's words."""


def test_anyone_can_submit_and_it_tallies(client):
    r = client.post("/feedback", json={
        "category": "idea", "message": "add a dark mode toggle", "rating": 5})
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "received"

    client.post("/feedback", json={"category": "bug",
                                   "message": "chat scroll jumps"})
    tally = client.get("/feedback").json()["tally"]
    assert tally["idea"] == 1 and tally["bug"] == 1
    assert client.get("/feedback").json()["total"] == 2


def test_bad_category_and_rating_and_message_refused(client):
    assert client.post("/feedback", json={
        "category": "rant", "message": "x"}).status_code == 422
    assert client.post("/feedback", json={
        "category": "idea", "message": "  "}).status_code == 422
    assert client.post("/feedback", json={
        "category": "idea", "message": "x", "rating": 9}).status_code == 422


def test_authenticated_submitter_sees_only_their_own(client, profile_id):
    # profile_id fixture authenticates the client as an owner.
    client.post("/feedback", json={"category": "improvement",
                                   "message": "faster compose"})
    mine = client.get("/feedback").json()["mine"]
    assert len(mine) == 1 and mine[0]["category"] == "improvement"

    # An anonymous caller sees the tally but no per-user list.
    anon = client.get("/feedback", headers={"authorization": ""}).json()
    assert anon["mine"] == []
    assert anon["tally"]["improvement"] >= 1


def test_two_users_dont_see_each_others_words(client):
    a = client.post("/interactors", json={"display_name": "A",
                                          "birthdate": "1990-01-01"}).json()
    b = client.post("/interactors", json={"display_name": "B",
                                          "birthdate": "1991-01-01"}).json()
    client.post("/feedback", json={"category": "idea", "message": "A's idea"},
                headers={"authorization": f"Bearer {a['token']}"})
    client.post("/feedback", json={"category": "idea", "message": "B's idea"},
                headers={"authorization": f"Bearer {b['token']}"})
    b_view = client.get("/feedback",
                        headers={"authorization": f"Bearer {b['token']}"}).json()
    msgs = [m["message"] for m in b_view["mine"]]
    assert msgs == ["B's idea"]
    assert b_view["tally"]["idea"] == 2          # tally counts both
