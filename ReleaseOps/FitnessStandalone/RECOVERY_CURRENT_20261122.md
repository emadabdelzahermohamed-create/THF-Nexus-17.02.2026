# TopHeroFit — canonical recovery checkpoint (2026-11-22)

Observed: 2026-11-22 13:40 UTC.
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical application merge: `0b2b52d204fc94944a077a383db7c5cb785c9147`.
Canonical branch tip when the PR ownership comparison was refreshed: `20a052fcab20310043e2663b3beac9c88a6675ad` (the four commits after the application merge are checkpoint/ownership documentation only).

## 1. Canonical Health Connect change merged

PR [#308 — quarantine conflicting same-version Health Connect record payloads](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/308) is merged.

- Tested source SHA: `44a84fa6a5a9abe47e89ac13cb8eef026864436a`.
- Merge commit / canonical HEAD: `0b2b52d204fc94944a077a383db7c5cb785c9147`.
- Exact-head workflow: [45028206758](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45028206758) — SUCCESS.
- Product, source-contract and backend regression step: PASS.
- Android API 36 setup: PASS.
- `:app:testDebugUnitTest`, `:app:lintDebug`, `:app:assembleDebug`, and `:app:bundleRelease`: PASS.
- Gradle BUILD SUCCESSFUL in 2m07s.

### Behavior

The previous provider-scoped version selector chose the first record when two records shared the same source/type/record ID, client version and provider modification time. If their reward-relevant payload or provenance differed, read order could decide which record entered verified totals.

The merged correction:
- Computes an internal, length-prefixed fingerprint for reward-relevant Steps, Distance, Active Calories and Exercise Session fields, plus client-record identity, recording method, device metadata and evidence decision.
- Continues selecting the highest client record version, then newest provider modification time.
- Collapses tied latest records only when all fingerprints are present and identical.
- Quarantines every tied latest record when fingerprints differ or are unavailable, preserving source-labelled provenance with `CONFLICTING_RECORD_VERSION_PAYLOAD`.
- Never resurrects an older version when the latest revision conflicts.
- Leaves unkeyed records independent and retains the existing cross-provider metric/session reconciliation.

### Exact files and canonical blob SHAs

| File | Canonical blob SHA |
|---|---|
| `HealthRecordDeduplicationPolicy.kt` | `5ee3626544fe4780538d14278b8076b110044aa1` |
| `HealthConnectRepository.kt` | `0e025f8297a2a01afc4d09473d2a1af962d91bb3` |
| `HealthRecordDeduplicationPolicyTest.kt` | `7365dcaf243eaf3672f6e88603d621b39da58bbf` |
| `test_health_record_version_conflicts.py` | `4d687f8baec478b8ba9929ecae5c880298afa506` |

The focused Kotlin policy suite contains 10 tests; the new product/source-contract file contains 4 tests.

Artifact 14757185084 (63,091,001 bytes):
- GitHub artifact ZIP SHA-256: `8ad614141b2352315871229525f0dbfcf4acc116d08c1d4df34c298b84af4f19`.
- QA APK SHA-256: `04f7f1880d1e450e04242d9534fee927e38fe9f7d72b0465cec9234086890470`.
- Unsigned validation AAB SHA-256: `6a03489b1f4e8b568d5413b055c3828f98485b4e8836d55654864e36e374b0ff`.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. Validation only; no release allocation or Play upload.

No GPS/activity-tracking native files, Health manifest/permissions, MainActivity, release/version/workflow/signing or Play files changed.

## 2. Health permission and provenance baseline

Canonical manifest blob SHA remains `0969cdb2f18775f23e0870bf754612a04376895f`. Exactly five Health Connect permissions remain:
- `READ_STEPS`
- `READ_EXERCISE`
- `WRITE_EXERCISE`
- `READ_DISTANCE`
- `READ_ACTIVE_CALORIES_BURNED`

No heart-rate permission. Optional heart rate remains unavailable unless separately approved, granted and backed by actual data.

PR [#93 — Health Services integration](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93) remains Draft/open. Fresh current-canonical comparison: 2 ahead / 409 behind. Its manifest blob `a3b24f09e6b0c8a67b0fee3e7578317cfe979092` declares 19 Health permissions, 14 more than canonical: basal metabolic rate, blood glucose, blood pressure, body fat, heart rate, height, nutrition, oxygen saturation, resting heart rate, sleep, speed, total calories, VO2 max and weight. It owns the manifest, MainActivity and Health Services bridge; no concurrent edit was made. A fresh scope/rebase blocker comment was posted: [PR #93 comment](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93#issuecomment-7079935393).

PR [#137 — permission minimization tests](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/137) remains open, 3 ahead / 264 behind; it changes only a reconciliation document and test, not the manifest. It is not a substitute for correcting PR #93.

Health changes already canonical:
- #282 metric truthfulness.
- #301 metric anomaly rejection.
- #304 cross-source metric mirror/overlap reconciliation.
- #305 walking/running/cycling session reconciliation.
- #306 compatible wearable swimming session reconciliation.
- #308 same-provider record-version conflict quarantine.

These policies validate Health Connect metadata and provider consistency. They are not cryptographic device attestation or proof of physical exercise.

## 3. GPS and physical acceptance — separate owner lane

Latest canonical GPS checkpoint remains [GPS_MAP_QUALITY_20261121.md](./GPS_MAP_QUALITY_20261121.md). Latest canonical recovery baseline before this merge was [RECOVERY_CURRENT_20261121.md](./RECOVERY_CURRENT_20261121.md).

PR [#307 — Fused/framework source arbitration](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/307) is still OPEN, Draft and unmerged:
- Branch head: `28d2fdee453a387ffe01a9b040737ca6f95fc3cd`.
- Application source SHA tested: `ff37ab739b4372d2512cec26e4d4bff6353db57b`; later branch commits are checkpoint documentation only.
- Current canonical comparison: 12 ahead / 5 behind.
- Exact-head candidate run: [44995245447](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44995245447) — SUCCESS; Product 77/77, source-contract 36/36, backend 29/29, Android 338/338, API 36, lint, APK and unsigned AAB validation passed.
- PR #307 owns `ActivityLocationFallbackPolicy.kt`, `ActivityTrackingService.kt`, its native tests and source-contract test. The Health lane did not edit these files.
- Its November 22 recovery/GPS checkpoint files are candidate-branch documentation, not canonical files.

PR #284 remains stale/Draft: 19 ahead / 106 behind, overlapping native work superseded by #303 and shared UI ownership. PR #248 remains Draft, 4 ahead / 243 behind; its standalone route-smoother helper has no production call site. Neither is approved for merge.

Physical P0 remains BLOCKED_NOT_RUN. Latest recorded Desktop Commander localhost is OFFLINE; last known handset is Samsung SM-A217F / Android 12, current app/session state unknown. No ADB, install, launch, notification action, location-setting change or Health record read was attempted. No physical GPS, route, wearable or Health acceptance is claimed.

The tested `ActivityEvidenceAnomalyPolicy.assessSegment()` remains unwired in the live service. The GPS owner must reconcile it with `GpsFixGate` and `GpsDistanceAccumulator`; the Health lane did not add a second native GPS gate. GPS rewards remain disabled.

## 4. Exercise catalog, programs and offline demonstrations

Current open handoffs remain diverged and own shared files:
- #160 bilingual catalog: 53 ahead / 264 behind; owns exercises.js/json, catalog manifest and builder.
- #213 timed RIR/program semantics: 190 ahead / 264 behind; touches programs, builders, app.js and shared motion/catalog assets.
- #224 active-workout offline demos: 153 ahead / 264 behind; owns active-workout demo module and shared app.js/index/motion assets.

Do not merge these branches wholesale. Rebase and isolate one semantically reviewed change at a time. The Health PR #308 changed no catalog, program, offline-media, voice or accessibility UI files.

## 5. Play and release gates

Latest independently recorded Play readback is 2026-11-21:
- Internal 51019: Completed.
- Alpha 51007: Draft.
- Production: not listed / not verified.
- No fresh 2026-11-22 Play readback is claimed.
- VersionCode 51020 remains unallocated.

Play Health declaration/privacy reconciliation, Data Safety consistency, physical Health Connect grant/revocation, wearable validation, GPS physical P0, signing and owner/API prerequisites remain hard release gates. No listing, track, version, signing, upload or Production state was changed.

No paid service or unrelated project was used.
