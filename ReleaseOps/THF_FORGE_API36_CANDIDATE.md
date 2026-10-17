# THF Forge exact API 36 candidate

- Canonical source archive: `Sources/THF_Forge_PHONE_FUNDAMENTALS_SRC3.zip`
- Source SHA-256: `75c3744af31f16273a174bdac53b9e812613e4d9ef8c2fa260521c7f7c40cbf8`
- Package: `com.topherofit.thf.forge`
- Version: `2.1.1-phone3` (`21102`)
- compile/target SDK: 36
- Build workflow verifies the exact source before producing APK/AAB, then records artifact hashes and package metadata.
- Signing: CI output is an install-test candidate only. Production Play signing remains an owner-controlled prerequisite.
- Rollback: revert the single candidate commit or reset this branch to base `1ffcbf59987343febf75570270bc9425eabd156f`.
- Physical phone and Play release remain unverified until evidence is captured by their authorized lanes.
