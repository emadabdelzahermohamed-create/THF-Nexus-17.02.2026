# THF Apps Factory checkpoint — 2026-09-14 00:08 EET

## Truth boundary

`FINAL_OR_PLAY_READY=FALSE`

Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity, federation and cross-app handoffs. Dedicated native game streams and token finance excluded.

No production signing, public rollout, paid spend, owner verification, legal acceptance, treasury action, token signing, or WAVE mutation was performed.

## Same-SHA skip discipline

No previously proven Core or runtime-bound app package gate was re-run because no regression evidence was found for those exact candidate SHAs. Existing physical-device requirements remain unchanged.

## New fail-closed federation contract

Added `ReleaseOps/apps_factory/contracts/thf_pass_federation_handoff_v1.json`, validator `tools/releaseops/validate_thf_pass_contract.py`, six regression tests, and `THF Apps Pass Contract Gate V1`.

Gate run: `34782662329` — SUCCESS.

The contract pins the deployed baseline hashes, tested candidate hashes, required session semantics, one-time short-lived audience-bound handoff semantics, query-token prohibition, HTTPS exchange requirement, and owner/device gates. It explicitly remains candidate-only and FINAL/PLAY_READY false.

## THF Pass federation/handoff disposable candidate

Workflow: `THF Pass Federation Handoff Candidate V1`
Run: `34782754469`
Commit: `2c66d90c315f6e2100abfccd252ffa4f169a58cf`
Result: **SUCCESS**
Artifact: `THF-PASS-FEDERATION-HANDOFF-CANDIDATE-V1`
Artifact ID: `10325945285`
Artifact SHA-256: `4e60829a240b3d947a4608ebd8c7cac4db35ab7ce9e4e5eaa0cef52e6848323f`

Exact immutable deployed baseline used:
- `src/thf/app.py`: `471a8e0c6b67320386db6efcd32a3718265a645a30af3d7a9ea95060258058be`
- `src/thf/identity/service.py`: `8421a63db2e05bbd3b10b60da3edb0a3190ad7c2ea0498f4a1a704c3f7827b9f`

Tested disposable federation candidate:
- `app.py`: `7f839cdba4307c5cd9a9aa258c4a3cdbf8bb55308f84ddda2b0217582ecc1ab2`
- `identity/service.py`: `547644ffa9f9bd4d4f09dc68da551749eefada1939510f3d803b07d939bd068f`

Candidate behavior proven in isolated copy:
- lifecycle refresh/logout/revoke implementation carried forward;
- one-time handoff code generation;
- locked THF app audience allowlist;
- 90-second handoff expiry;
- subject and audience binding;
- replay rejection;
- wrong-audience rejection;
- unknown audience rejection;
- handoff exchange issues a normal server session only after successful one-time consumption;
- query-string credential handoff is not accepted; exchange reads JSON body;
- deployed source hashes remained unchanged after tests.

Candidate-specific federation tests: **4 passed**.
Existing HTTP/security/unified-runtime regression suite: **16 passed**.
Total exercised in this candidate lane: **20 passed**.

`MUTATION_PERFORMED=FALSE`
`DEPLOYMENT_PERFORMED=FALSE`

## Contract binding update

The federation contract candidate hashes were advanced from the earlier lifecycle-only candidate to the exact tested federation candidate hashes in commit `89395753b107a2bc72376b1bd008f452c9d138b2`. Runtime evidence fields remain false because this candidate has not been deployed.

## Current blockers / next executable work

1. THF Pass staging still lacks the lifecycle/federation candidate; live refresh/logout/revoke/handoff claims remain false until a reversible candidate deployment and rollback rehearsal succeeds.
2. A non-production test identity is still required later for reachable HTTPS login/refresh/expiry/revoke/handoff validation; no production credential should be used.
3. Spark and Rush still require real test-source coverage beyond Gradle NO-SOURCE.
4. Exact-source notification inventory remains NONE across the nine apps; push readiness is false until a real shared contract plus app-specific implementation and provider/device evidence exist where required.
5. Every exact Android candidate still requires physical-phone install/launch/touch/layout/orientation/background-resume/offline-network/Data Saver/accessibility/RTL/core-journey/crash-free evidence before FINAL/PLAY_READY.
6. Production signing and public Play rollout remain later owner-controlled gates.

Next safe autonomous block: build a reversible non-public staging deployment rehearsal for the tested Pass candidate with exact pre/post hashes and rollback proof; keep public endpoint unchanged, then add genuine Spark/Rush source tests and shared notification contract enforcement.
