"""The agent's remit, which was prose in a docstring until this round.

`qrme/privileges.py` opens by saying what this agent is for — not a life-wide
companion, that is JIM's shape, but a thing that exists to **get a person's
matter resolved**: something wrong with the app, with their synthetic profiles,
or with the platform. Every power in that roster is justified by it.

    asked     can somebody get their issue looked at
    mattered  can they find out afterwards what happened to it

Three modules already answered questions that are not this one. `help` says
how the product works and writes nothing. `feedback` takes ideas into a box
nobody replies to. `problems` counts what broke, content-free, and never knows
whose failure it was. None of them is somewhere a person's own matter lives.

## What these hold

**The help box answers and does not settle.** The first draft let a recognised
question open the matter already settled, and the first sentence run through it
— *"my card was charged twice on tuesday"* — came back settled, by help, on a
keyword. Loose matching is right for a help box: an approximately right
paragraph costs a reader nothing. The same guess disposing of a billing
complaint costs them the complaint, silently, because a settled matter is in
nobody's queue. So `answered` means *here is something, is that it*, and only a
person moves anything to `settled`.

**A claim, because the hardest case in the remit is the person who cannot sign
in.** *Within the app and outside the app* includes the account somebody has
been locked out of, and an issue tracker that requires an account is closed to
exactly them. So a matter may be raised with no principal, and read back with
one string that is shown once and stored as a hash.

**The queue's default is unsettled, not open.** Written as `open` first, and it
came back empty on a database holding two matters nobody had answered — both
had gone to `answered` on help's say-so. A support queue that reports *nothing
to do* while people wait is worse than no queue at all.
"""

from __future__ import annotations

import ast
import hashlib
import pathlib

from qrme import db, help as helpbox, matters


def raise_one(client, trouble="my card was charged twice on tuesday",
              concerns="platform", **kw):
    response = client.post("/matters",
                           json={"trouble": trouble, "concerns": concerns},
                           **kw)
    assert response.status_code == 201, response.text
    return response.json()


# --- the help box offers, and never disposes --------------------------------

def test_the_help_box_answers_and_does_not_settle(client):
    """The billing complaint, by name, because it is the one that found this.

    It is still *answered* — help finds something to say about nearly
    anything, and that is not a defect in help. What it must never be is
    `settled`, which is the standing that takes it out of the queue.
    """
    matter = raise_one(client)
    assert matter["standing"] == "answered"
    assert matter["settled_by"] == "", (
        "the help box put its own name to somebody's billing complaint")


def test_only_a_person_ever_settles(client):
    matter = raise_one(client)
    assert matter["standing"] != "settled"
    settled = client.post(f"/matters/{matter['id']}/settle",
                          json={"answer": "refunded the duplicate"},
                          headers={"X-Matter-Claim": matter["claim"]})
    assert settled.status_code == 200
    assert settled.json()["settled_by"] == "the_person"


def test_the_answer_a_matter_carries_is_never_a_generated_one(client,
                                                              monkeypatch):
    """A model's sentence is offered, and the matter stays open.

    `help.ask` reaches a model where one is configured. That reply may be
    good; it is still a sentence assembled about the product rather than a
    fact somebody wrote down, and letting it stand as a matter's answer is the
    same failure as the keyword with worse odds.
    """
    class Provider:
        def generate(self, _system, _messages):
            return "You should try turning the beacon off and on again."

    monkeypatch.setattr(helpbox, "_model_is_real", lambda: True)
    monkeypatch.setattr(helpbox.llm, "get_provider", lambda: Provider())
    heard = helpbox.ask("zzzqq unmatchable string about nothing at all")
    assert heard["source"] == "model"
    assert heard["recognised"] is False, (
        "a generated sentence counted as the help box knowing the answer")


def test_the_fallback_is_not_a_recognition(client):
    """`source` cannot tell these apart, which is why `recognised` exists.

    The fallback — *I can only help with using QRME* — is as `written` as a
    real answer is. A caller wanting the difference had to compare the
    sentence against a copy of itself.
    """
    heard = helpbox.ask("zzzqq unmatchable string about nothing at all")
    assert heard["source"] == "written"
    assert heard["recognised"] is False


# --- somebody who cannot sign in --------------------------------------------

