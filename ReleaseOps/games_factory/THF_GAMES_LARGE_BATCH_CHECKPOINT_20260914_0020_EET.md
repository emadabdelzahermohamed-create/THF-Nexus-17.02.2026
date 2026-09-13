# THF Games Large-Batch Checkpoint — 2026-09-14 00:20 EET

## Scope and safety

This checkpoint covers THF Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games, and shared mobile/avatar/animation evidence. WAVE_MAWJA remained technically isolated and no WAVE file was used as THF input.

Canonical game source archives remained immutable. GCP access used GitHub OIDC/WIF + IAP; no persistent cloud key was introduced. No production signing, Google Play publishing, Cloudflare production cutover, Solana/token transaction, destructive cloud mutation, or canonical-archive overwrite/delete occurred.

Nothing in this checkpoint is FINAL or PLAY_READY. Exact-candidate physical-phone evidence remains mandatory.

## 1. Terra/Rift staging run reconciled to SUCCESS

The previously pending repaired workflow is now authoritative:

- workflow: `THF Terra Rift Staging APK V1`
- run: `34782130639`
- conclusion: `SUCCESS`
- artifact: `THF-TERRA-RIFT-STAGING-QA-APKS-V1`
- artifact ID: `10324994861`
- artifact digest: `sha256:53004a3fe2690399fd208f137ed256802dcef5fc18f4a5f0a4419de54d566dae`

Direct rehash of the rebuilt artifact established the current phone candidates:

