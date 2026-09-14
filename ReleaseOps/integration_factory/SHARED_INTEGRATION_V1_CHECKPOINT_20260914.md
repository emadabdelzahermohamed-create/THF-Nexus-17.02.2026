# THF Shared Integration V1 — checkpoint — 2026-09-14

## Scope completed
This batch establishes reusable shared contracts for THF Identity/federation, Google sign-in boundary validation, guest-to-account linking, health-provider provenance/deduplication, approved product naming/package compatibility, and operator-only Admin/Publisher visibility/RBAC. WAVE and financial/token execution were not touched.

## Shared identity / Google boundary
- Android integration contract is Credential Manager-first and allows Google/passkey/password-or-email-code flows at the shared contract layer.
- Mobile config requires a Google server client ID and rejects client secrets from application configuration.
- Google ID-token claims are rejected unless the caller first proves cryptographic signature/JWK verification. The shared helper then fail-closes issuer, audience, expiration, subject and verified-email claims.
- Production Google OAuth console/brand/consent/client configuration is intentionally still external and is NOT claimed configured.
- Guest-to-account linking requires verified identity proof and rejects identity collisions.

## Admin / Publisher isolation
- `THF Admin` / legacy `command` remains package `com.topherofit.thf.command` and requires `owner` or `admin`.
- `THF Publisher` / legacy `signal` remains package `com.topherofit.thf.signal` and requires `owner`, `admin` or `publisher`.
- Ordinary user/member/guest roles do not receive Admin or Publisher in `visible_products()`.
- Operator routes fail closed on server-authoritative role input; hidden UI is explicitly not treated as security.

## Health bridge contract
- Health Connect is the primary Android semantic health bridge.
- Samsung Health Data SDK is represented as an optional provider adapter boundary; no production partner access is claimed.
- Shared semantic metrics currently include activity, workout, steps, distance, calories, heart rate, sleep, weight and body-fat percentage.
- Every record carries provider + provider source-record ID + metric + time range and receives a deterministic SHA-256 deduplication key.
- Permission plans require explicit consent, tolerate provider absence, disable background/historical reads by default, and never treat raw provider data as reward authority.
- Physical Health Connect/Samsung/device verification remains required.

## Product names and package compatibility
Approved display names are now represented centrally while preserving internal legacy IDs and package IDs: THF Hub/Core, THF Fitness/Pulse, THF Market/Forge, THF Community/Echo, THF Learn/Codex, THF Wallet/Vault, THF World/Terra, THF Arena/Rift, THF Learn Games/Spark, THF Motion Games/Rush, THF Publisher/Signal and THF Admin/Command.

## Exact files
- `ReleaseOps/integration_factory/shared_integration_contracts.py`
- `ReleaseOps/integration_factory/test_shared_integration_contracts.py`
- `ReleaseOps/integration_factory/ANDROID_SHARED_INTEGRATION_V1.json`
- `.github/workflows/thf-shared-integration-v1.yml`

## CI evidence
GitHub Actions workflow `THF Shared Integration V1` run `34888971506`, job `104126560378` completed successfully on the exact updated shared-integration line. Passed steps:
- checkout: PASS
- Python compile: PASS
- shared integration regressions: PASS
- machine-readable Android integration manifest validation: PASS

The regression suite explicitly covers ordinary-user operator invisibility, role boundaries, rejection of mobile OAuth secrets, mandatory prior Google signature verification, Google audience/email checks, health provenance deduplication, consent-first/non-authoritative health permissions, verified guest linking and release-truth boundaries.

## Release truth / external blockers
The following remain FALSE / unproven and are not promoted by this checkpoint:
- Google OAuth console configured for production
- backend Google signature-verifier binding to a production endpoint
- Samsung Health partner registration / production access
- physical-device Health Connect validation
- physical-device Samsung Health validation
- physical-device application acceptance
- FINAL / PLAY_READY

Next integration work should consume these shared contracts from the concrete Android app/game clients and backend identity endpoints, then bind real provider SDKs/configuration without duplicating per-product policy logic.
