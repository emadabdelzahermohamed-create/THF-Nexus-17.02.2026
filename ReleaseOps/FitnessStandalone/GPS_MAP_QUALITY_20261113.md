# TopHeroFit GPS / Activity Engine quality report — 2026-11-13

## Scope and source of truth

This report records only Activity Engine, GPS quality, map-stack decision and safe device-QA status for `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.

Start evidence reviewed:
- Historical baseline: [GPS_MAP_QUALITY_20261101.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/gps-map-quality-20261030/ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261101.md)
- Latest canonical GPS report at start: [GPS_MAP_QUALITY_20261111.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/fitness-recovery/20261023/ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261111.md)
- Current canonical recovery checkpoint: [RECOVERY_CURRENT_20261112.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/fitness-recovery/20261023/ReleaseOps/FitnessStandalone/RECOVERY_CURRENT_20261112.md)

## Candidate and exact source

- Canonical base: `dedd5f39001781c19e7e19bdee8f44e2fa97b01d`
- PR: [#292 — GPS fallback resilience](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/292)
- Branch: `agent/codex/gps-fallback-resilience-20261113-r2`
- Source/test HEAD: `cb97dc0b66299825e6a02dd91ec53e369667bb74`
- Changed files: five Activity Engine/GPS source and test files only.
- Compare: 5 commits ahead, 0 behind the stated canonical base.

## Material fixes

1. **Provider disabled while registered:** previously, `alreadyRegistered` could prevent re-selection after the active framework provider was disabled. The service now detects current-provider availability and handles `onProviderEnabled` / `onProviderDisabled` immediately. It reselects only a permission-eligible enabled provider, or removes updates and clears selection if none is available.
2. **Registration retry storm:** repeated framework registration failures now use bounded 4s, 8s, 16s and 30s backoff instead of attempting every watchdog tick.
3. **Fused callback lifecycle:** each request has its own callback and session generation. Late Task success/failure after pause, stop or replacement cannot restart collection and removes only the stale callback.
4. **Permission-aware fallback:** coarse-only permission selects Network; GPS requires fine permission. A silent GPS source receives a bounded first-fix window before Network fallback.
5. **Accuracy truthfulness:** accepted accuracy is visible only for a fresh ready fix and a finite positive value. Stale, filtered, missing, invalid and paused states return null rather than 0 m.

Provider changes reset the location measurement anchor, observed/accepted accuracy and speed; distance is not bridged across source changes.

## Tests and validation

- Exact-source local Kotlin compile and behavior harness: 23 fallback/provider assertions PASS.
- Exact-source local accuracy-presentation harness: 12 assertions PASS.
- Exact fetched-source contract audit: 13/13 PASS.
- GitHub Android workflow: [run 43382459916](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43382459916), exact source HEAD `cb97dc0b66299825e6a02dd91ec53e369667bb74`.
- Exact-head Android run [43382459916](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43382459916) completed SUCCESS on source/test SHA `cb97dc0b66299825e6a02dd91ec53e369667bb74`.
- Product tests 67/67; source-contract 34/34; backend 29/29; Android unit tests 250/250 (0 failures, 0 ignored).
- Android API 36 setup, `:app:testDebugUnitTest`, `:app:lintDebug`, `:app:assembleDebug` and `:app:bundleRelease` validation all passed. Lint reports 0 errors, 16 warnings and 1 hint.
- Artifact ID `14017730574`; downloaded ZIP SHA-256 `e4f5c286137856df5c503cb3140eaff48608dd594004b6736637f5241fdcb149`; QA APK SHA-256 `ee26a73729eee644a279716e2b457c85a68fe26cea3d9663b96dc9e43c4f3e36`; validation AAB SHA-256 `fb1e66c0e2570ddd14d00367890da2ed95f6374b08239e5f1d537366c54b7b80`.
- The ZIP was downloaded and independently rehashed; `jarsigner -verify` reports the validation AAB is unsigned. Package `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is QA validation only, not a release artifact.
- Documentation-only checkpoint/report commits followed the tested application/test SHA; no application source changed after it. The exact tested application/test SHA remains `cb97dc0b66299825e6a02dd91ec53e369667bb74`.

## Physical-device QA

- Authorized Desktop Commander device `localhost`: OFFLINE, last seen 68 hours ago; ADB device list empty.
- No install, launch, Stop, pause/resume, location-setting change or activity-data read was attempted.
- Stationary-drift, measured-route, coarse-only Android 12, first-fix latency, screen-off/background, persistent-notification controls and process-death restoration remain `BLOCKED_NOT_RUN`.
- Preserve the unknown live phone session until the device reconnects and is confirmed safely idle.

## Maps and owner prerequisite

The current canonical decision remains the free Leaflet/WebView stack with attributed OpenStreetMap streets, OpenTopoMap terrain and EOX 2016 satellite/hybrid. It does not require Google Maps SDK billing or a key.

Historical Maps preflight `41684077962` (2026-11-03) found Maps Android Backend and API Keys APIs enabled, but key-inventory permission denied, no package/SHA-restricted Android key visible and no billing account linked. No new permission attempt, key, billing or paid infrastructure was made. Native Google basemap, traffic and transit layers are not present or claimed. Revisit only after owner prerequisites and an explicit canonical map-stack decision.

## Scope and release boundary

No `app.js`, `MainActivity.kt`, `test_source_contract.py`, Health/anti-cheat, exercise-catalog, workflow, release-version, signing or Play file changed in PR #292. VersionCode 51020 remains unallocated. No AAB was signed or uploaded; no Play state changed.
