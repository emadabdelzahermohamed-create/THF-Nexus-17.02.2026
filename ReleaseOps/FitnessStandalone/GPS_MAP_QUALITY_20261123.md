# TopHeroFit — GPS / Map Quality Checkpoint

**Observed:** 2026-11-23 19:51 Africa/Cairo  
**Canonical application branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical tip:** `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`

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

- Current PR head: `5326bdef60c5e7e65ff6633767e43ade17675955`.
- Exact-head CI: [45132278712](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45132278712), success.
- Product 81/81; Source Contract 39/39; Backend 29/29; Android 345/345; zero failures/ignored.
- Artifact 14797923310 ZIP SHA-256 `f3010f85b58670a7fada3de693aa4dd4a1e74f6d3fe8a0c1eed75102d1ce9c9d`.
- Unsigned validation AAB SHA-256 `97e790a850f404746a3c12f9107d1a18aaa2b3842c14a010c3d72b74bba52997`.
- The fix keeps Fused subscribed during framework fallback so a valid Fused fix can reclaim the source without the prior callback having been cancelled. The current branch is 9 ahead / 21 behind canonical; rebase and exact-head CI are still required.
- Physical P0 is not run. No GPS accuracy PASS is claimed.

### PR #284 — fallback watchdog / map settings

- Current head `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; 19 ahead / 129 behind canonical; 13 changed files.
- Historical exact-head run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) succeeded: Product 60/60, Source 38/38, Backend 29/29, Android 223/223, zero failures/ignored.
- Artifact 13707718861 ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`.
- Unsigned AAB SHA-256 `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`.
- The old failing run 42694199295 had a source-contract failure because `motionSnapshot` was absent from the truncated MainActivity input. The current PR branch tail contains `motionSnapshot` and the proposed `openLocationSettings()` bridge.
- The canonical MainActivity does not yet contain `openLocationSettings()`. Do not merge #284 wholesale: it overlaps #307, #93, #216 and #224. The settings bridge is a later isolated extraction, not permission to merge the stale branch.

## Physical P0 gate — BLOCKED

Desktop Commander localhost is offline; the Samsung SM-A217F's current state is unknown. Do not launch, install, force-stop, pause or finish any possibly active session until the device is reconnected and its current state is read-only inspected.

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
