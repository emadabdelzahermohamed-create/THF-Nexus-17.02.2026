# TopHeroFit canonical recovery — 2026-11-16

> **Authoritative current update: 2026-11-16.** This update supersedes all time-sensitive branch heads, PR comparisons and CI state in the retained 2026-11-15 checkpoint below. Repository remains the sole source of truth: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.

## Canonical state and completed Health delivery

- Canonical branch: `agent/codex/fitness-recovery/20261023`.
- Latest application merge: PR #299, squash merge commit `16fd1b16ef9d3592ef031298e059ed730ff92f92`.
- PR #299 exact tested source: `ed46cd03e0f71788ded660bd288852a9dca5a63c`.
- Parent at test time: `a4ccae5bd7f518ea906b1267c820f4296fefab63`.
- Post-merge comparison: exactly 1 commit ahead, 0 behind, exactly two files changed:
  - `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/HealthSportMapper.kt`
  - `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/HealthSportMapperTest.kt`
- Canonical blob SHAs:
  - HealthSportMapper.kt: `c6e149841f07946f46c768f28ec4f8ba34bc1258`
  - HealthSportMapperTest.kt: `9ae88535e44fcf75fb1c678d447e3851f4a1f2fa`
- No GPS/activity-tracking native files, manifest, MainActivity, app.js, catalog/program data, release version, workflow, signing or Play files changed in this merge.

## PR #299 — precise Health Connect exercise/program mapping

Merged: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/299

The writer supplies a broad section/program sport label plus the exercise/program ID. The old mapper always preferred the broad label, which caused concrete data errors:
- `walking-treadmill` under the running section was written as RUNNING instead of WALKING.
- `jogging-treadmill` and `running-treadmill` were written as generic RUNNING instead of RUNNING_TREADMILL.
- `bicycling-stationary` and `recumbent-bike` were written as BIKING instead of BIKING_STATIONARY.
- `rowing-stationary` and `elliptical-trainer` under HIIT were reduced to the broad HIIT type.
- `swim-dryland` and `swim-strength` were written as in-water SWIMMING_POOL despite their actual dryland strength prescriptions.

Known, unambiguous exercise/program IDs now take precedence; unknown IDs retain the existing broad-sport fallback. Dryland swim-support programs map to STRENGTH_TRAINING. This does not relax swimming eligibility: actual swimming still requires reviewed provider and compatible trusted wearable metadata.

### Exact-head CI and artifacts

Run 43881473640: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43881473640 — **SUCCESS** on exact source SHA `ed46cd03e0f71788ded660bd288852a9dca5a63c`.

- Product tests: 67/67.
- Source-contract tests: 34/34.
- Backend tests: 29/29.
- Android unit tests: 256/256; 0 failures; 0 ignored.
- Android API 36 setup, Kotlin compile, lintDebug, assembleDebug and bundleRelease validation: PASS.
- Gradle: BUILD SUCCESSFUL in 2m 1s.
- Lint: 0 errors, 16 warnings, 1 hint.

Artifact 14231754743 was downloaded and independently rehashed:
- ZIP SHA-256: `357e30ef3c6325cfd04ade7922da8990a9c596c1f99918330b1697a8e5da6713` (matches GitHub digest).
- QA APK SHA-256: `d892fd2d6fb60396276b27ee5024ebc2dc97a2ada9b9e771fc629b888a10f166`.
- Validation AAB SHA-256: `e2ea5d4b5c39b320e3435975736992af472db9d77114e82927b55391088aa7c1`.
- `jarsigner`: `jar is unsigned`.
- QA package: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. Validation only; never promote.

## Discarded false-positive candidate

PR #298 was closed unmerged: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/298

The proposed locale issue was invalid. Kotlin `String.lowercase()` uses invariant-locale Unicode mapping, so the existing implementation was already locale-independent. No source from #298 was merged. Do not count it as a delivered change.

## GPS checkpoint and ownership handoff

Latest GPS candidate: PR #297, https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297

- Current branch HEAD: `d572bae1baea0ea01fdca91d39cc089a30378e90`.
- Exact tested application/test source SHA: `3e784616e96aa810a7a10ded60b33bcf2bf6b57d`.
- Exact-head CI run 43817464009: SUCCESS.
- Product 67/67; source-contract 34/34; backend 29/29; Android 271/271; 0 failures; 0 ignored.
- Android API 36, lintDebug, assembleDebug and unsigned bundleRelease validation passed; lint 0 errors, 16 warnings, 1 hint.
- Artifact 14203510974 ZIP SHA-256: `f92f30e3053dbeae1644c1bee2e5fa6141e986a1dd8a647ed23110c4f89887d8`.
- QA APK SHA-256: `1831a6ca336ae907482194d2e6bd85045e7f50b7087e84c898746b46235369ed`.
- Validation AAB SHA-256: `86fe46286ada5f60415c86cb3bebd14f5f965e85802be2fac184dc50848049b1`; unsigned.
- New GPS correction: an Android 12+ precise-to-approximate permission downgrade switches an active framework GPS subscription to eligible NETWORK_PROVIDER on the next four-second watchdog poll, rather than waiting for the normal no-fix timeout. Coarse permission and NETWORK_PROVIDER are required; provider changes do not bridge distance.
- The two commits after the tested source SHA are checkpoint-documentation only; no app/test source changed after the tested SHA.
- After PR #299 merged, current compare against canonical `16fd1b16ef9d3592ef031298e059ed730ff92f92` is 14 ahead / 1 behind. PR-info currently reports mergeable=true; keep Draft and rerun exact-head CI on the combined current canonical tree before merging.
- PR #297 changes eight GPS source/test files plus its two GPS/recovery checkpoint documents. These are disjoint from PR #299's two HealthSportMapper files.
- GPS owner was notified of the new canonical base and the required combined-head validation. No GPS-owned file was edited in this run.
- `ActivityEvidenceAnomalyPolicy.assessSegment` remains unwired in the live tracking service. Do not claim full anti-cheat or location attestation.

