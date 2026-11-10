# TopHeroFit canonical recovery — 2026-11-10

Canonical repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
Canonical branch: `agent/codex/fitness-recovery/20261023`  
Canonical Android app-source SHA before this evidence checkpoint: `baab97b1ff1e2c4f0ca0bba7b1921ad9e5ff43b7`

## Resume boundary

This is a TopHeroFit-only recovery/evidence snapshot. The app-source change in this checkpoint is the tested Health Connect merge #285. The new recovery, integrator and route-sync documents are evidence/design only. No Android version was allocated; no release signing, Play upload, listing/track mutation, Production promotion, device/session action, paid infrastructure or other-project change occurred.

## Latest GPS / map candidate — PR #284

PR #284 remains Draft/open/unmerged on branch `agent/codex/gps-open-source-stack-20261109`, current HEAD `427ffe79ae7459fd062ce932bc1239a53cf2fcda`. Its Android app/test source head is `1fab42783712a980367079c413ba6708f772d130`; the later branch commits are documentation-only.

The latest full branch-head Android CI run [42776754514](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42776754514) passed on exact branch HEAD `427ffe79ae7459fd062ce932bc1239a53cf2fcda`: product 60/60, source-contract 40/40, backend 29/29, Android unit 225/225; `:app:lintDebug`, `:app:assembleDebug` and `:app:bundleRelease` succeeded.

The downloaded Gradle HTML report at `android/app/build/reports/tests/testDebugUnitTest/index.html` records **225 tests, 0 failures, 0 ignored**. This artifact-level count corrects the earlier 450/450 aggregate figure; the earlier figure was overstated.

- Artifact 13745030142 ZIP SHA-256: `1da4d39ecf577fa4edb7a2a52e5cc59a24e6807813e71117e8e7e032a4528285` (downloaded and independently rehashed).
- QA APK SHA-256: `7df926720bd9f1cd5f14e52285a05c06a6499eea5dc59826afd8bfe8bcadfc61`.
- Unsigned validation AAB SHA-256: `961e639ae8c348c866d3d409a68d24471b08a1a8d9c8cd4a1b226a3a221077cc` (extracted from the downloaded archive and independently hashed; no JAR signing entries).
- The AAB bytes are identical to the earlier run 42773832856 on source/test SHA `1fab...`; this documentation-only branch-head validation did not create new Android bundle bytes. Do not sign or upload this unchanged AAB.

The earlier requested checkpoint run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) on exact SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee` was also inspected. Artifact 13707718861 ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c` was downloaded and independently matched; its unsigned AAB SHA-256 is `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`. The later `1fab`/`427ffe` candidate contains the subsequent source corrections and supersedes that earlier artifact.

### Material GPS / Activity Engine behavior in #284

- Fused location requests use a unique callback and monotonically increasing request generation; late results/registration callbacks cannot restart collection after pause, stop or session replacement.
- First-fix/stale-fix watchdogs use an 8-second/12-second fallback to one Android framework provider (GPS when enabled, otherwise network); Fused is stopped after framework fallback registration.
- GPS state and accepted accuracy presentation are truthful; stale/off/paused/acquiring states do not display old accuracy or a false zero. The Location Settings CTA is shown when device-wide location is off.
- The map uses Leaflet with attributed OpenStreetMap streets, OpenTopoMap terrain and EOX Sentinel-2 cloudless 2016 satellite/hybrid layers, plus an external Google directions handoff. No Google Maps Rx, Maps SDK billing, API key or paid map infrastructure was added.

### Merge hold and overlap

After the disjoint #285 merge, PR #284 is 13 commits ahead / 6 behind canonical, with merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`. It remains Draft until physical P0 and owner Maps prerequisites pass and shared-file ownership is reconciled.

- #282 is open/draft and changes `app.js` for Health metric null-versus-zero truthfulness. It has exact-head CI on its old head but is based on older SHA `4e337838c079a75d9615653d14c38838e55d19ef`; it also overlaps open exercise UX handoffs. Reconcile/rebase and test the combined `app.js` tree before merge.
- #93 remains open and claims `MainActivity.kt` for the Health-settings bridge plus Health service/manifest/rationale files. Treat that claim as an active file-level hold; reconcile the two settings bridges and run exact combined-head CI before merging #284.
- #248 remains open/draft and adds only `ActivityGpsRouteSmoother.kt` plus its test. Its base is stale (`4a2315fd16be8610396d6415292f4863f90b8dd6`); its 11/11 local stub-harness result is not Android Gradle/JUnit CI. It is not wired into the route path and must remain display-only; raw accepted fixes remain the only metric source.
- #215 is closed; its GPS/session source was superseded by #264, already in the canonical lineage. #284 is the current active ActivityTrackingService fallback/generation-guard handoff.
- No formal active lease registry or lease PR was found. #93's ownership note is not treated as permission to edit its claimed MainActivity surfaces concurrently.

## Health Connect / anti-cheat integration

PR #285 was integrated separately because it was disjoint from GPS files and passed exact-head CI. Canonical squash merge: `baab97b1ff1e2c4f0ca0bba7b1921ad9e5ff43b7`; tested PR HEAD `c8d464b86576db172d03a734ca9a119bd47631fb`; exact-head run [42827029570](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42827029570).

