# TopHeroFit — GPS / Map Quality Checkpoint

**Observed:** 2026-11-25 17:51:58 UTC  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application base:** `85fb3e96f90ca5f7a9eac9072d8301d7f31d55bb`  
**GPS PR:** #311 — `5eee7f80543d88420af011e36c4001660e75ee3b` (current branch head; docs-only after tested app SHA)

## Exact tested GPS PR head

- Current PR head / exact tested source SHA: `5eee7f80543d88420af011e36c4001660e75ee3b`.
- Workflow [45566362328](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45566362328): SUCCESS on that exact PR head.
- Product 84/84; Source Contract 40/40; Backend 29/29; Android Unit 355/355; zero failures/ignored.
- Android API 36, Kotlin/Gradle, lint, assembleDebug and bundleRelease validation PASS. Lint 0 errors, 13 warnings, 1 hint.
- Artifact 14999518977, 63,102,392 bytes. ZIP SHA-256 `01d30c100dece05428d6f3bb78b61468ebf8281c031f675e243d56d2e0bf50b0`; independently rehashed and matches GitHub digest.
- Embedded source marker: `5eee7f80543d88420af011e36c4001660e75ee3b`.
- QA APK SHA-256: `154b76c9601db115a4b8484af8f051cce017abd10b5edf7a0e9b5e9e133ea301`.
- Validation AAB SHA-256: `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`; `jarsigner` reports unsigned.
- The AAB is byte-identical to the earlier corrected application build 45565394285; no signing, version allocation or Play upload occurred.
- QA package `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. Not a release artifact.

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
- Compared with canonical tip `ffb518f2fd4ef57399d0d1c96df707e857cc3199` before this docs-only checkpoint, the PR is 11 ahead / 13 behind. Behind changes are disjoint Health #312 and ReleaseOps/read-only probe updates; no GPS source/test overlap. The PR's two branch-local checkpoint files duplicate canonical ReleaseOps paths and must be dropped before any eventual merge.
- #311 remains Draft/unmerged until physical P0; no rebase/rebuild solely for disjoint docs/Health drift.
- #307 is closed, not merged, superseded by #311.
- #284 remains Draft: 13 files, no exact-head CI; it overlaps #311, #93, #216 and #224.

## Physical P0 — BLOCKED_NOT_RUN

Desktop Commander localhost is Offline; Samsung SM-A217F current app/session state is unknown. No ADB/device mutation was attempted.

Required: stationary 60-second drift; measured walking/running/cycling routes; precise/approximate and revoke/regrant; first-fix latency/accuracy; in-app navigation and screen-off/background; persistent notification Pause/Resume/Finish; process-death restore without crediting stopped time; crash/ANR/Logcat.

No GPS accuracy or phone QA PASS is claimed from CI alone.

## Separate route-sync gap

Finished route history remains local in WebView storage. No authenticated route-sync endpoint/table or precise-location upload exists. After #284 is validated, inspect account/backend contracts and design explicit opt-in, consent, retention/deletion and no precise-location upload by default. The 1-second local map refresh is not cloud sync.


## Integrator recheck — 2026-11-25 20:11 Africa/Cairo

### Latest GPS handoff: PR #311

- Exact PR head: `5eee7f80543d88420af011e36c4001660e75ee3b`; exact-head workflow [45566362328](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45566362328) succeeded with Product 84/84, Source Contract 40/40, Backend 29/29 and Android Unit 355/355; zero failures/ignored; API 36/Kotlin/Gradle, lint and unsigned QA APK/AAB validation PASS.
- Artifact 14999518977 was downloaded and independently rehashed again: ZIP `01d30c100dece05428d6f3bb78b61468ebf8281c031f675e243d56d2e0bf50b0`, APK `154b76c9601db115a4b8484af8f051cce017abd10b5edf7a0e9b5e9e133ea301`, AAB `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`. Embedded source marker matches `5eee7f80543d88420af011e36c4001660e75ee3b`; AAB is unsigned and QA-only at versionCode 51019. No rebuild/signing/Play upload.
- GPS logic: strict monotonic cross-provider arbitration; Fused batches sorted and checked against a rolling accepted anchor; optional API 26+ speed accuracy; stationary re-anchor only after two fresh same-source observations spanning at least 3 seconds with `speed + speedAccuracy <= 0.35 m/s`; one low-speed fix is provisional and missing speed accuracy is not stationary proof. Consecutive-fix gap is 30 seconds; anchor lifetime 120 seconds. `GpsFixGate` admits fixes and `GpsDistanceAccumulator` alone credits distance.
- Current compare is 11 ahead / 14 behind. Canonical-side changes since merge base are disjoint Health #312 and ReleaseOps/read-only-probe files; PR-local copies of the canonical recovery/GPS docs are duplicates. Keep Draft until physical P0 and remove duplicate docs before any future exact-head rebase/CI.

### PR #284 — stale GPS/map watchdog

- Current head `274155eafdfff381009ef5814a621f32b225f1a8`, 19 ahead / 164 behind, 13 changed files.
- No workflow run exists for the current head. Run 42694452852 passed only on historical SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; historical artifact 13707718861 is no longer retrievable (404).
- Shared ownership overlaps #311 GPS service/policies, #93 MainActivity/Manifest, and #216/#224 WebView files. Keep Draft; do not merge wholesale or extract settings bridge before owners release files and exact-head CI + physical P0.

### Map and physical boundary

- Leaflet + OSM-derived raster remains canonical; OpenTopoMap and EOX Sentinel-2 are optional. No Google Maps SDK/Rx, billing, key, traffic/transit layer or paid infrastructure.
- Desktop Commander localhost OFFLINE; SM-A217F state UNKNOWN. No ADB/device mutation. Physical GPS/background/session P0 remains BLOCKED_NOT_RUN.
- Finished GPS routes remain local WebView storage. No authenticated route-sync endpoint/table or precise-location upload. Route backup/sync remains deferred until #284 is validated and explicit opt-in/retention/deletion contracts are inspected.
