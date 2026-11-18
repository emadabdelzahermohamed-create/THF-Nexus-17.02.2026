# TopHeroFit GPS / Map Quality checkpoint — 2026-11-18

Scope: TopHeroFit only. Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.

## Starting evidence read

- Requested historical starting report: `ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261101.md`, branch `agent/codex/gps-map-quality-20261030`, blob `0e50b45f7be1e2a245753233f3e70343394b1115`.
- Latest canonical GPS report before this run: `GPS_MAP_QUALITY_20261117.md`, blob `66a2ba33d7c3237f54c60453d05e668870ea0f3f`.
- Canonical recovery checkpoint before this run: `RECOVERY_CURRENT_20261117.md`, blob `4ac6ebd10c91bf0fbf5fb16a8ddd100e29695cd8`.
- Canonical branch: `agent/codex/fitness-recovery/20261023`, HEAD `eb2e65780a7359ceb7da15edef9cdb03aad8591d`. That canonical commit is a documentation-only checkpoint; the prior canonical application/source head is `b248a3571d871c604dbc3a11af72858bbac74eb9`.

## Current GPS handoff and exact tested source

- PR: [#297](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297), Draft/open/unmerged.
- Candidate branch: `agent/codex/gps-permission-downgrade-20261116-r1`.
- Exact tested application/source SHA: `16c5104a4f8af94f8b8c5bd71b4f52123e0caa4a`.
- Current source diff against canonical application base: 14 GPS Activity Engine source/test files. The candidate is 8 commits ahead / 1 behind the canonical documentation checkpoint; the sole behind commit is documentation-only. No Health, anti-cheat, exercise catalog, `app.js`, MainActivity, manifest, release workflow, signing or Play file is in the GPS source diff.

### New test-quality correction

- Commit `157c2dee3f2509eba6d89b5887034e73caca26e0` corrected a Kotlin test fixture from a literal backslash-n to an actual newline. Previously, the malformed header could cause route data to be parsed as a header field, allowing negative assertions to pass for the wrong reason.
- Commit `16c5104a4f8af94f8b8c5bd71b4f52123e0caa4a` adds a positive control: a valid V1 checkpoint with two monotonic route points must decode successfully, while the existing zero-accuracy and non-monotonic route cases remain rejected.
- Changed application behavior: none in these two final test-only commits. The underlying GPS/session implementation remains the previously reviewed 14-file handoff.

## Exact-head Android CI — PASS

[Run 44257340423](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44257340423) completed SUCCESS on exact source SHA `16c5104a4f8af94f8b8c5bd71b4f52123e0caa4a`.

| Gate | Result |
|---|---:|
| Product tests | 69/69 |
| Source-contract tests | 34/34 |
| Backend tests | 29/29 |
| Android `:app:testDebugUnitTest` | 290/290; 0 failures; 0 ignored |
| Android API 36 | PASS |
| Kotlin compilation | PASS |
| `:app:lintDebug` | PASS |
| `:app:assembleDebug` | PASS |
| `:app:bundleRelease` | PASS_UNSIGNED |
| Gradle | BUILD SUCCESSFUL |
| Lint | 0 errors, 11 warnings, 1 hint |
| Competition backend job | Skipped; no competition files changed |

Artifact `14407185529` was downloaded and independently inspected:
- GitHub artifact ZIP digest: `sha256:05abf94fc8c98de81bec6cacbf55e27a43bfcf0f7b4ce711d4012c9b01525ebd`.
- Independently recomputed ZIP SHA-256: `05abf94fc8c98de81bec6cacbf55e27a43bfcf0f7b4ce711d4012c9b01525ebd` (exact match).
- QA APK SHA-256: `07cba26c0f3250b3f174f9e78688cd262d5d4734d24497bbd9bf1c465d15167b`.
- Validation AAB SHA-256: `c02f9ee942ab67261e76720927aff48dcfa129e4100d49e92f20195c10dcf5fb`.
- `jarsigner -verify`: `jar is unsigned`; no production signing is present.
- QA-only identity: `com.topherofit.thf.pulse.qa`, versionCode `51019`, versionName `5.0.0-v2-alpha19-debug`. This is validation only, not a production or Play artifact.

## Current Activity Engine / GPS behavior reviewed

- Fused Location Provider is primary: high-accuracy priority, 1-second interval/minimum interval, zero cached maximum age, zero batching delay, fine granularity and wait-for-accurate-first-fix.
- Framework fallback uses only one permission-eligible provider: GPS requires Fine; Network requires Coarse. Approximate-only downgrade switches an active GPS fallback to Network on the next four-second watchdog pass when Coarse and Network are available.
- Registration failure uses bounded exponential retry (4/8/16/30 seconds); generation guards prevent late Fused callbacks from reviving paused, stopped or replaced sessions.
- Provider changes clear the old source anchor and distance accumulator; distance is not bridged across providers.
- Fix gate rejects mock, invalid coordinates/accuracy, stale/future/out-of-order fixes and sport-speed jumps. Walk/run maximum accepted horizontal accuracy is 25 m; cycle is 40 m.
- Stationary jitter deadband uses the worse endpoint accuracy; rejected fixes do not advance the accepted speed anchor.
- Distance accumulator requires displacement beyond both reported accuracy radii plus 3 m, confirmed by at least three accepted fixes over six seconds; credited path is capped at 1.4x net displacement. A prolonged stationary drift is still not physically disproven.
- A live fix gap beyond 30 seconds clears the live speed/distance anchor while preserving route history; no unobserved distance is bridged.
- ActivitySessionCheckpoint V3 persists phase, wall/monotonic clocks, boot identity and bounded route. Lifecycle-critical writes/deletes use synchronous commit. Restore is limited to 24 hours with matching boot identity, otherwise the legacy fallback is 120 seconds. Only an unpaused, positive-accuracy route fix still within the 30-second freshness window may seed a live anchor.
- Foreground service, START_STICKY, ongoing notification, Pause/Resume/Finish actions and 10-second checkpoint writes exist in source. Notification content refreshes every five seconds.

These are source and CI findings, not physical GPS acceptance.

## Map stack and Google Maps owner prerequisite

The 2026-11-01 report documents four selectable Leaflet base styles, and the current canonical `app.js` confirms them in `ensureActivityMap()` (blob `05eab8a664458e2954259c85b120906b1b965820`):
1. Street — OpenStreetMap standard raster tiles.
2. Terrain — OpenTopoMap.
3. Satellite — EOX Sentinel-2 cloudless 2016 imagery.
4. Hybrid — EOX 2016 imagery plus transparent EOX streets overlay.

The inspected Android Gradle file contains `play-services-location:21.3.0`; no Google Maps SDK dependency was found. There is no native Google basemap, live traffic or transit overlay. EOX imagery is explicitly 2016, not current imagery. Browser tile cache is not a guaranteed offline package; OSM/OpenTopoMap are best-effort services without an app uptime SLA.

Latest owner prerequisite evidence remains the 2026-11-03 read-only preflight referenced by the November 1 report:
- Maps Android Backend API enabled.
- API Keys API enabled.
- Key inventory permission denied to the release-builder identity.
- No Android key restricted to the package and signing SHA is available.
- No billing account is linked; no payment method or paid infrastructure was added.

No new Cloud permission evidence was available in this run. Do not create or expose a key, link billing, or claim Google Maps readiness. Native Google Maps and Google traffic/transit remain blocked by the owner prerequisite.

## Physical-device QA

`BLOCKED_NOT_RUN` for this run.

- Fresh Desktop Commander device list: `localhost` OFFLINE, last seen about 21 hours before this check.
- Last known handset: Samsung SM-A217F / Android 12.
- No ADB device was available. No install, launch, force-stop, Stop action, settings change, location-mode change or activity-data read was attempted.
- The 2026-11-16 limited QA note used a separate QA package; the Play package `com.topherofit.thf.pulse` remained installed at 51019 and was not overwritten. The QA package was removed after the test.
- Prior observations: Arabic RTL onboarding without observed startup crash/ANR; foreground ActivityTrackingService and Fused high-accuracy request; stationary observation zero steps/zero distance; indoor poor fixes (about ±400 m then ±59 m) were filtered without accepting a route point; native bridge Pause/Resume toggled state.
- Not proven: outdoor measured walk/run/cycle, 60-second stationary drift, first-fix latency, permission downgrade on handset, full-screen or notification action taps, screen-off/background, task removal, process-death restore and battery behavior.
- Preserve the installed Play package and unknown current session until safe ADB inspection is available.

## Known shared UI ownership hold

Read-only inspection of canonical `app.js` (blob `05eab8a664458e2954259c85b120906b1b965820`) found:
- `renderActivity()` labels every `gpsFixState === 'ready'` as “GPS”, even when the accepted source is Fused or Network.
- It does not map `gpsFixState === 'paused'` to localized paused copy, so the screen falls through to generic GPS-waiting text.
- The native notification does distinguish GPS, Network and Fused source labels; the WebView screen does not yet expose that source distinction.

`app.js` remains under shared ownership holds (#216/#224; #284 also overlaps map UI). No shared UI file was edited. Resolve the lease and combined-head CI before changing this surface.

## Scope / release boundary

- No Health/anti-cheat or exercise-catalog file changed. `ActivityEvidenceAnomalyPolicy.assessSegment()` remains unwired in the live service; this work does not claim full anti-cheat or cryptographic location attestation.
- No route upload/cloud backup is claimed; finished route history remains local in WebView storage.
- No release version, workflow, signing, secret, billing or Play state changed.
- VersionCode 51020 remains unallocated. No signed AAB, upload, track mutation or Play PASS.
- Keep PR #297 Draft/unmerged until physical GPS/session P0 and shared UI/privacy gates pass.
