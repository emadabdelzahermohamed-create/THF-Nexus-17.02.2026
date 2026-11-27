# TopHeroFit — Current Integrator Leases

**Observed:** 2026-11-27T17:51:42Z  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Application baseline before this checkpoint:** `779df53146e23e76fe7b1faabffbc0e3540ee29a`  
**ReleaseOps branch tip before checkpoint:** `11f06f2554593a8d40949bdadcc142c1001fdc94`

## Exclusive canonical ownership

Only the canonical integrator writes:
- release/version allocation and `RELEASE_CURRENT.json`;
- release/publication workflow logic and triggers;
- signing and Google Play upload/commit/promotion;
- canonical recovery, GPS-quality and lease checkpoints.

No handoff PR may allocate versionCode, sign, upload, commit a Play release or promote a track.

## Current priority leases

| Lane | PR / branch | Current evidence | Decision |
|---|---|---|---|
| Canonical GPS/activity engine + Android 14 FGS guard | #315 — `agent/codex/gps-canonical-activity-engine-20261127-r1`; head `32b2eae0558e609bd2e3c453e1af6d25bc9df406` | Exact-head run 45955722335 PASS: Product 84 / Source 41 / Backend 29 / Android 359; zero failures/ignored; artifact 15178872128 independently rehashed; unsigned AAB. At CI time it was 9 ahead / 0 behind base 11f06f. The canonical branch then advanced four ReleaseOps-only checkpoint commits to b403005; current compare is 9 ahead / 4 behind, with the same six application/test files and no app-file overlap from those docs. | Draft until physical P0. This is the current GPS source integration candidate. |
| Earlier GPS stationary-drift handoff | #311 — `agent/codex/gps-stationary-speed-accuracy-guard-20261125-r1`; head `5eee7f80543d88420af011e36c4001660e75ee3b` | Exact-head run 45566362328 PASS; current compare 11 ahead / 29 behind; diverged; overlaps #315 GPS service/policy files. | Do not merge separately; preserve CI evidence. #315 ports this source onto the current canonical base and adds Android 14 FGS handling. |
| OSM map/settings fallback | #284 — `agent/codex/gps-open-source-stack-20261109`; head `274155eafdfff381009ef5814a621f32b225f1a8` | 13 files; 19 ahead / 179 behind; no exact-head CI. Historical run 42694452852 validates only `3fcbe6ac...`; artifact 13707718861 unavailable. Source-integrity check confirms complete 1,146-line MainActivity and `motionSnapshot()`. | Draft; do not merge wholesale. Overlaps #315 ActivityTrackingService, #93 MainActivity/Manifest and #216/#224 WebView. Extract only map/settings-specific delta after owners release files and validate exact head + physical P0. |
| Health Connect services / permissions | #93 — `agent/codex/health-services/20261025`; head `1cc08cef7dae7f432275fd23960f4390a49db14c` | 12 files; declares 19 scopes vs canonical five; MainActivity/Manifest ownership; behind current canonical base. | Hold; narrow scopes and reconcile privacy/Play Data Safety before integration. |
| Active workout resume | #216 — `agent/codex/active-workout-resume-protection-20261030`; head `1ef915886fdac62c8fe1d5e50505fd354d989ee3` | Five shared WebView files; stacked on #215; no exact-head Actions validation. | Hold; resolve shared-file ownership and run final combined-head tests. |
| Offline active-workout demos | #224 — `agent/codex/active-workout-offline-frame-autoplay-20261031`; head `cc703baa3cc0e1866e50aafb9a8caad26583fc0a` | Four files; source/V8 harness only; stacked on #223; native WebView/device acceptance incomplete. | Hold; run native product suite on final combined SHA and physical offline acceptance. |
| GPS route display smoother | #248 — `agent/codex/activity-gps-route-smoother-20261101-r1`; head `67d3b438815fe83ced301551aee43f5a6548c91d` | Two files; no production call site; diverged from canonical. | Do not merge unused/duplicate smoothing or let it alter metric credit. |
| Timed-program RIR | #213 — `agent/codex/program-timed-rir-semantic-display-20261030`; head `f719214d813f367350d8a10591903d16b68f8da1` | Six files; stacked on a separate exercise/program lane. | Keep separate; exact-source and final integrated tests required. |
| Arabic exercise cue cleanup | #160 — `agent/codex/catalog-arabic-filler-cleanup-batch6-20261028`; head `82e5ca5c2fe796b82cb8d02dbeece3f4b5df125c` | Six files; stacked catalog lane. | Keep separate; exact-source and final integrated tests required. |

## Newly merged / canonical