Latest GPS checkpoint on the GPS candidate branch (not canonical): `ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261116.md`, blob `3c2957db75a6a209a6b1c255c7d04f761712220c`. The physical P0 remains BLOCKED_NOT_RUN.

## Current open PR ownership (fresh comparison against canonical 16fd1b1)

| PR | Current comparison | Ownership / decision |
|---|---:|---|
| #93 | 2 ahead / 354 behind, diverged, 12 files | Health Services/MainActivity/manifest owner; still requests 19 Health scopes; blocked |
| #282 | 2 ahead / 93 behind, diverged, 2 files | Health metric truthfulness in app.js; shares app.js with #216; blocked pending rebase/combined CI |
| #160 | 53 ahead / 209 behind, diverged, 17 files | Bilingual exercise catalog and builder/tests; reconcile with #213 before integration |
| #213 | 190 ahead / 209 behind, diverged, 49 files | Program/RIR and shared catalog/UI data; overlaps #160 and #224; do not merge wholesale |
| #224 | 153 ahead / 209 behind, diverged, 36 files | Offline active-workout demo UI; overlaps #160/#213 and app.js |
| #284 | 19 ahead / 51 behind, diverged, 13 files | GPS/map UI and native overlap; not this lane |
| #297 | 14 ahead / 1 behind, diverged, 10 files | GPS owner; keep Draft until exact combined-head CI and physical P0 |

Shared ownership remains explicit:
- GPS native files: #297 / prior #294 lineage and #284; do not edit here.
- MainActivity/manifest/Health Services bridge: #93.
- app.js: #282 and #216; #224/#284 also overlap it.
- Catalog/program builders and JSON/JS data: #160/#213/#224 overlapping ownership.
- HealthSportMapper.kt and HealthSportMapperTest.kt: now canonical from #299; no overlap with current listed PRs.

## Health Connect permissions and evidence boundary

Canonical Android manifest blob remains `0969cdb2f18775f23e0870bf754612a04376895f` and contains exactly five Health Connect scopes:
1. READ_STEPS
2. READ_EXERCISE
3. WRITE_EXERCISE
4. READ_DISTANCE
5. READ_ACTIVE_CALORIES_BURNED

READ_HEART_RATE remains absent. No permission was added or broadened by PR #299.

PR #93 still requests 19 scopes, including 14 beyond the reviewed five-scope baseline. It must rebase, restore the five-scope allowlist and pass exact-head CI before consideration. The current MainActivity/WebView bridge still does not expose the privacy-safe per-record `recordProvenance` contract; PR #93 owns that bridge. No raw Health record IDs should cross it.

No physical Health Connect, real watch, heart-rate sensor or swimming record evidence was generated. Swimming remains eligible only with compatible reviewed wearable metadata; metadata is not cryptographic hardware attestation. Heart rate remains optional and unavailable until a genuine permitted source exists.

## Catalog, programs and offline demonstrations

The latest canonical catalog/program inventory retained from the previous checkpoint:
- 112 exercises.
- 84 Arabic/English instruction step-count mismatches; generic fallback cues still require movement-specific correction.
- 26 programs, 94 sessions and 470 exercise references.
- 232 timed references; 226 timed references still carry RIR despite their catalog entries disabling RIR.
- Six timed Superman prescriptions remain inconsistent with the catalog's repetition-based definition.
- Offline demonstrations: 5 video clips, 2 reviewed 16-frame sequences, 105 reference-only two-frame exercises.

PR #160 and #213 remain divergent and share generated catalog/program builders and data. PR #224 overlaps the same UI/demo surfaces. Reconcile one canonical data/build chain before integration; do not merge stacked branches wholesale. No new motion asset was created in this run.

## Physical and Play gates

- Latest device check recorded in the November 16 GPS candidate checkpoint: Desktop Commander localhost offline; last known handset Samsung SM-A217F / Android 12; current device/session state unknown. No ADB, install, launch, Stop, settings or activity-data action was performed.
- Physical P0 remains BLOCKED_NOT_RUN: stationary drift, measured walking/running/cycling routes, approximate-only permission transition, screen-off/background continuity, notification controls, process-death restore, Health Connect permission grant/revocation, and compatible physical wearable/swimming evidence.
- Latest Play readback retained from 2026-11-15: Internal 51019 completed; Alpha 51007 draft; Production not verified. No fresh Play readback was obtained in this run.
- VersionCode 51020 remains unallocated.
- No release version, workflow, signing, Play listing, upload, track or Production state was changed.

---
# Retained previous canonical recovery — 2026-11-15

> Historical checkpoint retained below for audit. The authoritative current state is the 2026-11-16 update at the top of this file.

## Current canonical state

- Repository: emadabdelzahermohamed-create/THF-Nexus-17.02.2026 only.
- Canonical branch: agent/codex/fitness-recovery/20261023.
- Canonical branch head before this evidence checkpoint: a8692a06ff93a7bb1b293f9eac986402f3f020c6.
- Canonical application merge: PR #296 at 1e38da33ba16e9fa6a3276606a1130ff8f95a454. The only application/test source change since that merge is the disjoint GPS PR #294 branch; it is not merged.
- A comment-only read-only Play probe trigger was committed at a8692a06ff93a7bb1b293f9eac986402f3f020c6. No workflow logic or app code changed in that trigger.

## GPS: PR #294 is the selected native handoff

