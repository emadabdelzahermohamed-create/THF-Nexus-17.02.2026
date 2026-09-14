# THF Games Large-Batch Checkpoint — 2026-09-14 04:10 EET

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING
Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games and shared backend authority / anti-cheat systems.

## Starting authoritative state

The latest proven game authority work already included:
- authenticated role authority PASS on canonical runtime source SHA-256 `6abec6481f40272f6a847e8da4ef6890243d55243e6d88d806cde6bfa97ac046`;
- Arena same-action cross-user ownership PASS;
- exact physical-device candidate registry still marked `final_or_play_ready=false` and `physical_device_status=PENDING`.

No Godot, Gradle, API36, package, avatar or mobile-orientation gate was repeated for an unchanged candidate SHA.

## Candidate registry re-check

`ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json` remains unchanged and keeps these exact device candidates:
- Terra `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

Terra/Rift remain sensor-landscape + expandable-aspect candidates with no active desktop override. Rift still requires physical combat evidence; Rush/Fitness still require physical sensor-motion evidence.

## New anti-cheat semantic gate

Added `.github/workflows/thf-game-anticheat-semantic-v1.yml`.

Commit: `9f942ba1587d31f6a179b0e8144cb1352ed86bdd`
Workflow: `THF Game Anti-Cheat Semantic V1`
Run: `34795115347`
Result: SUCCESS
Artifact: `THF-GAME-ANTICHEAT-SEMANTIC-V1`
Artifact ID: `10328938714`
Artifact digest: `sha256:4be79e11a8cead087107ffc6afa3352408c9fe45bc81ac602bcc902c259b0b30`

The proof ran through WIF/OIDC -> GCP -> IAP against an isolated temporary copy/database of the canonical THF runtime, with external network blocked and without production credentials.

The gate proved:
- ephemeral user registration/login succeeds;
- a canonical Arena match can be started and a normal `advance` action succeeds;
- an invalid `teleport` action carrying forged `damage`, `score`, `hp` and `winner` fields is rejected;
- the rejected invalid action does not increment the owner's server-side action counter;
- an accepted canonical `advance` request carrying forged `damage`, `score`, `hp`, `winner`, `rewards` and `token_award` values advances the server action sequence by exactly one;
- the forged extreme client-authoritative values are not reflected into the returned authoritative state;
- canonical runtime Python source SHA is unchanged before/after the proof;
- WAVE remains unread/unchanged by this gate.

Truth boundary:
- `ANTI_CHEAT_SEMANTICS=PASS` for the tested Arena mutation semantics;
- this does not prove every future cheat vector, physical-input authenticity, device sensor integrity or production multiplayer latency behavior;
- it does not replace physical Rift combat/device evidence;
- `FINAL_OR_PLAY_READY=FALSE`.

## Preserved blockers

All six exact APK candidates remain `PHYSICAL_DEVICE_PENDING`.
Required evidence still includes exact-SHA install/cold-launch, real touch, orientation/safe-area, background/resume, offline/network transition, crash-free core gameplay and FPS/RAM/thermal observation. Terra/Rift additionally need physical avatar/player movement/camera/world evidence; Rift needs physical combat; Rush/Fitness need real sensor-driven repetitions; Spark/Learn need real learning-game progression.

Production signing, signed AAB, Play Internal approval, stable production HTTPS/WSS cutover and any user-only console/2FA/legal actions remain unproven/non-delegable.

No canonical archive was overwritten, no production signing or Play publish occurred, no Cloudflare production cutover or Solana action occurred, and WAVE_MAWJA remains isolated.
