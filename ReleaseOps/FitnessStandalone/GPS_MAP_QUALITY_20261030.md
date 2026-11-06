# Top Hero Fit — GPS and activity map quality checkpoint

Date: 2026-10-30 (Africa/Cairo)
Base: canonical Play 51019 source lineage `agent/codex/fitness-recovery/20261023`
Base SHA: `4e207c7de988372f5922924ccac49ade212c8a0b`
Package: `com.topherofit.thf.pulse`

## Device facts observed over ADB
- Device: Samsung SM-A217F (Galaxy A21s).
- Installed package: versionCode `51019`, versionName `5.0.0-v2-alpha19`, targetSdk `36`.
- Fine and coarse location runtime permissions were granted to the current Android user.
- The system-wide location master switch was **off** (`cmd location is-location-enabled --user 0` returned `false`; `dumpsys location` showed user 0 disabled and GPS/network/fused providers off).
- The master location switch was enabled with `cmd location set-location-enabled true --user 0`; subsequent `cmd location is-location-enabled --user 0` returned `true`, and providers were enabled.
- The last available network/fused location was approximately nine days old and is not valid evidence of a current fix. GNSS report/TTFF counters were zero at the observation point. No fresh satellite fix was claimed.
- Wireless ADB later disconnected; `adb connect 192.168.8.6:37855` returned connection refused. Physical UI/runtime QA is therefore pending.

## Source findings
- The app already uses `FusedLocationProviderClient`, high-accuracy location requests, a foreground location service, mock/stale/speed/accuracy gates, and a persisted activity checkpoint.
- The activity map was not a Google map or a map tile layer: it was a dark SVG grid with a route polyline. It could not show streets, landmarks, or a usable geographic context.
- The canonical source includes the stricter GPS movement deadband based on the worse endpoint accuracy radius (the GPS drift regression from PR #158).
- The map provider is not configured with a Google Maps API key in this source tree or local configuration.

## Implemented on this branch
- Live location requests now disable batching (`setMaxUpdateDelayMillis(0L)`), reject cached initial fixes (`setMaxUpdateAgeMillis(0L)`), and wait briefly for a more accurate initial fix (`setWaitForAccurateLocation(true)`). This is appropriate for real-time outdoor activity tracking; power use still needs physical-device measurement.
- Replaced the placeholder-only map with a vendored Leaflet 1.9.4 interactive map using OpenStreetMap raster tiles and required attribution. Leaflet source/license are included locally; only map tiles require connectivity.
- Added route halo/line, start/current position markers, accuracy radius, automatic route fitting/following, user-pan preservation, and a recenter control.
- Preserved the SVG route fallback for offline/no-library cases.
- Added a Google Maps handoff link for the latest route point; Android now opens only the whitelisted Google Maps URL externally.
- Added source-contract tests for the map and the latency/accuracy request settings.

## Google Maps Platform constraint
Google's official Maps SDK for Android and Maps Embed API setup require a valid API key and a Cloud Billing account. The Embed API is documented as unlimited/free usage but still requires billing setup and a key. No Maps key or usable local Google Cloud CLI/configuration was found during this run. The current in-app map therefore uses the no-key OpenStreetMap tile service rather than falsely presenting the SVG or an unconfigured Google map as Google Maps. A restricted Google Maps key can be added later if the owner wants the Google basemap; key restrictions must include only the needed Maps API and the Android package/signing certificate for native SDK use.

## Verification boundary
- `node --check` on the activity UI: PASS.
- GPS source contract tests: PASS.
- Activity map source contract tests: PASS.
- `git diff --check`: PASS before the final documentation-only pass.
- Android Gradle build not run locally: no `gradle` executable or Android SDK configured in this Termux environment.
- No physical outdoor GPS, route accuracy, background/screen-off, battery, map tile, or external Google Maps launch PASS is claimed. ADB disconnected before the manual QA preflight could run.
- This is a source branch only; no version code allocated, no APK/AAB built, and no Play upload performed. Any next release must be greater than 51019 and pass exact-SHA CI and physical QA.

## Required physical QA when ADB is restored
1. Confirm system Location is on, app Precise location is allowed, Google Play services is available, and the device has an unobstructed outdoor sky view.
2. Start Walk while stationary; wait at least 60 seconds. Distance/pace/calories must remain zero and the session must remain ARMED.
3. Walk a measured 300–500 m route; compare GPS route/distance with a trusted reference and inspect fix accuracy and speed for jumps.
4. Repeat for Run and Cycle; validate sport-specific speed ceilings and movement activation.
5. Pause/resume, navigate to another screen, lock screen, return, and stop/save. Confirm route/session recovery and persistent notification.
6. Test map tile failure/offline state, recenter, pan/zoom, Google Maps handoff, and RTL/LTR layout.
