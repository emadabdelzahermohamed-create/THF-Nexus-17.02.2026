# TopHeroFit GPS / Map Quality — canonical checkpoint 2026-11-18

## Exact tested candidate

- PR #297 branch `agent/codex/gps-permission-downgrade-20261116-r1`.
- Exact candidate HEAD `f741af0dccd48dbcf258f5ae5b1d23e0db58f3af`.
- Canonical application base `7dc57dd9f6e647797cbbe2d1cfdb45773410a866` (includes merged Health metric guard #301).
- Compare: 11 ahead / 0 behind; exactly 14 GPS Activity Engine source/test files plus two candidate docs (16 total). No `app.js`, Health, MainActivity, Manifest, release, version, workflow, signing or Play source changes in the GPS diff.
- Exact-head run [44358671462](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44358671462) SUCCESS: Product 69/69, source-contract 34/34, backend 29/29, Android 304/304, 0 failures/0 ignored, API 36/Kotlin/lint/assembleDebug/unsigned bundle validation PASS.
- Artifact 14452564181 ZIP SHA-256 `1fe20c29953a629f35d93413473345ae67ddc3414f8b071d335e25701d309609`; APK SHA-256 `d471438d8ce89454a24ab6cd8d8f802ae58c2e270c1ca93f3a01e7478d8cf77f`; AAB SHA-256 `670d09313a87daf64ffa6dfe2dcd825fc6a7f8e9a7232c6eaf7f73eb93316082`.
- ZIP and embedded artifact hashes were independently checked. Debug APK package is QA-suffixed; release-validation AAB package ID is production `com.topherofit.thf.pulse`, versionCode 51019, unsigned and not a release. No signing/upload.

## Native GPS behavior

- Fused primary; permission-aware single framework fallback. Fine permission selects GPS_PROVIDER if enabled; coarse-only selects NETWORK_PROVIDER. Precise-to-approximate downgrade is detected.
- Provider changes invalidate the prior distance anchor. Late callbacks are guarded so paused/stopped/replaced sessions are not revived.
- Fix validation rejects mock, invalid, stale/future, non-monotonic, poor-accuracy and implausible-speed fixes.
- Distance accumulator uses uncertainty deadband, persistent displacement, bounded path/net ratio and source re-anchoring. It reduces jitter but cannot prove authenticity or prevent prolonged stationary drift without physical testing.
- V3 checkpoint stores phase, wall/monotonic clocks, boot identity and bounded route; it must not credit process downtime.
- Foreground service, START_STICKY, ongoing notification, Pause/Resume/Finish actions and periodic local checkpoint writes are present. Physical screen-off, notification taps and process-death restore remain unverified.

## Map stack

- Leaflet in WebView.
- OSM street tiles.
- OpenTopoMap terrain.
- EOX Sentinel-2 cloudless 2016 satellite.
- EOX hybrid.
- Browser cache is not a guaranteed offline tile package. No native Google Maps SDK, billing, API key, traffic or transit layer is used or claimed.

## Shared UI gap

The current `renderActivity()` status labels any `gpsFixState=ready` as “GPS”, even though the accepted fix can be Fused or NETWORK_PROVIDER. It also does not explicitly show `snapshot.paused` in the status line. A minimal `app.js` fix should show “Location” (not GPS) and a distinct paused state. Keep it in a dedicated line-range lease: #284 also touches map/pause copy, #216 owns active-workout/session hunks and #224 owns demo-motion hunks. Do not edit or merge the whole file without combined-head CI.

## Separate route-sync gap

`persistFinishedActivity()` stores finished route points in WebView localStorage. `BackendSyncRepository` sends only authenticated workout/set metadata to `/api/v2/workouts/sync` and reads `/api/v2/workouts?limit=200`; AppDeploy `android_v2_routes.ts` has a strict workout-field allowlist and no route endpoint/table. The route-sync document remains design-only. No coordinate upload, backup or cloud restore exists. Keep precise-route upload off by default and require separate account/per-session consent, retention, revocation, deletion and privacy/security gates.

## Physical P0

BLOCKED_NOT_RUN. Desktop Commander localhost OFFLINE, last seen ~31h before 2026-11-18 19:29 Cairo. Last known device SM-A217F / Android 12. Current session unknown; preserve it. No ADB, install, launch, force-stop, Stop, setting change or activity-data read. Outdoor reference routes, stationary drift, permission downgrade, screen-off/background, notification actions and process-death recovery are not PASS.

## Decision

PR #297 remains Draft/unmerged until physical P0. PR #284 current head `274155eafdfff381009ef5814a621f32b225f1a8` has no exact-head CI; its requested historical run 42694452852 validates only historical head `3fcbe6acbb4dc660284c74c8392818996e1de7ee`. VersionCode 51020 remains unallocated. No release signing or Play mutation.
