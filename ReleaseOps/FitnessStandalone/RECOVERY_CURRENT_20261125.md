# TopHeroFit — Canonical Recovery Checkpoint

**Observed:** 2026-11-25 17:51:58 UTC  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application base:** `85fb3e96f90ca5f7a9eac9072d8301d7f31d55bb`  
**Canonical ReleaseOps parent before this reconciliation:** `29ceacb0200bb1da26d7efe5535fa4cfa74b8a29`  
**Read-only Play probe trigger commit:** `43007c52b858e67fb42615da7c788c354b792620` (workflow-comment-only; no app source changed)

## Source of truth and startup

- This repository and branch are the only TopHeroFit source of truth.
- `RELEASE_CURRENT.json` is the canonical release pointer; only the canonical integrator may change release/version/workflow/signing/Play state.
- Latest GPS report is `GPS_MAP_QUALITY_20261125.md`.
- Current leases are `INTEGRATOR_LEASES_CURRENT_20261125.md`.
- No other project is in scope.

## Canonical Health update — PR #312

- PR #312 merged at canonical commit `85fb3e96f90ca5f7a9eac9072d8301d7f31d55bb`.
- Exact source SHA: `3f30353939806f50ebd7f5c45c30f4367fbd3426`.
- Exact-head workflow [45626405480](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45626405480): Product 84/84, Source Contract 35/35, Backend 29/29, Android Unit 346/346; zero failures/ignored; API 36, Kotlin/Gradle, lint, debug APK and unsigned AAB validation PASS.
- Artifact 15028895816 ZIP SHA-256: `f4ee13861128e192a4d08719e7f157a1e579451d92bfcb65e6106a3e52a834d7`; independently downloaded and rehashed.
- Embedded source marker: `3f30353939806f50ebd7f5c45c30f4367fbd3426`.
- QA APK SHA-256: `3bad782dd24cf1733dfbe04b8122f04bc2bea1cbc4660ce49a8600bb8892428a`.
- Validation AAB SHA-256: `2eb1a027e40b410c972c69b328d4b07f3942b8c9f12c167460f4e4b544d29091`; `jarsigner` confirms unsigned.
- Unknown Health Connect exercise types now fail closed as `UNSUPPORTED_EXERCISE_TYPE`; explicit `OTHER_WORKOUT` remains supported. Four Health-owned files only; no manifest/permission expansion. Physical Health/wearable acceptance remains unverified.

## GPS handoff — PR #311

- PR: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/311
- Branch: `agent/codex/gps-stationary-speed-accuracy-guard-20261125-r1`
- Current PR branch head: `5eee7f80543d88420af011e36c4001660e75ee3b`.
- The current PR head itself passed exact-head workflow [45566362328](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45566362328): Product 84/84, Source Contract 40/40, Backend 29/29, Android Unit 355/355; zero failures/ignored; Android API 36/Kotlin/Gradle, lint, APK and unsigned AAB validation PASS. Lint: 0 errors, 13 warnings, 1 hint.
- Artifact 14999518977, 63,102,392 bytes, downloaded and independently rehashed. ZIP SHA-256 `01d30c100dece05428d6f3bb78b61468ebf8281c031f675e243d56d2e0bf50b0`, matching GitHub digest. Embedded source marker is exactly `5eee7f80543d88420af011e36c4001660e75ee3b`. QA APK SHA-256 `154b76c9601db115a4b8484af8f051cce017abd10b5edf7a0e9b5e9e133ea301`. Validation AAB SHA-256 `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`; `jarsigner` confirms unsigned.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, `5.0.0-v2-alpha19-debug`. The AAB bytes are identical to the previous corrected application run 45565394285; no signed release candidate or Play upload exists.
- The current PR head is two documentation-only commits after application SHA `6dc578979bf940bfc0c2010ebe4f197557c1ea6b`; the current-head workflow above covers the exact PR head.
- Compared with canonical tip `ffb518f2fd4ef57399d0d1c96df707e857cc3199` before this docs-only checkpoint, PR #311 was 11 ahead / 13 behind. Behind changes are disjoint Health #312 and ReleaseOps/read-only probe updates; no GPS source/test overlap.
- Canonical `RECOVERY_CURRENT_20261125.md` and `GPS_MAP_QUALITY_20261125.md` now occupy the same paths as the PR's branch-local checkpoint files. Drop those two duplicate PR docs before any eventual merge.
- PR #311 remains Draft/unmerged because physical P0 is mandatory. Do not rebase/rebuild unchanged app bytes solely for docs/Health drift.

