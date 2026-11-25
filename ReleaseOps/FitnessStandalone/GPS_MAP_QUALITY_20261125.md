# TopHeroFit — GPS / Map Quality Checkpoint

**Observed:** 2026-11-25 17:51:58 UTC  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application base:** `85fb3e96f90ca5f7a9eac9072d8301d7f31d55bb`  
**GPS PR:** #311 — `5eee7f80543d88420af011e36c4001660e75ee3b` (current branch head; docs-only after tested app SHA)

## Exact tested GPS application candidate

- Tested application SHA: `6dc578979bf940bfc0c2010ebe4f197557c1ea6b`.
- Workflow [45565394285](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45565394285): SUCCESS.
- Product 84/84; Source Contract 40/40; Backend 29/29; Android Unit 355/355; zero failures/ignored.
- Android API 36, Kotlin/Gradle, lint, assembleDebug and bundleRelease validation PASS. Lint 0 errors, 13 warnings, 1 hint.
- Artifact 14999992451, 63,102,473 bytes. ZIP SHA-256 `238de38fb8c33b09ffce2e857c960e8df55bf017c5fca417dd710472498c538a`; independently rehashed and matches GitHub digest.
- Embedded source marker: `6dc578979bf940bfc0c2010ebe4f197557c1ea6b`.
- QA APK SHA-256: `93116e6cfeeffe3ce29cd0ae29ae0595191919205e0ddf0ca24cbda4ac1992aa`.
- Validation AAB SHA-256: `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`; unsigned by `jarsigner`.
- QA package `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. Not signed, not uploaded.

## GPS behavior under test

### Source arbitration and transition integrity

- Fused fix must be strictly newer than the currently accepted fresh framework fix; stale/equal elapsed-realtime values fail closed.
- Fused batches are sorted by elapsed-realtime and validated against a rolling accepted anchor.
- A candidate is checked against the current provider fix using a conservative displacement/sport-speed envelope. A rejected jump does not advance the anchor.
- Source promotion resets the live distance anchor without crediting the transition itself; cumulative distance and historical route remain.

### Stationary drift

- Android speed accuracy is optional and read only on API 26+ when `hasSpeedAccuracy()` is true.
- Two fresh same-source observations spanning >=3 seconds with `speedMps + speedAccuracyMps <= 0.35 m/s` confirm a stationary window and re-anchor the accumulator.
- A single low-speed observation is provisional; resumed movement is measured from that observation.
- If speed accuracy is absent, the system does not infer stationary state. Coherent GPS-only drift without speed-accuracy evidence remains a physical-QA risk.

### Stale-fix continuity and truthful distance

- Consecutive-fix gap: `MAX_FIX_GAP_MS = 30_000`.
- Stable movement-anchor lifetime: `MAX_ANCHOR_GAP_MS = 120_000`.
- A 31-second inter-fix gap with a 100 m apparent jump re-anchors; only the next measured 30 m / 15 s segment is credited.
- A 45-second slow-movement regression preserves 9 m continuous movement.
- Existing oscillating-path regression remains green.
- `GpsFixGate` is the admission gate; `GpsDistanceAccumulator` is the only distance-credit path. Do not stack the currently unwired anomaly policy as a second per-fix filter.

## Map stack

- Leaflet in Android WebView.
- OpenStreetMap-derived raster base.
- OpenTopoMap and EOX Sentinel-2 optional layers.
- No Google Maps SDK/Rx, billing, API key, traffic/transit layer or paid infrastructure is required for the current stack.
- The historical #284 branch's watchdog/settings bridge is not validated at its current head and must not be merged wholesale.

## Current PR comparison and merge boundary

- #311 current head `5eee7f80543d88420af011e36c4001660e75ee3b`, base `10d9794546e6ecd203bb8078ed458f25a23f056c`.
- Compared with canonical branch head `43007c52b858e67fb42615da7c788c354b792620`: 11 ahead / 3 behind. Three behind commits are disjoint Health and workflow-only changes; GPS files do not overlap.
- #311 remains Draft/unmerged until physical P0; no rebase/rebuild solely for disjoint docs/Health drift.
- #307 is closed, not merged, superseded by #311.
- #284 remains Draft: 19 ahead / 153 behind, 13 files, no exact-head CI; it overlaps #311, #93, #216 and #224.

## Physical P0 — BLOCKED_NOT_RUN

Desktop Commander localhost is Offline; Samsung SM-A217F current app/session state is unknown. No ADB/device mutation was attempted.

Required: stationary 60-second drift; measured walking/running/cycling routes; precise/approximate and revoke/regrant; first-fix latency/accuracy; in-app navigation and screen-off/background; persistent notification Pause/Resume/Finish; process-death restore without crediting stopped time; crash/ANR/Logcat.

No GPS accuracy or phone QA PASS is claimed from CI alone.

## Separate route-sync gap

Finished route history remains local in WebView storage. No authenticated route-sync endpoint/table or precise-location upload exists. After #284 is validated, inspect account/backend contracts and design explicit opt-in, consent, retention/deletion and no precise-location upload by default. The 1-second local map refresh is not cloud sync.
