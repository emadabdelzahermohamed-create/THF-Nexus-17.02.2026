# TopHeroFit — Canonical Recovery Checkpoint

**Observed:** 2026-11-25 17:51:58 UTC  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application base:** `85fb3e96f90ca5f7a9eac9072d8301d7f31d55bb`  
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
- Current PR branch head: `5eee7f80543d88420af011e36c4001660e75ee3b` (documentation-only commit after tested application SHA).
- Base recorded by PR: `10d9794546e6ecd203bb8078ed458f25a23f056c`.
- Corrected exact tested application SHA: `6dc578979bf940bfc0c2010ebe4f197557c1ea6b`.
- Exact-head workflow [45565394285](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45565394285): Product 84/84, Source Contract 40/40, Backend 29/29, Android Unit 355/355; zero failures/ignored; Android API 36/Kotlin/Gradle, lint, APK and unsigned AAB validation PASS. Lint: 0 errors, 13 warnings, 1 hint.
- Artifact 14999992451 was downloaded and independently rehashed. ZIP SHA-256 `238de38fb8c33b09ffce2e857c960e8df55bf017c5fca417dd710472498c538a`, matching GitHub digest. Embedded source marker matches `6dc578...`. QA APK SHA-256 `93116e6cfeeffe3ce29cd0ae29ae0595191919205e0ddf0ca24cbda4ac1992aa`. Validation AAB SHA-256 `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`; unsigned by `jarsigner`.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, `5.0.0-v2-alpha19-debug`. Not a release artifact.
- Current compare against canonical branch head at recheck `43007c52...`: 11 ahead / 3 behind. The three behind commits are disjoint Health #312 and read-only publication-probe workflow changes; no GPS file overlap.
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
- Compare to canonical branch head `43007c52...`: 19 ahead / 153 behind; 13 changed files.
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
