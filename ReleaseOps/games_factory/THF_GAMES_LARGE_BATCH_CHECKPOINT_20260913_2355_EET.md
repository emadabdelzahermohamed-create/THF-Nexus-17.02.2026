# THF Games Large-Batch Checkpoint — 2026-09-13 23:55 EET

## Safety / execution boundary
THF game engineering only. Canonical source archives were treated as immutable and exact SHA checks were retained. GitHub OIDC/WIF + IAP was used for GCP access; no persistent cloud key was introduced. WAVE_MAWJA files were not read into, copied into, or modified by these game workflows. No production signing, Google Play publishing, Cloudflare production cutover, Solana/token transaction, or destructive cloud mutation occurred.

Nothing here is FINAL or PLAY_READY. Physical-phone exact-SHA acceptance remains mandatory.

## Learn Games / Fitness Games — real-game candidate build gate now PASS
The previous run failed after source-contract PASS because Android release lint correctly rejected CAMERA permission without an explicit optional camera hardware declaration. This was a candidate-manifest/tooling problem, not a reason to suppress lint.

Commit `7a464bf86442af61b92a5b6785a0c95d83acf050` moved the fix into the primary reusable API36 candidate overlay: when CAMERA permission exists, the disposable manifest now declares `android.hardware.camera` with `required=false`, while retaining predictive-back API36 migration. Canonical archives remain unchanged.

Authoritative workflow `THF Learn Fitness Real Game Overlay V1`, run `34781606154`, completed SUCCESS for both jobs after the fix. Each job passed exact-source fetch via WIF/IAP, clean extraction, real-function overlay/audit, reversible staging HTTPS configuration, throwaway QA signing, Android regression/lint, assembleRelease, APK ZIP integrity, package/API36 inspection, and artifact upload.

### Learn Games candidate
- authoritative outer source SHA-256: `ce8547851c9573db02603ea6f11e020a1b7d346af0cac51e07947304f1a7c1f9`
- candidate tree-manifest SHA-256: `332eb7f36e032ef386b0406ee067ae2426a848e0c79828c2dce2849ae4c728d4`
- APK SHA-256: `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- package: `com.thf.topherofit.learngames`
- targetSdk: `36`
- game-like real-function source contract: PASS, no required failures
- DEX/package spot-check: `ThfGameApplication`, `Choreographer`, Learn Games and Mastery runtime markers present in the exact APK; ZIP integrity PASS
- aapt: camera hardware is optional rather than install-filtering
- QA signer is ephemeral/non-production; device status PENDING; final status NOT_FINAL
- artifact: `THF-learn-REAL-GAME-OVERLAY-V1`, ID `10325358218`, digest `sha256:b49e2be2b8643644e177e6ff84e29dc3311742c11cd20b10554bfea89e2357da`

### Fitness Games candidate
- authoritative outer source SHA-256: `cf5d73c3a03ab503dbd7c36a2d4db3ec1449ec8281304627b9463e2cb8732a25`
- candidate tree-manifest SHA-256: `59fb99299b4d38033a937284a140b8258227a79703efeac1b9da5b6a58c10611`
- APK SHA-256: `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`
- package: `com.thf.topherofit.fitnessgames`
- targetSdk: `36`
- game-like real-function source contract: PASS, no required failures
- DEX/package spot-check: `ThfGameApplication`, `Choreographer`, `SensorManager`, Fitness Games and Motion Reps runtime markers present in the exact APK; ZIP integrity PASS
- aapt: camera hardware is optional rather than install-filtering
- QA signer is ephemeral/non-production; device status PENDING; final status NOT_FINAL
- artifact: `THF-fitness-REAL-GAME-OVERLAY-V1`, ID `10325492741`, digest `sha256:c5f1097610dd5383199d298f97333841c6ed89aa9b2fa8dee9da91cbe193f424`

The artifact summaries contain an empty convenience `QA_CERT_SHA256` field because of an evidence-parser mismatch, but the exact `apksigner` evidence itself verifies one V2 QA signer for each APK. This is recorded as a non-fatal evidence-format defect; no production signer is involved.

## Tooling regression protection
Commit `d4af60ae029622f59b56f6b749eaee1e4379e88e` added candidate-manifest regression coverage for optional camera hardware and predictive-back. Commit `5bc12f512f68bc560d04c858d377776e4652e15d` added isolated workflow `THF Games Tooling Regression V1`. Run `34781741819` completed SUCCESS for syntax and fail-closed unit tests.

## Terra / Rift — stronger runtime binding proof without duplicate rebuild
Dynamic-player forensics run `34781122549` had already shown that Terra/Rift build their player/avatar runtime in executable scripts rather than a declarative CharacterBody3D scene. Artifact ID `10325256505`, digest `sha256:acb6109cb9db95417f39fbf6f4901897baa9aa5dd5d42db78c67d159118f97af`.

Commit `738317d7dbf0cc44165e02935fd4358a50ee8f90` added an exact-canonical-source runtime-binding lane using the stronger fail-closed audit and WIF/IAP read-only source fetch. Run `34781689558` completed SUCCESS for both Terra and Rift.

### Terra RC34 runtime binding
- canonical source SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`
- runtime-binding source contract: PASS
- dynamic player/runtime file: `native/world/WorldMain.gd`
- required player, locomotion, camera, avatar, animation, touch and world-interaction runtime bindings: PASS
- optional IK, server-authority and explicit local/offline markers: present
- artifact ID `10324932364`, digest `sha256:2201e1e4232ae55adf7f26b93e802c629dd7a834b5fbbb0b31f0f7dce6d4f96f`
- DEVICE_STATUS=PENDING; FINAL_STATUS=NOT_FINAL

