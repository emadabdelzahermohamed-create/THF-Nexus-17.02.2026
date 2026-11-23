# TopHeroFit — Current Integrator Leases

**Observed:** 2026-11-23 20:33 Africa/Cairo  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`
**Raw compare snapshot:** canonical ReleaseOps tip `54d6266c3c8bc469a339a2e1db59734b0ecc8908`, immediately before this documentation refresh.

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
| GPS source arbitration | #307 — `agent/codex/gps-fused-fallback-arbitration-20261122-r1` | `ActivityLocationFallbackPolicy.kt`, `ActivityTrackingService.kt`, focused Kotlin tests and source-contract tests | Draft; current head `923a951a...`, 2 ahead / 0 behind canonical tip `54d6266c...`; exact-head run 45238807995 PASS (83 Product / 39 Source / 29 Backend / 347 Android; zero failures/ignored). Four GPS-only files. Artifact 14851146115 ZIP `d8e716...`, unsigned AAB `833998...`. Strict elapsed-time ordering rejects older/equal Fused fixes and filters stale batch points. Physical P0 still blocks merge. |
| GPS map/settings watchdog | #284 — `agent/codex/gps-open-source-stack-20261109` | `app.js`, `index.html`, `MainActivity.kt`, `ActivityTrackingService.kt`, GPS policies/tests | Draft; current head `274155e...`, 19 ahead / 143 behind canonical tip `54d6266c...`, 13 files. Historical run 42694452852 validates only old SHA `3fcbe6ac...`; no current-head CI. Overlaps #307, #93, #216 and #224. Do not merge wholesale. |
| Health services / permissions | #93 | `MainActivity.kt`, Android Manifest, Health Services bridge | Draft; current handoff declares 19 Health scopes versus canonical five. Hold until narrowed and privacy/Play declarations reconciled. |
| Health permission minimization | #137 — `agent/codex/health-permission-minimization-20261027` | permission-minimization product test and ReleaseOps evidence | No exact-head workflow run; no Play declaration or physical watch/grant/revoke PASS. |
| Active workout resume | #216 — `agent/codex/active-workout-resume-protection-20261030` | active-workout resume state and shared WebView runtime | Draft; no exact-head Actions run; shared app.js/index/styles. |
| Offline active-workout demos | #224 — `agent/codex/active-workout-offline-frame-autoplay-20261031` | offline motion controller and shared WebView runtime/assets | Draft; no exact-head Actions run; stacked/shared app.js/index/motion assets. |
| Timed program semantics | #213 | program/RIR prescriptions and shared catalog assets | Draft; no exact-head Actions run; integrate only after its parent chain and final combined tests. |
| Exercise catalog | #160 | bilingual exercise catalog/build outputs | Draft; no exact-head native CI; shared catalog/build resources. |
| Route display smoother | #248 | standalone display-only smoother helper | Draft; no production call site; do not merge duplicate/unused metric or rendering logic. |

## Merged and closed lanes

- #309 merged at `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af` after exact-head run 45194352739; four-file Health-only diff, no permissions or release changes. Artifact 14828150903 ZIP SHA-256 `9d6938b7fce88e93d59065e10b64ee435420e9d4dc5e311589d750f579305be0` was independently rehashed; validation AAB `9d23056ae9abc9eb90cb8d69ef25717a51d997437109cd637b476eb7f6a180e5` is unsigned.
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

- Latest independently rehashed Play readback (2026-11-22 17:56:05 UTC): Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified. No new 2026-11-23 readback.
- Next versionCode 51020 remains unallocated.
- Owner Play/API write permission and GCP Secret Manager signing-key access are unverified.
- No new signed AAB or Play upload. The latest GPS validation AAB is unsigned QA-only and is not a release candidate.
- Route sync is design-only; no authenticated route endpoint or precise-location upload.
- Anti-cheat policy is tested but unwired; do not stack it as a second distance gate.
- No paid infrastructure or work outside TopHeroFit.
