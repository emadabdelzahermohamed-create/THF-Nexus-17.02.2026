# THF Core RC6 — Android unsigned pipeline checkpoint

Scope: **THF Core only**.

Authoritative source:
- `THF_Core_RC6_ANDROID_NATIVE_I18N_RELEASE_CUMULATIVE_SOURCE.zip`
- SHA-256: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`
- package: `com.topherofit.thf.core`
- version: `6.2.2-rc6`
- versionCode: `62200`
- compile/target SDK: `36`

Preserved without rerun: Core source/static regression **38/38 PASS**.

This checkpoint adds an isolated Core-only GitHub Actions lane. It uses the already prepared x86_64 builder and exact RC6 source input, then creates only:
- debug-signed test APK;
- unsigned release AAB;
- package/SDK inspection evidence;
- SHA-256 evidence.

It explicitly unsets production signing credentials and does not perform Play upload. It never reads or builds Terra/Rift sources and does not touch WAVE.

Truth boundary: this checkpoint by itself is not evidence of a successful binary build; the workflow run must complete successfully and its package evidence must be collected first.
