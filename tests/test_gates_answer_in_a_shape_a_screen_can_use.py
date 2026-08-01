"""A refusal built for a screen must survive the trip to one.

Several gates here answer with an **object** rather than a sentence. The plan
gate is the clearest:

    {"reason": "plan", "capability": "builders", "needs": "pro",
     "have": "free", "price_usd": 130, "period": "month",
     "message": "...", "billing": "simulated — no real funds move"}

Somebody built that on purpose. It exists so a console can say *which*
capability was wanted, *which* plan has it, what it costs, and that the money
is simulated — with a button. It is strictly more work than returning a
sentence, and the only reason to do it is for a UI.

The console then did `JSON.stringify(detail)` and threw it as the error
message, so every screen that catches an error and renders `.message` — which
is all of them — showed the user the raw object.

That is the defect worth a test: **the backend did the work of making a
refusal actionable and the transport threw the structure away at the last
step.** Nothing failed. The typecheck was clean, the request was correct, the
right refusal arrived, and it was destroyed on delivery.

So this file asserts the shape from the backend's side — that a gate still
answers with the fields a screen needs, and that the human sentence is one of
them — because the console's half of the fix (`RequestError`, `planGate`,
`Refusal.tsx`) is only worth anything while the object it reads still exists.
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

# What a screen needs to draw the upsell without inventing anything.
REQUIRED = ("reason", "capability", "needs", "have", "price_usd", "period",
            "message", "billing")


def _gated(client):
    """A profile on the free plan, and a call that the plan refuses."""
    p = client.post("/profiles", json={
        "owner_id": "acct_gate_shape", "kind": "fictional",
        "display_name": "Gated", "purpose": "companion_coach",
        "persona": "p", "verification": {"birthdate": "1990-01-01"},
    }).json()
    robot = client.post(f"/profiles/{p['id']}/robots",
                        json={"name": "Helper", "model": "u1_pro"},
                        headers={"authorization": f"Bearer {p['owner_token']}"})
    assert robot.status_code == 201, robot.text
    return client.put(
        f"/robots/{robot.json()['id']}/steering",
        json={"dials": {"autonomy": 20}},
        headers={"authorization": f"Bearer {p['owner_token']}"})


def test_the_plan_gate_answers_with_an_object_not_a_sentence(client):
    r = _gated(client)
    assert r.status_code == 402, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, dict), (
        "the plan gate answered with a bare string; a screen can no longer "
        "name the capability, the price or the simulated billing")


@pytest.mark.parametrize("field", REQUIRED)
def test_the_refusal_carries_what_a_screen_needs(field, client):
    detail = _gated(client).json()["detail"]
    assert field in detail, (
        f"the plan gate no longer carries {field!r}, so a console cannot draw "
        "the refusal without inventing it")


def test_the_object_carries_its_own_human_sentence(client):
    """The fallback the transport now relies on.

    `RequestError.message` quotes `detail.message` when there is one. Without
    it the class falls back to `JSON.stringify`, which is exactly the
    behaviour this whole change removed — so the sentence is load-bearing.
    """
    detail = _gated(client).json()["detail"]
    assert isinstance(detail.get("message"), str) and detail["message"], (
        "no human sentence on the refusal, so the console would fall back to "
        "showing the raw object again")


def test_the_price_never_travels_without_the_billing_disclosure(client):
    """Everywhere else in this repository, a figure is accompanied by the fact
    that the money is simulated. A refusal quoting a price is a place that is
    easy to forget, and it is the first price many people will see."""
    detail = _gated(client).json()["detail"]
    assert "price_usd" in detail and detail.get("billing"), (
        "a price with no billing note — a screen showing it would imply real "
        "money moves")
    assert "simulat" in detail["billing"].lower()

    # And in the sentence, which is now the only place the console shows
    # either. The card used to draw the price and the note itself, in English;
    # it renders `message` alone since that sentence started arriving in the
    # reader's language, so the pairing has to hold *inside* the sentence or it
    # does not reach anybody.
    said = detail["message"]
    assert str(detail["price_usd"]) in said, (
        "the sentence no longer names the price, and the card renders nothing "
        "else")
    assert "simulat" in said.lower(), (
        "the sentence quotes a price without saying the billing is simulated")


def test_the_gate_speaks_the_readers_language_through_the_real_handler(client):
    """Driven, and that is the point of it.

    `localize_detail` being right about a `Templated` is not the same as the
    handler reaching it. The plan gate's sentence sits inside a dict, and the
    dict branch used to call `tr_refusal` on it — which, because a `Templated`
    *is* a `str`, would look up the finished English sentence, find nothing,
    and hand the English straight back.

        asked     does the module translate this shape
        mattered  does the request path reach the code that does

    Every unit test of the plan gate passed with that branch broken, because
    none of them went through a request.
    """
    p = client.post("/profiles", json={
        "owner_id": "acct_gate_lang", "kind": "fictional",
        "display_name": "Gated", "purpose": "companion_coach",
        "persona": "p", "verification": {"birthdate": "1990-01-01"},
    }).json()
    robot = client.post(f"/profiles/{p['id']}/robots",
                        json={"name": "Helper", "model": "u1_pro"},
                        headers={"authorization": f"Bearer {p['owner_token']}"})
    # The *credential* decides the language, not the header — an owner has a
    # stored preference and `refusal_language` reads it in preference to
    # `Accept-Language`, which is the rule this repository settled on and the
    # one this test got wrong the first time.
    from qrme import i18n
    i18n.set_language(p["id"], "pt")
    refused = client.put(
        f"/robots/{robot.json()['id']}/steering",
        json={"dials": {"autonomy": 20}},
        headers={"authorization": f"Bearer {p['owner_token']}"})
    assert refused.status_code == 402, refused.text
    body = refused.json()
    for where in (body["detail"]["message"], body["message"]):
        assert "needs" not in where and "This account is on" not in where, (
            f"the plan gate arrived in English for a pt reader:\n{where}")
        assert "Esta conta" in where, where
    assert body["message"] == body["detail"]["message"], (
        "the lifted sentence and the nested one disagree")


def test_the_console_reads_the_structure_rather_than_stringifying_it():
    """The console half, checked structurally.

    `req()` threw `new Error(JSON.stringify(detail))` before. If that line
    comes back, every screen goes back to showing a blob and no runtime test
    here would notice, because the request itself is perfectly correct.
    """
    api = (REPO / "app/src/api.ts").read_text(encoding="utf-8")
    assert "class RequestError" in api, "the typed error is gone"
    assert "export function planGate" in api, "the gate reader is gone"
    # The specific regression: stringifying the detail on the way out.
    throw = re.search(r"throw new Error\(JSON\.stringify\(detail\)\)", api)
    assert not throw, (
        "req() is stringifying the structured detail again — the object the "
        "backend built for a screen would be shown to the user raw")
    # The structure rides out on the typed error. Matched as a prefix rather
    # than as the whole call: this pinned the exact two-argument spelling, and
    # broke when a third argument was added to carry the 422's sentence beside
    # the rows — a change that keeps `detail` exactly where this cares about
    # it. What matters is that the structure is still handed over unflattened.
    #
    #     asked     is the call spelled this exact way
    #     mattered  does the structure still ride out on it
    assert re.search(r"new RequestError\(res\.status, detail\b", api), (
        "req() no longer hands the structured detail to RequestError")

    refusal = (REPO / "app/src/Refusal.tsx").read_text(encoding="utf-8")
    # The price and the disclosure are rendered together, not separately.
    #
    # This used to check that `Refusal.tsx` names `gate.price_usd` and
    # `gate.billing`, because the card drew them itself. It drew them in
    # English, which cost nothing while `message` was English too — and became
    # the only untranslated text on the card the moment the server started
    # composing that sentence in the reader's language.
    #
    #     asked     does the card render the price and the disclosure
    #     mattered  do the price and the disclosure reach the reader together
    #
    # They do, inside `message`, in whichever language it arrives in — which is
    # a stronger version of the same invariant, since it now holds in ten
    # languages rather than one. The card renders that sentence; the driven
    # half of this file (`test_the_price_never_travels_without_the_billing_disclosure`)
    # is what holds the sentence itself to carrying both.
    assert "gate.message" in refusal, (
        "the card no longer renders the composed sentence, so the price and "
        "the simulated-billing disclosure reach the reader through nothing")
    assert "planGate(" in refusal, "the card no longer reads the structure"
