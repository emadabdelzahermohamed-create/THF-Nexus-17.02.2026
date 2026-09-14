# THF Games Factory — V16 checkpoint — 2026-09-14

## Scope reviewed
THF Terra/Nexus World, THF Rift/Nexus Arena, THF Spark, THF Rush, THF Learn Games/Fitness Games, and shared physical-device release evidence tooling.

## Source/change decision
The previous games checkpoint was `ba64fbbdbff4bc0a3bff65ff054e56de09ad1b7a`. The intervening repository commits before this batch were Apps/Core/TokenOps work; no game payload/source candidate change was identified in that interval. Therefore previously proven Godot/parser/import/API36/package/game-payload gates were not rerun solely to reproduce the same result.

## V16 completed
V16 extends V15 foreground-process provenance by binding every required gameplay capability's process proof to the exact physical-device fingerprint, exact APK candidate SHA, current registry SHA and exact manual-observation UTC timestamp. The process capture must also report successful `dumpsys activity` and `pidof` exit codes. V16 remains fail-closed and non-promotional.

A real ADB capture helper, `capture_game_process_provenance_v16.py`, was added. It refuses emulator/QEMU devices, requires exactly one authorized physical device, verifies the connected-device fingerprint against the evidence session, verifies the existing gameplay evidence bytes/SHA, requires the exact game package to be the resumed foreground activity with one live numeric PID, and writes a SHA-bound V16 process-provenance file. It never creates gameplay PASS or FINAL/PLAY_READY status.

## Regression/CI evidence
Initial V16 CI run `34850255832` correctly failed on a test-loader defect after compile and V15 preservation had passed. The validator was not weakened. The loader was corrected in commit `d5c66dbab6e99484547ea965d0cac1c18ff29a78`.

Validator-only V16 run `34850360807` completed SUCCESS. The expanded run `34850559539` also completed SUCCESS, including:
- compile of V7–V16 validators/tests plus the capture helper;
- V15 regression-chain preservation;
- V16 exact-provenance regressions;
- V16 physical process-capture helper regressions;
- assertion that V16 remains non-promotional and exact-bound.

Negative coverage includes device-fingerprint substitution, exact-APK substitution, registry substitution, observation-time substitution, failed dumpsys/pidof capture, wrong/background resumed package, wrong physical device and tampered gameplay evidence.

## Release truth / remaining external gate
No physical Android phone was attached to this execution environment, so no device PASS was manufactured. Terra/Rift/Spark/Rush/Learn Games/Fitness Games remain NOT_FINAL / PHYSICAL_DEVICE_PENDING until the full exact-installed-APK physical run succeeds, including install/cold launch, touch, sensor-landscape/orientation/safe-area where required, same-process background/resume, offline/local/online truth, crash-free logcat, FPS/RAM/thermal observations, and product-specific real gameplay evidence.

No production signing, Play publishing, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite, or WAVE_MAWJA change was performed by this games batch.
