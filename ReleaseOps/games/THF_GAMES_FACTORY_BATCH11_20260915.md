# THF Games Factory Batch 11 — 2026-09-15

## Result

Latest-authority reconciliation completed. FINAL/PLAY_READY remains FALSE and physical-device evidence remains PENDING.

## Authority retained

- THF World / Terra: RC34 Phone V4; source SHA-256 `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`; eligible QA APK `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`.
- THF Arena / Rift: `4.7.5-rc41`; source SHA-256 `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`; no eligible APK until exact RC41 bytes are staged and built. RC37 is rejected as superseded.
- THF Learn Games / Spark: APPS RC4 + real-game overlay; source SHA-256 `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`; eligible APK `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`.
- THF Motion Games / Rush: APPS RC4 + Native Verified-Motion V2 + product identity fix; source SHA-256 `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`; eligible APK `f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f`.

## Engineering delta

`ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json` was stale and still promoted superseded Terra, Rift RC37 and pre-Verified-Motion Rush APKs. It has been reconciled with `ReleaseOps/games/LATEST_GAME_AUTHORITY_V1.json`.

The registry validator is now fail-closed for the Rift no-candidate state: Rift may have a null APK only while its status is explicitly BLOCKED, preventing an older RC37 APK from being silently restored. Artifact provenance validation is conditional on an artifact actually being referenced, so authoritative candidates without retained GitHub artifact IDs remain representable without inventing evidence.

Historical Terra/Rift/Rush APK hashes were added to the rejected set. No validated content or real asset was removed; no arbitrary artifact-size cap was reintroduced.

## Remaining hard gates

1. Stage exact Rift RC41 canonical archive bytes, then run Godot 4.7.2 fresh import/headless/parser and API36 arm64 packaging. Do not substitute RC37.
2. Physical Android phone evidence for exact eligible candidates: install/cold launch, touch, orientation, background/resume, offline/network behavior, crash-free logcat, avatar/player load, movement/camera/core gameplay and FPS/RAM/thermal.
3. Rift additionally requires real combat state transition evidence; Rush requires verified sensor-motion evidence, and reward-bearing health/economy state remains backend/provider authoritative.

No production signing, Play publication, Cloudflare cutover, Solana/token mutation, canonical archive overwrite or WAVE_MAWJA modification occurred.
