# THF Rift RC37 — Android API 36 Gate

Date: 2026-09-12
Status: PASS

- Canonical source: `THF_Rift_v4.7.1_RC37_HUMAN_RELOAD_TIMING_PARITY_CUMULATIVE_SOURCE.zip`
- Canonical SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
- GitHub Actions run: `34676685100`
- Project root: `THF_Nexus_Arena_Core`
- Export preset: `Android AAB Candidate`
- Godot: `4.7.2.stable`
- Android target/API toolchain: 36
- Import: PASS (`import_rc=0`)
- Headless boot: PASS (`boot_rc=0`)
- Android Gradle template: PASS (`android_template_install_rc=0`)
- Debug/test AAB export: PASS (`android_export_rc=0`)
- Test AAB SHA-256: `1eb449b061135984bbdef5cecf012496b8d667963f37d813518f4fcd389652c7`
- Evidence artifact ID: `10292268329`
- Evidence artifact ZIP SHA-256: `0bca0ffdb2adbaf7281bb846d22968841d44c186f0a84823199184787dfca795`

Safety assertions:

- Production signing: NOT PERFORMED
- Canonical source archive mutated: FALSE
- WAVE_MAWJA touched: FALSE
- Persistent cloud credentials: NOT USED; GitHub OIDC/WIF + IAP/OS Login only

CI repair applied only to the temporary extracted workspace: the verified official Godot `android_source.zip` is installed deterministically into `res://android/build`, and `res://android/.build_version` is written as `4.7.2.stable`, matching Godot 4.7.2's own Android template installer contract. Canonical source bytes remain unchanged.

Next: retain this candidate as unsigned/test evidence and proceed to the next unblocked THF release-readiness gate. Production signing/Play publication remains explicitly gated.
