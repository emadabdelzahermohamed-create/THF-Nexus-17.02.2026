# THF Terra RC34 — Android API 36 Gate

Date: 2026-09-12
Status: PASS

- Canonical source: `THF_Terra_v4.6.8_RC34_REMOTE_LOD_HYSTERESIS_CUMULATIVE_SOURCE.zip`
- Canonical SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`
- GitHub Actions run: `34676649980`
- Godot: `4.7.2.stable`
- Android target/API toolchain: 36
- Import: PASS (`import_rc=0`)
- Headless boot: PASS (`boot_rc=0`)
- Android Gradle template: PASS (`android_template_install_rc=0`)
- Debug/test AAB export: PASS (`android_export_rc=0`)
- Test AAB SHA-256: `3af39232213171de0a5069dea2dfe3dab585d75f7246bf0bd75d61bb8a7dbee3`
- Evidence artifact ID: `10292063624`
- Evidence artifact ZIP SHA-256: `c92d52957cb6da1beeebbfe3b2edeb0c1d542f6c971d8680cbc8f96ca1bb0ebe`

Safety assertions:

- Production signing: NOT PERFORMED
- Canonical source archive mutated: FALSE
- WAVE_MAWJA touched: FALSE
- Persistent cloud credentials: NOT USED; GitHub OIDC/WIF + IAP/OS Login only

CI repair applied only to the temporary extracted workspace: the verified official Godot `android_source.zip` is installed deterministically into `res://android/build`, and `res://android/.build_version` is written as `4.7.2.stable`, matching Godot 4.7.2's own Android template installer contract. Canonical source bytes remain unchanged.

Next: retain this candidate as unsigned/test evidence and proceed to the next unblocked THF release-readiness gate. Production signing/Play publication remains explicitly gated.
