# Top Hero Fit Fitness V2 — Android

Offline-first Android source for `com.topherofit.thf.pulse`, API 36, versionCode 51003.
The packaged workout flow remains usable without a network or Health Connect. Active
session state is persisted across background/resume, and completed workouts are queued
locally before any optional Health Connect write.

Completed workouts are also queued for the shared V2 backend. The native HTTPS client
uses the same stable record/version contract as Health Connect, rejects redirects, and
accepts only a short-lived account access token supplied at runtime. Tokens are held in
memory only and are never written to preferences. Until the canonical account flow
completes the external-browser, PKCE-bound, single-use ticket flow (and `THF_BASE_URL`
is an approved persistent HTTPS endpoint), the
queue remains local and the app reports sync as unconfigured/unauthenticated.

Health Connect V2 currently requests only the data displayed or written:

- read steps, exercise sessions, distance, and active calories;
- write completed THF exercise sessions;
- no heart-rate, sleep, weight, body-fat, route, or background-read permission;
- stable `clientRecordId` plus version for retry de-duplication;
- provenance package names, last-sync, permission-revoke, empty, and error states.

The source gate and JVM tests are runnable with:

```sh
python fitness-v2/tests/test_source_contract.py
python -m unittest discover -s fitness-v2/backend/tests -v
gradle -p fitness-v2/android :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
```

Physical-device Health Connect and Samsung-origin evidence remain fail-closed until the
steps in `docs/SAMSUNG_HEALTH_CONNECT_QA.md` are completed against the exact APK SHA.
