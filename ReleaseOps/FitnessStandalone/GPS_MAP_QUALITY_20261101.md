# Top Hero Fit — GPS / Maps execution checkpoint

Date: 2026-11-01 (Africa/Cairo)
Branch: `agent/codex/gps-map-quality-20261030`
Checkpoint base: `d37ad669ead851231bfced58d3dea1d34852d38a`
PR: [#215](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/215)
Package: `com.topherofit.thf.pulse`
Current release baseline: Play Internal 51019; next release identity must be >51019.

## Verified source implementation
- Fused Location Provider uses high accuracy, disables batched delivery, rejects cached initial fixes, and waits for an accurate fix.
- Weak fixes are visible diagnostically but are not accepted into the route; stale/mock/speed/accuracy and movement-integrity gates remain in place.
- A persistent foreground tracking service and durable activity checkpoint are present in source.
- The previous placeholder SVG map was replaced by a Leaflet map using attributed OpenStreetMap tiles, with route halo/line, start/current markers, accuracy radius, fit/follow, pan preservation, recenter, and an external Google Maps handoff. This is NOT the Google Maps SDK or Google basemap.
- Offline SVG fallback remains available.

## Tests executed 2026-11-01 on the connected Termux environment
- `python3 -m unittest discover -s fitness-v2/tests -v`: PASS, 50 tests.
- `python3 -m unittest discover -s fitness-v2/product/tests -v`: PASS, 60 tests.
- `python3 -m unittest discover -s fitness-v2/backend/tests -v`: PASS, 15 tests.
- `node --check fitness-v2/android/app/src/main/assets/pulse/app.js`: PASS.
- Total: 125 Python tests PASS + JavaScript syntax PASS.
- Android Gradle build was not run locally (no Android SDK/Gradle toolchain in Termux). Prior CI build run [41117472955](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/41117472955) passed for older SHA `e0d5b64501cd0a8ca337733fd66afe9cc31b6d95`, versionCode 51019; artifact `13005344643`, digest `sha256:60f79bd68720c44bc2a57270e6de1e6685c2965276459c7960d9483d0a34b2ba`. This is validation evidence only, not a new release.

## Google Maps SDK blocker
- The enablement workflow authenticated to the existing THF Cloud project and confirmed project identity.
- Workflow run [41119539583](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/41119539583) failed at enabling `maps-android-backend.googleapis.com` because the existing release-builder service account lacks `serviceusage.services.enable`.
- No billing configuration was read or changed, no billing account was linked, and no API key was created.
- Owner action: enable [Maps SDK for Android in the existing project](https://console.cloud.google.com/apis/library/maps-android-backend.googleapis.com?project=project-b5e10d7e-8ce8-4aa4-a15), OR grant `roles/serviceusage.serviceUsageAdmin` to the existing release-builder service account on this project and rerun the workflow.
- After API enablement, provision a restricted Android API key for package `com.topherofit.thf.pulse`, using the Play **app-signing** SHA-1 (not the upload-key SHA-1). Store the key in GitHub/Secret Manager; never commit it.

## Physical QA blocker
- The local ADB inventory currently returns no attached devices.
- The last recorded wireless debugging endpoint `192.168.8.6:37675` refused connection; current mdns discovery is unsupported by the installed ADB binary.
- No new physical-device GPS fix, Google basemap rendering, measured route accuracy, background/screen-off session continuity, battery, or crash/ANR PASS is claimed.
- Once ADB is paired/connected, run stationary 60-second false-movement test, measured 300–500 m walk/run/cycle route, accuracy/jump inspection, screen-off/background/navigation recovery, pause/resume/stop, notification, and map layer/recenter/offline tests.

## Release decision
HOLD. Do not allocate 51020, merge #215, or upload to Play until the Google Maps key is securely provisioned, exact-head Android CI is green, and physical P0 GPS/session QA passes. Production remains unverified.
