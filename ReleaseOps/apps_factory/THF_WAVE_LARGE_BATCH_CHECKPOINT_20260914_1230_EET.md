# THF + WAVE Large-Batch Release Checkpoint — 2026-09-14 12:30 EET

## Scope
Release/platform/QA pass across THF and isolated WAVE release controls.

## Authoritative state read first
- Repository head before this batch: `50acf73748c1520ba59f07716ee6a7b0bdcf5161`.
- Latest THF Games checkpoint: physical-device evidence V11, workflow run `34826957412` SUCCESS.
- Six game exact candidates remain unchanged and `NOT_FINAL / PHYSICAL_DEVICE_PENDING`.
- Existing THF App evidence V7 binds lifecycle evidence to exact device fingerprint and observation interval but does not semantically bind the required offline -> local app operation -> online-restored transition.

## Material repair: THF App Physical Device Evidence V8
Added:
- `ReleaseOps/mobile/validate_app_device_evidence_v8.py`
- `ReleaseOps/mobile/test_validate_app_device_evidence_v8.py`
- `.github/workflows/thf-app-physical-device-evidence-tooling-v8.yml`

Commits:
- `eb174400b8c33ba18b22da11869975140eecb305` — V8 validator.
- `03d849b9b487faef28021a5403b70caabde0ccb4` — V8 regressions.
- `394d1e7777027296e9fde49826efc64c458526d1` — V8 CI gate.

V8 fail-closes app device acceptance unless one immutable SHA-256-bound ADB connectivity transcript from the same physical-phone session proves:
- exact session/package/APK candidate/source/device fingerprint identity;
- approved `adb-shell-connectivity-transition-v1` method;
- `offline_reached=true`;
- `local_mode_stayed_local=true`;
- `no_online_state_faked=true`;
- `online_restored=true`;
- same numeric PID before/after;
- strict ordered stages `OFFLINE_CONFIRMED -> LOCAL_APP_OPERATION_OBSERVED -> ONLINE_RESTORED`;
- observation interval entirely inside the declared physical-device session;
- evidence bytes match the declared lowercase SHA-256;
- duplicate/reordered/tampered/cross-session/wrong-lineage/wrong-device evidence fails closed;
- evidence tooling cannot self-promote FINAL/PLAY_READY.

## CI result
Workflow: `THF App Physical Device Evidence Tooling V8`
Run: `34828323753`
Result: SUCCESS.
PASS:
- compile V2-V8 validators/tests;
- complete V2-V8 regression chain;
- V8 authoritative pending-truth assertion.

## Release truth
- THF app candidates remain `PENDING_PHYSICAL_PHONE`.
- No physical-device/GPU QA was fabricated.
- No signed production AAB or Play approval was claimed.
- No production HTTPS/WSS or Cloudflare cutover was claimed.
- Candidate APK/source bytes were not rebuilt or relabeled because this batch changed release-control tooling only.

## WAVE isolation
WAVE was not modified. The previously known canonical-source/OS Login blocker is not bypassed here; no SSH/OS Login weakening, older-source substitution, Cloudflare cutover, or cross-project mutation was performed.

## Non-delegable remaining blockers
- exact-candidate physical-phone execution/evidence;
- production signing key use and signed AAB;
- Play Internal submission/acceptance;
- stable trusted production HTTPS/WSS and real endpoint health/auth/session proof;
- WAVE canonical source access under an authorized identity or cryptographically bound service-account-owned release workspace.

## Evidence body SHA-256
`b2a7cf795e4c88a41da7ca4bdeeccaa1609e61bd6df2e749509ac2f0ccb6c45c`
