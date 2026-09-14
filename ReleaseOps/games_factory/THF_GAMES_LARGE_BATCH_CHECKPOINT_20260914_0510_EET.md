# THF Games Large-Batch Checkpoint — 2026-09-14 05:10 EET

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING
Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games, shared authority/anti-cheat/offline systems.

## Authoritative-state recheck

The latest game checkpoint and `THF_GAME_DEVICE_CANDIDATES_V1.json` were re-read before work. No candidate source/APK bytes changed, so no previously proven Godot 4.7.2, Gradle, API36, package, avatar/UAL/MPFB, sensor-landscape or payload gate was repeated.

Exact device candidates remain:
- Terra `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

Registry remains `final_or_play_ready=false`, `physical_device_status=PENDING`.

## New dynamic world/economy/social semantic authority proof

Added `.github/workflows/thf-game-world-economy-semantic-v1.yml` at commit `086b69d93f1b8337d1428a1a4c9908dfedcdbd5e`.

Run `34798467300`: SUCCESS.
Artifact `THF-GAME-WORLD-ECONOMY-SEMANTIC-V1`:
- ID `10330054218`
- digest `sha256:a482ceeb76e53a677d6f79164b578933e1b9ffb5f007f3ac55503d82e6af57cb`

The proof used WIF/OIDC -> GCP -> IAP, an isolated temporary copy/database, canonical `make_server`, loopback-only networking, ephemeral users and no production credentials. It proved, for the tested canonical runtime:
- both users can authenticate normally;
- ordinary user cannot call `economy/internal-award` for self or another user with forged huge `amount/token_award/rewards` fields;
- both users' economy balance responses remain unchanged after those rejected attempts;
- ordinary user cannot mutate global world environment/weather/day-night/season state;
- when the world GET surface is available, rejected mutation does not alter the observed world state; mutation rejection remains required even if the read surface is unavailable;
- social position actor-ID injection is rejected or remains bearer-bound;
- social send sender-ID spoofing is rejected/invalid or remains bearer-bound;
- canonical Python source SHA remains unchanged, external network is blocked, WAVE is not read/changed.

Gate outputs: `WORLD_ECONOMY_SOCIAL_SEMANTICS=PASS`, `NO_PAY_TO_WIN_ECONOMY_SPOOF=PASS`, `FINAL_OR_PLAY_READY=FALSE`.

Truth boundary: this extends server-authority/no-pay-to-win semantic evidence but does not prove every economy/world/social vector, production multiplayer behavior, device authenticity or physical gameplay.

## New offline/local truth gate

Added:
- `ReleaseOps/validators/validate_game_offline_local_truth_v1.py`
- `ReleaseOps/validators/test_validate_game_offline_local_truth_v1.py`
- `.github/workflows/thf-game-offline-local-truth-v1.yml`

The gate audits the shipping disposable local overlay generators for Spark/Rush and Learn/Fitness and requires:
- explicit `LOCAL_ONLY_NO_RANKED_SOCIAL_ECONOMY_MUTATION` boundary;
- `READINESS_PROMOTION=NO`;
- local game view + frame loop + touch input;
- local progression (Spark/Learn) and sensor progression (Rush/Fitness);
- no HTTP/API/WebSocket/network transport in the local overlay generator;
- no SharedPreferences/SQLite/file persistence that could fabricate authoritative online state.

Initial run `34798523102` correctly failed due to a validator false-positive: Android's fixed manifest namespace `http://schemas.android.com/apk/res/android` was mistaken for network transport. The game overlays were not changed. The validator was corrected in commit `263781122d179fa839a75a89b5b0b7396265a7c2` to exclude only that exact standards namespace. Regression coverage was then expanded in `57d2359e2a0d978e698ddff837ae535b449f8350` so the Android namespace is allowed while any other HTTP(S) URL remains rejected.

Final run `34798602367`: SUCCESS.
Artifact `THF-GAME-OFFLINE-LOCAL-TRUTH-V1`:
- ID `10329824822`
- digest `sha256:32f8d858361f2ff37792222f336bd268b919b4d0bfb9c9115818eec6aa3f2e6d`

Truth boundary: `STATIC_LOCAL_OVERLAY_CONTRACT_ONLY_NOT_DEVICE_OR_PLAY_READY`. This gate protects against fake-online local modes but does not replace APK payload evidence or physical offline/network-transition testing.

## Preserved release truth

No APK bytes were changed during this batch. All six candidates remain NOT_FINAL / PHYSICAL_DEVICE_PENDING. Required exact-SHA physical-phone evidence still includes install/cold-launch, real touch, orientation/safe-area, true background/resume, offline<->network transition, crash-free core gameplay and FPS/RAM/thermal observation. Terra/Rift additionally require avatar/player load, movement, camera and world interaction; Rift requires physical combat; Rush/Fitness require real sensor-driven repetitions; Spark/Learn require real learning-game progression.

No production signing, Play publishing, Cloudflare production cutover, Solana/token action, canonical archive overwrite or destructive cloud action occurred. WAVE_MAWJA remained isolated.
