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

PR #307 remains open and Draft, exact previous tested head `46241bd8286b2b1d3489aef3a46432eea702a054`, prior workflow 45340645909 PASS. It was 3 ahead / 7 behind current canonical. The seven behind commits are canonical ReleaseOps/Health changes; no GPS file overlap. The new PR #311 carries the GPS-owned implementation/tests onto current canonical without force-pushing. Do not close #307 until #311's exact-head Android CI passes; then mark #307 superseded to avoid duplicate open GPS handoffs.

## Blockers

1. Physical P0: authorized device bridge OFFLINE from the prior single check; last known Samsung SM-A217F / Android 12, session state unknown. No retry or device mutation in this run.
2. Google Maps: owner Cloud key-inventory permission and billing/project prerequisite unavailable; exact production package/signing-certificate fingerprint is not established. No Maps key or billing change.
3. Native Google Maps, traffic and transit remain unimplemented; current map stack is Leaflet/OSM-derived raster plus OpenTopoMap/EOX.

## Safe next actions

1. Preserve workflow 45562000301 and artifact 14997818372 as exact-SHA CI evidence; do not rebuild the unchanged application SHA.
2. Keep PR #311 Draft until physical P0; close PR #307 as superseded after confirming #311 contains the same GPS handoff fixes.
3. Once #311 is proven, close PR #307 as superseded with a cross-link; do not force-push either branch.
4. Resume handset QA only after a fresh read-only device connection and confirmation the handset is idle; do not disturb an active user session.
5. Continue Google Maps only after owner permission, billing/project and exact release signing fingerprint are available.
6. Keep VersionCode 51020 unallocated; no signing, Play write or Production action.

