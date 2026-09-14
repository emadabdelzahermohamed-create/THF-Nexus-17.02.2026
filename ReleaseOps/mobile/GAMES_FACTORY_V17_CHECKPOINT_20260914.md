# THF Games Factory — V17 checkpoint — 2026-09-14

## Scope reviewed
THF Terra/Nexus World, THF Rift/Nexus Arena, THF Spark, THF Rush, THF Learn Games/Fitness Games, and shared physical-device release evidence tooling.

## Authoritative source/change inspection
This batch started by inspecting the current repository head and comparing the prior Games checkpoint `2866ab568c65fd9ca6e2b771051ce6a56046be37` to pre-batch head `bc4c023ccb1d62e399b78a95a9ed6f6394194499`.

The intervening range was 10 commits ahead and changed only Apps/Release Factory files (`thf-app-physical-device-evidence-tooling-v12.yml`, latest-assets baseline workflow, Release Factory state, and Apps V12 acceptance/validator/tests). No game payload/source candidate or Games V16 file changed in that range. Therefore already-proven Godot/parser/import/API36/package/game-payload work for the unchanged candidates was deliberately not rerun.

The V16 checkpoint remains the prior authoritative game-device baseline: all six products remain NOT_FINAL / PHYSICAL_DEVICE_PENDING until exact-candidate physical-device acceptance succeeds.

## V17 completed — Android boot-session binding
V16 already bound every required gameplay capability process proof to the physical-device fingerprint, exact installed candidate APK SHA, current registry SHA, exact observation timestamp, foreground/resumed package/PID, successful `dumpsys activity`, and successful `pidof`.

V17 closes a distinct replay/substitution gap: the same physical phone can retain the same device fingerprint across a reboot. A capability proof from before reboot must not be mixed with another capability proof after reboot and presented as one coherent physical test session.

Every required gameplay capability process proof must now include a canonical Android/Linux boot UUID captured from the same physical phone using exactly:

`adb -s <serial> shell cat /proc/sys/kernel/random/boot_id`

Required markers:
- `THF_ANDROID_BOOT_ID=<canonical UUID>`
- `THF_BOOT_ID_CAPTURE_METHOD=ADB_CAT_PROC_BOOT_ID`
- `THF_BOOT_ID_CAPTURE_COMMAND=cat /proc/sys/kernel/random/boot_id`
- `THF_BOOT_ID_CAPTURE_EXIT_CODE=0`

All required gameplay capability process proofs in one acceptance bundle must carry exactly the same boot UUID. Cross-reboot evidence mixing therefore fails closed.

A real capture helper, `capture_game_process_provenance_v17.py`, delegates the full V16 physical-device/package/APK/registry/gameplay verification, then rechecks the connected physical-device fingerprint before capturing the boot UUID. It rejects invalid/non-canonical boot IDs, failed boot-ID capture, or a device change. It recomputes the evidence SHA and never creates gameplay PASS or FINAL/PLAY_READY.

## Regression and CI evidence
V17 tooling added:
- `validate_game_device_evidence_v17.py`
- `capture_game_process_provenance_v17.py`
- `test_validate_game_device_evidence_v17.py`
- `test_capture_game_process_provenance_v17.py`
- `.github/workflows/thf-game-physical-device-evidence-tooling-v17.yml`
- `PHYSICAL_DEVICE_ACCEPTANCE_V17_20260914.md`

The first V17 CI run `34855430797` failed on a test-loader defect after compilation and V16 preservation had already passed. The validator was not weakened. The loader was fixed.

The second run `34855558490` again preserved compilation and V16, and six-product V17 positive coverage plus all but one negative test passed. The remaining failure was a test-fixture `KeyError` caused by assuming a literal Terra process-provenance key named `camera`; the fixture was changed to select an actual required provenance key dynamically. The validator was not weakened.

Final V17 CI run `34855785636`, job `104014860804`, completed SUCCESS. It passed:
- compile of V7–V17 validators, tests and capture helpers;
- complete V16 validator/capture regression preservation;
- V17 all-six-products same-boot positive coverage;
- V17 cross-reboot rejection and boot-marker negative coverage;
- V17 physical boot-bound capture-helper regressions;
- assertion that V17 remains non-promotional and boot-bound.

## Release truth / remaining external gate
V17 tooling PASS is not a physical-phone acceptance PASS. No FINAL/PLAY_READY promotion occurred.

Terra/Rift/Spark/Rush/Learn Games/Fitness Games remain NOT_FINAL / PHYSICAL_DEVICE_PENDING until the full exact-installed-APK physical-phone run exists in one coherent device/boot session, including install/cold launch, touch, sensor-landscape/orientation/safe-area where required, same-process background/resume, offline/local/online truth, crash-free logcat, FPS/RAM/thermal observation, and product-specific real gameplay evidence: Terra avatar/player movement/camera/world-NPC interaction; Rift those plus real combat state change; Spark/Learn real learning progression; Rush/Fitness real sensor motion and increasing repetition count.

No production signing, Play publishing, Cloudflare production cutover, Solana/token mutation, canonical game archive overwrite, or WAVE_MAWJA change was performed by this Games batch.
