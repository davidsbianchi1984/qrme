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


# -- platform custody: free never reaches the vault ----------------------------

class CountingVault:
    """A vault that records every write, so a test can assert there were none."""

    def __init__(self):
        self.store: dict[str, str] = {}
        self.writes: list[str] = []

    def put(self, key, value):
        self.writes.append(key)
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def delete(self, key):
        return self.store.pop(key, None) is not None


def test_the_vault_gate_asks_about_the_plan_not_the_deployment(client):
    """The bug this round is about. Every seal point read `if pdi is not None`
    — whether the *deployment* has a vault, not whether the *account* is on a
    plan that uses one."""
    fake = CountingVault()
    assert storage.vault_for("basic", fake) is fake
    assert storage.vault_for("pro", fake) is fake
    assert storage.vault_for("free", fake) is None
    assert storage.vault_for("visitor", fake) is None
    assert storage.vault_for("basic", None) is None


def test_a_profiles_plan_resolves_through_to_its_owner(client):
    """A membership belongs to the person, not the profile. Asking
    `plan_of(profile_id)` finds no membership, returns "visitor", and quietly
    treats every paying member's profile as an open-cloud account."""
    me = make_profile(client, plan="basic", owner_id="acct-c1")
    assert tiers.plan_of(me["id"]) == "visitor"
    assert tiers.plan_of_profile(me["id"]) == "basic"
    assert tiers.plan_of_profile("prf_nonexistent") == "visitor"


def test_free_is_platform_custody_and_paid_is_the_users(client):
    assert storage.custody_of("free") == "platform"
    assert storage.custody_of("basic") == "user"
    platform = storage.CUSTODY["platform"]
    assert platform["goes_through_a_vault"] is False
    assert platform["user_holds_a_key"] is False
    assert platform["returning_access"] is True
    assert "HTTPS" in platform["transport"]


def test_the_membership_says_who_holds_it(client):
    me = make_profile(client, plan="free", owner_id="acct-c2")
    out = client.get("/memberships/acct-c2", headers=auth_header(me)).json()
    assert out["storage"]["custody"]["who"] == "platform"
    assert out["storage"]["custody"]["held_by"] == "QRME"
    assert out["storage"]["custody"]["goes_through_a_vault"] is False


def test_custody_is_never_described_as_ownership(client):
    """A product decides who *holds* a record. It does not get to decide away
    somebody's statutory rights over their own personal data.

    Checked against the **values a user is shown**, not the module source — the
    JIM-mini version of this test first swept the source and failed on the
    comment explaining why ownership is the wrong word, which is the fourth
    time a substring guard in these repositories has tripped on its own
    explanation.
    """
    shown = " ".join(
        str(v) for spec in storage.CUSTODY.values() for v in spec.values()
    ).lower()
    for phrase in ("we own your", "the platform owns", "you do not own",
                   "owns your data", "our property"):
        assert phrase not in shown, (
            f"{phrase!r} is an ownership claim, not a custody one")
    assert "host your work" in shown and "access to it" in shown
    assert "statutory rights" in inspect.getsource(storage)


# -- a clinician's note about a real person ------------------------------------

def _referral_setup(client, plan, owner_id):
    """A real profile, a real interactor with a real conversation, and a real
    provider — so that removing the guard lets the referral actually succeed.

    The first version passed `provider_id="prv_any"`, and a mutation check
    showed it failed at "no such clinician" with the guard removed: a green
    tick that proved nothing. A refusal test has to be reached *by a request
    that would otherwise work.*
    """
    prof = make_profile(client, plan=plan, owner_id=owner_id)
    owner = auth_header(prof)
    it = client.post("/interactors", json={"display_name": "Dana"}).json()
    me = {"authorization": f"Bearer {it['token']}"}
    client.post(f"/profiles/{prof['id']}/chat", headers=owner, json={
        "interactor_id": it["id"], "message": "my chest has been tight"})
    # A referral signs at the `high` tier, so the interactor needs a
    # device-bound, document-proofed credential before prepare will run.
    from tests.test_signatures import Authenticator

    a = Authenticator()
    opts = client.post("/signatures/enroll/options",
                       json={"display_name": "Dana"}, headers=me).json()
    body = a.register(opts["challenge"])
    body.update({"proofing_level": "document", "display_name": "Dana",
                 "proofing_attestor": "clinic-registrar"})
    client.post("/signatures/enroll", json=body, headers=me)
    prov = client.post("/providers", json={
        "name": "Riverside Cardiology", "area": "medical",
        "location": "Leeds", "contact": "0113 000 0000"}).json()
    return prof, it, me, prov


