"""The free tier: the same app, with your data in the clear.

Free and Basic reach exactly the same capabilities. Twenty dollars buys
*privacy*, not features — and that only works if "not private" is impossible to
miss and impossible to forget. So the disclosure is a field on every surface
that stores something rather than a line in a Terms of Service nobody reads at
the moment it matters.

Two tests here are the ones that matter, and both are about somebody who is not
the account holder:

* `test_every_sensitive_kind_is_enforced_somewhere` — a payload named as too
  sensitive for the open store, with nothing actually refusing it, is a claim
  with no check behind it. This repository has found that gap in itself
  repeatedly.
* `test_a_downgrade_never_unseals_anything` — a billing event that
  declassified a year of somebody's records would be the worst thing this
  module could do.
"""

import inspect
import pathlib
import re

import pytest

from qrme import storage, tiers
from tests.test_capabilities import auth_header, make_profile


# -- the difference Basic actually buys ---------------------------------------

def test_free_and_basic_reach_the_same_capabilities(client):
    """The product decision. A free tier crippled into uselessness teaches
    nobody anything about the product."""
    assert tiers.includes("free") == tiers.includes("basic")
    assert tiers.includes("free")            # and it is not empty


def test_what_differs_is_where_the_data_lives(client):
    assert storage.is_private("free") is False
    assert storage.is_private("basic") is True
    assert storage.is_private("pro") is True
    assert storage.posture_of("free") == "open_cloud"
    assert storage.posture_of("basic") == "vault"


def test_the_free_plan_costs_nothing_and_says_what_that_means(client):
    assert tiers.PLANS["free"]["price_usd"] == 0
    page = client.get("/plans").json()
    free = next(p for p in page["plans"] if p["plan"] == "free")
    assert free["storage"]["private"] is False
    assert free["storage"]["not_private"] is True
    assert "in the clear" in free["storage"]["disclosure"]
    assert "where your data lives" in page["the_difference"]


def test_the_open_posture_names_who_can_read_it(client):
    """Vaguery here would be the whole problem. "Industry-standard security"
    is what a product says when it does not want to finish the sentence."""
    described = storage.describe("free")
    readers = " ".join(described["who_can_read"]).lower()
    assert "operate this deployment" in readers
    assert "lawful access" in readers
    assert described["encrypted_at_rest"] is False
    assert described["you_hold_a_key"] is False


def test_a_paid_plan_carries_no_free_disclosure(client):
    assert storage.describe("basic")["disclosure"] is None
    assert storage.describe("pro")["refused_here"] == []


# -- the disclosure is structural ----------------------------------------------

def test_a_free_membership_carries_its_posture(client):
    """A field, not a footnote."""
    me = make_profile(client, plan="free", owner_id="acct-f1")
    out = client.get("/memberships/acct-f1", headers=auth_header(me)).json()
    assert out["storage"]["not_private"] is True
    assert "in the clear" in out["storage"]["disclosure"]


def test_creating_a_profile_on_free_tells_you_so_in_the_response(client):
    """The moment it matters is the moment somebody makes something."""
    me = make_profile(client, plan=None, owner_id="acct-f2")
    assert me["membership"]["plan"] == "free"
    assert me["membership"]["storage"]["private"] is False
    assert me["membership"]["storage"]["disclosure"]


def test_every_plan_in_the_catalogue_states_its_posture(client):
    page = client.get("/plans").json()
    for row in page["plans"]:
        assert "storage" in row, row["plan"]
        assert row["storage"]["posture"] in storage.POSTURES


# -- what the open store may not hold -----------------------------------------

def test_every_sensitive_kind_is_enforced_somewhere(client):
    """A kind named as too sensitive for the open store, with nothing actually
    refusing it, is a claim with no check behind it.

    The first draft of `SENSITIVE` named `body_image` and `medical` — both
    JIM-mini's payloads, neither reachable from this repository — and a
    `signature`, which is not a storage-at-rest risk at all because WebAuthn
    keeps the private key on the device. This test is why the list is now only
    what this repository can refuse.
    """
    root = pathlib.Path(__file__).resolve().parent.parent / "qrme"
    body = "\n".join(p.read_text() for p in root.rglob("*.py")
                     if p.name != "storage.py")
    for kind in storage.SENSITIVE:
        assert f'"{kind}"' in body, (
            f"{kind!r} is listed as too sensitive for the open store and "
            "nothing outside storage.py refuses it")


def test_third_party_source_material_is_refused_on_free(client):
    """The person exposed did not choose the plan. That is the whole test for
    whether something belongs on this list."""
    me = make_profile(client, plan="free", owner_id="acct-f3",
                      kind="other_person",
                      consent={"basis": "subject_consent", "attestor": "dee"})
    r = client.post(f"/profiles/{me['id']}/sources",
                    json={"kind": "writing", "title": "letters",
                          "content": "things she told me"},
                    headers=auth_header(me))
    assert r.status_code == 402, r.text
    assert "did not pick this plan" in r.json()["detail"]


