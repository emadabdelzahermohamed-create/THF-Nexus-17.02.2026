# 51010 notification permission device API gate — 2026-10-24

## Exact live evidence
- Physical device reachable over ADB: Samsung SM-A217F.
- Installed package: `com.topherofit.thf.pulse`.
- Installed candidate: `versionCode=51010`, `versionName=5.0.0-v2-alpha10`, `targetSdk=36`.
- Installer remains `com.android.vending`; no uninstall, force-stop, or data deletion was used.
- Device OS is Android 12 / API 31 (`ro.build.version.release=12`, `ro.build.version.sdk=31`).
- Manifest declares `android.permission.POST_NOTIFICATIONS`.
- Because `POST_NOTIFICATIONS` is an Android 13+ (API 33+) runtime permission, this API-31 SM-A217F cannot physically exercise the 51010 API33+ Allow/Deny runtime-permission branch. Do not claim that branch PASS from this device.

## Outcome
- 51010 Play install remains verified on the physical phone.
- API33+ notification permission Allow/Deny physical acceptance is BLOCKED on this handset by OS level, not by the app/build/release pipeline.
- Notification foreground-service/Stop behavior on Android 12 remains a distinct executable phone gate and should be tested separately without conflating it with API33 permission acceptance.

## Next step
1. On SM-A217F/API31, exercise foreground tracking notification + Stop semantics while preserving data.
2. For the actual `POST_NOTIFICATIONS` Allow/Deny branch, use a physical or authorized test device/emulator running API33+; do not fabricate a PASS.
3. Keep outdoor GPS, Health Connect real record-level provenance, long-duration/process-death/reboot, and audible Arabic/offline voice explicit pending gates.
4. Production remains unclaimed.
