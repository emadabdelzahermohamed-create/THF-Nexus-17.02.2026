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
- Relative to current canonical HEAD `dbe85572669fe50fd16cb3e126ab763efd0d08f0`, #292 is 13 commits ahead / 4 behind with merge base `dedd5f39001781c19e7e19bdee8f44e2fa97b01d`. Its five app/test files are disjoint from #293, but the branch has not been rebased or tested against the current canonical combined head. GitHub reports mergeable/clean; that does not replace combined-head CI or physical QA.

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
