# TopHeroFit — GPS / Map Quality Checkpoint

**Observed:** 2026-11-27T17:51:42Z  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application baseline:** `779df53146e23e76fe7b1faabffbc0e3540ee29a`  
**ReleaseOps branch tip before checkpoint:** `11f06f2554593a8d40949bdadcc142c1001fdc94`

## Latest GPS/activity candidate — PR #315

- Exact PR head: `32b2eae0558e609bd2e3c453e1af6d25bc9df406`.
- Exact base: `11f06f2554593a8d40949bdadcc142c1001fdc94`; compare 9 ahead / 0 behind.
- Exact-head workflow [45955722335](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45955722335): SUCCESS.
- Product 84/84; Source Contract 41/41; Backend 29/29; Android Unit 359/359; failures 0; ignored 0.
- Android API 36 / Kotlin / Gradle / APK / unsigned-AAB validation PASS; Gradle BUILD SUCCESSFUL.
- Lint: 0 errors, 13 warnings, 1 hint.
- Artifact 15178872128 ZIP SHA-256 `2aed93edc954a537ac9fd25101264ad5efab231a3e987021db12f68b640bcae4`, independently downloaded and rehashed.
- Embedded source marker: `32b2eae0558e609bd2e3c453e1af6d25bc9df406`.
- Debug APK SHA-256 `cff4e87ca2d3736f2d13ce21d19b1256a57fcbab5e5a65e8fd45485e26cdcff1`.
- Unsigned AAB SHA-256 `db3c94e1d655177cda8f2c40180e428440360213e795f362da9eacc34061f406`; jarsigner confirms AAB unsigned.
- CI artifact versionCode is 51019; it is not signed and was not uploaded. No version allocation.

### GPS source behavior

PR #315 carries forward the validated #311 GPS handoff and adds Android 14+ foreground-service eligibility handling:

- Fused/framework provider arbitration with monotonic cross-provider transition validation.
- Permission revoke/downgrade cleanup; same-session Fused registration can resume after permission is restored.
- Optional API 26+ speed-accuracy evidence and conservative provider-confirmed stationary re-anchoring.
- 30-second consecutive-fix continuity cap with a 120-second stable movement-anchor lifetime.
- Distance remains owned only by `GpsDistanceAccumulator`; source admission remains `GpsFixGate`.
- Android 14+ uses LOCATION only when app location permission and system-wide location are enabled; HEALTH is selected when activity-recognition permission is available; a new foreground start is refused when neither type is eligible.
- A failed process-death restore preserves the durable checkpoint.

This is exact-head CI evidence, not physical GPS accuracy, background tracking, notification or process-death device evidence. PR #315 remains Draft until physical P0.

## Map stack

- Canonical map remains Leaflet in Android WebView.
- Base layer: OpenStreetMap-derived raster tiles.
- Optional layers: OpenTopoMap and EOX Sentinel-2.
- No Google Maps SDK/Rx, billing, Google basemap or new key is required for the current stack.
- The WebView network policy allowlists HTTPS raster endpoints from OSM/OpenTopoMap/EOX.
- `WebSettings.LOAD_DEFAULT` honors provider HTTP cache headers. This is not an offline tile pack, bulk prefetch or guaranteed offline map.
- Respect each tile provider's attribution, caching and rate limits.

## PR #284 map/settings handoff

- Current head: `274155eafdfff381009ef5814a621f32b225f1a8`; 19 ahead / 179 behind current canonical branch; diverged.
- Current-head CI: absent. Historical run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) validates only historical SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; artifact 13707718861 is unavailable.
- Source-integrity check at current #284 head: MainActivity is 1,146 lines, fetched in bounded ranges; `motionSnapshot()` exists in the tail. Blob SHA-1 `9d92bc47dfe317e1739b1d952f22ac00b10c00f6`.
- `app.js` contains the location-settings button and `PulseNative.openLocationSettings()` bridge.
- MainActivity contains the unique TopHeroFit User-Agent and `WebSettings.LOAD_DEFAULT`.
- `WebViewNetworkPolicy.kt` allowlists HTTPS OSM/OpenTopoMap/EOX raster endpoints.
- `ActivityLocationFallbackPolicy.kt` specifies an 8-second first accepted-fix watchdog, 12-second stale-fix timeout and 12-second silent-GPS-to-network fallback, with one permission-eligible framework provider active at a time.
- These are source observations only. #284 overlaps PR #315 ActivityTrackingService/GPS policy, #93 MainActivity/Manifest and #216/#224 WebView ownership. Keep Draft and do not merge wholesale.

## Physical P0 — BLOCKED_NOT_RUN

Desktop Commander localhost is Offline (last seen about 248 hours before the 2026-11-27 check); SM-A217F app/session state is unknown. No ADB or device mutation was attempted.

Required:
1. Stationary 60-second drift test.
2. Measured walking, running and cycling routes against known distances.
3. Precise/approximate permission downgrade, revoke and regrant.
4. First-fix latency and accuracy, provider changes and map marker truthfulness.
5. In-app navigation and screen-off/background tracking.
6. Persistent notification Pause/Resume/Finish.
7. Process-death restore without crediting stopped time.
8. Crash, ANR and Logcat inspection.

## Separate route-sync gap

Finished GPS routes remain in WebView localStorage. No authenticated route-sync endpoint/table or precise-location upload exists. After #284 is validated, inspect the existing account/backend contract and design explicit opt-in consent, retention/deletion and no precise-location upload by default. One-second local map refresh is not route sync.
