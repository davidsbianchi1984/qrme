"""One named thing, and who may ask about it.

Six reads that each answer about one particular thing, and six different
answers to *who is allowed*:

| | who may ask |
|---|---|
| the light legend | anybody; it takes no id at all |
| a campaign | **anybody**, deliberately |
| an organization | signed in |
| an excursion | the profile's owner |
| somebody's lent skills | themselves |
| a place's lent skills | you, filtered to your own |

**The campaign is the inversion, and it is the point.** It is the most public
read in this product, and that is what makes it honest: it carries
`proceeds_to`, so the person about to give money sees exactly who receives it
*before* they do. A fundraising page that hid its split would be the ordinary
kind of dishonest. In the same spirit a campaign cannot exist before the
designation does — creating one first is refused with *say where the money
goes first — designate loved ones or organizations before asking anyone for
it*.

Two reads are narrower than their names suggest, and both say so rather than
letting a screen misread them:

* an **excursion** carries the brief that was sanitised before it left and the
  count of what was stripped out. Owner-only, because those two numbers are
  the whole basis on which the feature asks to be trusted;
* a **place's** lent skills are filtered to the caller's own, with a `note`
  explaining that a room-wide view needs a membership check that does not
  exist yet. A short list there means *your* grants, not *no* grants, and a
  screen reading it the other way turns an access limit into an empty room.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


def _memorial(client, account="acct_named"):
    p = client.post("/profiles", json={
        "owner_id": account, "kind": "fictional", "display_name": "Rosa",
        "purpose": "legacy_memorial", "persona": "warm",
        "verification": {"birthdate": "1990-01-01"}}).json()
    head = {"authorization": f"Bearer {p['owner_token']}"}
    client.post(f"/memberships/{account}", json={"plan": "pro"}, headers=head)
    return p, head


def _designate(client, p, head, share=100):
    return client.put(f"/profiles/{p['id']}/proceeds", headers=head, json={
        "designees": [{"kind": "loved_one", "name": "Her daughter",
                       "share": share}]})


# --- the legend -------------------------------------------------------------

def test_the_legend_is_built_from_the_mapping(client):
    """Not written out beside it. A legend kept separately eventually
    describes a mapping the code does not have, and it is the legend people
    trust — so the statuses come back with each light."""
    from qrme import agentlight

    view = client.get("/agent/lights").json()
    assert view["order"] == list(agentlight.ORDER)
    driving = {s for row in view["legend"] for s in row["statuses"]}
    assert driving, "the legend names no statuses, so it explains nothing"
    for row in view["legend"]:
        assert row["labels"] and row["statuses"]


def test_the_legend_needs_no_token_and_no_id(client):
    assert client.get("/agent/lights").status_code == 200


# --- the campaign -----------------------------------------------------------

def test_a_campaign_cannot_exist_before_the_designation(client):
    """You may not ask anybody for money before saying where it goes."""
    p, head = _memorial(client, "acct_first")
    r = client.post(f"/profiles/{p['id']}/campaigns", headers=head,
                    json={"title": "A bench", "goal": 2000})
    assert r.status_code == 422
    assert "where the money goes first" in r.json()["detail"]


def test_a_campaign_is_readable_by_anybody(client):
    """The most public read in the product, on purpose."""
    p, head = _memorial(client, "acct_public")
    _designate(client, p, head)
    c = client.post(f"/profiles/{p['id']}/campaigns", headers=head,
                    json={"title": "A bench", "goal": 500}).json()
    assert client.get(f"/campaigns/{c['id']}").status_code == 200


def test_the_split_travels_with_the_campaign(client):
    """The reason it is public. Somebody about to give money is entitled to
    see who receives it, on the same card, before they give it."""
    p, head = _memorial(client, "acct_split")
    _designate(client, p, head)
    c = client.post(f"/profiles/{p['id']}/campaigns", headers=head,
                    json={"title": "A bench", "goal": 500}).json()
    view = client.get(f"/campaigns/{c['id']}").json()
    assert view["proceeds_to"], "a fundraising page with no visible split"
    assert view["proceeds_to"][0]["share"] == 100
    assert "simulat" in view["payment"].lower()


def test_the_screen_renders_the_split_and_the_simulated_note():
    src = _markup("app/src/screens/Named.tsx")
    assert "campaign.proceeds_to" in src
    assert "campaign.payment" in src, (
        "a figure is shown without the sentence saying the money is simulated")


def test_a_missing_campaign_says_so_rather_than_hiding(client):
    r = client.get("/campaigns/cmp_nothing")
    assert r.status_code == 404


# --- the narrower reads -----------------------------------------------------

def test_an_excursion_is_the_owners_alone(client):
    p, head = _memorial(client, "acct_exc")
    x = client.post(f"/profiles/{p['id']}/excursions", headers=head, json={
        "topic": "local parks", "question": "which are accessible",
        "private": ["4 Mill Lane"]}).json()
    assert client.get(f"/excursions/{x['id']}", headers=head).status_code == 200
    assert client.get(f"/excursions/{x['id']}").status_code == 401


def test_an_excursion_reports_both_numbers(client):
    """`left_host` and `redactions`. Either alone is misleading: *nothing
    left*, or *something left with this much taken out of it first*."""
    p, head = _memorial(client, "acct_two")
    x = client.post(f"/profiles/{p['id']}/excursions", headers=head, json={
        "topic": "parks", "question": "accessible?",
        "private": ["4 Mill Lane"]}).json()
    view = client.get(f"/excursions/{x['id']}", headers=head).json()
    assert "left_host" in view and "redactions" in view
    assert isinstance(view["redactions"], int)


def test_the_screen_shows_both_together():
    src = _markup("app/src/screens/Named.tsx")
    assert "excursion.left_host" in src and "excursion.redactions" in src


def test_a_persons_grants_are_theirs_alone(client):
    r = client.get("/people/usr_somebody/skill-grants")
    assert r.status_code == 401
    assert "on somebody's behalf" in r.json()["detail"]


def test_a_places_grants_are_filtered_to_the_caller(client):
    """It was meant to answer what a room can see about itself. With no
    membership check to hang that on it listed who is lending what to whom to
    anybody who guessed an id, so it is the caller's own until there is one."""
    fan = client.post("/interactors", json={"display_name": "Ana"}).json()
    r = client.get("/surfaces/room/room_x/skill-grants",
                   headers={"authorization": f"Bearer {fan['token']}"})
    assert r.status_code == 200
    assert r.json()["grants"] == []
    assert "your own grants" in r.json()["note"]


