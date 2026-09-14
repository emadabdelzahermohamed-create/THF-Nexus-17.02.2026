# THF Release / Phone-QA Factory — Batch 11 — 2026-09-15

Status: NOT_FINAL / PHONE_BUILD_PENDING

## Authority read
- Starting main HEAD: `2e24161ab407b2eab3c479c479af7bd7a8e2a167`.
- Latest six Phone Fundamentals sources were recovered as exact Library bytes and independently SHA-256 verified against `THF_APPS_PHONE_FUNDAMENTALS_SOURCE_V1_MANIFEST.json`.
- Older APKs tied to prior source SHAs remain superseded and ineligible for this batch.

## Exact source intake verified
- THF Market / forge — `d17477fd370fdc4b04562f7f1113e79942951f1d39444b498f18d82de983ed1f` — 56,911 B — package `com.topherofit.thf.forge`.
- THF Community / echo — `0b9d6180b1701b239c1288fa76418e32086b9fc679995d1d2acdc0c7f098554c` — 63,315 B — package `com.topherofit.thf.echo`.
- THF Learn / codex — `255d8f24aec054bc4a42f8de845eeb895276b0938864b49166d89ff27377e4bd` — 69,540 B — package `com.topherofit.thf.codex`.
- THF Wallet / vault — `2dc0f527b23bd9d6654cd611f94d8b6e4502f0e24184c846372cf4b9e007de2d` — 28,295 B — package `com.topherofit.thf.vault`.
- THF Publisher / signal — `da0282314077bd55912629eecd599b64f292c958163a6bede6804894769460aa` — 28,400 B — package `com.topherofit.thf.signal`.
- THF Admin / command — `fb31bd2a4dba0344f37eed27ff36eb918b81d502c394f0d423bc2d97e61ca1e5` — 42,273 B — package `com.topherofit.thf.command`.

## Static phone-baseline checks performed on exact bytes
- All six: compileSdk 36 / targetSdk 36 and minSdk 26.
- Version identity read from source: Forge/Echo/Codex `2.1.1` / versionCode `21100`; Vault/Signal `1.2.0-apps-rc2` / versionCode `12000`; Command `1.2.0` / versionCode `12000`.
- All six: exactly 20 `values*` string-resource sets, adaptive + monochrome icon resources, RTL support and Data Saver source hooks present.
- Public Forge/Echo/Codex/Vault retain MAIN/LAUNCHER.
- Private Signal/Publisher and Command/Admin have no MAIN/LAUNCHER and retain signature-protected private entry permissions; they remain internal/operator products.
- No obvious embedded production API key, client secret, private key, bearer token or `sk-` secret pattern was found in the exact source trees.
- No package IDs were changed.

## Shared integration authority
- Shared Integration V3 CI is authoritative for Google/THF Identity, passkey/email-code fallback contracts, Health Connect primary bridge, optional Samsung Health adapter, replay protection, cross-app handoff and shared RTL/Data Saver/Reduce Motion/High Contrast preferences.
- Production OAuth/provider binding, durable replay store, server signer and physical health-provider validation remain pending; no source-only claim upgrades them.

## Games authority retained
- Terra: source `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`; eligible QA APK `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`.
- Rift: 4.7.5-rc41 source `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`; no eligible APK; RC37 and earlier remain superseded.
- Spark: source `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`; eligible QA APK `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`.
- Rush: source `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`; previous APK remains rejected pending exact rebuild with native V2 motion/icon overlay.

## Build/device result this run
- A dedicated staging branch `phone-factory-20260915-batch11` was created from the exact main HEAD to isolate build work from main.
- The active remote Desktop Commander device was unavailable during this run, so no Android SDK/ADB build or physical-device action was fabricated.
- Current container has JDK 17 but no Android SDK/Gradle toolchain; Android SDK license acceptance was not performed on behalf of the user.
- Therefore the six new source candidates remain `NEEDS_EXACT_SOURCE_BUILD`; previous APKs are not promoted.

## Next exact actions
1. On the authorized Android builder, build the six exact source ZIPs without source mutation; prefer an ephemeral QA signing key only for installable phone candidates, never production signing.
2. Inspect each produced APK for exact package/version/targetSdk 36/ABI/payload/icon/zipalign/signature and ordinary-user launcher visibility policy.
3. Rebuild Rush exact current source with native V2 motion/icon overlay; do not reuse the rejected old APK.
4. Stage exact Rift RC41 bytes before any Rift build; never substitute RC37.
5. Run exact-candidate physical-phone acceptance before FINAL/PLAY_READY.

`FINAL_OR_PLAY_READY=FALSE`
`PHYSICAL_DEVICE_PASS=FALSE`
`PRODUCTION_SIGNING=FALSE`
`WAVE_TOUCHED=FALSE`
