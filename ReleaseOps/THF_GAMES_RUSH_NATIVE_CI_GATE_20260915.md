# THF Games — Rush native verified-motion CI checkpoint — 2026-09-15

Status: **NOT_FINAL / PHYSICAL_DEVICE_PENDING**

This checkpoint records only new evidence for the current authoritative game lineages. No older RC, stale asset set, wrapper APK, production signing, Play publishing, production cutover, token/economy mutation, canonical archive overwrite, or WAVE mutation is authorized or claimed.

## Latest-authority/no-regression precondition

Before editing, main HEAD was `f7bc8c405f89c7f84499e96b7a96baedf4ad1ae6`; the only commit after the previous Games checkpoint `f0344ca8b6df4707a1a5c8f022f5d461646af339` was Pulse-only and did not change a game source/candidate SHA.

Current authoritative game state therefore remains:

- THF World / Terra: source SHA-256 `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`; eligible QA APK SHA-256 `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`.
- THF Arena / Rift: `4.7.5-rc41`; source SHA-256 `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`; eligible APK remains `NONE`; RC37 and earlier remain superseded.
- THF Learn Games / Spark: source SHA-256 `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`; eligible QA APK SHA-256 `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`; package `com.topherofit.thf.spark`.
- THF Motion Games / Rush: source SHA-256 `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`; package `com.topherofit.thf.rush`. The prior APK SHA-256 `528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7` remains rejected for product-icon acceptance and is not promoted.

## New CI coverage added

Commit `6a07c106c94171912836a6a9f9f785e9d2ef8cb9` extends `.github/workflows/thf-rush-verified-motion-v2.yml` to gate the native Android overlay `ReleaseOps/games_factory/strengthen_rush_native_motion_v2.py` in addition to the HTML/local-practice overlay.

The gate now verifies:

- Python syntax for the native overlay.
- Android `SensorEvent` identity must match the registered accelerometer.
- at least three finite sensor axes are required.
- sensor timestamps must be positive/monotonic before local repetition state advances.
- manual activity values cannot advance repetitions.
- touch cannot increment repetitions.
- local repetitions do not authorize rewards.
- reward-bearing health evidence remains `BACKEND_REQUIRED`.
- approved user-facing name is `THF Motion Games`.
- package ID remains `com.topherofit.thf.rush`.
- both normal and round launcher icons are bound to `@drawable/thf_motion_games_icon`.
- launcher icon SHA is emitted by the overlay evidence.
- canonical archive mutation remains false.
- final state remains `NOT_FINAL`.

## CI evidence

The connector-generated push triggered Actions correctly.

- `THF Rush Verified Motion V2` run `34898842375`: **SUCCESS** on exact commit `6a07c106c94171912836a6a9f9f785e9d2ef8cb9`.
- `THF Games Latest Authority V1` run `34898842353`: **SUCCESS** on the same exact commit, so the new native gate did not regress the current Terra/Rift/Spark/Rush authority baseline.

This is source/contract CI evidence only. It does not replace an exact rebuilt Rush APK package/icon inspection.

## Remaining exact blockers

1. **Rush:** rebuild an exact RC4 disposable candidate with the native V2 overlay, then inspect the produced APK itself for API36/arm64, signature/installability, package ID, product name, non-empty product-specific launcher icon and exact APK SHA. The old iconless APK remains rejected.
2. **Rift RC41:** exact canonical RC41 ZIP/split-part bytes are still unavailable to the builder, so fresh Godot 4.7.2 import/headless plus API36 arm64 packaging may not substitute RC37 or an older artifact.
3. **All games:** exact-candidate physical Android evidence is still mandatory before FINAL/PLAY_READY: install/launch/touch/orientation/safe-area/background-resume/offline-network/crash-free behavior, avatar/player load, movement/camera/gameplay, product-specific combat/learning/motion behavior, and FPS/RAM/thermal observation.

`FINAL_OR_PLAY_READY=FALSE`
