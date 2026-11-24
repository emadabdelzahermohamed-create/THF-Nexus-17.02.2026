# TopHeroFit — Current Integrator Leases

**Observed:** 2026-11-24 19:38 Africa/Cairo  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `fad03f360c1d9a474b62239025ff76fde7eeb087`  
**ReleaseOps parent before this checkpoint:** `62e7cbf90c6d13656b0035f8fc86b1bf6b8bb683`

## Exclusive canonical ownership

Only the canonical integrator writes:
- release/version allocation and `RELEASE_CURRENT.json`;
- GitHub Actions release/publication workflows;
- signing configuration and signed AAB promotion;
- Google Play Internal/Alpha/Production writes and independent readback;
- canonical ReleaseOps recovery and lease records.

No handoff PR may allocate a versionCode, sign, upload, or commit a Play release.

## Active priority leases

| Lane | PR / branch | Exact current state | Decision |
|---|---|---|---|
| GPS source arbitration | #307 — `agent/codex/gps-fused-fallback-arbitration-20261122-r1` | Head `46241bd8286b2b1d3489aef3a46432eea702a054`; 3 ahead / 6 behind current canonical tip; exact-head run 45340645909 PASS (83 Product / 39 Source / 29 Backend / 349 Android; zero failures/ignored). Artifact 14895973148 ZIP `e7adc8ff91e2d0e338a7c0646111605cba36c32a257ede5bf8554e9ab3007bc9`; unsigned AAB `255dd7e12469fb342b8c7b1cc1cb044c81bb76e60b4e4cdda95dfe9fca1748d8`. Six changed files are GPS-only. | Draft; keep unmerged until physical P0. Do not rebase/rebuild while phone state is unknown. |
| GPS map/settings watchdog | #284 — `agent/codex/gps-open-source-stack-20261109` | Head `274155eafdfff381009ef5814a621f32b225f1a8`; 19 ahead / 149 behind; 13 files. Historical run 42694452852 validates only old SHA `3fcbe6ac...`; no current-head CI. | Draft; do not merge wholesale. Overlaps #307, #93, #216 and #224. |
| Health services / permissions | #93 — `agent/codex/health-services/20261025` | Draft; 12 files; declares 19 Health scopes against canonical five; MainActivity and Manifest ownership. | Hold until narrowed to approved scopes and privacy/Play declarations are reconciled. |
| Active workout resume | #216 — `agent/codex/active-workout-resume-protection-20261030` | Draft; five shared WebView files; no exact-head GitHub Actions run. | Hold; stack/reconcile after shared UI ownership is resolved. |
| Offline active-workout demos | #224 — `agent/codex/active-workout-offline-frame-autoplay-20261031` | Draft; four shared WebView/motion files; native Node/Actions/Android gates not run on final head. | Hold; integrate only after parent chain and exact final-head suite. |
| Timed program semantics | #213 | Draft; shared program/catalog assets; no exact-head Android CI. | Hold. |
| Exercise catalog | #160 | Draft; shared bilingual catalog/build outputs; no exact-head native CI. | Hold. |
| Route display smoother | #248 — `agent/codex/activity-gps-route-smoother-20261101-r1` | Draft; no production call site; two files. | Do not merge unused/duplicate smoothing or alter metric credit. |

## Integrated handoffs

### PR #310 — Health Connect non-transitive session-window quarantine

- Merged at `fad03f360c1d9a474b62239025ff76fde7eeb087`; exact tested PR head `e0cef880cf2d9986b42994bb547ce853f29f2011`; base `20fc6bea72d5d209a160f9b927a06485ac7a6274`.
- Exact-head run 45407977041: Product 84/84, Source Contract 35/35, Backend 29/29, Android Unit 342/342; zero failures/ignored; Android API 36/Kotlin/Gradle, lint, APK and unsigned AAB validation PASS.
- Artifact 14925853882 ZIP SHA-256 `e3787277bdd54e0f33e0275dfb24dafabe14295a315c129e3802dbd80d54d47c`; QA APK `73cfc638bd339b939669de963de683acbcc1e01dd4e9003e23b4fc25e9693a44`; unsigned AAB `1a0a872658b37e890852d924b0fc76afa64cacadc1aff119ba27e346f6de3c1d`.
- All four PR-head file blob SHAs match the canonical merge commit. Post-merge push run 45450665871 skipped deterministic-build; no duplicate build artifact. No Health permission/manifest changes. No physical Health/wearable PASS.

### Existing canonical integrations

- #309 Health reconciliation merged at `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`.
- #303 canonical Activity Engine/GPS base remains merged.
- #269 competition backend remains provisional `strength_volume_kg_reps`; all score/leaderboard responses remain `rewardEligible=false`; no GPS leaderboard or THF payouts.
- #308, #305, #304, #302, #301, #282 are merged.

## Fresh Google Play evidence

- Read-only probe run 45450770929 succeeded on 2026-11-24 17:38:34 UTC; job 138646921676.
- Artifact 14946783770 ZIP SHA-256 `b44459d24cd9e980423dd2dbef59959da21bbd1e99eedf176db9d0a31f010eb2`; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.
- Internal 51019 Completed; Alpha 51007 Draft; Production not listed / NOT_VERIFIED.
- `uploadAttempted=false`, `commitAttempted=false`; listing JSON hash unchanged. Support email remains TopHeroFit@gmail.com.

## Shared-file locks

- `ActivityTrackingService.kt`: #307 owns GPS arbitration; #284 is stale/overlapping.
- `MainActivity.kt` and Manifest: #93 owns Health/native integration; #284 must not overwrite.
- `app.js`, `index.html`, styles and motion assets: #216/#224/#213 and related exercise handoffs are stacked/shared. Do not merge a whole branch from stale parent history.
- #284's `openLocationSettings()` bridge is not in canonical MainActivity. Extract only after owner release, isolated exact-head CI and physical P0.

## Release, privacy and device gates

- Next versionCode 51020 remains **UNALLOCATED**.
- Owner Play/API write permission and GCP Secret Manager signing-key access remain NOT_VERIFIED.
- No new signed AAB, Play upload, listing change or track mutation.
- Samsung SM-A217F current app/session state is UNKNOWN. Desktop Commander localhost OFFLINE, last seen approximately 175 hours before this check. No ADB/install/launch/force-stop/session action was attempted.
- Physical P0 remains BLOCKED_NOT_RUN: stationary drift, measured walk/run/cycle, permission downgrade/revoke/regrant, first-fix latency/accuracy, background/screen-off, notification controls, process-death restore and crash/ANR/logcat.
- Route sync remains design-only: finished GPS routes are local in `pulse.v2.activities`; no authenticated route endpoint/table or precise-location upload. Revisit only after #284 validation and explicit opt-in/retention/deletion contracts.
- Anti-cheat remains tested but unwired; `GpsFixGate` is admission and `GpsDistanceAccumulator` is the sole metric-credit path.
- No paid infrastructure and no work outside TopHeroFit.
