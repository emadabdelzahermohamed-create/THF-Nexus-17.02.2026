# Top Hero Fit — GPS/Maps release checkpoint
Date: 2026-11-03 (latest evidence through 2026-11-03T17:13:48Z)
Repository: emadabdelzahermohamed-create/THF-Nexus-17.02.2026
Canonical branch: agent/codex/fitness-recovery/20261023
Canonical integration commit: 92462d59a76061b6a445b5e119ec28ca544893af

## Tested integration now canonical
- PR #264 merged as 92462d59a76061b6a445b5e119ec28ca544893af.
- Exact tested source head: 5ce141340282319723a218deafbd1f24eee2b04a.
- Exact-head Android CI: run 41681713383, SUCCESS. It passed product/source-contract/backend tests, Android unit tests, lint, debug APK, and release AAB build.
- Validation artifact 13253430826, ZIP SHA-256 70ae61660cd187c3aa054a803f26d0685a7e9ccc7cac28faf827d13f64d56240; downloaded archive hash independently matched.
- QA debug APK SHA-256 99ef0c1b23e708f98a8d9c236b0e6191ad5cd3d7246dbc9bcb115fa25dbac7ff, package com.topherofit.thf.pulse.qa, validation versionCode 51019.
- Unsigned validation AAB SHA-256 06cbb92df6daebf53bf8d9de79bd181464399ddb289583867da5c1e73d433395.
- The canonical merge tree's app/build.gradle, app.js, ActivityActivationGate.kt, ActivityTrackingService.kt, MainActivity.kt, and ActivitySessionCheckpoint.kt blobs match the exact tested candidate. Differences from the tested tree are limited to the canonical recovery/release evidence and read-only Play probe workflow.
- No signing, version allocation, Play upload, or Production promotion occurred.

## GPS and truthful metrics
- The current in-app fallback remains free: OSM street, OpenTopoMap terrain, and EOX Sentinel-2 cloudless 2016 satellite/hybrid with attribution. EOX imagery is explicitly 2016, not current; OSM/OpenTopoMap have no SLA and no offline bulk prefetch is used. Google Maps directions handoff remains available.
- The GPS/session integration uses the free map stack and Fused Location first-fix settings. Route smoothing remains display-only; raw accepted fixes drive metrics. No physical GPS accuracy improvement is claimed.
- Walk/run step activation now requires at least 4 counter steps in a 5–15 second evidence window and a plausible cadence no greater than 240 steps/min. Unconfirmed pre-activation counter noise is not credited on activation. This is a conservative gate, not proof of sensor authenticity, and has not passed physical P0.

## Google Maps SDK owner gate
- The latest GPS checkpoint records Maps SDK for Android and API Keys APIs enabled, but the release-builder cannot list keys; no restricted key exists or is stored, and no billing account is linked.
- Native Google Maps SDK rendering and Google traffic/transit overlays remain blocked. No billing, payment method, key, or paid infrastructure was changed. Continue the free map stack until owner API/key prerequisites are satisfied without violating the no-paid-infrastructure constraint.

## Independent Play readback
- Read-only publication probe run 41681987871, artifact 13254035412, archive SHA-256 2d99e956ce16f0e3a46dd24e646aa8105b4fc97765f5a0e596fd0322d897cb90; downloaded hash independently matched.
- Package com.topherofit.thf.pulse: Internal 51019 is completed; alpha 51007 remains draft. Production was not listed in the readback. uploadAttempted=false and commitAttempted=false.
- The listing still claims GPS/background tracking and estimated metrics. No listing edit was made; those claims remain subject to physical P0 and policy/privacy gates.

## Physical and release boundary
- Authorized Desktop Commander device is OFFLINE, last seen about 30 hours before this recheck. The last phone observation remains 2026-11-01T21:24:32Z, with a foreground tracking service and an active/ambiguous session; current session state is unknown.
- No ADB command, install, launch, Stop, session action, or activity-data read was performed. Physical P0 remains BLOCKED_NOT_RUN.
- Keep versionCode 51020 unallocated. The next release code must be greater than 51019 and may be allocated only after owner API/key prerequisites, exact-head Android CI, and physical P0 pass. Production remains NOT_VERIFIED until policy/privacy and physical gates pass.
