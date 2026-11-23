# TopHeroFit — GPS / Map Quality Checkpoint

**Observed:** 2026-11-23 19:51 Africa/Cairo  
**Canonical application branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`  
**Current ReleaseOps tip before this checkpoint:** `54d6266c3c8bc469a339a2e1db59734b0ecc8908`

## Canonical map stack

- Leaflet inside Android WebView.
- OpenStreetMap-derived raster tiles for the base map.
- OpenTopoMap and EOX Sentinel-2 as optional terrain/satellite layers.
- Canonical MainActivity appends `TopHeroFit/${BuildConfig.VERSION_NAME}` to the existing WebView User-Agent.
- Draft PR #284 proposes the explicit `TopHeroFit/${BuildConfig.VERSION_NAME} (Android; contact: TopHeroFit@gmail.com)` User-Agent; it is not in canonical source.
- No Google Maps SDK, Google Maps Rx, Maps billing, or new API key.
- The one-second map refresh is local UI state only. It is not route backup or cloud sync.
- Tile caching and WebView cache settings do not prove full offline map availability.

## Canonical source vs handoffs

### Canonical Activity Engine

PR #303 is already merged at `b097d6ef0025d615c261ee42e8d2246533224e70`. It supplies the canonical Activity Engine and GPS distance path. PR #309 was subsequently merged as a disjoint Health-only change; canonical tip is now `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`.

### PR #307 — source arbitration follow-up

- Current PR head: `923a951a304d1c8b2210539be83f07c8accb4371`, based directly on canonical tip `54d6266c3c8bc469a339a2e1db59734b0ecc8908`.
- Exact-head run [45238807995](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45238807995): Product 83/83; Source Contract 39/39; Backend 29/29; Android 347/347; zero failures/ignored; Android API 36/Kotlin/Gradle PASS; lint 0 errors, 11 warnings, 1 hint.
- Artifact 14851146115 ZIP SHA-256 `d8e716b24d085b65517354955483b0828c9eee1863b232129acc5a77e3389d8b`; QA APK SHA-256 `b26f62bed569b6a27c1c9fd83a3afa85513b3a89ab42418e7fc0ee7e21384739`; unsigned validation AAB SHA-256 `8339981e7fc59f3bbab0ab5c8d4b0b659048a08b9cddd39389cedebc6e973ee0`. All hashes were independently recomputed; embedded source marker equals the exact PR head; `jarsigner` confirms unsigned.
- Fused promotion now requires a strictly newer elapsed-realtime fix than the current fresh framework fix; equal timestamps fail closed. Older/equal entries in a batched Fused result are excluded before they can be appended after source promotion. The distance accumulator resets at the source boundary; no transition distance is credited.
- The initial rebased attempt `ecfe9adb...` failed one source-contract expectation before Android build and produced no artifact. The contract was corrected in `923a951a...`; the exact-head run above passed.
- Comparison: 2 ahead / 0 behind canonical ReleaseOps tip `54d6266c...`; four GPS-only application/test files. Physical P0 remains BLOCKED_NOT_RUN. Keep Draft/unmerged; no GPS/phone PASS is claimed.

### PR #284 — fallback watchdog / map settings

- Current PR head `274155eafdfff381009ef5814a621f32b225f1a8`; original base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`. Current comparison to canonical ReleaseOps tip `54d6266c3c8bc469a339a2e1db59734b0ecc8908`: 19 ahead / 143 behind; 13 changed files.
- Historical exact-head run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) succeeded only on old head `3fcbe6acbb4dc660284c74c8392818996e1de7ee`: Product 60/60, Source 38/38, Backend 29/29, Android 223/223, zero failures/ignored.
- Artifact 13707718861 ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`; embedded source marker exactly matches `3fcbe6ac...`; unsigned validation AAB SHA-256 `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`. ZIP/AAB hashes independently rechecked in this run.
- The old failing run 42694199295 failed because the uploaded MainActivity source was truncated before `motionSnapshot`; no artifact was produced. Current #284 MainActivity is 1,146 lines with `motionSnapshot` and `openLocationSettings`; canonical MainActivity is 1,140 lines with `motionSnapshot` but without the settings bridge.
- No exact-head CI exists for the current #284 head. Do not merge wholesale: ActivityTrackingService overlaps #307; MainActivity is leased by #93; app.js/index.html overlap #216/#224. Keep Draft; only a later isolated settings bridge can be considered after shared-file ownership is released and exact-head/device validation passes.

## Physical P0 gate — BLOCKED

The latest read-only Desktop Commander device-list check still reports localhost OFFLINE (last seen about 152 hours ago); the Samsung SM-A217F current app/session state is unknown. Do not launch, install, force-stop, pause or finish any possibly active session until the device is reconnected and its current state is read-only inspected.

Required measurements:
1. Stationary 60-second drift and false distance.
2. Known-distance walking, running and cycling.
3. Fine-to-approximate permission downgrade and recovery.
4. First-fix latency, displayed accuracy and stale-fix rejection.
5. Background/screen-off continuity and persistent notification controls.
6. Pause/resume/finish and process-death recovery without counting stopped time.
7. Raw Logcat, crash and ANR evidence.

## Separate route-sync gap

Completed routes remain in WebView localStorage `pulse.v2.activities`. No authenticated route API or backend table exists. Do not upload precise location by default; route sync requires separate opt-in consent, retention/deletion semantics and account deletion verification. The local 1-second UI refresh is not sync.
