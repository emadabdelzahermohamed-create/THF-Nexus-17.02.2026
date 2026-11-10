# TopHeroFit integrator recheck — 2026-11-10

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
Canonical branch: `agent/codex/fitness-recovery/20261023`  
Canonical app-source SHA before evidence refresh: `baab97b1ff1e2c4f0ca0bba7b1921ad9e5ff43b7`

## 1. Canonical recovery and merged disjoint handoff

Read the latest GPS checkpoint on PR #284, the canonical recovery snapshot from 2026-11-09, the current PR/ownership state, and the latest independent Play state probe. PR #285 was the only handoff integrated in this run.

PR #285 exact PR HEAD: `c8d464b86576db172d03a734ca9a119bd47631fb`. Exact-head Android CI [42827029570](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42827029570) succeeded: product 60/60, source-contract 34/34, backend 29/29, Android unit 225/225; lint, assembleDebug and bundleRelease passed.

- Canonical squash merge: `baab97b1ff1e2c4f0ca0bba7b1921ad9e5ff43b7`.
- Files changed: `HealthConnectRepository.kt`, `HealthRecordEvidencePolicy.kt`, `HealthSourceTrustPolicy.kt`, and `HealthConnectProvenanceTest.kt` only.
- Artifact 13769139185 ZIP SHA-256: `d5a85a4091d762009df90c9fc9db1e492270b84e96a0d3d4e967e6183a7d18a5` (downloaded and independently rehashed).
- QA APK SHA-256: `806855fe3bcb9fb0ff12fce2b52949e957e48898c01f4a65bb95f5714bbdfb0b`.
- Unsigned validation AAB SHA-256: `3a7dd174d7695a1b27ac1a8a497ea439f382a2d3be948c3b82ba0eadcd95dddc`; extracted and independently hashed; no JAR signing entries.
- The merge tree's four file blobs match the tested PR head. No version, signing, workflow, Play, manifest permission, or billing change.

This is a Health Connect provider/device metadata gate. It does not cryptographically attest that a physical watch produced the data; no physical watch/Health PASS or reward authorization is claimed.

## 2. GPS / map candidate and exact artifacts

PR #284 branch `agent/codex/gps-open-source-stack-20261109` remains Draft/open/unmerged. Current branch HEAD `427ffe79ae7459fd062ce932bc1239a53cf2fcda`; exact app/test source HEAD `1fab42783712a980367079c413ba6708f772d130`.

### Requested original checkpoint run

Run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) on exact SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee` was inspected with job logs and downloaded artifact:

- Artifact ID 13707718861; ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`.
- Embedded source SHA: `3fcbe6acbb4dc660284c74c8392818996e1de7ee`.
- Unsigned validation AAB SHA-256: `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`.
- Archive and AAB hashes were independently recomputed; no JAR signing entries found.

### Later exact source/test and current branch-head runs

- Exact source/test-head run [42773832856](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42773832856) passed on `1fab42783712a980367079c413ba6708f772d130`: product 60/60, source-contract 40/40, backend 29/29, Android unit 225/225, lint/assemble/bundleRelease passed. Artifact 13743311221 ZIP SHA-256 `1e38b7c2e199f51ef78df00a9e0921904a515cca8931279f2a4c1064913b4e73`; unsigned AAB SHA-256 `961e639ae8c348c866d3d409a68d24471b08a1a8d9c8cd4a1b226a3a221077cc`.
- Current full branch-head run [42776754514](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42776754514) passed on `427ffe79ae7459fd062ce932bc1239a53cf2fcda`: product 60/60, source-contract 40/40, backend 29/29, Android unit 225/225, lint/assemble/bundleRelease passed.
- Current branch artifact 13745030142 ZIP SHA-256 `1da4d39ecf577fa4edb7a2a52e5cc59a24e6807813e71117e8e7e032a4528285`; QA APK SHA-256 `7df926720bd9f1cd5f14e52285a05c06a6499eea5dc59826afd8bfe8bcadfc61`; unsigned AAB SHA-256 `961e639ae8c348c866d3d409a68d24471b08a1a8d9c8cd4a1b226a3a221077cc`.
- The downloaded current AAB bytes exactly match the `1fab` source/test-head AAB. The docs-only branch-head update produced no new bundle bytes. No signing or Play upload occurred. The artifact's Gradle HTML report records 225 Android unit tests, 0 failures and 0 ignored; this corrects the earlier 450/450 aggregate count.

### Current PR #284 merge blockers