### GPS implementation boundary

- Provider arbitration requires monotonic elapsed-realtime order; older/equal Fused fixes cannot displace a newer framework fix.
- Fused recovery batches are sorted and validated against a rolling accepted anchor and a conservative cross-provider displacement/sport-speed envelope.
- Optional Android speed-accuracy evidence is captured only on API 26+ when present.
- Stationary re-anchoring requires two fresh same-source low-speed observations at least 3 seconds apart with combined speed upper bound <=0.35 m/s. A single low-speed fix is provisional. Missing speed accuracy does not imply stationary.
- Consecutive-fix gap is capped at 30 seconds; stable movement-anchor lifetime remains 120 seconds. A 31-second gap re-anchors rather than bridging an unobserved 100 m jump; the next measured 30 m / 15 s segment is credited. A 45-second slow-movement regression preserves 9 m.
- `GpsFixGate` remains signal admission; `GpsDistanceAccumulator` remains the sole metric-credit path. Display smoothing must not alter distance, pace, speed or rewards.

## Superseded and overlapping GPS handoffs

### PR #307

- Closed, not merged, on 2026-11-25 as superseded by #311.
- Its tested source SHA `46241bd8286b2b1d3489aef3a46432eea702a054` and workflow 45340645909 remain historical evidence only; the GPS source changes were carried forward into #311.

### PR #284

- Open Draft; head `274155eafdfff381009ef5814a621f32b225f1a8`.
- PR #284 remains 13 changed files and has no exact-head CI; its only successful run is historical on SHA `3fcbe6ac...`.
- Historical run 42694452852 validates only old SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; no exact-head CI exists for the current PR head.
- Overlaps #311 (`ActivityTrackingService.kt` / GPS policy), #93 (`MainActivity.kt` / Manifest), and #216/#224 (`app.js` / `index.html`). Keep Draft; do not merge wholesale. Any map-only extraction must be isolated after owner release, exact-head CI and physical P0.

## Current ownership and other priorities

- #93 Health services remains Draft; its declared 19 scopes exceed the canonical five-scope allowlist. Keep blocked until narrowed and privacy/Play declarations reconcile.
- #216 active-workout resume remains Draft across shared WebView files; no exact-head Actions validation.
- #224 offline active-workout demo autoplay remains Draft; exact-source harness is not native Node/WebView/device acceptance.
- #248 route-display smoother remains Draft and has no production call site; do not allow display smoothing to affect metrics.
- #269 competition backend is merged but provisional `strength_volume_kg_reps` only. No independently verified GPS leaderboard; GPS `rewardEligible=false`; no THF payout authorized.
- #310 Health non-transitive session-window quarantine remains merged; #312 adds fail-closed unknown-type handling.

## Maps and route sync

- Canonical map remains Leaflet in Android WebView with OpenStreetMap-derived raster layers; OpenTopoMap and EOX Sentinel-2 are optional.
- No Google Maps SDK/Rx, Google basemap, traffic/transit layer, billing enablement or new Maps key is evidenced or required for this OSM stack.
- Completed GPS route history remains in WebView localStorage. No authenticated route-sync endpoint/table or precise-location upload exists.
- Route backup/sync remains a separate design-only gap. After #284 is validated, inspect account/backend contracts and design explicit opt-in consent, retention and deletion semantics; no precise-location upload by default. One-second local map refresh is not route sync.

## Live Google Play readback — 2026-11-25

- Read-only probe [45669171108](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45669171108) completed SUCCESS; probe job 139399438915 succeeded.
- Artifact 15049525912 ZIP SHA-256 `b0145bf9d7016f739da8528c6a538ccd9df3ad352208e68b89aa26045d3bb86a`; independently downloaded and rehashed.
- Embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.
- Internal 51019: Completed. Alpha 51007: Draft. Production: not listed / not verified.
- Listing and support contact unchanged; support email `TopHeroFit@gmail.com`.
- `uploadAttempted=false`, `commitAttempted=false`. Probe used a temporary empty edit session and deleted it; no listing, track, version, upload or commit mutation.
- Store copy continues to describe GPS/background sessions and labels calories/derived metrics as estimates. Do not claim physical GPS/background QA from listing text.

