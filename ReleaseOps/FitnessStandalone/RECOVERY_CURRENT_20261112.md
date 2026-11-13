# TopHeroFit recovery checkpoint — 2026-11-12

Scope: **TopHeroFit only**. Source of truth: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.

## Canonical starting point

- Canonical branch: `agent/codex/fitness-recovery/20261023`
- Current canonical HEAD after this run: `8929d1ef76b119f442409db709d9e319cefba399`
- Prior canonical recovery: [RECOVERY_CURRENT_20261111.md](RECOVERY_CURRENT_20261111.md), blob `472c2bd39e4cf4d7b19b23cc60eb8f726af14553`
- Prior canonical GPS checkpoint: [GPS_MAP_QUALITY_20261111.md](GPS_MAP_QUALITY_20261111.md), blob `2a36f80f297f562320eec4b4244491205a3c0659`
- Newer GPS candidate checkpoint: [GPS_MAP_QUALITY_20261112.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/gps-open-source-stack-20261109/ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261112.md), blob `ab41c38249c87145fbf24791a64b8012f1f52b4b`. This is on PR #284's candidate branch, **not canonical**.

## Merged and exact-head tested this run

| PR | Canonical merge commit | Exact tested head | Exact-head CI |
|---|---|---|---|
| [#285](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/285) swimming record ingestion gate | `baab97b1ff1e2c4f0ca0bba7b1921ad9e5ff43b7` | `c8d464b86576db172d03a734ca9a119bd47631fb` | [42827029570](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42827029570) — success |
| [#286](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/286) source-scoped latest record-version deduplication | `3b65efa94709e3a60cc62113e19c92639e2a76b9` | `71a2863e51465ad587df8230269c1af4cbdf55d9` | [43028123167](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43028123167) — success |
| [#288](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/288) fail-closed Health record-type policy | `bb9a6d01251e5de2da73965c82d2c0220fc0206d` | `67b19f344964051e9ccb1c394eed37bd7f9e6003` | [43224407466](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43224407466) — success |
| [#188](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/188) exact Health permission-scope regression gate | `f59d059868bbc417e381ded98374c44f898cf629` | `5344cf74751e34f4b501e4b89137e06239a9ce42` | [43225828775](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43225828775) — success |
| [#289](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/289) offline motion/catalog/license integrity regression gate | `8929d1ef76b119f442409db709d9e319cefba399` | `953f521ea3f2bc9ad03ea6ac6d0549259fa0979b` | [43226464817](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43226464817) — success |

The final #289 candidate was rebased on top of #288 and #188 before its exact-head run. Its final tested tree therefore included all three changes.

### Build/test evidence

- #288: product 60, source-contract 34, backend 29; Android `testDebugUnitTest`, lint, debug APK and validation AAB passed.
- #188: product 64, source-contract 34, backend 29; Android unit, lint, APK and validation AAB passed. All four Health permission-scope assertions passed.
- #289: product 67, source-contract 34, backend 29; all three new motion mapping/license tests passed; Android unit, lint, APK and validation AAB passed.
- #289 QA APK SHA-256: `86d6040e8c451e5d49ca2a67500bebe663d99483377adff3e655ad53b275f250`
- #289 validation AAB SHA-256: `e1b5bb32e416a3cffde2bd841a4f4246ece1c9a571334c3dabbfb486bba59981`
- #289 artifact ZIP SHA-256: `5d3b619bf0ceced4be1b08a8ba32669ce98cbc5e045967fd78c27cef733566e1`
- QA package identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, `5.0.0-v2-alpha19-debug`. These are validation outputs only; no signing or Play upload.

PR #287 was closed without changes after the canonical branch readback proved its proposed `ActivityEvidenceAnomalyPolicy.kt` and test blobs were already present. Do not recreate that policy.

## Health Connect and source provenance

### Least-privilege permissions

Canonical Android manifest blob: `0969cdb2f18775f23e0870bf754612a04376895f`. It declares exactly:

- `READ_STEPS`
- `READ_EXERCISE`
- `WRITE_EXERCISE`
- `READ_DISTANCE`
- `READ_ACTIVE_CALORIES_BURNED`

`READ_HEART_RATE` remains absent. No additional Health permission was added in this run.

PR [#93](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93) remains Draft at head `1cc08cef7dae7f432275fd23960f4390a49db14c`. Its manifest blob `a3b24f09e6b0c8a67b0fee3e7578317cfe979092` contains 19 Health permissions, including 14 extra scopes. Current compare from canonical: 2 ahead / 322 behind; merge base `cb425fef23b8541499acb02cecd8b86312b0eb34`. It has no exact-head workflow run. The merged #188 product test now enforces the exact five-permission allowlist and will fail on #93's current expanded manifest.

Do not expand scopes until each data type has a real surfaced feature, user purpose, minimum-necessary rationale, Play Health declaration, privacy/Data Safety reconciliation and physical grant/no-data/revoke/error evidence.

### Record integrity

- #285 requires a reviewed Health Connect writer, compatible watch/band metadata, stable record ID, active/automatic recording and valid session interval for verified swimming. Metadata is not cryptographic hardware attestation; no physical watch proof is established.
- #286 makes metric aggregation and provenance use the same latest source-scoped record version.
- #288 allows only stable Steps, Distance and Active Calories record types or a typed/stable Exercise Session record to continue through reward verification. Unknown future record types remain supported for diagnostics but reward-ineligible; metric/session type mismatches fail closed.
- Canonical `HealthRecordEvidencePolicy.kt` blob after #288: `b0e32513067193e724e3bd1b8efeddf6d698af1b`.
- Canonical regression test blob: `cdae35ca6b709084fffb16e4e4ae3a17b2271428`.

### Remaining Health integration blockers

1. Canonical `HealthConnectRepository.kt` blob `618836257a2650acb746954fd9bb0566827759f4` retains `HealthSnapshot.recordEvidence`, but canonical `MainActivity.kt` blob `b97e08756d5aba515c30f2d1a05517f56631ebf0` dispatches aggregate metrics, provider-level origins and counts only; it does not serialize per-record evidence to the WebView. PR #93 owns the MainActivity/reader boundary. Prefer privacy-safe stable hashed keys, not raw provider record IDs.
2. Phone ↔ Health walking/running/cycling reconciliation remains policy-only. The current `HealthConnectRepository.readRecent()` does not receive phone-session evidence or invoke the merged #117 time-proximity policy. Same-source records must deduplicate; nearby independent sessions from one source must remain separate; swimming must never time-deduplicate without stable identity.
3. Optional heart rate has no canonical reader or permission. Do not request it until a real feature, genuine source path and separate declaration/physical gates exist.

## GPS and anti-cheat ownership boundary

- Canonical GPS checkpoint remains the 2026-11-11 document above.
- PR #284's 2026-11-12 candidate app-source SHA is `68894a585e78df0a8d7b40cc68fa4f29acf10c9c`; exact-head Android run [43172404327](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43172404327) passed.
- PR #284 current branch head: `274155eafdfff381009ef5814a621f32b225f1a8`; compare from canonical: 19 ahead / 19 behind, merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`; GitHub reports unmergeable. It remains Draft because `app.js` and `MainActivity.kt` ownership conflicts remain.
- Canonical `ActivityEvidenceAnomalyPolicy.kt` blob `5643da3f8999298193b39d55e1d6104a95daf746` and its test blob `7606f4254b6cd1bd9bad2b64496ded3887019a73` already exist.
- Canonical `ActivityTrackingService.kt` blob `14fc1d0c4978e1840536eb4e990c10d36d6f43e4` and PR #284 candidate service blob `dc4576ef005f64aafda9cf52ac36f45697a2e480` do not call `ActivityEvidenceAnomalyPolicy` or construct `ActivityGpsFix`. The policy remains disconnected from live accepted GPS fixes.
- Do not edit GPS/activity tracking native files in this lane. The GPS owner must map actual raw Android Location provider, elapsedRealtimeNanos, coordinates, horizontal accuracy and OS mock flag into the policy before distance/pace/competition credit. Never use display-smoothed points as evidence.

Latest GPS checkpoint records Desktop Commander localhost offline (last seen 44 hours before that check), no ADB device, unknown current phone/session state, and physical GPS/background/session P0 as BLOCKED_NOT_RUN. Do not install, launch, stop or replace an unknown active session.

## Exercise catalog, programs and demonstrations

### Bilingual catalog

- Canonical `exercises.json` blob `425f0dab3fa1b0718cf84dd818a26d3585881718`: 112 unique exercise IDs; 84 records have different English and Arabic instruction-step counts.
- PR #160 branch blob `432b30edfd0a10d726f71debe17296a9b0a2c236` reduces step-count mismatches to zero, but its base is a noncanonical catalog stack, it has no exact-head CI, and semantic defects remain: `step-up-with-knee-raise` still reuses squat cues; `medicine-ball-scoop-throw` reuses hip-hinge/deadlift-style cues.
- Keep catalog, builder, generated manifest and active workout UI ownership with the existing stacked exercise PRs (#257/#259/#260 and related work). No catalog source was edited in this run.

### Program prescription

- Canonical `programs.json` blob `013022b7cb647e17b66cd2c9f3aad20c39050062`: 26 programs, 94 sessions, 470 exercise references, no unknown exercise IDs.
- 232 references have positive `durationSeconds`; all 232 carry non-null `targetRir`. 226 point to catalog exercises with `tracking.rir=false`.
- PR #213 candidate removes RIR from its 259 timed references, but its own exercise/program pair still has six `superman` references timed at 30 seconds while the exercise catalog says `durationSeconds: null` and `reps: 8–12`.
- PR #213 is based on a noncanonical branch, 190 ahead / 177 behind current canonical, and has no exact-head workflow run. Its #214 logger follow-on and other program PRs remain stacked. No program/catalog/UI source was edited.

### Offline demonstrations

Canonical motion manifest blob: `16fb02e9f87e7930fa6b779f8f6440f11d8ae1ab`.

- 7 mapped motion entries: 5 offline videos and 2 reviewed 16-frame sequences.
- All 7 keys resolve to real catalog exercise IDs.
- Video-license ledger covers the 5 videos with wger / CC-BY-SA-4.0 attribution.
- 105 other exercises still use reference-frame demonstrations, not full-motion video.

Merged #289 adds `fitness-v2/product/tests/test_offline_motion_mapping_integrity.py`. It verifies catalog-ID mapping, exact video/license/asset SHA agreement, source/author/license metadata, local asset existence and frame-sequence review/timing. It does not claim semantic content review or add new media.

## Play, privacy and release gates

Latest recorded Play readback remains 2026-11-10:
- Internal 51019: completed.
- Alpha 51007: draft.
- Production: not verified.
- VersionCode 51020: unallocated.

No new Play readback, declaration, upload, signing, listing change or promotion occurred. No Health declaration/privacy/Data Safety evidence or physical Health Connect acceptance is established. Physical grant/partial grant/no-data/revoke/error tests and real compatible-watch swimming validation remain NOT RUN.

## File ownership and next-run order

- #93: Health reader, MainActivity, manifest and rationale — keep held; per-record provenance serialization and phone-session reconciliation must be resolved here.
- #284: GPS/activity tracking native files — GPS owner only; this lane must not edit them.
- #282 and other exercise UX/demo PRs: shared `app.js` ownership.
- #160 and related PRs: shared exercise catalog/builder/manifest.
- #213/#214 and related PRs: shared program prescriptions and workout logger.
- #209 and related demo PRs: motion runtime manifest/asset ownership.

Next run should: (1) re-read this checkpoint and current PR heads; (2) resolve #93's provenance/UI and reconciliation handoff without broadening permissions; (3) keep GPS anomaly integration with the GPS owner and wait for physical P0; (4) consolidate bilingual catalog/program stacks onto canonical with semantic tests; (5) add only properly licensed, correctly mapped full-motion clips after motion-manifest ownership is free; (6) keep Play Health/privacy and physical tests as hard gates.

No GPS/activity-tracking native file, release version/workflow/signing file, Play state, device state or user data was changed in this run.

## 2026-11-12 19:44 Cairo — current integrator recheck

This addendum supersedes stale canonical-head, PR and GPS evidence fields above. Scope remains TopHeroFit only.

### Canonical source and exact-tree CI

- Canonical branch HEAD before this evidence-only refresh: `a4b853a231c5ee88741a23d581162e727d02d48f`.
- That commit changes only this recovery document; its parent/app-test commit is `8929d1ef76b119f442409db709d9e319cefba399`.
- The current canonical app/test tree is `7d84cab1d05e2ec111332b61457db07d80c17f53`, identical to tested PR #289 head `953f521ea3f2bc9ad03ea6ac6d0549259fa0979b`.
- Exact-tree CI: [43226464817](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43226464817) — SUCCESS. Product 67/67, source-contract 34/34, backend 29/29, Android 236/236, 0 failures/0 ignored; lint, assembleDebug and bundleRelease passed.
- Downloaded artifact 13948107645 and independently recomputed ZIP SHA-256 `5d3b619bf0ceced4be1b08a8ba32669ce98cbc5e045967fd78c27cef733566e1`; APK SHA-256 `86d6040e8c451e5d49ca2a67500bebe663d99483377adff3e655ad53b275f250`; validation AAB SHA-256 `e1b5bb32e416a3cffde2bd841a4f4246ece1c9a571334c3dabbfb486bba59981`. Independent `jarsigner -verify` reports the AAB is unsigned. This is validation identity 51019 only, not a release artifact.
- Canonical push run [43227243445](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43227243445) on merge commit `8929d1e...` succeeded at the changed-app job but skipped deterministic Android build on the canonical branch. Exact tree equality to #289's fully tested head is the Android validation basis; no new Android build artifact was produced by that push run.
- Release ledger was refreshed in commit `a29ec486a80598ea66ae246e718700250d84b7e4`; the current recovery update follows it.

### GPS / Maps handoff — PR #284

- Latest GPS checkpoint: [GPS_MAP_QUALITY_20261112.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/gps-open-source-stack-20261109/ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261112.md), blob `ab41c38249c87145fbf24791a64b8012f1f52b4b`. It is on the candidate branch, not canonical.
- PR #284 branch HEAD: `274155eafdfff381009ef5814a621f32b225f1a8`; tested application/test SHA: `68894a585e78df0a8d7b40cc68fa4f29acf10c9c`.
- Exact-source run [43172404327](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43172404327) — SUCCESS: product 60/60, source-contract 40/40, backend 29/29, Android 230/230, 0 failures/0 ignored; lint, assemble and bundle passed.
- Artifact 13922608138 ZIP SHA-256 `76aa03815f80106e962aa0dbd4df7c09fb41d762aa67e1895534d954dce6dca6`; APK SHA-256 `6ef8aff880b65ac86ccc76ae21d93c3d73a22211b045653455154ae7d2dde875`; unsigned validation AAB SHA-256 `cb8a4e0ad2e77d46cf4eb4964a534d1540b7665b9ff9dcf97f4c326d85489e1c`. ZIP was downloaded and independently rehashed; `jarsigner -verify` confirms the AAB is unsigned.
- Requested historical run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) is SUCCESS on old head `3fcbe6acbb4dc660284c74c8392818996e1de7ee), not current source. Artifact 13707718861 ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`; APK SHA-256 `08a5730096d1cfc97193e47726f90e533f89d9e0cc3c606faae467b46e72e9b5`; unsigned AAB SHA-256 `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`; Android 223/223. Historical artifacts were downloaded and rehashed.
- PR #284 remains Draft/unmerged. Current compare from canonical: 19 ahead / 20 behind, merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`; GitHub reports `mergeable=false`. Keep it Draft.
- The 42694199295 failure is the prior truncated API upload of `MainActivity.kt`; the recovery record documents the full 1,146-line restoration and `motionSnapshot` presence. No new phone install or activity action was taken.
- Keep the free Leaflet/WebView map: attributed OSM streets, OpenTopoMap terrain, EOX Sentinel-2 cloudless 2016 satellite/hybrid. No archived Google Maps Rx, Maps SDK billing, API key or paid infrastructure.

### Current ownership holds and anti-cheat wiring

- No explicit current lease registry file or lease issue was found. PR #93 claims `MainActivity.kt`; treat it as a hold. PRs #282/#216 and exercise UX handoffs overlap `app.js`; #284 also changes `app.js`. Shared files are not assumed free.
- #93 remains Draft, has no exact-head CI, and adds 14 Health read scopes (19 total) versus the merged five-scope allowlist enforced by #188. Its branch is 2 ahead / 323 behind current canonical. Do not merge it.
- #282 remains Draft; exact validation run 42506335882 passed (62 product / 34 source-contract / 29 backend / 218 Android), but it overlaps #284/#216 in `app.js`; no combined-head CI.
- #216 is open on a noncanonical base and has no exact-head workflow run. #248 is Draft, display-only, has no exact-head Android CI and is not connected to metric calculations.
- #188 (least-privilege permission gate), #288 (fail-closed Health record types), #286 (source-scoped latest-record dedup) and #285 (swimming wearable metadata gate) are merged after their recorded exact-head CI. #289 is merged as the test-only offline motion/catalog/license integrity gate.
- The pure `ActivityEvidenceAnomalyPolicy` and its tests exist on canonical. Neither canonical nor #284 `ActivityTrackingService.kt` references `ActivityEvidenceAnomalyPolicy`, `ActivityGpsFix` or `assessSegment`. The service reads provider, `elapsedRealtimeNanos` and the Android mock flag, but live accepted fixes are not yet passed into the policy. Do not credit distance, pace or competition from display-smoothed points; the GPS owner must wire raw provider/time/coordinates/accuracy/mock evidence before anti-cheat is considered integrated.

### Health, competitions and route sync

- Health Connect canonical permissions remain exactly five: Steps, Exercise, Exercise write, Distance and Active Calories. Heart-rate access remains absent. #93's extra scopes fail the merged #188 allowlist.
- #269 is merged as a backend-only provisional strength leaderboard. The admin route remains disabled without owner-managed `THF_COMPETITION_ADMIN_KEY`; no event is seeded and deployment is not independently verified. Scores are `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED`, `rewardEligible=false`; no THF rewards/payouts are authorized.
- Finished GPS route history remains in WebView localStorage. Route sync remains DESIGN ONLY: no authenticated route endpoint, no precise-location upload. Do not implement or claim cloud backup until #284 is physically validated and the separate consent, retention, deletion, backend and privacy gates are tested.

### Phone, Play and release boundary

- Desktop Commander `localhost` is OFFLINE; last seen about 55 hours before the 2026-11-12 19:44 Cairo check. Current SM-A217F session state is unknown. Last recorded device-wide `location_mode=0` is from 2026-11-09 and was not changed. No ADB, install, launch, Stop, pause/resume or settings action was taken.
- Latest successful read-only Play state readback remains run [42405709027, attempt 4](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42405709027), observed 2026-11-10 18:31:07 UTC. Downloaded artifact 13791872061 ZIP SHA-256 `bffbb6484802331c90f7b49ba029ab373f63cc2f13d94d10b980907008e775ee`; embedded JSON SHA-256 `09e7a346e5e1c893d4323d20105d8f4d63`; both independently verified again on 2026-11-12.
- Readback: Internal 51019 completed; Alpha 51007 draft; Production not listed/not verified; `uploadAttempted=false`, `commitAttempted=false`. No newer successful Play readback was found. This is the latest evidence, not a new 2026-11-12 Play observation.
- The recorded signed 51019 AAB SHA is `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5`, but its original artifact is no longer retrievable for fresh rehash. The new GPS and canonical validation AABs are unsigned and unuploaded.
- VersionCode 51020 remains unallocated. Keep release HOLD until owner-controlled release API/signing prerequisites, final combined-source exact-head Android CI, physical GPS/session P0, Health/privacy/Play declaration and policy gates pass. Production remains NOT VERIFIED.
- No merge, signing, Play write, Production promotion, device mutation, paid infrastructure or other-project work occurred in this recheck.

## 2026-11-13 — GPS fallback resilience handoff

### Canonical start and isolated candidate
- This run re-read the historical `GPS_MAP_QUALITY_20261101.md`, the latest canonical `GPS_MAP_QUALITY_20261111.md`, and this current recovery checkpoint before editing.
- Canonical branch base used for the isolated GPS handoff: `dedd5f39001781c19e7e19bdee8f44e2fa97b01d`. It is 11 commits after the prior app-source anchor `3b65efa94709e3a60cc62113e19c92639e2a76b9`; the intervening tree changes did not touch the five GPS/Activity files in this candidate.
- New clean PR: [#292](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/292), branch `agent/codex/gps-fallback-resilience-20261113-r2`, source/test HEAD `cb97dc0b66299825e6a02dd91ec53e369667bb74`.
- Changed files are limited to `ActivityTrackingService.kt`, `ActivityLocationFallbackPolicy.kt`, `ActivityLocationFallbackPolicyTest.kt`, `GpsFixPresentationPolicy.kt`, and `GpsAccuracyPresentationPolicyTest.kt`. No `app.js`, `MainActivity.kt`, `test_source_contract.py`, Health/anti-cheat, exercise-catalog, workflow, release-version, signing or Play file is in this PR.
- The older first attempt PR #291 was closed before merge because it was 11 commits behind the live base. #292 was recreated from the exact current base and compares 5 ahead / 0 behind. Keep #292 Draft until exact-head CI and physical P0 are complete. Older mixed PR #284 remains Draft/held for shared UI-file ownership; do not merge it as a whole.

### Material Activity Engine / GPS changes
- Fused Location requests use per-request callback identity and a monotonically increasing session generation. Late success/failure after pause, stop or session replacement cannot revive location collection; stale callbacks remove only their own registration.
- Framework provider selection respects fine/coarse permission. Approximate-only permission cannot request `GPS_PROVIDER`.
- A silent GPS provider falls back to `NETWORK_PROVIDER` after the bounded no-fix/stale window; a failed GPS registration can fall back immediately when coarse permission and network provider are available.
- The selected provider is retained only while still enabled. Provider enabled/disabled callbacks trigger immediate re-selection; if neither eligible provider exists, framework updates are removed and selection state is cleared.
- Provider changes reset the measurement anchor, observed/accepted accuracy and current speed; route distance is not bridged across sources.
- Repeated framework registration failures use bounded 4s/8s/16s/30s retry backoff.
- Accepted accuracy is exposed only for a fresh `ready` fix and only when finite and positive. Missing, invalid, stale, filtered and paused states return no accuracy value, not a fabricated zero.

### Exact source/test evidence
- Exact GitHub source blobs:
  - `ActivityTrackingService.kt`: `991d13677d2b23d1aa5fdd0530ae3d87a2a6999a`
  - `ActivityLocationFallbackPolicy.kt`: `df94187062dd8f58aaf8574cfc66f843f89e3634`
  - `ActivityLocationFallbackPolicyTest.kt`: `8f9cedbcd16750e67f92c7820a267b1b204ada8f`
  - `GpsFixPresentationPolicy.kt`: `e0471db0b13da797020175563a71c9534b6e0e3e`
  - `GpsAccuracyPresentationPolicyTest.kt`: `ac17d99d3b3b0ecf8328e9e2c4c153bd7e9c5fad`
- Local Kotlin compilation of the exact fetched policy sources passed: 23 fallback/provider assertions plus 12 accuracy-presentation assertions.
- Exact-fetched-source contract audit passed 13/13 checks, covering callback generation, late callback removal, permission-aware provider choice, provider re-selection, retry bounds, source reset and truthful accuracy.
- Exact-head GitHub Android run [43382459916](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43382459916) completed SUCCESS on source/test SHA `cb97dc0b66299825e6a02dd91ec53e369667bb74`. Product 67/67, source-contract 34/34, backend 29/29, Android 250/250 (0 failures, 0 ignored); API 36, lintDebug, assembleDebug and bundleRelease validation passed. Lint: 0 errors, 16 warnings, 1 hint.
- Artifact `14017730574`; downloaded ZIP SHA-256 `e4f5c286137856df5c503cb3140eaff48608dd594004b6736637f5241fdcb149`; QA APK SHA-256 `ee26a73729eee644a279716e2b457c85a68fe26cea3d9663b96dc9e43c4f3e36`; validation AAB SHA-256 `fb1e66c0e2570ddd14d00367890da2ed95f6374b08239e5f1d537366c54b7b80`. ZIP was downloaded and independently rehashed; `jarsigner -verify` reports the AAB is unsigned. Package `com.topherofit.thf.pulse.qa`, validation versionCode 51019 and versionName `5.0.0-v2-alpha19-debug`. No signing or upload.
- Final branch HEAD after documentation-only checkpoint/report commits: `e5fb687872285a9b185145aca5d90b9f45be2206`; the application/test source SHA remains the exact tested `cb97dc0b66299825e6a02dd91ec53e369667bb74`.

### Physical device and Maps gates
- Fresh Desktop Commander inventory reports `localhost` OFFLINE, last seen 68 hours ago. No ADB device is attached. No install, launch, Stop, pause/resume, location-setting change or activity-data read was attempted; preserve the unknown phone session. Physical stationary-drift, measured-route, screen-off/background, notification and process-death P0 remain NOT RUN.
- The canonical map decision remains the no-billing Leaflet/WebView stack: attributed OpenStreetMap streets, OpenTopoMap terrain and EOX Sentinel-2 cloudless 2016 imagery.
- Historical preflight `41684077962` recorded Maps Android Backend/API Keys APIs enabled, but key-inventory permission denied, no package/SHA-restricted Android key visible and no billing account linked. No permission retry, key creation, billing, payment method or paid infrastructure change occurred. Native Google basemap/traffic/transit is not present or claimed; revisit only after owner prerequisites and an explicit repository map-stack decision.

### Release boundary
- No release version, workflow, signing, Play, Health/anti-cheat or exercise-catalog file changed.
- VersionCode 51020 remains unallocated. No APK install, AAB signing/upload, Play write or Production promotion occurred.
- Physical-device QA and Play acceptance remain unverified.
