# TopHeroFit — Canonical Recovery Checkpoint

**Observed:** 2026-11-25 08:25 Africa/Cairo  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical HEAD:** `10d9794546e6ecd203bb8078ed458f25a23f056c`  
**Candidate branch:** `agent/codex/gps-stationary-speed-accuracy-guard-20261125-r1`  
**Candidate HEAD at code checkpoint:** `de8dd0c2f1df12f5647fa04eec6cb20605d4fe99`

## Startup / recovery inputs

- Requested `GPS_MAP_QUALITY_20261101.md`: absent (404).
- Newest available report read: `GPS_MAP_QUALITY_20261124.md` (blob `aa36e150f2994e943df1ff0c83ed48ab820347ba`).
- Canonical recovery read: `RECOVERY_CURRENT_20261124.md` (blob `33fc49c673b1663eaf3faa7b8ce13489f595c7e1`).
- `RELEASE_CURRENT.json` read only.
- Root `AGENTS.md` read from main; canonical branch does not contain the referenced AI_SWARM protocol/state files. Fitness execution contract `EXECUTION_20261024.md` and legacy recovery history were read.

## Current work — PR #311

- PR: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/311
- Branch: `agent/codex/gps-stationary-speed-accuracy-guard-20261125-r1`
- Base: canonical branch at `10d9794546e6ecd203bb8078ed458f25a23f056c`.
- App commits:
  - `581458f364bee9f77d00c0ed5d55c2391f2e81d0` — stationary drift guard and tests.
  - `de8dd0c2f1df12f5647fa04eec6cb20605d4fe99` — API wiring and compile correction.
- Eight changed files, all within Activity Engine/GPS implementation and tests.
- No Health/anti-cheat, catalog, release/version/workflow/signing/Play files changed.

### Exact-head workflow

- Run: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45562000301
- Exact tested application SHA: `de8dd0c2f1df12f5647fa04eec6cb20605d4fe99`.
- Workflow 45562000301 completed SUCCESS on exact application SHA `de8dd0c2f1df12f5647fa04eec6cb20605d4fe99`.
- Product 84/84; Source Contract 40/40; Backend 29/29; Android Unit 353/353; zero failures and zero ignored.
- Android API 36, Kotlin/Gradle, lint, Debug APK and unsigned AAB validation PASS; Gradle BUILD SUCCESSFUL in 3m; lint 0 errors, 13 warnings, 1 hint.
- QA package `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`.
- Artifact 14997818372, 63,102,201 bytes; ZIP SHA-256 `b1784658074f503d137fa0a31c49062ada76d411fd21b5074753436911969854`, independently rehashed and matched GitHub digest.
- APK SHA-256 `20a2f7131c65adc37471e62d2d4b89e26f0e21ab57aa52caf9871badaac4b8d7`.
- AAB SHA-256 `d599915e3ea9cfe8ca99c680628438e7bf89baa461e1b40d45b34e9f1c72514f`; `jarsigner` confirms unsigned. No signing or Play action occurred.

## Technical delta

- `GpsFix` now optionally carries `speedAccuracyMps`.
- Android `Location` supplies it only when API 26+ and `hasSpeedAccuracy()` is true.
- Two fresh same-source low-speed observations spanning >=3 seconds and a combined speed upper bound <=0.35 m/s re-anchor the distance accumulator and discard pending stationary drift.
- A single stationary-looking fix is provisional; resumed movement starts from that fix.
- Missing speed accuracy does not trigger stationary classification. Physical validation remains required.

## Previous PR #307

PR #307 is now closed (not merged) as superseded by PR #311 after exact-head workflow 45562000301 passed. Its exact previous tested head was `46241bd8286b2b1d3489aef3a46432eea702a054` (workflow 45340645909 PASS). It had been 3 ahead / 7 behind current canonical; the seven canonical-only commits were ReleaseOps/Health changes with no GPS file overlap. PR #311 carries the six GPS-owned implementation/test changes onto current canonical and adds the stationary-drift guard without force-pushing either branch.

## Blockers

1. Physical P0: authorized device bridge OFFLINE from the prior single check; last known Samsung SM-A217F / Android 12, session state unknown. No retry or device mutation in this run.
2. Google Maps: owner Cloud key-inventory permission and billing/project prerequisite unavailable; exact production package/signing-certificate fingerprint is not established. No Maps key or billing change.
3. Native Google Maps, traffic and transit remain unimplemented; current map stack is Leaflet/OSM-derived raster plus OpenTopoMap/EOX.

## Safe next actions

1. Preserve workflow 45562000301 and artifact 14997818372 as exact-SHA CI evidence; do not rebuild the unchanged application SHA.
2. Keep PR #311 Draft until physical P0; PR #307 is closed as superseded. Do not force-push either branch.
4. Resume handset QA only after a fresh read-only device connection and confirmation the handset is idle; do not disturb an active user session.
5. Continue Google Maps only after owner permission, billing/project and exact release signing fingerprint are available.
6. Keep VersionCode 51020 unallocated; no signing, Play write or Production action.



