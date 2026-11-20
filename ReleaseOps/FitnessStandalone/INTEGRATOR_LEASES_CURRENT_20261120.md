# TopHeroFit — active integration ownership (2026-11-20)

Canonical repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical HEAD before this documentation commit: `d8e315376de6785ec93a792342618737866ae121`.

## Health lane — merged

| PR | State | Scope / canonical disposition |
|---|---|---|
| #299 | Merged | Precise exercise/program to Health Connect sport mappings. |
| #300 | Merged | Future-dated Health Connect exercise-session rejection. |
| #301 | Merged | Metric value/interval anomaly rejection. |
| #304 | Merged | Cross-source exact metric mirror and overlapping interval reconciliation. |
| #305 | Merged | Walking/running/cycling exercise-session mirror and conflicting-sport reconciliation. |

PR #305 owns the latest Health session change. Canonical blobs are recorded in `RECOVERY_CURRENT_20261120.md`. No open PR was found editing the same HealthConnectRepository session-reconciliation block at this checkpoint.

## Active / diverged ownership

| PR | Owner boundary | Current state / required action |
|---|---|---|
| #93 | Health Services reader/bridge, AndroidManifest, MainActivity, Health UI strings | Draft; 19 Health permissions versus canonical 5; 2 commits ahead / 375 behind current canonical; must remove unapproved scopes and rebase before integration. |
| #160 | Exercise catalog JSON/JS, catalog builder and bilingual instruction tests | Draft; 53 commits ahead / 230 behind; owns catalog data/build files; rebase before merging. Canonical still has 84 English/Arabic step-array length mismatches. |
| #213 | Timed-program semantics, RIR, shared app.js, catalog/program JSON/JS, motion manifest, styles | Draft; 190 ahead / 230 behind; broad shared-file ownership; isolate and rebase. Canonical has 232 timed references carrying RIR, including six timed Superman references. |
| #216 | Active-workout resume, app.js, catalog/program/motion/style files | Draft; 201 ahead / 230 behind; overlaps #213 and #224; coordinate before touching shared files. |
| #224 | Offline active-workout motion, app.js, catalog/motion/style assets | Draft; 153 ahead / 230 behind; overlaps #213/#216; rebase and keep media-license evidence. |
| #130 | Truthful offline demo coverage UI and tests | Open, non-mergeable; 6 ahead / 230 behind; overlaps app.js/index/styles. |
| #139 | Offline video license and asset-integrity test | Open, non-mergeable; 1 ahead / 230 behind; test-only; reconcile with current motion manifest. |
| #182 | Offline video error/reference fallback UI | Open, non-mergeable; 2 ahead / 221 behind; overlaps app.js and demo UX. |
| #137 | Minimal Health permission test and reconciliation document | Open, non-mergeable; 3 ahead / 230 behind; test/docs only, not a manifest owner. |
| #119 | Phone P0 preflight/snapshot scripts and checkpoints | Open, non-mergeable; 14 ahead / 246 behind; physical preflight tooling; no physical P0 result implied. |
| #303 | Native GPS / Activity Engine | Draft; head `a3289482f93e500e2e0146e8f9b2d838a2390cb3`, 3 ahead / 2 behind current canonical; exact pre-rebase CI passed; native owner must rebase and pass physical P0. |
| #284 | Older GPS provider fallback and MainActivity/WebView | Draft, non-mergeable; 19 ahead / 72 behind; overlaps #303; do not merge. |
| #248 | Bounded GPS route smoother helper/test | Draft; 4 ahead / 209 behind; isolated helper, not yet integrated; GPS owner. |
| #257 | Arabic exercise cue content and catalog builder | Draft; 5 ahead / 209 behind; catalog ownership; rebase and coordinate with #160. |
| #258 | Exercise library profile/equipment filters | Draft, non-mergeable; 7 ahead / 207 behind; app.js/index/styles ownership; coordinate with #216/#224. |

Ahead/behind values are current comparisons to canonical `d8e315376de6785ec93a792342618737866ae121` at checkpoint creation; PR branches are not interchangeable merely because they pass CI. Rebase and rerun exact-head CI before merge.

## Non-negotiable integration rules

- Health Connect permissions remain exactly the canonical five. No heart-rate permission without separate privacy, grant and actual-data review.
- Health records remain source-labelled and provider/version deduplicated. Unknown/manual/untrusted sources do not become reward-eligible.
- Swimming remains compatible trusted wearable exercise-session data only; metadata is not hardware attestation.
- No GPS/activity-tracking native files are changed by the Health lane.
- Catalog/program/motion assets are edited only by their current owner branches or after explicit disjoint-file ownership is established.
- Every PR must be based on current canonical, pass exact-head product/source/backend and Android CI, and preserve physical-only acceptance gates.
- Play Health declaration/privacy and physical Health/GPS/wearable checks are hard release gates. No fabricated sensor, watch, Health, route or exercise evidence.
- No release version/workflow/signing/Play changes and no paid services.
