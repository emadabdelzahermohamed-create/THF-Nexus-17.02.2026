# Unified Android QA Matrix — reconciled 2026-09-15

Status: ACTIVE EVIDENCE MATRIX  
Scope: authoritative THF game candidates plus isolated WAVE_MAWJA lane.  
Global release truth: **FINAL/PLAY_READY = FALSE** until exact-candidate physical-device evidence passes.

## Rejected / superseded evidence

- Historical Terra/Rift runtime-fixed APKs with portrait hardware requirements remain REJECTED as phone candidates.
- Raw Spark/Rush RC4 shell APKs remain REJECTED because they do not contain the required packaged game loop.
- Rift RC37 APK `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb` is SUPERSEDED. Current Rift authority is RC41 `4.7.5-rc41`, source SHA `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`.
- Rush APK `528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7` is **REJECTED — iconless candidate** and must never receive new device evidence.

| Game | Authoritative source/version | Package | targetSdk | Exact eligible candidate | Physical device | Release state | Next blocker |
|---|---|---|---:|---|---|---|---|
| THF World / Terra | RC34 Phone V4; SHA `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68` | canonical `com.topherofit.thf.terra`; QA `com.topherofit.thf.terra.phoneqa` | 36 | `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec` | PENDING | NOT_FINAL | Exact-SHA phone install/launch/touch/orientation/HUD/avatar/locomotion/camera/world-NPC/offline-online/crash/FPS-RAM-thermal |
| THF Arena / Rift | RC41 `4.7.5-rc41`; SHA `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d` | `com.topherofit.thf.rift` | 36 required | **NONE — RC37 APK superseded** | PENDING | NOT_FINAL | Stage exact RC41 archive bytes, then Godot 4.7.2 clean import/headless/export + API36 arm64 package/signature/installability, then physical combat evidence |
| THF Learn Games / Spark | APPS RC4 + real-game overlay; SHA `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43` | `com.topherofit.thf.spark` | 36 | `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea` | PENDING | NOT_FINAL | Exact-SHA physical gameplay/touch/layout/lifecycle/offline-network/performance |
| THF Motion Games / Rush | APPS RC4 + Native Verified-Motion V2 + product identity fix; SHA `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c` | `com.topherofit.thf.rush` | 36 | `f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f` | PENDING | NOT_FINAL | Exact-SHA physical sensor/motion gameplay, install/launch/lifecycle/offline-network/crash/FPS-RAM-thermal |

## Rush Native Verified-Motion V2 exact package evidence

- Exact source SHA: `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`.
- Exact icon-correct QA APK SHA: `f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f`.
- Workflow run: `34904322777`; artifact ID: `10371807756`; artifact digest: `sha256:c158383f5b2183be0d677c65748376d44fc2f75a989f136ddfd62a126ab4f0d2`.
- Package: `com.topherofit.thf.rush`; user-facing name: `THF Motion Games`; targetSdk 36.
- QA signature PASS; zipalign PASS; APK ZIP integrity PASS; packaged-game-payload PASS.
- `aapt` application label is `THF Motion Games`; launcher icon is non-empty (`res/Zg.xml`), and the packaged resource table contains `com.topherofit.thf.rush:drawable/thf_motion_games_icon`.
- Native repetition input is Android `SensorManager` / `SensorEvent` only. Registered sensor identity, finite three-axis values and positive monotonic hardware timestamps are required.
- Manual activity values and touch cannot increment repetitions. Local repetitions cannot authorize rewards. Reward-bearing health/economy/ranked evidence remains `BACKEND_REQUIRED`.
- This is an eligible **physical-device QA candidate only**, not FINAL/PLAY_READY.

## Terra phone contract

- Godot 4.7.2 import/headless/export and exported payload gates are already PASS for the unchanged Terra candidate SHA.
- Sensor-landscape, expandable aspect, touch-safe local explore and no active desktop window override are required and already bound to the current candidate.
- Online world/social/economy mutation remains backend-authoritative; offline explore must remain genuinely local.

## Rift RC41 authority

- Version: `4.7.5-rc41`.
- Exact source SHA: `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`.
- No RC37 or older build may substitute for RC41.
- Fresh Godot 4.7.2/API36 arm64 packaging remains blocked only until exact RC41 archive bytes are staged to the builder.

## Evidence rules

- Verify exact SHA-256 before install/export/device evidence is accepted; never overwrite canonical archives.
- Source/static/build/package PASS is necessary but never equivalent to DEVICE-PASS.
- WebView/fallback wrappers without packaged game/domain runtime are FAIL.
- Godot phone candidates require exported payload, sensor-landscape, `expand` aspect, touch-safe runtime and no active non-zero desktop override.
- Online ranked/social/economy/world mutation stays backend-authoritative; local modes must not fabricate online state.
- Motion/repetition values intended for rewards must not trust manual fields, touch/pointer events or client-authored totals.
- Physical evidence must include exact installed APK bytes, cold launch, touch, orientation/safe-area, background/resume, offline-network truth, core gameplay, crash-free logcat and FPS/RAM/thermal observation. Product-specific evidence remains required: Terra avatar/movement/camera/world interaction; Rift combat state change; Spark learning progression; Rush verified sensor-motion and increasing repetitions.
- No production signing, Google Play publish, Cloudflare production cutover, Solana/token action, destructive cloud mutation or persistent cloud key is authorized by this matrix.

## Next safe sequence

1. Keep all rejected/superseded hashes ineligible for device evidence.
2. Rift: stage exact RC41 bytes only; then run Godot 4.7.2/API36 arm64 packaging and combat acceptance.
3. Rush: proceed only with exact APK SHA `f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f` for physical-device acceptance; never reuse the iconless predecessor.
4. Terra/Spark: do not rebuild unchanged, already-proven bytes; next meaningful gate is physical-device acceptance unless source/candidate SHA changes.
5. Never mark FINAL/PLAY_READY until the complete exact-candidate physical-device contract passes.
