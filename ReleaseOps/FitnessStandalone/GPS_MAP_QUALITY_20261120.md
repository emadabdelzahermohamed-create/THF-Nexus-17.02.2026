# TopHeroFit — GPS / Activity Engine checkpoint (2026-11-20)

Observed: 2026-11-20 14:01 UTC.
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical base: `d8e315376de6785ec93a792342618737866ae121`.

## Current GPS owner branch

PR [#303](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/303) remains Draft.

- Branch: `agent/codex/gps-activity-rebased-20261119-r1`.
- Current head: `a3289482f93e500e2e0146e8f9b2d838a2390cb3`.
- Previous base: `ae197167a90e64b39d6fd5ae475bdc8c480186fa`.
- Fresh comparison against current canonical `d8e315376de6785ec93a792342618737866ae121`: 3 ahead / 2 behind; diverged.
- The Health-only PR #305 merge did not modify any GPS or Activity Engine native file. The owner must rebase #303 onto current canonical and rerun exact-head CI before any merge consideration.
- Handoff comment posted to PR #303: [November 20 canonical rebase requirement](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/303#issuecomment-7041498318).

## Exact-head CI evidence (pre-rebase candidate)

- [Run 44689978734](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44689978734) — SUCCESS on exact PR head `a3289482f93e500e2e0146e8f9b2d838a2390cb3`.
- Product: 73/73; source contract: 35/35; backend: 29/29.
- Android API 36 setup, Kotlin/Gradle compilation, Android unit-test task, lint, debug APK and unsigned AAB validation passed.
- Artifact ID `14608472151`; ZIP digest `771af3bf867c4b3fed8b96ff36dff66c48155ef35f493b51100c1b7ec6b1620e`.
- This validates the pre-rebase candidate only. It does not validate the combined tree after canonical advanced.

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

Desktop Commander device `localhost` is OFFLINE (last seen 76 hours ago). Last known handset: Samsung SM-A217F / Android 12. Current device/app/session state is unknown.

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

- PR #284: stale GPS/provider fallback branch, head `274155eafdfff381009ef5814a621f32b225f1a8`, 19 ahead / 72 behind current canonical; overlaps GPS/MainActivity/WebView files with #303. Do not merge blindly.
- PR #248: bounded route smoother helper, head `67d3b438815fe83ced301551aee43f5a6548c91d`, 4 ahead / 209 behind; isolated helper/test, not yet integrated.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains a tested policy but is not wired into the live activity service. The Health session reconciliation in PR #305 does not solve GPS spoofing or location attestation. Native owner must address this in its lane.

## Maps and cost

The current no-billing design remains Leaflet in WebView with attributed OpenStreetMap streets, OpenTopoMap terrain and EOX Sentinel-2 cloudless imagery. No native Google basemap, traffic or transit overlay is present or claimed. No paid service, API key or billing configuration was introduced.

## Release gate

Keep PR #303 Draft/unmerged until current-head CI after rebase, physical P0, privacy/policy and Play declaration gates pass. No version allocation, signing, AAB upload, track mutation or Production promotion. VersionCode 51020 remains unallocated.
