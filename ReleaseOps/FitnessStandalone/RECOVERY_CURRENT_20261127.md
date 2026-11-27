# TopHeroFit — Canonical Recovery Checkpoint

**Observed:** 2026-11-27T17:51:42Z  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Application baseline before this checkpoint:** `779df53146e23e76fe7b1faabffbc0e3540ee29a`  
**ReleaseOps branch tip before this checkpoint:** `11f06f2554593a8d40949bdadcc142c1001fdc94`

## Current decisions

- TopHeroFit only. This repository and branch remain the only canonical release/version/signing/Google Play writer.
- No application PR was merged in this checkpoint.
- PR #315 has exact-head Android CI PASS and remains Draft pending physical P0.
- PR #284 remains Draft; its current head has no exact-head CI and is heavily behind.
- PR #311 remains Draft and is superseded for integration planning by the newer canonicalized #315 handoff; do not merge both.
- No versionCode was allocated. 51020 remains UNALLOCATED.
- No signing, upload, Play commit, track promotion, Production change, ADB or phone mutation occurred.
- No paid infrastructure was used.

## Latest GPS/activity handoff — PR #315

[PR #315](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/315)

- Branch: `agent/codex/gps-canonical-activity-engine-20261127-r1`
- Exact head: `32b2eae0558e609bd2e3c453e1af6d25bc9df406`
- Base: `11f06f2554593a8d40949bdadcc142c1001fdc94`
- Compare: 9 commits ahead, 0 behind; merge base equals current canonical base.
- Changed files: six GPS/activity source and test files only.
- Exact-head run: [45955722335](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45955722335), SUCCESS on the exact head.
- Product: 84/84; Source Contract: 41/41; Backend: 29/29; Android Unit: 359/359; failures 0; ignored 0.
- Android API 36, Kotlin/Gradle build, debug APK and unsigned AAB validation passed.
- Lint: 0 errors, 13 warnings, 1 hint.
- Artifact 15178872128, 63,107,155 bytes; ZIP SHA-256 `2aed93edc954a537ac9fd25101264ad5efab231a3e987021db12f68b640bcae4`, independently downloaded and rehashed.
- Embedded source marker: `SOURCE_SHA=32b2eae0558e609bd2e3c453e1af6d25bc9df406`.
- Debug APK SHA-256: `cff4e87ca2d3736f2d13ce21d19b1256a57fcbab5e5a65e8fd45485e26cdcff1`.
- Unsigned AAB SHA-256: `db3c94e1d655177cda8f2c40180e428440360213e795f362da9eacc34061f406`; `jarsigner` reports the AAB is unsigned.
- CI build identity uses versionCode 51019 / versionName `5.0.0-v2-alpha19-debug`; it is a validation artifact, not a signed release candidate.
- Source includes the tested GPS arbitration/stationary-drift guard and Android 14+ foreground-service type selection: LOCATION only when app location permission and device-wide location are enabled; HEALTH when activity-recognition permission is available; otherwise a new foreground start is refused.
- Keep Draft until physical P0 is completed. CI is not physical GPS, background, notification, or phone PASS.

## Earlier GPS handoffs

### PR #311

- Head `5eee7f80543d88420af011e36c4001660e75ee3b`; exact-head run 45566362328 succeeded.
- It is now 11 commits ahead / 29 behind the current canonical branch, diverged from the current base, and overlaps the newer #315 ActivityTrackingService/GPS policy files.
- Preserve its test evidence, but do not merge it separately. #315 is the current canonicalized integration candidate.

### PR #284 — OSM map/settings fallback

[PR #284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284)

- Current head: `274155eafdfff381009ef5814a621f32b225f1a8`; base SHA recorded by PR: `f596bcf722d5fac810538907ad6180999774bfc3`.
- Current compare to canonical tip: 19 ahead / 179 behind; diverged.
- Historical run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) validates only historical SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`, not the current head. Historical artifact 13707718861 is unavailable.
- The previous truncated MainActivity upload was repaired: current MainActivity at #284 head is 1,146 lines, fetched in two bounded windows; `motionSnapshot()` is present. This is source integrity only.
- #284 overlaps #315 ActivityTrackingService/GPS policy, #93 MainActivity/Manifest and #216/#224 WebView files. Keep Draft; do not merge wholesale. Extract the map/settings-only delta after shared owners release files, then run exact-head CI and physical map/location P0.

## Current canonical map and metrics boundaries

- Map: Leaflet in Android WebView, OpenStreetMap-derived raster base; OpenTopoMap and EOX Sentinel-2 are optional layers.
- Do not add archived Google Maps Rx, Google Maps SDK billing, a Maps key or a Google basemap for this OSM stack.
- HTTP tile cache headers are honored; this is not offline tile-pack storage or bulk prefetch.
- `GpsFixGate` is the signal-admission gate; `GpsDistanceAccumulator` is the only distance-credit path.
- Display smoothing must not change distance, pace, speed or rewards.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired. Do not stack it as a second per-fix filter without a unified false-positive policy.
- GPS reward eligibility remains false; no THF payouts are authorized.

## Health and competition state

- PR #314 merged at `779df53146e23e76fe7b1faabffbc0e3540ee29a`; exact source SHA `95f4996d0fefc3017401289d29278dda6740adec`, exact-head run 45830026710 passed (Product 84, Source 35, Backend 29, Android 352; zero failures/ignored). It changes only HealthSportMapper and its test.
- PR #312 unknown Health exercise types fail closed; PR #310 non-transitive Health session-window quarantine is merged.
- PR #93 remains Draft: 19 declared Health scopes versus the canonical five; hold for scope minimization and privacy/Play declaration reconciliation.
- PR #269 competition backend is merged but provisional `strength_volume_kg_reps` only. No independently verified GPS leaderboard; GPS reward eligibility false.

## Fresh Google Play readback — 2026-11-27

- Read-only probe [45872277536, attempt 2](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45872277536) completed SUCCESS at 2026-11-27T17:51:42Z.
- Job 140662113292 succeeded. It created and deleted a temporary empty Play edit solely to read listings/tracks; `uploadAttempted=false`, `commitAttempted=false`; no listing, track, version, upload or commit mutation.
- Artifact 15222725086, 1,918 bytes; ZIP SHA-256 `79b0718acfbf63d60324011832c11ac69b578c4894203d621998b86efb3577ef`, independently downloaded and rehashed.
- Embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`, independently rehashed.
- Package `com.topherofit.thf.pulse`; Internal 51019 Completed; Alpha 51007 Draft; Production not listed / not verified.
- Arabic and English listings are present. Support email: `TopHeroFit@gmail.com`. Listing describes calories/derived metrics as estimates and notes GPS quality depends on device/location/environment.
- This Play readback is independent of PR #315's unsigned CI AAB; it does not prove the new source is installed or released on Play.

## Device and physical P0

- Latest Desktop Commander device-list: localhost OFFLINE; last seen about 248 hours before this observation.
- Samsung SM-A217F current app/session state is UNKNOWN. No ADB, install, launch, force-stop, notification, permission or location-setting action was performed.
- Physical P0 remains BLOCKED_NOT_RUN: stationary 60-second drift; measured walk/run/cycle routes; precise/approximate and revoke/regrant; first-fix latency/accuracy; navigation and screen-off/background; persistent notification Pause/Resume/Finish; process-death restore without stopped-time credit; crash/ANR/Logcat.
- Do not interrupt a possible owner session when the device reconnects. Start with read-only state inspection.

## Release gates

- Last Play Internal versionCode: 51019.
- Next versionCode: 51020, UNALLOCATED. Allocate only after owner Play/API write prerequisites, GCP signing-key prerequisites, exact-head Android CI and physical P0 all pass.
- Owner Google Play/API write permission and GCP Secret Manager signing-key access remain NOT_VERIFIED.
- No new signed AAB. The existing signed 51019 artifact record remains preserved; its original build artifact is no longer retrievable for fresh rehash. The new #315 AAB is unsigned and must not replace it.
- Production remains NOT_VERIFIED and blocked on physical P0 plus policy/privacy gates.

## Separate route-sync gap

Completed GPS route history remains in WebView localStorage. No authenticated backend route-sync endpoint/table or precise-location upload path has been verified. After #284 is validated, inspect existing account/backend contracts and design opt-in backup/sync with explicit location consent, retention/deletion semantics and no precise-location upload by default. Do not conflate this with the one-second local GPS-to-map UI refresh.