- Tests: product 60/60, source-contract 34/34, backend 29/29, Android unit 225/225; lint, debug assemble and release bundle tasks succeeded.
- Artifact 13769139185 ZIP SHA-256: `d5a85a4091d762009df90c9fc9db1e492270b84e96a0d3d4e967e6183a7d18a5`.
- QA APK SHA-256: `806855fe3bcb9fb0ff12fce2b52949e957e48898c01f4a65bb95f5714bbdfb0b`.
- Unsigned validation AAB SHA-256: `3a7dd174d7695a1b27ac1a8a497ea439f382a2d3be948c3b82ba0eadcd95dddc`; downloaded archive independently hashed and no JAR signing entries found.
- The change wires the existing swimming eligibility policy into typed Health Connect ExerciseSessionRecord ingestion. Swimming requires an approved writer, active/automatic recording, valid interval, stable record ID and compatible watch/fitness-band metadata; phone-only, ring, chest-strap and unknown device classes fail closed.
- This is provider/device metadata provenance, **not cryptographic wearable attestation or physical sensor proof**. No physical watch/Health acceptance, reward payout, new permission, Play declaration or privacy PASS is claimed.

PR #282's Health metric null-versus-zero UI correction remains open/draft. Its exact head `3291e076510b5626dd8ee931dad84728ba01605d` passed run 42506335882, but its shared `app.js` ownership and stale base are unresolved. PR #93 Health Services reader and #188 permission-scope guard remain open; exact-head Android CI, privacy/declaration and physical grant/revoke/no-data/error checks remain gates.

## Live Play and release chain

Latest successful independent Play state readback is [run 42405709027, attempt 4](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42405709027), observed 2026-11-10 18:31:07 UTC. Artifact 13791872061 ZIP SHA-256 `bffbb6484802331c90f7b49ba029ab373f63cc2f13d94d10b980907008e775ee` was downloaded and independently rehashed; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.

- Internal track: versionCode 51019, completed.
- Alpha track: versionCode 51007, draft.
- Production: not listed / not verified.
- `uploadAttempted=false`; `commitAttempted=false`.
- Existing signed 51019 AAB SHA-256 remains `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5`, built from older source lineage `76053bd9127c38d8065eb7ac250bdeb34ab67854`. This is the current Play release artifact, not an artifact for canonical source `baab...` or GPS candidate `427ffe...`.
- The #284 and #285 AABs are unsigned validation artifacts only. No new signed AAB exists for current source, and the Nov 9 Play state probe is not a readback of either candidate artifact.

Keep versionCode `51020` unallocated. The next code must be greater than 51019 and allocated only after owner Maps API/key prerequisites, exact-head Android CI on the final combined source and physical P0 pass. Production remains NOT_VERIFIED until policy/privacy and physical gates pass.

## Device and owner Maps gates

- Current Desktop Commander check reports `localhost` OFFLINE; the 2026-11-10 20:31 Cairo recheck saw it last online about 8 hours earlier. Last known phone identity is Samsung SM-A217F / Android 12 with Play package `com.topherofit.thf.pulse`; last recorded device-wide `location_mode=0` was 2026-11-09. Current phone/session state is unknown. Preserve the existing install and any unknown live session.
- No ADB device was available. No install, launch, Stop, pause/resume, session action, settings change or activity-data read was attempted. Physical GPS stationary-drift, measured-route, background/screen-off, notification, pause/resume and process-death P0 remain NOT RUN.
- Latest owner Maps preflight remains run 41684077962 (2026-11-03): Maps Android Backend and API Keys APIs enabled, key-inventory permission denied, no package/SHA-restricted Android key visible, no billing account linked. Native Google Maps basemap/traffic/transit remains owner-gated. No permission retry, key, billing, secret or paid infrastructure change.

## Session, metrics, steps and competitions

- Foreground activity service/checkpoint and navigation persistence exist in source, but real screen-off/background/process-death/pause/resume/Stop behavior and notification metrics have not been revalidated on the physical phone.
- The 1-second GPS-to-map refresh is local presentation only. It is not route sync, cloud backup or an upload interval.
- DailyStepLedger core exists, but the all-day sensor observer, durable day-boundary owner and daily dashboard remain unwired. Current step observation remains session-scoped; do not claim all-day daily averages or anti-cheat PASS.
- Competition backend #269 remains merged source-only for strength volume (kg·reps). Scores remain `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED` and `rewardEligible=false`; no event is seeded, the admin key is not configured, and separate backend deployment is not independently verified. No competition payout or verified leaderboard claim.

## Route backup/sync gap

Completed GPS routes remain local-only. The inspected `persistFinishedActivity()` path writes route history to WebView local storage; the existing authenticated backend sync carries THF-created set/workout records only. No authenticated GPS route endpoint or cloud route upload was found.

Design-only document: [ROUTE_SYNC_DESIGN_20261110.md](ROUTE_SYNC_DESIGN_20261110.md). It defines separate default-off summary and precise-route consent, per-session opt-in, finished-session-only sync, bearer auth, per-user storage, idempotency, revocation/deletion, retention and tests. It explicitly keeps the one-second local map refresh separate. No route-sync implementation or cloud upload claim exists.

## Release decision

**HOLD.** No paid infrastructure, no version allocation, no signing, no Play write, no Production promotion. Preserve the unknown phone session. Keep #284 Draft until physical P0, owner Maps prerequisites and shared-file reconciliation are complete. Keep Health/privacy and competition reward gates closed until their exact source, backend, policy and physical evidence passes.