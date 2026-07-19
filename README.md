# QRME — AI Synthetic Profile Platform (v1)

![QRME — relationship-aware synthetic profiles](assets/design/00-cover.svg)

QRME lets a user create, customize, and interact with AI-driven synthetic
profiles — versions of themselves, another person (with consent/rights
handling), or a fictional persona. Profiles adapt to *who* they're talking to
(relationship-aware behavior) and *how engaged* that person is, while keeping
their core identity and boundaries fixed. See [docs/PRD.md](docs/PRD.md).

## What's in v1

| PRD feature | Implementation |
|---|---|
| Profile creation & onboarding (6.1) | `POST /profiles` with age/identity verification, guardian-consent flow for minor owners, consent/rights record for third-party profiles, anonymity toggle, source list |
| Relationship-aware modification (6.2) | `PUT /profiles/{id}/relationships/{interactor}` — type, nickname, tone, per-relationship topic boundaries fed into the persona prompt |
| Engagement-based learning (6.3) | `qrme/engagement.py` — auditable EMA score from message length, return visits, and explicit feedback; adapts style only, never identity/boundaries |
| Persistent memory (6.4) | Per-(profile, interactor) history included as chat context; `GET`/`DELETE /profiles/{id}/memory/{interactor}` for view/clear |
| Content moderation (6.5) | Every profile reply passes `qrme/moderation.py` before it's visible; `manual` mode holds all replies in an owner approval queue |
| Aging & lifecycle (6.6) | `aging_enabled` + `base_age` → effective age evolves with time; `successor_owner` for legacy succession |
| Adult content mode (6.7) | Age-gated at both ends: adult owner required to enable, verified 18+ interactor required to chat |
| In-app chat surface (6.8, v1) | `POST /profiles/{id}/chat` |

## Beyond the PRD

| Capability | Implementation |
|---|---|
| Profile purposes | `purpose` — `legacy_memorial`, `family`, `creator_persona`, `social_fan`, `companion_coach`, `enterprise_agent` — each conditions the persona prompt (brand-safe creator, wholesome family, knowledge-base enterprise agent, …) |
| Source material ("AI builds & trains the profile") | `POST`/`GET /profiles/{id}/sources` — photos, conversations, social posts, writings, voice notes, life events, knowledge entries, linked accounts; recent items are recalled naturally in every prompt |
| Age & maturity filters | Per-profile `maturity` dial (`strict` / `balanced` / `open`); minors are always held to strict, and `strict` filters flagged content even for verified adults |
| Multi-modal output | `ChatRequest.modality` (`text` / `voice` / `image` / `video`) → a render descriptor on the reply; voice reports whether it's preserved from voice-note sources (synthesis itself is out of scope for v1) |
| Cross-platform presence | `PUT`/`GET /profiles/{id}/surfaces` (chat, feed, web, AR/VR, wearable, `social:<name>`); chat validates the reporting surface |
| Posting at scale | `POST /profiles/{id}/compose` — a post in the profile's voice, through the same moderation pipeline (public posts always face the strict filter); `GET /profiles/{id}/posts` |
| Profile health, at a glance | `GET /profiles/{id}/stats` — sessions, memory entries, moderation pass rate, relationship graph size, engagement average, sources, posts, surfaces |
| AI Profile Marketplace | `POST`/`DELETE /profiles/{id}/marketplace` to list/unlist; `GET /marketplace?tag=` returns public discovery cards (display name, purpose, tags, blurb — never persona internals; anonymous profiles stay anonymous) |
| You own it / total control | `PATCH /profiles/{id}` (edit anytime), `GET /profiles/{id}/export` (full data export), `DELETE /profiles/{id}` (erases everything, including vaulted records) |
| Encrypted at rest (PDI tandem) | With `QRME_PDI_URL` + `QRME_PDI_TOKEN` (or an injected client), source-material content is sealed in PDI's AES-256-GCM vault (`qrme/pdi_client.py`); QRME keeps only key references, resolves them on read, and purges the vault on delete |

## Claims 21–26 (`qrme/adaptation.py`, `qrme/tasks.py`)

