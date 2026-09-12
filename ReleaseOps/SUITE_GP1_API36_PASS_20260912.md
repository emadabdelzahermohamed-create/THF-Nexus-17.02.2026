# THF Nexus Suite GP1 — Android/API 36 Gate PASS

Date: 2026-09-12
Scope: THF Nexus Suite only. WAVE_MAWJA untouched.

## Canonical source verification
- Outer source SHA-256: `b4786128ffd684ae83e1a99ddd5b798f1d55e196462518434513b5c28e63f721` — PASS
- Inner source SHA-256: `8c060bdb7776ccf485b6294cda513a75b0fd3be28d43a416431d1368260a4884` — PASS
- Application ID: `com.thf.topherofit`
- Target SDK: `36`

## Build verification
- Gradle: `8.13`
- Gradle distribution SHA-256: `20f1b1176237254a6fc204d8434196fa11a4cfb387567519c61556e8710aed78`
- Debug APK SHA-256: `905ffefd1ca1f00f62e089134844a3cf89490136fc4d4c0989752083a89fb858`
- Test unsigned AAB SHA-256: `6675b433374775005378673cdde2753db0101b8efd528527e67c1e368cbc4464`
- Final gate: `THF_NEXUS_SUITE_GP1_PASS`

## Evidence
- GitHub Actions run: `34682838077`
- Evidence artifact ID: `10294746743`
- Evidence artifact archive SHA-256: `ae5d1302cf2ca52e1a4209de87be3675bd11efe909dd6be239334122cbf58a6c`

## Safety / release boundary
- Production signing credentials used: NO
- Google Play upload performed: NO
- Canonical source modified: NO
- WAVE touched: NO
- Persistent cloud key used: NO; WIF/IAP path used.

## Non-blocking technical debt observed
- Android toolchain emitted an SDK XML version compatibility warning.
- MainActivity uses/overrides a deprecated Android API.
- Gradle reported deprecated features that will require cleanup before Gradle 9 migration.
These did not fail the current API 36 release gate but should be handled in the compatibility-hardening backlog.

## Next
Continue to the highest-priority unblocked THF service/application release-readiness gate. Keep WAVE_MAWJA isolated; its full runtime/source remains a separate prerequisite unless a newer canonical WAVE package appears.
