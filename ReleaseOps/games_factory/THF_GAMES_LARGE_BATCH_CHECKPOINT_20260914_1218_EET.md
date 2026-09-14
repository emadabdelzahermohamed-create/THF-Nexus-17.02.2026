# THF Games Large-Batch Checkpoint — 2026-09-14 12:18 EET

## Scope
THF Terra / Nexus World, THF Rift / Nexus Arena, THF Spark, THF Rush, Learn Games, Fitness Games, and shared physical-device/release-truth systems.

## Authoritative-state inspection
- Current game candidate registry was inspected before engineering work.
- All six exact APK SHAs and source versions remain unchanged.
- Registry remains `final_or_play_ready=false` and `physical_device_status=PENDING`.
- Previously proven Godot/parser/import/API36/package/game-payload gates for these unchanged SHAs were not rebuilt or re-labeled.
- Latest pre-batch V10 evidence tooling was inspected; it bound touch/orientation/safe-area/background-resume to a hash-bound ADB transcript but did not semantically bind the required offline -> local gameplay -> online-restored transition.

## New engineering batch: physical-device evidence V11
V11 extends V10 and fail-closes the offline/network acceptance gap.

New requirements:
- exact candidate package and same physical-device `session_id`;
- approved `adb-shell-connectivity-transition-v1` method;
- observation interval entirely inside the declared phone session;
- immutable non-empty safe-path transcript bound by SHA-256;
- `offline_reached=true`;
- `local_mode_stayed_local=true`;
- `no_online_state_faked=true`;
- `online_restored=true`;
- same numeric process PID before and after the transition;
- exactly one ordered stage sequence: OFFLINE_CONFIRMED -> LOCAL_GAMEPLAY_OBSERVED -> ONLINE_RESTORED;
- duplicate, missing, reordered, tampered, wrong-package, cross-session, wrong-method, changed-PID or fake-online-state evidence fails closed;
- validator remains non-promotional and always prints `FINAL_OR_PLAY_READY=FALSE` on successful validation.

Files:
- `ReleaseOps/mobile/validate_game_device_evidence_v11.py`
- `ReleaseOps/mobile/test_validate_game_device_evidence_v11.py`
- `.github/workflows/thf-game-physical-device-evidence-tooling-v11.yml`
- `ReleaseOps/games_factory/PHYSICAL_DEVICE_ACCEPTANCE_V11_20260914.md`

Commits:
- `12b4ff34cafe5400bb778215b9e3d3d29db8947d` — V11 validator
- `3553cac05a526e47f7b61379ca7dc016ba4eb3c8` — V11 regressions
- `eecc1d4721b86186cd06a038d4da12a93239a90d` — V11 CI
- `830d248dca066b4b0972895ff6c417418f011583` — V11 physical-device acceptance protocol

## CI evidence
Workflow: `THF Game Physical Device Evidence Tooling V11`
Run: `34826957412` — SUCCESS.

PASS steps:
- compile V7-V11 validators/tests;
- preserve V10 regression chain;
- V11 offline/network transition regressions;
- non-promotional FINAL gate assertion.

V11 regression coverage includes all six products plus negative cases for missing record, wrong package, cross-session evidence, false local-truth claim, SHA tamper, PID change, stage reorder, duplicate online-state truth marker, and unapproved method.

## Exact candidates remain unchanged
- Terra RC34 / source `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68` / APK `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift RC37 / source `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914` / APK `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark APPS_RC4+REAL_GAME_OVERLAY_V1 / source `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43` / APK `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush APPS_RC4+REAL_GAME_OVERLAY_V1 / source `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c` / APK `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games REAL_GAME_OVERLAY_V1 / source `ce8547851c9573db02603ea6f11e020a1b7d346af0cac51e07947304f1a7c1f9` / APK `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games REAL_GAME_OVERLAY_V1 / source `cf5d73c3a03ab503dbd7c36a2d4db3ec1449ec8281304627b9463e2cb8732a25` / APK `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

## Physical-device gate
Remote physical-device execution was unavailable during this batch. No synthetic device PASS was recorded.

All six remain `NOT_FINAL / PHYSICAL_DEVICE_PENDING`. Exact installed APK bytes still require one real-phone evidence-bound session covering install/cold launch, touch, orientation/safe area, same-PID background/resume, V11 offline/local/online transition, crash-free core gameplay, FPS/RAM/thermal and product-specific gameplay: Terra world/avatar/locomotion/camera interaction; Rift combat; Spark/Learn progression; Rush/Fitness real sensor-driven repetitions.

## Safety / unchanged external systems
- no production signing
- no Play publishing
- no Cloudflare production cutover
- no Solana/token mutation
- no canonical archive overwrite
- no wrapper/fallback candidate promoted
- WAVE_MAWJA untouched and isolated
