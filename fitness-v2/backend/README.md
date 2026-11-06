# Top Hero Fit Fitness V2 backend core

This directory contains the authenticated workout-history, progress and competition
verification boundary used by Web and Android.

The WSGI entry point is `api.create_app_from_environment`. It deliberately has no
development credential fallback. Deployment must provide:

- `THF_WORKOUT_DB`: durable SQLite path for this recovery implementation;
- `THF_AUTH_ISSUER` and `THF_AUTH_AUDIENCE`: exact shared-account token scope;
- `THF_AUTH_KEYS_JSON`: rotated `{kid: base64url-secret}` verification key ring.

Ingress must terminate TLS and forward `wsgi.url_scheme=https`. The API rejects
non-HTTPS requests, missing/expired/revoked sessions, client-supplied account identity,
ambiguous stable record versions and idempotency-key reuse with a different body.

Run the contract suite with:

```sh
python -m unittest discover -s fitness-v2/backend/tests -v
python fitness-v2/tests/test_source_contract.py
```

This source checkpoint is not a deployment claim. A production database migration,
issuer/key configuration, HTTPS deployment and live authenticated probes remain separate
release gates.


## Competition API — current limited scope

The current competition implementation supports **strength-training volume only**:

- Sport: `strength_training`
- Metric: `strength_volume_kg_reps`
- Unit: `kg·reps` (sum of reps × load for non-warmup sets)
- Admin create: `POST /api/v2/admin/competitions` with a valid bearer session and `X-THF-Competition-Admin-Key`.
- Browse: `GET /api/v2/competitions` and `GET /api/v2/competitions/{competitionId}`.
- Join: `POST /api/v2/competitions/{competitionId}/join`.
- Submit: `POST /api/v2/competitions/{competitionId}/submissions` with only `workoutClientRecordId`; the server derives the score from the stored workout.
- Leaderboard: `GET /api/v2/competitions/{competitionId}/leaderboard?limit=50`.

The competition admin route fails closed with `503 COMPETITION_ADMIN_DISABLED` unless the owner-managed `THF_COMPETITION_ADMIN_KEY` is configured. No competition is seeded by this change.

**Trust boundary:** the current score is labelled `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED`; every competition response sets `rewardEligible=false`. The workout source and package are stored server-side but originate from the authenticated client's sync payload; they are not cryptographic device attestation. This leaderboard is provisional and must not authorize THF/token rewards, prize payouts, or claims of verified athletic performance.

Capacity checks and score snapshot/idempotency checks use SQLite `BEGIN IMMEDIATE` transactions so concurrent workers serialize the relevant reads and writes. A later workout version does not rewrite an already-recorded competition score; a resubmission with changed facts conflicts.

Before any reward eligibility is enabled, add a trusted activity-evidence pipeline, replay/anti-cheat controls, auditability, deployment secret ownership, privacy/policy review, and physical device validation.

OpenAPI contract version: `0.2.0` (competition routes and explicit unverified/reward-ineligible response schema).