- Compare at pre-refresh canonical head `8db67a18002df0f9cedce48c31619433eb1876bd`: 13 ahead / 7 behind, merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`; this evidence-only refresh adds one canonical commit, so the live post-refresh comparison is 13 ahead / 8 behind. No rebase/cherry-pick was performed.
- PR #282 is open/draft and changes `app.js` for Health metric null-vs-zero truthfulness. Its base is old (`4e337838c079a75d9615653d14c38838e55d19ef`); exact-head CI exists on its old head, but open exercise UX handoffs also modify `app.js`. Reconcile and retest the combined file tree.
- PR #216 remains open and changes `app.js` for active-workout resume policy. It is separate from GPS activity-session persistence but overlaps #284's `app.js`; no exact-head Android CI is recorded. Reconcile it with #282 and exercise UX handoffs in one combined JS tree.
- PR #202 is closed; its `ActivityTrackingService.kt` / `ActivitySessionCheckpoint.kt` work is already in merged #264. No other active open PR directly changes `ActivityTrackingService.kt`; #284 is the current direct service handoff.
- PR #93 is open and claims `MainActivity.kt` for the Health-settings bridge, alongside Health reader/manifest/rationale surfaces. Reconcile that bridge with the location-settings bridge in #284 before merging.
- PR #248 is open/draft, adds only a display-smoothing helper and test, has an old base (`4a2315fd16be8610396d6415292f4863f90b8dd6`) and local 11/11 stub-harness evidence only. It has no exact-head Android Gradle/JUnit CI and is not wired into the route path.
- PR #215 is closed; its GPS source was superseded by #264, already in the canonical lineage. No other active direct ActivityTrackingService handoff was found.
- No explicit active lease registry or lease PR was found. Treat #93's MainActivity ownership note as a file-level hold.

Keep #284 Draft/unmerged until physical P0 and shared-file reconciliation pass. The Leaflet/OSM-derived map does not require a Google Maps SDK key or billing.

## 3. Device and Maps evidence

- Current Desktop Commander `localhost` check is OFFLINE; the 2026-11-10 20:31 Cairo recheck saw it last online about 8 hours earlier. Last recorded device identity is Samsung SM-A217F / Android 12; Play package `com.topherofit.thf.pulse`.
- Last recorded device-wide `location_mode=0` was from 2026-11-09. Current device/session state is unknown. No ADB device is available; no install, launch, Stop, pause/resume, settings or session action was attempted. Preserve the existing Play install and unknown session.
- Physical P0 remains NOT RUN: stationary drift, measured outdoor route, jump/multipath rejection, screen-off/background, Home/reopen, pause/resume, Stop, process-death recovery, notifications and daily-vs-session steps.
- Historical Maps preflight 41684077962 (2026-11-03) found no visible restricted key and no billing account. This is not a blocker for the current Leaflet/OSM/TopoMap/EOX map; it needs no Maps SDK key or billing. Google directions is an optional external handoff. Do not add Google Maps Rx, Maps SDK billing, or a key.

## 4. Live Play state and release lineage

Latest successful independent Play state readback: run 42405709027, attempt 4; artifact 13791872061; ZIP SHA-256 `bffbb6484802331c90f7b49ba029ab373f63cc2f13d94d10b980907008e775ee`; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`. Readback observed 2026-11-10 18:31:07 UTC.

- Internal 51019: completed.
- Alpha 51007: draft.
- Production: not listed / not verified.
- `uploadAttempted=false`; `commitAttempted=false`.
- Existing signed 51019 AAB SHA-256: `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5`, source SHA `76053bd9127c38d8065eb7ac250bdeb34ab67854`.
- Canonical app source after #285 is `baab97b1ff1e2c4f0ca0bba7b1921ad9e5ff43b7`; no signed AAB exists for it. #284's AAB is unsigned validation only. The Play readback is not a readback of current canonical source or either new candidate.

VersionCode 51020 remains unallocated. No new signed AAB, signing action, Play upload, listing edit, Production promotion or rollback.

## 5. Route-sync gap and next design

Completed GPS route history is still local-only in WebView local storage. Existing authenticated backend sync covers THF-created set/workout records, not GPS coordinates. No route endpoint, route table or cloud route upload is present in the inspected Android/AppDeploy contract.

Design-only document created: `ReleaseOps/FitnessStandalone/ROUTE_SYNC_DESIGN_20261110.md`. It requires separate default-off activity-summary and precise-route consent, per-session opt-in, finished-session-only uploads, bearer auth, per-user storage, idempotency, revocation, route/account deletion, explicit retention and privacy/Data Safety gates. The one-second map refresh remains local and is not route sync. No implementation or cloud upload claim.

## 6. Other priority state

- Session persistence/foreground service exists in source but is not physically revalidated. DailyStepLedger core exists; all-day observer/day-boundary/dashboard remain unwired.
- Health Connect now has the #285 typed swimming metadata gate; #282 truthfulness UI remains held, #93 reader and #188 permission guard remain open. Provider/device metadata is not cryptographic attestation.
- Competition backend #269 remains source-only for strength kg·reps; no event seed, admin key or independently verified backend deployment. Scores remain `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED`, `rewardEligible=false`.
- Privacy/Play Health declaration, Data Safety, bilingual medical disclaimer and public policy URL gates remain open. Production is NOT_VERIFIED.

**Release decision: HOLD.** No paid infrastructure. No version allocation, signing, Play write, device/session action or Production promotion.