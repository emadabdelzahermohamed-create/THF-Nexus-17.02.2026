# TopHeroFit — GPS / Map Quality Checkpoint

**Observed:** 2026-11-26 17:59:45 UTC  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `779df53146e23e76fe7b1faabffbc0e3540ee29a`  
**Latest Play readback:** [45872277536](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45872277536)

## Latest GPS source handoff — PR #311

- PR #311 current head: `5eee7f80543d88420af011e36c4001660e75ee3b`; base: `10d9794546e6ecd203bb8078ed458f25a23f056c`.
- Exact-head workflow [45566362328](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45566362328) succeeded on that exact head: Product 84/84, Source Contract 40/40, Backend 29/29, Android Unit 355/355; zero failures/ignored; API 36/Kotlin/Gradle, lint and APK/unsigned-AAB validation PASS. Lint: 0 errors, 13 warnings, 1 hint.
- Artifact 14999518977 ZIP SHA-256 `01d30c100dece05428d6f3bb78b61468ebf8281c031f675e243d56d2e0bf50b0`; APK `154b76c9601db115a4b8484af8f051cce017abd10b5edf7a0e9b5e9e133ea301`; unsigned AAB `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`. Source marker matches the exact PR head.
- QA-only identity: `com.topherofit.thf.pulse.qa`, versionCode 51019. No signed release candidate or Play upload.

### Source arbitration and stationary drift

- Fused fix must be strictly newer than the current fresh framework fix; stale/equal elapsed-realtime values cannot displace it.
- Fused batches are sorted by elapsed realtime and validated against a rolling accepted anchor.
- A candidate is checked against the current provider fix using a conservative displacement/sport-speed envelope. A rejected jump does not advance the anchor.
- Source promotion resets the live distance anchor without crediting the transition itself; cumulative distance and historical route remain.
- Android speed accuracy is optional and read only on API 26+ when present.
- Stationary re-anchoring requires two fresh same-source observations at least 3 seconds apart with combined speed upper bound <=0.35 m/s. One low-speed fix is provisional; resumed movement is measured from that observation. Missing speed accuracy does not imply stationary.
- Consecutive-fix gap cap: 30 seconds. Stable movement-anchor lifetime: 120 seconds.
- A 31-second gap with a 100 m apparent jump re-anchors; only the next measured 30 m / 15 s segment is credited. A 45-second slow-movement regression preserves 9 m continuous movement.
- `GpsFixGate` remains signal admission; `GpsDistanceAccumulator` remains the sole metric-credit path. Display smoothing must not alter distance, pace, speed or rewards.

## Map stack and PR #284

- Canonical map: Leaflet in Android WebView, OpenStreetMap-derived raster base; OpenTopoMap and EOX Sentinel-2 are optional layers.
- No Google Maps SDK/Rx, Maps SDK billing, Google basemap or new API key is required for the current OSM stack.
- PR #284 is Draft, current head `274155eafdfff381009ef5814a621f32b225f1a8`, base `f596bcf722d5fac810538907ad6180999774bfc3`, 13 files, 19 ahead / 169 behind.
- Historical workflow [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) validates only SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`, not the current head. Current-head CI is absent; historical artifact 13707718861 is unavailable.
- The PR overlaps #311 GPS service/policy, #93 MainActivity/Manifest and #216/#224 WebView files. Do not merge wholesale.
- Intended handoff behavior includes 8s/12s Fused-to-Android LocationManager fallback, selecting one framework provider (GPS if enabled, else network), stopping Fused after fallback registration, truthful GPS accuracy/pause UI, unique TopHeroFit User-Agent, OSM caching and explicit Android Location Settings bridge when device-wide location is off. This behavior is not validated at the current #284 head.

## Physical P0 — BLOCKED_NOT_RUN

Desktop Commander localhost is Offline; Samsung SM-A217F current app/session state is unknown. No ADB/device mutation was attempted.

Required:
1. Stationary 60-second drift test.
2. Measured walking, running and cycling routes.
3. Precise/approximate permission downgrade, revoke and regrant.
4. First-fix latency and accuracy.
5. In-app navigation and screen-off/background tracking.
6. Persistent notification Pause/Resume/Finish.
7. Process-death restore without crediting stopped time.
8. Crash, ANR and Logcat inspection.

No GPS accuracy, background tracking or phone QA PASS is claimed from CI alone.

## Separate route-sync gap

Finished route history remains in WebView localStorage. No authenticated route-sync endpoint/table or precise-location upload exists. After #284 is validated, inspect the existing account/backend contract and design explicit opt-in consent, retention/deletion and no precise-location upload by default. One-second local map refresh is not route sync.
