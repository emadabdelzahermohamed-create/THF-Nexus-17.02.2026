# THF Spark / Rush Runtime Wiring Checkpoint V1 — 2026-09-13

Workflow: `THF Spark Rush Runtime Wiring Forensics V1`
Run: `34768426201` — SUCCESS
Artifact: `THF-SPARK-RUSH-RUNTIME-WIRING-FORENSICS-V1`
Artifact ID: `10320333895`
Artifact ZIP digest: `8930e1cd8d695b2d7822700f9c633e2d07d2d3095462cee4ad1659333d0c0a81`

Safety: read-only, endpoints redacted, WAVE excluded, source SHAs reverified unchanged.

## Architecture finding
Both RC2 apps are WebView-hosted native Android shells. Both MainActivity sources expose the same 26-method host lifecycle/configuration surface, including `buildUi`, `configureWebView`, `loadProduct`, `loadUrl`, `showOffline`, `showNetworkError`, `showConfigError`, `injectNativePrefs`, deep-link handling and WebView navigation callbacks. No JavaScript interface is currently exposed.

This confirms that simply polishing the host UI would remain an invalid game substitute. A real local game mode must execute game state/input/update/render behavior inside a packaged local asset, and online/ranked state must stay server-authoritative.

## Spark RC2
Source SHA-256: `6b74f8d75df8c0b7f74d8c2fee8be7e3517f3803cb42968735bc7a10939bc18c`.

Detected contract markers:
- WebView: yes
- learning logic: yes
- network client: yes
- offline storage: yes
- ranking: yes
- economy/reward references: yes
- real game loop: no
- player/avatar state: no
- touch wiring: no
- sensor input: no
- canvas game surface: no
- JS/native bridge: no

Safe route literals include `/health`, `/leaderboard/{game_id}`, `/level/{game_id}`, `/scores`, `/leagues`, `/leagues/{league_id}/join`, `/api/v1/me`, registry/handoff routes and `/ai/proposals`. Two absolute endpoint literals exist but their values were not emitted.

Conclusion: Spark currently contains learning/business/backend behavior but not a real interactive game loop. It must not be described as game-ready.

## Rush RC2
Source SHA-256: `bb6ff035186b13cdde853145f42e66259c205889de2a7b368da34c9cb0582ba7`.

Detected contract markers:
- WebView: yes
- fitness logic: yes
- an update/timer game-loop-like marker: yes
- network client: yes
- offline storage: yes
- ranking: yes
- economy/reward references: yes
- camera-related marker: yes
- player/avatar state: no
- touch wiring: no
- sensor input: no
- canvas game surface: no
- JS/native bridge: no

Safe route literals include `/health`, `/leaderboard/{game_id}`, `/sessions`, `/results`, `/anti-cheat`, `/api/evidence/`, `/api/v1/internal/leaderboards/score`, `/api/v1/me` and registry/handoff routes. Five absolute endpoint literals exist but their values were not emitted.

Conclusion: Rush has fitness/session/ranking logic but lacks the player-state + touch-driven game interaction required to be a real mobile game.

## Engineering action started
A reversible local-practice candidate overlay has been created for the existing packaged `android/app/src/main/assets/offline.html` path. The candidate provides a responsive Canvas game surface, pointer/touch input, local player/avatar state, an animation/update loop and domain-specific practice behavior:
- Spark: local arithmetic learning rounds with two physical touch targets and local-only score.
- Rush: local touch/reaction training targets and local-only rep/streak state.

The mode explicitly writes no ranked/social/wallet/economy/reward/fitness-evidence state, uses no network and respects safe-area CSS, RTL direction detection, `prefers-reduced-motion` and `prefers-contrast`.

A dedicated build/package workflow is validating that these bytes are actually packaged into native API-36 APK candidates. Until that workflow passes and physical-phone evidence exists, status remains `PENDING / NOT_FINAL`.
