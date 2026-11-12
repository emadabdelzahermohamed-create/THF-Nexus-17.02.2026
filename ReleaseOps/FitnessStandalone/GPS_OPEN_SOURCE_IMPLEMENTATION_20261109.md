# TopHeroFit — open-source map and location implementation

Date: 2026-11-09
Canonical base: 9b5db58e809fa7d5e639bc4ee55df03d100467e8
Candidate branch: agent/codex/gps-open-source-stack-20261109

## Decision

Do not add Google Maps SDK, Google Maps Rx, or a new native map renderer as a prerequisite for fixing GPS.

The current activity map is already rendered by Leaflet in the local WebView and uses OpenStreetMap-derived raster layers (OSM streets, OpenTopoMap terrain, EOX satellite/hybrid). Leaflet is an open-source renderer. The Google Maps URL is an optional external directions handoff, not the in-app map renderer. A MapLibre Native migration is possible later if vector styling/offline packages become a demonstrated product need, but it is not necessary to fix location acquisition, tracking accuracy, or route persistence and would add a large native integration surface now.

## Location architecture

- Keep Fused Location Provider as the preferred source when Google Play services is present. It is free to use for this app flow and does not require a Google Maps API key or Maps billing.
- Do not assume a successful Fused Location Provider subscription guarantees callbacks. Add a bounded watchdog: if no accepted fix arrives within 8 seconds, or the last accepted fix becomes 12 seconds stale, register Android framework LocationManager GPS and network providers as a fallback.
- Keep fallback registration idempotent, stop Fused updates after the framework fallback is successfully registered, and remove the watchdog on pause, finish, or service destruction.
- Keep the existing accuracy, monotonic timestamp, mock-location, speed/jump, movement-activation and distance-accumulation gates. Do not use map display smoothing for metrics.
- Show accepted accuracy only while the GPS state is ready; missing accuracy must remain unavailable, not become a false 0 m. A paused session must explicitly report paused and clear stale accuracy.
- This fallback improves resilience when the fused subscription is silent. It cannot make a weak satellite signal accurate, defeat device power management, or replace physical walk/run/cycle tests.

## Map and tile-source policy

- Keep Leaflet and OSM-derived sources for now; no Google Maps SDK key or billing is needed for the in-app route map.
- Keep visible source attribution and use a distinct, stable TopHeroFit User-Agent with the support contact. WebView uses LOAD_DEFAULT caching so normal HTTP tile cache headers are honoured.
- Respect each provider's caching, attribution, identification and rate limits. The public tile.openstreetmap.org service is best-effort, has no SLA, and explicitly prohibits bulk prefetch/offline tile downloads. OSM data is free/open, but its community tile servers are not an unlimited free production CDN.
- For reliable scale or offline map packs, select a provider that explicitly permits the intended use or self-host regional vector/raster tiles. Do not scrape public OSM tile servers.

## Device-level location gate observed on 2026-11-09

The connected SM-A217F has TopHeroFit 51019 installed from Google Play and the app's fine/coarse location permissions are granted, but Android secure setting location_mode is 0 (device location disabled). No app GPS accuracy test can pass while the system-wide location service is off. The app now offers a button that opens Android Location settings when it detects the disabled state; it does not silently enable a device-wide privacy setting.

## Google Maps Rx link

The googlemaps/android-maps-rx repository is officially archived and deprecated. It is an RxJava adapter for Google Maps/Places SDK events. It does not provide a location provider, GPS fusion, satellite data, accuracy filtering, route smoothing, background tracking, or synchronization. It also does not remove Maps SDK key/billing requirements. It is not part of the GPS repair.

## Candidate source changes

- Added a tested time policy for activating Android framework location fallback after a silent/stale fused subscription.
- Wired a bounded watchdog into the foreground activity service and made legacy provider registration idempotent.
- Cleared pre-pause location observations on resume and hid stale accuracy in paused/acquiring states.
- Fixed WebView UI coercion where Number(null) could be rendered as 0 m.
- Added bilingual paused GPS status and focused Kotlin/Python regressions.

## Acceptance gates

- Exact-head Android CI must pass on this branch.
- Physical P0 still required on the Samsung SM-A217F: stationary walk/run/cycle drift, first-fix latency, outdoor/open-sky and urban multipath, short-loop distance, screen-off/background, provider fallback, pause/resume, process-death recovery, and notification/map consistency.
- No versionCode allocation, signing, Play upload, or production claim is authorized by this candidate alone.