- PR: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/294
- New head after force-with-lease rebase: 71364e31f4f631dc2593f38b15a8b92626aacdfe.
- Parent/base at test time: a8692a06ff93a7bb1b293f9eac986402f3f020c6.
- Comparison at test time: 1 ahead / 0 behind; exactly eight GPS source/test files; GitHub mergeable=true; PR remains Draft.
- The rebase preserved only the eight GPS files and was disjoint from the canonical Health provenance merge and documentation changes. No app.js, Health, catalog or competition files were changed by this GPS rebase.
- Exact-head CI: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43739798192 — SUCCESS on 71364e31f4f631dc2593f38b15a8b92626aacdfe.
- Tests: Product 67/67; source-contract 34/34; backend 29/29; Android 270/270; failures 0; ignored 0. Android API 36, lintDebug, assembleDebug and bundleRelease validation passed. Lint: 0 errors, 16 warnings, 1 hint.
- Artifact 14171273756 independently downloaded and rehashed:
  - ZIP SHA-256: 2c240ae85e192cea642b85979573e2f1936b9c88a4abb986ac55921d389bff53
  - QA APK SHA-256: cc1a54f8cfea54fe7651ce70c33e7d92028f9f4bc514c4d55c807b36b2257bce
  - Validation AAB SHA-256: f082889f60b80d3103fe1d3d8a419f4d8c7d8711b803b11a05b44b4f9a033f99
  - AAB is unsigned; QA identity com.topherofit.thf.pulse.qa, versionCode 51019. It is not a release artifact and must not be promoted.
- PR #294 body was updated with the exact tested head, file list, hashes and remaining blockers. It remains Draft.

## Historical GPS map PR #284

- Current PR head: 274155eafdfff381009ef5814a621f32b225f1a8; base remains 9b5db58e809fa7d5e639bc4ee55df03d100467e8.
- Compared with canonical head at this checkpoint: 19 ahead / 49 behind, 13 changed files, GitHub mergeable=false. No exact-head CI exists for this current head.
- Historical run 42694452852 is SUCCESS on the requested old head 3fcbe6acbb4dc660284c74c8392818996e1de7ee, not on current PR #284 head. Its ZIP/APK/unsigned AAB hashes were downloaded and independently rehashed: ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c; 08a5730096d1cfc97193e47726f90e533f89d9e0cc3c606faae467b46e72e9b5; 08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e.
- The failed 42694199295 source-contract log shows the 1,000-line read truncation: motionSnapshot was not found in the truncated input. The current PR #284 MainActivity.kt was fetched in two windows (1,000 + 146 lines = 1,146 lines) and motionSnapshot is present.
- Keep #284 Draft as a separate Leaflet/WebView map UI reference. Do not merge wholesale: it overlaps #294 ActivityTrackingService, #93 MainActivity/source-contract, and #282/#216 app.js.

## Open PRs and file ownership

| PR | Current comparison from canonical | Status / decision |
|---|---:|---|
| #294 native GPS | 1 ahead / 0 behind at tested base | Draft; exact-head CI PASS; physical P0 still required |
| #284 map/WebView | 19 ahead / 49 behind | Draft; current head not tested; overlaps #294/#93/#282/#216 |
| #282 Health metric truthfulness | 2 ahead / 91 behind | Draft; exact head 3291e076 passed run 42506335882, but shared app.js conflicts with #216 |
| #93 Health Services | 2 ahead / 352 behind | Draft; no exact-head run; 19 requested Health scopes conflict with canonical five-scope allowlist |
| #216 active workout/session UI | 201 ahead / 207 behind | Open; no exact-head workflow; stacked app.js/exercise UI handoff |
| #248 GPS route smoother | 4 ahead / 186 behind | Draft; no exact-head workflow; helper/test only |

PR #296 is merged at 1e38da33ba16e9fa6a3276606a1130ff8f95a454 after exact-head CI 43721667918. It changes only HealthConnectRepository, HealthRecordProvenancePresentationPolicy and its test.

No formal current lease registry file was found in the canonical ReleaseOps/FitnessStandalone or Swarm paths. Shared resources are not assumed free:
- ActivityTrackingService/GPS native files: #294.
- app.js: #282 and #216; #284 also touches map UI there.
- MainActivity/source-contract/manifest: #93; #284 also touches MainActivity.

## Fresh Google Play readback — 2026-11-15

Read-only probe: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43739661313 — SUCCESS, observed 2026-11-15 17:11:22 UTC.

- Artifact 14171926791 ZIP SHA-256: 81a58281458d9b4137a0a4da0a155a203ae6466f960f112199016286a72b8e38.
- Embedded JSON SHA-256 (full 64 hex characters): 09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63.
- Independent download and hash verification succeeded.
- Internal: 51019 completed.
- Alpha: 51007 draft.
- Production: not listed in readback / NOT VERIFIED.
- uploadAttempted=false; commitAttempted=false. No Play track, listing or artifact was changed.
- The probe used the existing Workload Identity read path and created/deleted a temporary empty edit; it did not upload an AAB or commit a track.

## Phone and physical P0

Desktop Commander localhost is OFFLINE; last seen about 126 hours before the 2026-11-15 19:12 Cairo check. Last known phone is Samsung SM-A217F / Android 12. Current phone/session state is unknown. Last recorded device-wide location_mode was 0 on 2026-11-09; no setting was changed.

No ADB, install, launch, Stop, session-data or settings action was attempted. Physical GPS stationary drift, measured walking/running/cycling routes, background/screen-off, notification Pause/Resume/Finish, process-death restore, Health Connect grants/revokes and real wearable/swimming checks remain BLOCKED_NOT_RUN.

## Active GPS guardrails and remaining anti-cheat boundary

