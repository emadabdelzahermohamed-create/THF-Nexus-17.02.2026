# THF Android Runtime Regression Guard V1 — 2026-09-13

Status: ACTIVE / PREVENT-RECURRENCE

## User-observed failures now treated as release blockers

1. Godot-based Android build can install but abort at runtime with missing project data / `.pck` payload.
2. Native THF Core can install and launch but show `service not configured` because no usable HTTPS service endpoint was embedded.
3. Godot `.import` sidecar files under Android `res/` can break resource merging even when the canonical source archive itself is valid.

## Corrective actions

- Rift RC37 is routed through a Godot-native export path that packages the project payload into the APK instead of treating the Android wrapper alone as a releasable application.
- Core RC6 is routed through a runtime-configured staging build that verifies an HTTPS `/health` endpoint before build and verifies the endpoint was embedded in the resulting APK.
- Added `ReleaseOps/scripts/android_runtime_release_guard_v1.sh` as a reusable build-time guard for THF Android apps/games.
- The guard requires: ZIP integrity, APK signature verification, zipalign, exact package, targetSdk 36, no Godot `.import` resource sidecars, optional Godot project payload, and optional HTTPS runtime endpoint literal.

## Policy

An Android artifact is no longer release-ready solely because Gradle/Godot export succeeds or because `apksigner` passes. Before any artifact is presented as a Final Release Candidate, the applicable runtime guard must pass. Godot applications additionally require project payload verification; network-dependent native applications additionally require runtime endpoint verification.

## Safety / isolation

- Canonical source archives remain immutable and SHA-256 checked before/after disposable extraction.
- Fixes occur in disposable work directories or release automation only.
- WAVE_MAWJA files are not copied into THF workspaces and THF files are not copied into WAVE workspaces.
- No production signing, Google Play publishing, Cloudflare production cutover, Solana financial action, or destructive cloud mutation is authorized by this checkpoint.

## Current next gates

- Rift RC37 runtime-fixed Godot APK build and payload gate.
- Core RC6 runtime-configured staging APK and `/health` gate.
- Apply the reusable runtime guard to remaining Android THF apps/games as each canonical source is promoted into its release build workflow.
