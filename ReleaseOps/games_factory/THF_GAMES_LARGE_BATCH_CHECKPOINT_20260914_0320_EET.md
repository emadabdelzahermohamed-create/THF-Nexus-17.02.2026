# THF Games Large-Batch Checkpoint — 2026-09-14 03:20 EET

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING
Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games and shared game/mobile acceptance systems.

## Authoritative state inspection

The latest game-specific ReleaseOps checkpoint before this batch was `THF_GAMES_LARGE_BATCH_CHECKPOINT_20260914_0225_EET.md`. No subsequent game source/candidate commit changed the six registered APK bytes before this work began; intervening main-branch commits were in separate app-factory work.

The exact phone candidates therefore remain unchanged:

- Terra `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

No same-SHA Godot/import/export/Gradle/package/API36 gate was rerun.

## Material defect found in device evidence V2

`capture_android_device_evidence_v2.py` did not establish a true background/resume transition. After sending HOME, it called the generic launch helper which performed `am force-stop` before launching again. That proves a second cold launch, not resume of the backgrounded process.

The V2 file was preserved as historical evidence. V3 fixes the semantics instead of rewriting old evidence.

## Physical device evidence V3

Added:

- `ReleaseOps/mobile/capture_android_device_evidence_v3.py`
- `ReleaseOps/mobile/validate_game_device_evidence_v3.py`
- `ReleaseOps/mobile/test_capture_android_device_evidence_v3.py`
- `ReleaseOps/mobile/test_validate_game_device_evidence_v3.py`
- `.github/workflows/thf-game-physical-device-evidence-tooling-v3.yml`
- `ReleaseOps/games_factory/PHYSICAL_DEVICE_ACCEPTANCE_V3_20260914.md`

V3 hardening:

1. Package and APK SHA are derived from the current candidate registry rather than duplicated CLI values.
2. Evidence is bound to SHA-256 of the exact registry bytes, preventing replay/rebinding after candidate-registry drift.
3. Emulator/QEMU/ranchu/goldfish/generic emulator signals are rejected; the acceptance path requires a physical Android phone.
4. Device identity is stored as a SHA-256 fingerprint; raw serial is not persisted, only a short redacted suffix.
5. Background/resume requires the same PID to survive HOME and return to foreground; no force-stop occurs during resume.
6. Objective capture retains install, cold launch, RAM, frame-stat rows, thermal/display/window/package snapshots and crash markers.
7. Manual observations are product-specific structured records requiring PASS + UTC observation timestamp + concrete evidence reference. They start FALSE and are never auto-promoted.
8. Rift requires combat evidence. Rush/Fitness require sensor-motion plus repetition-counting evidence. Terra/Rift require player/avatar, movement/camera and world/NPC evidence. Spark/Learn require learning progression evidence.
9. Online state must explicitly be proven not faked locally; local practice/explore must explicitly be proven genuinely local.
10. Performance requires actual FPS/RAM/thermal observations and duration, but V3 intentionally invents no arbitrary performance threshold.
11. Evidence input is forbidden from self-declaring FINAL/PLAY_READY; promotion remains a separate release gate.

## CI evidence

Workflow: `THF Game Physical Device Evidence Tooling V3`
Run: `34792205777`
Result: SUCCESS.

Successful steps:

- Python compile of V3 collector/validator/tests;
- validation of current exact-candidate registry;
- collector regression tests, including same-PID resume and emulator rejection;
- evidence-validator regression tests across all six products and negative cases;
- explicit assertion that tooling contains no readiness promotion.

CI output contract remains:

- `READINESS_PROMOTION=NO`
- `PHYSICAL_DEVICE_REQUIRED=YES`

## What remains blocked by real hardware

No physical Android phone was attached to this automation environment. Therefore no candidate receives device PASS from this batch.

The exact user/device-lab requirement is now deterministic: obtain each registered APK byte-for-byte, attach one authorized physical Android phone over ADB, run the V3 collector, perform the product-specific manual gameplay observations with concrete evidence references, record FPS/RAM/thermal observations, and run the V3 validator against the unchanged registry.

Until that happens all six candidates remain `PHYSICAL_DEVICE_PENDING` and `NOT_FINAL`.

## Preserved proven state

This batch does not invalidate earlier PASS evidence for unchanged SHAs: Terra/Rift Godot 4.7.2 parser/import/headless and Android package/payload/mobile config gates; Terra/Rift avatar/rig/runtime wiring; Spark/Rush real-game overlay and payload gates; Learn/Fitness real-game/API36/package gates; current artifact provenance; and dynamic fail-closed rejection of unauthenticated sensitive backend mutations remain preserved.

## Safety / isolation

- No canonical source archive was overwritten or deleted.
- No APK candidate bytes were changed.
- No production signing or Play publishing occurred.
- No Cloudflare production cutover or Solana/token action occurred.
- No destructive GCP operation or persistent cloud credential was used.
- WAVE_MAWJA files were not modified by this games batch.

## Next independent engineering block

Without repeating same-SHA build work, the next server-side block is authenticated/role/ownership authority testing with ephemeral local identities and deterministic temporary data, followed by anti-cheat mutation-semantic probes. Physical-phone acceptance can proceed independently when real hardware is available.
