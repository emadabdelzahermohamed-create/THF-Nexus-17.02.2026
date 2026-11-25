# TopHeroFit — Current Integrator Leases

**Observed:** 2026-11-25 17:51:58 UTC  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application base:** `85fb3e96f90ca5f7a9eac9072d8301d7f31d55bb`  
**Read-only Play probe trigger commit:** `43007c52b858e67fb42615da7c788c354b792620`

## Exclusive canonical ownership

Only the canonical integrator writes:
- release/version allocation and `RELEASE_CURRENT.json`;
- GitHub Actions release/publication workflows;
- signing and Google Play upload/commit/promotion;
- canonical recovery, GPS-quality and lease checkpoints.

No handoff PR may allocate versionCode, sign, upload, commit a Play release or promote a track.

## Active priority leases

| Lane | PR / branch | Current evidence | Decision |
|---|---|---|---|
| GPS source arbitration / stationary drift | #311 — `agent/codex/gps-stationary-speed-accuracy-guard-20261125-r1`; head `5eee7f80543d88420af011e36c4001660e75ee3b`; tested app SHA `6dc578979bf940bfc0c2010ebe4f197557c1ea6b` | Run 45565394285 PASS: 84 Product / 40 Source / 29 Backend / 355 Android; artifact 14999992451 ZIP `238de38fb8c33b09ffce2e857c960e8df55bf017c5fca417dd710472498c538a`; unsigned AAB `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`. Current compare 11 ahead / 11 behind; the behind side is disjoint Health #312 plus read-only workflow/ReleaseOps changes. The two branch-local checkpoint files duplicate canonical ReleaseOps paths and must be dropped before any eventual merge. | Draft; physical P0 required. No merge, signing or Play write yet. |
| GPS map/settings watchdog | #284 — `agent/codex/gps-open-source-stack-20261109`; head `274155eafdfff381009ef5814a621f32b225f1a8` | 19 ahead / 161 behind; 13 files. Run 42694452852 validates only historical SHA `3fcbe6ac...`; no current-head CI. | Draft; do not merge wholesale. Overlaps #311, #93, #216 and #224. |
| Health Connect services / permissions | #93 — `agent/codex/health-services/20261025`; head `1cc08cef7dae7f432275fd23960f4390a49db14c` | Draft; 12 files; declares 19 scopes vs canonical five; MainActivity/Manifest ownership. | Hold until narrowed to approved scopes and privacy/Play declarations reconcile. |
| Active workout resume | #216 — `agent/codex/active-workout-resume-protection-20261030`; head `1ef915886fdac62c8fe1d5e50505fd354d989ee3` | Draft; five shared WebView files; no exact-head GitHub Actions run. | Hold; resolve shared UI ownership and run exact combined-head tests. |
| Active workout offline demos | #224 — `agent/codex/active-workout-offline-frame-autoplay-20261031`; head `cc703baa3cc0e1866e50aafb9a8caad26583fc0a` | Draft; source-level V8 harness only; native Node/WebView/device acceptance not complete. | Hold; stack after parent chain and run native product suite on final combined SHA. |
| GPS route display smoother | #248 — `agent/codex/activity-gps-route-smoother-20261101-r1` | Draft; no production call site. | Do not merge unused/duplicate smoothing or alter metric credit. |

## Superseded / merged lanes

- #307 is closed (not merged), superseded by #311.
- #312 merged at `85fb3e96...`; exact source SHA `3f303539...`, run 45626405480: Product 84/84, Source 35/35, Backend 29/29, Android 346/346, zero failures/ignored; artifact 15028895816 ZIP `f4ee13861128e192a4d08719e7f157a1e579451d92bfcb65e6106a3e52a834d7`; unknown exercise types fail closed as `UNSUPPORTED_EXERCISE_TYPE`.
- #310 Health non-transitive session-window quarantine remains merged at `fad03f360c1d9a474b62239025ff76fde7eeb087`.
- #309 Health reconciliation and #303 Activity Engine/GPS base remain merged.
- #302 GPS status/pause presentation remains canonical.
- #269 competition backend remains provisional `strength_volume_kg_reps`; no verified GPS leaderboard, GPS reward eligibility false, no THF payouts.

## Shared-file ownership rules

- `ActivityTrackingService.kt` and GPS policy: #311 owns the active GPS handoff; #284 is stale/overlapping.
- `MainActivity.kt` and Manifest: #93 owns Health/native bridge; keep its 19-vs-5 scope blocker.
- `app.js`, `index.html`, styles and motion assets: #216/#224 and related exercise handoffs are stacked/shared. Do not merge a whole branch from stale parent history.
- #284's `openLocationSettings()` bridge is not canonical. Extract only after MainActivity/WebView owners release the shared files, then run exact-head CI and physical P0.

## Release, privacy and device gates

- Latest read-only Google Play probe [45669171108](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45669171108) confirms Internal 51019 Completed; Alpha 51007 Draft; Production not listed. Artifact 15049525912 ZIP SHA `b0145bf9d7016f739da8528c6a538ccd9df3ad352208e68b89aa26045d3bb86a`; embedded JSON SHA `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`. No upload/commit.
- Owner Play/API write permission and GCP Secret Manager signing-key access remain NOT_VERIFIED.
- VersionCode 51020 remains UNALLOCATED; no new signed AAB.
- Desktop Commander localhost Offline; Samsung SM-A217F app/session state unknown. No ADB or device mutation. Physical P0 BLOCKED_NOT_RUN.
- Route sync remains design-only; completed GPS routes are local in `pulse.v2.activities`; no authenticated route endpoint/table or precise-location upload.
- Anti-cheat `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired; `GpsFixGate` is admission and `GpsDistanceAccumulator` is the sole metric-credit path.
- No paid infrastructure or unrelated projects.
