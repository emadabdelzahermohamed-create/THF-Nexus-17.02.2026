# TopHeroFit GPS / Maps checkpoint — 2026-11-14

Scope: TopHeroFit only. Canonical repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.

## Current GPS handoffs

### PR #294 — selected native Activity Engine candidate

- [PR #294](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/294) remains Draft and unmerged.
- Branch: `agent/codex/gps-location-state-honesty-20261114-r1`.
- PR head at this checkpoint: `1191a9b4ba4bebcb484c78c3223dd6f48f3ab2da`.
- Exact tested application/test source: `9defd1296aa4575eafbe24981dfd95324ce14ef8`.
- Original base: `4fe915abfd6abb46072e1dfe0b30fcaa13f92014`.
- Latest canonical application source at recheck: `96d35d2edf292c16c5c462f4f6a2016576eb6a53`; intervening PR #295 Health provenance changes are disjoint from the six GPS source/test files. The canonical branch has since added recovery-only commits and a read-only Play-probe trigger commit. Rebase the six GPS files onto the current canonical HEAD and run combined-head CI before considering integration.

Material source changes:
1. Android API 28+ location-service status uses the system-wide `LocationManager.isLocationEnabled` switch, not independent provider flags.
2. Pre-28 provider availability is permission-aware: GPS requires fine permission; network requires coarse permission.
3. No location-settings probe occurs before location permission is granted.
4. The foreground notification reports the raw provider (GPS, network, fused or generic location), not an unconditional “GPS” label.
5. Accuracy presentation uses `±<1 m` for positive sub-metre values, rounds other positive radii upward, and renders missing/invalid accuracy as unavailable rather than zero.
6. Acquiring text is generic and does not promise high accuracy before a fix exists.
7. The same candidate includes bounded Fused-to-framework fallback, coarse-only NETWORK selection, provider re-selection and stale-anchor reset from the prior GPS fallback work.

No distance, speed, route or activity metric calculation changed in #294. These are source-truth and presentation corrections, not proof of improved physical accuracy.

### Exact-source verification and artifacts

[Exact-source CI run 43568499998](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43568499998) tested `9defd1296aa4575eafbe24981dfd95324ce14ef8` and succeeded:

- Product: 67/67
- Source-contract: 34/34
- Backend: 29/29
- Android unit: 261/261; 0 failures, 0 ignored
- Android API 36, Kotlin compile, lint, debug APK and unsigned validation AAB: PASS
- Lint: 0 errors, 16 warnings, 1 hint

Artifact 14102669147:
- ZIP SHA-256: `31cf603e660691d7783503a905a4fe0357e6e32022f4a10c883b9e9364aa02e5`
- QA APK SHA-256: `570a7e202a9a5ef81d016d03d3baf4cc9592a24e96e8fc6652566d9c8e8ce311`
- Validation AAB SHA-256: `281a178695405b5a589640e0f367b76235d42b3893aa5c529f930fa0f4c4e681`
- Downloaded archive and binary hashes independently matched. `jarsigner` confirms the AAB is unsigned. QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019.

A documentation-only PR-head update triggered a second build, [run 43568930832](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43568930832), artifact 14103910150. I downloaded both archives and independently compared them:
- Second ZIP SHA-256: `3950f65f0ea4cdd1472c7f1c1ad1af5452d0d83af5d257ed7346b0c9b3cda4b4`
- Second QA APK SHA-256: `17046c4e13eea43e72c02a0a8e86923aac2cd30015a38a9ef3418be2c30afac9`
- Second AAB SHA-256: `281a178695405b5a589640e0f367b76235d42b3893aa5c529f930fa0f4c4e681` — byte-identical to the first AAB.

The second run therefore rebuilt and re-uploaded an unchanged validation AAB because a docs-only commit changed the PR head. Do not repeat this build. The first exact-source run remains the authoritative tested artifact; a new build is justified only after the source tree changes (for example, after rebase onto the current Health merge).

### PR #284 — older map/UI and native fallback handoff

- [PR #284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284) remains Draft; do not merge wholesale.
- It changes `app.js`, `index.html`, `ActivityTrackingService.kt`, `ActivityLocationFallbackPolicy.kt`, `GpsFixPresentationPolicy.kt`, `MainActivity.kt` and `test_source_contract.py`.
- It overlaps #294 in five GPS source/test files; it also overlaps #282 and #216 in `app.js`, #216 in `index.html`, and #93 in `MainActivity.kt` plus `test_source_contract.py`.
- Treat #294 as the selected native GPS status/provider handoff. Retain #284 as a reference for its map/WebView UI changes only; reconcile those changes separately after the shared-file owners agree. Do not copy the old service implementation over #294.

## Canonical map stack

- Leaflet inside Android WebView.
- Attributed OpenStreetMap street tiles.
- OpenTopoMap terrain tiles.
- EOX Sentinel-2 cloudless 2016 satellite/hybrid imagery.
- No native Google Maps SDK, billing, key, live traffic or transit layer is required or present in the selected stack. Google directions is an optional external handoff only.
- The existing WebView cache is not an offline tile package; do not claim guaranteed offline map tiles.

No paid map service, billing account, key or secret was created or changed.

## Session and physical QA boundary

The native service has source-level mechanisms for a foreground notification, START_STICKY restoration, 10-second checkpoints, task-removal/destruction checkpoints, Pause/Resume/Stop notification actions and stale GPS-anchor reset. These are code observations, not physical-device PASS.

Desktop Commander device `localhost` is OFFLINE; last seen approximately 103 hours before the 2026-11-14 19:56 Cairo check. Last known phone: Samsung SM-A217F / Android 12. Current device and session state are UNKNOWN. Preserve the existing Play install and any possible live session. No ADB, install, launch, Stop, settings or activity-data action was attempted.

Physical P0 remains BLOCKED_NOT_RUN:
- stationary drift / false movement
- measured walking, running and cycling routes
- first-fix latency and provider switching
- approximate-only permission
- screen-off/background continuity and notification actions
- process-death recovery and explicit Finish

## Anti-cheat boundary

The canonical `ActivityEvidenceAnomalyPolicy.kt` exists and is unit-tested, but the #294 `ActivityTrackingService.kt` does not call `ActivityEvidenceAnomalyPolicy.assessSegment`. The service does capture OS mock state and monotonic elapsed time; `GpsFixGate` rejects mock fixes, invalid/poor accuracy, stale or non-monotonic timestamps and sport-speed violations. Source continuity, long-gap and uncertainty-adjusted segment decisions remain unintegrated. Do not use display-smoothed route points as evidence or grant full anti-cheat/reward credit.

## Route backup / sync — separate gap

`persistFinishedActivity()` still stores completed route points in WebView local storage (`pulse.v2.activities`, bounded to 100 entries). The existing Android `BackendSyncRepository` sends workout/set metadata to `/api/v2/workouts/sync` and `/api/v2/workouts?limit=200`; it contains no coordinate or route-point fields. `fitness-v2/appdeploy/android_v2_routes.ts` has no route endpoint and its resource-kind allowlist is limited to ticket/session/idempotency/workout-index. No authenticated route-sync endpoint or precise-location upload exists.

Design only: [ROUTE_SYNC_DESIGN_20261110.md](ROUTE_SYNC_DESIGN_20261110.md). Keep summary backup and precise-route backup as separate default-off consents; upload only finished sessions after explicit per-session consent; server derives account identity from bearer auth; define retention, per-route deletion, consent revocation and account deletion before implementation. Never connect route upload to the one-second local map refresh, Health sync, competitions or rewards.

## Next safe steps

1. Rebase only the six disjoint #294 source/test files onto current canonical HEAD and run exact combined-head Android CI. Keep Draft.
2. Keep #284's `app.js`/WebView map work separate until #282/#216/#93 file ownership is reconciled.
3. Preserve the unknown phone session; run physical P0 only after the authorized device is online and confirmed idle.
4. Wire raw Android GPS fixes into the anomaly policy before distance/pace/competition credit.
5. Keep route sync design-only until the account/deletion/privacy contract and tests are implemented.

No version allocation, signing, Play upload, Production promotion or GPS physical PASS occurred.


## Rebased exact combined-head validation — 2026-11-14 20:13 Cairo

PR #294 was safely rebased onto current canonical HEAD `82ac0797f26ef142bee868ea6f8378066a961b1e` by force-with-lease (expected previous PR head `1191a9b4ba4bebcb484c78c3223dd6f48f3ab2da`). The resulting PR head is `7933a0eb0b6bedf8d00af49fee41ed24d88c264f`, exactly one commit ahead and zero behind canonical. Its diff contains only six GPS source/test files; the canonical recovery and GPS reports remain in the base branch.

[Exact rebased-head CI run 43625025348](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43625025348) completed SUCCESS on that exact SHA:
- Product 67/67; source-contract 34/34; backend 29/29.
- Android unit 262/262; 0 failures; 0 ignored.
- API 36, Kotlin compile, lint, debug APK and unsigned validation AAB all PASS; Gradle BUILD SUCCESSFUL.
- Lint: 0 errors, 16 warnings, 1 hint.

Artifact 14125129060 was downloaded and independently rehashed:
- ZIP: `d37f8558119c0303a81cc8567ce98f3a32c7df89c02c1c77fdfad0e112f1e09e`.
- QA APK: `03ff83dbe381022012e9eb2035c8edea42b98ccabadc851d8ca530f153d0a336`.
- AAB: `92806387b1b068e4beeddca059a2ec520e5d080e39c0c4990e2f35080d72577d`.
- `jarsigner` reports the AAB is unsigned. APK identity is QA package `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is not a store artifact.

The rebased AAB differs from the pre-Health-base AAB `281a1786...`, as expected because canonical PR #295 Health provenance is now part of the combined source. The separate docs-only run 43568930832 had the same AAB bytes as its predecessor and was a redundant rebuild; do not repeat that pattern.

PR #294 remains Draft. The exact combined-head CI gate is now met, but physical P0 is still BLOCKED_NOT_RUN because Desktop Commander is offline and the SM-A217F/session state is unknown. No merge, install, signing, Play upload or version allocation.


## Canonical branch drift after exact GPS CI — 2026-11-14 20:18 Cairo
The canonical branch has advanced from the PR #294 tested base `82ac0797f26ef142bee868ea6f8378066a961b1e` to `055f97d2e842170e45a838b21ed10e2c469d710d` through three documentation-only commits (GPS checkpoint, recovery checkpoint and release ledger). Current compare is 1 ahead / 3 behind; the PR diff still contains the same six GPS source/test files and no changed application/test blobs from those later commits. Do not rebuild or re-upload the unchanged AAB for this documentation-only drift. Re-evaluate mergeability against the latest canonical head only when physical P0 is ready; if rebase is required then, run exact-head CI only if the application/test tree changes.
