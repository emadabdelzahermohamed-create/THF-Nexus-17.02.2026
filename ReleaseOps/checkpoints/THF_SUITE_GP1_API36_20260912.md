# THF Nexus Suite GP1 API36 checkpoint — 2026-09-12

Scope: THF Nexus Suite Android wrapper only. WAVE and other THF canonical sources untouched.

## Canonical provenance
- Outer package: `01_THF_NEXUS_SUITE_FINAL_GOOGLE_PLAY_SOURCE.zip`
- Outer SHA-256: `b4786128ffd684ae83e1a99ddd5b798f1d55e196462518434513b5c28e63f721`
- Embedded canonical source: `THF_NEXUS_6_FINAL_SOURCE_20260829.zip`
- Embedded source SHA-256: `8c060bdb7776ccf485b6294cda513a75b0fd3be28d43a416431d1368260a4884`
- Application ID: `com.thf.topherofit`
- targetSdk: `36`

## Gate history
- Initial isolated run `34681553655` verified Drive SHA + WIF/IAP staging + package manifest, then failed only because a global `gradle` command was not installed on the builder. This was classified as tooling, not source failure.
- Tooling was corrected in the shared isolated small-app gate by using Gradle 8.13, the minimum/default version required by AGP 8.13.x, with JDK 17 and the existing Android SDK 36 toolchain.

## Final result — PASS
- Matrix run: `34681807008`
- Suite matrix job: SUCCESS
- Drive exact-source download: PASS
- WIF authentication: PASS
- IAP exact-source staging: PASS
- ZIP traversal/integrity guard: PASS
- Outer and embedded source SHA verification: PASS
- `PLAY_RELEASE_STATUS.json` contract: PASS
- compileSdk/targetSdk/applicationId contract: PASS
- Gradle: 8.13; JVM: 17.0.20
- Debug APK build: PASS
  - SHA-256: `905ffefd1ca1f00f62e089134844a3cf89490136fc4d4c0989752083a89fb858`
  - size: 12,347 bytes
  - ZIP integrity: PASS
- Test-only unsigned AAB build: PASS
  - SHA-256: `6675b433374775005378673cdde2753db0101b8efd528527e67c1e368cbc4464`
  - size: 8,769 bytes
  - ZIP integrity: PASS
  - `jarsigner` confirms `jar is unsigned`
- Evidence artifact id: `10293593957`
- Evidence artifact SHA-256: `8e3eeb107553d689e3386aeb319ba5eb0781a5af9eb81eff1be27bc386582c32`

## Security/compliance observations
- Release cleartext traffic is disabled by manifest placeholder policy; debug-only local cleartext remains intentionally enabled.
- `allowBackup=false`; WebView debug is restricted to `BuildConfig.DEBUG`; SSL errors are cancelled; file access is disabled; external navigation is restricted to the trusted host path logic.
- Manifest requests INTERNET, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION, and ACCESS_COARSE_LOCATION. Before Play production submission, each sensitive permission must be mapped to an actual promoted core feature and reflected accurately in Play permissions/Data Safety declarations; permissions should be reduced if a specific app does not require them.
- Current Google Play submission policy (effective 2026-08-31) requires new apps/updates to target Android 16 / API 36 or higher; this wrapper meets targetSdk 36.

## Safety boundary
- production_signing_credentials_used: false
- play_upload_performed: false
- canonical_source_modified: false
- wave_touched: false
- No Cloudflare production cutover.
- No Solana/token financial action.
- No canonical archive overwrite/delete.

## Disposition
`THF-SUITE-GP1-API36-TEST` is CLOSED / PASS for source integrity + test Android build readiness. Production endpoint, production signing, Play declarations/listing/testing and physical-device QA remain final-release gates and were not performed.
