# RuinsCiv Android QA signing recovery V2 — 2026-09-22

## Scope and identity
- Project: RuinsCiv only.
- QA package: `com.topherofit.ruins.civ.phoneqa`.
- Canonical production identity remains `com.topherofit.ruins.civ`.
- THF Terra is historical/superseded and is rejected from the Android template and payload.

## Evidence from failed gate
- GitHub Actions run: `35683425839`.
- Source head: `9ad10a68b8c19ac6a60f5d461ea25cc8db2088ad`.
- Godot import: completed on `4.7.2.stable`.
- Main-scene headless boot: completed.
- Android export: completed.
- APK ZIP integrity: passed.
- Failure: initial `apksigner verify` reported an unsigned APK (`Missing META-INF/MANIFEST.MF`).
- The gate correctly stopped before accepting package/API36/arm64/payload evidence.

## Safe release-only fix
The workflow now treats the initial signature check as a probe. If Godot emits an unsigned QA APK, it:
1. zipaligns the disposable QA APK;
2. creates a 30-day ephemeral key whose certificate DN is `CN=RuinsCiv QA,O=THF,C=EG`;
3. signs the QA-only `.phoneqa` package with v1/v2/v3 schemes;
4. deletes the keystore and unsigned intermediate immediately;
5. re-runs `apksigner`, zipalign, package, targetSdk 36, arm64, forbidden-identity, and real-payload gates.

No production/upload key is read or created. This recovery cannot promote the artifact beyond QA. Physical-device status stays `PENDING`, and `FINAL` / `PLAY_READY` remain false.

## Next acceptance boundary
Accept the build only if the rerun produces a terminal-success workflow plus an artifact containing the final APK, SHA-256, signer certificate evidence, package/API36/arm64 badging, payload hits, import log, and scene-boot log. Device install/launch/touch/FPS/RAM/thermal remain separate required evidence.
