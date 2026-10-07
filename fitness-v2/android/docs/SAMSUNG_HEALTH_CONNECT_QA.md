# Samsung Health → Health Connect → Top Hero Fit QA

Status: **NOT YET PHYSICALLY VERIFIED**. This document is a device evidence procedure,
not a PASS claim.

## Preconditions

1. Install the exact candidate APK and record its SHA-256, versionCode, signer digest,
   device model, Android version, Health Connect version, and Samsung Health version.
2. In Samsung Health, enable sharing of steps and exercise sessions with Health Connect.
3. In Health Connect, grant Top Hero Fit read access to steps, exercise, distance, and
   active calories plus write access to exercise sessions. Do not grant unrelated types.

## Read path

1. Record at least 20 steps or one short exercise in Samsung Health.
2. Open Top Hero Fit → **الصحة** → **مزامنة الآن**.
3. Capture the screen showing non-zero data and a provenance pill for Samsung Health's
   package (`com.sec.android.app.shealth`).
4. Capture Health Connect's data/access screen showing the same source record and time.

## Write and de-duplication path

1. Complete one THF workout and note its locally persisted `clientRecordId`.
2. Verify exactly one exercise session appears in Health Connect from
   `com.topherofit.thf.pulse`.
3. Reopen the app and retry sync. Verify the stable client ID does not create a second
   session.
4. Revoke one permission, resume Top Hero Fit, and capture the disconnected/error state.
5. Restore permission, sync, and capture recovery plus the last-sync timestamp.

## Evidence required for PASS

- unedited screen recording covering read, write, retry, revoke, and recovery;
- APK SHA-256 and signing certificate SHA-256;
- `adb shell dumpsys package com.topherofit.thf.pulse` excerpt;
- Health Connect and Samsung Health source screenshots;
- device/runtime metadata and any crash/logcat excerpt.
