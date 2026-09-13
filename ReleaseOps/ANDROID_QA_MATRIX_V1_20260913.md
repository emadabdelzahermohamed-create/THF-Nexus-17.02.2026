# Unified Android QA Matrix — reconciled 2026-09-14

Status: ACTIVE EVIDENCE MATRIX
Scope: THF Android/game candidates plus isolated WAVE_MAWJA lane.

> Historical Terra/Rift runtime-fixed APKs `388f3c09...` and `fe35328b...` are REJECTED as phone candidates because direct aapt inspection showed a portrait hardware requirement. They remain historical package evidence only and must not receive device evidence.

| App | Canonical/source checkpoint | Package | targetSdk | Runtime/package gate | Current exact candidate APK SHA-256 | Physical device | Final/Play | Primary blocker |
|---|---|---|---:|---|---|---|---|---|
| THF Core | RC6 | `com.topherofit.thf.core` | 36 | PASS — HTTPS staging endpoint + service health, run `34743356308` | `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical acceptance; stable production hostname before final AAB |
| THF Terra / Nexus World | RC34 canonical source SHA `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68` | `com.topherofit.thf.terra` | 36 | PASS — Godot 4.7.2 import/headless/export, real payload, sensor-landscape overlay, expand aspect, zeroed desktop overrides, staged HTTPS, no portrait hardware requirement; run `34782130639` SUCCESS | `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA phone touch/orientation/HUD/avatar/locomotion/camera/world/FPS-RAM-thermal |
| THF Rift / Nexus Arena | RC37 canonical source SHA `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914` | `com.topherofit.thf.rift` | 36 | PASS — Godot 4.7.2 import/headless/export, real payload, sensor-landscape overlay, expand aspect, zeroed desktop overrides, staged HTTPS, no portrait hardware requirement; run `34782130639` SUCCESS | `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA phone touch/orientation/HUD/avatar/locomotion/camera/combat/FPS-RAM-thermal |
| THF Spark | APPS RC3 source SHA `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0` + changed-byte real-game overlay | `com.topherofit.thf.spark` | 36 | PASS — real frame/game loop, touch hit-testing, score/streak/level learning progression, package/API36/DEX checks | `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical gameplay/touch/layout/lifecycle/offline-network/performance |
| THF Rush | APPS RC3 source SHA `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b` + changed-byte real-game overlay | `com.topherofit.thf.rush` | 36 | PASS — Choreographer game loop + SensorManager motion/repetition behavior + package/API36/DEX checks | `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA phone sensor-driven repetitions + lifecycle/gameplay/performance |
| THF Learn Games | authoritative outer source SHA `ce8547851c9573db02603ea6f11e020a1b7d346af0cac51e07947304f1a7c1f9` + real-game overlay | `com.thf.topherofit.learngames` | 36 | PASS — real-function contract, Choreographer/runtime learning-mastery markers, lint/package/API36, optional camera hardware; run `34781606154` SUCCESS | `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical user journey/touch/layout/lifecycle/offline-network/performance |
| THF Fitness Games | authoritative outer source SHA `cf5d73c3a03ab503dbd7c36a2d4db3ec1449ec8281304627b9463e2cb8732a25` + real-game overlay | `com.thf.topherofit.fitnessgames` | 36 | PASS — Choreographer + SensorManager/motion-reps runtime markers, lint/package/API36, optional camera hardware; run `34781606154` SUCCESS | `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical sensor/motion gameplay + lifecycle/layout/performance |
| WAVE_MAWJA | RC14 state / exact RC13-RC14 runtime still missing | UNKNOWN-current | UNKNOWN-current | BLOCKED — do not infer from RC9 | N/A-current | PENDING | NOT_FINAL / NOT_UPLOADED | `WAVE-LIVE-SOURCE-MISSING`; remains technically isolated from THF |

## Terra/Rift rebuilt artifact reconciliation

- Workflow: `THF Terra Rift Staging APK V1`, run `34782130639`, conclusion `SUCCESS`.
- Artifact: `THF-TERRA-RIFT-STAGING-QA-APKS-V1`, ID `10324994861`, digest `sha256:53004a3fe2690399fd208f137ed256802dcef5fc18f4a5f0a4419de54d566dae`.
- Exact downloaded APK rehash:
  - Terra: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`.
  - Rift: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`.
- Both: canonical archive unchanged, QA signing only, production signing false, device status PENDING, final status NOT_FINAL.
- aapt evidence: package identities correct, targetSdk 36, no `android.hardware.screen.portrait` declaration.
- Network overlay evidence: remaining explicit placeholder URL markers = 0; endpoint values redacted; production cutover=false.

## Evidence rules

- Verify exact SHA-256 before any install/export evidence is accepted; never overwrite canonical archives.
- Source/static/build/package PASS is necessary but never equivalent to DEVICE-PASS.
- Godot phone candidates require real exported payload, sensor-landscape (`orientation=4`), `expand` aspect, touch-safe runtime and no active desktop override. A desktop override explicitly neutralized to `0` is acceptable; a non-zero active override is a FAIL.
- Online ranked/social/economy/world mutation remains backend-authoritative. Offline/local mode may be real local gameplay but must not fabricate online state.
- Physical evidence must cover exact candidate install/launch/touch/orientation-layout/background-resume/offline-network/core journey/crash-free smoke. Games additionally require player/avatar where applicable, movement/camera/gameplay interaction, plus FPS/RAM/thermal observation. Rift requires combat evidence; Rush/Fitness require sensor-motion evidence.
- `ReleaseOps/mobile/mobile_real_function_gate.py` is fail-closed for exact-SHA mismatch and now exposes `--requires-combat` and `--requires-sensor-motion` for product-specific device contracts.
- `ReleaseOps/mobile/capture_android_device_evidence_v2.py` may collect objective adb evidence, but intentionally leaves human gameplay/touch/orientation/offline-network assertions false until actually observed.
- No production signing, Google Play publishing, Cloudflare production cutover, Solana/token action, destructive cloud mutation, or persistent cloud key is authorized by this matrix.

## Next safe sequence

1. Use only the current exact candidate SHAs above for device testing; reject historical hashes automatically.
2. Capture objective adb install/launch/lifecycle/memory/gfx/thermal/log evidence, then complete human-observed touch/orientation/core-gameplay fields without fabricating PASS.
3. Run `mobile_real_function_gate.py` against the exact APK and completed device JSON; use `--requires-combat` for Rift and `--requires-sensor-motion` for Rush/Fitness Games.
4. Continue source/gameplay improvements only when candidate bytes or authoritative sources actually change; do not rerun proven gates for unchanged SHAs.
