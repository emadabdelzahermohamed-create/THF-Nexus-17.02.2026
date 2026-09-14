# THF Apps Factory Large-Batch Checkpoint — 2026-09-14 15:05 EET

## Scope and run-start authority
- Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity and cross-app handoffs.
- Dedicated native game streams and token finance were not modified.
- Authoritative Apps Factory state remains `THF_APPS_FACTORY_STATE_20260914_1115_EET.json` for the same candidate SHAs; same-SHA rebuild/package work was skipped.
- Core production authority remains package `com.topherofit.thf.core`, targetSdk 36, APK SHA-256 `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`.
- Existing production candidates remain physical-phone pending; no FINAL/PLAY_READY promotion is made.

## New condition discovered
A separate Core Phone UI1 local QA APK now exists for physical-phone design compatibility work:
- package: `com.topherofit.thf.core.debug`
- targetSdk: 36
- APK SHA-256: `465faa1a04a276c648ef851f758b79640eddff0c2b3bf382a7cf8021cc6aca71`
- debug signed; production signing false; Play upload false; backend-dependent features not accepted.

This artifact is useful QA evidence but is not the authoritative Core production candidate and is not eligible to satisfy exact-candidate physical release evidence.

## Engineering completed
1. Commit `b74606afe9c98f08bf480a81f17aa218af6c3fee` created `THF_AUXILIARY_MOBILE_ARTIFACT_REGISTRY_V1.json`, explicitly separating QA/debug artifacts from release authority.
2. Commit `6608cabedd7e603cc0d2c32fc47aa9f2d1284f21` added `validate_auxiliary_mobile_artifact_authority_v1.py`.
   - Fail-closed checks bind QA package/APK/source/version/targetSdk/evidence/checkpoint to the registered artifact.
   - The guard rejects production package/SHA aliasing, production state/physical-registry drift, QA insertion into the physical release authority registry, missing files, evidence mismatch, production signing/Play/final promotion, and path escape.
3. Commit `02d656ccdd27e5bc8671e3a8e4221eee975959d2` added regression coverage for release-authority promotion, physical-evidence promotion, FINAL promotion, package/APK aliasing, lineage drift, state/physical drift, QA-registry contamination, missing artifacts and evidence identity mismatch.
4. Commit `ff993a016918ddcbccfa31886ca970a42f80935c` added `THF Apps Auxiliary Artifact Authority Gate V1`.
5. Commit `47c9d8e3fa602e3bcffd20d20c5253f4c8df4739` hardened that workflow so it resolves the latest `THF_APPS_FACTORY_STATE_*.json` dynamically rather than hard-coding a dated state file, and widened path triggers to future Core QA artifacts/state validator changes.

## CI evidence
- Workflow run `34841145439` on `ff993a016918ddcbccfa31886ca970a42f80935c`: SUCCESS.
- Workflow run `34841213411` on `47c9d8e3fa602e3bcffd20d20c5253f4c8df4739`: SUCCESS.
- The second run passed:
  - latest authoritative Apps Factory state resolution;
  - Python 3.12 compile of both release-authority guards;
  - auxiliary/mobile release-authority isolation validation;
  - regression tests;
  - revalidation of latest production state against the physical-device authority registry.

## Release truth after this batch
- `FINAL_OR_PLAY_READY=FALSE`
- `PHYSICAL_DEVICE_PASS=FALSE`
- `NETWORK_RELEASE_READY=FALSE`
- `PUSH_READY=FALSE`
- Core Phone UI1 local QA artifact is explicitly non-authoritative and cannot substitute for the production Core APK SHA.
- No production signing, Play upload, public rollout, backend cutover, token-finance mutation, or dedicated native-game implementation occurred.

## Remaining external/user-only gates
- Stable externally reachable trusted-TLS THF Pass/backend staging with real health/auth/session/federation evidence.
- Real FCM/APNs provider credentials within a KMS/secret-management boundary.
- Physical Android evidence for every exact production APK SHA: installed-byte identity, install/launch/touch/layout/orientation/background-resume/offline-network/core journey/crash-free/accessibility/Data Saver/RTL/20-language readiness; notification permission/channel/receive/tap/deeplink where applicable.
- Production signing, Play Console/legal acceptance and final rollout remain separate gated actions.

## Rollback
The batch is metadata/validator/CI only and is reversible by reverting commits `47c9d8e3`, `ff993a01`, `02d656cc`, `6608cabe`, and `b74606af` in reverse order. No production service or release payload was cut over.
