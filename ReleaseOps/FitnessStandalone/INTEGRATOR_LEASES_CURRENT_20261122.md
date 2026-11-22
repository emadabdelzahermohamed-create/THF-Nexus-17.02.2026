# TopHeroFit — active integration ownership (2026-11-22)

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical application merge: `0b2b52d204fc94944a077a383db7c5cb785c9147`. The PR comparison snapshot below was measured against canonical tip `20a052fcab20310043e2663b3beac9c88a6675ad`; checkpoint commits after that snapshot are documentation-only.

This registry supersedes the 2026-11-21 snapshot. Shared files are not assumed free. Only disjoint, exact-head-tested handoffs may integrate.

## Canonical Health lane

| PR | State | Scope / disposition |
|---|---|---|
| #282 | Merged | Metric truthfulness and missing-vs-zero distinction. |
| #301 | Merged | Metric value/interval anomaly rejection. |
| #304 | Merged | Cross-source exact metric mirror and overlapping interval reconciliation. |
| #305 | Merged | Walking/running/cycling session mirror and conflicting-sport reconciliation. |
| #306 | Merged | Compatible trusted wearable swimming session reconciliation. |
| #308 | Merged | Same-provider/type/record-ID/version/time payload conflict quarantine. |

PR #308 owns the canonical `HealthRecordDeduplicationPolicy.kt`, `HealthConnectRepository.kt` conflict wiring, its focused Kotlin tests and one product/source-contract test. It changed exactly four files and passed exact-head workflow 45028206758 on source SHA `44a84fa6a5a9abe47e89ac13cb8eef026864436a` before merge. The inspected open PRs #93, #137, #160, #213, #224 and #307 do not change those same four files.

Canonical Health Connect permissions remain exactly five: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE and READ_ACTIVE_CALORIES_BURNED. Heart rate is not requested.

## Active Health / GPS ownership

| PR | Current comparison to canonical | Owner boundary / disposition |
|---|---:|---|
| #93 | 2 ahead / 409 behind | Health Services bridge, manifest, MainActivity and Health rationale strings. Draft. Manifest has 19 Health permissions vs canonical 5; remove 14 unapproved scopes and rebase. |
| #137 | 3 ahead / 264 behind | Permission reconciliation document and test only. Does not change manifest; rebase before integration. |
| #307 | 12 ahead / 5 behind | Native GPS source arbitration: ActivityLocationFallbackPolicy, ActivityTrackingService and tests. Draft. Exact application SHA `ff37ab739b4372d2512cec26e4d4bff6353db57b` CI PASS; physical P0 pending. |
| #284 | 19 ahead / 106 behind | Legacy GPS/provider fallback and shared UI. Draft/stale; native hunks superseded by #303, UI conflicts with #93/#216/#224. Do not merge. |
| #248 | 4 ahead / 243 behind | Standalone GPS route smoother helper/test only; no production call site. Do not add a duplicate display smoother. |

Health lane must not edit GPS/activity-tracking native files, MainActivity, manifest or Health Services bridge while their owners retain these leases.

## Catalog and bilingual guidance

| PR | Current comparison | Files / owner boundary |
|---|---:|---|
| #160 | 53 ahead / 264 behind | exercises.js/json, catalog manifest, build_catalog and bilingual quality tests. |
| #213 | 190 ahead / 264 behind | programs.js/json, program builder, app.js, and inherited catalog/motion files; highly stacked/diverged. |
| #224 | 153 ahead / 264 behind | active-workout demo module plus app.js, index.html, styles and motion/catalog dependencies. |

These PRs share catalog JSON/JS, manifests, builders, app.js and motion assets. Rebase and isolate one compatible change at a time; do not merge whole divergent stacks.

## Release and privacy ownership

ReleaseOps, version allocation, workflows, signing, Google Play listing/tracks and uploads remain canonical integrator-only. Play Health declaration/privacy, Data Safety and physical grant/revocation checks remain hard gates. No versionCode 51020 allocation is authorized.

## Integration protocol

1. Fetch the current canonical branch tip and current PR head.
2. Compare exact changed paths with active leases; reject shared-file overlap.
3. Rebase/isolate onto current canonical without overwriting another owner.
4. Run exact-head Product, source-contract, backend and Android API 36 unit/lint/build validation.
5. Record artifact identity and hashes; distinguish unsigned validation AAB from signed release.
6. Merge only the tested exact head with expected-head protection.
7. Keep physical P0, Health Connect grant/revocation, wearable eligibility, Play declaration/privacy, signing and publication as separate acceptance gates.

No paid infrastructure, unrelated project or unverified sensor/Health/route evidence is authorized.


## Late GPS / release refresh — 2026-11-22 18:05 UTC

Comparison snapshot base: `6a5a9f470c4aa165733f86d958d7651f55e2aed7`.

| PR | Current comparison | Updated disposition |
|---|---:|---|
| #307 | 1 ahead / 2 behind | Draft. Head `45b27cc6a04b48931291e821efc85e76569965fe`; exact-head CI 45052702946 PASS. Four GPS-only policy/service/test/source-contract files. Fused callback now remains subscribed during framework fallback; lifecycle teardown still invalidates it. Unsigned QA AAB only. Physical P0 blocks merge. |
| #284 | 19 ahead / 110 behind | Draft/stale. Native GPS overlaps and is superseded by #303/#307; remaining app.js/index.html/MainActivity UI overlaps shared leases #93/#216/#224. Do not merge. |
| #93 | 2 ahead / 413 behind | Draft. Manifest declares 19 Health permissions vs canonical 5; remove 14 unapproved scopes and rebase. Owns manifest/MainActivity/Health Services bridge. |
| #137 | 3 ahead / 268 behind | Open; permission reconciliation document and test only. |
| #248 | 4 ahead / 247 behind | Draft. Standalone route-smoother helper has no production call site; do not add a duplicate display smoother. |
| #216 | 201 ahead / 268 behind | Draft. Active-workout resume policy plus app.js/index.html/styles; shared UI ownership with #213/#224. |
| #160 | 53 ahead / 268 behind | Draft. Exercise catalog data, manifest and builder. |
| #213 | 190 ahead / 268 behind | Draft. Program semantics/builders and shared app.js/catalog/motion assets; highly diverged. |
| #224 | 153 ahead / 268 behind | Draft. Offline active-workout demos plus shared app.js/index.html/styles/motion/catalog assets. |

#307's exact-head run and artifact are recorded in RECOVERY_CURRENT_20261122.md and RELEASE_CURRENT.json. The canonical branch has received ReleaseOps-only state/checkpoint commits after the tested base; the GPS application diff remains disjoint from those files. Do not rebase merely to rebuild unchanged AAB bytes. Before any merge, re-check current base/head and exact changed paths; physical P0 remains mandatory.

Release writer remains canonical-integrator-only. Latest read-only Play readback (2026-11-22 17:56:05 UTC, run 43739661313 attempt 7): Internal 51019 Completed, Alpha 51007 Draft, Production not listed/not verified; no upload or commit. VersionCode 51020 remains unallocated. Owner API write access and signing-key access remain unverified.
