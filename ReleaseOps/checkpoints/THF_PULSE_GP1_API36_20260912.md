# THF Pulse GP1 API36 checkpoint — PASS

Scope: THF Pulse only. WAVE_MAWJA untouched.

## Source identity
- Canonical outer SHA-256: `8f18fc7f889c1fd0e01994350b399434a9779e714664c6974bb7925f36f50913`
- Canonical inner/source SHA-256: `31116912623767ebc2edcd56ad55fb2358a4cf398d2765f5eb1de9d842a75ad2`
- Application ID: `com.thf.topherofit.fitness`
- Android target SDK: `36`

## Toolchain
- GCP access: GitHub OIDC/WIF + IAP; no persistent cloud key.
- Gradle: `8.13`
- Gradle distribution SHA-256: `20f1b1176237254a6fc204d8434196fa11a4cfb387567519c61556e8710aed78`
- Android SDK/API 36 from the existing builder toolchain cache.

## Build and package evidence
- GitHub Actions run: `34682783304`
- Debug APK SHA-256: `8e7fd62f48247a0bd2e25ddfece452cfb21e0c189038f8988ed13bfe1c284af7`
- Debug APK size: `12383` bytes
- Test unsigned AAB SHA-256: `cd0e46163bd04b28f95349570d6889b64ce1b483514726387c564926ae1b9f34`
- Test unsigned AAB size: `8791` bytes
- Evidence artifact ID: `10294382372`
- Evidence artifact ZIP SHA-256: `bf1b9d551a0e411d2482b28956ea409ac5a05cf4c519a24dadf8ad46d1a0d459`
- Debug and release/test builds: PASS.
- AAB ZIP integrity: PASS.
- Final gate: `THF_PULSE_GP1_PASS`.

## Safety truth
- Production signing credentials used: NO.
- Google Play upload/publish performed: NO.
- Canonical source modified: NO.
- WAVE files/runtime touched: NO.
- Cloudflare production cutover: NO.
- Solana/token financial action: NO.

## Non-blocking observations
- Current Android/Gradle stack emits deprecation warnings and an SDK XML-version compatibility warning. They did not fail the API36 build gate and should be tracked for future toolchain modernization rather than patched into canonical source during release intake.

## Next
Continue to the next highest-priority unblocked THF release-readiness gate. Keep physical-device acceptance and production signing/publish external until explicitly authorized.