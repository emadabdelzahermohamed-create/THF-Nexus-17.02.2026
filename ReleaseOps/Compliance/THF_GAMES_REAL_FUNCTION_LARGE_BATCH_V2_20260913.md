# THF Games Real-Function Large Batch V2 — 2026-09-13

## Scope
Read-only/source-contract audit plus CI/forensics hardening for THF Terra/Nexus World, THF Rift/Nexus Arena, THF Learn Games, THF Fitness Games, and source discovery for THF Spark/Rush. WAVE_MAWJA was excluded from all source scans and no WAVE files were read or changed.

This checkpoint does **not** grant FINAL/PLAY_READY. Device acceptance remains PENDING for every game candidate.

## Authoritative source inputs verified
- Terra RC34 — `THF_Terra_v4.6.8_RC34_REMOTE_LOD_HYSTERESIS_CUMULATIVE_SOURCE.zip`
  - SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`
  - Clean-extract file count in audit: 784
- Rift RC37 — `THF_Rift_v4.7.1_RC37_HUMAN_RELOAD_TIMING_PARITY_CUMULATIVE_SOURCE.zip`
  - SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
  - Clean-extract file count in audit: 771
- Learn Games P49 RC2 — `THF_LEARN_GAMES_P49_RC2_SOURCE.zip`
  - SHA-256: `dbd259b224924e60902fb0e1b2ebca77bc243e5f29a64d04fd3114438fd41484`
  - Clean-extract file count in audit: 7
- Fitness Games P49 RC2 — `THF_FITNESS_GAMES_P49_RC2_SOURCE.zip`
  - SHA-256: `da3c865a76848c170d679547e05d6edbc0b5ffd6a48002b12ad0d26415fd0273`
  - Clean-extract file count in audit: 6

All four source SHAs were verified before extraction and rechecked after audit. Canonical archives were not mutated.

## Engineering delivered
- Added `ReleaseOps/scripts/thf_game_real_function_audit_v2.py`.
- Added `ReleaseOps/tests/test_thf_game_real_function_audit_v2.py`.
- Added and repaired `.github/workflows/thf-games-real-function-large-batch-v2.yml` for GitHub Actions -> WIF -> IAP -> GCP builder read-only auditing.
- Repaired `.github/workflows/thf-terra-rift-mobile-config-forensics-v1.yml` and made it emit redacted mobile-config/placeholder evidence.
- Fixed a false-positive where `preload` could satisfy Rift `reload`/combat detection.
- Corrected Godot sensor-landscape contract to `SCREEN_SENSOR_LANDSCAPE = 4` and aligned audit parsing with serialized `project.godot` key form.
- Regression suite now passes 4/4 tests and explicitly verifies UI-only rejection, placeholder rejection, Rift combat requirement, and static-source PASS never promoting device state beyond PENDING.

Relevant commits in this batch:
- `e136807a3917b26c74ae42a682dd4519b4b5655a` — real-function audit V2 initial
- `bf71dc14a0141d83e9f542d7fd080caca14a502b` — V2 tests initial
- `d06f7b7a21b2f551358c08b71e917d0950eec1ba` — large-batch workflow initial
- `b1779691e346bffe0ec0b402ae4d2b14216346d2` — YAML-safe/observable large-batch workflow
- `347d0e49b1df68fb82661c19a067b88b7a280f56` — combat false-positive fix
- `39f383fa9bae0fffc6068ebe3560bf710413c51b` — mobile-config forensics workflow repair
- `8c02d4151a19859fbde3aba081ac34285180eb56` — sensor-landscape test correction
- `2d42d9ca95401e072fb9e26228d78982abc7bf71` — Godot mobile config syntax/enum audit correction

## Latest successful large-batch evidence
GitHub Actions run: `34765317113`

Artifact: `THF-GAMES-REAL-FUNCTION-LARGE-BATCH-V2`
- Artifact ID: `10320441233`
- Artifact ZIP SHA-256: `6829550f679a270696309764af7a0d1f06d3ddefdfdabdee8d4cdaa17b201c85`
- Workflow result: SUCCESS
- Regression tests: PASS (4/4)
- WIF auth: PASS
- IAP/GCP source audit: PASS
- Safety assertions: PASS

### Terra RC34
`source_contract_status=FAIL`, `device_status=PENDING`

Required failures:
- `no_placeholder_endpoint`
- `sensor_landscape`
- `expandable_aspect`
- `no_desktop_window_override`

21 audit checks passed. Real player/game/world markers are present; this is not evidence of a UI-only shell. Previous package/payload/API36 success for the same canonical SHA was not redundantly rerun in this batch.

### Rift RC37
`source_contract_status=FAIL`, `device_status=PENDING`

Required failures:
- `no_placeholder_endpoint`
- `sensor_landscape`
- `expandable_aspect`
- `no_desktop_window_override`

21 audit checks passed, including combat markers after the regex false-positive fix. Previous package/payload/API36 success for the same canonical SHA was not redundantly rerun.

### Learn Games P49 RC2
`source_contract_status=FAIL`, `device_status=PENDING`

Required failures:
- `no_ui_only_shell`
- `real_input_wiring`
- `player_or_avatar_load`
- `no_placeholder_endpoint`

This source must not be represented as a real mobile game until real input/player/gameplay behavior is implemented and re-audited.

### Fitness Games P49 RC2
`source_contract_status=FAIL`, `device_status=PENDING`

Required failures:
- `no_ui_only_shell`
- `real_input_wiring`
- `player_or_avatar_load`
- `no_placeholder_endpoint`

This source must not be represented as a real mobile game until real input/player/gameplay behavior is implemented and re-audited.

### Spark / Rush
Read-only builder discovery found `candidate_count=0` for standalone ZIPs named for Spark/Rush while excluding WAVE paths. This is a source-discovery blocker; no alternate THF or WAVE package may be substituted.

## Terra/Rift mobile-config forensics
GitHub Actions run: `34765228769`

Artifact: `THF-TERRA-RIFT-MOBILE-CONFIG-FORENSICS`
- Artifact ID: `10319954650`
- Artifact ZIP SHA-256: `e32010f771cd00ca8f3ab37388e2ff4c0b4e4304b51509902644173a9b81ceb8`
- Workflow result: SUCCESS

Canonical SHA verification passed before and after inspection. Endpoint values were never printed; only token locations were emitted.

Runtime-relevant localhost markers include:
- Terra: `project.godot:27`, `native/world/WorldMain.gd:172`, plus protocol/runtime contract material.
- Rift: `THF_Nexus_Arena_Core/project.godot:27`, `native/arena/ArenaMain.gd:178`, plus protocol/runtime contract material.

Therefore the placeholder/localhost blocker is present in runtime-relevant source, not only documentation.

## Safety / isolation
- `canonical_archives_mutated=false`
- `wave_files_read_or_changed=false`
- No production signing.
- No Google Play publishing.
- No Cloudflare production cutover.
- No Solana/token transaction or financial action.
- No destructive GCP change.
- No persistent cloud keys; WIF/IAP path used.
- No FINAL/PLAY_READY label applied.

## Next engineering gates
1. Extract the exact Terra/Rift `project.godot` `window/*` keys on disposable clean copies and generate cumulative candidate overlays that set sensor-landscape (`orientation=4`), `stretch/aspect="expand"`, and remove non-zero desktop window overrides without modifying canonical archives.
2. Do not replace localhost with a fabricated endpoint. Resolve only to an authorized reachable HTTPS/WSS game backend and prove health/auth plus server authority for ranked/social/economy/world mutation.
3. After overlay bytes change, rerun Godot 4.7.2 parser/import/headless, native Android export, API36/package/payload/security gates and record new candidate SHA(s).
4. Implement real mobile game-loop/input/player/avatar behavior for Learn/Fitness Games rather than wrappers or UI-only demos, then rerun the V2 audit.
5. Locate authoritative Spark/Rush source archives and verify their versions/SHAs before any engineering work.
6. Preserve no-pay-to-win and keep online state server-authoritative; local practice/explore/training must remain genuinely local.
7. Physical-phone exact-SHA acceptance remains mandatory: install, cold launch, touch HUD, orientation/layout, background/resume, offline/network transition, player/avatar load, movement/camera/gameplay/combat as applicable, crash-free smoke, FPS/RAM/thermal observations.
