# TopHeroFit — GPS / Maps quality checkpoint (2026-11-21)

Canonical branch: `agent/codex/fitness-recovery/20261023`.  
Canonical application merge: `b097d6ef0025d615c261ee42e8d2246533224e70`.  
Exact tested source: `26e90573ddda077ca2665ebdccd5600cc9316dd7`.  
Exact test run: [44929317705](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44929317705).

## Native GPS / Activity Engine — merged

PR [#303](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/303) is merged. It was exactly 1 commit ahead / 0 behind canonical at merge preparation and changed 15 files, all native Activity Engine/GPS source and tests. No WebView map, MainActivity, Manifest, Health, release, signing or Play files were changed. The squash merge tree SHA `9fa0cea8f307c05483f336c409390727c1f7ebc4` equals the tested source tree SHA.

CI:
- Product 77/77; source-contract 35/35; backend 29/29.
- Android API 36; Android unit 335/335, 0 failures, 0 ignored.
- Kotlin/Gradle, lint, debug APK and unsigned AAB validation PASS.
- Gradle BUILD SUCCESSFUL in 3m11s; lint 0 errors / 11 warnings / 1 hint.
- Artifact 14715989999 ZIP SHA-256 `d081932610a732a35df9e5eb37e641938566fe1cd15744760ae195f486a2268e`, independently rehashed.
- APK SHA-256 `39dc453eb4d5572f534ccd910882a17ccfb5b5c04849755897dcd6f73de2d9f5`.
- AAB SHA-256 `4854e2585757383ce7d59e10b3bff48537a7bf4387dd2359c7918d339719d7d4`; unsigned validation only.

Native behavior:
- Fused primary, permission-level granularity; approximate-only permission does not request GPS.
- First-fix fallback at 8 seconds; stale accepted fix watchdog at 12 seconds.
- One framework provider at a time; GPS to Network fallback only when permissions/provider state allow.
- Listener and registration-generation guards reject callbacks queued by replaced providers.
- Source changes reset distance anchor, preventing cross-provider bridging.
- Mock/invalid/stale/future/out-of-order/poor-accuracy/implausible fixes are filtered.
- Distance requires multi-fix confirmation, uncertainty/deadband and re-anchoring after long gaps.
- Session checkpoint includes phase, wall/monotonic clocks, boot identity and bounded route; downtime is excluded from active elapsed time.
- Foreground service and notification controls are in source but not yet proven on the physical handset.

These filters reduce noise; they are not cryptographic location attestation and cannot guarantee rejection of prolonged stationary multipath drift.

## Map stack and PR #284

Canonical map stack:
- Leaflet inside Android WebView.
- Attributed OpenStreetMap streets.
- OpenTopoMap terrain.
- EOX Sentinel-2 cloudless imagery.

No Google Maps Rx, Maps SDK, billing, API key or paid map provider is required for this stack.

PR [#284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284) remains Draft, open and unmerged. Its head `274155eafdfff381009ef5814a621f32b225f1a8` is 19 commits ahead / 80 behind current canonical, 13 files changed, and no exact-head CI exists. The historical PASS 42694452852 applies only to SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; the historical failure 42694199295 was the truncated MainActivity/missing `motionSnapshot` source-contract failure.

After #303 merged:
- #284 native provider/service/presentation/test changes are superseded and must not be merged.
- Remaining #284 UI changes touch app.js, index.html and MainActivity (location status/pause, Android Location Settings bridge, accuracy-circle gating and User-Agent). These overlap #93/#216/#224 ownership.
- The existing Leaflet/tile stack is already canonical; no standalone map-tile patch remains.
- Keep #284 Draft. Any retained UI change must be extracted under an explicit shared-file lease and pass exact-head CI.

## Display-only route smoother PR #248

PR [#248](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/248) remains Draft, 4 commits ahead / 231 behind canonical, with no exact-head CI. It adds only a standalone Kotlin smoother and its tests; the helper has no production call site. Canonical WebView `app.js` already has and calls `smoothActivityRouteForDisplay()` during map rendering. Keep one presentation implementation; do not merge an unused duplicate. Neither smoother may feed metrics, activation or rewards.

## Route history and sync boundary

`persistFinishedActivity()` writes completed route points to WebView localStorage. The map's one-second polling is a local UI update only. Existing account sync handles workout/set metadata and does not include coordinates. No authenticated route API or cloud upload exists. Keep route backup as a separate default-off feature with independent consent, finished-session-only upload, retention, revocation, deletion and privacy/security review. See `ROUTE_SYNC_CONTRACT_RECHECK_20261121.md`.

## Physical P0 — BLOCKED_NOT_RUN

Desktop Commander localhost is OFFLINE (last seen 103 hours before the 2026-11-21 check). Last known handset: Samsung SM-A217F / Android 12; current app/session state unknown. No ADB or session/device action was attempted.

Required tests: stationary drift; measured walk/run/cycle; precise-to-approximate downgrade; first-fix latency and truthful accuracy; background/screen-off/task removal; notification Pause/Resume/Finish; process-death restore without downtime credit; crash/ANR review.

No phone/GPS/route/notification PASS is claimed. No versionCode allocation, signing, Play upload or Production promotion is authorized by this checkpoint.
