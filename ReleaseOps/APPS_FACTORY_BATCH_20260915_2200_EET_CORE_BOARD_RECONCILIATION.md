# THF Apps Factory — Core board reconciliation

Date: 2026-09-15 22:00 EET

## Authority read

Apps Factory re-read `ReleaseOps/APK_FIRST_ORCHESTRATION.md` and `ReleaseOps/APK_FIRST_TARGETS.json` before acting.

The policy assigns candidate promotion and board ownership to THF Release Factory. Apps Factory therefore does **not** edit `APK_FIRST_TARGETS.json` to promote Core.

## Reconciliation result

The board currently reports THF Core (`com.topherofit.thf.core`) as `NEEDS_CANONICALIZATION`, but the repository already contains the authoritative Apps Factory checkpoint:

- manifest: `ReleaseOps/APPS_FACTORY_CORE_RC6_CANDIDATE_READY.json`
- checkpoint commit: `f5ee3974899eb23018c92478a8c8f98058570443`
- candidate status: `CANDIDATE_READY`
- source archive: `THF_Core_RC6_ANDROID_NATIVE_I18N_RELEASE_CUMULATIVE_SOURCE.zip`
- exact source SHA-256: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`
- package id: `com.topherofit.thf.core`
- versionName/versionCode: `6.2.2-rc6` / `62200`
- compileSdk/targetSdk: `36` / `36`
- source modified by canonicalization: **no**
- new version created by canonicalization: **no**

Recorded coherence evidence in that manifest includes 38/38 Core tests PASS, compile/static/localization/API36/integrity gates PASS, exact-source Android build/package inspection PASS, debug APK SHA-256 `87d119badc52504bd2471eec53fcc0142ca2e2cbac3171ab825b871c4087199f`, and unsigned AAB SHA-256 `e71625911d2c06eb0d084f6ed094fcd142f093fcfbb2bf2b13b59a4221760e6e`.

## Lane ownership / no-regression decision

- Forge, Echo, Codex, Vault, Signal and Command are already `APK_CANDIDATE` on the Release Factory board. Apps Factory leaves those frozen candidates untouched.
- No existing `PHONE_TEST_TARGET` exists for Apps Factory products on the board; therefore no pinned phone target was abandoned.
- Signal and Command remain internal-only and are not exposed as ordinary-user launcher products.
- THF Pass remains a backend/SDK integration component, not a standalone APK.
- Pulse, all games and WAVE remain excluded from this lane.

## Required Release Factory action

Release Factory should reconcile Core from board state `NEEDS_CANONICALIZATION` against the already-published `CANDIDATE_READY` manifest and perform its normal stale-candidate/build/package arbitration. Apps Factory does not self-promote Core to `APK_CANDIDATE` or `PHONE_TEST_TARGET`.

## Remaining gates

Production signing, external OAuth/provider/durable identity-session runtime, and physical-phone acceptance remain unproven. Nothing in this checkpoint claims `PHONE_TEST_TARGET`, `PHONE_PASS`, `PLAY_CANDIDATE`, `FINAL`, or `PLAY_READY`.
