# TopHeroFit canonical recovery — 2026-11-14

Scope: **TopHeroFit only**. Sole source of truth: [`emadabdelzahermohamed-create/THF-Nexus-17.02.2026`](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026).
Canonical branch: `agent/codex/fitness-recovery/20261023`.

## Canonical source and latest tested application

- Canonical application merge: PR #295, merge commit `96d35d2edf292c16c5c462f4f6a2016576eb6a53`.
- PR #295 tested source: `06ce46526bd01b7a887b736add55451421ce9536`.
- Exact-head Android CI: [43602214529](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43602214529), SUCCESS.
- Product 67/67; source-contract 34/34; backend 29/29; Android unit, lint, assembleDebug and bundleRelease passed.
- Validation artifact 14117290237: ZIP SHA-256 `5b923c85c700f4e189e81bd6d815a563a9fd251b5aadf6689a741065d8211e85`. The candidate AAB was unsigned; no release signing or Play upload occurred.
- The canonical merge added a second fail-closed reviewed-provider check to Health provenance presentation. The canonical manifest still contains exactly five Health scopes: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE and READ_ACTIVE_CALORIES_BURNED. READ_HEART_RATE remains absent.
- The current canonical branch has since received documentation-only recovery updates and a comment-only read-only Play-probe trigger. These do not represent a new signed app or release.

## Latest GPS handoff and decision

