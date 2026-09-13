# THF Games Factory — Stream Reconciliation V2 — 2026-09-13

## Why this addendum exists
A concurrent game stream advanced Spark/Rush after the earlier discovery checkpoint. This file supersedes only the earlier Spark/Rush source-availability statement; all previously proven Terra/Rift/Learn/Fitness evidence remains valid for its exact SHA.

## Spark / Rush authoritative candidate sources now observed
The current builder stream provides independent RC2 source archives:
- Spark source: `$HOME/thf-apps-rc2-exact-candidate-v2/source/spark.zip`
  - SHA-256: `6b74f8d75df8c0b7f74d8c2fee8be7e3517f3803cb42968735bc7a10939bc18c`
- Rush source: `$HOME/thf-apps-rc2-exact-candidate-v2/source/rush.zip`
  - SHA-256: `bb6ff035186b13cdde853145f42e66259c205889de2a7b368da34c9cb0582ba7`

These sources are handled independently from Terra/Rift/Learn/Fitness and from WAVE_MAWJA.

## Spark/Rush local-practice candidate evidence
Run `34769249423` reached the disposable Spark build and produced a valid signed debug APK with targetSdk 36, but the strict package-identity gate correctly rejected it because the debug variant produced `com.topherofit.thf.spark.debug` rather than canonical `com.topherofit.thf.spark`.

The candidate overlay itself established, on the disposable Spark tree:
- local-only practice mode
- real pointer/touch input marker
- local player state
- requestAnimationFrame game loop
- learning-domain loop
- no ranked/social/economy/fitness-evidence writes
- canonical archive unchanged
- device status PENDING
- final status NOT_FINAL

The failure is therefore packaging identity, not permission to weaken the package gate.

Artifact from failed-but-diagnostic run:
- `THF-SPARK-RUSH-LOCAL-PRACTICE-CANDIDATE-V1`
- Artifact ID: `10321671131`
- ZIP SHA-256: `70e4b1328126df82e0eff904d1e09996f10f31171bf6ae3c8a63e44852c2a272`

## Fix applied
Workflow `.github/workflows/thf-spark-rush-local-practice-candidate-v1.yml` now builds the disposable candidate with `assembleRelease` so the QA candidate preserves the canonical applicationId, then zipaligns and signs only with an ephemeral QA keystore that is deleted immediately. The gate still requires targetSdk 36, packaged offline game payload, touch/player/game-loop markers, canonical source SHA unchanged, no online state writes, and device/final PENDING.

No production signing material is used or requested.

## Terra/Rift QA packaging path
A reusable exporter `ReleaseOps/scripts/godot_candidate_tree_apk_v1.sh` and workflow `.github/workflows/thf-terra-rift-staging-apk-v1.yml` were added to build new QA APKs from the already-proven disposable mobile + staging-network overlays. The initial workflow registration failed before creating jobs because of YAML heredoc indentation; this was corrected in commit `56702c16ae07a82afc2be8b5e050993eee5634f1`. Run `34769408210` is the corrected execution path.

The exporter requires:
- Godot 4.7.2 import and headless boot
- installable APK export
- exact expected package
- targetSdk 36
- zip integrity
- APK signature verification, with ephemeral QA-sign fallback only
- zipalign
- packaged Godot payload
- no leaked Godot `.import` files under Android resources
- device status PENDING and final status NOT_FINAL

## Safety posture
- WIF/IAP only for GCP access.
- No persistent cloud keys.
- No production signing.
- No Play publication.
- No Cloudflare production cutover; Terra/Rift endpoint remains reversible staging only.
- No Solana/token financial action.
- No destructive cloud change.
- Canonical archives are never overwritten or mutated.
- WAVE_MAWJA remains isolated and untouched.

## Remaining hard gates
- Terra/Rift: successful rebuilt QA APK exact SHAs, then physical-phone install/launch/touch/orientation/background-resume/offline-network/player/avatar/movement/camera/world-or-combat/FPS-RAM-thermal evidence.
- Spark/Rush: successful canonical-package QA build, then physical-phone evidence; online authority remains separately blocked until a real authorized HTTPS/WSS backend contract exists. Local practice must never masquerade as ranked/social/economy state.
- Learn/Fitness: current P49 RC2 source packages remain blocked as full game experiences because required locomotion/camera/touch systems are absent from the verified source evidence.
