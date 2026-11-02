# Top Hero Fit — GPS, Maps and Phone QA checkpoint

Date: 2026-11-01 (Africa/Cairo)
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
Working branch: `agent/codex/gps-map-quality-20261030`
PR: [#215](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/215)
Android package: `com.topherofit.thf.pulse`
Installed Play baseline: `versionCode 51019`
Next release versionCode: must be greater than 51019; do not allocate until all release gates pass.

## Confirmed Google Cloud state
- `maps-android-backend.googleapis.com` (Maps SDK for Android) is ENABLED. Verified by the read-only GitHub Actions preflight.
- `apikeys.googleapis.com` (API Keys API) is ENABLED. Enabled from the existing THF project in Cloud Console; no billing settings were touched.
- Google Cloud Console's Maps Platform credentials flow explicitly prompts to select/link a Google Maps Platform billing account for this project. No billing account was linked, no payment method was added, and no chargeable configuration was changed.
- The release-builder service account cannot list API keys (`apikeys.keys.list` permission denied). No Google Maps API key has been created or stored.
- Therefore native Google Maps SDK rendering and Google traffic/transit overlays are NOT ready. Do not claim they are.
- The app's external Google Maps directions handoff remains available and does not require the in-app Maps SDK key.
- Free Google Maps SDK usage still requires a billing-enabled project. Do not link a billing account or add a payment method without explicit owner approval.

## Implemented free in-app map layers
The activity map now offers four real selectable base styles:
1. Street: OpenStreetMap standard raster tiles.
2. Terrain: OpenTopoMap raster tiles.
3. Satellite: EOX Sentinel-2 cloudless 2016 imagery, explicitly labelled with its 2016 vintage.
4. Hybrid: EOX 2016 satellite imagery plus transparent EOX streets overlay.

Attribution is shown in the Leaflet map control:
- OSM: © OpenStreetMap contributors.
- OpenTopoMap: map data © OpenStreetMap contributors, SRTM; map style © OpenTopoMap (CC-BY-SA). Its official page permits commercial use with attribution/share-alike, but provides no uptime SLA and asks users not to overload its volunteer service.
- EOX 2016 Sentinel-2 cloudless layer: current WMTS capabilities identify CC BY 4.0 and require attribution to EOX IT Services GmbH and modified Copernicus Sentinel data 2016.
- EOX streets overlay: data © OpenStreetMap contributors; rendering © EOX IT Services GmbH and MapServer.

Operational constraints:
- OSM standard tile server is best-effort, has no SLA, requires a stable app-identifying User-Agent, normal HTTP caching, visible attribution, and prohibits prefetch/offline bulk downloads.
- OpenTopoMap is a community service with no SLA; do not bulk-download or prefetch.
- EOX imagery is from 2016 and must not be represented as current imagery.
- No in-app live traffic layer is supplied by these free sources.

## WebView network hardening and tile delivery
- WebView external HTTP(S) requests are allowed only for exact approved HTTPS map tile hosts and tile paths: OSM, OpenTopoMap a/b/c, and EOX s2cloudless/streets WMTS layers.
- All other external HTTP(S) subresources are intercepted and blocked; file/data resources remain local.
- The User-Agent identifies TopHeroFit with the app version; cache mode explicitly remains LOAD_DEFAULT.
- Map controls are compact for phone viewports; zoom and scale controls remain available.
- Google Maps handoff now opens route directions from first to last recorded point (walking or bicycling), not only a single-point search.

## Verified source and endpoint checks
- Python source tests: 50 PASS.
- Product/catalog tests: 60 PASS.
- Backend tests: 15 PASS.
- JavaScript syntax check: PASS.
- Git diff whitespace check: PASS.
- Live tile endpoint smoke checks from the connected phone environment: 4/4 HTTP 200 (OSM street, OpenTopoMap terrain, EOX 2016 satellite, EOX streets overlay).
- New Kotlin unit tests cover exact tile host/path allowlisting, HTTPS-only behavior, lookalike-host rejection, and external resource blocking. They still require the Android CI run to confirm compilation/execution.
- Prior Android CI build attempt found and caught a Kotlin WebResourceResponse constructor incompatibility; this was corrected to the API 21+ six-argument constructor. The corrected exact-head CI run is required before any install/release decision.

## Physical-device state and safety
- ADB wireless connection is restored and the Samsung phone is visible.
- Installed Play app identity is `com.topherofit.thf.pulse`, versionCode 51019.
- A native foreground workout service/session was active/restored when the app was launched. It was deliberately not stopped, reset, or overwritten.
- Because a live workout was present, no new GPS test activity was started and no APK was installed over the Play app. This avoids losing the user's current session/data.
- No physical route accuracy, stationary drift, screen-off GPS continuity, or map-layer UI PASS is claimed yet.
- Once the current workout is safely ended by the user, run the phone P0 suite: stationary 60s drift, measured 300–500m walk/run/cycle, GPS accuracy/jump review, background/screen-off, pause/resume/stop, notification, map layer switching/recenter, and network/offline behavior.

## Release decision
HOLD — not Play-ready.
- Do not upload a new AAB, merge the release PR, or allocate 51020 until exact-head Android CI passes and the physical P0 phone suite passes.
- Google Maps native SDK remains blocked by the billing-account requirement. Continue with the no-billing map stack unless the owner explicitly authorizes linking an existing billing account.
- No billing account/payment method was added, no API key was created, no versionCode 51020 was allocated, and no Play upload was made.

## Scheduling
Automations support recurring schedules only at daily, weekly, or monthly cadence. The three independent THF tracks are kept on daily schedules (GPS/phone QA, Health/exercise, and integration/Play). Hourly or per-second recurring schedules are not supported; do not create duplicate retry loops.


## Follow-up — 2026-11-02 08:23 Cairo

### Bounded route-line smoothing (display only)
- Source/test commit: \`3f7fbb71c912c0a088990bcf3506e7cbb2301edf\` (code commit \`05085a2b5f19847ceff37f7453b53a4735e723f3\`).
- The map route line now applies a bounded, timestamp-weighted correction to small lateral jitter between already accepted fixes. It preserves endpoints and sharp turns, skips poor-accuracy/non-monotonic/stale-gap triples, caps shifts at 3 m (and at half the reported accuracy), and handles longitude wrap.
- The smoothing output is used only for the Leaflet/SVG route stroke. Raw accepted points still drive distance/speed/pace/calorie metrics, the Google Maps directions endpoints, the current marker, and the accuracy circle. This is a display-quality improvement, not a claim that the underlying GPS measurement became more accurate.
- Verification on the exact source commit: full \`app.js\` parse PASS; deterministic route-smoothing harness 13/13 assertions PASS (bounded jitter, immutable input/evidence, endpoints, corners, stale gaps, accuracy ceilings, uneven timestamps, short routes, and date-line normalization); persisted Python test method syntax PASS.
- Exact-head Android CI was not rerun. The commit has no combined status checks; the only associated workflow run returned is unrelated \`THF No Arbitrary Artifact Size Cap V1\` run \`41400025755\`. Do not treat that run as Android CI or build evidence.

### Current blockers and release boundary
- Desktop Commander reports the authorized \`localhost\` device OFFLINE (last seen about 1 hour ago). No ADB command, install, launch, session action, or physical GPS test was performed in this run. The latest device observation remains the 2026-11-01 21:24Z checkpoint; it is not a fresh session-state read.
- Google Maps SDK and API Keys APIs remain enabled, but no billing account is linked and no API key exists. The owner billing prerequisite is unmet; no credential or billing change was attempted. Native Google traffic/transit layers remain unavailable in the current no-billing stack.
- No versionCode, release workflow, signing, Play state, Health/anti-cheat, or exercise catalog files were changed. Physical P0 and release gates remain HOLD.
