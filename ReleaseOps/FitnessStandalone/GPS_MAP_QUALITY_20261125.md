# TopHeroFit — GPS / Map Quality Checkpoint

**Observed:** 2026-11-25 08:25 Africa/Cairo  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical base SHA:** `10d9794546e6ecd203bb8078ed458f25a23f056c`  
**Candidate branch:** `agent/codex/gps-stationary-speed-accuracy-guard-20261125-r1`  
**Candidate application SHA:** `de8dd0c2f1df12f5647fa04eec6cb20605d4fe99`

## Starting evidence

- The requested path `ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261101.md` is absent (GitHub Contents API 404 on the default branch and canonical recovery branch).
- Newest available canonical GPS report: `GPS_MAP_QUALITY_20261124.md`, blob `aa36e150f2994e943df1ff0c83ed48ab820347ba`.
- Canonical recovery input: `RECOVERY_CURRENT_20261124.md`, blob `33fc49c673b1663eaf3faa7b8ce13489f595c7e1`.
- Canonical pointer `RELEASE_CURRENT.json` was read only.
- Repository root `AGENTS.md` on main requires the fitness canonical branch and worker-PR boundary. The referenced `ReleaseOps/AI_SWARM/PROTOCOL.md` and `STATE.json` are absent on the canonical branch (404); the live Fitness execution contract and current recovery checkpoint were read.

## Material GPS delta

The existing `GpsDistanceAccumulator` already used reported horizontal accuracy, a three-fix/six-second confirmation window, a 1.4x path-to-net cap and spike-return rejection. Its own source comment explicitly acknowledged that prolonged coherent stationary drift could still be credited.

This candidate adds provider-confirmed stationary re-anchoring:

- Android `Location` speed accuracy is captured only on API 26+ when `hasSpeedAccuracy()` is true. Older devices and providers that omit speed accuracy leave the optional field null.
- Two same-source, fresh observations spanning at least 3 seconds whose `speedMps + speedAccuracyMps <= 0.35 m/s` confirm a stationary window and re-anchor the accumulator, clearing pending path/displacement evidence.
- A single low-speed observation is provisional. If movement resumes before confirmation, the accumulator re-anchors at that observation and measures the resumed segment.
- When speed accuracy is unavailable, the filter does not infer that the user is stationary; coherent GPS-only drift remains a physical-QA risk.

### Regression coverage added

- Repeated confident stationary fixes with drifting coordinates do not earn distance.
- One stationary-looking observation followed by resumed movement does not permanently suppress movement.
- Low reported speed without speed-accuracy evidence does not trigger stationary classification.
- Python source contract checks the API-level guard and accumulator wiring.

## Exact source / CI evidence

- Initial implementation commit: `581458f364bee9f77d00c0ed5d55c2391f2e81d0`.
- Corrective compile/API-wiring commit: `de8dd0c2f1df12f5647fa04eec6cb20605d4fe99`.
- Exact candidate workflow: [45562000301](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45562000301).
- Workflow [45562000301](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45562000301) completed **SUCCESS** on exact application SHA `de8dd0c2f1df12f5647fa04eec6cb20605d4fe99`.
- Product 84/84; Source Contract 40/40; Backend 29/29; Android Unit 353/353; failures 0; ignored 0.
- Android API 36, Kotlin/Gradle, lint, Debug APK and unsigned AAB validation PASS. Gradle BUILD SUCCESSFUL in 3m. Lint: 0 errors, 13 warnings, 1 hint.
- QA package `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`.
- Artifact 14997818372, size 63,102,201 bytes. ZIP SHA-256 `b1784658074f503d137fa0a31c49062ada76d411fd21b5074753436911969854`; independently rehashed and matched GitHub digest.
- QA APK SHA-256 `20a2f7131c65adc37471e62d2d4b89e26f0e21ab57aa52caf9871badaac4b8d7`.
- Validation AAB SHA-256 `d599915e3ea9cfe8ca99c680628438e7bf89baa461e1b40d45b34e9f1c72514f`; `jarsigner -verify` reports `jar is unsigned`.
- Exact PR: [#311](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/311), Draft, unmerged.
- Candidate compare at code head: 2 commits ahead / 0 behind canonical; only GPS Activity Engine implementation/tests changed.

## Previous GPS handoff

PR #307 exact head `46241bd8286b2b1d3489aef3a46432eea702a054` had prior exact-head CI PASS (workflow 45340645909; Android 349/349). It was 3 ahead / 7 behind the current canonical branch; the seven canonical-only changes since its merge base are ReleaseOps/Health files, with no GPS application-file overlap. To avoid force-pushing, this candidate copied the six GPS-owned PR #307 source/test files onto the current canonical base before adding the stationary guard. After PR #311 passed exact-head CI 45562000301, PR #307 was closed (not merged) as superseded; the six prior GPS changes are carried in PR #311.

## Physical P0 — BLOCKED_NOT_RUN

The authorized Desktop Commander localhost was previously recorded OFFLINE; the last known handset is Samsung SM-A217F / Android 12, with current app/session state unknown. This run did not retry ADB, install, force-stop, permission mutation, notification action or GPS-setting mutation. No physical GPS or phone PASS is claimed.

Required handset acceptance remains: 60-second stationary drift, measured walk/run/cycle routes, precise/approximate and revoke/regrant, first-fix latency/accuracy, in-app navigation, background/screen-off, notification Pause/Resume/Finish, process-death restore, crash/ANR/logcat.

## Google Maps

- Current canonical stack: Leaflet in Android WebView, OSM-derived raster, OpenTopoMap and EOX Sentinel-2.
- No native Google Maps SDK/Rx, Google basemap, traffic or transit layer is evidenced.
- Maps APIs were previously recorded enabled, but key inventory permission was denied and no billing account was linked.
- Owner Cloud permission, billing/project prerequisite and exact production package/signing-certificate fingerprint are not available. No key, secret, billing or paid service was created.

## Release / scope boundary

- No Health/anti-cheat, exercise catalog, release version, workflow, signing, Play, backend or location-upload file changed.
- VersionCode 51020 remains unallocated.
- No signed AAB or Play action was attempted.
- This is source/CI work only; do not merge PR #311 before exact-head Android CI and physical P0.
