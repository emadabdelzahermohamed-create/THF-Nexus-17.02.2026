# TopHeroFit — Canonical Recovery Checkpoint

**Observed:** 2026-11-24 08:24 Africa/Cairo  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`  
**Canonical ReleaseOps parent before this checkpoint:** `c8f16884b099655950b692c8e735f1dea8b920a3`  
**Current canonical ReleaseOps tip after this checkpoint:** `b688c1793be0a15bd4302c9b7eea0106ed0ea0a5`

## Source-of-truth and starting files

- The canonical pointer is `ReleaseOps/FitnessStandalone/RELEASE_CURRENT.json`; it was read only.
- Requested `GPS_MAP_QUALITY_20261101.md` is absent (404). Latest available report used: `GPS_MAP_QUALITY_20261123.md`.
- Latest canonical recovery input used: `RECOVERY_CURRENT_20261123.md`.
- This checkpoint is documentation-only on the canonical recovery branch. It does not merge or cherry-pick PR #307.

## Activity Engine / GPS

### PR #307 — current GPS handoff candidate

- Branch: `agent/codex/gps-fused-fallback-arbitration-20261122-r1`.
- Exact head: `46241bd8286b2b1d3489aef3a46432eea702a054`.
- Previous exact tested head: `923a951a304d1c8b2210539be83f07c8accb4371`.
- Latest commit: `fix(gps): reject impossible Fused source-transition jumps`.
- Compare snapshot against canonical branch before this checkpoint: 3 commits ahead / 1 behind at `c8f16884b099655950b692c8e735f1dea8b920a3`. This checkpoint adds one more documentation-only canonical commit, so current compare is 3 ahead / 2 behind. Both behind commits (`c8f16884...` and `b688c1793be0a15bd4302c9b7eea0106ed0ea0a5`) are ReleaseOps-only; application changes remain six GPS-owned files. No Health, catalog, release, signing or Play paths are in the PR.
- PR [#307](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/307) remains Draft/unmerged and mergeable.

### New source correction

Fused source recovery previously validated candidates without the fresh framework point as a continuity anchor. The new `GpsFixGate.acceptsSourceTransition()` checks monotonic elapsed time and conservative cross-provider displacement/sport-speed plausibility while allowing a stationary handoff. Fused batch points are sorted and validated against a rolling accepted anchor. Two Kotlin unit tests cover the new cases.

### Exact-head workflow — PASS

- [Workflow 45340645909](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45340645909) completed **SUCCESS** on exact SHA `46241bd8286b2b1d3489aef3a46432eea702a054`.
- Product 83/83; Source Contract 39/39; Backend 29/29; Android Unit 349/349; zero failures and zero ignored.
- Android API 36, Kotlin/Gradle, lint, Debug APK and unsigned AAB validation all PASS. Gradle BUILD SUCCESSFUL in 3m03s; lint 0 errors, 11 warnings, 1 hint.
- Artifact 14895973148 was downloaded and independently rehashed: ZIP SHA-256 `e7adc8ff91e2d0e338a7c0646111605cba36c32a257ede5bf8554e9ab3007bc9`, matching GitHub digest; embedded source marker matches exact SHA.
- QA APK SHA-256 `e43f460a600be7ca4c0ea96dd61a973e13b43714545a45df79a7dabc6810aa98`.
- Validation AAB SHA-256 `255dd7e12469fb342b8c7b1cc1cb044c81bb76e60b4e4cdda95dfe9fca1748d8`; `jarsigner` reports `jar is unsigned`.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is not a signed release or Play upload.
- PR description was updated with the defect, fix, tests and final workflow evidence. PR #307 remains Draft/unmerged; its mergeability is false only because the canonical branch advanced by two documentation-only commits. No app-file overlap was introduced.

## Physical device and GPS quality

- Desktop Commander localhost: OFFLINE; last seen 164 hours ago.
- Last known device: Samsung SM-A217F, Android 12. Current application/session state unknown.
- No ADB or device mutation was attempted.
- Physical P0 remains BLOCKED_NOT_RUN; no GPS accuracy or phone QA PASS.

## Maps

- Canonical stack remains Leaflet + OSM raster, with OpenTopoMap and EOX Sentinel-2 optional layers.
- No Google Maps SDK/Rx, Maps billing enablement, package/SHA-restricted key, traffic layer or transit layer is evidenced.
- Owner Cloud permissions and exact package/signing SHA prerequisite are not available to this run. No key, secret or paid infrastructure was created.

## Release and prohibited areas

- No release version, workflow, signing, Google Play, Health/anti-cheat or exercise-catalog files were changed.
- VersionCode 51020 remains unallocated.
- No signed AAB or Play mutation was attempted.
- No route sync or precise-location upload was added.

## Next safe sequence

1. Read the terminal result of workflow 45340645909; if successful, capture exact test counts and independently verify the produced QA artifact hashes.
2. Keep PR #307 Draft until physical P0 is completed on an authorized handset.
3. Restore device access only after confirming the handset's current state read-only; do not disturb a potentially active session.
4. Continue Maps integration only when owner Cloud permission, billing/project state and package/signing SHA are available.
