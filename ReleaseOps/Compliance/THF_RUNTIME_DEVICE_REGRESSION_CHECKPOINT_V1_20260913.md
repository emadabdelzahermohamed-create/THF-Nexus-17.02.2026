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

## Terra RC34 — FAIL-RUNTIME-PACKAGING (diagnostic retry active)
Previous runtime-fixed run `34743325701` failed inside the Godot runtime export phase after canonical SHA verification passed. No artifact was accepted.
Canonical SHA-256 remains `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`.

The shared Godot packaging script was hardened to emit exact failing phase plus tails of import/boot/template/export logs. Commit: `74c3b0e5af23adccfddb74312c7853da92f267d5`.
A new Terra run is triggered automatically by the shared-script path dependency. Final status pending.

## Rift RC37 — FAIL-RUNTIME-PACKAGING (diagnostic retry active)
Previous runtime-fixed run `34743337175` failed inside the Godot runtime export phase after canonical SHA verification passed. No artifact was accepted.
Canonical SHA-256 remains `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`.

The same diagnostic hardening applies. New Rift run `34745986135` was queued from commit `74c3b0e5af23adccfddb74312c7853da92f267d5`.

## Permanent release rule
An Android build is not considered a release candidate solely because compilation, signing or installation succeeds.

Godot applications must additionally prove packaged project payload and successful engine boot path. Service-native applications must prove a non-placeholder HTTPS runtime endpoint and service-health gate. Device/runtime acceptance remains mandatory before final-release status.

## Next
1. Consume the new Terra/Rift diagnostic runs and fix the exact Godot import/export blocker in disposable build copies only.
2. Rebuild Terra/Rift and require payload/package/API36/signature/zipalign PASS.
3. Run the reusable Android runtime release guard against Core/Terra/Rift outputs.
4. Continue equivalent runtime-config/payload regression checks across remaining THF Android apps and games.
5. WAVE_MAWJA remains isolated; resume its independent lane only from a verified canonical RC13/RC14 source/workspace, never by substituting RC9.
