# TopHeroFit — Canonical Recovery Checkpoint

**Observed:** 2026-11-24 08:24 Africa/Cairo  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`  
**Canonical ReleaseOps parent before this checkpoint:** `c8f16884b099655950b692c8e735f1dea8b920a3`  
**Evidence-refresh parent before this correction:** `39f0e2e81fbcdc42db7f05e2b3d963021ef4dfd0`

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
- Compare snapshot against canonical branch at evidence-refresh parent `39f0e2e81fbcdc42db7f05e2b3d963021ef4dfd0`: 3 commits ahead / 3 behind. The three behind commits (`c8f16884...`, `b688c179...`, `39f0e2e...`) are documentation-only ReleaseOps checkpoints; application changes remain six GPS-owned files with no overlap. No Health, catalog, release, signing or Play paths are in the PR.
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

1. Preserve exact-head workflow 45340645909 and independently rehashed artifact 14895973148 as the current CI evidence; do not rebuild the unchanged SHA.
2. Keep PR #307 Draft until physical P0 is completed on an authorized handset.
3. Restore device access only after confirming the handset's current state read-only; do not disturb a potentially active session.
4. Continue Maps integration only when owner Cloud permission, billing/project state and package/signing SHA are available.


## Evening canonical integration and Play readback — 2026-11-24 19:38 Africa/Cairo

**Canonical application merge:** `fad03f360c1d9a474b62239025ff76fde7eeb087` (PR #310).
**ReleaseOps parent before this checkpoint:** `62e7cbf90c6d13656b0035f8fc86b1bf6b8bb683`.
**Current candidate/QA boundary:** no release version allocated, no signing, no Play write.

### PR #310 — integrated Health Connect reconciliation fix

- PR #310 was Draft, exact-head tested, reviewed for scope, marked ready and squash-merged at `fad03f360c1d9a474b62239025ff76fde7eeb087`.
- Exact PR source head: `e0cef880cf2d9986b42994bb547ce853f29f2011`; canonical base: `20fc6bea72d5d209a160f9b927a06485ac7a6274`.
- Exact-head CI [45407977041](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45407977041): Product 84/84, Source Contract 35/35, Backend 29/29, Android Unit 342/342; zero failures/ignored; Android API 36, Kotlin/Gradle, lint and APK/AAB validation PASS.
- Artifact 14925853882 was downloaded and independently rehashed: ZIP SHA-256 `e3787277bdd54e0f33e0275dfb24dafabe14295a315c129e3802dbd80d54d47c`; embedded source marker `e0cef880cf2d9986b42994bb547ce853f29f2011`; QA APK SHA-256 `73cfc638bd339b939669de963de683acbcc1e01dd4e9003e23b4fc25e9693a44`; validation AAB SHA-256 `1a0a872658b37e890852d924b0fc76afa64cacadc1aff119ba27e346f6de3c1d`. `jarsigner` confirms the AAB is unsigned.
- The four changed file blobs at the PR head and merge commit were independently compared and are identical. The post-merge push workflow [45450665871](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45450665871) passed the changed-app guard and skipped deterministic-build; no duplicate build artifact was produced.
- The fix quarantines non-transitive connected session-window chains as `NON_TRANSITIVE_ACTIVITY_SESSION_WINDOW`, retaining source-labelled evidence rather than silently collapsing non-pairwise sessions. No Health permissions or manifest scopes changed. No physical Health/wearable PASS is claimed.

### PR #307 — current GPS handoff

- Exact current head remains `46241bd8286b2b1d3489aef3a46432eea702a054`.
- Exact-head CI [45340645909](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45340645909) passed: Product 83/83, Source Contract 39/39, Backend 29/29, Android Unit 349/349; zero failures/ignored; API 36/Kotlin/Gradle and APK/unsigned-AAB validation PASS; lint 0 errors, 11 warnings, 1 hint.
- Artifact 14895973148 was downloaded and independently rehashed: ZIP SHA-256 `e7adc8ff91e2d0e338a7c0646111605cba36c32a257ede5bf8554e9ab3007bc9`; embedded source marker equals the exact head; QA APK SHA-256 `e43f460a600be7ca4c0ea96dd61a973e13b43714545a45df79a7dabc6810aa98`; validation AAB SHA-256 `255dd7e12469fb342b8c7b1cc1cb044c81bb76e60b4e4cdda95dfe9fca1748d8`. `jarsigner` confirms unsigned.
- Current compare against the canonical branch before this checkpoint: 3 ahead / 6 behind. The six later commits are ReleaseOps-only checkpoints, the disjoint #310 Health merge, and the read-only Play-probe trigger; the six GPS implementation/test files do not overlap those changes.
- PR #307 remains Draft/unmerged and GitHub reports mergeable=false while behind. Physical P0 remains BLOCKED_NOT_RUN. Do not rebase/rebuild until handset access returns and P0 can be run without disturbing an unknown active session.

### PR #284 — stale map/settings handoff

- Current head `274155eafdfff381009ef5814a621f32b225f1a8`; 19 ahead / 149 behind current canonical branch; 13 files.
- Run 42694452852 validates only historical SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; no exact-head CI exists for the current PR head.
- It overlaps #307 (`ActivityTrackingService.kt`), #93 (`MainActivity.kt`/Manifest), and #216/#224 (WebView files). Keep Draft; do not merge wholesale.

### Fresh Google Play readback — 2026-11-24 17:38:34 UTC

- Read-only probe [45450770929](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45450770929) succeeded; job 138646921676 succeeded.
- Artifact 14946783770 independently rehashed: ZIP SHA-256 `b44459d24cd9e980423dd2dbef59959da21bbd1e99eedf176db9d0a31f010eb2`; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.
- Internal 51019: Completed. Alpha 51007: Draft. Production is not listed and is NOT_VERIFIED.
- Listing JSON hash is unchanged from the previous readback. `uploadAttempted=false`; `commitAttempted=false`. The probe created and deleted an empty edit session solely to read details/listings/tracks; it did not upload, commit, or change any listing/track/version.
- Support email remains TopHeroFit@gmail.com.

### Device and release gates

- Desktop Commander localhost is OFFLINE; last seen approximately 175 hours ago at this check. Samsung SM-A217F current app/session state is UNKNOWN.
- No ADB command, install, launch, force-stop, notification action, permission change or location-setting change was attempted.
- Physical P0 remains BLOCKED_NOT_RUN: stationary drift, measured routes, permission downgrade/revoke/regrant, first-fix latency/accuracy, background/screen-off, notification controls, process-death recovery, crash/ANR/logcat.
- VersionCode 51020 remains UNALLOCATED. Owner Play/API write permission and GCP Secret Manager signing-key access remain NOT_VERIFIED. No new signed AAB exists.
- Route sync remains design-only; completed routes remain local in `pulse.v2.activities`. No authenticated route endpoint or precise-location upload was added.
- Anti-cheat remains tested but unwired; `GpsFixGate` remains admission and `GpsDistanceAccumulator` remains the sole metric-credit path.
- Competition backend remains provisional `strength_volume_kg_reps`; GPS reward eligibility remains false and no THF payout is authorized.