## Phone and release gates

- Latest Desktop Commander device-list result: localhost OFFLINE (last seen about 200 hours earlier); Samsung SM-A217F current app/session state UNKNOWN.
- No ADB, install, launch, force-stop, notification, permission or location-setting action was performed.
- Physical P0 remains BLOCKED_NOT_RUN: stationary drift; measured walk/run/cycle routes; permission downgrade/revoke/regrant; first-fix latency/accuracy; background/screen-off; notification Pause/Resume/Finish; process-death restore; crash/ANR/logcat.
- Owner Google Play/API write permission and GCP Secret Manager signing-key access remain NOT_VERIFIED.
- Next versionCode 51020 remains UNALLOCATED. No new signed AAB. Production remains blocked on physical P0, policy/privacy and release gates.
- No paid infrastructure, no unrelated projects, no Play write.


## Canonical integrator recheck — 2026-11-25 20:11 Africa/Cairo

- Starting canonical branch tip: `6b8117d4d0d859c2586217418b2d172ed81fa350` (`docs(releaseops): record exact PR 311 head CI evidence`). Canonical application base remains `85fb3e96f90ca5f7a9eac9072d8301d7f31d55bb`; no application source or release configuration was changed in this recheck.
- PR #311 exact current head `5eee7f80543d88420af011e36c4001660e75ee3b` has successful exact-head workflow [45566362328](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45566362328): Product 84/84, Source Contract 40/40, Backend 29/29, Android Unit 355/355; zero failures/ignored; Android API 36, Kotlin/Gradle, lint and APK/unsigned-AAB validation PASS (0 lint errors, 13 warnings, 1 hint).
- Artifact 14999518977 was downloaded again and independently rehashed during this recheck: ZIP SHA-256 `01d30c100dece05428d6f3bb78b61468ebf8281c031f675e243d56d2e0bf50b0`; QA APK `154b76c9601db115a4b8484af8f051cce017abd10b5edf7a0e9b5e9e133ea301`; validation AAB `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`. Embedded `SOURCE_SHA` is exactly `5eee7f80543d88420af011e36c4001660e75ee3b`; `jarsigner` confirms the AAB is unsigned. This is QA-only package `com.topherofit.thf.pulse.qa`, versionCode 51019; no new build was produced.
- Current compare: #311 is 11 ahead / 14 behind canonical tip. The 14 canonical-side commits since its merge base are disjoint Health #312 and ReleaseOps/read-only-probe changes; no GPS source/test overlap. The PR's two branch-local recovery/GPS documents duplicate canonical paths and must be dropped before any eventual integration. Keep Draft/unmerged until physical P0.
- PR #284 current head is `274155eafdfff381009ef5814a621f32b225f1a8`, 19 ahead / 164 behind canonical, 13 files. No PR-triggered workflow run exists for that current SHA. Historical run 42694452852 succeeded only on `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; its artifact listing is empty and direct retrieval of historical artifact 13707718861 returns 404. Keep Draft; no current-head CI or physical P0 evidence.
- Latest live read-only Play readback remains run [45669171108](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45669171108), completed 2026-11-25 17:51:58 UTC. Artifact 15049525912 was downloaded and rehashed: ZIP `b0145bf9d7016f739da8528c6a538ccd9df3ad352208e68b89aa26045d3bb86a`; embedded JSON `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`. Readback: Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified; `uploadAttempted=false`, `commitAttempted=false`; support email TopHeroFit@gmail.com. No Play write occurred.
- Desktop Commander localhost remains OFFLINE (last seen about 200 hours before this recheck); SM-A217F current app/session state remains UNKNOWN. No ADB or phone/session action was attempted. Physical P0 remains BLOCKED_NOT_RUN.
- VersionCode 51020 remains UNALLOCATED. Owner Play/API write permission and GCP Secret Manager signing-key access remain NOT_VERIFIED. No signed AAB, Play upload, track mutation, or production action.
