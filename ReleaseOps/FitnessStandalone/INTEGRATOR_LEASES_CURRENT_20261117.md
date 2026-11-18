# TopHeroFit Integrator file ownership / lease registry — 2026-11-17

Scope: TopHeroFit only. Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical application source head at this checkpoint: `b248a3571d871c604dbc3a11af72858bbac74eb9`.

## Authority and invariants

- The canonical integrator is the sole writer for release/version allocation, canonical workflows, signing configuration, Google Play edits/uploads/track commits and Production promotion.
- Release chain remains source SHA -> exact-head tests -> signed AAB -> independent Play Internal readback.
- Next Android versionCode must be greater than 51019. 51020 is not allocated.
- Never merge an untested handoff, rebuild/reupload unchanged bytes, or claim phone/Play/Production PASS without exact artifact SHA and independent readback.
- Physical P0, privacy/policy, owner API/key and signing prerequisites are separate gates; source CI does not waive them.

## Active file-level ownership

| Surface | Owner / PR | Current rule |
|---|---|---|
| `ActivityTrackingService.kt`, `ActivityLocationFallbackPolicy.kt`, `ActivitySessionCheckpoint.kt`, `ActivitySnapshotPolicy.kt`, `GpsFixGate.kt`, `GpsDistanceAccumulator.kt`, `GpsFixPresentationPolicy.kt` and related GPS tests | PR #297, head `c340e330d8e634fab231976bac1b8f9ad44915cc` | Sole native GPS/session owner. Exact-head CI 44139154404 PASS. Keep Draft until physical P0; no parallel service edits. |
| Health metric summary hunk in `app.js` | PR #282 merged at `b248a3571d871c604dbc3a11af72858bbac74eb9` | Null/undefined/invalid metrics render as unavailable; genuine zero remains zero. Exact-head CI 44138210115 PASS. No Health permission changes. |
| Remaining `app.js` active-workout/session UI and offline demo runtime | PRs #216 and #224; #284 also touches map UI | Shared ownership hold. No whole-file overwrite. Isolate minimal hunks and run combined product/source/Android CI. #216/#224 remain highly divergent. |
| `MainActivity.kt`, `AndroidManifest.xml`, Health Services bridge and rationale strings | PR #93 | Health Services owner. Canonical Health Connect allowlist is exactly five scopes; #93 still requests 19 and is blocked. #284 also touches MainActivity/source contract. |
| Exercise catalog JSON/JS, catalog builder/manifest/tests | PR #160 | Catalog owner; 53 ahead / 219 behind, Draft, no exact-head native CI. Coordinate with #213/#224. |
| Program JSON/JS, program builder/manifest and prescription UI | PR #213 | Program/RIR owner; 190 ahead / 219 behind, Draft, no exact-head native CI. Coordinate with #160/#224/app.js owner. |
| Offline demo runtime and active-workout demo UI | PR #224 | Demo owner; 153 ahead / 219 behind, Draft, no exact-head native Node/Android CI. |
| `ActivityGpsRouteSmoother.kt` and test | PR #248 | Helper/test only; 4 ahead / 198 behind, Draft; not integrated into service and no Android Gradle/JUnit exact-head CI. |
| ReleaseOps, release workflows, signing, versionCode, Play | Canonical integrator only | No parallel PR/agent may allocate a version, change signing/workflow or write Play. Owner API/key prerequisites remain unverified. |

## Current PR register (compared with canonical `b248a3571d871c604dbc3a11af72858bbac74eb9`)

| PR | State | Ahead / behind | Head | Decision |
|---|---|---:|---|---|
| #297 GPS/session | Draft | 5 / 0 | `c340e330d8e634fab231976bac1b8f9ad44915cc` | Exact-head CI 44139154404 PASS; 14 GPS files only; physical P0 required. |
| #284 Maps/GPS | Draft | 19 / 61 | `274155eafdfff381009ef5814a621f32b225f1a8` | No current-head CI; overlaps #297/#93/#282/#216; do not merge wholesale. |
| #282 Health metric truthfulness | Merged | — | `a7fb7af746640f7154c4ef079d1a7b69e1be7a39` | Merge `b248a3571d871c604dbc3a11af72858bbac74eb9`; exact-head CI 44138210115 PASS; two-file isolated fix. |
| #93 Health Services | Draft | 2 / 364 | `1cc08cef7dae7f432275fd23960f4390a49db14c` | 19 scopes vs canonical five; no current-head CI; blocked. |
| #216 Workout resume | Draft | 201 / 219 | `1ef915886fdac62c8fe1d5e50505fd354d989ee3` | Stacked/divergent app.js/catalog branch; no exact-head workflow. |
| #160 Arabic catalog | Draft | 53 / 219 | `82e5ca5c2fe796b82cb8d02dbeece3f4b5df125c` | Source assertions only; no exact-head native CI. |
| #213 Timed RIR/programs | Draft | 190 / 219 | `f719214d813f367350d8a10591903d16b68f8da1` | Stacked/divergent; no exact-head Python/CI. |
| #224 Offline demos | Draft | 153 / 219 | `cc703baa3cc0e1866e50aafb9a8caad26583fc0a` | Compatibility harness only; no exact-head native Node/Android CI. |
| #248 Route smoother | Draft | 4 / 198 | `67d3b438815fe83ced301551aee43f5a6548c91d` | Helper/test only; no Android Gradle/JUnit CI. |
| #294 GPS predecessor | Closed unmerged | — | `71364e31f4f631dc2593f38b15a8b92626aacdfe` | Superseded by #297; do not reopen/merge. |
| #295 Health provenance | Merged | — | — | Merged after exact-head CI. |
| #299 Health sport mapping | Merged | — | — | Merged after exact-head CI. |
| #300 Health future-session guard | Merged | — | — | Merged after exact-head CI. |
| #269 Competition backend | Merged | — | — | Provisional `strength_volume_kg_reps` only; admin key/deployment verification absent. |

## Release / device blockers

- Latest device list at 2026-11-17 19:43 Cairo: Desktop Commander localhost OFFLINE, last seen about 8 hours earlier. Last known handset Samsung SM-A217F / Android 12. Current app/session state unknown; preserve it.
- Last recorded device-wide `location_mode=0` is from 2026-11-09 and was not changed. No ADB, install, launch, Stop, setting change or activity-data action in this recheck.
- Physical P0 remains BLOCKED_NOT_RUN: stationary 60-second drift, measured outdoor walk/run/cycle, permission downgrade, first-fix latency, screen-off/background, notification Pause/Resume/Stop and process-death recovery.
- Latest available read-only Play probe: run 43739661313 attempt 2, completed 2026-11-16 17:56:42Z. Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified; upload/commit attempts false. No newer Play probe found in the latest 100 workflow runs.
- The probe confirms read-only Android Publisher access only; Play write permission and GCP Secret Manager signing access are not verified. Legacy promotion workflow remains pinned to old source/certificate and versionCode 51019; it is not a 51020 workflow.
- Route sync remains design-only. Completed routes remain local in WebView localStorage; no authenticated route endpoint or precise-location upload.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains unwired in `ActivityTrackingService`; no full anti-cheat, cryptographic location attestation or reward eligibility PASS.
- No paid infrastructure, Maps billing/key or unrelated project.
