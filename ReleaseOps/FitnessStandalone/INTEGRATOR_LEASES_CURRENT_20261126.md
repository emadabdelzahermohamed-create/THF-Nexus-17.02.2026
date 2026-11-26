# TopHeroFit — Current Integrator Leases

**Observed:** 2026-11-26 17:59:45 UTC  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `779df53146e23e76fe7b1faabffbc0e3540ee29a`  
**Latest read-only Play probe:** 45872277536

## Exclusive canonical ownership

Only the canonical integrator writes:
- release/version allocation and `RELEASE_CURRENT.json`;
- GitHub Actions release/publication workflow logic and triggers;
- signing and Google Play upload/commit/promotion;
- canonical recovery, GPS-quality and lease checkpoints.

No handoff PR may allocate versionCode, sign, upload, commit a Play release or promote a track.

## Active priority leases

| Lane | PR / branch | Current evidence | Decision |
|---|---|---|---|
| GPS source arbitration / stationary drift | #311 — `agent/codex/gps-stationary-speed-accuracy-guard-20261125-r1`; head `5eee7f80543d88420af011e36c4001660e75ee3b` | Exact-head run 45566362328 PASS: 84 Product / 40 Source / 29 Backend / 355 Android; artifact 14999518977 independently hashed; unsigned AAB. Current compare 11 ahead / 19 behind and non-mergeable; two duplicate checkpoint files. | Draft; physical P0 required. Do not merge or rebase/rebuild unchanged bytes yet. |
| GPS map/settings watchdog | #284 — `agent/codex/gps-open-source-stack-20261109`; head `274155eafdfff381009ef5814a621f32b225f1a8` | 13 files; 19 ahead / 169 behind; no exact-head CI. Historical 42694452852 validates only `3fcbe6ac...`; artifact unavailable. | Draft; do not merge wholesale. Overlaps #311, #93, #216 and #224. |
| Health Connect services / permissions | #93 — `agent/codex/health-services/20261025`; head `1cc08cef7dae7f432275fd23960f4390a49db14c` | 12 files; declares 19 scopes vs canonical five; MainActivity/Manifest ownership; non-mergeable. | Hold until narrowed and privacy/Play declarations reconcile. |
| Active workout resume | #216 — `agent/codex/active-workout-resume-protection-20261030`; head `1ef915886fdac62c8fe1d5e50505fd354d989ee3` | Five shared WebView files; stacked on #215; no exact-head Actions validation. | Hold; resolve ownership and run final combined-head tests. |
| Offline active-workout demos | #224 — `agent/codex/active-workout-offline-frame-autoplay-20261031`; head `cc703baa3cc0e1866e50aafb9a8caad26583fc0a` | Four files; source/V8 compatibility harness only; stacked on #223; native WebView/device acceptance incomplete. | Hold; run native product suite on final combined SHA. |
| GPS route display smoother | #248 — `agent/codex/activity-gps-route-smoother-20261101-r1`; head `67d3b438815fe83ced301551aee43f5a6548c91d` | Two files; no production call site; diverged from canonical. | Do not merge unused/duplicate smoothing or change metric credit. |
| Timed program RIR / exercise content | #213, #160 and other catalog handoffs | Separate exercise/catalog lane; not release/GPS ownership. | Keep separate; require exact-source tests before integration. |

## Newly integrated handoff

### PR #314 — Health Connect sport mapping

- Merged 2026-11-26 at `779df53146e23e76fe7b1faabffbc0e3540ee29a`.
- Exact source SHA `95f4996d0fefc3017401289d29278dda6740adec`; exact-head workflow 45830026710: Product 84/84, Source 35/35, Backend 29/29, Android 352/352; zero failures/ignored; lint 0 errors, 12 warnings, 1 hint.
- Artifact 15121128134 ZIP SHA-256 `5792eb77f98ec89e165350a6adcedcf4729c49b899e6a992b5f37971fd340e8d`; APK `fbd89742d804a4755fe9b45f2d1df84f23e306a1004292c5bc448f1b68665bec`; unsigned AAB `477f52c66fa404ff294371a1a6e0b5bb9aaa5b5e2826f2f9a5f3c7bb3363bf2a`.
- Only HealthSportMapper and its unit test changed. No permission or manifest expansion, no GPS overlap, no release/version/signing/Play mutation.
- Post-merge file blobs exactly match the tested PR-head blobs.

## Merged / superseded lanes

- #312 merged at `85fb3e96f90ca5f7a9eac9072d8301d7f31d55bb`; unknown Health Connect exercise types fail closed as `UNSUPPORTED_EXERCISE_TYPE`.
- #310 Health non-transitive session-window quarantine merged at `fad03f360c1d9a474b62239025ff76fde7eeb087`.
- #307 closed, not merged, superseded by #311.
- #269 competition backend merged but provisional `strength_volume_kg_reps` only; no verified GPS leaderboard, GPS `rewardEligible=false`, no THF payouts.

## Shared-file ownership rules

- `ActivityTrackingService.kt` and GPS policy: #311 owns the active GPS handoff; #284 is stale/overlapping.
- `MainActivity.kt` and Manifest: #93 owns Health/native bridge; retain the 19-vs-5 scope blocker.
- `app.js`, `index.html`, styles and motion assets: #216/#224 and related exercise handoffs are stacked/shared.
- #284's `openLocationSettings()` bridge is not canonical. Extract only after native/WebView owners release the shared files, then run exact-head CI and physical P0.

## Release, privacy and device gates

- Latest live read-only Play probe [45872277536](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45872277536): Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified. Artifact 15142793403 ZIP SHA `7e51b333a5da1a8ad6390c4722bf1c49316e19b706e46975c5b283956a1b6e5d`; embedded JSON SHA `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`. No upload/commit.
- Owner Play/API write permission and GCP Secret Manager signing-key access remain NOT_VERIFIED.
- VersionCode 51020 remains UNALLOCATED; no new signed AAB.
- Desktop Commander localhost Offline; Samsung SM-A217F app/session state unknown. Physical P0 BLOCKED_NOT_RUN.
- Route sync remains design-only/localStorage; no authenticated route endpoint/table or precise-location upload.
- Anti-cheat `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired; `GpsFixGate` is admission and `GpsDistanceAccumulator` the sole metric-credit path.
- No paid infrastructure or unrelated projects.
