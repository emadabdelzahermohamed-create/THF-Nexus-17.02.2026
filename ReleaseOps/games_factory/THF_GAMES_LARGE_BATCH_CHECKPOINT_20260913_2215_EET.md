# THF Games Large-Batch Checkpoint — 2026-09-13 22:15 EET

## Safety / truth boundary
THF game engineering only. Canonical source archives remained immutable. WAVE_MAWJA was not read into, copied into, or modified by this batch. GitHub OIDC/WIF with Drive read-only access was used; no persistent cloud key was introduced. No production signing, Play publishing, Cloudflare production cutover, Solana/token action, or destructive cloud change occurred.

Nothing in this checkpoint is FINAL or PLAY_READY. Exact-candidate physical-phone acceptance remains mandatory.

## Starting authoritative blockers
The latest game checkpoint for the exact Spark/Rush RC3 source SHAs recorded:
- Spark source SHA-256 `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0`: missing only `timed_or_frame_loop_OR_render_or_motion`.
- Rush source SHA-256 `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b`: missing `timed_or_frame_loop_OR_render_or_motion` and `fitness_domain`.

Previously proven package/API36 results for the unchanged canonical sources were not rerun merely for repetition. This batch created changed-byte disposable candidate overlays, therefore the affected source/build/package gates were rerun.

## Engineering implemented
Commit `a70d28093f147e5c7e976f885b1bd59360818261` added `ReleaseOps/games_factory/apply_spark_rush_real_game_overlay_v1.py`.

The overlay is applied only to clean extracted disposable source trees and fail-closes if a custom Android Application would be overwritten.

### Spark candidate
Added a lifecycle-aware Canvas game view driven by `Choreographer` frame callbacks, with real touch hit-testing, moving target, math-question progression, score, streak and level state. Offline semantics are explicitly local and do not synthesize ranked/social/economy state.

### Rush candidate
Added a lifecycle-aware Canvas fitness game view with `SensorManager`, linear-acceleration/accelerometer motion input, real motion magnitude, repetition thresholding/debounce, local rep/streak session state, touch reset and visible motion feedback. Offline semantics remain local only and do not synthesize ranked/social/economy state.

Commit `0a2d19d722b0e83ee6c961457f9d6fa7a0a784fe` added workflow `.github/workflows/thf-spark-rush-real-game-overlay-v1.yml`, binding exact source SHA verification, source contract, regression, release APK build, ZIP integrity, package identity and API36 evidence.

An initial Rush run exposed a validator false negative: the fitness-domain regex accepted singular `rep` but not the actual `reps`/sensor vocabulary used by the real candidate. Commit `def7e965a9ce915c3da4dfdb7c50b79267f126f7` corrected the fail-closed auditor to recognize plural reps/repetitions/sets and sensor/motion/accelerometer signals. Commit `67cbd9ed974eba888bcd4d832b662262dded9abe` added regression coverage for sensor-driven plural-reps fitness behavior.

## Authoritative changed-byte candidate run — PASS
Workflow: `THF Spark Rush Real Game Overlay V1`
Run: `34776954754`
Result: Spark `SUCCESS`; Rush `SUCCESS`.

Both jobs passed:
- exact authoritative source SHA verification;
- source ZIP integrity and clean extraction;
- disposable overlay application;
- game-like real-function source contract;
- 4 Android regression/lint tasks;
- `assembleRelease`;
- APK ZIP integrity;
- exact canonical package identity;
- `targetSdkVersion=36`.

### Spark evidence
- Authoritative input SHA-256: `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0`
- Candidate tree-manifest SHA-256: `118123bc0cdc9bfc961706fc171d874812017afe4cd479283011becb264c04bc`
- Game-like source contract: `PASS`
- APK SHA-256: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- APK package: `com.topherofit.thf.spark`
- targetSdk: `36`
- Artifact: `THF-spark-REAL-GAME-OVERLAY-V1`
- Artifact ID: `10323696925`
- Artifact digest: `sha256:09df3000b54b836db725771c6ccb3a440a70bb69dd2280bd70310614eb0b08ea`

### Rush evidence
- Authoritative input SHA-256: `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b`
- Candidate tree-manifest SHA-256: `dec621f68effd73f73a70c3e623c52a29a2b9dfea6fd65fbf9258f14dbe4129c`
- Game-like source contract: `PASS`
- APK SHA-256: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- APK package: `com.topherofit.thf.rush`
- targetSdk: `36`
- Artifact: `THF-rush-REAL-GAME-OVERLAY-V1`
- Artifact ID: `10323397773`
- Artifact digest: `sha256:5da6e6dca8ef11a1404e904bb3a610d07424592a9612ae6489fd2a15a9e7331a`

For both candidates: `PRODUCTION_SIGNING=NO`, `DEVICE_STATUS=PENDING`, `FINAL_STATUS=NOT_FINAL`.

## Other game streams — no duplicate work
Terra RC34 / Rift RC37 mobile configuration, Godot 4.7.2 import/headless, shared GLB/MPFB/UAL container integrity and previously proven staging/package gates were not repeated for unchanged candidate/source SHAs. Their exact-candidate physical-device gate remains open.

Learn Games / Fitness Games remain engineering-first and are not promoted from their known thin source contracts merely because Spark/Rush progressed. Existing provenance and real-function blockers remain authoritative until changed bytes or stronger source lineage is produced.

## Next highest-priority gates
1. Physical Android exact-SHA acceptance for Spark APK `9fffc4d9...165ea` and Rush APK `3e9aabae...d0e3a`: install/cold-launch, touch, responsive/safe layout, background/resume, offline/network transition, core game session, crash-free smoke, FPS/RAM/thermal; Rush must additionally prove real sensor-driven rep behavior on hardware.
2. Terra/Rift exact-candidate device acceptance remains mandatory: sensor-landscape, touch HUD, avatar/player load, locomotion, camera, world/combat interaction, background/resume, network/offline transition and FPS/RAM/thermal.
3. Continue Learn/Fitness Games only from authoritative/recovered lineage with real player/input/camera/game-loop implementation; do not substitute wrappers or static UI.
4. Extend shared avatar evidence from container integrity into runtime animation-tree/state-machine, locomotion/IK/root-motion/retarget and gameplay-binding evidence when candidate bytes change or a device/GPU runner is available.
