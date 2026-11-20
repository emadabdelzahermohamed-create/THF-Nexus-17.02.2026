# TopHeroFit — active integration ownership (2026-11-20)

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical HEAD at this registry update: `a32075263aa7a87c43be58cd960e795fc0338be0` (documentation-only checkpoint over application merge `d8e315376de6785ec93a792342618737866ae121`).

## Health lane — merged

| PR | State | Scope / canonical disposition |
|---|---|---|
| #299 | Merged | Precise exercise/program to Health Connect sport mappings. |
| #300 | Merged | Future-dated Health Connect exercise-session rejection. |
| #301 | Merged | Metric value/interval anomaly rejection. |
| #304 | Merged | Cross-source exact metric mirror and overlapping interval reconciliation. |
| #305 | Merged | Walking/running/cycling exercise-session mirror and conflicting-sport reconciliation. |

PR #305 is the latest Health source change. It reconciles only verified Health Connect exercise-session records, preserves source labels and fails closed on conflicting activity types. Its exact-head CI and artifacts are in `RECOVERY_CURRENT_20261120.md`. No open PR in this checkpoint changes the same HealthConnectRepository reconciliation block.

## Active Health / GPS ownership

| PR | Current comparison to canonical | Owner boundary and disposition |
|---|---:|---|
| #93 | 2 ahead / 376 behind | Health Services reader/bridge, AndroidManifest, MainActivity and Health UI strings. Draft. Manifest declares 19 Health permissions versus canonical 5; remove unapproved scopes and rebase before integration. |
| #303 | 3 ahead / 3 behind | Native GPS / Activity Engine: ActivityTrackingService, session checkpoint, GPS fix gates/accumulator/presentation and tests. Draft. Exact pre-rebase CI passed; rebase to current canonical and pass physical P0. |
| #284 | 19 ahead / 73 behind | Older GPS provider fallback; overlaps ActivityTrackingService, MainActivity and WebView files with #303. Draft/non-mergeable; do not merge blindly. |
| #248 | 4 ahead / 210 behind | Bounded GPS route-smoother helper/test only; not yet integrated; GPS owner. |

The Health lane does not edit GPS/activity-tracking native files. The activity anomaly policy remains tested but unwired in the live service; GPS owner must address that in the native lane.

## Catalog, bilingual guidance and muscle metadata

| PR | Current comparison | Files / owner boundary |
|---|---:|---|
| #160 | 53 ahead / 231 behind | exercises.js/json, catalog manifest and build_catalog; main bilingual-catalog lane. |
| #257 | 5 ahead / 210 behind | exercises.js/json, catalog manifest/builder; Arabic core/conditioning cues. |
| #244 | 5 ahead / 210 behind | exercises.js/json, catalog manifest/builder; primary/secondary muscle tag deduplication. |
| #140 | 12 ahead / 231 behind | exercises.json, catalog manifest/builder and source-sync tests; bilingual step-source alignment. |
| #129 | 2 ahead / 231 behind | exercises.js and Arabic instruction-quality tests. |
| #260 | 15 ahead / 210 behind | exercises.js/json, catalog manifest/builder; front-squat and dip-machine Arabic cues. |
| #259 | 10 ahead / 210 behind | exercises.js/json, catalog manifest/builder; triceps-dip Arabic cues. |
| #255 | 200 ahead / 231 behind | Broad stack touching app.js, exercises, programs, motion manifest, index/styles and builders; not an isolated calf-cue change; do not merge as a small content patch. |

These branches share catalog JSON/JS, manifest and build_catalog ownership. Rebase and isolate one compatible batch at a time. Canonical audit: 112 exercises, 84 bilingual step-array length mismatches.

## Program semantics and workout persistence

| PR | Current comparison | Files / owner boundary |
|---|---:|---|
| #213 | 190 ahead / 231 behind | app.js, exercises/programs JSON/JS, motion manifest, styles and program/catalog builders; timed RIR semantics. |
| #138 | 10 ahead / 231 behind | programs.js/json, PROGRAMS_MANIFEST and build_programs; program level/timed-block budgets. |
| #234 | 10 ahead / 211 behind | programs.js/json, PROGRAMS_MANIFEST and build_programs; bodyweight progression. Same core program files as #138/#213. |
| #216 | 201 ahead / 231 behind | Active-workout resume plus app.js, exercises/programs/motion/style assets; overlaps #213/#224. |
| #227 | 6 ahead / 211 behind | app.js, index.html and workout-local-calendar.js; local calendar-day history/streak semantics. |

