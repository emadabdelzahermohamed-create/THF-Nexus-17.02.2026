# THF Device Runtime Failure Prevention — 2026-09-13

Status: ENFORCED FOR RELEASE CANDIDATES
Scope: THF Android/native/Godot applications and games. WAVE_MAWJA remains technically isolated and must use an equivalent WAVE-specific gate when its canonical source is available.

## User-device failures that triggered this policy

1. Godot Android build installed but aborted at startup with missing project data / missing `.pck` semantics.
   - Root cause: the installable APK path compiled the generated Android Gradle tree directly instead of exporting the Godot project through Godot, so the project payload was not packaged.
   - Correct classification: `FAIL-RUNTIME`, regardless of APK signature or successful Gradle build.

2. THF Core installed but displayed `الخدمة غير معدة` / secure service address not included.
   - Root cause: release APK was assembled with empty runtime service properties.
   - Correct classification: `FAIL-RUNTIME-CONFIG`.

3. Direct Android build paths for Godot projects can also ingest Godot editor sidecars such as `*.import` under Android resources and fail AAPT/resource compilation.
   - Correct prevention: Godot projects must use the engine export path. Direct generated-Gradle-tree packaging is not a release artifact path.

## Mandatory release gates

### Godot applications and games

A candidate MUST NOT be called Final/Release Candidate unless all are true:

- Canonical source SHA-256 verified before and after build.
- Parser/import succeeds using the pinned Godot version.
- Headless project boot succeeds before export.
- Android SDK target is API 36.
- Android export is executed by Godot (`--export-debug` for installable QA or release export at the authorized signing stage), not by invoking the generated Gradle project as the primary packaging path.
- Export preset/package/version are verified.
- APK/AAB integrity and signature state are verified.
- APK contains a non-empty Godot project payload (`assets/` and/or `.pck` as appropriate for the export format).
- Missing-project-data / missing-PCK evidence is a hard failure.
- `zipalign` and `apksigner verify` pass where applicable.

The shared implementation is `ReleaseOps/scripts/godot_runtime_fixed_apk_v1.sh`.

### Service-dependent native Android applications

A candidate MUST NOT be called Final/Release Candidate unless all are true:

- Service endpoint is non-empty.
- Endpoint scheme is HTTPS.
- `localhost`, loopback, example/placeholder, and unset endpoints are rejected for device release candidates.
- The selected endpoint `/health` succeeds before packaging.
- The compiled artifact is inspected to verify the endpoint/configuration was actually embedded.
- Package name and targetSdk 36 are verified.
- APK integrity/signature/alignment pass.
- A screen that reports missing service configuration is a hard `FAIL-RUNTIME-CONFIG`.

The current staging implementation is `ReleaseOps/scripts/core_runtime_configured_staging_v1.sh`. A Cloudflare Quick Tunnel is staging-only; production release remains blocked on a stable production hostname and explicit production cutover authorization.

## Device-runtime acceptance rule

Build success is not equivalent to release readiness. Before a THF Android artifact is promoted to Final Release Candidate, it must pass an on-device runtime acceptance check covering at minimum:

- package installs;
- app launches without engine/bootstrap error;
- Godot project/assets load for Godot apps;
- main screen becomes reachable;
- required backend/service configuration is present;
- no known fatal startup dialog;
- package/version/SDK match the release manifest.

Until physical-device or equivalent Android instrumentation evidence exists, the artifact status is at most `BUILD-PASS / DEVICE-RUNTIME-PENDING`.

## Recurrence prevention across remaining THF apps/games

Every future Android release workflow must select one of these explicit classes:

- `GODOT_RUNTIME`: use Godot engine export + project-payload assertion.
- `SERVICE_NATIVE`: require verified HTTPS runtime configuration + embedded-config assertion.
- `OFFLINE_NATIVE`: prove no required network endpoint at startup and run launch smoke.

A workflow that has no runtime class declaration must fail release-readiness review.

## Isolation and safety

- Never mutate canonical source archives.
- Work only on disposable extractions/candidates.
- Never copy WAVE_MAWJA bytes into THF or THF bytes into WAVE_MAWJA.
- Production signing, Play publishing, Cloudflare production cutover, Solana/token financial actions, and destructive cloud changes remain separate authorization gates.
