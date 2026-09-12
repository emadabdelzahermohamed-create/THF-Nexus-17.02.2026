# Rift RC39 source delta

- app/services/arena.py: server-owned dropped weapon loot now preserves chambered and attachment state; pickup validates attachment ids fail-closed; empty-magazine chamber state is bounded false; pickup into the currently equipped empty slot no longer clobbers the incoming weapon via stale active-state storage.
- android-arena/app/build.gradle: 42073 / 4.7.3-rc39; compileSdk/targetSdk 36 unchanged.
- export_presets.cfg: 42073 / 4.7.3-rc39; package/AAB/arm64/unsigned policy preserved.
- project.godot: stage RC39 only; ETC2/ASTC setting preserved.
- config/animations.json: RC39 state-persistence contract metadata.
- scripts/rift_rc39_dropped_weapon_state_gate.py: focused server lifecycle gate.

No .gd gameplay source changed in RC39. Hit/damage/ranked authority unchanged.
