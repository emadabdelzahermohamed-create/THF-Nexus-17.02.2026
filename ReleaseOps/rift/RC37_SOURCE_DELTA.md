# Rift RC37 source delta

Baseline RC36 SHA `6b738d80e3e97376cd4e7a9498e653b90bc7a926076c2c6e98431209cdc5147f`.

Changed Rift-only files:
- `app/services/arena.py`: server-timed human reload lifecycle, pending/cancel/complete state, down-state cancellation.
- `android-arena/app/build.gradle`: 42071 / 4.7.1-rc37, API 36 preserved.
- `export_presets.cfg`: 42071 / 4.7.1-rc37 and RC37 test-AAB filename, unsigned boundary preserved.
- `config/animations.json`: RC37 reload parity policy.
- `scripts/rift_rc37_human_reload_timing_gate.py`: deterministic 45-check focused gate.

Native/Godot files: 34/34 byte-identical to RC36.
