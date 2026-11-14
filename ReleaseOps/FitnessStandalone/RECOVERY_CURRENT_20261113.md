# TopHeroFit recovery checkpoint — 2026-11-13

Scope: **TopHeroFit only**. Source of truth: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.

## Canonical starting point and latest source

- Canonical branch: `agent/codex/fitness-recovery/20261023`.
- Canonical application merge commit: `778f159402902549983142c83151a09745f624cc` (PR #293).
- Latest documentation/checkpoint commit: `82c29ba9d49b2e3e46d35c74f60a37359b1e3db9` before this ownership-safe checkpoint.
- Prior recovery: [RECOVERY_CURRENT_20261112.md](RECOVERY_CURRENT_20261112.md).
- Latest GPS candidate report: [GPS_MAP_QUALITY_20261113.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/gps-fallback-resilience-20261113-r2/ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261113.md). This is GPS-owner evidence on PR #292, not a canonical physical-device pass.

## Health provenance — merged

- PR [#293](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/293) merged at `778f159402902549983142c83151a09745f624cc`.
- Tested exact head: `d69e969404f728f8666eedbf4d3c9ad08104b60e`.
- Exact-head Android CI [43438628557](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43438628557): SUCCESS.
- Product 67/67, source-contract 34/34, backend 29/29; Android unit tests, lint, assembleDebug and bundleRelease passed.
- QA APK SHA-256: `e6287984b4b869ac689fd49958cd7b9f7f63dbe094c20fccc3e25b940102dc47`.
- Unsigned validation AAB SHA-256: `de4e22f442b8d9ebe8cf0a3deb2ecc94f2ff62ba943485ca8fa121639de0cab2`.
- Artifact ZIP SHA-256: `4aed8a0bbf9c57b3f4e2a5069c13b75776c4bba158a8975696ad6986e3b3d44d`, artifact ID `14044676485`.

Canonical provenance files:
- `HealthConnectRepository.kt`: `dd65d53a70a8287014666d3759b0f4bab98aa152`.
- `HealthRecordProvenancePresentationPolicy.kt`: `ceba7bd93637c4acd83d7f0dd6d68cf666aa9e6d`.
- `HealthRecordProvenancePresentationPolicyTest.kt`: `f595c43f5073c7da39de8011a1f6ed499836b91c`.

The public `HealthSnapshot.recordProvenance` projection contains source package, stable record type, recording method, device class, integrity class, reward decision and constrained reason. Raw provider/client IDs and manufacturer/model are omitted. Its deterministic pseudonymous key is for UI/list reconciliation only, not anonymization, hardware attestation or authorization. Unknown types remain reward-ineligible; presentation cannot upgrade repository evidence.

## Health permission and integration gates

Canonical manifest blob: `0969cdb2f18775f23e0870bf754612a04376895f`. Exactly five Health permissions remain:
- `READ_STEPS`
- `READ_EXERCISE`
- `WRITE_EXERCISE`
- `READ_DISTANCE`
- `READ_ACTIVE_CALORIES_BURNED`

`READ_HEART_RATE` remains absent.

PR [#93](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93) still owns Health service/manifest/rationale and MainActivity/WebView bridge files. Its manifest blob `a3b24f09e6b0c8a67b0fee3e7578317cfe979092` declares 19 scopes, including 14 deferred scopes. It remains Draft, diverged and unmergeable; merged PR #188's exact-five allowlist rejects it. No extra scope is authorized. PR #93 must rebase, keep five scopes and consume #293's summary without raw IDs.

The phone↔Health walking/running/cycling reconciliation policy remains unconnected to `HealthConnectRepository.readRecent()`. Same-source records deduplicate; nearby independent same-source sessions remain separate; swimming never time-deduplicates without stable identity.

## GPS and anti-cheat — separate owner

- PR [#292](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/292), branch `agent/codex/gps-fallback-resilience-20261113-r2`.
- Current branch HEAD: `de304b6f4baa44dc80b3245493d7275fe39f00fe`.
- Tested application/test SHA: `cb97dc0b66299825e6a02dd91ec53e369667bb74`.
- Exact-source Android CI [43382459916](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43382459916): SUCCESS; Product 67/67, source-contract 34/34, backend 29/29, Android 250/250; lint, assembleDebug and bundleRelease passed.
- Candidate provides bounded provider fallback/backoff, coarse-only NETWORK selection, generation-scoped callbacks and truthful accuracy. It is not merged. Its source and tests remain GPS-owner files; this lane did not edit them.
- Physical stationary-drift, measured-route, screen-off/background, notification, process-death and live-session P0 remain BLOCKED_NOT_RUN. Authorized device is offline; current session state unknown. Do not install, launch, stop or alter the phone until safely idle.
- Canonical anomaly policy/tests exist, but live accepted GPS fixes are not yet passed through the policy. GPS owner must supply actual raw Android Location provider, elapsedRealtimeNanos, coordinates, horizontal accuracy and OS mock flag before distance/pace/competition credit. No display-smoothed evidence.

## Exercise content, programs and offline motion

- Canonical catalog: 112 exercises; 84 Arabic/English step-count mismatches.
- PR #160 reduces count mismatches to zero but is 53 ahead / 180 behind and has two semantic mapping defects: Step-up with Knee Raise uses squat cues; Medicine Ball Scoop Throw uses hinge/deadlift cues. No exact-head CI.
- Canonical programs: 26 programs / 94 sessions / 470 references.
- PR #213 is 190 ahead / 180 behind, spans 49 files and has no exact-head CI. It removes timed RIR but leaves six 30-second Superman program holds mismatched to a repetition-based catalog entry.
- Offline media inventory: five videos, two reviewed 16-frame sequences, 105 two-frame reference-only exercises. Merged #289 protects mappings, local asset hashes and license attribution; no new clips were added.

## Release and physical gates

Play Health declaration/privacy/Data Safety reconciliation, physical Health grant/revoke/no-data/error checks, actual wearable/swimming verification and GPS physical P0 remain hard gates. No Play upload, release version allocation, signing, workflow change, billing or paid service occurred.

## Next safe order

1. Rebase PR #93 onto canonical, restore the five-scope permission allowlist, and integrate the merged per-record provenance contract through its owned bridge.
2. Connect phone-session evidence to walking/running/cycling reconciliation without editing GPS acquisition.
3. Port bilingual catalog and timed-program corrections onto canonical with semantic tests and exact-head CI.
4. Expand genuinely licensed full-motion clips with exact exercise-ID mapping.
5. Preserve physical Health/wearable/GPS and Play privacy gates until actual evidence exists.


## Integrator recheck — 2026-11-13 19:47 Africa/Cairo

### Canonical and GPS handoff
- Canonical branch HEAD at recheck: `dbe85572669fe50fd16cb3e126ab763efd0d08f0`. This includes merged Health provenance PR #293 and the ownership-safe recovery checkpoint.
- PR [#293](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/293) is merged at `778f159402902549983142c83151a09745f624cc`; exact-head CI [43438628557](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43438628557) passed on `d69e969404f728f8666eedbf4d3c9ad08104b60e`. Its three Health provenance files are disjoint from the five GPS source/test files in #292.
- PR [#292](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/292) remains Draft. Branch HEAD is `de304b6f4baa44dc80b3245493d7275fe39f00fe`; tested source/test SHA is the same exact branch HEAD.
- Exact PR-head Android CI is [43383307618](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43383307618), not the earlier synthetic merge-event run 43382459916. Run 43383307618 checked out `de304b6f4baa44dc80b3245493d7275fe39f00fe` and completed SUCCESS.
- Product 67/67; source-contract 34/34; backend 29/29; Android unit 250/250 (0 failures, 0 ignored); Android API 36, lintDebug, assembleDebug and bundleRelease validation passed. Lint: 0 errors, 16 warnings, 1 hint.
- Exact-head artifact ID `14017568163`; downloaded ZIP SHA-256 `d1aee733160901a21e0752b8615c3e2c6a858a64c529e28e9147162553458c32`; APK SHA-256 `a0914f8767fdebc6799cc8bc2858dabf46355f87e1828742d1e482160ef63289`; unsigned validation AAB SHA-256 `fb1e66c0e2570ddd14d00367890da2ed95f6374b08239e5f1d537366c54b7b80`. The ZIP and internal file hashes were recomputed from the downloaded artifact; `jarsigner -verify` reports the AAB is unsigned. QA identity remains `com.topherofit.thf.pulse.qa`, versionCode 51019; no release allocation or signing.
- At the initial 19:47 recheck, pre-ledger canonical HEAD was `dbe85572669fe50fd16cb3e126ab763efd0d08f0`; after the evidence-ledger commits, current canonical HEAD is `6286c7cebcf79872f0606e34ca5ba5c4e4efac28`. Relative to that current HEAD, #292 is 13 commits ahead / 6 behind with merge base `dedd5f39001781c19e7e19bdee8f44e2fa97b01d`. Its five app/test files remain disjoint from #293, but the branch has not been rebased or tested against the current canonical combined head. GitHub's earlier clean mergeability snapshot does not replace combined-head CI or physical QA.

### Current PR ownership / overlap snapshot
| PR | Current state | Files / hold |
|---|---|---|
| #292 | Draft; exact PR-head CI PASS | Isolated Activity Engine/GPS source and tests plus its GPS report. No app.js, MainActivity or test_source_contract changes. Physical P0 remains blocked. |
| #284 | Draft; mergeable=false / dirty | Older GPS UI/native handoff. Shares ActivityTrackingService with #292; app.js overlaps #282/#216; MainActivity and test_source_contract overlap #93. Do not merge wholesale. |
| #282 | Draft | app.js Health metric null-vs-zero UI; no combined-head CI. |
| #216 | Open, not Draft | app.js active-workout resume; stale base and no current exact-head CI. |
| #93 | Draft | Still declares 19 Health permissions including READ_HEART_RATE versus canonical five-scope allowlist; owns MainActivity and test_source_contract. No extra Health scopes authorized. |
| #248 | Draft | Separate ActivityGpsRouteSmoother helper/tests; stale base and no exact-head Android CI. Keep separate from raw GPS evidence. |
| #293 | Merged | Privacy-safe per-record Health provenance projection; exact-head CI passed. |

No formal lease record was found. Treat #93's MainActivity/test_source_contract claim and the observed PR file overlaps as ownership holds. #292 is the selected native GPS handoff; #284 remains a held reference for its map/UI changes. Do not merge #284 or #292 before physical P0 and a final combined-head CI after safe base reconciliation.

### Activity tracking / session persistence — source audit only
- `ActivityTrackingService` uses a foreground location/health service, returns START_STICKY for restorable sessions, writes checkpoints at most every 10 seconds, forces a checkpoint on task removal and destruction, and restores route/distance/session phase from SharedPreferences.
- The ongoing notification refreshes every 5 seconds and exposes Pause/Resume and Stop controls. Pause unregisters sensors/location; Resume resets stale GPS anchors and re-registers sources.
- These are source-level observations only. Background execution, screen-off continuity, notification actions and process-death recovery have not passed physical-device P0.

### Anti-cheat integration gap
- Canonical `ActivityEvidenceAnomalyPolicy.kt` and its tests exist, but the #292 `ActivityTrackingService.kt` contains no `ActivityEvidenceAnomalyPolicy`, `ActivityGpsFix` or `assessSegment` call. It captures provider, mock flag, elapsed-realtime timestamp, coordinates and accuracy, then applies `GpsFixGate` and `GpsDistanceAccumulator` directly.
- Do not treat this as full anti-cheat. Before distance/pace/competition credit, wire actual raw Android fixes through the anomaly policy and test mock/source-change/monotonic-time/accuracy/gap/implausible-speed cases. Never use display-smoothed route points as evidence.

### Phone and physical P0
- Desktop Commander `localhost` is OFFLINE; last seen 79 hours before the 2026-11-13 19:47 Cairo check. Current SM-A217F session state is unknown. No ADB, install, launch, Stop, pause/resume, settings or activity-data action was attempted. Last recorded device-wide `location_mode=0` remains from 2026-11-09 and was not changed.
- Stationary drift, measured route, coarse-only permission, first-fix latency, screen-off/background, notification actions and process-death P0 remain BLOCKED_NOT_RUN. Preserve the unknown live session.

### Google Play — latest verified readback, not a fresh live probe
- Latest successful read-only Play state readback remains [run 42405709027, attempt 4](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42405709027), started 2026-11-10 18:30:50Z. Downloaded artifact 13791872061 was independently rehashed: ZIP SHA-256 `bffbb6484802331c90f7b49ba029ab373f63cc2f13d94d10b980907008e775ee`; embedded JSON SHA-256 `09e7a346e5e1c893d4323d20105d8f4d63`.
- The JSON reports Internal 51019 completed, Alpha 51007 draft, and Production not listed/verified. `uploadAttempted=false`, `commitAttempted=false`. The Arabic and English listings still claim GPS/background sessions, offline-ready exercise content and voice guidance; reconcile those claims against physical and media evidence before Production.
- The later publication-state probe run [42672026813](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42672026813) failed before creating any job or artifact; it is not a Play API observation. No newer successful probe was found in the latest repository Actions run page. The probe workflow is `workflow_dispatch` only; this GitHub connection exposes no dispatch action and Desktop Commander is offline. Therefore no fresh Play API readback was performed on 2026-11-13.
- VersionCode 51020 remains unallocated. Owner release API/signing prerequisites, final combined-head Android CI, physical P0 and policy/privacy gates remain mandatory. No signing, upload, track commit, listing edit or Production promotion occurred.

### Route backup / sync remains separate
- Completed routes are still persisted in WebView localStorage; no authenticated route-sync endpoint or precise-location upload exists. The opt-in route backup design remains design-only with separate summary/precise-location consent, retention and deletion requirements. Do not implement or upload routes until the GPS and privacy/backend contracts are tested.


## Final canonical-head reconciliation

- Canonical application/source comparison baseline: `6286c7cebcf79872f0606e34ca5ba5c4e4efac28`. The two subsequent evidence-only ledger commits advanced the branch to pre-checkpoint HEAD `22e5ad588811d84e36129779447c0432978210a4`; they changed only recovery/release documentation, not application source.
- At pre-checkpoint HEAD `22e5ad588811d84e36129779447c0432978210a4`, PR #292 head `de304b6f4baa44dc80b3245493d7275fe39f00fe` is 13 ahead / 8 behind; merge base `dedd5f39001781c19e7e19bdee8f44e2fa97b01d`. Keep Draft; no rebase/merge was performed.
- At the same pre-checkpoint HEAD, PR #284 head `274155eafdfff381009ef5814a621f32b225f1a8` is 19 ahead / 30 behind; merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`. GitHub reports #284 `mergeable=false`, `dirty`; keep Draft.
- The preceding CI/artifact evidence is unchanged: PR #292 exact branch-head run 43383307618 on `de304b6`, artifact 14017568163, ZIP `d1aee733160901a21e0752b8615c3e2c6a858a64c529e28e9147162553458c32`, unsigned AAB `fb1e66c0e2570ddd14d00367890da2ed95f6374b08239e5f1d537366c54b7b80`.
- This final update is documentation-only. Its resulting commit is the new canonical branch HEAD; application/test source is unchanged.


## GPS report correction and final PR-head snapshot

- PR #292's branch HEAD is now `b0db64ad668cd2921cc8dcc34970912b42351b1f`. This commit changes only `GPS_MAP_QUALITY_20261113.md`; no Android source or tests changed after exact PR-head source/test SHA `de304b6f4baa44dc80b3245493d7275fe39f00fe` passed run 43383307618. The exact-head artifact hashes remain unchanged; no rebuild or reupload was made.
- Relative to pre-this-checkpoint canonical HEAD `935b18a835b4f5555b6be529fbe5c2c528abc792`, #292 is 14 ahead / 9 behind from merge base `dedd5f39001781c19e7e19bdee8f44e2fa97b01d`. The branch is still not reconciled/tested against the current canonical combined head.
- #284 remains Draft/dirty. Relative to the same pre-checkpoint canonical HEAD, it is 19 ahead / 31 behind from merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`; GitHub reports `mergeable=false` / `dirty`.
- This snapshot is documentation-only. No PR was merged, no phone action was taken, and no Play state changed.


## 2026-11-14 Health provenance / ownership checkpoint

### Canonical state after tested Health merge
- Canonical branch before this checkpoint: `96d35d2edf292c16c5c462f4f6a2016576eb6a53`, squash merge of PR #295.
- PR [#295](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/295) added a second fail-closed reviewed-provider check at the privacy-safe Health provenance presentation boundary.
- Exact tested PR source SHA: `06ce46526bd01b7a887b736add55451421ce9536`.
- Exact-head Android CI [run 43602214529](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43602214529): SUCCESS. Product 67/67, source-contract 34/34, backend 29/29; Android `:app:testDebugUnitTest`, lintDebug, assembleDebug and bundleRelease all PASS; Gradle BUILD SUCCESSFUL.
- Validation artifact 14117290237; ZIP SHA-256 `5b923c85c700f4e189e81bd6d815a563a9fd251b5aadf6689a741065d8211e85`. QA-only package `com.topherofit.thf.pulse.qa`, validation VersionCode 51019; unsigned AAB only, no release signing/upload.
- Canonical blobs after merge: `HealthRecordProvenancePresentationPolicy.kt` = `cc2c32803d2f4ad5ad696903e86048273a0d032a`; test = `b990558fe736c50da502341b6c412e0721949d83`.
- The presentation layer now also calls `HealthSourceTrustPolicy.isApprovedHealthConnectProvider(normalizedSource)`. A deliberately inconsistent `VERIFIED + verifiedForRewards=true` evidence object from an unreviewed provider remains source-labelled but reward-ineligible.
- Canonical manifest was re-fetched after merge: blob `0969cdb2f18775f23e0870bf754612a04376895f`; exactly five Health Connect scopes remain: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE, READ_ACTIVE_CALORIES_BURNED. READ_HEART_RATE remains absent.

### Health ownership and integration blockers
- PR [#93](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93) still owns AndroidManifest, Health service models/readers/activity/tests, MainActivity bridge, rationale strings and source-contract tests.
- Exact PR #93 manifest patch still adds 14 optional Health scopes beyond the five-scope canonical allowlist: total calories, sleep, heart rate, resting heart rate, weight, height, body fat, basal metabolic rate, oxygen saturation, VO2 max, speed, nutrition, blood pressure and blood glucose. Merged PR #188's permission-scope gate rejects that expansion. Keep all 14 out until each service has a user-facing purpose, minimum-necessary rationale, Play Health/privacy/Data Safety reconciliation and physical grant/revoke/no-data/error QA.
- Canonical MainActivity blob `b97e08756d5aba515c30f2d1a05517f56631ebf0` still serializes aggregate origins/counts only; it does not serialize `HealthSnapshot.recordProvenance` / `recordEvidence`. PR #93 owns this bridge. Send only privacy-reduced summaries; never expose raw record IDs, client IDs, manufacturer or model.
- PR [#117](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/117) is merged and its cross-source walking/running/cycling time-proximity policy is canonical. However, canonical `HealthConnectRepository.kt` blob `dd65d53a70a8287014666d3759b0f4bab98aa152` does not invoke it or receive phone-measured session evidence. Stable Health record identity dedup remains separate from phone-vs-Health session reconciliation. Same-origin nearby sessions must not be silently dropped; swimming is never time-deduplicated without stable identity.
- Optional heart-rate evidence remains policy-only and unintegrated. No READ_HEART_RATE permission, reader, physical watch sample or heart-rate evidence is available/claimed.

### GPS owner handoff — no GPS edits in this lane
- Latest candidate PR [#294](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/294), report [GPS_MAP_QUALITY_20261114.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/gps-location-state-honesty-20261114-r1/ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261114.md), report blob `80aa04e8c0ae3cdcd840dccc25d0d2d3d43ec3a7`.
- Exact GPS application/test source `9defd1296aa4575eafbe24981dfd95324ce14ef8`; exact-head Android CI [run 43568499998](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43568499998): SUCCESS. PR remains Draft and unmerged.
- After Health merge #295, GPS branch compares 6 ahead / 1 behind canonical; merge base remains `4fe915abfd6abb46072e1dfe0b30fcaa13f92014`. The one-behind commit touches only the two Health provenance files; there is no file overlap. GPS owner must run combined-head CI after any rebase.
- Exact PR #294 `ActivityTrackingService.kt` blob `3525cbc55b9cd9bf3bc3b5d6399ae3e5a8ff0d4d` captures OS mock flag and monotonic elapsed time and passes fixes through `GpsFixGate`, which already rejects mock, invalid/poor accuracy, stale/non-monotonic timestamps and sport-speed violations. It does not invoke canonical `ActivityEvidenceAnomalyPolicy.assessSegment` (blob `5643da3f8999298193b39d55e1d6104a95daf746`); source-continuity, long-gap and uncertainty-adjusted segment checks remain unintegrated. Integrator comment recorded on #294. Do not use display-smoothed points as evidence.
- Desktop Commander device list on 2026-11-14: localhost OFFLINE, last seen 99 hours ago. No ADB device attached; current phone/session state unknown. No install, launch, stop, permission or activity-data action. Physical GPS/session P0 remains BLOCKED_NOT_RUN.

### Exercise/catalog ownership
- PR #160 shares five files with #159 and four with #233; it remains an unmerged catalog chain with no exact-head GitHub Actions/Python unittest acceptance. Keep generated JSON/JS, builder, manifest and source-sync ownership together.
- Program PRs #204/#212/#213/#234 share generated program JSON/JS, builder and manifest; #213 also overlaps app.js with #214/#216/#282. Do not merge these branches blindly; require a single reconciled canonical catalog/program source and native regression/Android WebView tests.
- Last canonical offline motion inventory: 5 offline videos, 2 reviewed 16-frame sequences and 105 two-frame reference-only exercises. PR #289's mapping/license/hash regression is canonical; it does not create additional motion assets.

### Play and release hard gates
- No fresh Google Play API readback was obtained on 2026-11-14. Latest verified readback remains run 42405709027 from 2026-11-10: Internal 51019 completed, Alpha 51007 draft, Production not verified. Do not treat this as a current live Play observation.
- Play Health declaration/privacy/Data Safety reconciliation, physical Health Connect grant/revoke/no-data/error checks, compatible wearable/swimming validation, GPS physical P0 and final combined-head CI remain hard gates.
- VersionCode 51020 remains unallocated. No release workflow, signing, Play listing, upload or track state changed.
