# Rift RC36 Source Delta

Baseline artifact SHA: `ed3d1e3ede527b39f0110bbb83aab8e0d91cc4be4367b1634f14e17c02106558` (RC35).

Changed Rift-only files:
- `THF_Nexus_Arena_Core/project.godot`: RC36 marker + Android ETC2/ASTC import.
- `THF_Nexus_Arena_Core/export_presets.cfg`: test AAB name + 42070 / 4.7.0-rc36.
- `THF_Nexus_Arena_Core/android-arena/app/build.gradle`: synchronize versionCode/versionName to 42070 / 4.7.0-rc36; API 36 preserved.
- `THF_Nexus_Arena_Core/scripts/rift_rc36_android_export_preflight_gate.py`: new focused export preflight gate.

Focused and clean-extract gates: 12/12 PASS. Deterministic artifact SHA: `6b738d80e3e97376cd4e7a9498e653b90bc7a926076c2c6e98431209cdc5147f`.

No tactical/combat authority, Terra, WAVE, or unrelated THF application logic changed.
