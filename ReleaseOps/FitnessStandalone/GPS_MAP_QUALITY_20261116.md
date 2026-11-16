# TopHeroFit GPS / Maps quality checkpoint — 2026-11-16

Scope: TopHeroFit Activity Engine, GPS quality, Maps readiness, session persistence and safe QA only.
Canonical repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical base at exact-head validation: `fbb63025ef0d6dbfe22c7661b049a4b72da2b5a0`.

## Selected GPS handoff
- PR #297: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297
- Branch: `agent/codex/gps-permission-downgrade-20261116-r1`.
- Exact PR HEAD after canonical rebase: `1c099845979a998dc0d374322f471c39400e566e`.
- Compare: 8 commits ahead / 0 behind; exactly eight GPS source/test files; no Health, app.js, MainActivity, manifest, workflow, release or signing files.
- Rebase used force-with-lease from old head `d572bae1baea0ea01fdca91d39cc089a30378e90` onto canonical `fbb63025ef0d6dbfe22c7661b049a4b72da2b5a0`.
- PR remains Draft; do not merge until physical P0 and release/privacy gates pass.

## Exact-head CI and artifacts
[Run 43923207674](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43923207674) completed SUCCESS on exact PR HEAD `1c099845979a998dc0d374322f471c39400e566e`.
- Product tests: 67/67.
- Source-contract tests: 34/34.
- Backend tests: 29/29.
- Android unit tests: 273/273; 0 failures; 0 ignored.
- Android API 36, Kotlin compilation, lintDebug, assembleDebug and unsigned bundleRelease validation: PASS.
- Lint: 0 errors, 16 warnings, 1 hint.

Artifact 14253604668 was downloaded and independently rehashed:
- ZIP SHA-256: `58c87c1a0ebf5d5a606375fee5a56aad2cf39ef2accd02f068ae8b8b199cc1aa`.
- QA APK SHA-256: `65cdf02aade50cb3916932e9af8187dd13ea5e21e38fe997ee795dcc3b283d98`.
- Validation AAB SHA-256: `6e9d73ecf9a50838e17a7c3551f41931d21684d3e1c2af7dc443f5412250dfdc`.
- `jarsigner -verify` reports `jar is unsigned`.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. Validation only; never promote.

## GPS/provider behavior
- Fused Location Provider remains primary, with one permission-eligible Android framework fallback provider.
- GPS_PROVIDER requires fine permission; coarse-only permission selects NETWORK_PROVIDER.
- If Android 12+ downgrades precise to approximate while GPS is active, the four-second watchdog switches to eligible NETWORK_PROVIDER immediately instead of waiting for the normal 12-second no-fix timeout.
- The fallback fails closed when coarse permission or NETWORK_PROVIDER is unavailable.
- Provider switches unregister the old provider and invalidate the previous source's live anchor/accumulator; no distance is bridged across providers.
- Bounded 8-second initial fallback, 12-second stale/no-fix fallback, retry backoff and generation guards prevent late Fused callbacks from reviving paused/stopped/replaced sessions.
- A live fix gap beyond 30 seconds clears the stale speed/distance anchor; activity and route history remain, but unobserved distance is not bridged.
- GPS presentation separates permission, device location switch, stale signal, filtered fix, accepted source, accuracy and paused state.

## Filtering and anti-cheat boundary
- GpsFixGate rejects mock/invalid coordinates, poor accuracy, stale/non-monotonic timestamps and sport-speed violations.
- GpsDistanceAccumulator enforces source continuity, re-anchors on provider change or long gap, uses endpoint-accuracy deadband, requires persistent threshold-crossing excursion and caps path inflation.
- `ActivityEvidenceAnomalyPolicy.assessSegment` exists and has tests but is not called by `ActivityTrackingService`. Do not claim full anti-cheat, cryptographic device/location attestation or reward eligibility.
- Passing source-level tests do not establish real GPS accuracy, genuine movement or physical device provenance.

## Session persistence/background boundary
- Source contains a Foreground Service, START_STICKY, local checkpoint every 10 seconds, ongoing notification and Pause/Resume/Finish controls.
- Restored route history is display/history only; only a fresh monotonic checkpoint may seed a live speed anchor. Stale anchors are cleared.
- Physical screen-off/background, notification controls, process-death restore and real movement tests remain BLOCKED_NOT_RUN.

## Maps stack
- Leaflet in Android WebView.
- OpenStreetMap street tiles, OpenTopoMap terrain and EOX Sentinel-2 cloudless 2016 imagery.
- WebView `LOAD_DEFAULT` is ordinary browser cache, not a guaranteed offline tile package.
- Tile providers have attribution and usage policies; free endpoints are not unlimited bulk/offline hosting.
- No Google Maps SDK, billing, API key, native traffic or transit overlay is used or claimed. Google directions is an optional external handoff.

## Separate route-sync gap
- Finished route history remains in WebView localStorage.
- Existing authenticated workout sync sends workout/set metadata only; no authenticated route endpoint or cloud route backup/restore exists.
- `ROUTE_SYNC_DESIGN_20261110.md` remains design-only with separate summary/precise-route consent, per-session opt-in, retention, deletion and revocation. No precise-location upload by default.

## Physical device and release gates
- Desktop Commander `localhost`: OFFLINE; last seen about 151 hours at the 2026-11-16 check.
- Last known handset: Samsung SM-A217F / Android 12. Current device/session state is unknown.
- No ADB, install, launch, Stop, settings or activity-data action was attempted.
- Physical P0 remains BLOCKED_NOT_RUN: stationary 60-second drift, measured walk/run/cycle, precise-to-approximate permission downgrade, first-fix latency, screen-off/background, notification Pause/Resume/Stop and process-death recovery.
- Latest read-only Play probe attempt 2 completed 2026-11-16 17:56:42Z: Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified. Upload and commit attempts were false. No Play mutation.
- VersionCode 51020 remains unallocated. No release signing, AAB upload, Play track mutation or Production promotion.