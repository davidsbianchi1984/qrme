"""The agent asks people, not just pages — and the people learn nothing.

An excursion asks a model and gets back what is already written down. An
inquiry asks *people*, because the thing a person two streets over knows was
never written down anywhere. Somebody with no account answers it, the owner
folds the answer into the profile, and the offline model ends up knowing
something it could not have looked up.

    asked     can the agent look it up
    mattered  can the agent ask somebody who knows, without telling them who

The second half is what the guards here are about. Every route on the
stranger's side is checked twice: once for what it actually returns, and once
structurally, so a field added to the owner's view later cannot quietly appear
on the board.
"""

import ast
import inspect
from pathlib import Path

from qrme import inquiries

ROUTER = Path(__file__).resolve().parent.parent / "qrme" / "routers" / "inquiries.py"

# The fields an outsider may ever see. This tuple is the contract; the guards
# below compare against it rather than against a list written out again here,
# so widening the contract is a one-line change somebody has to mean.
PUBLIC = set(inquiries.PUBLIC_FIELDS)

# What must never reach them, spelled out because a regression here is silent:
# the response still parses, the screen still renders, and somebody's name is
# in it.
OWNER_ONLY = {"profile_id", "topic", "question", "redactions"}


def _interactor(client):
    r = client.post("/interactors", json={"display_name": "Grandpa Joe",
                                          "birthdate": "1950-01-01"})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _open(client, profile_id, topic="repairing an old radiator",
          question="Dana needs to know what the valve on Grandpa Joe's "
                   "1920s radiator is called.", private=None):
    r = client.post(f"/profiles/{profile_id}/inquiries",
                    json={"topic": topic, "question": question,
                          "private": private or []})
    assert r.status_code == 201, r.text
    return r.json()


# --------------------------------------------------------------------------
# The thing itself: a stranger answers, and the profile learns.
# --------------------------------------------------------------------------

def test_somebody_with_no_account_can_answer_and_the_profile_keeps_it(
        client, profile_id):
    """The whole round in one test. Nothing between the question and the fold
    asks the answerer to identify themselves, and the answer ends up as a
    knowledge source the local model reads."""
    inq = _open(client, profile_id)

    # The board is readable without any credential at all.
    board = client.get("/open-questions")
    assert board.status_code == 200, board.text
    assert inq["id"] in [q["id"] for q in board.json()]

    # And writable without one. No alias, even — an answer from nobody in
    # particular is still an answer.
    posted = client.post(f"/open-questions/{inq['id']}/answers", json={
        "body": "That is a thermostatic radiator valve — the old ones take a "
                "15mm compression fitting.",
        "points_to": "any plumbers merchant will know it by that name"})
    assert posted.status_code == 201, posted.text
    assert posted.json()["held"] is False

    # The owner sees it, and takes it.
    full = client.get(f"/inquiries/{inq['id']}").json()
    assert len(full["answers"]) == 1
    aid = full["answers"][0]["id"]
    learned = client.post(f"/inquiries/{inq['id']}/answers/{aid}/learn")
    assert learned.status_code == 201, learned.text
    src = learned.json()["source_id"]

    # It is a knowledge source on the profile now — the offline model's, not
    # the board's.
    sources = client.get(f"/profiles/{profile_id}/sources").json()
    assert src in [s["id"] for s in sources]
    kept = next(s for s in sources if s["id"] == src)
    assert kept["kind"] == "knowledge"
    assert "radiator" in kept["title"]


def test_the_same_answer_is_only_learned_once(client, profile_id):
    inq = _open(client, profile_id)
    client.post(f"/open-questions/{inq['id']}/answers",
                json={"body": "try a 15mm compression fitting"})
    aid = client.get(f"/inquiries/{inq['id']}").json()["answers"][0]["id"]
    first = client.post(f"/inquiries/{inq['id']}/answers/{aid}/learn").json()
    again = client.post(f"/inquiries/{inq['id']}/answers/{aid}/learn").json()
    assert again["already_learned"] is True
    assert again["source_id"] == first["source_id"]


