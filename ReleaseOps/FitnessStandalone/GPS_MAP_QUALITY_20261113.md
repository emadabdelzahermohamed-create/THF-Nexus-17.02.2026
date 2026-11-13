# TopHeroFit GPS / Activity Engine quality report — 2026-11-13

## Scope and source of truth

This report records only Activity Engine, GPS quality, map-stack decision and safe device-QA status for `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.

Start evidence reviewed:
- Historical baseline: [GPS_MAP_QUALITY_20261101.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/gps-map-quality-20261030/ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261101.md)
- Latest canonical GPS report at start: [GPS_MAP_QUALITY_20261111.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/fitness-recovery/20261023/ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261111.md)
- Current canonical recovery checkpoint: [RECOVERY_CURRENT_20261113.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/fitness-recovery/20261023/ReleaseOps/FitnessStandalone/RECOVERY_CURRENT_20261113.md)

## Candidate and exact source

- Canonical base: `dedd5f39001781c19e7e19bdee8f44e2fa97b01d`
- PR: [#292 — GPS fallback resilience](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/292)
- Branch: `agent/codex/gps-fallback-resilience-20261113-r2`
- Original PR source/test HEAD: `de304b6f4baa44dc80b3245493d7275fe39f00fe` (exact PR-head CI source/test SHA).
- Changed files: five Activity Engine/GPS source/test files plus the GPS report and a prior-day recovery note; no `app.js`, `MainActivity.kt`, `test_source_contract.py` or Health manifest changes.
- The PR was originally based on `dedd5f39001781c19e7e19bdee8f44e2fa97b01d`. The canonical branch has since advanced; this branch has not been rebased or combined-tested against the latest canonical head.

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
- Read-only notification/session-control audit: 6/6 PASS — foreground service calls `startForeground`, ongoing notification refreshes every 5 seconds, notification exposes Stop/Pause/Resume actions, and MainActivity exposes pause/resume/end plus snapshot pause/accuracy state. Source evidence only; device interaction remains NOT RUN.
- Synthetic PR merge-event validation: [run 43382459916](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43382459916) on merge SHA `cb97dc0b66299825e6a02dd91ec53e369667bb74`; this was not the exact branch-head run.
- Exact PR-head Android run [43383307618](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43383307618) completed SUCCESS on source/test SHA `de304b6f4baa44dc80b3245493d7275fe39f00fe`.
- Product tests 67/67; source-contract 34/34; backend 29/29; Android unit tests 250/250 (0 failures, 0 ignored).
- Android API 36 setup, `:app:testDebugUnitTest`, `:app:lintDebug`, `:app:assembleDebug` and `:app:bundleRelease` validation all passed. Lint reports 0 errors, 16 warnings and 1 hint.
- Exact-head artifact ID `14017568163`; independently rehashed ZIP SHA-256 `d1aee733160901a21e0752b8615c3e2c6a858a64c529e28e9147162553458c32`; QA APK SHA-256 `a0914f8767fdebc6799cc8bc2858dabf46355f87e1828742d1e482160ef63289`; validation AAB SHA-256 `fb1e66c0e2570ddd14d00367890da2ed95f6374b08239e5f1d537366c54b7b80`.
- The ZIP was downloaded and independently rehashed; `jarsigner -verify` reports the validation AAB is unsigned. Package `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is QA validation only, not a release artifact.
- The exact tested application/test SHA remains `de304b6f4baa44dc80b3245493d7275fe39f00fe`. This report correction is documentation-only; it does not change that tested source/test tree or justify rebuilding/reuploading the unchanged validation AAB.

## Physical-device QA

- Authorized Desktop Commander device `localhost`: OFFLINE; last seen about 79 hours before the 2026-11-13 19:47 Cairo check. Current phone session state is unknown; no ADB device or session action was attempted.
- No install, launch, Stop, pause/resume, location-setting change or activity-data read was attempted.
- Stationary-drift, measured-route, coarse-only Android 12, first-fix latency, screen-off/background, persistent-notification controls and process-death restoration remain `BLOCKED_NOT_RUN`.
- Preserve the unknown live phone session until the device reconnects and is confirmed safely idle.

## Maps and owner prerequisite

The current canonical decision remains the free Leaflet/WebView stack with attributed OpenStreetMap streets, OpenTopoMap terrain and EOX 2016 satellite/hybrid. It does not require Google Maps SDK billing or a key.

Historical Maps preflight `41684077962` (2026-11-03) found Maps Android Backend and API Keys APIs enabled, but key-inventory permission denied, no package/SHA-restricted Android key visible and no billing account linked. No new permission attempt, key, billing or paid infrastructure was made. Native Google basemap, traffic and transit layers are not present or claimed. Revisit only after owner prerequisites and an explicit canonical map-stack decision.

## Scope and release boundary

No `app.js`, `MainActivity.kt`, `test_source_contract.py`, Health/anti-cheat, exercise-catalog, workflow, release-version, signing or Play file changed in PR #292. VersionCode 51020 remains unallocated. No AAB was signed or uploaded; no Play state changed.


## Map cache and anti-cheat clarifications — 2026-11-13

- The map implementation is Leaflet with attributed OSM street tiles, OpenTopoMap terrain and EOX Sentinel-2 cloudless 2016 satellite imagery plus an EOX street overlay. The satellite layer is explicitly 2016 imagery, not live satellite.
- MainActivity uses a unique `TopHeroFit/<version>` User-Agent and a strict HTTPS host/path allowlist for OSM/OpenTopoMap/EOX raster tiles. WebView cache mode is `LOAD_DEFAULT`; this is ordinary WebView HTTP caching, **not** a guaranteed offline tile package or a custom durable OSM tile cache. Offline map availability is not claimed.
- The map is not Google Maps SDK and requires no Google Maps billing/key. Map tiles still depend on provider availability, attribution and each provider's usage policy.
- The native service captures raw provider, elapsed-realtime timestamp, mock flag, coordinates and accuracy, but its accepted-fix path still uses `GpsFixGate` and `GpsDistanceAccumulator`; it does not invoke the separate `ActivityEvidenceAnomalyPolicy` / `assessSegment` pipeline. This is not full anti-cheat verification and must be wired before competition distance/pace/reward credit.