def test_a_matter_can_be_raised_with_no_account(client):
    matter = raise_one(client, trouble="I cannot sign in at all",
                       concerns="app")
    assert matter["anonymous"] is True
    assert matter["claim"], "nothing came back that could read it again"


def test_the_claim_is_the_only_way_in(client):
    matter = raise_one(client)
    mid = matter["id"]
    assert client.get(f"/matters/{mid}").status_code == 404
    assert client.get(f"/matters/{mid}",
                      headers={"X-Matter-Claim": "not-the-claim"}
                      ).status_code == 404
    assert client.get(f"/matters/{mid}",
                      headers={"X-Matter-Claim": matter["claim"]}
                      ).status_code == 200


def test_the_claim_itself_is_not_kept(client):
    """The row holds a hash, the way the waiver in `escalation` does.

    A support table holding the strings that open its own rows is a table
    whose backup opens everybody's matters.
    """
    matter = raise_one(client)
    stored = db.connect().execute(
        "SELECT claim FROM matters WHERE id=?", (matter["id"],)).fetchone()
    assert stored["claim"] != matter["claim"]
    assert stored["claim"] == hashlib.sha256(
        matter["claim"].encode("utf-8")).hexdigest()


def test_an_anonymous_matter_is_in_nobodys_list(client):
    raise_one(client)
    assert client.get("/matters").json()["my_matters"] == []
    assert matters.mine("anonymous") == [], (
        "anonymous matters are reachable as a group, so one caller reads "
        "everybody's")


# --- the queue --------------------------------------------------------------

def test_the_queue_shows_what_is_waiting_rather_than_what_is_open(client):
    """The regression this default was changed for.

    Two matters, neither answered by a person, and a queue keyed on `open`
    showed nothing at all.
    """
    raise_one(client)
    raise_one(client, trouble="what is a beacon", concerns="app")
    waiting = client.get("/matters/queue").json()["unsettled"]
    assert len(waiting) == 2, "the queue is empty while two people wait"
    assert client.get("/matters/queue?standing=open").json()["unsettled"] == []


def test_a_settled_matter_leaves_the_queue(client):
    matter = raise_one(client)
    client.post(f"/matters/{matter['id']}/settle",
                json={"answer": "refunded"},
                headers={"X-Matter-Claim": matter["claim"]})
    assert client.get("/matters/queue").json()["unsettled"] == []


def test_the_raiser_can_say_that_was_not_the_answer(client):
    """Otherwise the only exit from a wrong answer is somebody here noticing."""
    matter = raise_one(client)
    back = client.post(f"/matters/{matter['id']}/not-it",
                       headers={"X-Matter-Claim": matter["claim"]})
    assert back.status_code == 200
    assert back.json()["standing"] == "open"
    assert back.json()["answer"] == ""
    assert "not_the_answer" in [s["did"] for s in back.json()["trail"]], (
        "a matter answered wrongly once reads the same as one never answered")


def test_only_the_raiser_can_reject_the_answer(client):
    matter = raise_one(client)
    assert client.post(f"/matters/{matter['id']}/not-it").status_code == 404


# --- nothing here is a dead control -----------------------------------------

def test_every_way_a_matter_can_be_settled_is_reachable(client):
    """`SETTLED_BY` names three, and all three happen through the routes.

    The roster next door refuses to carry a row for an unbuilt power — the
    person says yes and yes does nothing. A vocabulary with a value nothing
    can produce is the same dead control one layer down.
    """
    reached = set()

    mine = raise_one(client)
    client.post(f"/matters/{mine['id']}/settle", json={"answer": "worked it out"},
                headers={"X-Matter-Claim": mine["claim"]})
    reached.add(client.get(f"/matters/{mine['id']}",
                           headers={"X-Matter-Claim": mine["claim"]}
                           ).json()["settled_by"])

    helped = raise_one(client, trouble="what is a beacon", concerns="app")
    client.post(f"/matters/{helped['id']}/settle",
                json={"answer": helped["answer"], "helped": True},
                headers={"X-Matter-Claim": helped["claim"]})
    reached.add(client.get(f"/matters/{helped['id']}",
                           headers={"X-Matter-Claim": helped["claim"]}
                           ).json()["settled_by"])

    theirs = raise_one(client)
    client.post(f"/matters/{theirs['id']}/take")
    client.post(f"/matters/{theirs['id']}/settle", json={"answer": "fixed it"})
    reached.add(client.get(f"/matters/{theirs['id']}",
                           headers={"X-Matter-Claim": theirs["claim"]}
                           ).json()["settled_by"])

    assert reached == {v for v in matters.SETTLED_BY if v}


