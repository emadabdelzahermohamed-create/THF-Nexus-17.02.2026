# Rift RC40 source delta

- `app/services/arena.py`: added fail-closed `_clear_active_weapon_state`, used for no-weapon sync and final-weapon drop; prevents stale chamber/attachments/aim/recoil projection.
- `scripts/rift_rc40_empty_inventory_state_gate.py`: focused authoritative lifecycle gate.
- `config/animations.json`: records RC40 server-owned state-hygiene contract.
- `android-arena/app/build.gradle`, `export_presets.cfg`, `project.godot`: synchronized 42074 / 4.7.4-rc40 / RC40 while preserving API36, package id and unsigned production policy.
- No native `.gd` gameplay source changed.

Artifact SHA-256: `dc96736d909913d4e8f436121de1d8e34b7ed8643d5b4f207251ff66760765c2`.
