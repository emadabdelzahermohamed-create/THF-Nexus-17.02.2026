# TopHeroFit — GPS and Activity Engine quality report

Date: 2026-11-11 (Africa/Cairo)  
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
Canonical branch at checkpoint start: `agent/codex/fitness-recovery/20261023`  
Canonical HEAD at checkpoint start: `c6da9f647d089c159b01c28e46d5e2da93baf712`  
Candidate PR: [#284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284)  
Candidate branch: `agent/codex/gps-open-source-stack-20261109`  
Exact candidate HEAD: `fdbdd0588222ba366e56767e3b21de66c3f0d829`

## Source-of-truth review
- Historical requested report `GPS_MAP_QUALITY_20261101.md` re-read from `agent/codex/gps-map-quality-20261030`, blob `0e50b45f7be1e2a245753233f3e70343394b1115`.
- Candidate's latest prior GPS report `GPS_MAP_QUALITY_20261110.md` re-read, blob `a71defe348f650743d4a2623c731f14e107829ed`.
- Canonical `RECOVERY_20261023.md` re-read from `agent/codex/fitness-recovery/20261023` before this update.
- Latest canonical map decision is commit `c6da9f647d089c159b01c28e46d5e2da93baf712`; it selects the current Leaflet/OSM-derived stack and says Maps SDK, billing and key are not required for that stack.

## Material Activity Engine correction
Commit `fdbdd0588222ba366e56767e3b21de66c3f0d829` fixes a fallback-provider permission mismatch:
- Before the fix, the framework fallback chose GPS_PROVIDER whenever the device reported it enabled, even when the user had granted only approximate/coarse location.
- The coarse-only user could therefore hit a GPS-provider permission failure while the code did not try NETWORK_PROVIDER.
- The new pure policy chooses GPS_PROVIDER only with fine permission, chooses NETWORK_PROVIDER for coarse-only permission, and returns no provider when permission or an enabled eligible provider is absent.
- Provider-enabled checks are isolated so a failure checking GPS does not suppress a usable network-provider fallback.
- The Fused Location request, generation guard, callback ownership, accepted-fix gate, distance accumulator and activity metrics were not changed by this commit.

Exact source blobs:
- `ActivityTrackingService.kt`: `95230f9ae374fa806ec7674cb046ab7726427f74`
- `ActivityLocationFallbackPolicy.kt`: `b9455186801cee379458be3468263b3ec4832f3b`
- `ActivityLocationFallbackPolicyTest.kt`: `cf46a254559e18ba0c23b36b641b344fc45d8157`

## Exact-head Android CI and artifact evidence
- Workflow: Fitness Activity Candidate Build
- Run: [42976730277](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42976730277)
- Exact tested SHA: `fdbdd0588222ba366e56767e3b21de66c3f0d829`
- Result: SUCCESS
- Product tests: 60/60
- Source-contract tests: 40/40
- Backend tests: 29/29
- Android Gradle unit-test HTML report: 228/228, 0 failures, 0 ignored
- Android API 36 setup: PASS
- `:app:testDebugUnitTest`: PASS
- `:app:lintDebug`: PASS
- `:app:assembleDebug`: PASS
- `:app:bundleRelease`: PASS (validation only)
- Artifact ID: `13836420964`
- Artifact ZIP SHA-256: `774f3bf4c415f0b8c4c658953a54fa2c1ff69350ab892ab3cc847aff5cf59853`
- QA APK SHA-256: `11290ca3db6cac232431eab9ff7a771e7d913446f07cdfe55a2956dfc2811fa1`
- Validation AAB SHA-256: `be085f9f86bb147a88430983944d249254ff9a8cf3e7ad22d03e10e2f1c43239`
- The downloaded AAB was independently extracted and checked with `jarsigner -verify`; the result was `jar is unsigned`.
- Artifact package: `com.topherofit.thf.pulse.qa`; validation versionCode 51019; versionName `5.0.0-v2-alpha19-debug`.

This is exact-head source/build validation, not physical GPS QA or Play acceptance. No production signing, version allocation, upload, or Play PASS occurred.

## Physical-device QA
- Desktop Commander `localhost` is OFFLINE, last seen about 20 hours before this run.
- The last recorded identity is Samsung SM-A217F / Android 12; prior ADB check returned no attached device.
- No ADB install, launch, Stop, pause/resume, settings change, or activity-data read was attempted.
- Preserve the installed Play package and any unknown live session.
- Physical stationary-drift, measured-route, approximate-permission fallback, first-fix latency, jump/multipath rejection, background/screen-off, notification actions and process-death P0 remain NOT RUN.

## Maps decision and owner boundary
- Current canonical stack: Leaflet in the local WebView, attributed OpenStreetMap streets, OpenTopoMap terrain, and EOX Sentinel-2 cloudless 2016 satellite/hybrid.
- Canonical commit `c6da9f647d089c159b01c28e46d5e2da93baf712` says this stack does not require Google Maps SDK, billing or a key; Google directions is an optional external handoff.
- Historical preflight `41684077962` (2026-11-03) recorded Maps Android Backend and API Keys APIs enabled, key-inventory permission denied, no package/SHA-restricted key visible, and no billing account linked.
- No permission retry, billing, payment method, key, secret or paid infrastructure change was made.
- No native Google basemap, traffic overlay or transit overlay is present or claimed. Revisit native Google integration only after the owner prerequisite and an explicit repository decision to change the current map-stack choice.

## PR merge/ownership boundary
- At run start, canonical branch HEAD was `c6da9f647d089c159b01c28e46d5e2da93baf712`; candidate compare: 14 ahead / 8 behind, merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`.
- PR #284 remains Draft. Its file set overlaps #282 and #216 on `app.js`; #93 claims `MainActivity.kt` and also overlaps `test_source_contract.py`. These shared-file changes require reconciliation and exact combined-head CI before merge.
- PR #248 is a separate route-display smoothing handoff with stale base and no exact-head Android Gradle/JUnit CI; it remains unintegrated and must stay display-only if later accepted.

## Scope and release boundary
No Health/anti-cheat or exercise-catalog files, release version, workflow, signing, billing, secret or Play files were changed. VersionCode 51020 remains unallocated. No APK was installed on the phone, no AAB was signed or uploaded, and no Play state changed.

## Next safe work
1. Reconcile #284's shared `app.js`, `MainActivity.kt` and source-contract ownership before rebasing/merging.
2. Restore an ADB-visible authorized phone and confirm the current activity is safely idle before physical P0.
3. Test the coarse-only provider-selection path on Android 12; the current evidence is unit/Android-build validation only.
4. Keep the existing Leaflet/OSM stack until the owner prerequisite and an explicit map-stack decision authorize native Google Maps SDK work.
5. Keep VersionCode 51020 unallocated and PR #284 Draft.


---

## Integrator recheck — 2026-11-11 19:46 Africa/Cairo

This section supersedes the earlier run/head observations above; it does not change the earlier historical evidence.

- PR #284 current head: `be95a73bce584043eaffe17df1c1a99a81251488`.
- Exact current-head run: [42978310512](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42978310512), SUCCESS. The implementation/test source commit remains `fdbdd0588222ba366e56767e3b21de66c3f0d829`; the final head adds only recovery-document synchronization.
- Tests: product 60/60; source-contract 40/40; backend 29/29; Android 228/228, 0 failures, 0 ignored. Lint, debug APK, and release AAB validation passed.
- Artifact 13836587093: ZIP SHA-256 `5c601d070f86f01729138eb90d84cf039b64499a73ad90f71541036c226fff5d`; APK SHA-256 `cd665518980fa18d910c7850c4ed602c251d0f0ebff16a399d67551788d65738`; AAB SHA-256 `be085f9f86bb147a88430983944d249254ff9a8cf3e7ad22d03e10e2f1c43239`. The AAB is unsigned and matches the prior source-head AAB; no signing or upload.
- Requested run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) was a successful historical run on `3fcbe6acbb4dc660284c74c8392818996e1de7ee`, not the current PR head. Artifact ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`; APK SHA-256 `08a5730096d1cfc97193e47726f90e533f89d9e0cc3c606faae467b46e72e9b5`; unsigned AAB SHA-256 `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`; Android tests 223/223.
- The preceding failed run [42694199295](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694199295) failed the source-contract assertion that `motionSnapshot` exists because the uploaded MainActivity source was truncated. The current PR-head MainActivity file was fetched in two ranges (1–999 and 1000–1146): 1,146 lines total; `motionSnapshot` is present.
- Current canonical app-source head: `3b65efa94709e3a60cc62113e19c92639e2a76b9`. Fresh compare: 15 ahead / 11 behind, merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`. PR remains Draft despite GitHub's mergeable=true.
- Physical P0 remains NOT RUN: device offline, last seen about 31 hours before this recheck. Last recorded `location_mode=0` is from 2026-11-09; no device-wide setting was changed.
- Current Leaflet/OSM-derived map stack remains the chosen free route; no Google Maps SDK, billing, or key is required for this stack.
- No current candidate AAB was signed or uploaded. Latest Play readback remains 51019 Internal completed / 51007 Alpha draft / Production not verified; it is not a readback of this GPS candidate.

Merge hold remains: #282/#216/exercise UX overlap `app.js`; #93 claims `MainActivity.kt`; physical P0 has not run.
