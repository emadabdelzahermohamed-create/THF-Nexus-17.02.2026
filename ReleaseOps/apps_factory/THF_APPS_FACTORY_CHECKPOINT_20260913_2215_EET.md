# THF Apps Factory checkpoint — 2026-09-13 22:15 EET

## Truth boundary

Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity and cross-app handoffs. Dedicated native-game streams and token finance are excluded.

`FINAL_OR_PLAY_READY=FALSE`

No production signing, public rollout, paid spend, legal acceptance, identity verification, treasury action or token signing was performed.

## Authoritative inputs retained

Core RC6 exact APK SHA-256 remains `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`; same-SHA proven gates were not rerun because no regression evidence was found.

The exact app-source matrix remains:

- Pulse RC3 — `71a16804e7c138535bb373263ae4374d8a5eef410ffe83b165472c684b6c8b10` — `com.topherofit.thf.pulse`
- Forge RC3 — `0f7a416a9e14af9dbb3cdcb26bfb891e0c680d4a33a73d60601eda215e697e51` — `com.topherofit.thf.forge`
- Echo RC4 — `87c6a532fc56870b9a4c1039ac1f44b43e1a2f4c5c4518caf0d6537c61704226` — `com.topherofit.thf.echo`
- Codex RC4 — `c5108b257b5e9af6849c43df7b7aa671e586bb4a9c91964566c85b1a6329e83d` — `com.topherofit.thf.codex`
- Spark RC3 — `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0` — `com.topherofit.thf.spark`
- Rush RC3 — `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b` — `com.topherofit.thf.rush`
- Vault RC4-BF1 — `dd6db86d7532f773a8d1d2662bf466bdcc0f1c64a863602ecdd1267c8f82fa33` — `com.topherofit.thf.vault`
- Signal RC4-BF1 — `377044263fa0fc366afe67c6b42ccf4f3e2d1bc75769350f2ee885983f820ddf` — `com.topherofit.thf.signal`
- Command RC3 — `f7da9039041b8142d795e96934b95f00b83ac8fb5e3d6f5d9bfbff0aeb2eb408` — `com.topherofit.thf.command`

A separate Spark/Rush RC4 workflow exists in the dedicated game-labelled stream and passed there, but it is not silently substituted for the later authoritative Apps matrix above. Project isolation is preserved.

## Block 1 — deep runtime source contract audit

Added:

- `ReleaseOps/validators/audit_app_runtime_contract_v2.py`
- regression tests in `ReleaseOps/validators/test_audit_app_runtime_contract_v2.py`
- `.github/workflows/thf-apps-runtime-contract-audit-v2.yml`

The first CI setup failure was traced to an invalid truncated `upload-artifact` pin and fixed immediately. The successful exact-source run is `34776549014` on commit `79bbf9828d6262a6cc254dae9f16ba9c50529c5f`.

Every ZIP was downloaded through Drive read-only WIF, SHA-256 matched against the matrix, and archive integrity was checked before inspection.

### Confirmed source-contract positives across all nine apps

- backend configuration surface exists;
- network-state/Data-Saver-related surface exists;
- genuine local/offline storage surface exists;
- cross-app handoff send/receive surface exists;
- no placeholder runtime URL detected;
- no cleartext HTTP/WS runtime transport detected;
- no source pattern indicating fake offline authoritative economy/social/ranked-state success/commit after false-positive hardening.

The offline-authority detector was corrected and regression-protected after a Spark line containing `offline_fallback` and a later unrelated database `commit()` produced a cross-line false positive.

### Identity/session gaps now separated precisely

| App | Auth | Session | Expiry | Refresh | Logout | Revoke |
|---|---:|---:|---:|---:|---:|---:|
| Pulse | no | yes | no | no | no | no |
| Forge | yes | yes | yes | no | no | no |
| Echo | yes | yes | yes | no | no | no |
| Codex | yes | yes | yes | no | no | no |
| Spark | yes | yes | yes | no | no | no |
| Rush | yes | yes | yes | no | no | no |
| Vault | no | no | no | no | no | no |
| Signal | no | no | no | no | no | no |
| Command | no | no | no | no | no | no |

This is source evidence only. It does not prove a reachable THF auth service or successful token lifecycle.

### Notifications

The notification source contract is absent in all nine authoritative sources: no complete registration + Android notification-channel + receiver/action contract was detected. This is now an explicit engineering backlog item rather than an assumed feature.

## Block 2 — visible controls and route wiring

Added:

- `ReleaseOps/validators/audit_visible_action_contract.py`
- regression tests in `ReleaseOps/validators/test_audit_visible_action_contract.py`
- `.github/workflows/thf-apps-visible-action-audit-v1.yml`

The auditor was iteratively hardened against real source styles: legacy DOM named IDs (`save.onclick`), selector helpers (`$('#react').onclick`), helper-bound forms (`wire(form,'/api/...')`) and parameterized API prefixes (`/api/handoff/` -> `/api/handoff/{target}`). These were tooling false positives, not silently treated as app defects.

Final exact-source run `34776819955` on commit `6340b51dd4a9a014982f6ce7ba27bd45e037ce12` reports all nine apps with:

- zero orphan visible buttons detected;
- zero dead anchors detected;
- zero orphan forms detected;
- zero unmapped literal local API references detected;
- `source_action_contract=true`.

This establishes source-level wiring only. It **does not** establish touch behavior, responsive layout, successful HTTP responses, cross-app navigation on-device, or end-to-end user journeys.

## Mobile Real-Function Release Policy state

No app was promoted to FINAL or PLAY_READY. Required evidence still missing includes:

1. effective exact-candidate THF backend and THF Pass HTTPS/WSS endpoints plus real health/auth/session tests;
2. refresh, logout, revocation and expired-session behavior protected by runtime/integration tests;
3. a concrete THF Pass standalone/service contract and candidate-bound endpoint evidence;
4. notification implementation and tests (or an explicit per-app product decision that notifications are not applicable);
5. real Spark/Rush unit-test sources rather than `NO-SOURCE` Gradle test tasks;
6. exact-APK physical-phone install/launch/touch/layout/orientation/background-resume/offline-network/core-journey/crash-free evidence;
7. production signing / Play / legal owner gates when later authorized.

## Next safe executable blocks

- Trace the effective generated candidate values for `THF_BASE_URL` / `THF_PASS_URL` and run fail-closed health/auth probes without exposing secrets.
- Define and regression-test the shared session lifecycle contract (refresh, logout, revoke, expiry) before patching individual apps.
- Add a shared notification foundation with API-36-safe permission/channel behavior where product requirements call for notifications; do not claim push delivery without provider/runtime evidence.
- Build real Spark/Rush unit tests around score/session integrity and offline-vs-ranked boundaries.
- Keep exact package IDs, API 36, localization/RTL, accessibility, Data Saver, project isolation and rollback gates unchanged.
