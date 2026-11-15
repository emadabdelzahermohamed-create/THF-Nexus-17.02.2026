# TopHeroFit GPS / Maps quality checkpoint — 2026-11-15

## Selected native GPS handoff

PR #294: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/294

- Branch: agent/codex/gps-location-state-honesty-20261114-r1
- Tested head: 71364e31f4f631dc2593f38b15a8b92626aacdfe
- Canonical parent at test time: a8692a06ff93a7bb1b293f9eac986402f3f020c6
- Compare: 1 ahead / 0 behind; exactly eight native GPS source/test files; PR remains Draft.
- Exact-head run 43739798192: SUCCESS.
- Product 67/67; source-contract 34/34; backend 29/29; Android 270/270; 0 failures / 0 ignored.
- Android API 36, lintDebug, assembleDebug and bundleRelease validation PASS; lint 0 errors, 16 warnings, 1 hint.

Artifact 14171273756 was downloaded and rehashed:
- ZIP: 2c240ae85e192cea642b85979573e2f1936b9c88a4abb986ac55921d389bff53
- QA APK: cc1a54f8cfea54fe7651ce70c33e7d92028f9f4bc514c4d55c807b36b2257bce
- Validation AAB: f082889f60b80d3103fe1d3d8a419f4d8c7d8711b803b11a05b44b4f9a033f99
- AAB unsigned; QA package com.topherofit.thf.pulse.qa, versionCode 51019. Never promote this artifact.

## GPS behavior in the selected handoff

- Fused Location Provider is primary, with Android LocationManager fallback.
- One framework provider is selected: GPS when eligible/enabled, otherwise network when permission/provider eligibility allows.
- Fallback watchdog and retry policy are bounded; generation guards prevent late Fused callbacks from reviving a paused/stopped/replaced session.
- Restore preserves activity and historical route, but only a fresh checkpoint point within the 30-second monotonic window may be used as the live speed-gate anchor.
- A live fix gap beyond 30 seconds clears the stale anchor and accumulator; the next fix starts a new measurement window. The activity and historical route remain, but no distance is bridged across the gap.
- GPS status separates permission, device location switch, stale signal, filtered fix, accepted source, accuracy and paused state.

## Active filtering and anti-cheat boundary

- GpsFixGate checks mock flag, coordinate validity, accuracy, monotonic freshness and sport-specific speed.
- GpsDistanceAccumulator enforces source continuity, re-anchors on provider change or a gap beyond 120 seconds, uses endpoint accuracy deadband, requires a persistent threshold-crossing excursion and caps path inflation at 1.4x net displacement.
- ActivityEvidenceAnomalyPolicy.assessSegment exists and is tested but is not called by ActivityTrackingService. Do not claim this separate policy is active or that GPS proves a genuine activity.
- No cryptographic device/location attestation exists. Physical GPS and wearable P0 remains mandatory.

## Historical #284 checkpoint

Run 42694452852 passed on historical head 3fcbe6acbb4dc660284c74c8392818996e1de7ee. Artifact 13707718861 was downloaded and rehashed:
- ZIP ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c
- APK 08a5730096d1cfc97193e47726f90e533f89d9e0cc3c606faae467b46e72e9b5
- Unsigned AAB 08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e
- Android 223/223, 0 failures / 0 ignored.
- This is historical, not current #284 head evidence.

The failed 42694199295 log confirms the source-contract test saw a truncated MainActivity input ending at the 1,000-line limit. Current #284 MainActivity.kt was fetched in two ranges: 1,000 + 146 lines = 1,146; motionSnapshot is present.

Current #284 head 274155eafdfff381009ef5814a621f32b225f1a8 is 19 ahead / 49 behind canonical and has 13 changed files. It has no exact-head CI. Keep Draft and do not merge wholesale because it overlaps #294 ActivityTrackingService, #93 MainActivity/source-contract and #282/#216 app.js.

## Maps stack decision

- Leaflet in Android WebView.
- OpenStreetMap street tiles, OpenTopoMap terrain and EOX Sentinel-2 imagery.
- WebView cache mode LOAD_DEFAULT is browser cache, not a guaranteed offline tile package.
- No Google Maps SDK, billing, key or archived Google Maps Rx dependency.
- Raster tile providers have attribution and usage policies; do not treat free tile endpoints as unlimited bulk/offline hosting.

## Session persistence and physical gate

Foreground service, START_STICKY, local checkpoint every 10 seconds, ongoing notification and Pause/Resume/Finish actions exist in source. No phone-level background/screen-off/process-death pass is claimed.

Desktop Commander localhost is offline; last seen about 126 hours before the 2026-11-15 19:12 Cairo check. Last known device: Samsung SM-A217F / Android 12. Current device/session state unknown. No ADB, install, Stop or device-setting action was performed. Physical stationary-drift, measured-route, background and process-death P0 remains BLOCKED_NOT_RUN.

## Separate route sync gap

Finished route history is stored in WebView localStorage; existing authenticated workout sync does not send GPS coordinates. No authenticated route endpoint or cloud route backup exists. ROUTE_SYNC_DESIGN_20261110.md remains design-only with separate summary/precise-route consent, per-session opt-in, retention, deletion and revocation. No precise-location upload by default.
