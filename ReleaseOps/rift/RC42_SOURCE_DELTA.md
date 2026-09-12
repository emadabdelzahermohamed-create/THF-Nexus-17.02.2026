# RIFT RC42 source delta

- `app/services/arena.py`: invalid weapon switches now fail closed without cancelling reload or mutating the equipped weapon; empty-inventory holster requests remain forcibly holstered; attachment changes are rejected while server-owned reload is pending.
- `scripts/rift_rc42_weapon_command_fail_closed_gate.py`: focused source/runtime gate for weapon-command lifecycle invariants.
- `config/animations.json`: RC42 server-owned weapon-command fail-closed contract metadata.
- `project.godot`: stage RC42 only; no `.gd` gameplay delta.
- `export_presets.cfg`: 42076 / 4.7.6-rc42; package/API36/arm64/AAB/unsigned policy preserved.
- `android-arena/app/build.gradle`: 42076 / 4.7.6-rc42; compile/target SDK 36 preserved.
