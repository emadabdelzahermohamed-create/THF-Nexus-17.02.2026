# Unified Android QA Matrix — reconciled 2026-09-14

Status: ACTIVE EVIDENCE MATRIX
Scope: THF Android/game candidates plus isolated WAVE_MAWJA lane.

> Historical Terra/Rift runtime-fixed APKs `388f3c09...` and `fe35328b...` are REJECTED as phone candidates because direct aapt inspection showed a portrait hardware requirement. They remain historical package evidence only and must not receive device evidence.

> Raw Spark/Rush RC4 exact-QA APKs `9dba464d...567fd` and `92663a7e...e29a` are REJECTED as game candidates. Exact APK inspection shows WebView/offline-shell payloads without the required packaged game loop. The authoritative RC4 sources are retained, but phone candidates use reversible real-game overlays.

> Rift RC37 APK `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb` is SUPERSEDED and is no longer eligible for new device evidence. Rift authority moved to RC41 source SHA `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`; an RC41 Android candidate must be built from those exact bytes before device acceptance resumes.

> Rush APKs `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a` and `92663a7e2963b2b4d233808013bdb6c4bed279fc9cedb423b1bf74f1e1aae29a` are SUPERSEDED. The eligible Rush QA candidate is now Native Verified-Motion V2 SHA `528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7`, built from exact RC4 source SHA `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c` in run `34893899367`.

| App | Canonical/source checkpoint | Package | targetSdk | Runtime/package gate | Current exact candidate APK SHA-256 | Physical device | Final/Play | Primary blocker |
|---|---|---|---:|---|---|---|---|---|
| THF Core | RC6 | `com.topherofit.thf.core` | 36 | PASS — HTTPS staging endpoint + service health, run `34743356308` | `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical acceptance; stable production hostname before final AAB |
| THF World / Terra | RC34 canonical source SHA `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68` + Phone V4 local-explore overlay | canonical `com.topherofit.thf.terra`; QA `com.topherofit.thf.terra.phoneqa` | 36 | PASS — Godot 4.7.2 import/headless/export, exported payload, sensor-landscape, expand aspect, touch-safe local explore, no active desktop override, exact package/signature/installability gate | `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec` (QA-only V4) | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical install/touch/orientation/HUD/avatar/locomotion/camera/world-NPC/offline-online/FPS-RAM-thermal |
| THF Arena / Rift | RC41 `4.7.5-rc41` canonical source SHA `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d` | `com.topherofit.thf.rift` | 36 required | SOURCE PASS — RC41 is authoritative and includes cumulative server-authoritative pickup reachability; old RC37 AAB lane is retired by a superseded guard; Godot 4.7.2 fresh preflight is blocked until exact RC41 archive bytes are staged on builder | NONE — RC37 APK superseded | PENDING | NOT_FINAL / NOT_UPLOADED | stage exact RC41 archive bytes, then Godot 4.7.2 import/headless/export + API36 arm64 package/signature/installability; afterwards physical combat acceptance |
| THF Learn Games / Spark | APPS RC4 canonical source SHA `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43` + reversible real-game overlay | `com.topherofit.thf.spark` | 36 | PASS — RC4 exact source verified; packaged frame/game loop, touch hit-testing and score/streak/level learning progression; raw wrapper APK rejected | `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical gameplay/touch/layout/lifecycle/offline-network/performance |
| THF Motion Games / Rush | APPS RC4 canonical source SHA `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c` + Native Verified-Motion V2 | `com.topherofit.thf.rush` | 36 | PASS — run `34893899367`; exact RC4 clean extract; native SensorManager gameplay requires registered sensor identity, finite 3-axis values and monotonic hardware timestamp; touch/manual values cannot increment reps; QA signature/zipalign/package/API36/packaged-game-payload PASS; local reps never authorize rewards | `528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical sensor/motion gameplay, lifecycle/layout/performance; provider/server-verifiable health evidence remains required for reward-bearing paths |
| THF Learn Games legacy lane | authoritative outer source SHA `ce8547851c9573db02603ea6f11e020a1b7d346af0cac51e07947304f1a7c1f9` + real-game overlay | `com.thf.topherofit.learngames` | 36 | PASS — real-function contract, Choreographer/runtime learning-mastery markers, lint/package/API36, optional camera hardware; run `34781606154` SUCCESS | `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical user journey/touch/layout/lifecycle/offline-network/performance |
| THF Fitness Games legacy lane | authoritative outer source SHA `cf5d73c3a03ab503dbd7c36a2d4db3ec1449ec8281304627b9463e2cb8732a25` + real-game overlay | `com.thf.topherofit.fitnessgames` | 36 | PASS — Choreographer + SensorManager/motion-reps runtime markers, lint/package/API36, optional camera hardware; run `34781606154` SUCCESS | `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a` | PENDING | NOT_FINAL / NOT_UPLOADED | exact-SHA physical sensor/motion gameplay + lifecycle/layout/performance |
| WAVE_MAWJA | RC14 state / exact RC13-RC14 runtime still missing | UNKNOWN-current | UNKNOWN-current | BLOCKED — do not infer from RC9 | N/A-current | PENDING | NOT_FINAL / NOT_UPLOADED | `WAVE-LIVE-SOURCE-MISSING`; remains technically isolated from THF |