| Claim | Implementation |
|---|---|
| 21 — latent persona embeddings, persistent cross-session state | A per-(profile, interactor) named latent vector (engagement, warmth, depth, positivity, stress, continuity), EMA-updated after every interaction and versioned in `persona_embeddings`; `GET /profiles/{id}/embedding/{interactor}` |
| 22 — attention conditioning from engagement | The embedding renders as attention weighting in the system prompt (shared history, warmth, depth, reassurance weights), so engagement conditions where the model attends |
| 23 — real-time biometric monitoring during interaction | `ChatRequest.biometrics` (stress_level, heart rate, condition — typically from JIM-mini) is stored, feeds the embedding's stress dimension, and adds a monitored-situation note to the prompt |
| 24 — switching between domain-specialized agents | `PUT /profiles/{id}/specialists` maps domains (mental_health, medical, finance) to specialist profiles; biometric signals route the reply to the matching specialist, reported in `ChatResponse.handoff` |
| 25 — autonomous multi-step tasks with revocable vault access | `POST /profiles/{id}/grants` issues a scoped, revocable token; `POST /profiles/{id}/tasks` runs grant-check → scoped vault read → compose → moderation, logging step summaries only (raw vaulted data is never retained); `DELETE /grants/{id}` revokes instantly |
| 26 — encrypted, offline fine-tuning | `POST /profiles/{id}/finetune` recomputes all embeddings from stored history locally — no external calls — and seals the adaptation artifact in the PDI vault when configured; runs recorded with metrics and `external_transmission: false` |

## Architecture

- **API**: FastAPI (`qrme/api.py`), app factory `create_app()`.
- **Storage**: SQLite (`qrme/db.py`), path via `QRME_DB` (default `qrme.db`).
- **Persona conditioning**: `qrme/persona.py` builds the system prompt from
  profile identity + relationship + engagement + aging.
- **LLM**: official Anthropic SDK (`qrme/llm.py`), model `claude-opus-4-8`
  with adaptive thinking. Without credentials (or with `QRME_LLM=stub`) a
  deterministic stub provider is used, so everything runs offline.

## Run

```bash
pip install -e .[dev]
uvicorn qrme.api:app --reload
```

Set `ANTHROPIC_API_KEY` (or log in with `ant auth login`) for real model
replies; otherwise the stub provider answers. Override the model with
`QRME_MODEL`.

## Test

```bash
pytest
```

## Example flow

```bash
# 1. Create a profile (owner is age-verified)
curl -s localhost:8000/profiles -H 'content-type: application/json' -d '{
  "owner_id": "owner-1", "kind": "self", "display_name": "Dana",
  "persona": "A retired teacher who loves gardening and dry humor.",
  "verification": {"birthdate": "1984-06-01"}}'

# 2. Register an interactor and set the relationship
curl -s localhost:8000/interactors -d '{"display_name": "Sam", "birthdate": "2000-01-15"}' -H 'content-type: application/json'
curl -s -X PUT localhost:8000/profiles/$PROFILE/relationships/$INTERACTOR \
  -H 'content-type: application/json' \
  -d '{"relationship_type": "grandchild", "nickname": "kiddo", "tone": "playful", "boundaries": ["finances"]}'

# 3. Chat — reply is persona-, relationship-, and engagement-conditioned,
#    and moderated before it is shown
curl -s localhost:8000/profiles/$PROFILE/chat -H 'content-type: application/json' \
  -d '{"interactor_id": "'$INTERACTOR'", "message": "Tell me about your garden!"}'
```

## Design assets

The PRD-derived visual asset brief lives in
[docs/design/image-prompts.md](docs/design/image-prompts.md) — twelve
image-generation prompts covering the app icon, hero banner, onboarding flow,
and feature illustrations. Vector concept renditions of each (shared palette:
deep indigo / soft silver / warm amber) are in
[assets/design/](assets/design/), with a browsable
[gallery](assets/design/gallery.html).

## Out of scope for v1 (per PRD non-goals)

Biometric persona switching, robotic embodiment, media watermarking/provenance,
profile marketplace. Social-platform posting integrations are stubbed as a
`sources` list only.