### Rift RC37 runtime binding
- canonical source SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
- runtime-binding source contract: PASS
- dynamic player/runtime file: `THF_Nexus_Arena_Core/native/arena/ArenaMain.gd`
- required player, locomotion, camera, avatar, animation, touch and combat runtime bindings: PASS
- optional IK, server-authority and explicit local/offline markers: present
- artifact ID `10324599384`, digest `sha256:b6d2ff2824fc12ecc2bca4692456af6af31a230604377bb632ea95432d36cab5`
- DEVICE_STATUS=PENDING; FINAL_STATUS=NOT_FINAL

## Spark / Rush — exact existing APK payload reinspection, no duplicate build
The already-proven changed-byte candidates were downloaded from their existing artifacts and re-hashed; no Gradle build was repeated.

- Spark exact APK SHA-256 remains `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`; package `com.topherofit.thf.spark`, targetSdk 36, ZIP/DEX present, runtime DEX contains application/frame-loop/game markers. Existing artifact ID `10323696925`.
- Rush exact APK SHA-256 remains `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`; package `com.topherofit.thf.rush`, targetSdk 36, ZIP/DEX present, runtime DEX contains application/frame-loop/SensorManager/motion/reps markers. Existing artifact ID `10323397773`.

Both remain exact-SHA DEVICE_PENDING and NOT_FINAL.

## Terra / Rift mobile candidate truth correction and staging recovery
Independent exact-APK inspection found that the older runtime-fixed APKs (`388f3c09...b18c7` Terra and `fe35328b...024b1` Rift) still declare `android.hardware.screen.portrait` in aapt badging. They are therefore REJECTED as physical-phone candidates under the sensor-landscape contract even though their package/payload/API36 gates had passed.

The later disposable staging overlay artifact from run `34769408210` was then inspected instead. The build portion of that historical run had succeeded; only its brittle final exact-count shell gate failed because layered evidence duplicated valid truth markers.

Exact staged APK evidence recovered from artifact `THF-TERRA-RIFT-STAGING-QA-APKS-V1`, ID `10321397268`, digest `sha256:287f3348489c48b816211c4c48ff37fc8f8455e47f65f5509bee79b6d8aa952e`:
- Terra staged APK SHA-256 `409aa1efc12e10cd3acf962451b00348e8891c906164aacde9a988d208530963`
- Rift staged APK SHA-256 `ba094e2232d229cb93eda78c5e7da2c08e26a01a3015ccce4994bc8050c86480`
- both package/API36/payload PASS; QA signing only; canonical archives unchanged
- mobile overlay changed `window/handheld/orientation` to Godot `SCREEN_SENSOR_LANDSCAPE=4`, `window/stretch/aspect` to `expand`, and neutralized width/height desktop overrides
- exact staged APK aapt badging no longer declares `android.hardware.screen.portrait`
- network endpoint overlay replaced explicit localhost/placeholder URL markers; remaining explicit placeholder URL marker count = 0; endpoint values remain redacted; production cutover=false
- DEVICE_STATUS=PENDING; FINAL_STATUS=NOT_FINAL

Commit `44cce79367e9705dd5a6e2bb854a82f4c495d909` repaired the staging workflow to use the existing duplicate-safe fail-closed key/value gate and added strict candidate checks for mobile overlay keys, neutralized desktop overrides, absence of APK portrait hardware requirement, and zero remaining placeholder endpoint markers. New run `34782130639` was queued from this tooling correction at checkpoint creation; its result must be reconciled before replacing the staged APK SHAs above if the rebuilt bytes differ.

## Remaining non-delegable / physical gates
1. Terra/Rift: exact-candidate physical Android install/cold-launch, sensor-landscape rotation behavior, expandable/safe HUD, touch input, avatar/player load, locomotion, camera, Terra world interaction / Rift combat, background-resume, offline/network transition, crash-free smoke, FPS/RAM/thermal. The old portrait APKs are not eligible.
2. Spark: exact SHA `9fffc4d9...165ea` physical phone gameplay/touch/layout/background-resume/offline-network/crash/performance evidence.
3. Rush: exact SHA `3e9aabae...d0e3a` physical phone evidence plus real sensor-driven repetition behavior.
4. Learn/Fitness: physical phone evidence for the exact new candidate SHAs above, including lifecycle, touch/layout, offline/network transition and crash/performance; Fitness must prove sensor/motion gameplay on hardware where used.
5. Shared avatar/animation: source/runtime binding is stronger now, but physical rendering/animation/IK/root-motion/retarget quality and thermal/performance remain device/GPU evidence gates.