- PR #294 has a shared 30-second monotonic freshness gate for live fixes and checkpoint anchors. Stale/future/malformed restore anchors are not used; a live observation gap beyond 30 seconds clears the live anchor and distance accumulator without deleting the session or bridging distance.
- GpsFixGate rejects mock locations, invalid coordinates, poor accuracy, stale/non-monotonic fixes and sport-specific speed violations.
- GpsDistanceAccumulator requires source continuity, re-anchors on provider change or a gap beyond 120 seconds, applies endpoint-accuracy deadband, requires a persistent threshold-crossing excursion, and caps credited path length at 1.4 times net displacement.
- ActivityEvidenceAnomalyPolicy.assessSegment remains a separate tested policy and is not called by ActivityTrackingService. Do not claim complete anti-cheat, cryptographic location attestation or reward eligibility.
- Foreground service, START_STICKY, 10-second local checkpoints and notification controls exist in source, but background/process-death behavior has not passed physical P0.

## Health, metrics and competitions

- Canonical Health Connect manifest remains five scopes: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE and READ_ACTIVE_CALORIES_BURNED. READ_HEART_RATE remains absent.
- PR #296 adds a fail-closed Health Connect swimming presentation gate requiring reviewed provider, compatible watch/band metadata, active/automatic recording, stable record ID and valid exercise-session type/time. Phone, ring and chest-strap swimming records fail closed. This is metadata policy, not cryptographic wearable attestation; physical wearable validation remains open.
- PR #282's null-versus-zero fix is not merged. Canonical app.js still converts missing Health metrics to zero in renderHealthSnapshot; current PR #282 exact head passed 42506335882 but is 91 commits behind and shares app.js with #216.
- Competitions remain Strength Volume only. Server-side tests are present, but admin key is not configured, no events are seeded/production-verified, and rewardEligible remains false until physical activity verification.

## Route backup/sync remains separate

persistFinishedActivity() still stores finished route history in WebView localStorage (pulse.v2.activities). Existing authenticated workout sync carries workout metadata, not GPS coordinates; no authenticated route endpoint exists. ROUTE_SYNC_DESIGN_20261110.md remains DESIGN ONLY: separate summary and precise-route consent, per-session opt-in, finished sessions only, retention/deletion/revocation and no precise-location upload by default. No cloud route sync was implemented.

## Release decision

- Current Internal versionCode: 51019.
- Next versionCode 51020 is NOT allocated.
- The current signing contract requires the four Android upload-key secrets and a Play-bound upload certificate. The existing 51019 promotion workflow is pinned to old source 76053bd and versionCode 51019; it is not a 51020 workflow.
- The new Play probe proves read access only, not signing-secret presence or upload permission. No new signed AAB exists.
- No signing, version allocation, Play upload, track commit or Production promotion occurred. Production remains blocked by policy/privacy and physical gates.
- No paid infrastructure, Maps billing/key or unrelated project was used.

## Next safe order

1. Reconnect SM-A217F; inspect current session state before any install/Stop/settings action.
2. Run physical GPS P0 and background/session persistence checks on the exact QA candidate.
3. Keep #294 Draft until P0 and policy/privacy gates pass; do not merge #284.
4. Reconcile #282 and #216 shared app.js changes and run combined exact-head CI.
5. Keep #93 blocked until it is rebased to canonical five-scope Health permission policy and exact-head CI passes.
6. Keep competitions reward-ineligible until physical provenance and admin/backend gates pass.
7. Implement route backup only after the separate consent, retention and deletion contract is reviewed and tested.
8. Allocate 51020 only after owner signing/API prerequisites, exact-head Android CI and physical P0 pass.

---

## Previous detailed checkpoint (earlier 2026-11-15; retained for continuity)

The earlier detailed audit follows. Its time-sensitive branch heads, PR comparisons, Play readback and phone last-seen values are superseded by the authoritative update above.

Scope: **TopHeroFit only**. Sole source of truth: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.

## Canonical source

- Starting canonical HEAD for this run: `73cdb2f5082f7631d4d6ce6459a6f6a89ba4db15`.
- Latest application merge: PR #296, squash merge `1e38da33ba16e9fa6a3276606a1130ff8f95a454`.
- Canonical branch now points to `1e38da33ba16e9fa6a3276606a1130ff8f95a454`.
- PR #296 was 3 ahead / 0 behind its exact canonical base; after merge, the canonical compare is 1 commit ahead / 0 behind.
- The three changed application/test files were independently re-fetched from canonical and their blobs match the tested PR tree:
  - `HealthConnectRepository.kt`: `d9e97dd12eb900c5101ba5569a90a73d2605a931`
  - `HealthRecordProvenancePresentationPolicy.kt`: `2803a7def252ebe645d33c800f8c9ef956a15a59`
  - `HealthRecordProvenancePresentationPolicyTest.kt`: `4dd3a9c095da7258c15136346d90dc26e894b2c8`
- Canonical Android manifest was re-fetched unchanged: `0969cdb2f18775f23e0870bf754612a04376895f`.

## PR #296 — Health Connect swimming presentation fail-closed

