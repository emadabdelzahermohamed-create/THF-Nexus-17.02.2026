# RIFT RC41 source delta

- `app/services/arena.py`: authoritative loot distance/reachability helpers; pickup now requires range + server collision sweep and selects nearest reachable weapon.
- `scripts/rift_rc41_server_pickup_reachability_gate.py`: focused source/behavior/integration gate.
- `config/animations.json`: RC41 server-owned pickup reachability contract metadata.
- `project.godot`: stage RC41 only; no `.gd` gameplay delta.
- `export_presets.cfg`: 42075 / 4.7.5-rc41; package/API36/arm64/AAB/unsigned policy preserved.
- `android-arena/app/build.gradle`: 42075 / 4.7.5-rc41; compile/target SDK 36 preserved.