def test_a_referral_cannot_be_prepared_on_an_open_plan(client):
    """A clinician's written opinion about a real person reached the open
    store because the referral flow writes through `referral.reply` rather
    than `add_source`, so the third-party rule — which is the same rule —
    never saw it. The patient is frequently not the account holder."""
    prof, it, me, prov = _referral_setup(client, "free", "acct-c3")
    out = client.post("/referrals/prepare", headers=me, json={
        "interactor_id": it["id"], "profile_id": prof["id"],
        "provider_id": prov["id"]})
    assert out.status_code == 402, out.text
    assert "did not pick this plan" in out.json()["detail"]


def test_the_refusal_lands_before_any_clinician_is_contacted(client):
    """Refusing when the note comes back would strand a real person who has
    already been written to, mid-flow, holding words they cannot file."""
    from qrme import db as qdb

    prof, it, me, prov = _referral_setup(client, "free", "acct-c4")
    client.post("/referrals/prepare", headers=me, json={
        "interactor_id": it["id"], "profile_id": prof["id"],
        "provider_id": prov["id"]})
    n = qdb.connect().execute(
        "SELECT COUNT(*) AS n FROM referrals").fetchone()["n"]
    assert n == 0, "a referral row was created before the refusal"


def test_the_same_referral_prepares_normally_on_a_paid_plan(client):
    """The other half. Without it the two tests above pass if referrals broke
    entirely, which is a different bug wearing the same green tick."""
    prof, it, me, prov = _referral_setup(client, "basic", "acct-c5")
    out = client.post("/referrals/prepare", headers=me, json={
        "interactor_id": it["id"], "profile_id": prof["id"],
        "provider_id": prov["id"]})
    assert out.status_code in (200, 201), out.text


def test_every_sensitive_kind_is_still_enforced_somewhere(client):
    """Re-asserted after adding `clinical_note`, because the whole value of
    that list is that nothing sits on it unenforced."""
    root = pathlib.Path(__file__).resolve().parent.parent / "qrme"
    body = "\n".join(p.read_text() for p in root.rglob("*.py")
                     if p.name != "storage.py")
    for kind in storage.SENSITIVE:
        assert f'"{kind}"' in body, (
            f"{kind!r} is listed as too sensitive for the open store and "
            "nothing outside storage.py refuses it")


def test_signing_deliberately_keeps_the_real_vault(client):
    """The trap this module already fell into once, recorded so the loop is
    not closed the tidy-looking way. A signer is frequently an interactor with
    no membership: gating `_seal` by their plan returns None, and the custody
    chain a referral depends on quietly stops being written."""
    src = inspect.getsource(storage.vault_for)
    assert "signatures._seal" in src
    assert "vault_for" not in inspect.getsource(
        __import__("qrme.signatures", fromlist=["_seal"])._seal)


# -- the copy cannot go stale behind the list ----------------------------------

_COUNT_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8}


def test_no_copy_hardcodes_a_stale_count_of_refusals(client):
    """The gap this test exists for actually shipped.

    `SENSITIVE` gained `clinical_note` and four pieces of user-facing copy went
    on saying **two**: screen 138's card, screen 140's subtitle, the
    walkthrough lesson, and a README heading. A number written into prose is a
    duplicate of a list, and duplicates drift silently — nothing fails when a
    dict grows an entry.

    So no copy near a refusal may name a count that disagrees with the list.
    The honest fix is usually to stop counting in prose at all, which is what
    the copy does now.
    """
    import re

    n = len(storage.SENSITIVE)
    sources = {
        "qrme/tutorial.py": pathlib.Path("qrme/tutorial.py"),
        "docs/screens/build.py": pathlib.Path("docs/screens/build.py"),
        "README.md": pathlib.Path("README.md"),
    }
    root = pathlib.Path(__file__).resolve().parent.parent
    pattern = re.compile(
        # No em dash and a short window: the first version reached across
        # "all three products — never stored, so it cannot disagree", which is
        # a sentence about the agent light. A guard with a false positive gets
        # loosened until it catches nothing.
        r"\b(one|two|three|four|five|six|seven|eight)\b[^.\n\u2014]{0,25}?"
        r"(we refuse|are refused|refused rather|never stored|"
        r"will not leave open|not be stored)",
        re.IGNORECASE)
    for label, rel in sources.items():
        text = (root / rel).read_text()
        for m in pattern.finditer(text):
            said = _COUNT_WORDS[m.group(1).lower()]
            assert said == n, (
                f"{label} says {m.group(1)!r} where SENSITIVE holds {n}: "
                f"{m.group(0)!r}")


