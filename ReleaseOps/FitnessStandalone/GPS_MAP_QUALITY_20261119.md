# TopHeroFit GPS / Map Quality — canonical checkpoint 2026-11-19

## Exact native candidate

- Selected PR #303, branch `agent/codex/gps-activity-rebased-20261119-r1`.
- Exact candidate HEAD/source SHA `6e73d988fe668c5b86f2ff4c053f2f43c2c4b6a8`; canonical base `e28994ea76e67e0bed6eef3860f995b27388a002`.
- Exactly 14 native GPS/Activity Engine source/test files; 1 ahead / 0 behind canonical. No WebView, MainActivity, Manifest, Health, catalog, release, workflow, signing or Play file changes.
- Exact-head run [44582044304](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44582044304) SUCCESS: Product 73/73, source-contract 34/34, backend 29/29, Android 316/316, 0 failures / 0 ignored, API 36/Kotlin/lint/assembleDebug/unsigned bundle validation PASS.
- Artifact 14560755289 ZIP SHA-256 `844d8cf09ede8ee9e7357d3461bfab6e557bce785bf4b1252a2aa470502af10b`; QA APK SHA-256 `ebeb5eb8725b8c265bc641f87046f80bb72e3150cb6018d825c35cb703c7917a`; unsigned validation AAB SHA-256 `62233609a6bb52f27a6905a028bcd5335f593c045e3ec60b5cb84cdd5a7c0fd9`. All were independently rehashed from the downloaded artifact. AAB has no META-INF signing entries. QA/validation only; not a release.
- Lint: 0 errors, 12 warnings, 1 hint. Gradle BUILD SUCCESSFUL in 3m 8s.

## Native behavior and limitations

- Fused primary; permission-aware single Android framework fallback. Fine permission can select GPS; coarse-only selects Network; no GPS request without fine permission.
- Provider changes clear prior source anchors; no cross-provider distance bridge. Mock, invalid, stale/future, out-of-order, poor-accuracy and implausible fixes are rejected.
- Distance accumulation uses endpoint-accuracy uncertainty deadband, multi-fix confirmation, long-gap re-anchoring and bounded path/net ratio. This reduces noise but is not proof against prolonged stationary multipath drift.
- V3 local checkpoint preserves phase, wall/monotonic clocks, boot identity and bounded route; process downtime is not credited.
- Foreground service, START_STICKY, ongoing notification, Pause/Resume/Finish actions and periodic local checkpoint writes exist in source. They are not physically proven until the SM-A217F P0 matrix passes.

## Map stack

- Leaflet in WebView.
- OpenStreetMap attributed street tiles.
- OpenTopoMap terrain.
- EOX Sentinel-2 cloudless 2016 satellite and hybrid.
- Browser cache is not a guaranteed offline map package. No Google basemap, traffic or transit layer is present or claimed. No Maps SDK, billing or key is required for this selected stack.

## PR #284 reconciliation

- Historical run 42694452852 validates only historical SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; its downloaded ZIP SHA-256 was independently verified as `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`.
- Historical run 42694199295 failed at the motionSnapshot source-contract test because MainActivity was truncated at that historical head. The current #284 head `274155eafdfff381009ef5814a621f32b225f1a8` has a 1,146-line MainActivity with motionSnapshot present, but has no exact-head CI.
- Current #284 compare: 19 ahead / 69 behind; 13 files; overlaps #303 native service/provider code, #216/#224 shared app.js, and #93 MainActivity/Health bridge. Keep Draft and unmerged. Extract map-only changes if retained.

## Route sync and anti-cheat boundaries

- Completed route points remain local in WebView localStorage; no authenticated route endpoint/table or precise-location cloud upload exists. Route backup is design-only with separate consent, retention, revocation and deletion gates.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired in the live service. Current GPS filters do not constitute complete anti-cheat or cryptographic location attestation.

## Physical P0

BLOCKED_NOT_RUN. Desktop Commander localhost OFFLINE, last seen 56 hours ago on 2026-11-19. Last known device SM-A217F / Android 12; current app/session unknown. Preserve it. No ADB, install, launch, force-stop, notification action, settings change or activity-data read was attempted.

Required P0: stationary drift; measured outdoor walk/run/cycle; fine-to-coarse downgrade; first-fix latency and accuracy honesty; navigation/background/screen-off/task removal; notification Pause/Resume/Finish; process-death restore without downtime credit; crash/ANR review.

## Release decision

PR #303 remains Draft/unmerged pending physical P0 and privacy/policy gates. VersionCode 51020 remains unallocated. No signing, Play upload or Production promotion.
