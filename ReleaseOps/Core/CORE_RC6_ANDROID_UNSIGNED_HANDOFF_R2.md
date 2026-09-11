# THF Core RC6 — Android unsigned pipeline R2

Scope: **THF Core only**.

Authoritative source:
- `THF_Core_RC6_ANDROID_NATIVE_I18N_RELEASE_CUMULATIVE_SOURCE.zip`
- SHA-256: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`
- package: `com.topherofit.thf.core`
- version: `6.2.2-rc6`
- versionCode: `62200`
- compileSdk/targetSdk: `36`

Preserved without rerun: Core source/static regression **38/38 PASS**.

R1 evidence: run `34651159978` stopped at WIF authentication before any build step; no Core extraction/build occurred and no Terra/Rift/WAVE source was touched.

R2 safe remediation: execute the dedicated Core-only workflow from the existing WIF-authorized ReleaseOps ref while keeping all stream state/evidence under `ReleaseOps/Core/**`. The workflow reads only the exact Core RC6 archive, verifies its SHA/size, builds a debug test APK and unsigned release AAB, inspects package/SDK/signature state, and emits SHA-256 evidence.

No production signing, Google Play upload/approval, physical-device QA, financial action, or production cutover is performed or claimed.
