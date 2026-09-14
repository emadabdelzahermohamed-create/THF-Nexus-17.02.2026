# THF RELEASE / PHONE-QA — Batch 11 checkpoint

Date: 2026-09-15
Status: NOT_FINAL / NO_GO

## Authority reviewed
- Shared Integration authority: V5; CI run 34909604361 = SUCCESS.
- Apps Phone Fundamentals authority: V3 exact-source candidates for Forge/Echo/Codex/Vault/Signal/Command. Exact V3 ZIP bytes were independently located in Library and SHA-256 matched current ReleaseOps authority.
- Games authority: Terra RC34 Phone V4; Rift 4.7.5-rc41 only; Spark APPS RC4 + real-game overlay; Rush APPS RC4 + Native Verified-Motion V2.
- Pulse authority: Motion Coach QA2 source tree SHA-256 6a180cf6599f8827e824431caf4566f520cc3796d9366c30abc197b4aeb6ba34.

## Apps V3 source-byte verification
Forge / THF Market:
- package: com.topherofit.thf.forge
- source ZIP SHA-256: 75c3744af31f16273a174bdac53b9e812613e4d9ef8c2fa260521c7f7c40cbf8
- version: 2.1.1-phone3 / 21102
- compileSdk/targetSdk: 36/36
- ordinary launcher: yes

Echo / THF Community:
- package: com.topherofit.thf.echo
- source ZIP SHA-256: 3c90b53009d34e9c391bc8f977daf70195a041ba6c0098eca82709932b8734e9
- compileSdk/targetSdk: 36/36
- ordinary launcher: yes

Codex / THF Learn:
- package: com.topherofit.thf.codex
- source ZIP SHA-256: 44ff76cca12b6b13febc53e9e0b8748a01949eb07c40b020d76b82f45a094950
- version: 2.1.1-phone3 / 21102
- compileSdk/targetSdk: 36/36
- ordinary launcher: yes

Vault / THF Wallet:
- package: com.topherofit.thf.vault
- source ZIP SHA-256: e33c7c7f1f6d7f913dfe6ca5d674aff2883f7a230c2a323724088c30c4497585
- version: 1.2.0-apps-rc4 / 12002
- compileSdk/targetSdk: 36/36
- ordinary launcher: yes

Signal / THF Publisher:
- package: com.topherofit.thf.signal
- source ZIP SHA-256: 3b6ba96076decd62e31a90c60d91a101806d6a6e9be329a58baa55ece82227ef
- compileSdk/targetSdk: 36/36
- ordinary launcher: NO
- internal/signature boundary retained

Command / THF Admin:
- package: com.topherofit.thf.command
- source ZIP SHA-256: 314a89f33f62d754edc9cc369fcc35b019d6081c6be0dcfbffa0fe5801ce0ffc
- version: 1.2.0-apps-rc4 / 12002
- compileSdk/targetSdk: 36/36
- ordinary launcher: NO
- internal/signature boundary retained

Static inspection also found adaptive/monochrome launcher resources and 20 localized values sets in all six V3 sources. No APK authority is assigned to old binaries for these V3 sources.

## Games
- Terra: source eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68; current QA APK e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec.
- Rift: ONLY 4.7.5-rc41, source/archive 29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d; exact eligible APK still NONE. RC37 and older remain superseded.
- Spark: source 58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43; current QA APK 9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea.
- Rush: source 766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c; current QA APK f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f.

## Pulse repairs performed in this batch
1. Commit 694ec6795638fdf9e3779e938eed4158afcc141c restored valid GitHub Actions YAML after an unindented heredoc had caused no-job parse failures.
2. Run 34910616004 then reached WIF -> gcloud -> IAP -> GCP builder, and correctly failed closed before build because the builder source directory contained a different raw tree hash.
3. Read-only source forensics run 34908505961 proved the directory was polluted by generated Android/Gradle outputs, including android/.gradle, android/app/build intermediates, and an unsigned release APK.
4. Commit 62f5dcd14eda9ff16bb395426b20f3dd99d23dfc now clears previous Pulse output before source validation, preventing stale prior APK/evidence from being retrieved after a pre-build failure.
5. Commit d0ef0b88cec851feb5c8668ea04e8908b52e317b computes the authoritative source hash on an isolated staging copy after removing generated Android/Gradle outputs plus Python caches. The canonical source directory itself is not mutated. The workflow remains fail-closed if the clean tree still does not equal 6a180cf6599f8827e824431caf4566f520cc3796d9366c30abc197b4aeb6ba34.
6. Pulse run 34911159245 is the exact affected rerun for this repair and is not considered PASS until completion.

## Current blockers / next executable gates
- The six Apps V3 sources have exact bytes and API36 metadata verified, but exact APK builds remain pending because the currently connected automation runtime has no Android SDK/Gradle toolchain and the authorized desktop builder is disconnected. No old APK is substituted.
- Rift needs exact RC41 source bytes staged into an eligible Godot/API36 build path; no RC37 fallback.
- Pulse must finish the repaired exact-source gate and then package validation.
- Exact-candidate physical-phone evidence remains mandatory for every app/game: install, launch, touch, layout/orientation, background/resume, offline/network, core journey, crash-free; games additionally avatar/player load, movement/camera/gameplay and FPS/RAM/thermal observation.
- Production OAuth console binding, production signing, Play Console actions and legal acceptance remain non-delegable and were not fabricated.

## Release truth
PHYSICAL_DEVICE_PASS=FALSE
PRODUCTION_SIGNING_PASS=FALSE
PLAY_READY=FALSE
FINAL_OR_PLAY_READY=FALSE
WAVE_TOUCHED=FALSE

Checkpoint body SHA-256 (before commit): 84dfe8d482606fdd1c71abb49d8a156959b4d22cca6b94d64ab16478b61b614a
