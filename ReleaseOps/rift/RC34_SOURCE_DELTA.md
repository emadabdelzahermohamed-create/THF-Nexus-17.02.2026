# Rift RC34 source delta

Checkpoint: `RIFT-RC34-HUMAN-REVIVE-THREAT-INTERRUPTION`
Baseline artifact: `cd2ae24b9adffe27873acbee42e1380c50665dfbc9d21a6a560fc665ed1b961d`
Artifact SHA-256: `2b565ee09eb00d3c1a5b54c7d07910c68daad11b40fcd8d361b672477a4023f6`

Changed source scope only:
- `app/services/arena.py`: generic server-owned immediate-threat helper, human revive pre-start threat rejection, and active revive cancellation.
- `config/animations.json`: RC34 behavior contract.
- `android-arena/app/build.gradle`: 4.6.8-rc34 / versionCode 42068; API 36 unchanged.
- `scripts/rift_rc34_human_revive_threat_interruption_gate.py`: targeted deterministic gate.

Native/GDScript delta: **none**. Latest Godot 4.7.2 parser/import/headless evidence remains RC32 workflow run `34651723807` PASS.

Validation: targeted 49/49 PASS; clean-extract 49/49 PASS; compile/static checks PASS; deterministic rebuild exact SHA; ZIP integrity PASS.

Next verified gap: project root contains `project.godot` but no `export_presets.cfg`; add a non-secret Android export preset as the next export-readiness gate.
