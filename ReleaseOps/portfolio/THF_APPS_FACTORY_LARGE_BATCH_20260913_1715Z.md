# THF Apps Factory — Large-Batch Checkpoint — 2026-09-13 17:15Z

## Scope

Non-native-game / non-token-finance application lane: Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass, shared identity/federation and cross-app handoffs.

## Skip / preservation rule

- THF Core RC6 exact-candidate package gate was already proven for its existing SHA; it was not rebuilt in this batch because no regression evidence exists.
- Existing APPS-RC3 source regression results were preserved; this batch did not re-label source/static PASS as mobile release PASS.
- No production signing, Play public rollout, treasury action, token signing, paid spend or irreversible infrastructure cutover was performed.

## RC3 authoritative source recovery

The nine authoritative APPS-RC3 source archives were recovered from the persistent THF workspace, content-hash checked against the recorded RC3 source-of-truth, ZIP-integrity checked, staged to `THF Apps Factory Staging`, and shared read-only with the release-builder service account.

| App | Package | Authoritative RC3 source SHA-256 |
|---|---|---|
| Pulse | `com.topherofit.thf.pulse` | `71a16804e7c138535bb373263ae4374d8a5eef410ffe83b165472c684b6c8b10` |
| Forge | `com.topherofit.thf.forge` | `0f7a416a9e14af9dbb3cdcb26bfb891e0c680d4a33a73d60601eda215e697e51` |
| Echo | `com.topherofit.thf.echo` | `40a197b60563e560cab93ba0a64c859d9b650da222fdaec933993977d63902ab` |
| Codex | `com.topherofit.thf.codex` | `3d60cc550732468c89fe120f552def53ac798646d065e94efa153f8979e15b1e` |
| Spark | `com.topherofit.thf.spark` | `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0` |
| Rush | `com.topherofit.thf.rush` | `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b` |
| Vault | `com.topherofit.thf.vault` | `7a2ba4236a0c42d2521fa2eb2c2d7108ceba0d2929ebdf68959a6eacbce4a793` |
| Signal | `com.topherofit.thf.signal` | `51d7ce44fed24f7490973bcc7e019a8430157c4d5bfa1541e7cb590b0b7957c0` |
| Command | `com.topherofit.thf.command` | `f7da9039041b8142d795e96934b95f00b83ac8fb5e3d6f5d9bfbff0aeb2eb408` |

A new fail-closed exact-candidate lane was added at `.github/workflows/thf-apps-rc3-exact-candidate-drive-v2.yml` (workflow source commit `2b534c2c0883df4bf77be164b16e13c6cce01b8d`). Its first attempt correctly failed because the newly staged Drive files were not yet shared with the WIF release-builder service account. That access issue was repaired by granting the builder read-only access to each of the nine exact files. Attempt 2 then passed the exact Drive download + SHA verification stage and proceeded to isolated GCP staging/build. The final build result must be recorded separately when the run completes; no APK PASS is claimed here.

## Mobile Real-Function source audit findings

A fresh runtime-source scan found two release-policy defects in APPS-RC3 that were not acceptable as final:

1. **Codex** had a user-visible THF Link anchor hard-coded to `http://127.0.0.1:8102/...` on the home route.
2. **Echo** seeded an enabled demo ad campaign whose landing URL was `https://example.com`.

Both are prohibited by the real-function policy: network-required cross-app behavior cannot depend on loopback, and a placeholder external destination cannot be represented as a real campaign.

## RC4 partial hardening — Codex

New source artifact: `THF_Codex_APPS_RC4_RELEASE_POLICY_SOURCE.zip`

- SHA-256: `c5108b257b5e9af6849c43df7b7aa671e586bb4a9c91964566c85b1a6329e83d`
- Package identity preserved: `com.topherofit.thf.codex`
- Android API 36 source identity preserved.
- Hard-coded loopback handoff removed from the visible home route.
- Optional media/store integration bases are disabled when absent and fail closed unless they are external HTTPS URLs.
- Partner/ad seed is not created when a real HTTPS store base is unavailable.
- Clean-extract source verification: `compileall PASS`; `pytest 8 passed`.
- Runtime scan excluding tests/docs: no `http://localhost`, `http://127.0.0.1`, `http://0.0.0.0`, `https://example.com`, or `usesCleartextTraffic="true"` finding.

Readiness: `SOURCE_HARDENED_NOT_FINAL`. Exact RC4 APK inspection and physical-device evidence still required.

## RC4 partial hardening — Echo

New source artifact: `THF_Echo_APPS_RC4_RELEASE_POLICY_SOURCE.zip`

- SHA-256: `87c6a532fc56870b9a4c1039ac1f44b43e1a2f4c5c4518caf0d6537c61704226`
- Package identity preserved: `com.topherofit.thf.echo`
- Android API 36 source identity preserved.
- The fake/example seeded ad was removed.
- Admin-created campaign landing URLs are fail-closed unless external HTTPS.
- Legacy invalid campaigns are disabled before serving/click settlement.
- Protected-context ad suppression remains intact.
- Clean-extract source verification: `compileall PASS`; `pytest 6 passed`.
- Runtime scan excluding tests/docs: no `http://localhost`, `http://127.0.0.1`, `http://0.0.0.0`, `https://example.com`, or `usesCleartextTraffic="true"` finding.

Readiness: `SOURCE_HARDENED_NOT_FINAL`. Exact RC4 APK inspection and physical-device evidence still required.

## Truth boundary / remaining gates

No app in this checkpoint is promoted to `FINAL` or `PLAY_READY` solely from source/build evidence. Mandatory remaining evidence includes:

- exact-candidate package/payload/SHA inspection for each current source candidate;
- reachable HTTPS/WSS backend health/auth for every network-required flow;
- phone install, launch, touch, responsive layout/orientation, background/resume, real offline/network transition, core journey and crash-free smoke;
- accessibility, Data Saver, RTL/localization, notification behavior and rollback acceptance;
- production signing/Play-track work only after the relevant owner-controlled signing/console gates.

THF Pass remains a federation/backend/SDK dependency and is not represented as a fake standalone Play-ready client. Signal/Command remain internal-control surfaces unless separately approved for public distribution.
