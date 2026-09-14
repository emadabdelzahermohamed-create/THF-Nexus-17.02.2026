# THF Release/Phone-QA batch checkpoint — 2026-09-14 late EET

## Scope and isolation
THF-only release/phone-QA tooling and candidate authority review. WAVE_MAWJA was not modified. No production/store/financial action was performed.

## Authority retained
- Core exact APK authority remains `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`, package `com.topherofit.thf.core`, targetSdk 36, physical device PENDING.
- Terra remains RC34 source SHA `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`, exact QA APK SHA `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`, package `com.topherofit.thf.terra`, targetSdk 36, physical device PENDING.
- Rift RC37 is superseded. Latest authority is RC41 / 4.7.5-rc41 source SHA `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`. Exact RC41 bytes remain missing from the builder, so no older Rift candidate is promoted.
- Spark exact QA APK remains `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`; Rush `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`; Learn Games `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`; Fitness Games `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`. All remain physical-device PENDING / NOT_FINAL.
- Existing durable Vault authority remains package `com.topherofit.thf.vault`, targetSdk 36, canonical source SHA `052e2c55c6066c15eee63528218b8eab9711bec9de71335c67c7e1692a5b5432`, APK SHA `7431987b0be9589f997d505cfe69c6d3e217deb7d2783c44f99e6f263693209e`.
- Existing durable Signal authority remains package `com.topherofit.thf.signal`, targetSdk 36, canonical source SHA `f78890c3bf036d80a568ec39baac4a665d6092b9bbc8c4f080f2651785c1a275`, APK SHA `c7eb1044426423862687f93a875208a5ea8c5703d4978efb93eb4b54a1555d75`.
- No newer authoritative candidate/source SHA for Core, Forge, Echo, Codex or Command was proven in the reviewed ReleaseOps state, so no source-only/template-only output replaces prior validated evidence.

## Pulse repair
Exact Pulse source tree SHA `6a180cf6599f8827e824431caf4566f520cc3796d9366c30abc197b4aeb6ba34` reached Gradle on the WIF/IAP GCP builder. The build failure was a Java/Kotlin Health Connect 1.1.0 interop mismatch: `HealthPermission.getReadPermission` requires `KClass`, while generated Java passed `Class`.
- `a314988cd6a91e55b4998ec33b86a4d3a891a791`: added a fail-closed Java `Class` -> Kotlin `KClass` build-overlay repair for all nine Health Connect record permissions.
- `2006d5ddc7fdee0208ab0e92e00f71967bd28c47`: wired the repair into the isolated Pulse QA2 WIF/GCP build.
- Run `34892108356` was launched for the exact source and remained in progress at checkpoint time. No APK PASS is claimed until the run completes its fail-closed package/evidence gate.

## Vault / Signal phone-baseline tooling repairs
The canonical native build itself had succeeded through Gradle but was rejected by a stale postbuild assumption that the source vector pathname `res/drawable/ic_thf_launcher.xml` must survive unchanged inside the APK. aapt2 had correctly compiled the icon to a generated path such as `res/MD.xml`.
- `4c01134cb34bd78d6921f7455f065ef4d3a2bbcd`: validate the canonical source icon before compilation and verify the actual aapt-reported compiled icon path exists in the APK.
- `2dff3da3af3c4218d13ac71600721ef87a8fe403`: wired this repair into the canonical workflow.
- The first rerun correctly exposed a second tooling-only issue: the canonical generator expected the obsolete icon-check text literally and failed with `icon validation anchor drift`.
- `3d07e6caddd58118005689677a94ef92d1595886`: made the canonical generator accept the new aapt-aware icon gate and emit explicit `APK_ICON_FAIL` diagnostics.
- `5e44db5b4e80b719ef4a680a0a52ed5550ad40ea`: wired the generator repair into the WIF/GCP workflow. Run `34892459224` was queued at checkpoint time.
- No production signing is performed. Signal/Publisher remains internal-only and requires server-verified publisher/admin authority; Command/Admin remains admin-only. UI hiding is not treated as authorization.

## Shared integration truth
The THF Pass receiver retains cryptographic verifier boundaries, package-bound handoff/session state, replay protection and server-authoritative private-app role claims. Private Signal/Command require online verified roles. Stable trusted HTTPS/WSS deployment of the verifier remains NOT_PROVEN.

## Release truth
`PHYSICAL_DEVICE_PASS=FALSE`
`FINAL_OR_PLAY_READY=FALSE`
`PRODUCTION_SIGNING=FALSE`
`PLAY_PUBLISH=FALSE`
`PRODUCTION_CUTOVER=FALSE`

Exact-candidate physical phone evidence remains mandatory for install, launch, touch, layout/orientation, background/resume, offline/network transitions, core journey and crash-free smoke. Games additionally require avatar/player load, movement/camera/gameplay and FPS/RAM/thermal observation; Rift requires combat; Rush/Fitness require sensor-motion evidence.

Checkpoint body SHA-256: `e72d8588a59cd03b8bd278c1b1eca19c57ae14396ec8e916dfeac21707f9601b`
