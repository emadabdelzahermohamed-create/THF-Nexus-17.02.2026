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

### Exact-head validation — pending

Workflow [45340645909](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45340645909) is attached to exact head `46241bd8286b2b1d3489aef3a46432eea702a054`.

At checkpoint time:
- Product, source-contract and backend regression step: **SUCCESS**.
- Android unit/lint/API 36/APK/AAB build step: **IN_PROGRESS**.
- No artifact has been published by this run yet.
- Do not claim full CI PASS, Android test PASS, GPS accuracy PASS or phone QA PASS until exact workflow completion and physical evidence.

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

1. Read the terminal result for exact-head workflow 45340645909; record artifact hashes only if it completes successfully.
2. Keep PR #307 Draft until Physical P0 passes on an authorized handset.
3. Resume device work only after read-only inspection confirms no existing activity session will be disturbed.
4. Keep Google Maps provisioning blocked until owner Cloud permission and package/signing SHA prerequisites are evidenced.
