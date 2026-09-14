# THF Games — Physical Device Acceptance V15

Status: **NON-PROMOTIONAL GATE**. Passing this validator does not by itself make any game FINAL or PLAY_READY.

## New V15 requirement
Every gameplay capability evidence file accepted by V14 must have a separate SHA-256-bound process-provenance record captured while the exact game package is the Android foreground/resumed activity.

The provenance record must bind the same session, package, capability and gameplay-evidence SHA, and must contain a positive foreground PID, an equal resumed PID, `THF_ACTIVITY_RESUMED=TRUE`, `THF_PROCESS_ALIVE_AFTER=TRUE`, and `THF_PROCESS_CAPTURE_METHOD=ADB_DUMPSYS_ACTIVITY_PIDOF`.

This prevents gameplay evidence from a wrapper, stale/background process, another package, or substituted evidence file from satisfying the physical-device gate.

## Required physical run remains unchanged
Use one real Android-device session for the exact installed APK candidate. Preserve the existing install/cold-launch, touch, sensor-landscape/orientation/safe-area, same-process background/resume, offline/local/online, crash-free, performance, and per-product gameplay requirements from V7–V14.

Terra/Rift still require real avatar/player load, movement, camera and world interaction; Rift also requires combat state change. Spark/Learn Games require learning progression. Rush/Fitness Games require sensor events and increasing repetition count.

## Release truth
Until the complete exact-candidate physical-device evidence chain passes, release truth remains `FINAL_OR_PLAY_READY=FALSE` and physical-device acceptance remains pending. Source/static/build-only evidence, wrapper behavior, or synthetic online state cannot promote a candidate.
