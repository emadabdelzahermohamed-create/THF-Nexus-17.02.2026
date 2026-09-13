# THF Apps Factory checkpoint — 2026-09-14 01:08 EET

## Truth boundary

`FINAL_OR_PLAY_READY=FALSE`

Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity, federation and cross-app handoffs. Dedicated native game streams and token finance excluded.

No production signing, public rollout, paid spend, owner verification, legal acceptance, treasury/token action, native game mutation, or WAVE mutation was performed.

## Same-SHA skip discipline

Previously proven Core and runtime-bound Android candidate package gates were not re-run because no regression evidence was found for those exact SHAs. Existing physical-device requirements remain unchanged.

## THF Pass reversible private runtime rehearsal

Workflow: `THF Pass Private Runtime Rehearsal V1`
Successful run: `34785750443`
Workflow commit: `7f90422c4434efa0c5c9db1ba5756df2198f6c8c`
Artifact: `THF-PASS-PRIVATE-RUNTIME-REHEARSAL-V1`
Artifact ID: `10326054232`
Artifact ZIP SHA-256: `d5037443fc4fa4445cadbb985fc087b3fd8fcc149e0fab720cb99335ff917eb2`

The first rehearsal run exposed a CI assumption that the identity candidate text SHA would exactly equal the earlier disposable candidate despite equivalent semantics. This tooling issue was corrected automatically; no product baseline was mutated.

Immutable deployed baseline verified before and after rehearsal:
- `src/thf/app.py`: `471a8e0c6b67320386db6efcd32a3718265a645a30af3d7a9ea95060258058be`
- `src/thf/identity/service.py`: `8421a63db2e05bbd3b10b60da3edb0a3190ad7c2ea0498f4a1a704c3f7827b9f`

Exact disposable rehearsal candidate:
- `app.py`: `7f839cdba4307c5cd9a9aa258c4a3cdbf8bb55308f84ddda2b0217582ecc1ab2`
- `identity/service.py`: `36c9a173d394a9c2d19c931dbf8e89ab5478c27b197b278ce76b9b9b8286443c`

Private runtime evidence proven on `127.0.0.1` with a temporary DB and non-production test identity:
- register/login: PASS;
- refresh token rotation: PASS;
- old token rejected after refresh: PASS;
- logout revokes current session: PASS;
- revoke-all invalidates concurrent sessions and a handoff-issued session: PASS;
- one-time audience-bound handoff create/exchange: PASS;
- handoff replay rejected: PASS;
- existing HTTP/security/unified-runtime regression suite: 16 tests PASS;
- deployed baseline source hashes unchanged after rehearsal: PASS;
- rollback proof: PASS;
- public endpoint changed: FALSE;
- deployment performed: FALSE.

This closes the isolated-runtime lifecycle/federation rehearsal only. It does not constitute reachable HTTPS staging proof or FINAL readiness.

## Shared notification contract and fail-closed gate

Added:
- `ReleaseOps/apps_factory/contracts/thf_notifications_v1.json` — commit `b760cebfa2fd6d36de9c43ac708d8f18a5440252`;
- `ReleaseOps/validators/validate_thf_notifications_contract.py` — commit `e8c176f13679707a8773b90872b1436cd231270f`;
- regression tests — commit `ed7c4c82df070b8f83457310f316e08df814d63e`;
- `THF Apps Notification Contract Gate V1` — commit `e01b22b198141589dccc4ad128f05dde6f607bd6`.

Gate run `34785707053`: SUCCESS.

The contract keeps `PUSH_READY=FALSE` and enforces API 36, HTTPS/WSS transport, contextual permission handling, secure provider-token storage/registration/rotation/logout revocation, no query-string credentials, allowlisted credential-free deep links, Data Saver behavior, RTL/localized content, accessibility labeling, truthful offline behavior, and physical-device receive/tap/background-resume evidence before promotion. Source-only/mock-only PASS is forbidden.

Exact-source inventory remains `NONE_ACROSS_NINE_APPS`; this contract is a release-control prerequisite, not evidence that push is implemented.

## Current blockers / next executable work

1. THF Pass lifecycle/federation candidate is still not deployed to an isolated reachable HTTPS staging service. Live external refresh/logout/revoke/handoff claims remain false until a reversible non-public staging deployment, health/auth/session probe, and rollback proof succeed.
2. A non-production test identity is required for the later externally reachable HTTPS login/refresh/expiry/revoke/handoff test. Production credentials must not be used.
3. Spark and Rush still require genuine source test coverage; Gradle `NO-SOURCE` is not a test PASS.
4. App-specific push implementation/provider integration remains absent across the nine exact authoritative app sources. The shared contract now prevents false promotion but `PUSH_READY=FALSE` remains correct.
5. Every exact Android candidate still requires physical-phone install/launch/touch/responsive-layout/orientation/background-resume/offline-network/Data Saver/accessibility/RTL/core-user-journey/crash-free evidence before FINAL/PLAY_READY.
6. Production signing, Play publication, OAuth/legal/owner approvals remain later owner-controlled gates.

Next safe autonomous block: package the tested Pass candidate as a reproducible exact-hash patch, rehearse it on an isolated non-public HTTPS staging instance with exact pre/post hashes and rollback, then add real Spark/Rush tests and app-specific notification implementation lanes without changing the public endpoint.
