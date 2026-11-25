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
- Observed at checkpoint: changed-app job SUCCESS; Product, source-contract and backend regression step SUCCESS; Android API 36 install SUCCESS; lint/build candidate step still IN_PROGRESS.
- No Android unit/build PASS, artifact digest, signing or Play PASS is claimed until the run reports completion.

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

1. Read workflow 45562000301 to completion on exact application SHA `de8dd0c2f1df12f5647fa04eec6cb20605d4fe99`; fix only a newly observed failure, never rerun identical successful gates.
2. After exact-head Android CI passes, update PR #311 with test counts and artifact evidence; keep it Draft until physical P0.
3. Once #311 is proven, close PR #307 as superseded with a cross-link; do not force-push either branch.
4. Resume handset QA only after a fresh read-only device connection and confirmation the handset is idle; do not disturb an active user session.
5. Continue Google Maps only after owner permission, billing/project and exact release signing fingerprint are available.
6. Keep VersionCode 51020 unallocated; no signing, Play write or Production action.

