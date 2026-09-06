"""Eyes, ears, hands and a body, fitted without leaving the seat.

    asked     add the robotics from inside the builder
    mattered  and the eyes, the ears and the body with them, in an
              order where each one leads into the next until you hire
              and seat your new hire

Every one of the four doors this walks already worked. What did not
work was reaching them: a screen was placed from the employee file, a
speaker was added in the Workshop, a robot was bound on the settings
shelf, and a face was claimed in the studio. Kitting out a new hire
began by walking out of the hire.

The ladder puts all four inside the seat, and that forces an ordering
the console cannot choose its way around: **a seat has no profile until
it is signed**, so none of the four fittings can be pressed while the
founder is standing there choosing them. The choices are held and the
signature is what fits them.

Which is the thing worth a test rather than a screenshot. Signing and
fitting are two acts, the second happens after the first has already
stood, and a fitting that fails must not come back looking like a hire
that failed — the person is hired, they are in the seat, and one piece
of equipment did not go on. Nothing about that is visible from the
console's own code, so it is asserted here against the real doors.
"""

from __future__ import annotations

import io
import os

from qrme import avatarreg
from tests.test_where_do_i_find_my_owner_token import _account, _auth


def _png(color=(40, 90, 200)) -> bytes:
    from PIL import Image
    out = io.BytesIO()
    Image.new("RGB", (256, 256), color).save(out, format="PNG")
    return out.getvalue()


HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDER = os.path.join(HERE, "app", "src", "screens", "Companies.tsx")

#: An interview thin enough to be refused is three answers short of a
#: hire — `company.hire` requires the name, the duties and the authority.
CHARTER = [
    {"question": "Full name:", "answer": "June Okafor"},
    {"question": "Duties:",
     "answer": "Take orders, box pastries, ring up sales."},
    {"question": "Decides alone vs escalates:",
     "answer": "Decides substitutions; escalates refunds."},
]


def _hired_seat(client, monkeypatch):
    """A founder, a company, a seat, and somebody signed into it.

    Returns the company, the seat, the founder's own key, the hired
    profile, and an owner key minted for it — everything the console
    holds at the moment the last rung of the ladder is pressed.
    """
    me = _account(client, monkeypatch, "founder@example.test")
    r = client.post("/profiles", json={
        "owner_id": me["account_id"], "kind": "self",
        "display_name": "David",
        "persona": "Runs a bakery and is opening a second one.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"})
    assert r.status_code == 201, r.text
    founder = r.json()

    co = client.post("/companies",
                     json={"name": "Bianchi & Sons Bakery",
                           "industry": "bakery", "headcount": 4},
                     headers=_auth(founder["owner_token"])).json()
    seat = client.post(f"/companies/{co['id']}/seats",
                       json={"title": "Counter clerk",
                             "department": "Front of house"},
                       headers=_auth(founder["owner_token"])).json()
    r = client.post(f"/companies/{co['id']}/seats/{seat['id']}/hire",
                    json={"answers": CHARTER},
                    headers=_auth(founder["owner_token"]))
    assert r.status_code in (200, 201), r.text
    hired = r.json()

    # The key the console mints on the last rung. The hire hands back a
    # profile id and no credential, which is correct — a hire is not a
    # grant — so the ladder goes and asks the account for one.
    r = client.post(
        f"/accounts/{me['account_id']}/profiles/{hired['profile_id']}"
        "/owner-token", headers=_auth(me["account_token"]))
    assert r.status_code in (200, 201), r.text
    return (co, seat, founder["owner_token"], hired,
            r.json()["owner_token"])


