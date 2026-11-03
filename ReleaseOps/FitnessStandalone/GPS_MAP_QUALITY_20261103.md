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

## Evidence refresh — 2026-11-03T17:40:52Z
- Current canonical app-source SHA is `7bdf52e260f741889fa85e5699a038a307acb285` (PR #117 merge). Canonical branch HEAD at this observation is `2994f3015af8769e9e9ebfaa766f3c0e8442e943`; intervening commits after the app-source SHA are evidence/workflow-comment only, with no app-source changes.
- Candidate build run [41684206709](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/41684206709) passed on exact app-source SHA `7bdf52e260f741889fa85e5699a038a307acb285`: product/source/backend checks, Android unit tests, lint, debug APK and unsigned AAB build. Artifact 13254807503 ZIP SHA-256 `3317fdfbf7136713ee4776d6cbb9a4b161965db12589862ef52ce7ad7952cab0` was downloaded and independently matched. QA APK SHA-256 `bacba395c94823081aa2d214887f298ce454b4b1df55a704ee216deb71eda94f`; unsigned AAB SHA-256 `bd0d8504025a0cc07a38271abd50f1b47c76f0ad4807fa5fe9a380077d632333`; validation identity only, versionCode 51019, package `com.topherofit.thf.pulse.qa`.
- The run 416842 AAB SHA is byte-identical to the earlier exact-head PR #117 validation AAB from run 41683629360. This was an automatic post-merge validation rebuild, not a new release artifact; no signing or upload occurred. Do not repeat a build for unchanged bytes.
- Latest Maps preflight [41684077962](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/41684077962), source head `150d9ea001bab6e8970f22ba9f21e69f3ea595a7`, completed successfully at 17:25:55Z. Maps Android Backend and API Keys APIs are enabled; key listing is permission-denied; the Maps key secret is missing/not visible to the builder; no billing configuration changed. Native SDK remains blocked by owner key/billing prerequisites; no paid infrastructure.
- Latest independent Play readback [41686496926](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/41686496926), artifact 13254613906, ZIP SHA-256 `de4b1199534e758b9bd1f384713e14deff86274d45cf4506776f460d28221b17`, independently verified after download. Internal 51019 is completed; alpha 51007 is draft; Production was not listed; `uploadAttempted=false`, `commitAttempted=false`. This is a read-only state check, not a readback of a new app artifact; no listing edit occurred.
- The latest phone connection check reports the authorized device offline (last seen about 31 hours before the 17:30Z check). Last phone observation remains 2026-11-01T21:24:32Z with an active/ambiguous session; no ADB or session action was attempted. Physical P0 remains BLOCKED_NOT_RUN.
