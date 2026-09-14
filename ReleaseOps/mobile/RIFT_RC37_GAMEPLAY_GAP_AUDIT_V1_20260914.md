# THF Rift RC37 Gameplay Gap Audit V1 — 2026-09-14

## Authority / provenance
- Canonical source archive: `$HOME/thf-rift-rc37-gate/input/THF_Rift_v4.7.1_RC37_HUMAN_RELOAD_TIMING_PARITY_CUMULATIVE_SOURCE.zip`
- Canonical archive SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
- Extracted Godot project: `THF_Nexus_Arena_Core`
- `native/arena/ArenaMain.gd` SHA-256: `884243a61d9bb39b276e77ba14579e290c25cec184d24a948e6cd4f45935bdae`
- Audit Run: `34867855094`, Job: `104056109852`
- Immutable audit artifact: `THF-RIFT-RC37-GAMEPLAY-GAP-AUDIT-V1`, artifact ID `10357792123`, uploaded artifact ZIP SHA-256 `c8bbd9312be54c5fdc913baaceaa661a6da471d59dee12ca56fd5193cabd0130`.
- Canonical archive was SHA-verified before extraction and remained unchanged.

## Newly proven gaps
1. **Phone configuration is not candidate-safe yet.** `project.godot` contains desktop overrides `window_width_override=1280` and `window_height_override=720`, with `window/stretch/mode="canvas_items"`. These must not survive into a Terra/Rift phone candidate. The phone candidate must use sensor-landscape, expandable aspect and no desktop window override.
2. **The current `offline_solo` training path is not genuinely local.** `ArenaMain.gd::_start_training()` creates a payload with `mode="training"`, `connectivity="offline_solo"`, `bot_count=5`, but then calls `await api.request_json("/api/session", HTTPClient.METHOD_POST, payload)`. Therefore training currently depends on backend session creation and cannot be accepted as offline/local gameplay.
3. **Touch targets need a phone pass.** Movement buttons are created at `Vector2(66.0, 54.0)` and combat buttons at `Vector2(88.0, 50.0)`, so their vertical dimensions are below the established >=62 px touch target used by the Terra phone candidate gate.

## Preserved systems / constraints
- Local avatar uses the real MPFB/UAL asset path `res://web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb`.
- Rift includes real locomotion, MPFB rig/IK, camera collision, weapon socket/presentation, touch look, combat HUD, remote actor interpolation and presentation LOD systems.
- Online combat remains server-authoritative: fire presentation is driven after authoritative ammunition consumption; damage/world impacts are derived from authoritative snapshots/events; weapon socket/IK/camera layers explicitly do not own hit, LOS, damage, ammo, ranked outcomes or economy.
- Any new local training implementation must use separate local-only state, must not create/fake an online session, must not mutate ranked/social/economy/world state, and must leave the online request/snapshot path unchanged.

## Current truth
- `FINAL_OR_PLAY_READY=FALSE`
- Physical-device acceptance remains `PENDING`.
- The source-audit step and artifact upload passed. The workflow's final ReleaseOps upload step failed only because the large Markdown report exceeded the shell argument size when passed to `gh api`; this concise GitHub checkpoint replaces that failed reporting step without changing any game gate.