### Terra / Nexus World
- canonical source SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`
- current APK SHA-256: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- package: `com.topherofit.thf.terra`
- targetSdk: `36`
- Godot exported payload: PASS
- sensor-landscape candidate overlay: PASS (`orientation=4`)
- expandable aspect: PASS (`expand`)
- desktop width/height overrides: neutralized to `0`
- APK portrait hardware requirement: ABSENT
- explicit placeholder URL markers after network overlay: `0`
- canonical archive unchanged: true
- QA signing only: true
- device status: PENDING
- final status: NOT_FINAL

### Rift / Nexus Arena
- canonical source SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
- current APK SHA-256: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- package: `com.topherofit.thf.rift`
- targetSdk: `36`
- Godot exported payload: PASS
- sensor-landscape candidate overlay: PASS (`orientation=4`)
- expandable aspect: PASS (`expand`)
- desktop width/height overrides: neutralized to `0`
- APK portrait hardware requirement: ABSENT
- explicit placeholder URL markers after network overlay: `0`
- canonical archive unchanged: true
- QA signing only: true
- device status: PENDING
- final status: NOT_FINAL

Historical runtime-fixed APKs `388f3c09...b18c7` (Terra) and `fe35328b...024b1` (Rift) remain REJECTED as physical-phone candidates because their aapt badging retained an Android portrait hardware requirement. Device evidence for those hashes is invalid for current promotion.

## 2. Current exact candidate matrix reconciled

`ReleaseOps/ANDROID_QA_MATRIX_V1_20260913.md` was updated to bind device testing to the current exact candidates:

- Terra: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games: `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games: `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

Spark/Rush/Learn/Fitness builds were not repeated because the exact candidate bytes and already-proven build/package evidence did not change.

## 3. Mobile real-function gate corrected and strengthened

Commit `bb8524ef9293ef1a202a69a0a7a6669cb14c4f99` corrected the generic Godot source gate:

- sensor-landscape is parsed as an exact setting and must equal `4`;
- stretch aspect must exactly equal `"expand"`;
- desktop override keys are allowed only when absent or numerically neutralized to zero;
- active non-zero desktop overrides remain a FAIL;
- `--requires-combat` adds a mandatory `combat_pass=true` device gate for Rift/Arena;
- `--requires-sensor-motion` adds mandatory `sensor_motion_pass=true` for Rush/Fitness Games.

Commit `55db3e2a1489928dbfd12032f24da53f5a9c7bbe` added regression coverage for these contracts.

## 4. Exact-SHA Android physical evidence collector added

Commit `a6b570ab01c0953a61007c54f858365682d45d13` added `ReleaseOps/mobile/capture_android_device_evidence_v2.py`.

It is deliberately fail-closed and objective-only:

- recomputes and locks the exact APK SHA before adb work;
- requires exactly one authorized physical adb device;
- captures install, cold launch/process presence, lifecycle smoke, meminfo, gfx framestats, thermal service, display/window/package snapshots and logcat fatal markers;
- redacts most of the adb serial;
- NEVER auto-promotes touch, orientation/layout, offline/network transition, core user journey, avatar/player, movement/camera, gameplay, combat, or sensor-motion observations;
- those fields stay false until actually observed on hardware.

Commit `62cb3afb29f787a651827684b8569e588f91a862` added collector regressions. Commit `37e62ab70901820d9bfb6a48a3c2543028878f30` integrated the collector and mobile gate into CI.

Authoritative test run:

- workflow: `THF Mobile Real-Function Gate Tests`
- run: `34783226457`
- conclusion: `SUCCESS`
- compile gate: PASS
- fail-closed unit tests: **11/11 PASS**

Tests cover exact-SHA mismatch, engine-only Godot APK rejection, payload acceptance, sensor-landscape/expand/touch, zero override acceptance, active override rejection, placeholder rejection, exact one-device requirement, no manual auto-promotion, and combat/sensor-specific device requirements.

## 5. Physical-device protocol upgraded

`ReleaseOps/DEVICE_ACCEPTANCE_PROTOCOL_V1_20260913.md` was revised to the current exact candidates and now explicitly requires:

- exact-SHA install and cold launch;
- real touch-safe mobile HUD/layout;
- Terra/Rift sensor-landscape and expandable behavior;
- background/resume and re-launch after process kill;
- honest offline/network transition;
- core user journey without crash;
- real FPS/frame, RAM and thermal observation during interaction;
- no secret/token exposure in UI/logs.

Product-specific additions:

- Terra: player/avatar, locomotion, camera, world/NPC interaction;
- Rift: real combat and `combat_pass=true`;
- Spark/Learn: real learning-game loop and progression from actual input;
- Rush/Fitness: actual hardware sensor/motion exercise and `sensor_motion_pass=true`.

## 6. Canonical Terra/Rift asset and provenance audit

A new read-only archive auditor was added in commit `e00bf3374c6ca70b1a7e5bfacacee2c3c133aa41`, with WIF/IAP workflow commit `b1f7f70c45d6b5b9bbb0f4e19b13eeafdb1d071e`.

Authoritative run:

- workflow: `THF Game Asset Provenance Audit V1`
- run: `34783340000`
- conclusion: `SUCCESS`
- artifact: `THF-GAME-ASSET-PROVENANCE-V1`
- artifact ID: `10326035955`
- artifact digest: `sha256:6d0235f6d9c554144a726e123675512e346eb417cbf9b4a2f0a373fc3e3cc610`

The audit operated directly on the canonical ZIPs without extraction or mutation and verified the exact expected SHAs.

### Terra archive results
- exact canonical SHA: PASS
- file count: `784`
- asset files: `155`
- model files: `79`
- animation-capable files: `80`
- avatar/character marker paths: `245`
- animation/motion marker paths: `130`
- provenance-document paths: `14`
- MakeHuman/MPFB named signal: present
- UAL named signal: present
- unsafe ZIP members: `0`
- symlink-like ZIP members: `0`
- casefold collisions: `0`
- oversized assets >512 MiB: `0`
- canonical archive mutated: false

### Rift archive results
- exact canonical SHA: PASS
- file count: `771`
- asset files: `147`
- model files: `74`
- animation-capable files: `75`
- avatar/character marker paths: `247`
- animation/motion marker paths: `106`
- provenance-document paths: `13`
- MakeHuman/MPFB named signal: present
- UAL named signal: present
- unsafe ZIP members: `0`
- symlink-like ZIP members: `0`
- casefold collisions: `0`
- oversized assets >512 MiB: `0`
- canonical archive mutated: false

This proves source-archive safety and the presence of avatar/animation/provenance integration signals. It does not replace visual-quality, rig correctness, animation-retarget, IK/root-motion or performance validation on real GPU/device hardware.

## 7. WAVE and TokenOps isolation

- WAVE_MAWJA remained untouched by these game workflows (`wave_files_read_or_changed=false`).
- WAVE still has its independent `WAVE-LIVE-SOURCE-MISSING` blocker for exact RC13/RC14 runtime/source recovery.
- Open PR #2 remains isolated TokenOps read-only work; no token transaction/signing/transfer/burn/authority action was performed.

## Remaining blockers / next highest-value work

1. Physical phone/device-lab acceptance for all six exact candidate APK SHAs above.
2. Terra: verify on hardware avatar render, locomotion, camera, touch HUD, world/NPC interactions, landscape safe area, lifecycle, offline/network transition and FPS/RAM/thermal.
3. Rift: same plus real combat interaction and `combat_pass=true`.
4. Rush/Fitness Games: prove sensor-driven behavior using real phone sensors and `sensor_motion_pass=true`.
5. Spark/Learn Games: prove real learning gameplay/progression, not static navigation/UI, on exact APK bytes.
6. Shared avatar/animation: physical GPU/device proof for MPFB/MakeHuman rendering, UAL retarget quality, IK/root-motion, animation blending, clipping and thermal/performance.
7. Do not rebuild unchanged exact candidates merely to repeat already-proven gates; resume source changes only when new defects/evidence justify changed bytes.