def test_the_refusal_screen_names_every_kind_on_the_list(client):
    """A screen that lists the refusals and misses one is the same drift in
    the other direction — the list grew and the drawing did not."""
    build = (pathlib.Path(__file__).resolve().parent.parent
             / "docs" / "screens" / "build.py").read_text()
    start = build.index('num=140')
    screen = build[start:build.index("], button=", start)].lower()
    for kind, hint in [("third_party_source", "letters"),
                       ("clinical_note", "clinician"),
                       ("rated_content", "age gate")]:
        assert kind in storage.SENSITIVE
        assert hint in screen, (
            f"screen 140 does not name {kind!r} (looked for {hint!r})")


def test_a_free_account_puts_nothing_in_the_vault(client, monkeypatch):
    """The end-to-end half of the vault gate, which JIM-mini had and this
    repository did not.

    A unit test of `vault_for` proves the function; it does not prove that
    every seal point calls it. Counting writes across a real exercise is what
    catches the site somebody adds next month and wires straight to
    `app.state.pdi`.
    """
    from qrme import adaptation, companion

    vault = CountingVault()
    me = make_profile(client, plan="free", owner_id="acct-c6")
    companion.sunset(dict(id=me["id"], display_name="X", owner_id="acct-c6"),
                     pdi=vault)
    adaptation.finetune(me["id"], pdi=vault)
    assert vault.writes == [], (
        "a free profile reached the vault at: " + ", ".join(vault.writes))


def test_the_same_work_on_a_paid_plan_does_reach_the_vault(client):
    """Otherwise the test above passes if sealing broke outright, which is a
    different bug wearing the same green tick."""
    from qrme import adaptation, companion

    vault = CountingVault()
    me = make_profile(client, plan="pro", owner_id="acct-c7")
    companion.sunset(dict(id=me["id"], display_name="X", owner_id="acct-c7"),
                     pdi=vault)
    assert vault.writes, "nothing sealed on a vault plan"
    assert all(k.startswith(f"qrme/{me['id']}/") for k in vault.writes)


def test_the_two_ungated_seal_points_are_unreachable_on_an_open_plan(client):
    """`rated.py` and `referral.py` still read `if pdi is not None` rather
    than asking the plan, and that is deliberate — both sit behind an earlier
    refusal that an open plan cannot get past, so a second gate would be dead
    code pretending to be defence.

    It is only safe while the earlier refusal holds, which is exactly the kind
    of thing that breaks silently when somebody moves a check. So the chain is
    asserted rather than trusted: on a free plan, neither door opens.
    """
    # rated events need a rated profile, and a rated profile needs a vault plan
    r = client.post("/profiles", json={
        "plan": "free", "owner_id": "acct-c8", "kind": "fictional",
        "display_name": "Velvet", "persona": "A cabaret singer.",
        "adult_mode": True, "maturity": "open",
        "verification": {"birthdate": "1984-06-01"}})
    assert r.status_code == 402, "a rated profile opened on an open plan"

    # clinical notes need a referral, and a referral needs a vault plan
    prof, it, me, prov = _referral_setup(client, "free", "acct-c9")
    out = client.post("/referrals/prepare", headers=me, json={
        "interactor_id": it["id"], "profile_id": prof["id"],
        "provider_id": prov["id"]})
    assert out.status_code == 402, "a referral opened on an open plan"
