# TopHeroFit — Current Integrator Leases

**Observed:** 2026-11-23 19:51 Africa/Cairo  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`
**Raw compare snapshot:** canonical branch tip `96266069014b154edb5d08d7677d9349c4530649`, immediately before this lease refresh commit.

## Exclusive canonical ownership

The canonical integrator is the only writer for:
- release/version allocation and `RELEASE_CURRENT.json`;
- GitHub Actions release/publication workflows;
- signing configuration and signed AAB promotion;
- Google Play Internal/Alpha/Production writes and independent readback;
- canonical ReleaseOps recovery/lease records.

No other PR may allocate a versionCode, sign, upload or commit a Play release.

## Active priority leases

The raw ahead/behind values below are snapshots against `962660...` before this lease-refresh commit. The additional behind commits since application head `fe06...` are ReleaseOps checkpoint-only; the application-file diffs listed below remain unchanged. This lease refresh itself is documentation-only.

| Lane | PR / owner | Owned files or scope | Current decision |
|---|---|---|---|
| GPS source arbitration | #307 — `agent/codex/gps-fused-fallback-arbitration-20261122-r1` | `ActivityLocationFallbackPolicy.kt`, `ActivityTrackingService.kt`, focused Kotlin tests and source-contract tests | Draft; exact-head CI passed on 5326bdef; raw compare 9 ahead / 31 behind at 962660. Ten extra behind commits since app head fe06 are ReleaseOps-only. Rebase and rerun CI; physical P0 still blocks merge. |
| GPS map/settings watchdog | #284 — `agent/codex/gps-open-source-stack-20261109` | `app.js`, `index.html`, `MainActivity.kt`, `ActivityTrackingService.kt`, GPS policies/tests | Draft; raw compare 19 ahead / 139 behind at 962660; ten extra behind commits since app head fe06 are ReleaseOps-only. Overlaps #307, #93, #216 and #224. Do not merge wholesale. |
| Health services / permissions | #93 | `MainActivity.kt`, Android Manifest, Health Services bridge | Draft; current handoff declares 19 Health scopes versus canonical five. Hold until narrowed and privacy/Play declarations reconciled. |
| Health permission minimization | #137 — `agent/codex/health-permission-minimization-20261027` | permission-minimization product test and ReleaseOps evidence | No exact-head workflow run; no Play declaration or physical watch/grant/revoke PASS. |
| Active workout resume | #216 — `agent/codex/active-workout-resume-protection-20261030` | active-workout resume state and shared WebView runtime | Draft; no exact-head Actions run; shared app.js/index/styles. |
| Offline active-workout demos | #224 — `agent/codex/active-workout-offline-frame-autoplay-20261031` | offline motion controller and shared WebView runtime/assets | Draft; no exact-head Actions run; stacked/shared app.js/index/motion assets. |
| Timed program semantics | #213 | program/RIR prescriptions and shared catalog assets | Draft; no exact-head Actions run; integrate only after its parent chain and final combined tests. |
| Exercise catalog | #160 | bilingual exercise catalog/build outputs | Draft; no exact-head native CI; shared catalog/build resources. |
| Route display smoother | #248 | standalone display-only smoother helper | Draft; no production call site; do not merge duplicate/unused metric or rendering logic. |

## Merged and closed lanes

- #309 merged at `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af` after exact-head run 45194352739; four-file Health-only diff, no permissions or release changes.
- #303 merged at `b097d6ef0025d615c261ee42e8d2246533224e70` after exact-head CI; canonical Activity Engine/GPS base.
- #308, #305, #304, #302, #301, #282 and #269 are already merged.
- #269 competition backend currently exposes `strength_volume_kg_reps` only. GPS reward eligibility remains false.
- #118/#119 are QA evidence/tooling lanes; current physical P0 remains blocked.
- #127 is an old 51018 release-candidate lane and must not be reused.

## Shared-file lock rules

- `ActivityTrackingService.kt`: #307 owns current arbitration work; #284 is stale/overlapping.
- `MainActivity.kt` and Manifest: #93 owns the Health/native integration lane; #284 must not overwrite them.
- `app.js`, `index.html`, styles and motion assets: #216/#224/#213 and related exercise handoffs are stacked/shared. Do not merge a whole branch based on stale parent history.
- #284's `openLocationSettings()` bridge is not in canonical MainActivity. Extract only after the MainActivity/WebView owner releases the file and the isolated change passes exact-head CI and physical P0.

## Release and privacy gates

- Current Internal: 51019 Completed; Alpha: 51007 Draft; Production not verified.
- Next versionCode 51020 remains unallocated.
- Owner Play/API write permission and GCP Secret Manager signing-key access are unverified.
- No new signed AAB or Play upload.
- Route sync is design-only; no authenticated route endpoint or precise-location upload.
- Anti-cheat policy is tested but unwired; do not stack it as a second distance gate.
- No paid infrastructure or work outside TopHeroFit.
