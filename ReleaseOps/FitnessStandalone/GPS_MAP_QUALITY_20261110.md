# TopHeroFit — GPS and Activity Engine quality report

Date: 2026-11-10 (Africa/Cairo)  
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
Canonical branch: `agent/codex/fitness-recovery/20261023`  
Canonical base: `9b5db58e809fa7d5e639bc4ee55df03d100467e8`  
Candidate branch: `agent/codex/gps-open-source-stack-20261109`  
Candidate exact HEAD: `1fab42783712a980367079c413ba6708f772d130`  
Pull request: [#284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284) (Draft, open, unmerged)

## Source-of-truth review

- Re-read the requested historical `GPS_MAP_QUALITY_20261101.md` from `agent/codex/gps-map-quality-20261030`, blob `0e50b45f7be1e2a245753233f3e70343394b1115`.
- Re-read the newest canonical GPS report `GPS_MAP_QUALITY_20261108.md`, blob `44d1a3e751f193d7e95377ed1e9df526b95ba495`.
- Re-read the 2026-11-09 GPS accuracy report from the superseded #283 candidate branch, blob `65d7f587355ee16796a7ecaf8d8cf5161a06207b`.
- Re-read the canonical recovery checkpoint `RECOVERY_20261023.md`, blob `578be4a435991324d3eb3263e5e7127f479ec569`.
- Re-read the open-source map decision `GPS_OPEN_SOURCE_IMPLEMENTATION_20261109.md`, blob `5ff41d2badec177ca7294582b960b2faebdc38bb`.
- PR #284 is 7 commits ahead and 0 behind the canonical base. The exact current branch head is `1fab42783712a980367079c413ba6708f772d130`.

## Material Activity Engine correction

Commit `1fab42783712a980367079c413ba6708f772d130` fixes an asynchronous location-registration lifecycle race:

- Every Fused Location Provider request now owns a unique callback and monotonically increasing request generation.
- Location results are accepted only while the same activity mode is still active, the session is not paused, and the request generation still matches.
- A late successful registration after pause, stop, or replacement removes its own exact callback.
- A late failed registration may start framework-provider fallback only when its original session generation is still current and unpaused.
- Framework fallback registration independently checks session identity, pause state, and duplicate registration.
- Pause/finish/destruction invalidate the generation before removing the exact Fused callback and framework updates.

This prevents a delayed Fused Location task from resurrecting background location collection after the user has paused or ended the activity. It does not prove GPS accuracy or background reliability on a physical route.

Exact source blobs at the current head:
- `ActivityTrackingService.kt`: `1224735a15a6215c347a1b9d6d4b27e7a000f615`
- `ActivityLocationFallbackPolicy.kt`: `4333c16b61c769991476ff98d7be66a688bc2ea5`
- `ActivityLocationFallbackPolicyTest.kt`: `7cbccd55ce59725702179f4e445e62661bfcd1dd`
- `test_source_contract.py`: `ca8482e56de20a415ccd5d68c64f1a2ba06106be`

## Exact-head CI evidence

- Workflow: Fitness Activity Candidate Build
- Run: [42773832856](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42773832856)
- Exact tested SHA: `1fab42783712a980367079c413ba6708f772d130`
- Result: SUCCESS
- Product tests: 60/60
- Source-contract tests: 40/40
- Backend tests: 29/29
- Android API 36 setup: PASS
- `:app:testDebugUnitTest`: PASS
- `:app:lintDebug`: PASS
- `:app:assembleDebug`: PASS
- `:app:bundleRelease`: PASS (unsigned validation output only)
- Candidate artifact ID: `13743311221`
- Candidate archive SHA-256: `1e38b7c2e199f51ef78df00a9e0921904a515cca8931279f2a4c1064913b4e73`

The artifact is a QA/validation candidate using the existing 51019 QA identity. No production signing, version allocation, Play upload, or Play PASS occurred.

## Physical-device QA and exact blocker

The authorized Desktop Commander device is online. Read-only device checks established:

- Device model: Samsung SM-A217F
- Android release: 12
- Installed package list includes `com.topherofit.thf.pulse`.
- `adb devices -l` returned an empty attached-device list.
- A direct read-only `settings get secure location_mode` call from the Termux UID failed with `SecurityException` because UID 10261 lacks `INTERACT_ACROSS_USERS`.

The last recorded device-level observation in the 2026-11-09 candidate report was `location_mode=0` (device location disabled). That value was not independently re-read today. No ADB install, app launch, Stop, session action, or activity-data read was attempted. No physical GPS, stationary-drift, route-distance, screen-off, background, notification, pause/resume, or process-death PASS is claimed. Preserve the installed Play app and any unknown live session.

## Map stack and Google Maps owner gate

- The in-app map remains Leaflet in the local WebView with attributed OpenStreetMap streets, OpenTopoMap terrain, and EOX Sentinel-2 cloudless 2016 satellite/hybrid layers.
- Google Maps remains an external directions handoff, not the native in-app basemap.
- The 2026-11-09 implementation review rejects Google Maps Rx: its archived/deprecated RxJava adapter is not a location provider, GPS accuracy, or synchronization solution.
- The latest owner Maps preflight remains run `41684077962` (2026-11-03): Maps Android Backend and API Keys APIs enabled; key-inventory permission denied; no package/SHA-restricted Android key visible; no billing account linked.
- No billing, payment method, key, secret, paid infrastructure, or permission retry was performed. Native Google basemap, traffic, and transit remain owner-gated.

## Remaining acceptance gates

1. Restore an ADB-visible authorized device connection. Reconfirm device location state and the current session without installing or stopping anything.
2. After the existing activity is safely idle, run physical P0: stationary 60-second drift, measured walk/run/cycle route, first-fix latency, accuracy/jump review, pause/resume/stop, notification actions, background/screen-off, and process-death recovery.
3. Meet the owner billing/key prerequisite before any native Google Maps SDK key creation. Then use Android package plus signing-certificate SHA restrictions and API restrictions before implementing native basemap/traffic/transit.
4. Keep PR #284 Draft and unmerged until the device P0 and owner Maps gates are satisfied.

## Scope and release boundary

No Health/anti-cheat or exercise-catalog files, release version, workflow, signing, billing, secret, or Play files were changed. VersionCode 51020 remains unallocated. No APK was installed on the phone, no AAB was signed or uploaded, and no Play status was changed.
