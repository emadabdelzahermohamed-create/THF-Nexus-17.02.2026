# THF Apps Factory Checkpoint — 2026-09-14 12:05 EET

## Scope and same-SHA skip
This batch covers THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass, shared identity/federation, cross-app handoffs and release controls. Dedicated native game streams and token finance were excluded from implementation changes.

The authoritative exact-device registry remains `ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json`. The ten exact APK/source SHA bindings are unchanged from the 11:12 checkpoint, so already-proven same-SHA package/API-36 work was not rebuilt merely to create activity. All ten candidates remain `PENDING_PHYSICAL_PHONE`.

## New finding — V6 lifecycle transcript admitted ambiguous substring identity evidence
V6 correctly added one immutable lifecycle transcript across touch/orientation/background-resume, but its required-marker checks used substring presence for identity/truth markers. A transcript line such as `THF_PACKAGE=<expected>.attacker` could contain the expected marker as a substring even though it was not an exact identity record. V6 also did not carry the declared device fingerprint or the observation start/end timestamps as exact transcript records.

This is insufficient for exact-candidate physical-phone acceptance because transcript substitution/duplication must fail closed rather than rely on permissive string containment.

## V7 hardening implemented
Added `ReleaseOps/mobile/validate_app_device_evidence_v7.py` and regressions. V7 layers V6 and additionally requires:
- each required lifecycle identity/truth key exactly once;
- exact key/value equality, not substring presence;
- `THF_DEVICE_FINGERPRINT_SHA256` bound to the declared physical-device fingerprint;
- `THF_OBS_STARTED_AT_UTC` and `THF_OBS_ENDED_AT_UTC` bound to the declared lifecycle observation interval;
- duplicate required keys rejected, including conflicting truth markers;
- exact package/candidate/source/session values retained;
- identical numeric PID before/after resume retained;
- `physical_device=true` and `emulator_detected=false` retained;
- explicit `final_or_play_ready=false` retained.

Regression coverage includes:
- valid exact device-bound chain;
- package substring spoof rejection;
- duplicate identity-key rejection;
- device-fingerprint substitution rejection;
- observation-interval substitution rejection;
- duplicate/conflicting truth-marker rejection;
- emulator claim rejection;
- inherited V2-V6 regressions remain in the V7 workflow.

Implementation commits:
- `8a89fca1c2b78acf0bd7edf0532eae5ebbd359d0` — V7 validator.
- `b9b550cd1350423f61a7c4b12ad0245023aebf66` — V7 regressions.
- `34ca9c6758e397a4436c5bea27d8d27a075645f7` — V7 CI gate.

## CI status at checkpoint creation
`THF App Physical Device Evidence Tooling V7` run `34825724480` was created for exact commit `34ca9c6758e397a4436c5bea27d8d27a075645f7`. At checkpoint creation it remained GitHub-hosted-runner `queued`; therefore this checkpoint does **not** claim the new V7 suite PASS yet. The queued runner is treated as a transient CI condition, not a reason to waive or fabricate evidence.

## Current release truth
- `FINAL_OR_PLAY_READY=FALSE`.
- `PHYSICAL_DEVICE_PASS=FALSE`; all ten exact candidates remain pending real phone evidence.
- `NETWORK_RELEASE_READY=FALSE`; stable externally reachable trusted-TLS THF backend/Pass health-auth-session-federation evidence remains required.
- `PUSH_READY=FALSE`; real provider/KMS integration and exact-device notification receive/tap evidence remain required.
- Production signing/AAB, Play Internal rollout, OAuth/legal/billing/2FA and device-only acceptance remain external/user/device gates and were not bypassed.

## Rollback
This batch changes release-control validator/tests/workflow only and does not deploy a backend, change public endpoints, sign/publish packages, touch token finance or modify dedicated native game implementation. Roll back in reverse order: workflow commit `34ca9c6758e397a4436c5bea27d8d27a075645f7`, test commit `b9b550cd1350423f61a7c4b12ad0245023aebf66`, validator commit `8a89fca1c2b78acf0bd7edf0532eae5ebbd359d0`.
