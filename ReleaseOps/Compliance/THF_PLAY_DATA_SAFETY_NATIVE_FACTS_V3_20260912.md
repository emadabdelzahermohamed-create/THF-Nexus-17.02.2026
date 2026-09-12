# THF Play Data Safety Native Facts V3 — PASS

Date: 2026-09-12
Scope: THF only. WAVE_MAWJA excluded and untouched.
Execution path: GitHub Actions -> GCP WIF -> IAP -> thf-wave-builder.
Run: 34697279008
Job: 103562820313
Workflow commit: 5c65a3197e7405773e9bb9eae5548629d03fab78

## Result

- Gate: PASS
- Native metadata files discovered: 3
- THF/WAVE scope isolation: PASS
- Mutation performed: FALSE
- Production signing performed: FALSE
- Google Play upload performed: FALSE
- Cloudflare production cutover performed: FALSE
- Solana financial action performed: FALSE

## Exact native metadata evidence

### Android app Gradle
Path: `thf-runtime-s1/outer/01_THF_NEXUS_SUITE/ANDROID_PLAY_SOURCE/app/build.gradle`
SHA-256: `7e88c51c54a49e5e31faf3a3532effe85742eec5c36aa2c14db904b9b6a1cc3a`

Observed build facts:
- namespace: `com.thf.topherofit`
- applicationId: `com.thf.topherofit`
- compileSdk: 36
- targetSdk: 36
- minSdk: 26

### Android manifest
Path: `thf-runtime-s1/outer/01_THF_NEXUS_SUITE/ANDROID_PLAY_SOURCE/app/src/main/AndroidManifest.xml`
SHA-256: `83341f4f62ad3784db34ec689bd912ddd3894a15de98266f55744d3fea1b9a0c`

Declared permissions:
- `android.permission.ACCESS_COARSE_LOCATION`
- `android.permission.ACCESS_FINE_LOCATION`
- `android.permission.CAMERA`
- `android.permission.INTERNET`
- `android.permission.RECORD_AUDIO`

Observed manifest flags:
- `android:allowBackup="false"`
- `android:usesCleartextTraffic="${cleartextTraffic}"`

### Root Gradle
Path: `thf-runtime-s1/outer/01_THF_NEXUS_SUITE/ANDROID_PLAY_SOURCE/build.gradle`
SHA-256: `96a33edb21d173da2c36f5312f50cdfb9f71d9f5078c081c81f2d029547f6cb9`

## Compliance interpretation

This gate records technical declarations only. A manifest permission does not by itself prove that data is collected, shared, retained, or transmitted. Google Play Data Safety answers must be derived from runtime/code-path evidence plus backend handling and policy contracts.

The next reversible gate is to map each declared sensitive permission to actual native/WebView/runtime request paths and purposes, then reconcile those facts with the existing runtime Data Safety inventory. Privacy/Terms/account-deletion/security.txt remain separate release-readiness blockers until standalone policy resources and a public account-deletion path are implemented and verified.

## Safety boundary

No canonical source archive was overwritten or deleted. No WAVE file was inspected through the THF native scope. No persistent cloud key was used.