- Selected native GPS handoff: [PR #294](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/294), Draft/open/unmerged.
- Branch: `agent/codex/gps-location-state-honesty-20261114-r1`.
- Tested source SHA: `9defd1296aa4575eafbe24981dfd95324ce14ef8`; exact-source CI [43568499998](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43568499998) SUCCESS.
- Product 67/67, source-contract 34/34, backend 29/29, Android 261/261 (0 failures, 0 ignored), API 36, Kotlin, lint, debug APK and unsigned AAB PASS.
- Artifact 14102669147: ZIP `31cf603e660691d7783503a905a4fe0357e6e32022f4a10c883b9e9364aa02e5`; APK `570a7e202a9a5ef81d016d03d3baf4cc9592a24e96e8fc6652566d9c8e8ce311`; unsigned AAB `281a178695405b5a589640e0f367b76235d42b3893aa5c529f930fa0f4c4e681`.
- The later documentation-only PR-head run 43568930832 produced artifact 14103910150. Its downloaded AAB hash is identical to the first AAB; the APK and ZIP differ. This was an unnecessary repeated validation build. Do not repeat it.
- PR #294 was originally based on `4fe915abfd6abb46072e1dfe0b30fcaa13f92014`. Current canonical had advanced through PR #295 and documentation-only commits. The intervening application change is limited to Health provenance policy/test and is disjoint from the six GPS source/test files. Rebase only those six files onto the current canonical HEAD, then require exact combined-head CI. Keep Draft; physical P0 remains mandatory before merge.
- Full map/provider/accuracy and artifact evidence: [GPS_MAP_QUALITY_20261114.md](GPS_MAP_QUALITY_20261114.md).

### PR #284 reconciliation

[PR #284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284) remains Draft and must not be merged wholesale. It overlaps #294 in five native GPS source/test files; #284 also changes `app.js` and `index.html`, which overlap #282 and #216, and `MainActivity.kt` plus `test_source_contract.py`, which overlap #93. Use #294 as the current native GPS status/provider handoff. Keep #284's Leaflet/OSM WebView map changes as a separate reference until shared-file owners reconcile them.

PR #292 is closed unmerged as superseded by #294.

## Current PR / ownership snapshot

| PR | Current state | Decision |
|---|---|---|
| #294 GPS status/provider | Draft; exact source CI PASS | Rebase onto current canonical, combined-head CI, then physical P0; no merge now |
| #284 GPS/map UI | Draft; overlaps #294, #282, #216 and #93 | Keep as map/UI reference; no wholesale merge |
| #282 Health metric truthfulness | Draft; changes `app.js` | Exact-head CI and combine with #216 only after file-level reconciliation |
| #216 active-workout resume | Open, not Draft; changes `app.js` | No current exact-head Android CI; preserve active-workout state |
| #93 Health services | Draft; claims MainActivity, manifest and source-contract ownership | Reconcile to five approved scopes; its 19-scope manifest is not authorized |
| #248 GPS route smoother | Draft; helper/tests only | No exact-head Android CI; presentation-only, never metric evidence |

No formal lease registry was found. Treat observed shared-file overlap and #93's explicit MainActivity/source-contract claim as active ownership holds. Do not edit or merge shared files concurrently.

## GPS, session and anti-cheat

- Map stack: Leaflet/WebView, attributed OSM streets, OpenTopoMap terrain and EOX Sentinel-2 cloudless 2016 imagery. No native Google Maps SDK, key, billing, traffic or transit layer is required or claimed. Browser caching is not a downloadable offline tile package.
- Native session source contains Foreground Service, START_STICKY, periodic checkpoints, task-removal/destruction checkpoints and notification Pause/Resume/Stop actions. This is source-level evidence only.
- The anomaly policy exists and is unit-tested. #294's service captures mock state and monotonic timestamps and applies `GpsFixGate` checks for mock/accuracy/time/speed, but does not invoke `ActivityEvidenceAnomalyPolicy.assessSegment`. Source continuity, long-gap and uncertainty-adjusted segment checks remain unintegrated.
- Do not grant distance, pace or competition credit as fully anti-cheat verified until raw Android fixes pass the anomaly policy and the physical spoof/drift tests pass.

## Physical device

Desktop Commander `localhost` is OFFLINE; last seen approximately 103 hours before the 2026-11-14 19:56 Cairo check. Last known device is Samsung SM-A217F / Android 12. Current device/session state is unknown. Preserve the Play install and any possible live session. No ADB, install, launch, Stop, settings or activity-data action was attempted.

Physical P0 remains BLOCKED_NOT_RUN: stationary drift, measured walking/running/cycling routes, coarse-only permission, first-fix latency, provider switching, screen-off/background, notification actions and process-death recovery.

## Health, metrics and competitions

- Canonical Health scopes remain exactly five; #93's 19-scope manifest is incompatible with the merged #188 allowlist. No extra scope is authorized.
- #282 still needs to preserve `null`/missing as unavailable and numeric zero as a genuine measured zero. Do not render denied Health metrics as 0.
- Competition PR #269 is merged backend-only and currently supports provisional `strength_volume_kg_reps`. Admin creation remains disabled without owner-managed `THF_COMPETITION_ADMIN_KEY`; no event is seeded or production backend deployment independently verified. Scores remain `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED`; `rewardEligible=false`. No THF rewards or payouts are authorized.

## Route backup/sync — separate gap

Completed GPS routes remain in WebView local storage (`pulse.v2.activities`, latest 100). The native `BackendSyncRepository` sends workout/set metadata to `/api/v2/workouts/sync` and `/api/v2/workouts?limit=200`, with bearer auth and idempotency, but no coordinate fields. `fitness-v2/appdeploy/android_v2_routes.ts` has no route endpoint; its resource kinds do not include route records. No authenticated GPS route upload or restore path exists.

Design only: [ROUTE_SYNC_DESIGN_20261110.md](ROUTE_SYNC_DESIGN_20261110.md). Keep activity-summary backup and precise-route backup separate and default-off. Precise routes require explicit account and per-session consent, finished-session-only upload, server-derived account identity, per-route deletion, consent revocation and account-deletion integration. Do not connect this to the one-second local map refresh, Health, competitions or rewards. No route-sync code or cloud upload claim.

## Fresh Google Play readback — 2026-11-14

A read-only probe was successfully triggered by a comment-only workflow-file update. No app build, version, signing, track or listing write was performed.

- Workflow run: [43624419818](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43624419818), SUCCESS, observed 2026-11-14 18:03:26 UTC.
- Artifact 14125382777 ZIP SHA-256: `c1d38fe46a63a310558e9671645cbccfb4752b99aedf6d98d8aac0bd78b4363e`.
- Embedded JSON SHA-256 independently recomputed: `09e7a346e5e1c893d4323d20105d8f4d63`.
- Package: `com.topherofit.thf.pulse`.
- Internal: versionCode 51019, `THF Fitness 51019 Internal`, status completed.
- Alpha: versionCode 51007, `Top Hero Fit 51007 Closed Test`, status draft.
- Production: not listed in readback; NOT_VERIFIED.
- `uploadAttempted=false`; `commitAttempted=false`.

The current Arabic and English listings include estimated-metric and no-medical-diagnosis/professional-advice disclaimers. They still claim GPS sessions, background tracking, offline exercise/program content and voice guidance; those claims remain subject to physical and asset QA. No listing edit was made.

## Signing and release prerequisites

- The read-only Play probe proves the configured GitHub OIDC/Workload Identity Federation path can authenticate and read Android Publisher track/listing state. It does **not** prove Play upload/write permission or signing-key access.
- The legacy `fitness-51008-internal-promote.yml` is hard-coded to source SHA `76053bd9127c38d8065eb7ac250bdeb34ab67854`, versionCode 51019 and upload certificate SHA-1 `D8:BB:CA:BC:17:78:03:43:2E:5D:95:7B:19:61:D2:03:6A:3A:03:06`. It references GCP Secret Manager secrets for the upload keystore, store password, alias and key password. It is not a valid 51020 release workflow and must not be run for the next release.
- `fitness-sensor-candidate.yml` is QA-only: package `com.topherofit.thf.pulse.qa`, fixed validation versionCode 51019, unsigned AAB. It is not a release/signing workflow.
- Owner-controlled signing secret access, expected upload-certificate fingerprint, Play upload/write permission and a new exact-source release workflow for a fresh versionCode remain unverified. Do not read or expose secret values in a chat or logs.

## Release boundary

- Latest Internal versionCode: 51019.
- Next versionCode: **51020 remains unallocated**; allocate only after owner API/key prerequisites, final exact-head Android CI and physical P0 pass.
- No new signed AAB exists for the current source. The recorded 51019 signed AAB SHA remains `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5`; its original build artifact is no longer retrievable for fresh rehashing.
- Production remains NOT_VERIFIED. Do not promote before policy/privacy, Data Safety, listing truthfulness and physical gates pass.
- No paid infrastructure, Maps billing/key, signing, version allocation or Play upload occurred in this checkpoint.

## Next safe execution order

1. Rebase the six disjoint #294 GPS source/test files onto the current canonical HEAD and run exact combined-head CI. Keep Draft.
2. Keep #284's map/UI changes separate; reconcile `app.js` with #282/#216 and MainActivity/source-contract ownership with #93.
3. Preserve the unknown phone session; run physical P0 only after the authorized phone is online and confirmed idle.
4. Integrate raw GPS fixes with `ActivityEvidenceAnomalyPolicy` and test source continuity, monotonic time, mock state, accuracy, gaps and sport-specific speed.
5. Complete #282's null-vs-zero UI truthfulness without adding Health scopes.
6. Keep competitions reward-ineligible until server deployment, owner key, trusted physical evidence and anti-cheat gates are verified.
7. Keep route sync design-only until consent, account isolation, deletion, retention, storage-security and privacy contracts are implemented and tested.

No merge, version allocation, signing, upload or Production promotion is authorized by this checkpoint.


## 2026-11-14 rebased GPS integration update

- Rebased PR #294 onto canonical base `82ac0797f26ef142bee868ea6f8378066a961b1e`; new exact PR head `7933a0eb0b6bedf8d00af49fee41ed24d88c264f`, 1 ahead / 0 behind, six source/test files only.
- Exact combined-head Android CI [43625025348](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43625025348): SUCCESS. Product 67/67, source-contract 34/34, backend 29/29, Android 262/262 (0 failures/ignored), API 36, Kotlin, lint, assemble and unsigned AAB PASS. Lint 0 errors, 16 warnings, 1 hint.
- Artifact 14125129060: ZIP SHA `d37f8558119c0303a81cc8567ce98f3a32c7df89c02c1c77fdfad0e112f1e09e`; APK SHA `03ff83dbe381022012e9eb2035c8edea42b98ccabadc851d8ca530f153d0a336`; unsigned AAB SHA `92806387b1b068e4beeddca059a2ec520e5d080e39c0c4990e2f35080d72577d`. Artifact downloaded and hashes independently verified; jarsigner confirms unsigned.
- PR #294 body now records the rebased head, exact CI and artifact hashes. It remains Draft. The exact CI gate is met; physical P0 remains blocked by offline Desktop Commander and unknown SM-A217F/session state.
- PR #284 received an ownership comment: keep Draft, use its map/WebView changes as a separate reference, and do not merge its overlapping native service, app.js, MainActivity or source-contract files wholesale.
- The earlier documentation-only run 43568930832 produced an identical AAB SHA to run 43568499998. That redundant build is documented and must not be repeated. The new rebased AAB is different because canonical Health provenance is now in the combined source.
- No merge, version allocation, signing, upload or Production promotion.


## Canonical branch drift after exact GPS CI — 2026-11-14 20:18 Cairo
The canonical branch has advanced from the PR #294 tested base `82ac0797f26ef142bee868ea6f8378066a961b1e` to `055f97d2e842170e45a838b21ed10e2c469d710d` through three documentation-only commits (GPS checkpoint, recovery checkpoint and release ledger). Current compare is 1 ahead / 3 behind; the PR diff still contains the same six GPS source/test files and no changed application/test blobs from those later commits. Do not rebuild or re-upload the unchanged AAB for this documentation-only drift. Re-evaluate mergeability against the latest canonical head only when physical P0 is ready; if rebase is required then, run exact-head CI only if the application/test tree changes.