Canonical audit: 26 programs, 94 sessions, 470 exercise references, 232 timed references; all 232 still carry RIR, including six timed Superman references. Do not combine divergent program branches without rebase and semantic regression.

## Offline demonstrations, accessibility and training UX

| PR | Current comparison | Files / owner boundary |
|---|---:|---|
| #224 | 153 ahead / 231 behind | Active-workout offline motion, app.js, motion manifest/library, index/styles; overlaps #213/#216. |
| #111 | 2 ahead / 319 behind | motion-manifest.js and runtime preference test; older offline motion branch. |
| #152 | 2 ahead / 224 behind | app.js and screen-reader motion labels. |
| #139 | 1 ahead / 231 behind | Offline video license/asset-integrity test only. |
| #130 | 6 ahead / 231 behind | app.js/index/styles and truthful demo-coverage UI. |
| #182 | 2 ahead / 222 behind | app.js and video-error/reference fallback. |
| #124 | 1 ahead / 239 behind | app.js/index and accessible exercise-search announcements. |
| #115 | 6 ahead / 247 behind | app.js/index/styles, muscle presentation and workout guidance. |
| #120 | 6 ahead / 247 behind | app.js/index/styles, accessible rest-timer adjustments. |
| #187 | 17 ahead / 222 behind | app.js/index and dialog focus trap/restore helper. |
| #132 | 2 ahead / 231 behind | app.js and source-contract test for detail-dialog focus containment. |
| #256 | 174 ahead / 231 behind | Broad favorites/program-filter stack: app.js, exercise/program cards, catalog, motion and styles. |
| #254 | 168 ahead / 231 behind | Broad exercise-favorites stack; shares most of #256's app.js/catalog/motion/style files. |
| #258 | 7 ahead / 208 behind | app.js/index/styles and exercise-library equipment filters. |

The largest conflicts are app.js/index/styles shared by #115/#120/#124/#132/#152/#187/#213/#216/#224/#227/#254/#256/#258/#255; and catalog/motion/program assets shared by #160/#213/#216/#224/#234/#244/#254/#255/#256/#257/#259/#260. Keep ownership disjoint; no blind merges.

Latest canonical offline-motion inventory from November 19: 5 licensed videos, 2 reviewed 16-frame sequences, 105 reference-only exercises. Reference-only entries must not be represented as full-motion offline demonstrations.

## Physical P0 / release and QA ownership

| PR | Current comparison | Scope / disposition |
|---|---:|---|
| #119 | 14 ahead / 247 behind | Phone P0 preflight/snapshot scripts and checkpoint docs; no physical P0 result implied. |
| #118 | Open | Critical phone evidence checkpoint tests; must be run on the actual handset. |
| #127 | Open | Release candidate 51018 preparation; release/version/signing/Play ownership is outside this Health lane. |

Desktop Commander localhost is offline (last seen 76h ago); last known handset Samsung SM-A217F / Android 12, current state unknown. Physical GPS, Health Connect grant/revocation, watch/swimming and background-session acceptance remain not run.

## Integration rules

- Health permissions remain exactly the canonical five. No heart-rate permission without separate privacy, grant and actual-data review.
- Health records remain source-labelled, provider/version deduplicated and anomaly checked. Unknown/manual/untrusted sources cannot become reward-eligible.
- Swimming requires a reviewed provider, compatible watch/fitness-band metadata, stable record identity, valid exercise-session time and active/automatic recording. Metadata is not hardware attestation.
- GPS/activity-tracking native files remain owned by the GPS lane.
- Catalog/program/motion assets are edited only by their current owner branches or after explicit disjoint-file ownership is established.
- Every candidate must be rebased to current canonical and pass exact-head product/source/backend and Android CI. Physical-only tests remain separate hard gates.
- Play Health declaration/privacy reconciliation and physical acceptance remain hard release gates. No fabricated sensor, watch, Health, GPS, route or exercise evidence.
- No release version/workflow/signing/Play changes and no paid services.
