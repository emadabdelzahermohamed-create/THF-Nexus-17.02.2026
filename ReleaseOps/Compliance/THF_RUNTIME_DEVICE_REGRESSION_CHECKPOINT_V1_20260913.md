# THF Runtime / Device Regression Checkpoint V1 — 2026-09-13

## Scope
Re-validation after real-device reports showed that build/install success alone did not guarantee runtime readiness.

THF and WAVE_MAWJA remain technically isolated. No canonical source archive was overwritten or deleted. No production signing, Google Play publishing, Cloudflare production cutover, Solana/token financial action, or destructive cloud action was performed.

## Core RC6 — PASS-STAGING-RUNTIME-CONFIG
Canonical source:
- `THF_Core_RC6_ANDROID_NATIVE_I18N_RELEASE_CUMULATIVE_SOURCE.zip`
- SHA-256: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`

GitHub Actions run: `34743356308` — SUCCESS.
Artifact: `THF-Core-RC6-RUNTIME-CONFIGURED-STAGING` (artifact id `10312629324`).
Artifact ZIP digest: `sha256:ecb52d75fbc99960937f4e00ad2019ba3dbdc723296a76278ff0a7ebdcb916d9`.
APK SHA-256: `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`.
Package: `com.topherofit.thf.core`.
Version: `6.2.2-rc6` / versionCode `62200`.
compileSdk/targetSdk: `36/36`.
Runtime service URL: embedded HTTPS staging endpoint; health gate PASS.
Production signing: false.
Production cutover: false.
Canonical archive mutated: false.
WAVE touched: false.

This closes the previously observed `service_not_configured` packaging defect for the staging candidate. Device-level acceptance is still required before final-release status.

## Terra RC34 — FAIL-APK-VERIFICATION; SAFE RECOVERY ACTIVE
Canonical source:
- `THF_Terra_v4.6.8_RC34_REMOTE_LOD_HYSTERESIS_CUMULATIVE_SOURCE.zip`
- SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`

Diagnostic run `34745986144` verified the canonical SHA and completed Godot 4.7.2 import, headless boot, Android template installation and Android export. The exported APK then failed in the generic APK verification phase; no artifact was accepted. Import logs show the main scene and runtime assets loading correctly, so the previous missing-project-data defect is no longer the first failing phase.

A release-tooling correction was committed at `65dab598cb5dbb2ddf8ef2628c34f95ddee92fcb`:
- split signature / zipalign / badging / package / targetSdk checks into independently reported phases;
- if the isolated Godot HOME emits an unsigned-but-structurally-valid debug APK, recover only with a disposable QA keystore;
- production signing remains false;
- canonical archives remain immutable;
- signature recovery cannot touch WAVE.

Replacement Terra run triggered from that commit: `34748278028` (status to be consumed on the next checkpoint).

## Rift RC37 — FAIL-APK-VERIFICATION; SAFE RECOVERY ACTIVE
Canonical source:
- `THF_Rift_v4.7.1_RC37_HUMAN_RELOAD_TIMING_PARITY_CUMULATIVE_SOURCE.zip`
- SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`

Diagnostic run `34745986135` verified the canonical SHA and completed Godot 4.7.2 import, headless boot, Android template installation and Android export. It failed at the same generic APK verification phase after the export completed; no artifact was accepted. Import/boot evidence shows `arena_main.tscn`, `ArenaMain.gd` and avatar assets loading before packaging verification.

The same safe recovery commit `65dab598cb5dbb2ddf8ef2628c34f95ddee92fcb` applies. Replacement Rift run: `34748278032`.

## Cross-app prevention rule
An Android build is not considered a release candidate solely because compilation, signing or installation succeeds.

Every THF Android lane must be classified and gated as one of:
1. `GODOT_RUNTIME`: canonical SHA, parser/import, headless boot, Android export, embedded Godot payload/assets, package, API 36, signature, zipalign, then device/runtime acceptance.
2. `SERVICE_NATIVE`: canonical SHA, package/API36/signature/zipalign plus non-placeholder HTTPS endpoint embedded in the artifact and service-health proof, then device/runtime acceptance.
3. `OFFLINE_NATIVE`: canonical SHA, package/API36/signature/zipalign and offline boot/content checks, then device/runtime acceptance.

This rule is mandatory for the remaining THF apps/games to prevent repeats of both observed failures: missing Godot project data and missing service configuration.

## WAVE_MAWJA lane
WAVE remains isolated. Current policy remains: resume WAVE only from a verified canonical RC13/RC14 source/workspace and never substitute or silently mutate RC9. No WAVE bytes were copied into THF in this checkpoint.

## Open PR / protected actions
PR #2 remains a draft TokenOps read-only lane. No Solana transaction, signing, burn, transfer or authority mutation was performed.

No production signing, irreversible Play publishing, Cloudflare production cutover or destructive cloud change was performed.

## Next
1. Consume Terra `34748278028` and Rift `34748278032`; accept artifacts only on full payload/package/API36/signature/zipalign PASS.
2. If either fails, use its now-specific phase and evidence rather than rerunning blindly.
3. Apply the reusable runtime-release guard to accepted Core/Terra/Rift artifacts.
4. Extend the same classification/gates across remaining THF Android apps and games.
5. Continue WAVE independently when verified canonical RC13/RC14 source becomes available in an authorized workspace.
