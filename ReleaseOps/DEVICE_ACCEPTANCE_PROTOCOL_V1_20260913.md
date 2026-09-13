# Android Physical-Device Acceptance Protocol — current revision 2026-09-14

Purpose: prevent build/package/static PASS from being mistaken for a real mobile-game release. Exact-candidate device evidence is mandatory and is invalidated by any APK byte change.

## Candidate identity lock

Before installation, the APK SHA-256 must exactly match the active ReleaseOps matrix. Evidence from any other hash is not transferable.

Current game candidate hashes:

- THF Terra / Nexus World: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- THF Rift / Nexus Arena: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- THF Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- THF Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- THF Learn Games: `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- THF Fitness Games: `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

Historical Terra/Rift APKs `388f3c09...b18c7` and `fe35328b...024b1` are explicitly ineligible because they retained a portrait hardware requirement.

## Mandatory checks per game/game-like app

1. Exact APK SHA-256 is recomputed locally and matches the active candidate.
2. Android install succeeds without parse/signature/package failure.
3. Cold launch after force-stop succeeds; no immediate process exit, missing Godot project payload, renderer fatal, blank fatal screen, ANR, or crash.
4. Package identity/version correspond to the candidate lane.
5. Touch controls and touch-safe HUD/layout work on a physical phone; no desktop-only control dependency.
6. Orientation/layout contract works on-device. Terra/Rift specifically require sensor-landscape and expandable layout with no desktop window override behavior.
7. Background -> foreground resume works, followed by re-launch after process kill.
8. Network loss/recovery is tested. Network-required surfaces must fail/recover honestly; local modes must remain genuinely local and must never simulate ranked/social/economy/world mutation.
9. Core user journey is completed without a crash.
10. Record FPS/frame evidence, RAM, and thermal observation during real interaction rather than launch-only idle.
11. Record device manufacturer/model, Android version/API, install timestamp, package, exact APK SHA-256 and test notes.
12. No secret/token material appears in UI, evidence, or logs.

## Product-specific game evidence

### Terra / Nexus World
- real player/avatar loads and renders;
- locomotion responds to phone controls;
- player camera works;
- world/NPC interaction executes real behavior;
- weather/day-night/visual systems that are present must not break mobile interaction/performance;
- online world mutation remains backend-authoritative.

### Rift / Nexus Arena
All Terra-style player/movement/camera evidence where applicable, plus:
- real combat input and combat interaction succeeds;
- combat evidence field `combat_pass=true` is mandatory;
- ranked/economy outcomes may not be produced locally as fake online state.

### Spark / Learn Games
- learning-game interaction loop executes beyond static navigation/UI;
- score/progression/mastery behavior changes from real input;
- no template/wrapper-only acceptance.

### Rush / Fitness Games
- physical sensor/motion gameplay is exercised on real hardware when the candidate claims it;
- `sensor_motion_pass=true` is mandatory;
- repetition/motion state must be driven by actual sensor behavior, not a mocked online/ranked result.

## Evidence tooling

`ReleaseOps/mobile/capture_android_device_evidence_v2.py` captures objective adb evidence for an exact APK: SHA lock, install, launch/process presence, lifecycle smoke, meminfo, gfx framestats, thermal snapshot and logcat fatal markers. It intentionally leaves touch/orientation/gameplay/offline-network/combat/sensor assertions false until actually observed.

`ReleaseOps/mobile/mobile_real_function_gate.py` performs the final fail-closed evidence check. Use:

- Rift: `--requires-combat`
- Rush/Fitness Games: `--requires-sensor-motion`

A CI PASS or objective collector output alone is never DEVICE-PASS.

## Evidence classification

- `DEVICE-PASS`: every mandatory and product-specific check passes for the exact candidate hash.
- `DEVICE-FAIL-RUNTIME`: installation works but runtime/interaction fails.
- `DEVICE-FAIL-INSTALL`: Android refuses the exact candidate.
- `DEVICE-INCONCLUSIVE`: candidate hash, package/version, or required observation cannot be proven.

## Promotion gate

Only exact-SHA DEVICE-PASS may proceed to final production-signing preparation / Play Internal readiness. This protocol does not authorize production signing, Play publication, Cloudflare production cutover, Solana/token transactions, or destructive cloud actions.

## WAVE isolation

WAVE_MAWJA does not inherit THF evidence, APKs, source, runtime configuration, or device acceptance. Its exact RC13/RC14 canonical runtime/source must first be recovered and verified independently; older RC9 material must not be substituted.