def test_all_four_fittings_land_on_a_seat_signed_a_moment_ago(
        client, monkeypatch):
    """The whole ladder, in the order it is walked."""
    _, _, _, hired, key = _hired_seat(client, monkeypatch)
    pid = hired["profile_id"]

    eyes = client.post(f"/profiles/{pid}/displays",
                       json={"kind": "counter_screen",
                             "label": "The front counter"},
                       headers=_auth(key))
    assert eyes.status_code in (200, 201), eyes.text

    ears = client.post(f"/profiles/{pid}/embodiments",
                       json={"name": "Front of house speaker",
                             "kind": "speaker", "has_llm": False},
                       headers=_auth(key))
    assert ears.status_code in (200, 201), ears.text

    hands = client.post(f"/profiles/{pid}/robots",
                        json={"model": "digit", "name": "Digit"},
                        headers=_auth(key))
    assert hands.status_code in (200, 201), hands.text

    face = avatarreg.mint(data=_png(), source="curated_library",
                          likeness="invented")
    body = client.post(f"/profiles/{pid}/avatar/claim",
                       json={"registry_id": face["id"]},
                       headers=_auth(key))
    assert body.status_code in (200, 201), body.text

    # And they are all on the same person. A robot is an embodiment like
    # any other — see `qrme/routers/robots.py` — so the speaker and the
    # machine come back from one list.
    forms = client.get(f"/profiles/{pid}/embodiments",
                       headers=_auth(key)).json()
    assert {f["kind"] for f in forms} >= {"speaker"}
    assert any(f["kind"] in ("robot", "humanoid") for f in forms), forms
    screens = client.get(f"/profiles/{pid}/displays",
                         headers=_auth(key)).json()["displays"]
    assert [d["label"] for d in screens] == ["The front counter"]


def test_a_fitting_that_fails_does_not_unhire_anybody(client, monkeypatch):
    """The consequence of signing first.

    The hire has already stood by the time any of this runs. A refused
    fitting is one piece of equipment that did not go on, and the seat
    stays filled — which is why the ladder reports the pieces it could
    not fit *by name* rather than raising a failure over the hire.
    """
    co, seat, founder_key, hired, key = _hired_seat(
        client, monkeypatch)
    pid = hired["profile_id"]

    # The body rung's *painted* road is the real example, not a
    # contrived one: it needs an image service, and a deployment with no
    # image key refuses it with a 503 that says exactly that. On such a
    # host the founder walks the whole ladder, signs, and the face is
    # the one piece that does not go on.
    painted = client.post(f"/profiles/{pid}/avatar/painted",
                          json={"direction": "a woman in a baker's apron"},
                          headers=_auth(key))
    assert painted.status_code >= 400, painted.text

    # Still hired, still seated. Read with the founder's key, not the
    # employee's: the roster is the founder's, and asking with the wrong
    # one would answer 403 and turn this assertion into a check that
    # never runs.
    roster = client.get(f"/companies/{co['id']}",
                        headers=_auth(founder_key))
    assert roster.status_code == 200, roster.text
    row = next(x for x in roster.json()["seats"] if x["id"] == seat["id"])
    assert row["status"] == "hired"
    assert row["profile_id"] == pid

    # And the rungs after the failed one still land.
    ok = client.post(f"/profiles/{pid}/embodiments",
                     json={"name": "Front of house speaker",
                           "kind": "speaker", "has_llm": False},
                     headers=_auth(key))
    assert ok.status_code in (200, 201), ok.text


def test_the_builder_reaches_all_four_without_leaving_the_seat():
    """The regression that would put the founder back out in settings.

    This is a source assertion on purpose. The bug it guards against is
    not a wrong answer from a door — it is a door being reached from
    somewhere else, which no request can see.
    """
    with open(BUILDER, encoding="utf-8") as fh:
        src = fh.read()
    for door in ("api.placeDisplay(", "api.addEmbodiment(",
                 "api.bindRobot(", "api.claimFace(", "api.paintFace("):
        assert door in src, (
            f"{door} is not in the Company Builder, so that half of the "
            "kit is somewhere the founder has to walk to")
    # And in order. A ladder whose rungs are declared out of order is a
    # wall of forms with a list on top of it.
    assert 'const RUNGS = ["eyes", "ears", "hands", "body"] as const;' in src
