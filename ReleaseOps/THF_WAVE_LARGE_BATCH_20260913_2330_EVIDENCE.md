# THF + WAVE Large-Batch Release/Platform/QA Checkpoint — 2026-09-13 23:30 EEST

## Scope and release truth
This checkpoint records only evidence established in this pass. It does not claim physical-device/GPU QA, production signing, signed AAB, Play approval, or production deployment.

## Authoritative Learn/Fitness inputs
- Learn Games canonical source: `~/thf-small-learn-games/source.zip`
  - SHA-256: `ce8547851c9573db02603ea6f11e020a1b7d346af0cac51e07947304f1a7c1f9`
  - package identity: `com.thf.topherofit.learngames`
- Fitness Games canonical source: `~/thf-small-fitness-games/source.zip`
  - SHA-256: `cf5d73c3a03ab503dbd7c36a2d4db3ec1449ec8281304627b9463e2cb8732a25`
  - package identity: `com.thf.topherofit.fitnessgames`
- Both canonical ZIPs remained unchanged. Candidate fixes were applied only to extracted disposable trees.

## Safe reversible repairs completed
1. Commit `f5252e380bc92e61187f9897a6aecad2c83ea46c` corrected the CI signing contract to the exact environment names required by the canonical Gradle sources (`THF_KEYSTORE_PATH`, `THF_KEYSTORE_PASSWORD`, `THF_KEY_ALIAS`, `THF_KEY_PASSWORD`) using a short-lived QA JKS that is removed after build.
2. Commit `ab369a443a27d276eff9fa24ee65b67c2153aeaf` added an API-36 candidate gate and repaired predictive-back behavior in the disposable candidate using `OnBackInvokedDispatcher`, while retaining a legacy fallback.
3. Commit `1c1c5c16afca75bd98a7735c11e2ddb273882f6b` fixed Play/ChromeOS compatibility by declaring camera hardware optional (`android.hardware.camera`, `required=false`) in the disposable candidate manifest.

## Successful evidence run
- Workflow: `THF Learn Fitness Android36 Backfix V2`
- Run: `34781356793`
- Head commit: `1c1c5c16afca75bd98a7735c11e2ddb273882f6b`
- Learn matrix job: PASS
- Fitness matrix job: PASS
- WIF/OIDC -> GCP -> IAP source retrieval: PASS
- Exact source SHA verification and ZIP integrity: PASS
- Reversible staging HTTPS `/health`: PASS
- Real-function source contract: PASS for both
- Gradle 8.13 / JDK 17 / API 36 lint: PASS
- Release unit-test task: PASS or no source
- `assembleRelease`: PASS
- APK ZIP integrity: PASS
- package identity: PASS
- targetSdk: 36
- APK Signature Scheme v2 verification under ephemeral QA certificate: PASS
- Production signing: NO
- Production cutover: NO

## Exact QA candidates
### THF Learn Games
- APK: `learn-android36-backfix-v2-release.apk`
- package: `com.thf.topherofit.learngames`
- targetSdk: 36
- version: `P49-RC2` / versionCode `4902`
- APK SHA-256: `04134c48df8f8b771a09ace6db4843bc66f46f2e13e6fbba993b092b80fe38ba`
- candidate-tree manifest SHA-256: `ba8cc23c149722d2279080f30c20da8b318e0457c9b05295021fe3bbd7f3b1e2`
- artifact ZIP digest: `sha256:ca90036ebb9324bf34cf1111eb657f7042a34da1d41ae748bb513288a6131aa4`
- compiled payload inspection: `classes.dex` present; touch and draw handlers and learning score/level markers are present.
- physical-device status: PENDING
- FINAL: NO
- PLAY_READY: NO

### THF Fitness Games
- APK: `fitness-android36-backfix-v2-release.apk`
- package: `com.thf.topherofit.fitnessgames`
- targetSdk: 36
- version: `P49-RC2` / versionCode `4902`
- APK SHA-256: `41b52e0273d062f98595f476bdcbc46802007663ba2729ada37f49c52aeacdef`
- candidate-tree manifest SHA-256: `ca39caee06ea6dd3f134b859de7c4ed4bbc191928f386c6e2f50959182efc4c8`
- artifact ZIP digest: `sha256:3c61a69bf4598321912ccc572534f78bb1462f5c148e231fad8476ce1038ca74`
- compiled payload inspection: `classes.dex` present; touch and draw handlers plus `Motion Reps`, repetition, player, and local motion-validation markers are present.
- physical-device status: PENDING
- FINAL: NO
- PLAY_READY: NO

## Mobile Real-Function Release Policy
Learn/Fitness now clear the static/build/package portion of the policy for the exact APK hashes above, but remain hard-blocked from FINAL until the exact hashes receive physical-device evidence covering install, launch, touch, responsive layout/orientation, background/resume, offline/network transitions, core journey, and crash-free smoke. Because they are games, evidence must additionally cover player/avatar load, movement/camera/gameplay interaction, and FPS/RAM/thermal observation. No device evidence was fabricated in this pass.

## Endpoint / production status
The successful candidates are bound to a healthy reversible Cloudflare Quick Tunnel staging endpoint. That is not a stable production hostname and is explicitly recorded as `PRODUCTION_CUTOVER=NO`. Stable production HTTPS/WSS evidence therefore remains required.

## WAVE RC14
No material WAVE RC14 resolution was established in this pass. The known blocker remains canonical-source access: WIF/GCP/IAP are operational, but the CI OS Login identity cannot read the canonical `/root/workspace/wave-mawja` tree. Do not weaken OS Login/SSH or grant broad Owner access. Preferred remediation remains a builder-owned release workspace tied cryptographically to the canonical checkout, or narrowly approved OS Login admin access.

## Other non-delegable final gates
Production signing key use, signed AAB generation with the production key, Play Internal upload/approval, legal/store acceptance, and exact-candidate physical-device testing remain non-delegable or intentionally not executed here. Independent release work may continue without falsely promoting these gates.

Checkpoint body SHA-256 (content above, excluding this line): `a05fa13a480c4fcddafb5c5b03f9aefdba328bb67fc131ea6c9d673fdf120f42`
