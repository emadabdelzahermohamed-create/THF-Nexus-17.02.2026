# THF Games Large-Batch Checkpoint — 2026-09-15 02:30 EET

## Scope
THF World/Terra, THF Arena/Rift, THF Learn Games/Spark, THF Motion Games/Rush.

## Latest-authority proof before edits
No game payload/source commit superseded the previous Games checkpoint. Current authoritative registry remains:

- Terra / **THF World** — `RC34 Phone V4`; source SHA `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`; eligible QA APK SHA `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`; canonical package `com.topherofit.thf.terra`, QA package `com.topherofit.thf.terra.phoneqa`.
- Rift / **THF Arena** — `4.7.5-rc41`; authoritative source/archive SHA `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`; eligible Android candidate **NONE**. RC37 and older are superseded/ineligible.
- Spark / **THF Learn Games** — `APPS RC4 + real-game overlay`; source SHA `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`; eligible QA APK SHA `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`; package `com.topherofit.thf.spark`.
- Rush / **THF Motion Games** — `APPS RC4 + Native Verified-Motion V2 + product identity fix`; source SHA `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`; eligible QA APK SHA `f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f`; package `com.topherofit.thf.rush`.

Global truth remains `FINAL_OR_PLAY_READY=FALSE`; all physical-device statuses remain `PENDING`.

## Meaningful engineering completed in this batch
The latest-authority validator previously pinned the exact Rush candidate and prevented a Rift candidate, but Terra and Spark candidate acceptance was only format/superseded-list checked. A different non-superseded SHA could therefore have entered the registry without an intentional authority migration.

Closed that fail-open:

1. `ReleaseOps/scripts/validate_latest_game_authority_v1.py`
   - Pins exact authoritative version, source SHA and eligible candidate SHA for all four products.
   - Pins Terra QA package ID.
   - Requires Rift candidate to remain `NONE` until an RC41 build exists.
   - Validates every superseded SHA format and rejects duplicates.
   - Rejects cross-product candidate-SHA reuse.
   - Requires the Android QA matrix to contain Terra and Spark exact candidate evidence in addition to existing Rift/Rush evidence.

2. `.github/workflows/thf-games-latest-authority-v1.yml`
   - Adds exact Terra candidate assertion: `e0ac997e...0cfbec`.
   - Adds exact Spark candidate assertion: `9fffc4d9...165ea`.
   - Retains Rift RC41-only / candidate `NONE` and Rush exact-candidate assertions.

Commits:
- `5dc0eb075a990b472876a2093fcc18245f67671a` — validator exact-candidate hardening.
- `621a7be15d6534fea24cc58f0faeacb85f69ef25` — CI exact Terra/Spark candidate assertions.

## CI evidence
`THF Games Latest Authority V1` run `34909052826`, job `104192229120`: **SUCCESS**.

Successful stages:
- checkout
- reject stale RCs, wrappers and superseded APKs
- preserve non-promotional exact authority evidence
- evidence artifact upload

This proves the stricter validator is consistent with the current authoritative registry; it does not constitute physical-device gameplay evidence.

## Rift RC41 exact-byte blocker rechecked
Library search reconfirmed RC41 authority and deterministic evidence:

- focused `40/40 PASS`
- clean-extract `40/40 PASS`
- deterministic rebuild exact SHA `29edaa0e...cb95d`
- ZIP integrity PASS
- API36/AAB/arm64 metadata preserved

However, only handoff/state/checksum evidence was available in the current accessible Library search; the exact RC41 ZIP or both split archive bytes were not retrieved. Therefore fresh RC41 Godot 4.7.2 parser/import/headless and API36 arm64 Android packaging remain blocked on exact artifact staging. No RC37/older fallback is permitted.

## No-repeat / preserved evidence
No unchanged Terra/Spark/Rush package or gameplay gate was rerun merely to repeat an existing PASS. Existing validated gameplay, real assets, MPFB/MakeHuman/UAL integration, local/online authority boundaries and no-pay-to-win constraints remain preserved.

## Release truth / external gates
No game is FINAL or PLAY_READY.

Still mandatory before such a label:
- exact-candidate physical-phone install/cold launch
- touch/orientation/safe-area and lifecycle/background-resume
- offline/network truth
- crash-free evidence
- product-specific core gameplay evidence
- avatar/player load, movement/camera where applicable
- Rift combat state change
- Spark learning progression
- Rush verified sensor-motion/repetition behavior
- FPS/RAM/thermal observation

No production signing, Play publication, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite, content pruning-for-size, or WAVE_MAWJA modification occurred in this batch.
