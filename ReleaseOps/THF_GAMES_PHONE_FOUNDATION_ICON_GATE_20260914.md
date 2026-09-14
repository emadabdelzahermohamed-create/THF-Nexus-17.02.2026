# THF Games phone-foundation checkpoint — 2026-09-14

Status: **NOT_FINAL / PHYSICAL_DEVICE_PENDING**

This checkpoint preserves latest-authority truth and records the product-identity defect found by direct inspection of the exact THF Motion Games candidate artifact. No production signing, Play publishing, production cutover, token/economy mutation, canonical-archive overwrite, or WAVE mutation is authorized or claimed.

## Latest authoritative lineage

- THF World / Terra: source SHA-256 `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`; eligible QA APK SHA-256 `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`; package lineage preserved.
- THF Arena / Rift: `4.7.5-rc41`; source SHA-256 `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`; eligible APK remains `NONE`. RC37 and earlier candidates remain superseded.
- THF Learn Games / Spark: source SHA-256 `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`; eligible QA APK SHA-256 `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`; package `com.topherofit.thf.spark`.
- THF Motion Games / Rush: source SHA-256 `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`; previously eligible QA APK SHA-256 `528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7`; package `com.topherofit.thf.rush`.
- Latest-authority validator run `34895081755` is PASS after stale operational Rift RC37 lanes were retired.

## Direct exact-artifact inspection — Rush V2

Downloaded GitHub Actions artifact ID `10368186302` and inspected the exact APK bytes rather than relying only on CI metadata.

Exact APK SHA-256 reverified:

`528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7`

Confirmed:

- package `com.topherofit.thf.rush`
- versionCode `36200`, versionName `3.6.2`
- compile/target SDK 36, min SDK 26
- user-facing label `THF Motion Games`
- native SensorManager/game-loop payload signals remain present
- manual/touch repetition increments remain rejected by the V2 source policy
- local repetitions remain non-rewarding; reward-bearing health evidence remains backend/provider required

New blocking defect found:

`aapt dump badging` reports `application: label='THF Motion Games' icon=''`.

Therefore the previous Rush APK is **not accepted as satisfying the approved product-specific icon requirement**, despite its package/signature/API36/game-payload PASS. It must not be promoted to FINAL/PLAY_READY.

## Repair applied

Commit `093e0596c5708c188bb842f8d878fb6c1e98d99d` updates `ReleaseOps/games_factory/strengthen_rush_native_motion_v2.py` so future exact RC4 disposable candidate trees:

- preserve package `com.topherofit.thf.rush`
- set user-facing name `THF Motion Games`
- create product-specific vector launcher resource `@drawable/thf_motion_games_icon`
- bind both `android:icon` and `android:roundIcon` to that resource
- record launcher-icon SHA-256 in evidence
- retain the verified SensorEvent identity/finite-axis/monotonic-timestamp gates
- retain `manual_activity_values_accepted=false`
- retain `touch_repetition_increment=false`
- retain `local_repetitions_reward_authorized=false`
- retain `reward_bearing_health_evidence=BACKEND_REQUIRED`
- never mutate the canonical RC4 archive

A rebuilt Rush candidate is required before the authority registry may replace APK SHA `528f7d...65ed7` with a new icon-correct exact SHA.

## Terra staging workflow authority hardening

Commit `35ce19c1dd1c6523d472fbae451455589ed69fc6` extends the Terra staging workflow trigger to include changes to `validate_latest_game_authority_v1.py` and binds its guard to the exact current Terra, Rift, Spark and Rush candidate/source state before remote staging. This prevents a staging run from silently accepting a later registry drift.

GitHub does not automatically start Actions from these connector-generated content commits, so no new build PASS is claimed for either commit. Re-running an older failed job is insufficient because GitHub reuses that run's historical head; this was verified and rejected as new evidence.

## Rift RC41 exact-artifact blocker

Library search again found RC41 validation/state/diff material proving deterministic ZIP SHA `29edaa0e...cb95d`, focused `40/40 PASS`, clean-extract `40/40 PASS`, and the two split-part hashes, but the actual canonical RC41 ZIP or split-part bytes are still absent from the accessible Library. Fresh Godot 4.7.2 import/headless and API36 arm64 packaging therefore remain blocked on **exact artifact staging**, and no older Rift source/APK may substitute.

## Finality boundary

All games remain `NOT_FINAL / PHYSICAL_DEVICE_PENDING`. Exact-candidate physical Android evidence is still mandatory for install/launch/touch/orientation/safe-area/background-resume/offline-network/crash-free behavior, plus player/avatar load, movement/camera/gameplay, product-specific learning/combat/motion behavior and FPS/RAM/thermal observations.
