# THF Apps Factory Checkpoint — Raw ADB Evidence V9

## Scope / same-SHA authority
This pass covers THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass, shared identity/federation, cross-app handoffs and release controls. Dedicated native game implementation and token finance were excluded.

Authoritative app state remains `ReleaseOps/apps_factory/THF_APPS_FACTORY_STATE_20260914_1115_EET.json` plus `THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json`. The exact Core + nine app candidate APK/source SHA bindings did not change, so proven same-SHA package/API-36 work was skipped rather than rebuilt. All ten exact candidates remain `PENDING_PHYSICAL_PHONE`.

## Finding
V8 correctly required one SHA-bound offline -> local -> online transcript, but that transcript could still be the sole artifact for the transition. A structurally valid summary file is not equivalent to separate raw ADB captures from the physical-phone observation window.

## V9 implemented
PR #14 was merged as `4fb2892ad2ce69ed82f36c1fd62331ce17b38d24`.

V9 layers V8 and additionally requires:
- exactly three raw captures: offline connectivity, local UI state, online connectivity;
- three distinct files and distinct SHA-256 digests;
- approved ADB command binding for each capture;
- successful ADB exit-code binding;
- exact session/package/APK SHA/source SHA/device-fingerprint identity inside every raw capture;
- capture timestamps inside the V8 network observation and strictly `offline < local < online`;
- the V8 summary transcript to bind the exact SHA-256 of all three raw files;
- rejection of missing/extra captures, wrong command, cross-package substitution, failed ADB command, timestamp reorder/out-of-window evidence, duplicate raw files and summary-SHA substitution;
- `FINAL_OR_PLAY_READY=false` remains mandatory.

Implementation commits on the PR branch:
- `6f743501a2ad963c0c39f793d6ebf44bff4ae487` — V9 validator.
- `5ddaf35b6cbc34e33d909f66a02f1cfe400eb1f6` — V9 regressions.
- `419d18e0ecd59faa9108aeafa6b6f59ee326a876` — V9 CI gate.

## CI evidence
PR run `34831383474` on exact head `419d18e0ecd59faa9108aeafa6b6f59ee326a876`: SUCCESS.
- Python 3.12 compile V2-V9: PASS.
- Complete V2-V9 regression suite: PASS.
- authoritative pending-truth check: PASS.

Post-merge push run `34831433723` on exact merge commit `4fb2892ad2ce69ed82f36c1fd62331ce17b38d24`: SUCCESS.

## Current release truth
- `FINAL_OR_PLAY_READY=FALSE`.
- `PHYSICAL_DEVICE_PASS=FALSE`; all ten exact candidates remain pending V9-grade real-phone evidence.
- `NETWORK_RELEASE_READY=FALSE`; configured endpoint binding/third-party reachability is not THF backend health/auth proof.
- `PUSH_READY=FALSE`; real provider/KMS integration plus exact-device notification receive/tap evidence remains required.
- THF Pass stable externally reachable non-public trusted-TLS staging remains pending.
- Production signing/AAB, Play Internal rollout, OAuth/legal/billing/2FA and device-only acceptance remain owner/device/external gates and were not bypassed.

## Rollback
No candidate APK, public endpoint, production signing, token finance or dedicated native game implementation was changed. Revert merge commit `4fb2892ad2ce69ed82f36c1fd62331ce17b38d24` to remove V9 validator/tests/workflow. This checkpoint is documentary and may be reverted independently.
