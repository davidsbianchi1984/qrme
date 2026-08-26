"""The voice binds to the account that brought it.

The binding read is public on purpose — a voice a stranger can hear is a
voice a stranger should be able to check the provenance of. Which means
every voice id on the deployment is one screen away from every other
tester; and the engine key is the deployment's, so nothing at the provider
stops a copied id from speaking. The warning was given the day the key
went deployment-wide: anyone who learns a voice id can bind it and speak
with somebody else's cloned voice.

    asked     whose voice is a bound voice
    mattered  a voice made of a real person's throat, claimable by whoever
              reads its id off a public payload, is impersonation with
              extra steps

So the first account to bind an id holds it. Their own profiles may share
it — one person's voice on that person's own cast is the product working —
another account is refused with the reason, and unbinding everywhere
releases the claim.

## Where the claim stops

The first live refusal this claim ever produced was over **Daniel** — the
premade British voice on the first row of the deployment's own picker.
Nobody's throat, offered to every account, and the claim handed him to
whichever account clicked first: a roster row everybody is shown that only
one account could have.

    asked     is this voice already spoken for
    mattered  was it anybody's to speak for in the first place

So the claim is bounded by the provider's own ``cloned`` mark, which is the
fact it was written to protect. Premade library voices are everybody's; a
voice the library does not know stays claimable, because when nothing can
say a voice is nobody's it is treated as somebody's — the ids these tests
invent land on that side, which is why the guards above needed no change.
"""

from __future__ import annotations


def a_profile(client, owner: str, name: str):
    r = client.post("/profiles", json={
        "owner_id": owner, "kind": "self", "display_name": name,
        "persona": "A retired teacher who likes gardening and dry humor.",
        "verification": {"birthdate": "1984-06-01"}, "plan": "pro"})
    assert r.status_code == 201, r.text
    return r.json()["id"], r.json()["owner_token"]


def head(token):
    return {"authorization": f"Bearer {token}"}


def _bind(client, pid, tok, voice="v-david"):
    return client.put(f"/profiles/{pid}/voice",
                      json={"voice_id": voice, "label": "A made voice"},
                      headers=head(tok))


def test_another_account_cannot_bind_a_claimed_voice(client):
    pid_a, tok_a = a_profile(client, "owner-a", "Ada")
    pid_b, tok_b = a_profile(client, "owner-b", "Bea")
    assert _bind(client, pid_a, tok_a).status_code == 200
    r = _bind(client, pid_b, tok_b)
    assert r.status_code == 422
    assert "already spoken for" in r.text
    # And the refusal changed nothing: B's profile still has no voice.
    assert client.get(f"/profiles/{pid_b}/voice").json()["speaks"] is False


def test_the_same_account_shares_its_voice_across_its_cast(client):
    pid_1, tok_1 = a_profile(client, "owner-c", "Cal")
    pid_2, tok_2 = a_profile(client, "owner-c", "Cam")
    assert _bind(client, pid_1, tok_1).status_code == 200
    assert _bind(client, pid_2, tok_2).status_code == 200
    assert client.get(f"/profiles/{pid_2}/voice").json()["speaks"] is True


def test_unbinding_everywhere_releases_the_claim(client):
    pid_a, tok_a = a_profile(client, "owner-d", "Dee")
    pid_b, tok_b = a_profile(client, "owner-e", "Eve")
    assert _bind(client, pid_a, tok_a).status_code == 200
    assert _bind(client, pid_b, tok_b).status_code == 422
    # The claim is the bindings, not a separate ledger: when the last row
    # holding this id under owner-d goes, the id is anybody's to bring.
    client.put(f"/profiles/{pid_a}/voice", json={"voice_id": ""},
               headers=head(tok_a))
    assert _bind(client, pid_b, tok_b).status_code == 200


def test_a_different_voice_id_is_untouched_by_the_claim(client):
    pid_a, tok_a = a_profile(client, "owner-f", "Fay")
    pid_b, tok_b = a_profile(client, "owner-g", "Gus")
    assert _bind(client, pid_a, tok_a, voice="v-one").status_code == 200
    assert _bind(client, pid_b, tok_b, voice="v-two").status_code == 200


DANIEL = "onwK4e9ZLuTAKqWW03F9"


def test_a_premade_library_voice_is_everybodys(client):
    """Two accounts, one stock voice, no refusal. The picker offers it to
    both of them, and a picker that offers what the claim then refuses is
    the defect this guard exists to keep out."""
    from qrme import spoken
    assert any(v["id"] == DANIEL and not v["cloned"]
               for v in spoken.FALLBACK_VOICES)
    pid_a, tok_a = a_profile(client, "owner-h", "Hal")
    pid_b, tok_b = a_profile(client, "owner-i", "Ida")
    assert _bind(client, pid_a, tok_a, voice=DANIEL).status_code == 200
    assert _bind(client, pid_b, tok_b, voice=DANIEL).status_code == 200
    assert client.get(f"/profiles/{pid_b}/voice").json()["speaks"] is True


def test_the_boundary_is_the_cloned_mark_and_not_the_list(client):
    """`_shared` reads what the library says a voice is, not which file the
    id happens to sit in — a cloned voice that reached the library keeps
    the claim, however it got there."""
    from qrme import spoken
    cloned = dict(spoken.FALLBACK_VOICES[0], id="v-somebodys-throat",
                  cloned=True)
    spoken.FALLBACK_VOICES.append(cloned)
    try:
        pid_a, tok_a = a_profile(client, "owner-j", "Jo")
        pid_b, tok_b = a_profile(client, "owner-k", "Kim")
        assert _bind(client, pid_a, tok_a,
                     voice="v-somebodys-throat").status_code == 200
        r = _bind(client, pid_b, tok_b, voice="v-somebodys-throat")
        assert r.status_code == 422
        assert "already spoken for" in r.text
    finally:
        spoken.FALLBACK_VOICES.pop()
