# THF Games Large-Batch Autonomous Checkpoint V3 — 2026-09-13

## Scope and safety
This checkpoint covers THF Terra / Nexus World, THF Rift / Nexus Arena, THF Spark, THF Rush, Learn/Fitness game-like streams, and shared release tooling. WAVE_MAWJA remains technically isolated. No production signing, Google Play publishing, Cloudflare production cutover, Solana/token financial action, destructive cloud operation, persistent cloud key, or canonical-source overwrite/delete was performed.

`FINAL` / `PLAY_READY` remains prohibited until exact-candidate physical-phone evidence exists for install, launch, touch, orientation/layout, background/resume, offline/network transitions, core gameplay, crash-free smoke, and (for games) real player/avatar load, movement, camera/gameplay/combat where applicable plus FPS/RAM/thermal observation.

## Authoritative-source update: Spark / Rush moved to APPS-RC3
Main commit `2b534c2c0883df4bf77be164b16e13c6cce01b8d` introduced the authoritative APPS-RC3 Drive/WIF/IAP exact-source workflow. It defines and verifies the current canonical candidates:

- Spark APPS-RC3 source SHA-256: `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0`, package `com.topherofit.thf.spark`.
- Rush APPS-RC3 source SHA-256: `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b`, package `com.topherofit.thf.rush`.

GitHub Actions run `34770503751`, attempt 2, has already passed **Download and verify authoritative APPS-RC3 sources** using short-lived WIF credentials and Drive read-only access. At this checkpoint the isolated-builder staging/build portion is still in progress, so no RC3 APK/package result is claimed yet.

The older Spark/Rush RC2 evidence remains historical evidence only and must not supersede RC3. Its proven QA-only local-practice candidates were:

- Spark RC2 source SHA `6b74f8d75df8c0b7f74d8c2fee8be7e3517f3803cb42968735bc7a10939bc18c`; QA APK SHA `35d1f481aa28acb9c99af16d5df7a87435c02a42027acf2deb21aa721a6282a1`.
- Rush RC2 source SHA `bb6ff035186b13cdde853145f42e66259c205889de2a7b368da34c9cb0582ba7`; QA APK SHA `5e3b1f8f6c7726d8e0d83f5ad6284a0a8657692e537c2565832789b2934f61de`.

For both RC2 local-practice candidates, package/runtime evidence proved targetSdk 36, packaged local game loop, touch input, local player state, no ranked/economy/fitness-evidence writes, QA-only signing and unchanged canonical archives. They remain `device_status=PENDING` and `NOT_FINAL`. Their old workflow red status was a truth-gate counting false negative, not a build/package failure.

## Terra / Rift staging QA package truth
Run `34769408210` produced both disposable staging APKs successfully and uploaded artifact `THF-TERRA-RIFT-STAGING-QA-APKS-V1` (artifact ID `10321397268`, uploaded artifact digest `287f3348489c48b816211c4c48ff37fc8f8455e47f65f5509bee79b6d8aa952e`). The build, retrieval, and artifact-upload steps all passed. Its final CI step failed only because the shell gate expected exactly two occurrences of repeated truth markers even though layered evidence printed each marker twice per game.

Verified candidate facts from that run:

- Terra canonical RC34 source remained SHA `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68` and unchanged. Staging QA APK SHA `409aa1efc12e10cd3acf962451b00348e8891c906164aacde9a988d208530963`; package `com.topherofit.thf.terra`; targetSdk 36; exported Godot payload PASS; QA signing only; device PENDING; NOT_FINAL.
- Rift canonical RC37 source remained SHA `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914` and unchanged. Staging QA APK SHA `ba094e2232d229cb93eda78c5e7da2c08e26a01a3015ccce4994bc8050c86480`; package `com.topherofit.thf.rift`; targetSdk 36; exported Godot payload PASS; QA signing only; device PENDING; NOT_FINAL.
- Staging HTTPS health passed. Endpoint value remained redacted. Production cutover/signing stayed false. WAVE files were not read or changed.

No same-SHA game rebuild was started merely to turn this historical false-red workflow green.

## CI truth-gate repair
To prevent duplicated layered evidence from causing future false negatives while still failing closed on missing or forbidden facts:

- `0ff3002cd7e3e1fb6e8ee29dfd88b999838fdb86` — added `ReleaseOps/scripts/kv_summary_gate_v1.py` with minimum-count requirements and forbidden-marker checks.
- `6f7f758353f34e7f28dd04586f6ea363de0c8933` — added regression tests for duplicated truth, missing truth, and forbidden production-signing truth.
- `b5ab669b6cea5be319fe164e7be43b1f6ddd394f` — added isolated CI workflow `ReleaseOps KV Summary Gate V1`.
- Run `34770929000` completed SUCCESS: syntax PASS and all regression tests PASS.

This repair is tooling-only and intentionally did not trigger redundant Terra/Rift or RC2 Spark/Rush rebuilds.

## Learn Games / Fitness Games
The last authoritative audits remain unchanged for their current known source SHAs: their thin source packages do not yet satisfy the real-function game contract (real locomotion/camera/touch/player/game loop coverage remains insufficient). They must not be promoted based on source/static/package-only checks. No fabricated wrapper/fallback is accepted as a game.

## Highest-priority next gates
1. Finish APPS-RC3 exact-candidate build/inspection already in progress and capture Spark/Rush RC3 APK SHA/package/API36/signature/non-debuggable evidence without reverting to RC2.
2. For Terra/Rift, preserve the proven staging package candidates and move to exact-SHA physical-phone acceptance; do not label FINAL before phone evidence.
3. Continue Learn/Fitness real-game implementation work only from their authoritative source lineage, with real input/player/game-loop wiring before packaging claims.
4. Keep online ranked/social/economy/world mutation backend-authoritative. Local practice/explore may remain genuinely local but must not synthesize online state.
5. Keep WAVE isolated and preserve all production/signing/financial/destructive safety boundaries.
