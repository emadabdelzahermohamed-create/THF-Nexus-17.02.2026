# THF Terra RC34 Installable QA APK — V1

Status: **PASS-QA / NOT PRODUCTION-SIGNED**
Date: 2026-09-13

## Provenance

- Workflow: `THF Terra RC34 Installable QA APK`
- GitHub Actions run: `34735556336`
- Workflow head commit: `438aa08fd8f511a3a98574f78c3604b6f49a9ae2`
- Transport/authentication: GitHub OIDC/WIF -> GCP -> IAP -> `thf-wave-builder`
- Persistent cloud keys: **not used**

## Verified build result

- Artifact: `THF-Terra-RC34-INSTALLABLE-QA`
- GitHub artifact id: `10309714856`
- Artifact ZIP SHA-256: `052f1c48855066cb4bf80dff22453a398fe6feb89ff318f02474ebfff0e1329b`
- APK: `THF-Terra-RC34-INSTALLABLE-QA.apk`
- APK SHA-256: `b45a1b461cf24bbe4eb7d8499ed15ab440df3ef1232c5c83e70759d89fa0ca31`
- APK size: `127228252` bytes
- Package: `com.topherofit.thf.terra`
- Version code: `42068`
- Version name: `4.6.8-rc34`
- compileSdk: `36`
- targetSdk: `36`
- minSdk: `24`
- Install location: `auto`

The SHA-256 recorded inside the workflow artifact was independently recomputed from the downloaded APK and matched exactly.

## Gate checks

- Gradle clean + `assembleStandardDebug`: PASS
- Canonical package assertion: PASS
- Version code/name assertions: PASS
- zipalign verification: PASS
- APK signature verification: PASS
- Artifact retrieval through WIF/IAP path: PASS
- Artifact upload: PASS

The APK uses a QA/debug keystore created only for installability testing. This is **not** production signing and must never be treated as the Play production artifact.

## Isolation and safety

- THF Terra-only QA build path.
- WAVE_MAWJA files were not used or copied into THF.
- No production signing.
- No Google Play upload/publishing.
- No Cloudflare production cutover.
- No Solana/token transaction or signing.
- No canonical source archive deletion or overwrite.

## Next step

Continue the equivalent installable/API-36 QA readiness gate for the next highest-priority THF native app whose canonical source/version is already verified, while retaining canonical archive hashes and the same WIF/IAP-only cloud authentication policy.