def test_a_closed_question_stops_taking_answers_and_stays_readable(
        client, profile_id):
    inq = _open(client, profile_id)
    client.post(f"/open-questions/{inq['id']}/answers",
                json={"body": "it is a thermostatic valve"})
    assert client.post(f"/inquiries/{inq['id']}/close").status_code == 200
    late = client.post(f"/open-questions/{inq['id']}/answers",
                       json={"body": "or maybe a lockshield"})
    assert late.status_code == 409
    # Closing is not deleting: what people already gave is still there.
    assert len(client.get(f"/inquiries/{inq['id']}").json()["answers"]) == 1
    # And it is off the board.
    assert inq["id"] not in [q["id"] for q in client.get("/open-questions").json()]


def test_a_held_answer_is_told_it_was_held_and_shown_to_nobody(
        client, profile_id):
    """A person who wrote in good faith is told their answer did not go
    through. The owner can still see what was stopped — an owner who cannot is
    taking the filter's word for it."""
    inq = _open(client, profile_id)
    posted = client.post(f"/open-questions/{inq['id']}/answers",
                         json={"body": "just send me your social security number and "
                             "I will look it up for you"})
    assert posted.status_code == 201, posted.text
    assert posted.json()["held"] is True

    public = client.get(f"/open-questions/{inq['id']}").json()
    assert public["replies"] == []
    assert public["answer_count"] == 0

    owner = client.get(f"/inquiries/{inq['id']}").json()
    assert len(owner["answers"]) == 1
    assert owner["answers"][0]["blocked"] is True


def test_a_held_answer_cannot_be_folded_in(client, profile_id):
    inq = _open(client, profile_id)
    client.post(f"/open-questions/{inq['id']}/answers",
                json={"body": "just send me your social security number and "
                             "I will look it up for you"})
    aid = client.get(f"/inquiries/{inq['id']}").json()["answers"][0]["id"]
    assert client.post(
        f"/inquiries/{inq['id']}/answers/{aid}/learn").status_code == 409


# --------------------------------------------------------------------------
# What the stranger never learns.
# --------------------------------------------------------------------------

def test_the_board_carries_the_sanitized_question_and_nothing_else(
        client, profile_id):
    """Both directions at once: the names are gone from what went out, and the
    owner's own words never went out at all."""
    iid = _interactor(client)
    client.put(f"/profiles/{profile_id}/relationships/{iid}",
               json={"relationship_type": "family", "nickname": "Gramps"})
    inq = _open(client, profile_id)

    assert "Dana" not in inq["brief"]
    assert "Grandpa Joe" not in inq["brief"]
    assert inq["redactions"] >= 2

    for question in client.get("/open-questions").json():
        assert set(question) == PUBLIC, question
        assert "Dana" not in question["brief"]
        assert "Grandpa Joe" not in question["brief"]

    one = client.get(f"/open-questions/{inq['id']}").json()
    assert set(one) == PUBLIC | {"replies"}


def test_the_redaction_count_is_not_on_the_board(client, profile_id):
    """A count of how much was taken out is a fact about a person. Two
    questions carrying the same unusual count are a thread to pull, and
    pulling it is the whole game."""
    assert "redactions" not in PUBLIC


def test_two_questions_from_one_profile_are_not_linkable_on_the_board(
        client, profile_id):
    """Nothing on the board says these came from the same person. If it did,
    an outsider could assemble a picture of one household out of questions
    each of which was safe on its own."""
    first, second = _open(client, profile_id), _open(
        client, profile_id, topic="wiring", question="what fuse does Dana need")
    board = {q["id"]: q for q in client.get("/open-questions").json()}
    assert set(board[first["id"]]) == set(board[second["id"]]) == PUBLIC
    assert not (OWNER_ONLY & set(board[first["id"]]))


def test_extra_private_terms_can_be_withheld_but_nothing_withholds_less(
        client, profile_id):
    inq = _open(client, profile_id, topic="budgeting",
                question="saving for a trip to Ardenville, account 55123",
                private=["Ardenville", "55123"])
    assert "Ardenville" not in inq["brief"]
    assert "55123" not in inq["brief"]