def test_a_keyword_cannot_put_help_in_settled_by(client):
    """`helped` is the raiser's word, and only on a matter with an answer."""
    matter = raise_one(client)
    client.post(f"/matters/{matter['id']}/not-it",
                headers={"X-Matter-Claim": matter["claim"]})
    client.post(f"/matters/{matter['id']}/settle",
                json={"answer": "sorted", "helped": True},
                headers={"X-Matter-Claim": matter["claim"]})
    read = client.get(f"/matters/{matter['id']}",
                      headers={"X-Matter-Claim": matter["claim"]}).json()
    assert read["settled_by"] == "the_person"


# --- the module records powers and does not hold them -----------------------

POWERS = ("research", "inquiries", "briefing", "delegation", "escalation",
          "privileges")


def test_nothing_here_exercises_one_of_the_agents_powers():
    """A support record that could also spend somebody's grants would be a
    second door onto every power in the roster, and the roster's whole
    argument is that there is one door per power with the person standing in
    it.

    Read from the module's own imports rather than trusted, because the line
    that breaks this rule is one line and looks helpful.

    The first version of this guard read the source as text and asked whether
    `"from . import research"` appeared in it. Adding `research` to the
    import this module already has — `from . import db, help as helpbox` —
    left it green, because that string never appears in a grouped import. A
    guard that only catches the defect written the way the author imagined is
    a guard for the author.
    """
    tree = ast.parse(pathlib.Path(matters.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.Import):
            imported.update(a.name.split(".")[-1] for a in node.names)
    reached = imported & set(POWERS)
    assert not reached, (
        f"matters.py imports {sorted(reached)} — record that a power ran, "
        "do not run it")


def test_a_step_is_recorded_rather_than_performed(client):
    """`used` writes down that a power ran. It cannot make one run."""
    matter = raise_one(client)
    noted = client.post(f"/matters/{matter['id']}/used",
                        json={"did": "read_up", "note": "billing docs"})
    assert noted.status_code == 200
    assert [s["did"] for s in noted.json()["trail"]][-1] == "read_up"
    assert client.post(f"/matters/{matter['id']}/used",
                       json={"did": "invent_a_power"}).status_code == 422


# --- closed sets, and one shape ---------------------------------------------

def test_the_vocabularies_are_closed_so_the_shells_can_say_them(client):
    listed = client.get("/matters").json()
    assert listed["concerns"] == list(matters.CONCERNS)
    assert listed["standings"] == list(matters.STANDINGS)
    assert client.post("/matters", json={"trouble": "x", "concerns": "nope"}
                       ).status_code == 422


def test_a_matter_reads_the_same_whether_or_not_anything_happened(client):
    """One shape, from raised to settled.

    A payload that grows fields only when something happened hands four shells
    `undefined` on the case they meet most — which is the fresh one. Compared
    across two different matters at two different points in their lives, not
    against a second call on the same one, which would compare the shape with
    itself.
    """
    fresh = raise_one(client)
    untouched = client.get(f"/matters/{fresh['id']}",
                           headers={"X-Matter-Claim": fresh["claim"]}).json()

    worked = raise_one(client, trouble="what is a beacon", concerns="app")
    client.post(f"/matters/{worked['id']}/take")
    client.post(f"/matters/{worked['id']}/used", json={"did": "read_up"})
    client.post(f"/matters/{worked['id']}/settle", json={"answer": "done"})
    finished = client.get(f"/matters/{worked['id']}",
                          headers={"X-Matter-Claim": worked["claim"]}).json()

    assert set(untouched) == set(finished)
    assert untouched["settled_at"] is None and finished["settled_at"]
    # And what `raise_it` adds on top is exactly the two things only its own
    # caller can use: the claim, shown once, and what help offered instead.
    assert set(fresh) - set(untouched) == {"claim", "offered"}


def test_the_words_a_person_wrote_are_kept_as_written(client):
    said = "  my card was charged twice on tuesday  "
    matter = raise_one(client, trouble=said)
    assert matter["trouble"] == said.strip()
    assert client.post("/matters", json={"trouble": "   ", "concerns": "app"}
                       ).status_code == 422
