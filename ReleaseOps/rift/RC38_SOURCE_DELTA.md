# Rift RC38 source delta

Scope: THF Rift/Nexus Arena only. Baseline artifact SHA `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`.

Changes:
- `app/services/arena.py`: `pickup_weapon` now cancels any pending human reload before loot/equip mutation (`reason=pickup_weapon`), preventing an old reload timer from completing against a newly picked-up weapon.
- `config/animations.json`: records RC38 server-owned pickup/reload lifecycle guarantees.
- `project.godot`: Rift stage synchronized to RC38; Android ETC2/ASTC setting preserved.
- `export_presets.cfg`: versionCode 42072 / versionName 4.7.2-rc38; package/API36/AAB/arm64/unsigned policy preserved.
- `android-arena/app/build.gradle`: versionCode 42072 / versionName 4.7.2-rc38; compile/target SDK 36 preserved.
- New focused gate: `scripts/rift_rc38_pickup_reload_lifecycle_gate.py`.

Canonical artifact SHA-256: `46ee385c21fb2e437f48a051ab59d90010eb6b0b0b9727f269b37cfa20711c81`.
