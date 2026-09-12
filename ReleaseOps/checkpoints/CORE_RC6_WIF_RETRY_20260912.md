# Core RC6 WIF-safe retry checkpoint — 2026-09-12

Scope: THF Core only. Terra/Rift/WAVE source untouched.

## Prior blocker
- GitHub Actions run `34651159978` failed at WIF authentication before any GCP build step.
- Root cause class matched the previously observed long-ref `google.subject` WIF limit; no source/build failure was established by that run.

## Remediation
- Created short WIF-safe branch `c/r6` from exact Core RC6 gate commit `57843bd7ae36db908532cf9dfc587dbb68b35387`.
- Added isolated workflow `thf-core-rc6-unsigned-build-v2.yml` on commit `4a38c1b6451c523bfc1f29a7607bab752f38d227`.
- Canonical Core RC6 source remained read-only: `THF_Core_RC6_ANDROID_NATIVE_I18N_RELEASE_CUMULATIVE_SOURCE.zip`.
- Verified source SHA-256: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`.
- Production signing environment variables were explicitly unset by the gate.

## Final result — PASS
- GitHub Actions run: `34678895451` — SUCCESS.
- WIF authentication: PASS.
- GCP/IAP builder execution: PASS.
- Exact source SHA verification: PASS.
- Package id: `com.topherofit.thf.core`.
- Version: `6.2.2-rc6`; versionCode `62200`.
- targetSdk: `36`.
- Gradle debug/release build: PASS; release lintVital: PASS.
- Debug APK ZIP integrity: PASS; SHA-256 `87d119badc52504bd2471eec53fcc0142ca2e2cbac3171ab825b871c4087199f`.
- Release AAB ZIP integrity: PASS; SHA-256 `e71625911d2c06eb0d084f6ed094fcd142f093fcfbb2bf2b13b59a4221760e6e`.
- Package evidence JSON SHA-256: `1a583d9ae021b950978d3867eac8c0175535d3a91b378c8c4d87dbb1721a36ee`.
- GitHub artifact: `THF-Core-RC6-unsigned-test-candidates-v2`, artifact id `10293900762`, artifact digest `sha256:af44ff5d20abce39bbd73ef4fa2e3d68ea0385b2c642f2069b485e673d0652de`.
- APK signer verification identifies Android Debug certificate only; no production signing credentials used.

## Truth / safety boundary
- production_signing_credentials_used: false
- play_upload_performed: false
- physical_device_qa: false
- other_app_source_touched: false
- wave_touched: false
- No Cloudflare production cutover.
- No Solana transaction or financial action.
- No canonical archive overwrite/delete.

## Gate disposition
`CORE-RC6-ANDROID-UNSIGNED-R2` is CLOSED / PASS. Do not rerun unless source or release tooling changes materially.

## Next
Resume the highest-priority unblocked THF release-readiness gate after Core/Terra/Rift, while keeping WAVE_MAWJA isolated. WAVE remains independently blocked only if the full canonical runtime/source is still absent from the builder/intake sources.
