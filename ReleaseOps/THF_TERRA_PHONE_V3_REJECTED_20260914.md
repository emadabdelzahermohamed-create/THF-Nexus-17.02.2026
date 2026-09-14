# THF Terra RC34 Phone V3 — REJECTED

Date: 2026-09-14

Artifact:
- `THF-TERRA-4.6.8-RC34-PHONE-V3.apk`

Physical-device result:
- Android package installer reports that the package appears invalid and refuses installation.

Disposition:
- HARD REJECT
- DO NOT PROMOTE
- DO NOT REUSE AS INSTALLABILITY BASELINE
- DO NOT DOWNGRADE TO OLD CORE/WEB UI AS A WORKAROUND

Required next candidate:
1. Build from latest authoritative Terra lineage only.
2. Preserve current MPFB/MakeHuman + UAL + native Godot runtime and all later cumulative Terra features.
3. Run `apksigner verify --verbose --print-certs` on the final APK.
4. Run `aapt2 dump badging` / manifest identity validation on the final APK.
5. Confirm expected package, versionCode/versionName, targetSdk 36, and arm64-v8a.
6. Run an Android 12-compatible install smoke test (`adb install -r`) before sending it to the user when an emulator/device lane is available.
7. Capture SHA-256 only after final signing and all post-processing.
8. If any check is missing, fail closed and do not deliver.

This rejection is a permanent regression-prevention input for subsequent THF app/game pipelines.