## 2026-11-25 08:53 Cairo — latest GPS source delta

- Canonical base: `agent/codex/fitness-recovery/20261023` at `10d9794546e6ecd203bb8078ed458f25a23f056c`.
- Corrected source commit: `6dc578979bf940bfc0c2010ebe4f197557c1ea6b`; branch head before this checkpoint is the same SHA. The documentation update after it is docs-only.
- The first attempt incorrectly capped total anchor lifetime at 30 seconds; workflow 45564776923 failed one Android test that protects longer movement accumulation. It was corrected by separating `MAX_FIX_GAP_MS = 30_000L` from `MAX_ANCHOR_GAP_MS = 120_000L`.
- The 31-second stale inter-fix regression excludes a 100 m unobserved jump and credits only the next 30 m / 15 s segment.
- The 45-second slow-movement regression preserves 9 m of continuous movement.
- The source contract verifies the live service resets stale prior location/accuracy, accumulator and current speed before processing the next accepted fix.
- Source/test paths changed: `GpsDistanceAccumulator.kt`, `GpsDistanceAccumulatorTest.kt`, `fitness-v2/tests/test_source_contract.py`. No other ownership lane files changed.

### Exact validation

- Workflow 45564776923 on the superseded first attempt: Product/Source/Backend PASS; 354 Android tests with one failure, `oscillatingAcceptedFixesCannotInflateCreditedPathBeyondNetDisplacementEnvelope`.
- Workflow 45564822387 targets the superseded implementation and does not validate the corrected code.
- Corrected workflow 45565394285 targets exact SHA `6dc578979bf940bfc0c2010ebe4f197557c1ea6b`: Product/Source/Backend and Android API 36 setup passed; Android Unit/Lint/APK/AAB step was in progress at checkpoint capture.
- Previous complete candidate remains SHA `de8dd0c2f1df12f5647fa04eec6cb20605d4fe99`, workflow 45562000301, Android 353/353.

### Current blockers

- Device list read once at 08:53 Cairo: localhost OFFLINE, last seen 189 hours ago. No ADB or device mutation; Physical P0 BLOCKED_NOT_RUN.
- Google Maps remains gated by owner Cloud key-inventory permission, billing/project prerequisite and exact production signing fingerprint. No key/billing action.
- PR #311 remains Draft/unmerged; VersionCode 51020 unallocated; no signing or Play action.
- No Health/anti-cheat or exercise catalog changes; no release/workflow/signing files changed.

### Next action

Check corrected workflow 45565394285 on exact SHA `6dc578979bf940bfc0c2010ebe4f197557c1ea6b`. Keep PR #311 Draft until Physical P0 is complete.


## 2026-11-25 — corrected stale-gap candidate exact-head PASS

- Exact application SHA: `6dc578979bf940bfc0c2010ebe4f197557c1ea6b`.
- Workflow [45565394285](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45565394285): SUCCESS.
- Product 84/84; Source Contract 40/40; Backend 29/29; Android Unit 355/355; zero failures and zero ignored.
- Android API 36, Kotlin/Gradle, lint, assembleDebug and bundleRelease validation PASS. Lint: 0 errors, 13 warnings, 1 hint. Gradle BUILD SUCCESSFUL in 3 minutes.
- Test HTML in the downloaded artifact independently confirms 355/355 and that both `gapBeyondFreshFixWindowReanchorsWithoutBridgingStaleDistance` and `slowContinuousMovementCanAccumulateAcrossFreshFixesBeyondThirtySeconds` passed, alongside `oscillatingAcceptedFixesCannotInflateCreditedPathBeyondNetDisplacementEnvelope`.
- Artifact 14999992451 (63,102,473 bytes): ZIP SHA-256 `238de38fb8c33b09ffce2e857c960e8df55bf017c5fca417dd710472498c538a`, independently rehashed; APK SHA-256 `93116e6cfeeffe3ce29cd0ae29ae0595191919205e0ddf0ca24cbda4ac1992aa`; unsigned AAB SHA-256 `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`. Jarsigner confirms unsigned.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName 5.0.0-v2-alpha19-debug, API 36. No production signing or release version allocation.

### Current PR / blockers

- PR #311 remains Draft/unmerged; corrected application SHA above is CI PASS. The latest branch commit after it is documentation-only.
- The initial 30-second whole-anchor attempt was correctly rejected by the oscillating-path regression in runs 45564776923 and 45564822387; the split 30-second inter-fix / 120-second anchor policy is the tested correction.
- Device bridge remains OFFLINE from the single read-only check (08:53 Cairo, last seen 189 hours earlier); no ADB or device mutation. Physical P0 remains BLOCKED_NOT_RUN.
- Google Maps SDK/key remains owner Cloud permission + project/billing + exact production signing fingerprint gated. No Google Maps integration or billing/key change.
- No Health/anti-cheat, exercise catalog, release/workflow/signing/Play files changed. VersionCode 51020 remains unallocated.
