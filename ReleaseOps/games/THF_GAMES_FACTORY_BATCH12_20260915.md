# THF Games Factory — Batch 12 — 2026-09-15

Status: NOT_FINAL / PHYSICAL_DEVICE_PENDING

## Lineage proof
- Started from games checkpoint `ec6483bacb09707102ba32b8db76d61e62984cd8`.
- Current HEAD before this batch was `e11a47b135ba92e63cf1ef8864920c4aa5a7ed8b`.
- Compare showed exactly five intervening commits, all Shared Integration V7 / Apps identity work; no game source, game authority, game candidate, or game asset files changed.
- Therefore previously proven exact-candidate gates were not rerun for unchanged bytes.

## Current game authority preserved
- THF World / Terra: RC34 Phone V4; eligible QA candidate unchanged.
- THF Arena / Rift: 4.7.5-rc41 only; no eligible Android candidate; older RC/APK remains rejected.
- THF Learn Games / Spark: APPS RC4 + real-game overlay; eligible QA candidate unchanged.
- THF Motion Games / Rush: APPS RC4 + Native Verified-Motion V2 + product identity fix; eligible QA candidate unchanged.

## New work
Added `ReleaseOps/games/game_integration_v7_gate.py` to fail closed if Shared Integration V7 regresses game-critical identity/health boundaries. It pins approved names/package IDs, API 36/arm64 requirements, Rift RC41/no-stale-APK truth, Rush verified-motion + reward-bearing health-evidence requirements, and NOT_FINAL/physical-device-pending truth.

## Authority boundaries
- Manual activity is never accepted as verified motion/health evidence.
- Client-local motion practice remains non-authoritative for rewards/economy/ranked state.
- Reward-bearing health evidence remains provider/backend-authoritative.
- Online ranked/social/economy/world mutation remains backend-authoritative.

## Blockers intentionally not faked
1. Rift RC41 exact canonical archive bytes are still required before fresh Godot 4.7.2 import/headless/API36 arm64 candidate construction.
2. Physical Android device evidence is still required for exact-candidate install/launch/touch/orientation/background-resume/offline-network/core-gameplay/crash-free/FPS/RAM/thermal validation.
3. Production signing / Play publishing remain separate user/provider gates.

No validated content or uploaded real assets were removed. No 100 MB internal size ceiling was reintroduced.
