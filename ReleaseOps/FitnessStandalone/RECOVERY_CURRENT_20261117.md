# TopHeroFit canonical recovery — 2026-11-17

> Authoritative update: 2026-11-17. Repository remains the sole source of truth: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`. This checkpoint supersedes time-sensitive PR comparisons and validation status in the November 16 recovery. No GPS/activity-tracking native files, release versions/workflows, signing or Play state were edited.

## Canonical branch and completed Health delivery

- Canonical branch: `agent/codex/fitness-recovery/20261023`.
- Canonical application merge: PR #300, squash merge `a2abf30766c943ae86672eaaa746b67f5497b3fb`.
- PR #300 exact tested source HEAD: `db26ff77dfce8a799b0f845af88336efdac2b317`.
- Candidate branch: `agent/codex/health-session-temporal-guard-20261117-r1`.
- Compare before merge: 8 commits ahead / 0 behind; exactly six Health evidence source/test files.
- PR: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/300
- Exact-head CI: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44093001171 — SUCCESS.
- Product tests 67/67; source-contract tests 34/34; backend tests 29/29.
- Android `:app:testDebugUnitTest`, `:app:lintDebug`, `:app:assembleDebug`, and `:app:bundleRelease`: PASS. Gradle BUILD SUCCESSFUL in 2m 54s.
- QA identity only: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. No Play signing, upload, or track change.
- Artifact ID `14332068360`; ZIP SHA-256 `c337d8614de0b636c90504a367b2677c410e4919a1b029e7906da16038f00d06`.

### PR #300 — future-dated Health Connect session rejection

Health Connect `readRecent()` now captures its exact query-end/observation instant and carries the epoch timestamp only inside `HealthRecordEvidence`. The evidence policy requires that boundary for exercise-session reward eligibility and returns `MISSING_OBSERVATION_TIME` when absent or `FUTURE_EXERCISE_SESSION` when the session end is later than the read boundary. The privacy-safe presentation policy independently rechecks the same boundary, so inconsistent upstream VERIFIED flags cannot upgrade a future-dated or observation-less session.

The observation timestamp is not exposed in `HealthRecordProvenanceSummary`. No raw provider/client IDs or device manufacturer/model were added to the bridge.

Exact canonical post-merge blob SHAs:
- `HealthConnectRepository.kt`: `a4e0f769e1bdcdb860f7102c0e0928213f40b778`
- `HealthRecordEvidencePolicy.kt`: `4434c82d5d30f8eef69de2e4e5662f31c0cac4b9`
- `HealthRecordProvenancePresentationPolicy.kt`: `91b71686ee21ea20d3ed1e46ea2460e432a8f863`
- `HealthRecordEvidencePolicyFailClosedTest.kt`: `3a74f2ad3bc4a88109bec8eaf525ad0db74fa137`
- `HealthConnectProvenanceTest.kt`: `6fc735cdba9ecf555b74efc1d3d3a8689f255d5b`
- `HealthRecordProvenancePresentationPolicyTest.kt`: `360c47512f7737d593c0ac2a15ca25f149265be4`

The first CI attempt caught a Kotlin nullable-receiver compile error; the guard was corrected with an explicit non-null comparison. The second exact-head run passed all jobs. No Health permissions, manifest, MainActivity, GPS, app.js, catalog/program data, release version, workflow, signing or Play files changed in PR #300.

## Health Connect least-privilege baseline

Canonical manifest blob: `0969cdb2f18775f23e0870bf754612a04376895f`. Exactly five Health Connect scopes remain:
1. READ_STEPS
2. READ_EXERCISE
3. WRITE_EXERCISE
4. READ_DISTANCE
5. READ_ACTIVE_CALORIES_BURNED

`READ_HEART_RATE` remains absent.

### PR #93 — Health Services ownership blocker

- PR: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93
- Current head: `1cc08cef7dae7f432275fd23960f4390a49db14c`.
- Compare to current canonical after PR #300: 2 ahead / 359 behind, diverged and not mergeable.
- PR manifest blob: `a3b24f09e6b0c8a67b0fee3e7578317cfe979092`, declaring 19 Health permissions rather than five. The 14 extras include total calories, sleep, heart rate/resting heart rate, body measurements, BMR, oxygen saturation, VO2 max, speed, nutrition, blood pressure and blood glucose.
- PR #93 owns AndroidManifest, MainActivity, HealthConnectServiceSource, HealthServiceModels, HealthServicesActivity, localized strings and its source-contract tests.
- Handoff comment: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93#issuecomment-6949552478
- Rebase onto current canonical, remove the 14 additional scopes, expose only the privacy-reduced per-record provenance contract, then run exact-head CI. Play Health declaration/privacy reconciliation and physical grant/revoke checks remain hard gates.

## GPS checkpoint and owner handoff

Starting recovery: `RECOVERY_CURRENT_20261115.md`, blob `09b1df7dfb7280953c07106a405b85f6eb945a43` (authoritative content dated 2026-11-16).

Latest GPS checkpoint: `GPS_MAP_QUALITY_20261116.md`, blob `129ac2360d8978fbf5cfd83444b217a9e1e400ad`. It contains the November 17 stale restore-anchor correction and limited physical QA notes.

### PR #297 — GPS native owner only

- PR: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297
- Current head: `c289043e43ae7bdad955f2995edc0156b616a41f`.
- Current compare after PR #300: 3 ahead / 1 behind canonical; diverged and not mergeable.
- The PR body cites tested source `349fcbb40ffbda9641e33ab68637b29c99bc960e`, but fetched current-head diff `c289043e...` includes later application/test changes in `ActivitySnapshotPolicy.kt`, `ActivityTrackingService.kt` and `ActivitySnapshotPolicyTest.kt`. Therefore the earlier run `44038771808` on `349fcbb...` does not validate the current PR head.
- GPS owner handoffs: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297#issuecomment-6949456299 and https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297#issuecomment-6949574452
- Required: rebase onto current canonical, run exact-head CI on the new head, preserve physical P0 and Play/privacy gates. No GPS-owned files were edited by this Health run.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains unwired in the live service; do not claim full GPS anti-cheat or location attestation.

### Physical-device boundary

- Current Desktop Commander device list: `localhost` OFFLINE, last seen about 3 hours ago at this check.
- Latest GPS checkpoint had a prior safe check where localhost was the Samsung SM-A217F / Android 12 Termux host, but `adb devices -l` was empty; no ADB workstation was attached.
- Earlier limited QA reported indoor fixes filtered, zero stationary steps/distance and no accepted route point. Native bridge Pause/Resume returned expected paused state, but full UI/notification interaction was not proven.
- Outdoor measured walk/run/cycle, 60-second stationary drift, screen-off/background, notification action taps, process-death restore and full physical P0 remain unverified. Do not infer them from CI.

## Catalog, programs and offline demonstrations — fresh canonical audit

Canonical data blob SHAs:
- `exercises.json`: `425f0dab3fa1b0718cf84dd818a26d3585881718`
- `programs.json`: `013022b7cb647e17b66cd2c9f3aad20c39050062`
- `motion-manifest.js`: `14c10ef922840641336150efa28a11292e345140`

Fresh audit:
- 112 exercises; 84 Arabic/English step-array length mismatches.
- 9 rows match the three reviewed generic Arabic fallback cue strings (this exact-string count is not an exhaustive semantic-quality count).
- 26 programs, 94 sessions, 470 exercise references.
- 232 timed references; all 232 currently have `targetRir`.
- Six timed Superman references carry RIR despite being duration-based.
- Motion manifest: 5 licensed offline-video entries and 2 reviewed 16-frame sequences. 105 exercises remain reference-only; do not describe these as full-motion offline demonstrations.

### Catalog/program/demo PR ownership

| PR | Current compare to canonical | Files/decision |
|---|---:|---|
| #160 | 53 ahead / 214 behind, diverged | 17 catalog/builder/test files; bilingual cues; overlaps #213 |
| #213 | 190 ahead / 214 behind, diverged | catalog + program builders/data, app.js, motion/UI/tests; isolate timed RIR data from stacked UI changes |
| #224 | 153 ahead / 214 behind, diverged | active-workout demo, app.js, motion manifest, catalog and tests; overlaps #213 |
| #282 | 2 ahead / 98 behind, diverged | app.js + Health metric truthfulness test; shares app.js with #216 |
| #216 | Open, Draft | app.js and active-workout resume UI ownership |

Fresh owner handoffs:
- #160: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/160#issuecomment-6949553330
- #213: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/213#issuecomment-6949554142
- #224: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/224#issuecomment-6949557540
- #282: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/282#issuecomment-6949562692

Do not merge the diverged branches as-is. Rebase to canonical, isolate disjoint data/UI ownership, verify clip-to-exercise mappings and licensing, then exact-head test.

## Play and release boundary

- Latest read-only Play probe recorded in the November 16 recovery: Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified.
- No fresh Play readback was performed in this run.
- VersionCode 51020 remains unallocated.
- No AAB signing, upload, Play track mutation, listing change or Production promotion occurred.
- Play Health declaration/privacy reconciliation remains a hard gate.

## Next execution priorities

1. Reconcile PR #93 to the five-scope permission baseline and integrate privacy-reduced per-record provenance through its owned bridge.
2. Keep future-dated/observation-less session rejection canonical; next Health anti-cheat work must validate actual metric intervals/values and preserve source-labelled deduplication.
3. Connect walking/running/cycling Health records only with genuine phone-session reconciliation evidence; do not alter GPS-owned files.
4. Rebase and isolate catalog bilingual cue fixes, timed-program RIR correction and offline-demo mapping from the shared PR #160/#213/#224 stacks.
5. Expand genuinely licensed offline full-motion clips; keep 105 reference-only exercises honestly labelled.
6. Keep heart rate deferred until a real optional data path and separate permission/privacy review exist.
7. Do not approve release readiness until physical GPS/Health/wearable checks and Play Health/privacy reconciliation are completed.

No sensor, watch, Health Connect record, physical route or exercise evidence was fabricated. No paid services or unrelated projects were used.