### PR #314 — Health Connect exercise mapping

- Merged at `779df53146e23e76fe7b1faabffbc0e3540ee29a`.
- Exact source SHA `95f4996d0fefc3017401289d29278dda6740adec`; exact-head workflow 45830026710: Product 84/84, Source 35/35, Backend 29/29, Android 352/352; zero failures/ignored.
- Artifact 15121128134 ZIP SHA-256 `5792eb77f98ec89e165350a6adcedcf4729c49b899e6a992b5f37971fd340e8d`; APK `fbd89742d804a4755fe9b45f2d1df84f23e306a1004292c5bc448f1b68665bec`; unsigned AAB `477f52c66fa404ff294371a1a6e0b5bb9aaa5b5e2826f2f9a5f3c7bb3363bf2a`.
- Only HealthSportMapper and its unit test changed; no manifest/permission expansion, GPS overlap or Play mutation.

Other merged:
- #312 unknown Health exercise types fail closed as `UNSUPPORTED_EXERCISE_TYPE`.
- #310 non-transitive Health session-window quarantine.
- #269 competition backend, still provisional `strength_volume_kg_reps`; no independently verified GPS leaderboard, GPS reward eligibility false, no THF payouts.
- #307 is closed, not merged, superseded by later GPS work.

## Live Google Play state — 2026-11-27

- Probe [45872277536, attempt 2](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45872277536) SUCCESS at 2026-11-27T17:51:42Z.
- Artifact 15222725086 ZIP SHA-256 `79b0718acfbf63d60324011832c11ac69b578c4894203d621998b86efb3577ef`; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`; both independently rehashed.
- Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified.
- `uploadAttempted=false`; `commitAttempted=false`; no listing/track/version mutation. The probe creates and deletes a temporary empty edit only to read the current API state.
- Arabic and English listings present; support email `TopHeroFit@gmail.com`.

## Release, privacy and device gates

- Last Internal versionCode: 51019. Next 51020 remains UNALLOCATED.
- Owner Play/API write permission and GCP Secret Manager signing-key access: NOT_VERIFIED.
- No new signed AAB. PR #315 CI AAB is unsigned; do not upload it.
- Desktop Commander localhost Offline, last seen about 248 hours before this observation; SM-A217F current app/session state unknown. No ADB or session action performed.
- Physical P0 BLOCKED_NOT_RUN: stationary drift, measured walk/run/cycle routes, permission downgrade/regrant, first-fix latency/accuracy, screen-off/background, persistent notification controls, process-death restore, crash/ANR/Logcat.
- Production remains blocked on physical P0, privacy/policy and release gates.
- Completed route history remains in WebView localStorage; no authenticated route-sync endpoint/table or precise-location upload. Route backup remains design-only pending #284 validation and explicit consent/retention/deletion design.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired. `GpsFixGate` is signal admission and `GpsDistanceAccumulator` the sole metric-credit path.
- No paid infrastructure or unrelated projects.


## Supporting open QA / Health / session-history PRs

These are not release-authority lanes and none has exact-head CI on its current head at this checkpoint:

| PR | Head | Scope / current evidence | Decision |
|---|---|---|---|
| #118 | `1dee6b430ac63a344d1ca5bd2b8fd5901dd84d46` | Two-file physical-QA evidence collector; open, non-Draft, stale base and currently unmergeable; no workflow run on current head. | Preserve as tooling only; rebase and exact-head test before use. No physical P0 is implied by the collector. |
| #119 | `a832ac650acc6bf3606856361a9a3b85bf679834` | Seven-file Play 51018 preflight/blocked-P0 record; open, non-Draft, stale base and unmergeable; no workflow run on current head. Its installed-version observation is superseded by the current 51019 Play readback. | Historical QA evidence only; do not treat as current Play state or release proof. |
| #137 | `551cccdbf74b17001dfcad8ccc94ca340faafd72` | Two-file Health permission-surface guard; open, non-Draft, stale base and unmergeable; no workflow run on current head. | Keep as a candidate guard, but reconcile with #93 and the canonical five-scope Health allowlist before integrating. |
| #227 | `24e1b4ace1d86ea8e02d558ad9db993e4e627c77` | Four-file local-calendar workout-history/streak fix; Draft, stale base and unmergeable; no workflow run on current head. | Keep separate from GPS service work; exact-head product/native tests required before integration. |

The open exercise-experience queue also includes #160 and #213 (catalog/program lanes), #224 (offline demo autoplay), and older accessibility/content PRs. Do not batch-merge stacked branches. Reconcile each against the canonical tree and its actual shared-file owner before testing a combined head.
