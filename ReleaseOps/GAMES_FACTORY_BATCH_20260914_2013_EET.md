# THF Games Factory — Large-Batch checkpoint — 2026-09-14 20:13 EET

## Authority inspected
- Latest repository head observed before game work: `407f16d11c7e04dae8e61324f1bd9011f1d17544` (Apps-only checkpoint after the latest game checkpoint).
- Latest authoritative Rift QA evidence checkpoint: `eb9d85d80c196636b0b673da0a520a691835c648`.
- Rift canonical source SHA-256 remains `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`.
- Rift RC37 Phone V1 APK SHA-256 remains `8d023174dc30cb7899c21b66e6d7deaca8e16ddd0371f337f589a812c22a8f15`.
- Exact APK payload gate was already PASS; it was not repeated for the same SHA.
- Spark/Rush authoritative RC4 real-game candidates remain unchanged in the durable factory state: Spark APK `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`; Rush APK `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`.

## New engineering work
The exact Rift APK is functionally packaged but is 196,716,096 bytes. Its payload inspection shows that the largest entry is the arm64 Godot runtime (`libgodot_android.so`, 76,181,608 bytes) and that substantial validated avatar/texture content accounts for much of the remainder. The full APK therefore remains a QA/full candidate, not the requested compact delivery artifact.

To avoid deleting validated content merely to satisfy an APK-size target, this batch added a separate Play-oriented AAB export path:
- `ReleaseOps/scripts/godot_candidate_tree_aab_v1.sh` at commit `3244de7af1e256ab149e5d85465440b3bd3371cd`.
- `.github/workflows/thf-rift-rc37-phone-v1-aab-build.yml` at commit `6b397e250eb37a981a719eebc5170820a7646007`.

The AAB helper is fail-closed and preserves the same exact-source overlay path. It forces Android App Bundle export only in the disposable candidate tree, retains Godot 4.7.2 headless import/boot/parser checks, validates bundle ZIP integrity, requires `BundleConfig.pb`, Android manifest, arm64 Godot runtime and packaged game assets, and keeps `production_signing=false`, `device_status=PENDING`, `final_status=NOT_FINAL`.

The AAB workflow reuses the exact canonical Rift source SHA, the same mobile overlay, same genuine local-training/combat overlay, same staging endpoint binding, sensor-landscape, expandable aspect and zero desktop override. It explicitly records `content_pruned=FALSE` so this path cannot hide content deletion as an optimization.

## Execution status
The GitHub connector-created commits did not automatically produce a workflow run for head `6b397e250eb37a981a719eebc5170820a7646007`; querying Actions by that head returned zero runs. Therefore no AAB build PASS, size claim, Play upload-budget claim, or artifact SHA is asserted in this checkpoint. The source/workflow path exists and is ready for the next executable workflow dispatch/push context.

## Physical-device gate
No physical Android device is connected to the available execution environment. No install/launch/touch/orientation/background-resume/offline-network/core-gameplay/crash-free/FPS/RAM/thermal evidence is fabricated. Rift still requires exact installed APK/AAB-derived APK evidence, real avatar load, movement, camera and combat state transition on-device. Terra/Spark/Rush/Learn Games/Fitness Games retain their existing exact-candidate physical-device gates.

## Release truth
- `FINAL_OR_PLAY_READY=FALSE`
- `PHYSICAL_DEVICE_STATUS=PENDING`
- `PRODUCTION_SIGNING=FALSE`
- `PLAY_PUBLISH=FALSE`
- `PRODUCTION_CUTOVER=FALSE`
- Online ranked/social/economy/world mutation remains backend-authoritative.
- Local modes must remain genuine local state and must not fabricate online state.
- No validated game content was removed in this batch.
- WAVE_MAWJA was not modified.
