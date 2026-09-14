# THF Apps Factory — Large-Batch Checkpoint — 2026-09-14 07:15 EET

## Scope
THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass, shared identity/federation and cross-app handoffs. Dedicated native game streams and token finance were excluded from this engineering pass.

## Baseline and same-SHA policy
- Main baseline observed at run start: `232a38bd0058e8088984be1d36e6052ab709e418`.
- Latest prior Apps Factory reconciliation: `5ceef8f9c111d11bd8b8e941fcd3fe217e073711`.
- Core, Pulse, Forge, Echo, Codex, Vault, Signal and Command exact candidate/package/API36/runtime gates were not rebuilt or relabeled because their authoritative SHAs were unchanged and already held PASS evidence.
- No same-SHA PASS was re-created merely to produce activity.

## Defect found and fixed: split release authority
`THF_APPS_FACTORY_STATE_20260913_2035_EET.json` still referenced the pre-reconciliation Spark/Rush app candidates while `THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json` already referenced the reconciled real-function candidates. That allowed two ReleaseOps surfaces to disagree about the exact APK/source SHA for the same package IDs.

The state is now reconciled to the exact physical-device authority:
- Spark: package `com.topherofit.thf.spark`, source SHA-256 `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`, APK SHA-256 `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`.
- Rush: package `com.topherofit.thf.rush`, source SHA-256 `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`, APK SHA-256 `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`.
- The superseded runtime-bound candidate SHA is retained as history; it is not treated as current authority.
- Spark/Rush source-history truth remains `NO_TESTS`; the exact-source external regression packs remain separately recorded as PASS and are not misrepresented as native source tests.

## Fail-closed protection added
`validate_apps_factory_state.py` now accepts the physical-device evidence registry and fails if any of the following drift occurs:
- candidate set mismatch;
- package mismatch;
- APK SHA mismatch;
- non-Core source SHA mismatch;
- registry `all_pending` becomes false without evidence;
- any candidate is promoted from `PENDING_PHYSICAL_PHONE` by metadata alone.

Regression tests cover authoritative alignment plus negative APK drift, source drift and false device promotion. The Apps Factory workflow now always validates the state against the physical-device registry before running the regression suite.

## Evidence
Commits in this batch:
1. `27a21b513d231c533278980b62ee282ae065f7be` — reconcile Apps Factory state to Spark/Rush exact authority.
2. `ca765d3c341e165f5d90d225e03586a3e7d41141` — bind state validation to physical candidate registry.
3. `ca4166f22d67b52674d7b5d81ef888e3685e15dd` — regression-protect authority alignment.
4. `6f91b4895a58cbc586696c6048fec476b07529fb` — enforce cross-registry validation in CI.

GitHub Actions `THF Apps Factory State Gate` run `34804792550` on exact head `6f91b4895a58cbc586696c6048fec476b07529fb` completed `SUCCESS` on the first attempt.

## Release truth after this batch
- `FINAL_OR_PLAY_READY = FALSE`.
- All ten exact APK candidates remain `PENDING_PHYSICAL_PHONE`.
- `PUSH_READY = FALSE`; provider delivery and device receive/tap evidence remain unproven.
- Shared staging health/binding remains proven for its existing same SHA, but THF Pass full lifecycle/federation is still only proven in isolated rehearsal; stable externally reachable non-public trusted-TLS staging remains pending.
- No production signing, public rollout, Play publication, OAuth/legal acceptance, token-finance operation or native-game-stream modification was performed.

## Remaining external/user-only gates
1. Physical-phone evidence bound to each exact APK SHA: install, launch, touch/route behavior, responsive layout/orientation, background-resume, real offline/network transitions, Data Saver, accessibility, RTL/20-language behavior, core journey and crash-free smoke; notification permission/channel/receive/tap/deeplink where applicable.
2. Stable externally reachable non-public THF Pass staging over trusted TLS before promoting auth/session/federation from isolated rehearsal to staging-live.
3. Approved FCM/APNs provider credentials behind a KMS/secret boundary before production push delivery testing.
4. Production signing/Play/legal/OAuth/2FA remain owner-controlled gates and cannot be inferred from CI.

## Rollback
This batch changed ReleaseOps truth/validation/CI only. It did not cut over a runtime or production endpoint. Rollback is a Git revert of the four implementation commits above plus this checkpoint; no production data migration or service rollback is required.