[PR #296](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/296) merged successfully.

- Tested PR head: `c2e3058c936b59e71f3c7e67cb854be516a6b4d9`.
- Merge commit: `1e38da33ba16e9fa6a3276606a1130ff8f95a454`.
- Exact-head Android candidate workflow [43721667918](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43721667918): SUCCESS.
- Product tests: 67/67.
- Source-contract tests: 34/34.
- Backend tests: 29/29.
- Android `:app:testDebugUnitTest`: 254 tests, 0 failures, 0 skipped.
- Android API 36, lint, `:app:assembleDebug` and `:app:bundleRelease`: PASS.
- Lint: 0 errors, 16 warnings, 1 hint.
- Gradle: BUILD SUCCESSFUL in 3m 1s.

Artifact 14164513840:
- ZIP SHA-256: `762540d8b291c1e7b7419130b2decd8c8c6b7c3b3a41183bbeb37f66c09c7659` (independently recomputed and matched).
- QA APK SHA-256: `e20af5bdcfe34c088bcb5ddba8ba1852b26d36b6281c3614654cd1b2a9b7456a`.
- Unsigned validation AAB SHA-256: `34998ff0a56b601aca328392e31d697d79ca02f7be3922e2ba00d27d6efe89ec`.
- `jarsigner` confirms the AAB is unsigned.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is not a release artifact.

Material behavior:
- Internal Health evidence now retains the actual exercise-session type and start/end instants from the Health Connect record.
- These fields are not added to the privacy-reduced UI summary.
- The presentation policy independently requires complete exercise-session metadata and valid positive session time.
- Swimming presentation reuses the canonical swimming eligibility policy: reviewed provider, compatible watch/fitness-band metadata, active/automatic recording, stable record ID and valid time range.
- Phone, ring and chest-strap swimming records fail closed even if upstream flags inconsistently claim VERIFIED.
- Missing exercise type/time and exercise metadata attached to a metric record fail closed.
- The reviewed-provider phone path for non-swimming running remains intact.
- This is a Health Connect metadata gate, not cryptographic hardware attestation. Physical wearable validation remains mandatory.

## Latest recovery and GPS handoff

Starting recovery document: [RECOVERY_CURRENT_20261114.md](RECOVERY_CURRENT_20261114.md), blob `57003b8fdd576f7ca6a11d95503e8a622fdd703c`.

Latest GPS report: [GPS_MAP_QUALITY_20261114.md](GPS_MAP_QUALITY_20261114.md), blob `b7436e3871ceae09188a66fe6b482c10ce5c674f`.

- Selected native GPS PR #294 remains open/Draft/unmerged.
- Current PR head: `a238aef70f5114fb845d7a55cdb59a1fc1bfd61e`; base remains `82ac0797f26ef142bee868ea6f8378066a961b1e`.
- Compare against current canonical: 4 ahead / 6 behind; current diff contains eight GPS source/test files.
- PR body still describes the earlier exact-tested source `7933a0eb0b6bedf8d00af49fee41ed24d88c264f` and six files; its metadata/body is stale relative to current head. The prior exact combined-head run [43625025348](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43625025348) passed that tested source, but does not establish current-head CI.
- Keep GPS ownership with #294. Do not edit or merge GPS native files in this lane.
- The canonical anomaly policy exists, but the selected GPS service still does not call `ActivityEvidenceAnomalyPolicy.assessSegment`. Live source-continuity, long-gap and uncertainty-adjusted segment checks remain outstanding.

## Current PR and file ownership audit

| PR | Current comparison / changed surface | Decision |
|---|---|---|
| #93 Health Services | 2 ahead / 349 behind; manifest, MainActivity, source-contract, reader/models/activity and rationale strings | Diverged; 19-scope manifest conflicts with canonical five-scope allowlist. Keep Draft. |
| #282 Health metric truthfulness | 2 ahead / 88 behind; shared `app.js` plus focused product test | Keep separate from #216 shared active-workout UI. |
| #160 bilingual catalog | 53 ahead / 204 behind; exercises JS/JSON, catalog manifest, builder and tests | Do not merge stacked branch; semantic and parity reconciliation required. |
| #213 timed program prescriptions | 190 ahead / 204 behind; `app.js`, programs JS/JSON, manifest, builder and tests | Do not merge stacked branch; reconcile with #204/#212/#214/#233/#234 and active workout UI. |
| #224 offline active demos | 153 ahead / 204 behind; active-workout demo module, `app.js`, `index.html`, test | Keep separate until shared UI ownership is reconciled. |
| #294 GPS | 4 ahead / 6 behind; eight GPS source/test files | GPS owner only; current PR body/head mismatch and physical P0 remain. |
| #296 swimming presentation gate | Merged at `1e38da33ba16e9fa6a3276606a1130ff8f95a454` | Canonical and exact-head tested. |

A current ownership/blocker note was added to [PR #93](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93): [comment 6895448461](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93#issuecomment-6895448461). It records the latest 2-ahead / 349-behind comparison, 19-vs-5 permission discrepancy and the disjoint #296 ownership boundary.

## Health permissions and evidence

Canonical manifest remains exactly five Health Connect scopes:
- `READ_STEPS`
- `READ_EXERCISE`
- `WRITE_EXERCISE`
- `READ_DISTANCE`
- `READ_ACTIVE_CALORIES_BURNED`

`READ_HEART_RATE` remains absent. No optional heart-rate permission or reader was added.

PR #93 still adds 14 extra declarations, including sleep, total calories, heart rate/resting heart rate, body measurements, oxygen saturation, VO2 max, speed, nutrition, blood pressure and glucose. These remain unauthorized until least-privilege feature, rationale, Play declaration and privacy gates are satisfied.

The live Health UI bridge still does not serialize `HealthSnapshot.recordProvenance`; PR #93 owns MainActivity and source-contract integration. Only privacy-reduced summaries may be bridged. Raw provider/client record IDs and device manufacturer/model must not be exposed.

## Exercise catalog, programs and offline motion audit

Current canonical data blobs:
- `exercises.json`: `425f0dab3fa1b0718cf84dd818a26d3585881718`
- `programs.json`: `013022b7cb647e17b66cd2c9f3aad20c39050062`
- `motion-manifest.json`: `16fb02e9f87e7930fa6b779f8f6440f11d8ae1ab`
- `video-licenses.json`: `e0b7c9e4bfc4afab643dc9c5b9d198c0d1f48887`

Fresh data audit:
- 112 exercises; 84 English/Arabic step-count mismatches.
- At least 23 Arabic step rows match known generic fallback phrases; semantic quality review remains necessary.
- 26 programs, 94 sessions, 470 exercise references, zero unknown exercise IDs.
- 232 timed references; all 232 currently carry RIR, including 226 whose catalog tracking disables RIR.
- Six timed Superman references still conflict with the catalog's repetition-based prescription.
- PR #160's parity candidate and PR #213's program candidate remain highly divergent and have shared-file ownership collisions; do not merge wholesale.

Offline motion manifest has seven entries: five licensed offline video assets and two reviewed 16-frame sequences. The other 105 catalog exercises remain reference-only two-frame demonstrations; do not describe them as full-motion videos. Merged PR #289's mapping/license/hash tests remain canonical.

The passing product suite on #296 also rechecked bilingual voice guidance, Health permission scope, forced-colors accessibility, keyboard focus, reduced motion, program progression and offline asset mappings.

## Physical, Play and release gates

- Desktop Commander `localhost` was checked on 2026-11-15 and remains OFFLINE (last seen 123 hours ago). Last known phone in the prior checkpoint: Samsung SM-A217F / Android 12. Current device/session state is unknown.
- No ADB, install, launch, Stop, settings or activity-data action was attempted.
- Physical Health Connect grant/partial-grant/revoke/no-data/error checks, actual compatible wearable validation, physical swimming, GPS stationary drift, measured routes, background/screen-off and process-death checks remain BLOCKED_NOT_RUN.
- The latest verified Play readback remains 2026-11-14 18:03:26 UTC: Internal 51019 completed; Alpha 51007 draft; Production not verified. No new Play readback was obtained in this run.
- VersionCode 51020 remains unallocated. No signing, release workflow, listing, upload or Production promotion occurred.
- Play Health declaration/privacy reconciliation remains a hard release gate. No new Health scopes were added.
- No paid service, Maps billing/key, unrelated project or external route upload was used.

## Next safe execution order

1. Keep PR #93 blocked until it rebases, restores the five-scope allowlist and integrates the privacy-reduced per-record provenance bridge with exact-head CI.
2. Connect phone-measured evidence to walking/running/cycling reconciliation without editing GPS acquisition.
3. Keep the live GPS anomaly-policy wiring with the #294 owner; require current-head CI and physical P0.
4. Consolidate bilingual catalog semantic fixes and timed-program RIR/dose corrections onto canonical without merging divergent stacks.
5. Expand genuinely licensed full-motion offline demonstrations with exact exercise mappings.
6. Keep heart rate optional and absent until a real supported data path and least-privilege declaration exist.
7. Preserve physical Health/wearable/GPS and Play privacy gates before any release decision.

No release version, signing configuration, workflow, Play state, GPS native file or tracking session was changed in this run.



---

## Previous detailed checkpoint (retained; time-sensitive values superseded above)

Scope: **TopHeroFit only**. Sole source of truth: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.

## Canonical source

- Starting canonical HEAD for this run: `73cdb2f5082f7631d4d6ce6459a6f6a89ba4db15`.
- Latest application merge: PR #296, squash merge `1e38da33ba16e9fa6a3276606a1130ff8f95a454`.
- Canonical branch now points to `1e38da33ba16e9fa6a3276606a1130ff8f95a454`.
- PR #296 was 3 ahead / 0 behind its exact canonical base; after merge, the canonical compare is 1 commit ahead / 0 behind.
- The three changed application/test files were independently re-fetched from canonical and their blobs match the tested PR tree:
  - `HealthConnectRepository.kt`: `d9e97dd12eb900c5101ba5569a90a73d2605a931`
  - `HealthRecordProvenancePresentationPolicy.kt`: `2803a7def252ebe645d33c800f8c9ef956a15a59`
  - `HealthRecordProvenancePresentationPolicyTest.kt`: `4dd3a9c095da7258c15136346d90dc26e894b2c8`
- Canonical Android manifest was re-fetched unchanged: `0969cdb2f18775f23e0870bf754612a04376895f`.

## PR #296 — Health Connect swimming presentation fail-closed

[PR #296](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/296) merged successfully.

- Tested PR head: `c2e3058c936b59e71f3c7e67cb854be516a6b4d9`.
- Merge commit: `1e38da33ba16e9fa6a3276606a1130ff8f95a454`.
- Exact-head Android candidate workflow [43721667918](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43721667918): SUCCESS.
- Product tests: 67/67.
- Source-contract tests: 34/34.
- Backend tests: 29/29.
- Android `:app:testDebugUnitTest`: 254 tests, 0 failures, 0 skipped.
- Android API 36, lint, `:app:assembleDebug` and `:app:bundleRelease`: PASS.
- Lint: 0 errors, 16 warnings, 1 hint.
- Gradle: BUILD SUCCESSFUL in 3m 1s.

Artifact 14164513840:
- ZIP SHA-256: `762540d8b291c1e7b7419130b2decd8c8c6b7c3b3a41183bbeb37f66c09c7659` (independently recomputed and matched).
- QA APK SHA-256: `e20af5bdcfe34c088bcb5ddba8ba1852b26d36b6281c3614654cd1b2a9b7456a`.
- Unsigned validation AAB SHA-256: `34998ff0a56b601aca328392e31d697d79ca02f7be3922e2ba00d27d6efe89ec`.
- `jarsigner` confirms the AAB is unsigned.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is not a release artifact.

Material behavior:
- Internal Health evidence now retains the actual exercise-session type and start/end instants from the Health Connect record.
- These fields are not added to the privacy-reduced UI summary.
- The presentation policy independently requires complete exercise-session metadata and valid positive session time.
- Swimming presentation reuses the canonical swimming eligibility policy: reviewed provider, compatible watch/fitness-band metadata, active/automatic recording, stable record ID and valid time range.
- Phone, ring and chest-strap swimming records fail closed even if upstream flags inconsistently claim VERIFIED.
- Missing exercise type/time and exercise metadata attached to a metric record fail closed.
- The reviewed-provider phone path for non-swimming running remains intact.
- This is a Health Connect metadata gate, not cryptographic hardware attestation. Physical wearable validation remains mandatory.

## Latest recovery and GPS handoff

Starting recovery document: [RECOVERY_CURRENT_20261114.md](RECOVERY_CURRENT_20261114.md), blob `57003b8fdd576f7ca6a11d95503e8a622fdd703c`.

Latest GPS report: [GPS_MAP_QUALITY_20261114.md](GPS_MAP_QUALITY_20261114.md), blob `b7436e3871ceae09188a66fe6b482c10ce5c674f`.

- Selected native GPS PR #294 remains open/Draft/unmerged.
- Current PR head: `a238aef70f5114fb845d7a55cdb59a1fc1bfd61e`; base remains `82ac0797f26ef142bee868ea6f8378066a961b1e`.
- Compare against current canonical: 4 ahead / 6 behind; current diff contains eight GPS source/test files.
- PR body still describes the earlier exact-tested source `7933a0eb0b6bedf8d00af49fee41ed24d88c264f` and six files; its metadata/body is stale relative to current head. The prior exact combined-head run [43625025348](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43625025348) passed that tested source, but does not establish current-head CI.
- Keep GPS ownership with #294. Do not edit or merge GPS native files in this lane.
- The canonical anomaly policy exists, but the selected GPS service still does not call `ActivityEvidenceAnomalyPolicy.assessSegment`. Live source-continuity, long-gap and uncertainty-adjusted segment checks remain outstanding.

## Current PR and file ownership audit

| PR | Current comparison / changed surface | Decision |
|---|---|---|
| #93 Health Services | 2 ahead / 349 behind; manifest, MainActivity, source-contract, reader/models/activity and rationale strings | Diverged; 19-scope manifest conflicts with canonical five-scope allowlist. Keep Draft. |
| #282 Health metric truthfulness | 2 ahead / 88 behind; shared `app.js` plus focused product test | Keep separate from #216 shared active-workout UI. |
| #160 bilingual catalog | 53 ahead / 204 behind; exercises JS/JSON, catalog manifest, builder and tests | Do not merge stacked branch; semantic and parity reconciliation required. |
| #213 timed program prescriptions | 190 ahead / 204 behind; `app.js`, programs JS/JSON, manifest, builder and tests | Do not merge stacked branch; reconcile with #204/#212/#214/#233/#234 and active workout UI. |
| #224 offline active demos | 153 ahead / 204 behind; active-workout demo module, `app.js`, `index.html`, test | Keep separate until shared UI ownership is reconciled. |
| #294 GPS | 4 ahead / 6 behind; eight GPS source/test files | GPS owner only; current PR body/head mismatch and physical P0 remain. |
| #296 swimming presentation gate | Merged at `1e38da33ba16e9fa6a3276606a1130ff8f95a454` | Canonical and exact-head tested. |

A current ownership/blocker note was added to [PR #93](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93): [comment 6895448461](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93#issuecomment-6895448461). It records the latest 2-ahead / 349-behind comparison, 19-vs-5 permission discrepancy and the disjoint #296 ownership boundary.

## Health permissions and evidence

Canonical manifest remains exactly five Health Connect scopes:
- `READ_STEPS`
- `READ_EXERCISE`
- `WRITE_EXERCISE`
- `READ_DISTANCE`
- `READ_ACTIVE_CALORIES_BURNED`

`READ_HEART_RATE` remains absent. No optional heart-rate permission or reader was added.

PR #93 still adds 14 extra declarations, including sleep, total calories, heart rate/resting heart rate, body measurements, oxygen saturation, VO2 max, speed, nutrition, blood pressure and glucose. These remain unauthorized until least-privilege feature, rationale, Play declaration and privacy gates are satisfied.

The live Health UI bridge still does not serialize `HealthSnapshot.recordProvenance`; PR #93 owns MainActivity and source-contract integration. Only privacy-reduced summaries may be bridged. Raw provider/client record IDs and device manufacturer/model must not be exposed.

## Exercise catalog, programs and offline motion audit

Current canonical data blobs:
- `exercises.json`: `425f0dab3fa1b0718cf84dd818a26d3585881718`
- `programs.json`: `013022b7cb647e17b66cd2c9f3aad20c39050062`
- `motion-manifest.json`: `16fb02e9f87e7930fa6b779f8f6440f11d8ae1ab`
- `video-licenses.json`: `e0b7c9e4bfc4afab643dc9c5b9d198c0d1f48887`

Fresh data audit:
- 112 exercises; 84 English/Arabic step-count mismatches.
- At least 23 Arabic step rows match known generic fallback phrases; semantic quality review remains necessary.
- 26 programs, 94 sessions, 470 exercise references, zero unknown exercise IDs.
- 232 timed references; all 232 currently carry RIR, including 226 whose catalog tracking disables RIR.
- Six timed Superman references still conflict with the catalog's repetition-based prescription.
- PR #160's parity candidate and PR #213's program candidate remain highly divergent and have shared-file ownership collisions; do not merge wholesale.

Offline motion manifest has seven entries: five licensed offline video assets and two reviewed 16-frame sequences. The other 105 catalog exercises remain reference-only two-frame demonstrations; do not describe them as full-motion videos. Merged PR #289's mapping/license/hash tests remain canonical.

The passing product suite on #296 also rechecked bilingual voice guidance, Health permission scope, forced-colors accessibility, keyboard focus, reduced motion, program progression and offline asset mappings.

## Physical, Play and release gates

- Desktop Commander `localhost` was checked on 2026-11-15 and remains OFFLINE (last seen 123 hours ago). Last known phone in the prior checkpoint: Samsung SM-A217F / Android 12. Current device/session state is unknown.
- No ADB, install, launch, Stop, settings or activity-data action was attempted.
- Physical Health Connect grant/partial-grant/revoke/no-data/error checks, actual compatible wearable validation, physical swimming, GPS stationary drift, measured routes, background/screen-off and process-death checks remain BLOCKED_NOT_RUN.
- The latest verified Play readback remains 2026-11-14 18:03:26 UTC: Internal 51019 completed; Alpha 51007 draft; Production not verified. No new Play readback was obtained in this run.
- VersionCode 51020 remains unallocated. No signing, release workflow, listing, upload or Production promotion occurred.
- Play Health declaration/privacy reconciliation remains a hard release gate. No new Health scopes were added.
- No paid service, Maps billing/key, unrelated project or external route upload was used.

## Next safe execution order

1. Keep PR #93 blocked until it rebases, restores the five-scope allowlist and integrates the privacy-reduced per-record provenance bridge with exact-head CI.
2. Connect phone-measured evidence to walking/running/cycling reconciliation without editing GPS acquisition.
3. Keep the live GPS anomaly-policy wiring with the #294 owner; require current-head CI and physical P0.
4. Consolidate bilingual catalog semantic fixes and timed-program RIR/dose corrections onto canonical without merging divergent stacks.
5. Expand genuinely licensed full-motion offline demonstrations with exact exercise mappings.
6. Keep heart rate optional and absent until a real supported data path and least-privilege declaration exist.
7. Preserve physical Health/wearable/GPS and Play privacy gates before any release decision.

No release version, signing configuration, workflow, Play state, GPS native file or tracking session was changed in this run.


## 2026-11-16 19:56 Cairo integrator update — supersedes earlier GPS/Play values

### Canonical and GPS rebase
- Canonical branch before this documentation checkpoint: `fbb63025ef0d6dbfe22c7661b049a4b72da2b5a0`; latest application merge remains PR #299 at `16fd1b16ef9d3592ef031298e059ed730ff92f92`.
- PR #297 is now the selected native GPS handoff. Its branch was rebased with force-with-lease from `d572bae1baea0ea01fdca91d39cc089a30378e90` onto canonical `fbb63025ef0d6dbfe22c7661b049a4b72da2b5a0`.
- New exact PR HEAD: `1c099845979a998dc0d374322f471c39400e566e`; compare 8 ahead / 0 behind, exactly eight GPS source/test files. The two old checkpoint documents were excluded from the source-only rebase; the canonical GPS report is now recorded separately.
- Exact-head run [43923207674](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43923207674) completed SUCCESS on `1c099845979a998dc0d374322f471c39400e566e`: Product 67/67, source-contract 34/34, backend 29/29, Android 273/273, zero failures/ignored; API 36, Kotlin, lintDebug, assembleDebug and unsigned bundleRelease validation PASS.
- Artifact 14253604668 independently downloaded and rehashed: ZIP `58c87c1a0ebf5d5a606375fee5a56aad2cf39ef2accd02f068ae8b8b199cc1aa`; QA APK `65cdf02aade50cb3916932e9af8187dd13ea5e21e38fe997ee795dcc3b283d98`; unsigned AAB `6e9d73ecf9a50838e17a7c3551f41931d21684d3e1c2af7dc443f5412250dfdc`. `jarsigner` reports unsigned; QA identity/versionCode 51019 only. Never promote.
- PR #297 remains Draft and mergeable; physical P0 remains BLOCKED_NOT_RUN. `ActivityEvidenceAnomalyPolicy.assessSegment` remains unwired; do not claim complete anti-cheat or location attestation.

### Fresh Play readback — 2026-11-16
- Re-ran only the existing read-only publication-state job (run [43739661313](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43739661313), attempt 2). The workflow file blob at the old run head is identical to current canonical, SHA `33cf9e555e68e00b7990545720bd7e0403a96716`.
- Job succeeded at 17:56:42Z. Artifact 14255396385 ZIP SHA-256 `c3634fa8a1c4c462deecf4ad6582db0c395481a7b8758051b709374d55e7a025`; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`, independently rehashed.
- Play readback: Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified. `uploadAttempted=false`, `commitAttempted=false`. Arabic and English listings are unchanged; estimated-metric and no-medical-diagnosis disclaimers are present. GPS/background/offline/voice claims remain gated by physical QA. No Play mutation occurred.

### Phone and physical P0
- Fresh Desktop Commander listing: `localhost` OFFLINE, last seen about 151 hours. Last known handset Samsung SM-A217F / Android 12; current device and session state unknown.
- No ADB, install, launch, Stop, settings change or activity-data read was attempted. Preserve the Play installation and any possible live session.
- Physical stationary drift, measured walk/run/cycle, precise-to-approximate transition, first-fix latency, screen-off/background, notification controls and process-death recovery remain BLOCKED_NOT_RUN.

### Current PRs and file ownership
- #297: Draft, 8 ahead / 0 behind, exact-head CI PASS.
- #284: Draft, 19 ahead / 52 behind, no current-head CI; overlaps #297 native GPS, #93 MainActivity/source-contract and #282/#216 app.js. Do not merge wholesale.
- #282: Draft, 2 ahead / 94 behind; null-vs-zero formatter and product test only, but stale app.js base overlaps #216/#224/#284.
- #93: Draft, 2 ahead / 355 behind; requests 19 Health scopes against the canonical five-scope allowlist. Blocked.
- #216, #160 and #213 were converted to Draft because they are highly divergent/stacked and lack exact current-head CI. #224 and #248 remain Draft. Detailed file ownership is recorded in `INTEGRATOR_LEASES_CURRENT_20261116.md`.
- #294 is closed unmerged and superseded by #297. #295 and #299 are merged.
- No formal lease registry existed at the previous checkpoint; a canonical file-level ownership registry has now been added.

### Release and sync boundary
- Latest Play Internal remains 51019. Next Android versionCode 51020 is unallocated. No release signing, upload, track mutation or Production promotion.
- Existing route history remains local in WebView localStorage. Authenticated route backup/sync remains design-only; no precise-location cloud upload.
- Health scopes remain exactly five. `READ_HEART_RATE` remains absent. Competition admin creation remains disabled without the owner-managed key; scores are not physically verified and rewards remain ineligible.
- No paid infrastructure, Maps billing/key, unrelated project or device mutation was used.