def test_the_same_material_is_fine_on_a_paid_plan(client):
    me = make_profile(client, plan="basic", owner_id="acct-f4",
                      kind="other_person",
                      consent={"basis": "subject_consent", "attestor": "dee"})
    r = client.post(f"/profiles/{me['id']}/sources",
                    json={"kind": "writing", "title": "letters",
                          "content": "things she told me"},
                    headers=auth_header(me))
    assert r.status_code in (200, 201), r.text


def test_your_own_source_material_is_fine_on_free(client):
    """The refusal is about *whose* exposure it is. Your own notes about
    yourself are yours to put wherever you like."""
    me = make_profile(client, plan="free", owner_id="acct-f5", kind="self")
    r = client.post(f"/profiles/{me['id']}/sources",
                    json={"kind": "writing", "title": "mine",
                          "content": "my own diary"},
                    headers=auth_header(me))
    assert r.status_code in (200, 201), r.text


def test_a_rated_profile_cannot_be_made_on_free(client):
    r = client.post("/profiles", json={
        "plan": "free", "owner_id": "acct-f6", "kind": "fictional",
        "display_name": "Velvet", "persona": "A cabaret singer.",
        "adult_mode": True, "maturity": "open",
        "verification": {"birthdate": "1984-06-01"}})
    assert r.status_code == 402, r.text
    assert "age gate" in r.json()["detail"]


def test_a_hard_line_is_never_answered_with_a_price(client):
    """The ordering bug this caught, and the reason it matters.

    A rated profile *of another real person* is refused at any price. The
    first version checked the storage posture first, so the response was 402
    — telling somebody the line is a price. It is not, and a payment response
    in front of a hard line is the one impression this refusal must never
    give.
    """
    r = client.post("/profiles", json={
        "plan": "free", "owner_id": "acct-f7", "kind": "other_person",
        "display_name": "Somebody", "persona": "A real person.",
        "adult_mode": True, "maturity": "open",
        "consent": {"basis": "subject_consent", "attestor": "dee"},
        "verification": {"birthdate": "1984-06-01"}})
    assert r.status_code == 403, r.text
    assert "never available" in r.json()["detail"]


def test_a_signing_credential_is_deliberately_not_on_the_list(client):
    """Recorded because the first version got it wrong. It reads like the most
    sensitive thing in the product and is not a storage-at-rest risk: WebAuthn
    keeps the private key on the device."""
    assert "signature" not in storage.SENSITIVE
    src = inspect.getsource(storage)
    assert "private key on the device" in src


# -- moving between plans ------------------------------------------------------

def test_a_downgrade_never_unseals_anything(client):
    """A billing event that declassified a year of somebody's records would be
    the worst thing this module could do."""
    effect = storage.downgrade_effect("pro", "free")
    assert effect["existing_stays_sealed"] is True
    assert effect["new_content_in_the_clear"] is True
    assert "does not declassify your history" in effect["note"]


def test_the_downgrade_helper_performs_nothing(client):
    """It states the rule rather than enacting it — no write, no move."""
    src = inspect.getsource(storage.downgrade_effect)
    for verb in ("INSERT", "UPDATE", "DELETE", "put(", "connect("):
        assert verb not in src, f"downgrade_effect does {verb!r}"


def test_an_upgrade_does_not_un_expose_what_was_already_open(client):
    """Sealing content afterwards protects it from here on. A product that
    implied otherwise would be selling absolution rather than encryption."""
    effect = storage.upgrade_effect("free", "basic")
    assert effect["new_content_sealed"] is True
    assert effect["existing_content_sealed"] is False
    assert "does not un-expose it" in effect["note"]
    assert "Backups" in effect["note"] or "backups" in effect["note"]


def test_moving_between_two_private_plans_changes_nothing(client):
    for effect in (storage.upgrade_effect("basic", "pro"),
                   storage.downgrade_effect("pro", "basic")):
        assert "nothing changes" in effect["note"]


# -- the ladder ----------------------------------------------------------------

def test_the_order_runs_visitor_free_basic_pro(client):
    assert tiers.ORDER == ("visitor", "free", "basic", "pro")
    assert tiers.DEFAULT_PLAN == "free"


def test_every_plan_has_a_posture(client):
    """A plan with no entry would fall to open_cloud silently, which is the
    wrong direction to fail in."""
    for plan in tiers.ORDER:
        assert plan in storage.BY_PLAN, plan


def test_a_free_account_still_reaches_its_capabilities(client):
    """The point of the tier. If free cannot make a profile it is not a free
    version of this product, it is a brochure."""
    me = make_profile(client, plan="free", owner_id="acct-f8")
    assert me["id"]
    r = client.get(f"/profiles/{me['id']}", headers=auth_header(me))
    assert r.status_code == 200


def test_free_is_still_refused_the_paid_capabilities(client):
    me = make_profile(client, plan="free", owner_id="acct-f9")
    r = client.post("/marketplace/listings",
                    json={"profile_id": me["id"], "title": "x", "price": 1},
                    headers=auth_header(me))
    assert r.status_code == 402
    assert r.json()["detail"]["needs"] == "pro"
