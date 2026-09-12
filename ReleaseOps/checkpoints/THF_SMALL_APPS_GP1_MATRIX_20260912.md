# THF small-app Android/API36 matrix — 2026-09-12

Purpose: exact-source, isolated, non-production Android readiness gate for the seven standalone THF wrappers. WAVE_MAWJA and Godot Terra/Rift sources are excluded from this matrix.

## Gate implementation
- Branch: `a/gp1`
- Workflow: `.github/workflows/thf-small-apps-gp1-api36-gate.yml`
- Initial workflow commit: `28d8e29ed57216ea27aac7f9015318e47536b05e`
- Run: `34681807008`
- WIF -> Drive read-only -> IAP -> isolated builder workspace.
- Android SDK: API 36.
- AGP in source wrappers: 8.13.2.
- Toolchain: Gradle 8.13 + JDK 17; Gradle distribution is fetched from official Gradle distribution service with its official `.sha256` checked before extraction.
- No production signing keys are supplied. Test-only unsigned AAB uses a disposable workspace-only signing-guard bypass; canonical build.gradle and archives remain unchanged.

## Exact source manifest
| App | Application ID | Outer SHA-256 | Embedded source SHA-256 |
|---|---|---|---|
| THF Nexus Suite | `com.thf.topherofit` | `b4786128ffd684ae83e1a99ddd5b798f1d55e196462518434513b5c28e63f721` | `8c060bdb7776ccf485b6294cda513a75b0fd3be28d43a416431d1368260a4884` |
| THF Pulse | `com.thf.topherofit.fitness` | `8f18fc7f889c1fd0e01994350b399434a9779e714664c6974bb7925f36f50913` | `31116912623767ebc2edcd56ad55fb2358a4cf398d2765f5eb1de9d842a75ad2` |
| THF Link | `com.thf.topherofit.link` | `e0d785b57bb5e9368b1055f2ef831a1b8679786fee00c05dfe43458d48510ab5` | `b9a4df060668dde23462c8f279e492e1687ac3f7e37f74571d95d819c281085b` |
| THF Quest | `com.thf.topherofit.learn` | `d4eb28417af5793c903d8962838715fd59a1e7b226dee07b9e94806aab9cd284` | `f1cc6360a8e248794dbeb23e402d77da3d879212c59f0c2f545c86727c7a4394` |
| THF Market | `com.thf.topherofit.market` | `46d2c0055b81cc325267401bcefbb28df8cf9c36e0029827a7cc0d0dde2712a0` | `5050b95e37d766734b37d2763eddf5c76c605bdedcce0da3733ad27412c97b64` |
| THF Learn Games | `com.thf.topherofit.learngames` | `ce8547851c9573db02603ea6f11e020a1b7d346af0cac51e07947304f1a7c1f9` | `dbd259b224924e60902fb0e1b2ebca77bc243e5f29a64d04fd3114438fd41484` |
| THF Fitness Games | `com.thf.topherofit.fitnessgames` | `cf5d73c3a03ab503dbd7c36a2d4db3ec1449ec8281304627b9463e2cb8732a25` | `da3c865a76848c170d679547e05d6edbc0b5ffd6a48002b12ad0d26415fd0273` |

## Current results at checkpoint creation
- Suite: PASS; detailed checkpoint `THF_SUITE_GP1_API36_20260912.md`.
- Pulse: active in the same matrix after exact-source staging was prepared.
- Link, Quest, Market, Learn Games, Fitness Games: exact bytes copied to isolated Drive staging and Reader access granted only to the GCP release-builder service account; matrix jobs queued.

## Static security/compliance findings common to the wrappers
- `allowBackup=false`.
- Release `usesCleartextTraffic=false`; local debug uses cleartext intentionally.
- WebView file access disabled; WebView debugging only in debug builds; SSL errors are cancelled; navigation and web permission handling use a trusted-origin check.
- Manifests declare INTERNET, CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION and ACCESS_COARSE_LOCATION. Before production Play submission, sensitive permissions must be justified per app against actual promoted core functionality and reflected in Data Safety/permissions declarations; remove any permission shown unnecessary by product-level verification.
- targetSdk 36 meets the Google Play target API requirement effective 2026-08-31 for new apps and app updates.

## Safety boundary
- production signing: NOT performed
- Google Play upload/publish: NOT performed
- Cloudflare production cutover: NOT performed
- Solana/token financial action: NOT performed
- canonical source mutation: NONE
- WAVE source/runtime touched: FALSE
