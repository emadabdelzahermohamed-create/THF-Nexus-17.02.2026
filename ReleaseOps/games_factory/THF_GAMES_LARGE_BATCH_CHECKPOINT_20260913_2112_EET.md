# THF Games Large-Batch Checkpoint — 2026-09-13 21:12 EET

## Truth boundary

Scope: THF Terra/Nexus World, Rift/Nexus Arena, Spark learning game-like experience, Rush fitness game-like experience, Learn Games/Fitness Games, and shared game systems. WAVE is excluded and remains technically isolated.

`FINAL_OR_PLAY_READY=FALSE`

No production signing, Google Play publication, Cloudflare production cutover, Solana/token financial action, destructive cloud mutation, canonical archive overwrite, or persistent cloud key use occurred in this batch.

Physical-phone acceptance remains mandatory and must be bound to the exact candidate APK SHA. Source/static/build/package evidence never substitutes for install/launch/touch/orientation/layout/background-resume/offline-network/core-gameplay/crash-free evidence; game candidates additionally require real player/avatar load, movement, camera/gameplay interaction (combat where applicable), and FPS/RAM/thermal observation.

## Authoritative source identities carried forward

Do not rerun already-proven gates for an unchanged source SHA without regression evidence.

- Spark APPS-RC3 canonical source SHA-256: `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0`.
- Rush APPS-RC3 canonical source SHA-256: `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b`.
- Terra/Rift remain on their previously recorded canonical/staging identities; this batch does not rerun their already-proven package gates solely for status.
- Learn Games/Fitness Games remain non-promoted until real locomotion/camera/touch/player/game-loop contracts are satisfied; UI-only/fallback wrappers are not accepted as games.

## Spark/Rush exact-source regression remediation — PASS

Workflow: `.github/workflows/thf-spark-rush-regression-v1.yml`

GitHub Actions run `34773691664` completed `SUCCESS` after the workflow was corrected to use module-qualified Android tasks. Both matrix jobs:

1. authenticated with GitHub OIDC/WIF using the existing release-builder service account and Drive read-only scope;
2. downloaded the exact authoritative source archive from Drive;
3. recomputed and matched the expected canonical SHA-256;
4. passed ZIP integrity and clean extraction;
5. ran `validate_mobile_real_function_source.py` against the shipping source root/package identity;
6. discovered Gradle tasks with provisioned Gradle 8.13 / Java 17;
7. executed at least two real Android regression/lint tasks;
8. built the `app:assembleRelease` target;
9. uploaded independent evidence artifacts.

Evidence artifacts:

- Spark: `THF-spark-REGRESSION-V1`, artifact id `10322956989`, artifact ZIP digest `sha256:e892d9a0cd648eac4744f59d1a6919ae08fa556b6fc5209c6b95ccff5f560470`.
- Rush: `THF-rush-REGRESSION-V1`, artifact id `10322627891`, artifact ZIP digest `sha256:8be740da37e01d671c8a17961b850bc9e72ad1a3ddbe347bd7f6bad79bf6867c`.

This closes the previous CI/tooling blocker caused by unqualified Gradle task assumptions. It does **not** promote either app/game-like experience to FINAL/PLAY_READY.

## Game real-function invariants retained

- Terra/Rift phone candidates must remain sensor-landscape, expandable aspect, touch-safe, and free of desktop window overrides.
- Ranked/social/economy/world mutation remains backend-authoritative; genuinely local training/explore may operate offline but must never fabricate ranked/social/economy state.
- Engine/template APKs without exported game payload are rejected.
- Placeholder endpoints and source/static/build-only PASS are rejected.
- No-pay-to-win remains a release invariant.
- Data Saver, Reduce Motion, High Contrast/accessibility, localization and RTL/safe-area contracts remain mandatory where implemented.

## Highest-priority next executable work

1. Produce/inspect exact APK package metadata and candidate SHA evidence for Spark/Rush RC3 without production signing; bind any future phone evidence to those exact bytes.
2. Reconcile latest Terra/Rift candidate overlays against the source-contract/mobile-real-function gates without re-running unchanged canonical PASS work; rerun only if candidate bytes/config changed.
3. For Learn Games/Fitness Games, prioritize real input/player/camera/game-loop implementation evidence before any packaging promotion.
4. Continue shared avatar/MPFB/MakeHuman/UAL, locomotion/IK, touch HUD, NPC/world, weather/day-night/PBR/audio/VFX/LOD/occlusion, anti-cheat/server-authority and offline-mode audits only where current SHA evidence is incomplete.
5. Physical-device exact-SHA acceptance remains the final non-delegable gate before any FINAL/PLAY_READY label.

Rollback is Git-native; this checkpoint is evidence-only and does not mutate validated source archives or production infrastructure.
