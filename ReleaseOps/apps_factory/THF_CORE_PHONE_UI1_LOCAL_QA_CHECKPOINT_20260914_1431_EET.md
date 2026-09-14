# THF Core Phone UI1 Local QA Checkpoint — 2026-09-14 14:31 EET

## Authority / starting state
- Run-start `main`: `a58736f7014a691bed7b6892d4c968552f5a3346`.
- Authoritative Core source archive SHA-256: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`.
- This path is an isolated physical-phone design-compatibility QA build, not the authoritative production release candidate.

## Failure found
GitHub Actions run `34838193570` failed after WIF/GCP/IAP access and source/Gradle checksum verification succeeded. The failure was exit code `141`.

Root cause was a tooling false-negative: `set -o pipefail` combined with `zipinfo/unzip | grep -q`. `grep -q` exits once it finds the expected match, the producer receives SIGPIPE, and the otherwise-successful inspection becomes status 141.

## Safe reversible repair
Commit `33fa42481915684c355f935f8d1145630e80087e` (`fix(core): make Phone UI1 APK inspection pipefail-safe`) materializes ZIP/index inspection output to regular files before matching. No source SHA, package policy, target SDK, signing state, backend acceptance, or release gate was weakened.

## Re-run evidence
GitHub Actions run `34838408684`: SUCCESS.
- WIF authentication: PASS.
- GCP setup: PASS.
- IAP staging/build path: PASS.
- Source SHA-256 verification: PASS.
- Gradle 8.11.1 cached distribution verification: PASS.
- Android build/package inspection: PASS.
- targetSdk: `36`.
- Package: `com.topherofit.thf.core.debug`.
- versionCode: `62203`.
- versionName: `6.2.2-rc6-phoneui1-debug`.
- Bundled Core UI: PASS.
- Bundled i18n: PASS.
- Bundled world3d payload: PASS.
- APK SHA-256: `465faa1a04a276c648ef851f758b79640eddff0c2b3bf382a7cf8021cc6aca71`.
- APK size: `95799` bytes.
- Artifact: `THF-CORE-RC6-PHONE-UI1-LOCAL-QA`, ID `10345495309`.
- Artifact ZIP SHA-256: `01d03681d0272d753db2e4dd6178b62b0772a5eb31220ea2eb9d365aedc6d7b0`.

## Mobile Real-Function Release Policy truth
This artifact is NOT FINAL and is not Play-ready.
- It is debug-signed and uses the `.debug` package identity.
- `production_signing=false`.
- `play_upload=false`.
- Backend-dependent features are explicitly NOT accepted by this candidate.
- No physical Android device was attached; therefore install, launch, touch, layout/orientation, background/resume, offline/network transitions, core journey, crash-free smoke, FPS/RAM/thermal, or GPU/device QA are not claimed.
- This artifact must not substitute for exact-authoritative-candidate physical-device evidence.

## Program isolation / unchanged blockers
- No WAVE files, canonical source, SSH/OS Login policy, Cloudflare production configuration, or deployment state were mutated.
- No signed AAB, Play approval, production HTTPS/WSS cutover, or production deployment is claimed.
- Existing Games V14 physical-evidence policy remains in force and game candidates remain NOT_FINAL / PHYSICAL_DEVICE_PENDING.

Body SHA-256 (content above this line): `c5ee682376b0215d12e368a0d1b9a2ff237a48cfca8a963a3367d324afb72402`
