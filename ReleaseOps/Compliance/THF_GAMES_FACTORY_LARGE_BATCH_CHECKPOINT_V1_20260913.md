# THF Games Factory — Large Batch Checkpoint V1 — 2026-09-13

## Scope
THF game/game-like streams only: Terra/Nexus World, Rift/Nexus Arena, Learn Games, Fitness Games, Spark/Rush discovery posture, and shared avatar/animation/game systems. WAVE_MAWJA is explicitly out of scope and untouched.

## Authoritative canonical inputs
- Terra RC34: `THF_Terra_v4.6.8_RC34_REMOTE_LOD_HYSTERESIS_CUMULATIVE_SOURCE.zip`
  - SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`
- Rift RC37: `THF_Rift_v4.7.1_RC37_HUMAN_RELOAD_TIMING_PARITY_CUMULATIVE_SOURCE.zip`
  - SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
- Learn Games P49 RC2: `THF_LEARN_GAMES_P49_RC2_SOURCE.zip`
  - SHA-256: `dbd259b224924e60902fb0e1b2ebca77bc243e5f29a64d04fd3114438fd41484`
- Fitness Games P49 RC2: `THF_FITNESS_GAMES_P49_RC2_SOURCE.zip`
  - SHA-256: `da3c865a76848c170d679547e05d6edbc0b5ffd6a48002b12ad0d26415fd0273`

All four archives were SHA-verified before clean extraction and re-verified unchanged after the audits.

## Terra/Rift reversible staging authority gate
GitHub Actions run: `34769077363` — SUCCESS.

Evidence:
- local THF runtime health: PASS
- reversible public HTTPS staging health: PASS
- unauthenticated arena mutation guard: PASS
- Terra source real-function contract after candidate-only mobile/network overlays: PASS
- Rift source real-function contract after candidate-only mobile/network overlays: PASS
- Godot 4.7.2 Terra import: PASS
- Godot 4.7.2 Terra headless boot: PASS
- Godot 4.7.2 Rift import: PASS
- Godot 4.7.2 Rift headless boot: PASS
- candidate staging endpoint embedded: true; endpoint value redacted
- endpoint class: Cloudflare Quick Tunnel staging only
- production cutover: false
- production signing: false
- canonical archives mutated: false
- WAVE files read or changed: false
- device status: PENDING
- final status: NOT_FINAL

Artifact: `THF-TERRA-RIFT-STAGING-NETWORK-AUTHORITY-V1`
- Artifact ID: `10321426704`
- Artifact ZIP SHA-256: `3ec94b442f0edbfe9839ef8831ab3a75b73578d17f673b4bdf9a9fb91aeaecbf`

The candidate-only mobile overlay enforces Godot sensor-landscape (`orientation=4`), expandable aspect, and removes desktop width/height overrides from the disposable project tree. The network overlay replaces placeholder/local endpoints only in the disposable staging candidate and preserves the canonical archives.

## Shared game-systems audit
New read-only audit: `ReleaseOps/scripts/thf_game_shared_systems_audit_v1.py`.
Regression suite: `ReleaseOps/tests/test_thf_game_shared_systems_audit_v1.py`.
CI run: `34769206703` — SUCCESS, including 3/3 regression tests and WIF/IAP execution.

Artifact: `THF-GAME-SHARED-SYSTEMS-AUDIT-V1`
- Artifact ID: `10320174889`
- Artifact ZIP SHA-256: `ab67152e5180daa6f5913a6d0c5c4897525a7e9ec78807c83d07c202faa48e18`

The audit inventories implementation signals for avatar/MakeHuman/MPFB/humanoid skeletons, AnimationTree/AnimationPlayer/UAL/retargeting, IK, locomotion, camera, touch, combat, NPC AI, world/weather/day-night, PBR/lighting, audio/VFX, LOD/occlusion, performance, anti-cheat, server authority, offline/local modes, economy/ranked markers, and accessibility/data-saver/reduce-motion/high-contrast/RTL/safe-area markers. It is evidence only and never upgrades device/final status.

### Terra RC34
- text/source files scanned: 272
- required shared-system signal set: PASS
- required missing: none
- canonical archive unchanged: true
- device status: PENDING
- final status: NOT_FINAL

### Rift RC37
- text/source files scanned: 279
- required shared-system signal set: PASS
- required missing: none
- canonical archive unchanged: true
- device status: PENDING
- final status: NOT_FINAL

### Learn Games P49 RC2
- text/source files scanned: 3
- shared-system status: BLOCKED
- required missing: `locomotion,camera,touch`
- canonical archive unchanged: true
- device status: PENDING
- final status: NOT_FINAL

This confirms the current RC2 archive is not sufficient evidence of a real mobile game. UI/static/build evidence must not be promoted to game readiness.

### Fitness Games P49 RC2
- text/source files scanned: 2
- shared-system status: BLOCKED
- required missing: `locomotion,camera,touch`
- canonical archive unchanged: true
- device status: PENDING
- final status: NOT_FINAL

This confirms the current RC2 archive is not sufficient evidence of a real mobile game. UI/static/build evidence must not be promoted to game readiness.

## Spark / Rush
No authoritative independent Spark or Rush source ZIP was proven in the latest verified discovery state. Do not substitute Learn/Fitness, Terra/Rift, a wrapper, demo shell, or unrelated archive. Continue authoritative source discovery independently.

## Mobile Real-Function gate posture
Terra/Rift static/source gates are improved but this does NOT make either game FINAL or PLAY_READY. Candidate-only overlay bytes differ from the earlier canonical-source APK candidates, so the next phone candidate must be rebuilt and receive a new exact APK SHA before physical-device evidence is collected.

Required remaining phone evidence for that exact rebuilt SHA includes install, cold launch, touch HUD, sensor-landscape/orientation, expandable phone-safe layout, background/resume, offline/network transition, real avatar/player load, locomotion, camera, real world/combat interaction as applicable, crash-free smoke, and FPS/RAM/thermal observation.

Learn/Fitness must first obtain/implement real locomotion, camera and touch-driven gameplay in a real source candidate before Android/device readiness can be considered. Spark/Rush remain source-discovery blocked.

## Safety and isolation
- GCP access: WIF + IAP; no persistent cloud key.
- Canonical source archives: never overwritten/deleted/mutated.
- WAVE_MAWJA: untouched and not scanned as a substitute for THF game sources.
- Production signing: not performed.
- Google Play irreversible publication: not performed.
- Cloudflare production cutover: not performed.
- Solana/token financial action: not performed.
- Destructive cloud change: not performed.
- Open TokenOps PR remains unrelated to this game batch.

## Next highest-priority unblocked work
1. Build new disposable Terra/Rift Android candidates from the proven mobile + staging-authority overlays; run Godot 4.7.2 import/headless/export, API 36 package/payload/security gates and assign new exact APK SHAs.
2. Preserve staging-only authority and no-pay-to-win/server-authoritative online state; do not promote quick-tunnel staging to production.
3. Recover or expand Learn/Fitness real-game source implementation instead of polishing UI-only shells.
4. Continue independent authoritative Spark/Rush source discovery.
5. Physical-phone acceptance remains the final non-delegable engineering gate before any FINAL/PLAY_READY label.