## Latest authority reconciliation

- Terra authority remains RC34 source SHA `eaa2ae79...bdbd68`, with Phone V4 candidate SHA `e0ac997e...0cfbec`.
- Rift authority is RC41 SHA `29edaa0e...cb95d`, not RC37. The former RC37 AAB workflow is now a fail-closed superseded guard and no longer builds RC37.
- Spark authority remains APPS RC4 SHA `58a32690...48d43` plus the real-game overlay; its raw wrapper APK remains rejected.
- Rush authority is APPS RC4 SHA `766936c2...f771c` plus Native Verified-Motion V2. Exact QA APK SHA `528f7d11...65ed7` passed run `34893899367`; artifact ID `10368186302`, digest `sha256:989137c623a8f137267dd7239d2d27b450512ddd9fabc6aa7656b3457ed22ac8`.

## Rush Native Verified-Motion V2 evidence

- Exact source SHA before extraction: `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`.
- Exact candidate APK SHA: `528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7`.
- User-facing label: `THF Motion Games`; canonical package remains `com.topherofit.thf.rush`.
- targetSdk 36; QA signature verified; zipalign verified; APK ZIP integrity PASS; packaged real-game payload PASS.
- Native repetition input is Android `SensorManager`/`SensorEvent` only. Events must originate from the registered sensor object, contain at least three finite axes, and carry a positive monotonic hardware timestamp.
- Touch can reset a local session but cannot increment repetitions. Manual activity totals are not accepted.
- Local repetitions are explicitly non-rewarding. Reward/economy/ranked paths continue to require backend-authoritative verified provider/health evidence with anti-replay/provenance controls.
- Physical-device status remains PENDING and final status remains NOT_FINAL.

## Terra package/installability reconciliation

- Phone V4 exact APK SHA: `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`.
- QA package: `com.topherofit.thf.terra.phoneqa`; canonical production package remains `com.topherofit.thf.terra`.
- targetSdk 36; arm64 present; zipalign/apksigner/package checks are fail-closed.
- QA signing only; production signing false; physical device status PENDING; final status NOT_FINAL.

## Rift RC41 source state

- Version: `4.7.5-rc41`.
- Exact source SHA: `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`.
- RC41 source/preflight workflow intentionally fails closed when these exact archive bytes are not found on the builder; no older RC may be substituted.
- Required next package path: exact RC41 bytes -> clean extract -> Godot 4.7.2 import/headless -> Android API36 arm64 export -> payload/package/signature/installability gates -> physical-device evidence.

## Evidence rules

- Verify exact SHA-256 before any install/export evidence is accepted; never overwrite canonical archives.
- Source/static/build/package PASS is necessary but never equivalent to DEVICE-PASS.
- A game APK must pass packaged-payload inspection; a WebView/offline fallback shell without packaged game-loop/domain runtime is a FAIL even when package, signature and API36 checks pass.
- Godot phone candidates require real exported payload, sensor-landscape (`orientation=4`), `expand` aspect, touch-safe runtime and no active desktop override. A desktop override explicitly neutralized to `0` is acceptable; a non-zero active override is a FAIL.
- Online ranked/social/economy/world mutation remains backend-authoritative. Offline/local mode may be real local gameplay but must not fabricate online state.
- Motion/repetition values intended for rewards must not trust manual fields, pointer/touch events or client-authored totals. Local sensor-only practice may remain local and non-rewarding; reward-bearing evidence requires a stronger provider/server-verifiable evidence path.
- Physical evidence must cover exact candidate install/launch/touch/orientation-layout/background-resume/offline-network/core journey/crash-free smoke. Games additionally require player/avatar where applicable, movement/camera/gameplay interaction, plus FPS/RAM/thermal observation. Rift requires combat evidence; Rush/Fitness require sensor-motion evidence.
- `ReleaseOps/validators/audit_game_apk_payload_v1.py` is the fail-closed packaged-payload gate for Spark/Rush-style game candidates.
- `ReleaseOps/mobile/mobile_real_function_gate.py` is fail-closed for exact-SHA mismatch and exposes `--requires-combat` and `--requires-sensor-motion` for product-specific device contracts.
- No production signing, Google Play publishing, Cloudflare production cutover, Solana/token action, destructive cloud mutation, or persistent cloud key is authorized by this matrix.

## Next safe sequence

1. Reject all superseded hashes above before any new device evidence is captured.
2. Rift: stage only exact RC41 archive bytes and continue Godot 4.7.2/API36 arm64 packaging; never fall back to RC37.
3. Rush: use only exact Native Verified-Motion V2 QA candidate SHA `528f7d11...65ed7` for physical acceptance; never reuse a pre-V2 Rush APK.
4. Terra/Spark: do not rebuild unchanged proven bytes; proceed to physical-device acceptance only when a real phone is available.
5. Never mark FINAL/PLAY_READY until exact candidates pass physical install/launch/touch/orientation/background-resume/offline-network/core gameplay/crash-free plus product-specific avatar/movement/camera/combat/learning/motion and FPS/RAM/thermal evidence.
