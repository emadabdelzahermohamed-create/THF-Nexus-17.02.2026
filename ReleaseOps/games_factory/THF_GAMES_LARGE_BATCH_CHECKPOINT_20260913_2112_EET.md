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

GitHub Actions run `34773691664` completed `SUCCESS` after the workflow was corrected to use module-qualified Android tasks. Both matrix jobs authenticated with GitHub OIDC/WIF + Drive read-only, downloaded and re-hashed the exact authoritative source, passed ZIP integrity/clean extraction, passed `validate_mobile_real_function_source.py`, executed at least two real Android regression/lint tasks with Gradle 8.13 / Java 17, built `app:assembleRelease`, and emitted evidence artifacts.

Baseline evidence artifacts:

- Spark: `THF-spark-REGRESSION-V1`, artifact id `10322956989`, artifact ZIP digest `sha256:e892d9a0cd648eac4744f59d1a6919ae08fa556b6fc5209c6b95ccff5f560470`.
- Rush: `THF-rush-REGRESSION-V1`, artifact id `10322627891`, artifact ZIP digest `sha256:8be740da37e01d671c8a17961b850bc9e72ad1a3ddbe347bd7f6bad79bf6867c`.

This closes the previous CI/tooling blocker caused by unqualified Gradle task assumptions.

## Spark/Rush APK-bound package evidence — PASS

The same exact-source workflow was strengthened at commit `93b662bebdda07fa3f738600d5caba2bf001692f` so `assembleRelease=PASS` is no longer accepted alone. It now also runs APK ZIP integrity, calculates/stores the generated APK SHA-256, extracts APK badging with Android build-tools `aapt`, fail-closes unless the APK package exactly equals the canonical package, fail-closes unless `targetSdkVersion=36`, and explicitly records `READINESS_PROMOTION=NO` / `PHYSICAL_DEVICE_REQUIRED=YES`.

Run `34773862098` completed `SUCCESS` for both Spark and Rush matrix jobs. Updated artifacts:

- Spark: artifact id `10322822555`, ZIP digest `sha256:1448ec8a2f3da689e9aad1ecfd4c0aff529bd9b0ca4615c3e1a0269d69bc302d`.
- Rush: artifact id `10322593340`, ZIP digest `sha256:1d9ff8d9891c2f6b4bee76d28f129142d3c642b439a7872535d0cceb5ad93bc1`.

The exact APK SHA values are carried inside those evidence artifacts; this checkpoint deliberately does not invent or infer them from artifact ZIP digests. Device evidence must use the APK SHA recorded by the build itself.

## New fail-closed game-like real-function source gate — PASS regression

Added `ReleaseOps/validators/audit_game_like_real_function.py` plus four regression tests and workflow `.github/workflows/thf-game-like-real-function-validator-v1.yml`.

The auditor rejects UI-only shells unless current shipping source demonstrates interactive input, state/progression, a timed/frame loop or real render/motion wiring, and the appropriate learning/fitness domain signals. It always preserves the runtime/device truth boundary. CI run `34773912828` completed `SUCCESS`: Python syntax PASS and all four positive/negative regression tests PASS.

## Exact Spark/Rush RC3 game-like contract — FAIL, precise blockers captured

Workflow `.github/workflows/thf-spark-rush-game-like-contract-v1.yml` reuses only exact-source download/SHA/integrity plus the new source auditor; it intentionally does **not** repeat Gradle/build/package work already proven for the same SHA.

Initial run `34774018878` failed closed for both exact sources. Evidence naming was then made self-describing at commit `fbf60bb43860f3c41c928d62e151c70efab8fe32` so missing required signals are visible without exposing source bytes or secrets. Run `34774066695` emitted:

- Spark RC3: `FAIL` — missing `timed_or_frame_loop_OR_render_or_motion` only. Artifact id `10322867697`, digest `sha256:d580f041f982b1abd772e6aa185b10b64899f653670ce194a65edb57e6e10755`.
- Rush RC3: `FAIL` — missing `timed_or_frame_loop_OR_render_or_motion` **and** `fitness_domain`. Artifact id `10322977488`, digest `sha256:903cd22510d58a80c5ff3dac5dc0fd3df3b695059878e556e2629523df8e7d3a`.

Because the auditor lists only missing requirements, the exact sources did demonstrate the other required high-confidence source signals such as interactive input and state/progression; however, those source signals are not runtime proof. Spark therefore currently behaves more like an interactive learning app without proven game loop/render-motion wiring. Rush additionally lacks high-confidence shipping-source fitness-domain wiring under the current RC3 source contract. Neither may be marketed or promoted as a complete game-like experience on current evidence.

## Game real-function invariants retained

- Terra/Rift phone candidates must remain sensor-landscape, expandable aspect, touch-safe, and free of desktop window overrides.
- Ranked/social/economy/world mutation remains backend-authoritative; genuinely local training/explore may operate offline but must never fabricate ranked/social/economy state.
- Engine/template APKs without exported game payload are rejected.
- Placeholder endpoints and source/static/build-only PASS are rejected.
- No-pay-to-win remains a release invariant.
- Data Saver, Reduce Motion, High Contrast/accessibility, localization and RTL/safe-area contracts remain mandatory where implemented.

## Highest-priority next executable work

1. Spark RC3: add/recover real timed/frame loop or render/motion gameplay wiring in a reversible candidate overlay, then rerun only the source contract affected by changed bytes before build/package/device gates.
2. Rush RC3: add/recover real fitness-domain behavior plus timed/frame loop or render/motion wiring in a reversible candidate overlay; do not fake fitness state with static labels.
3. Reconcile latest Terra/Rift candidate overlays against source-contract/mobile-real-function gates without rerunning unchanged canonical PASS work; rerun only when candidate bytes/config changed.
4. Learn Games/Fitness Games remain engineering-first: real input/player/camera/game-loop evidence before packaging promotion.
5. Continue shared avatar/MPFB/MakeHuman/UAL, locomotion/IK, touch HUD, NPC/world, weather/day-night/PBR/audio/VFX/LOD/occlusion, anti-cheat/server-authority and offline-mode audits only where current SHA evidence is incomplete.
6. Physical-device exact-SHA acceptance remains the final non-delegable gate before any FINAL/PLAY_READY label.

Rollback is Git-native; all changes in this batch are CI/validator/evidence changes and do not mutate validated source archives or production infrastructure.
