# THF Games Large-Batch Checkpoint — 2026-09-14 02:25 EET

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING
Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games and shared game/runtime authority systems. WAVE_MAWJA remained technically isolated and was not modified.

## Same-SHA preservation
No previously proven Godot/import/export/package/API36 build was repeated for unchanged candidate bytes. Current exact phone candidates remain:
- Terra `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

## Backend authority blocker resolved dynamically
The prior raw-handler harness produced HTTP 500 because it instantiated `ThreadingHTTPServer` directly and bypassed the application's canonical runtime bootstrap. A safe AST-only runtime-shape inspection established that `thf.app` exposes `make_server(host, port, root, db_path)`, `run(host, port)`, `Runtime(root, db_path)` and `Handler`.

The dynamic authority harness was changed to use `make_server` on a temporary source copy, temporary SQLite DB/data/home, loopback-only networking and no production credentials. Canonical source is hashed before/after and is not modified.

Workflow `THF Game Backend Authority Dynamic V1`, run `34789521630`: SUCCESS.
Evidence:
- health status required and returned HTTP 200;
- 7/7 sensitive unauthenticated mutation probes returned fail-closed 401/403;
- covered world environment mutation, social position/send, avatar generation, arena start/action and economy internal award;
- `external_network_allowed=false`;
- `production_credentials_used=false`;
- `wave_files_read_or_changed=false`;
- canonical source unchanged;
- `FINAL_OR_PLAY_READY=FALSE`.

Artifact: `THF-GAME-BACKEND-AUTHORITY-DYNAMIC-V1`, ID `10327755583`, digest `sha256:8f537af7bee39e2a466f61102f1e5928f85318d7288f6bbd82274a899343abec`.

Runtime-shape workflow was also repaired to tolerate gcloud SSH-key-generation stdout noise by using bounded evidence markers. Run `34789544539`: SUCCESS. This tooling emits structural names only, not secret/environment values.

## Exact device candidate registry
Added `ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json` binding for every game candidate:
source version + source SHA -> package -> targetSdk 36 -> exact APK SHA -> workflow run -> artifact ID/digest -> product-specific device evidence requirements.

Fail-closed validator and regression tests enforce:
- exactly the six game/game-like candidates once;
- valid source/APK/artifact SHA-256 values;
- unique package/APK identities and targetSdk 36;
- Terra/Rift sensor-landscape + expand + inactive desktop override;
- Rift combat evidence requirement;
- Rush/Fitness sensor-motion evidence requirement;
- `PHYSICAL_DEVICE_STATUS=PENDING` and no FINAL claim;
- historical portrait/wrapper candidates cannot be rebound as current candidates.

Workflow `THF Game Device Candidate Registry V1`, run `34789500092`: SUCCESS, including all negative regression cases.

## Live artifact provenance
Added a read-only live GitHub Actions provenance gate. It checks each registry artifact ID against the GitHub Actions API and requires the recorded workflow run, artifact digest and non-expired status to match.

Workflow `THF Game Candidate Artifact Provenance V1`, run `34789570490`: SUCCESS for all six candidate bindings.
Artifact: `THF-GAME-CANDIDATE-ARTIFACT-PROVENANCE-V1`, ID `10327144981`, digest `sha256:5304621289ecedc6c590bdbb4f7dc8a668445e2534bfbc135b2b9337861d9904`.

## What this does and does not prove
Backend authority now has real dynamic evidence that the tested sensitive unauthenticated mutations fail closed under the canonical server factory. This materially closes the earlier parser/harness blocker. It does not prove every authenticated authorization rule, role boundary, anti-cheat decision or production deployment path; those remain separate gates.

No candidate is FINAL/PLAY_READY. Exact-SHA physical Android evidence remains mandatory for install/cold launch, touch, phone-safe layout/safe areas/orientation, background/resume, offline/network transition, core gameplay, crash-free smoke and FPS/RAM/thermal observation. Terra additionally needs real avatar/player load + locomotion + camera + world/NPC interaction; Rift needs those plus combat; Rush/Fitness need real sensor-driven movement/repetition; Spark/Learn need real learning-game interaction/progression.

## Safety
No canonical archive overwrite/delete, production signing, Play publishing, Cloudflare production cutover, Solana/token financial action, destructive cloud mutation or persistent cloud credential was used. WIF/IAP remained the cloud access path, and WAVE files were not read or changed by the game authority probe.

## Next safe engineering block
1. Extend dynamic authority from unauthenticated rejection into isolated authenticated/role-bound tests using ephemeral local identities, without external network or production credentials.
2. Add anti-cheat/server-authority mutation-semantic probes where the runtime supports deterministic temporary data.
3. Preserve current APK bytes unless implementation changes; when a physical Android device becomes available, collect objective ADB evidence and human-observed gameplay fields only against the exact registry SHAs.
