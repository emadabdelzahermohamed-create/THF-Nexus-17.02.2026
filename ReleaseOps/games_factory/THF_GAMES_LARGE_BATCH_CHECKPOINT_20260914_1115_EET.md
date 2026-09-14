# THF Games Large-Batch Checkpoint — 2026-09-14 11:15 EET

## Scope
THF Terra / Nexus World, THF Rift / Nexus Arena, THF Spark, THF Rush, Learn Games, Fitness Games, and shared physical-device acceptance tooling.

## Authoritative-state inspection
- Repository main was inspected before game work.
- Main had advanced due to Apps Factory runtime-truth work; no new game-candidate/source change was identified that justified rebuilding already-proven exact APK candidates.
- Previously proven Godot/parser/import/API36/package/game-payload gates for unchanged game SHAs were not repeated.

## New engineering batch: physical-device evidence V10
V10 extends V9 and fail-closes physical-phone claims that were previously represented as booleans/manual evidence without one immutable ADB lifecycle transcript.

New requirements:
- exact package identity in lifecycle transcript;
- same physical-device session_id in transcript and evidence JSON;
- touch observed;
- sensor-landscape observed;
- expandable aspect observed;
- safe-area behavior observed;
- background/resume preserves the exact same numeric PID;
- transcript is non-empty, safe-path, SHA-256 bound, and session-time bounded;
- V9 installed-byte, performance-provenance and crash-free-logcat chain remains mandatory;
- validator cannot promote FINAL/PLAY_READY.

Files:
- `ReleaseOps/mobile/validate_game_device_evidence_v10.py`
- `ReleaseOps/mobile/test_validate_game_device_evidence_v10.py`
- `.github/workflows/thf-game-physical-device-evidence-tooling-v10.yml`

Commits:
- `3ed30b9c40f55a89dd164469f24a2b61f578260b` — validator V10
- `a9e6b48c5fe61733f10a80e3a9bd6e05a70ae566` — V10 regressions
- `3f51545d0563e137b27d5f7c6d661b61df30a9e7` — V10 CI
- `315c371a1aff4b1cf52523ad97f3b3068f7b3978` — fix test-module execution bug
- `2997fc5a2ebd6f228edf3b912bcd1f6142203d24` — keep positive lifecycle fixture inside declared phone session

## CI evidence
Final workflow run: `34821721771` — SUCCESS.
- compile V7–V10: PASS
- preserve V9 regression chain: PASS
- V10 lifecycle/touch/orientation regressions: PASS
- non-promotional FINAL gate assertion: PASS

Two earlier V10 CI attempts failed for test/tooling reasons only:
1. test import called `exec_module()` with the ModuleSpec instead of the module object;
2. positive test fixture ended 10 seconds outside the declared phone session.
Both were fixed without weakening the validator or changing any game candidate.

## Exact candidates remain unchanged
- Terra: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games: `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games: `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

## Release truth
All six remain `NOT_FINAL / PHYSICAL_DEVICE_PENDING`.
No candidate may be called FINAL or PLAY_READY until the same exact installed APK bytes are exercised on a real Android phone in one evidence-bound session covering install/cold launch, touch, sensor-landscape/orientation, safe area, same-PID background/resume, offline/network behavior, crash-free core gameplay, FPS/RAM/thermal, plus product-specific gameplay (Terra world/avatar/locomotion/camera interaction; Rift combat; Spark/Learn progression; Rush/Fitness sensor-driven repetitions).

## Safety / unchanged external systems
- no production signing
- no Play publishing
- no Cloudflare production cutover
- no Solana/token mutation
- no canonical archive overwrite
- WAVE_MAWJA untouched and isolated
