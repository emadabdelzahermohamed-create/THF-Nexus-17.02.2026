# THF Apps Factory Checkpoint — 2026-09-13 21:10 EET

## Scope and truth boundary

This checkpoint covers THF Core and the non-game app factory (Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command and shared THF Pass/federation coordination). Native dedicated game streams and token finance are excluded. No production signing, public rollout, paid spend or token/treasury action was performed.

`FINAL_OR_PLAY_READY=FALSE`

Physical-phone acceptance remains mandatory and must be bound to the exact APK SHA. Source/static/transport evidence below does not replace install/launch/touch/layout/background-resume/offline-network/core-journey/crash-free evidence.

## Authoritative source state preserved

No already-proven package gate was repeated merely for status. Core RC6 remains `PASS_PREEXISTING_SAME_SHA` and is not rebuilt without regression evidence. The nine current app source identities remain the factory-state values recorded in `THF_APPS_FACTORY_STATE_20260913_2035_EET.json`, including Vault/Signal RC4-BF1.

## Block A — runtime endpoint transport probe

Created `.github/workflows/thf-apps-backend-reachability-v1.yml` at commit `5c23b470a4846f2b5fcf7a8b26750788bc187818`.

GitHub Actions run `34773438267` completed SUCCESS and emitted artifact `THF-APPS-BACKEND-REACHABILITY-V1` (artifact id `10321964268`, artifact ZIP digest `sha256:7b9f973b83df2d52a934968281a0c4cf408e41c03d813ad52b6cb0fb8d31e847`). Exact source archives were re-hashed before inspection.

Literal shipping-source HTTPS origins discovered and transport-probed:

- Pulse RC3: `https://www.who.int` -> HTTP 200; `https://pubmed.ncbi.nlm.nih.gov` -> HTTP 200; `https://esm.sh` -> HTTP 200.
- Vault RC4-BF1: `https://solscan.io` -> HTTP 403 (reachable transport).
- Signal RC4-BF1: `https://api.telegram.org` -> HTTP 302 (reachable transport).
- Command RC3: `https://solscan.io` -> HTTP 403 (reachable transport).
- Forge, Echo, Codex, Spark and Rush: no literal HTTPS origin was emitted by the shipping-runtime URL scanner.

`UNREACHABLE_LITERAL_ORIGIN_COUNT=0`

This is explicitly non-promotional. Most discovered origins are external reference/provider surfaces, not proof of a THF backend. BuildConfig/injected endpoint configuration and live THF health/auth/session remain separate unresolved runtime gates. A TLS response, including 401/403/404, proves only transport reachability and not successful auth or user-flow behavior.

## Block B — Spark/Rush regression lane

Created exact-source Spark/Rush Android regression workflow at commit `b393cc10f2ffc2db3fdaa5c70ceccb7d49d0f65c`. First run `34773457906` failed safely before executing Gradle tasks because the authoritative archives do not include `gradlew`. This was a CI/tooling assumption, not application regression.

The workflow was repaired at commit `c6f39bc4e763ca737fd82a0730bae6cfc2cb3477` to provision Gradle 8.13 explicitly, matching the already-working hosted candidate pipeline. Run `34773571994` is the remediation run; readiness must not be promoted until its two matrix jobs complete and their artifacts are inspected.

## Block C — identity/federation fail-closed tooling

Added `ReleaseOps/validators/audit_identity_handoff_contract.py` and regression tests. The auditor inspects only shipping runtime paths and inventories:

- auth/session lifecycle surfaces including logout/revocation and expiry/refresh handling;
- secure-storage implementation surfaces;
- THF Pass/federation binding surfaces;
- send + receive cross-app handoff surfaces;
- sensitive token/session values embedded in query-string-like source patterns;
- cleartext HTTP/WS runtime endpoint patterns.

It is deliberately non-promotional: source contract evidence does not prove live identity service success or a physical cross-app handoff. Exact-source portfolio workflow `.github/workflows/thf-apps-identity-handoff-audit-v1.yml` was added at commit `eb7524d797eda5497ae86716e55f4df2e5d62d38` and must be evaluated by its emitted evidence before any readiness change.

## Current blockers / next executable work

1. Complete and inspect Spark/Rush exact-source Gradle regression run after the safe CI remediation.
2. Complete and inspect the nine-app identity/handoff audit. Treat missing surfaces as engineering debt, not as implicit PASS.
3. Resolve candidate-bound THF backend/Pass runtime configuration and then test reachable HTTPS health/auth/session, logout/revocation and expired-session behavior. Current literal URL transport evidence is insufficient.
4. Add or recover real regression tests for Spark/Rush if the Android source has no discoverable unit/lint test task coverage; do not fabricate pytest PASS.
5. Physical-phone acceptance for every exact APK SHA remains an owner/device gate before FINAL/PLAY_READY.

Rollback is Git-native: each new block is isolated in its own commit and can be reverted without changing validated app source archives or production infrastructure.