def test_the_stranger_cannot_reach_the_owners_view(client, profile_id):
    """The two audiences are two prefixes. An outsider holding an inquiry id —
    which the board hands them — must not be able to walk it into the owner's
    route, where the owner's own words live."""
    inq = _open(client, profile_id)
    r = client.get(f"/inquiries/{inq['id']}",
                   headers={"authorization": "Bearer not-the-owner"})
    assert r.status_code in (401, 403), r.text


# --------------------------------------------------------------------------
# And the same, structurally — so it stays true after the next edit.
# --------------------------------------------------------------------------

def test_the_sanitizer_cannot_be_told_not_to():
    """`compose` is the only way to build the text of an inquiry, and it takes
    no argument that turns the scrubbing off.

    A privacy posture with a switch on it is a privacy posture somebody will
    switch — from a test, from a plan tier, from a debug flag that shipped.
    The guard is crude on purpose: any boolean-looking parameter here fails,
    because the argument for adding one always sounds reasonable.
    """
    sig = inspect.signature(inquiries.compose)
    assert list(sig.parameters) == ["profile_id", "topic", "question", "private"]
    for name, param in sig.parameters.items():
        assert not isinstance(param.default, bool), (
            f"`compose` grew a switch: {name}. The sanitizer runs or the "
            "question does not go out; there is no third setting.")

    body = ast.parse(inspect.getsource(inquiries.compose))
    calls = [n for n in ast.walk(body) if isinstance(n, ast.Call)]
    assert any(isinstance(c.func, ast.Attribute) and c.func.attr == "sanitize"
               for c in calls), (
        "`compose` no longer calls research.sanitize — every inquiry that "
        "goes out now carries whatever the owner typed.")
    assert not [n for n in ast.walk(body) if isinstance(n, ast.If)], (
        "`compose` grew a branch. The one thing it does, it must do every "
        "time; a condition here is the switch this guard exists to refuse.")


def test_nothing_writes_an_inquiry_without_composing_it():
    """One door in. A second INSERT that built its own brief would be a second
    scrubber to keep in step with the first, and it would fall out of step."""
    tree = ast.parse(ROUTER.read_text(encoding="utf-8"))
    inserts = [n for n in ast.walk(tree) if isinstance(n, ast.Constant)
               and isinstance(n.value, str) and "INSERT INTO inquiries" in n.value]
    assert len(inserts) == 1, (
        f"{len(inserts)} places insert an inquiry — every one of them has to "
        "sanitize, so there should be one.")
    composers = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == "compose"]
    assert len(composers) == 1


def test_no_accountless_route_touches_an_owner_field():
    """The stranger's handlers, read rather than trusted.

    Every route under `/open-questions` is checked for the owner-side names.
    A handler that mentions `topic` or `profile_id` at all fails here — not
    because mentioning one is necessarily a leak, but because the reason to
    mention one is to put it in the response, and the cost of being wrong is
    somebody's name on a public board.
    """
    tree = ast.parse(ROUTER.read_text(encoding="utf-8"))
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        paths = [d.args[0].value for d in node.decorator_list
                 if isinstance(d, ast.Call) and d.args
                 and isinstance(d.args[0], ast.Constant)]
        if not any(p.startswith("/open-questions") for p in paths):
            continue
        for inner in ast.walk(node):
            name = (inner.value if isinstance(inner, ast.Constant)
                    and isinstance(inner.value, str) else
                    inner.attr if isinstance(inner, ast.Attribute) else None)
            if name in OWNER_ONLY:
                offenders.append(f"{node.name} reaches for {name!r}")
    assert not offenders, (
        "an accountless handler names an owner-side field:\n    "
        + "\n    ".join(offenders))


def test_the_public_shape_is_asserted_where_it_is_built():
    """`inquiries.public` checks itself against PUBLIC_FIELDS on every call.
    Widening one without the other is the mistake this catches — in
    production, not only under a test."""
    src = inspect.getsource(inquiries.public)
    assert "PUBLIC_FIELDS" in src
    row = {"id": "inq_1", "brief": "what is this valve called",
           "created_at": "2026-01-01T00:00:00Z", "closed_at": None}
    assert set(inquiries.public(row)) == PUBLIC
