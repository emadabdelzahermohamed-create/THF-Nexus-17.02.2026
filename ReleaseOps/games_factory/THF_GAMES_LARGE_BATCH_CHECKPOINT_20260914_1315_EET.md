# THF Games Factory Checkpoint — Raw ADB Transition Evidence V12

## Same-SHA authority
At run start, `main` had advanced because of Apps/TokenOps work, while the authoritative game candidate bytes remained unchanged from the Games V11 checkpoint. Proven same-SHA Godot/parser/import/API-36/package/game-payload gates were therefore not rebuilt.

Exact APK candidates remain:
- Terra: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games: `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games: `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

Release truth remains `FINAL_OR_PLAY_READY=FALSE` and physical-device acceptance remains pending.

## Finding
Games V11 required one hash-bound offline -> local-gameplay -> online-restored transcript, but the summary transcript could still be the sole artifact describing all three states. Apps Factory had already closed an analogous gap by requiring separate raw ADB captures. Games Factory needed the same anti-substitution property without rebuilding unchanged candidates.

## V12 implemented
`ReleaseOps/mobile/validate_game_device_evidence_v12.py` layers V11 and requires exactly three raw captures:
1. offline connectivity — `adb shell dumpsys connectivity`
2. local game/UI state — `adb shell uiautomator dump /dev/tty`
3. restored online connectivity — `adb shell dumpsys connectivity`

Every raw capture must:
- be a distinct non-empty file with a distinct lowercase SHA-256;
- bind the same session ID, package, exact candidate APK SHA, registry SHA and physical-device fingerprint;
- bind its exact approved ADB command, capture timestamp and successful ADB exit code;
- carry the correct capture-kind marker;
- occur inside the V11 observation interval with strict `offline < local < online` timestamp ordering.

The V11 summary transcript must additionally bind the exact SHA-256 of all three raw files. Missing/extra raw captures, wrong commands, wrong identity, failed ADB, reordered timestamps, duplicate files/digests or summary-SHA substitution all fail closed. V12 cannot self-promote FINAL/PLAY_READY.

## Regression/CI evidence
Implementation:
- `85849cd04233e95b34b1e4701c24adeb4dcab287` — V12 validator.
- `36c5d6740983754b910553258354fe7971b49ee3` — V12 regression suite.
- `f7bdb592b063b10d04afc0231727b2c21347b1dc` — V12 CI workflow.

GitHub Actions run `34832196334`, job `103937859909`, on exact head `f7bdb592b063b10d04afc0231727b2c21347b1dc`: **SUCCESS**.
The workflow compiled the V7-V12 validator chain, preserved V11 regressions, ran V12 positive/negative regressions, and asserted that V12 contains no `FINAL_OR_PLAY_READY=TRUE` promotion path.

## Remaining non-substitutable gate
No physical Android phone was available to this execution environment. The six candidates therefore remain NOT_FINAL / PHYSICAL_DEVICE_PENDING until the exact installed APK bytes complete the single-session physical acceptance chain: install/cold launch; touch; sensor-landscape/orientation and safe area; same-PID background/resume; V12 raw offline/local/online transition; crash-free core gameplay; FPS/RAM/thermal; Terra/Rift avatar, locomotion, camera and world interaction; Rift combat; Spark/Learn progression; Rush/Fitness sensor-driven repetitions.

## Safety / isolation
No production signing, Play publish, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite or WAVE_MAWJA change occurred in this batch.
