# TopHeroFit — GPS / Activity Engine checkpoint (2026-11-20)

Observed: 2026-11-20 17:40 UTC.
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical application base: `d8e315376de6785ec93a792342618737866ae121`.
Latest canonical branch tip before this checkpoint update: `f596bcf722d5fac810538907ad6180999774bfc3` (documentation-only).

## Current GPS owner branch

PR [#303](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/303) remains Draft and is now based on current canonical.

- Branch: `agent/codex/gps-activity-rebased-20261119-r1`.
- Head: `e905d906300d48e3927c0f9fd745cdad39b39334`.
- Base at rebase: `f596bcf722d5fac810538907ad6180999774bfc3`.
- Comparison at rebase: 15 ahead / 0 behind, exactly 15 changed files.
- Rebase preserved all 15 tested candidate file blobs exactly; canonical Health #305 and documentation commits did not overlap these paths.
- Backup ref `agent/codex/gps-pre-rebase-20261120-a328` preserves the pre-rebase head. Staging ref `agent/codex/gps-activity-rebased-20261120-r2-stage` points to the same rebased commit as PR #303 and is retained for audit.

## Exact-head CI evidence (rebased candidate)

- [Run 44784273743](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44784273743) — SUCCESS on exact head `e905d906300d48e3927c0f9fd745cdad39b39334`.
- Product: 77/77; source-contract: 35/35; backend: 29/29.
- Android API 36; unit tests 330/330, zero failures and zero ignored; Kotlin, lint, debug APK and unsigned AAB validation passed.
- Gradle BUILD SUCCESSFUL in 2m54s; lint zero errors / 11 warnings.
- Artifact ID 14652904221; ZIP SHA-256 `195f57456763ad82f66b0f1f1ecc08bb57c6c05e15a6e44e91a6fa99ad107600`, downloaded and independently rehashed.
- APK SHA-256 `d4a9246f95ff6e57b09f04b57caef2463844c57c390a6d25851734368237a6fb`.
- AAB SHA-256 `472c1968ba2fc20e25ea5a6a3d855fb0cf3f87153f5b0d5f963b3183029d9678`; jarsigner reports unsigned. Validation-only identity 51019; not a release artifact.

## Legacy PR #284 reconciliation

PR #284 is now retargeted to the canonical branch but remains Draft: head `274155eafdfff381009ef5814a621f32b225f1a8`, 19 ahead / 74 behind, 13 changed files, no exact-head CI. Historical run 42694452852 passed only on `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; artifact ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c` was independently rehashed. Run 42694199295 failed because the then-truncated MainActivity lacked `motionSnapshot`; current #284 MainActivity is 1,146 lines and contains the symbol, but current-head CI remains absent.

#284 duplicates native fallback/service work now owned by #303. Its UI changes to `app.js`, `index.html` and `MainActivity.kt` conflict with #93/#216/#224 leases. The Leaflet/OSM/OpenTopoMap/EOX stack already exists in canonical; there is no standalone map-tile change to extract. Do not merge #284.

## Candidate behavior represented by PR #303

- Fused Location Provider primary, with permission-aware Android framework fallback.
- Fused request uses permission-level granularity; fine-to-coarse permission downgrade is handled without requesting GPS when fine permission is absent.
- Provider changes clear the previous source anchor; distance is not bridged across providers.
- Mock, invalid, stale/future, out-of-order, poor-accuracy and implausible fixes are filtered.
- Distance accumulator uses accuracy uncertainty, multi-fix confirmation, long-gap re-anchoring and bounded path/net ratio.
- V3 local checkpoint preserves phase, wall/monotonic clocks, boot identity and bounded route; downtime is excluded from active elapsed time.
- Foreground service, ongoing notification and Pause/Resume/Finish actions are represented in source. Physical continuity remains unproven.

The GPS branch is owned by its native Activity Engine lane. The Health lane made no changes to `ActivityTrackingService.kt`, `ActivitySessionCheckpoint.kt`, `ActivitySnapshotPolicy.kt`, `GpsDistanceAccumulator.kt`, `GpsFixGate.kt`, `GpsFixPresentationPolicy.kt`, `ActivityLocationFallbackPolicy.kt`, MainActivity or GPS tests.

## Physical P0 — BLOCKED / NOT RUN

Desktop Commander device `localhost` is OFFLINE (last seen 79 hours ago). Last known handset: Samsung SM-A217F / Android 12. Current device/app/session state is unknown.

No ADB connection, install, launch, force-stop, notification action, location-setting change or activity-data read was attempted.

Required physical tests:
1. Stationary drift with phone still and screen on/off.
2. Measured outdoor walking, running and cycling against a known route.
3. Fine-to-coarse permission downgrade and source-switch behavior.
4. First-fix latency and honest provider-reported accuracy.
5. In-app navigation, background, screen-off and task removal continuity.
6. Notification Pause/Resume/Finish behavior.
7. Process-death restore, crash/ANR and session-end correctness.

No route distance, GPS accuracy, sensor event, notification interaction or physical exercise is claimed.

## Related branches

- PR #284: stale GPS/provider fallback branch, head `274155eafdfff381009ef5814a621f32b225f1a8`, 19 ahead / 74 behind current canonical; retargeted to canonical, no exact-head CI, overlaps #303/#93/#216/#224. Keep Draft.
- PR #248: bounded route smoother helper, head `67d3b438815fe83ced301551aee43f5a6548c91d`, 4 ahead / 209 behind; isolated helper/test, not yet integrated.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains a tested policy but is not wired into the live activity service. The Health session reconciliation in PR #305 does not solve GPS spoofing or location attestation. Native owner must address this in its lane.

## Maps and cost

The current no-billing design remains Leaflet in WebView with attributed OpenStreetMap streets, OpenTopoMap terrain and EOX Sentinel-2 cloudless imagery. No native Google basemap, traffic or transit overlay is present or claimed. No paid service, API key or billing configuration was introduced.

## Release gate

Keep PR #303 Draft/unmerged until current-head CI after rebase, physical P0, privacy/policy and Play declaration gates pass. No version allocation, signing, AAB upload, track mutation or Production promotion. VersionCode 51020 remains unallocated.
