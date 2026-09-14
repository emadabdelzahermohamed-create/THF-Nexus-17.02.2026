# THF Games Factory — Batch 10 Checkpoint — 2026-09-15

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING

## Latest authoritative game lineage

- THF World / Terra: RC34 Phone V4; canonical source SHA-256 `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`; eligible QA APK SHA-256 `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`.
- THF Arena / Rift: `4.7.5-rc41`; canonical source SHA-256 `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`; eligible Android candidate: NONE until exact RC41 archive bytes are staged and rebuilt. RC37 Android candidate is superseded.
- THF Learn Games / Spark: APPS RC4 + real-game overlay; source SHA-256 `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`; eligible candidate APK SHA-256 `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`.
- THF Motion Games / Rush: APPS RC4 + Native Verified-Motion V2 + product identity fix; source SHA-256 `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`; eligible candidate: NONE until a product-icon-correct rebuild completes. The prior APK SHA-256 `528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7` is explicitly rejected because packaged `aapt` identity showed an empty launcher icon.

## Batch changes

1. Release authority was corrected fail-closed so the rejected iconless Rush APK cannot remain an eligible candidate.
2. The latest-authority validator now distinguishes historical/audit references from actual promotion truth. A superseded hash may remain in evidence, but cannot be the registry candidate.
3. Android QA matrix was reconciled with the Rush rejection and rebuild requirement.
4. Rush candidate CI now performs exact RC4 SHA verification, safe clean extraction, real-game overlay, Native Verified-Motion V2, source contract audit, API 36 release build, QA signature, zipalign/apksigner verification, packaged-game-payload inspection and product launcher identity inspection.
5. Rush packaged launcher identity is proven by two independent checks: non-empty `aapt dump badging` application icon plus presence of `thf_motion_games_icon` in the packaged resource table. The workflow no longer assumes the badging icon path must preserve the source drawable name verbatim.
6. Terra staging authority guard was reconciled with the new Rush candidate truth and its expensive Godot/network workflow was decoupled from unrelated game-registry churn. It remains triggered by Terra/network implementation changes or explicit dispatch.

## CI evidence

- `THF Games Latest Authority V1` run `34904322614` on commit `a4a8e05f2b1f796b57e9d2a1fd692631b00f7cce`: SUCCESS.
- Rush rebuild run `34904322777`: in progress at checkpoint time. Exact RC4 clean extraction and Verified-Motion overlays are PASS; API36/package/signature/payload stage is still running. No candidate SHA is registered until every gate passes.
- Terra staging run `34904370227`: in progress at checkpoint time. Latest-authority guard, syntax, WIF auth, gcloud setup and staging of Terra validation tools are PASS; remote Terra Godot/network validation is still running.

## Rush evidence boundary

Rush local repetition input remains Android `SensorManager` / `SensorEvent` only, with registered sensor identity, finite 3-axis values and positive monotonic hardware timestamps. Manual activity values and touch cannot increment repetitions. Local repetitions cannot authorize rewards. Reward/economy/ranked paths remain backend/provider evidence gated.

## Physical-device gate

No connected Android device was available to the authorized execution environment in this batch. Therefore no new install/launch/touch/orientation/background-resume/offline-network/core-gameplay/crash-free/FPS/RAM/thermal evidence is claimed. `FINAL_OR_PLAY_READY=FALSE` remains mandatory for all four games.

## Remaining exact blockers

- Rift: stage the exact RC41 canonical archive bytes matching SHA `29edaa0e...cb95d`, then run fresh Godot 4.7.2 clean import/headless/export and API36 arm64 package/signature/installability gates. No older Rift RC may be substituted.
- Rush: allow run `34904322777` to finish; only a fully passing exact APK with non-empty product icon and exact SHA may become eligible for physical-device evidence.
- Terra/Spark: do not rebuild unchanged already-proven candidate bytes; next meaningful gate is physical-device acceptance unless their source/candidate SHA changes.

No production signing, Google Play publication, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite or WAVE_MAWJA modification was performed.
