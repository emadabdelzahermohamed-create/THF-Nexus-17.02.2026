# THF Games Factory — Batch 10 Checkpoint — 2026-09-15

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING

## Latest authoritative game lineage

- THF World / Terra: RC34 Phone V4; canonical source SHA-256 `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`; eligible QA APK SHA-256 `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`.
- THF Arena / Rift: `4.7.5-rc41`; canonical source SHA-256 `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`; eligible Android candidate: NONE until exact RC41 archive bytes are staged and rebuilt. RC37 is superseded.
- THF Learn Games / Spark: APPS RC4 + real-game overlay; source SHA-256 `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`; eligible APK SHA-256 `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`.
- THF Motion Games / Rush: APPS RC4 + Native Verified-Motion V2 + product identity fix; source SHA-256 `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`; eligible QA APK SHA-256 `f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f`. Previous APK `528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7` remains REJECTED as iconless.

## Completed batch changes

1. Corrected ReleaseOps authority so the rejected iconless Rush APK cannot remain eligible.
2. Corrected stale/superseded validation semantics: historical evidence may reference old hashes, but release authority cannot promote them.
3. Rebuilt Rush from the exact authoritative RC4 source with safe clean extraction, real-game overlay and Native Verified-Motion V2.
4. Passed API36 release build, QA signing, zipalign, apksigner, APK ZIP integrity and packaged-game-payload gates.
5. Passed independent packaged identity checks: `aapt` reports label `THF Motion Games`, non-empty launcher icon `res/Zg.xml`, and resource table contains `com.topherofit.thf.rush:drawable/thf_motion_games_icon`.
6. Registered exact Rush candidate provenance: workflow run `34904322777`, artifact `10371807756`, artifact digest `sha256:c158383f5b2183be0d677c65748376d44fc2f75a989f136ddfd62a126ab4f0d2`.
7. Reconciled the Android QA matrix and latest-authority CI to the new exact Rush candidate.
8. Decoupled the expensive Terra staging workflow from unrelated candidate-registry churn while retaining Terra/network implementation triggers.

## CI evidence

- Rush candidate run `34904322777`: **SUCCESS**. Exact APK SHA is `f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f`.
- Terra staging/network authority run `34904370227`: **SUCCESS**, including corrected authority guard and remote Terra validation path.
- Latest games authority run `34904647839`: **SUCCESS** after exact Rush candidate registration; `FINAL_OR_PLAY_READY=FALSE` remains enforced.

## Rush verified-motion boundary

Rush local repetitions consume native Android `SensorManager` / `SensorEvent` evidence with registered sensor identity, finite three-axis values and positive monotonic hardware timestamps. Manual activity values and touch cannot increment repetitions. Local repetitions cannot authorize rewards. Reward/economy/ranked paths remain backend/provider-evidence gated.

## Physical-device gate

No connected Android device was available to the authorized execution environment in this batch. Therefore no install/launch/touch/orientation/background-resume/offline-network/core-gameplay/crash-free/FPS/RAM/thermal PASS is claimed. All games remain NOT_FINAL / PHYSICAL_DEVICE_PENDING.

## Remaining exact blockers

- Rift: stage only the exact RC41 archive bytes matching `29edaa0e...cb95d`, then fresh Godot 4.7.2 clean import/headless/export and API36 arm64 package/signature/installability gates. Never substitute RC37 or older.
- Rush: next meaningful gate is physical-device acceptance using only APK SHA `f81ecebd...9072f` unless source/candidate bytes change.
- Terra/Spark: do not rebuild unchanged proven bytes; next meaningful gate is physical-device acceptance unless source/candidate SHA changes.

No production signing, Google Play publication, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite or WAVE_MAWJA modification was performed.