def test_that_note_is_rendered_rather_than_summarised():
    """Without it a short list reads as an empty room instead of an access
    limit, which is a different and much more reassuring claim."""
    assert "place.note" in _markup("app/src/screens/Named.tsx")


def test_an_unknown_surface_is_a_404_not_an_empty_list(client):
    fan = client.post("/interactors", json={"display_name": "Ana"}).json()
    r = client.get("/surfaces/nowhere/x/skill-grants",
                   headers={"authorization": f"Bearer {fan['token']}"})
    assert r.status_code == 404


def test_an_organization_needs_somebody_signed_in(client):
    p, head = _memorial(client, "acct_org")
    org = client.post("/organizations", headers=head, json={
        "name": "Vale Clinic", "kind": "clinic",
        "owner_id": "acct_org"}).json()
    assert client.get(f"/organizations/{org['id']}").status_code == 401
    assert client.get(f"/organizations/{org['id']}",
                      headers=head).status_code == 200


def test_the_six_do_not_all_answer_the_same_way(client):
    """The point of the round, asserted in one place. If these ever collapse
    to one policy that should be a decision, not a drift."""
    p, head = _memorial(client, "acct_six")
    _designate(client, p, head)
    c = client.post(f"/profiles/{p['id']}/campaigns", headers=head,
                    json={"title": "A bench", "goal": 500}).json()
    org = client.post("/organizations", headers=head, json={
        "name": "V", "kind": "clinic", "owner_id": "acct_six"}).json()

    tokenless = {
        "lights": client.get("/agent/lights").status_code,
        "campaign": client.get(f"/campaigns/{c['id']}").status_code,
        "organization": client.get(f"/organizations/{org['id']}").status_code,
        "person_grants": client.get(
            "/people/usr_x/skill-grants").status_code,
    }
    assert tokenless == {"lights": 200, "campaign": 200,
                         "organization": 401, "person_grants": 401}


# --- the console half -------------------------------------------------------

def _src(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def _markup(rel: str) -> str:
    s = re.sub(r"/\*.*?\*/", "", _src(rel), flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


def test_the_screen_exists():
    assert (REPO / "app/src/screens/Named.tsx").exists()


@pytest.mark.parametrize("binding", [
    "api.agentLights(", "api.campaign(", "api.organization(",
    "api.excursion(", "api.grantsForPerson(", "api.grantsInPlace(",
])
def test_the_screen_calls_it(binding):
    assert binding in _src("app/src/screens/Named.tsx")


def test_the_campaign_lookup_sends_no_token():
    """Reading one is public, and a console that required a token to render
    a fundraising page would be closing the door the backend left open."""
    import sys

    sys.path.insert(0, str(REPO / "tests"))
    import clientpaths as cp

    src = _src("app/src/screens/Named.tsx")
    start = src.index("api.campaign(") + len("api.campaign")
    assert "token" not in cp._call_body(src, start)
