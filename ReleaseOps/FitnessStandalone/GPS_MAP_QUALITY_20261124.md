# TopHeroFit — GPS / Map Quality Checkpoint

**Observed:** 2026-11-24 08:24 Africa/Cairo  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`  
**Canonical ReleaseOps tip before this checkpoint:** `c8f16884b099655950b692c8e735f1dea8b920a3`

## Starting evidence

- The requested path `ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261101.md` returned GitHub Contents API 404 on the default branch.
- The newest available canonical GPS report is `GPS_MAP_QUALITY_20261123.md` (blob `388bbcb5f18de972d5e84c1f8f61cd657ae1406f`).
- The canonical recovery input is `RECOVERY_CURRENT_20261123.md` (blob `6a5fad9daa2fecf86533b504e678f22c210eccf2`).
- `ReleaseOps/FitnessStandalone/RELEASE_CURRENT.json` exists and designates the canonical recovery branch; it was read only and not modified.

## Canonical map state

- Leaflet in Android WebView.
- OpenStreetMap-derived raster base layer.
- OpenTopoMap and EOX Sentinel-2 optional layers.
- No native Google Maps SDK/Rx integration, Maps billing enablement, or Android-restricted Maps key is evidenced.
- No Google traffic/transit layer is integrated.
- Do not provision a key until owner Cloud permission, billing/project prerequisites and the exact release package/signing SHA are available. No paid service or secret was created in this run.

## PR #307 — cross-provider jump guard

**Branch:** `agent/codex/gps-fused-fallback-arbitration-20261122-r1`  
**Exact current head:** `46241bd8286b2b1d3489aef3a46432eea702a054`  
**Previous tested head:** `923a951a304d1c8b2210539be83f07c8accb4371`  
**Commit:** `46241bd8286b2b1d3489aef3a46432eea702a054` — `fix(gps): reject impossible Fused source-transition jumps`

### Defect found

The Fused recovery batch was admitted using `GpsFixGate.accepts(..., previous = null)`. That checked each candidate in isolation and bypassed spatial/speed continuity against the fresh framework fix currently owning the route. A more accurate but physically impossible cross-provider jump could become the first post-promotion route anchor.

### Implemented correction

- Added `GpsFixGate.acceptsSourceTransition()`.
- It applies the normal mock/accuracy/coordinate/freshness gate, requires strictly increasing elapsed-realtime timestamps, and applies a conservative displacement/sport-speed ceiling against the previous accepted fix.
- It deliberately does not apply the stationary movement deadband at a source handoff, so a stationary but valid Fused fix can still take over.
- Fused batches are sorted by elapsed-realtime timestamp and checked against a rolling last-accepted anchor. Rejected candidates do not advance that anchor.
- Added two Kotlin tests covering stationary/plausible handoff, teleport rejection, duplicate timestamps and stale previous anchors.
- Extended the GPS source-contract test to require sorted, anchored transition validation.

### Exact-head validation — PASS

Workflow [45340645909](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45340645909) completed **SUCCESS** on exact head `46241bd8286b2b1d3489aef3a46432eea702a054`.

| Suite / validation | Result |
|---|---:|
| Product | 83/83 |
| Source contract | 39/39 |
| Backend | 29/29 |
| Android unit | 349/349 |
| Android failures / ignored | 0 / 0 |
| Android API 36 / Kotlin / Gradle | PASS |
| Lint | 0 errors, 11 warnings, 1 hint |
| Debug APK / unsigned AAB validation | PASS |

Gradle BUILD SUCCESSFUL in 3m03s. APK identity was verified in the workflow log: `com.topherofit.thf.pulse.qa`, versionCode `51019`, versionName `5.0.0-v2-alpha19-debug`.

Artifact `14895973148` was downloaded and independently rehashed:
- ZIP size: 63,097,908 bytes.
- ZIP SHA-256: `e7adc8ff91e2d0e338a7c0646111605cba36c32a257ede5bf8554e9ab3007bc9` (matches GitHub artifact digest).
- Embedded source marker: `46241bd8286b2b1d3489aef3a46432eea702a054`.
- QA APK SHA-256: `e43f460a600be7ca4c0ea96dd61a973e13b43714545a45df79a7dabc6810aa98`.
- Validation AAB SHA-256: `255dd7e12469fb342b8c7b1cc1cb044c81bb76e60b4e4cdda95dfe9fca1748d8`.
- `jarsigner -verify`: `jar is unsigned`.

This is an unsigned QA validation artifact only, not a signed release or Play upload. Android CI PASS does not establish physical GPS or phone QA PASS.

The PR remains Draft/unmerged. The changed-file set is six GPS-owned implementation/test files only:
- `ActivityLocationFallbackPolicy.kt`
- `ActivityTrackingService.kt`
- `GpsFixGate.kt`
- `ActivityLocationFallbackPolicyTest.kt`
- `GpsFixGateTest.kt`
- `fitness-v2/tests/test_source_contract.py`

## Physical P0 — BLOCKED_NOT_RUN

Latest read-only device list reports Desktop Commander `localhost` OFFLINE, last seen 164 hours ago. Samsung SM-A217F / Android 12 remains the last known handset; current app and activity-session state is unknown.

No ADB, install, force-stop, notification action, permission mutation or GPS-setting change was attempted.

Required P0 evidence:
1. Stationary 60-second drift and false-distance measurement.
2. Known-distance walking, running and cycling.
3. Fine-to-Approximate downgrade, revoke/regrant and same-session recovery.
4. First-fix latency, displayed accuracy and stale/mock/jump rejection.
5. In-app navigation, background and screen-off continuity.
6. Persistent notification Pause/Resume/Finish.
7. Same-session process-death recovery without crediting stopped time.
8. Raw Logcat, crash and ANR evidence.

## Release boundary

- No version allocation or release workflow/signing change.
- VersionCode 51020 remains unallocated.
- No signed AAB, Play upload, track mutation or listing change.
- No Health/anti-cheat or exercise-catalog file changed.
- No paid infrastructure or unrelated project work.

## Next safe action

1. Do not rebuild the unchanged exact application SHA; run 45340645909 is the completed evidence for this source tree.
2. Keep PR #307 Draft until Physical P0 passes on an authorized handset.
3. Resume device work only after read-only inspection confirms no existing activity session will be disturbed.
4. Keep Google Maps provisioning blocked until owner Cloud permission and package/signing SHA prerequisites are evidenced.


## Evening update — 2026-11-24 19:38 Africa/Cairo

### Latest exact GPS source handoff

PR #307 remains the active GPS source-arbitration handoff at exact head `46241bd8286b2b1d3489aef3a46432eea702a054`. The 2026-11-24 cross-provider continuity guard prevents a fresh-but-impossible Fused fix from becoming the route anchor after framework fallback. It applies normal fix validation, strictly increasing elapsed-realtime timestamps, and a conservative displacement/sport-speed envelope; batches are sorted and checked against a rolling accepted anchor. A stationary but valid handoff remains allowed.

Exact-head run [45340645909](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45340645909) passed 83 Product, 39 Source Contract, 29 Backend and 349 Android unit tests, with zero failures/ignored. Artifact 14895973148 ZIP SHA-256: `e7adc8ff91e2d0e338a7c0646111605cba36c32a257ede5bf8554e9ab3007bc9`; QA APK: `e43f460a600be7ca4c0ea96dd61a973e13b43714545a45df79a7dabc6810aa98`; unsigned validation AAB: `255dd7e12469fb342b8c7b1cc1cb044c81bb76e60b4e4cdda95dfe9fca1748d8`.

The PR remains Draft. Current canonical compare is 3 ahead / 6 behind, with only disjoint ReleaseOps/Health/probe commits behind it. GitHub reports mergeable=false while behind. No source rebase or repeat build was performed.

### PR #284 remains unvalidated at its current head

Current head `274155eafdfff381009ef5814a621f32b225f1a8`, 19 ahead / 149 behind, 13 files. Its only successful workflow is historical run 42694452852 on `3fcbe6ac...`; that is not evidence for the current head. Shared ownership conflicts remain across ActivityTrackingService, MainActivity/Manifest and WebView files. Keep Draft and extract no partial bridge until the relevant owners release those files and the isolated change receives exact-head CI and physical P0.

### Map and metrics boundary

Leaflet/WebView + OpenStreetMap-derived raster layers remain canonical, with OpenTopoMap and EOX Sentinel-2 optional layers. No Google Maps SDK/Rx, billing, API key, traffic or transit overlay was added. Map refresh remains local UI only; it is not route sync. GPS display smoothing must never alter distance, pace, speed or reward metrics.

Physical P0 is still BLOCKED_NOT_RUN because the authorized Desktop Commander device is offline and the Samsung SM-A217F session state is unknown. No phone/GPS accuracy PASS is claimed.
