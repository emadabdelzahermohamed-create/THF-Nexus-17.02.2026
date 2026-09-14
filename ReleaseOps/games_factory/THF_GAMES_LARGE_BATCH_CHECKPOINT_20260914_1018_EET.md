# THF Games Large-Batch Checkpoint — 2026-09-14 10:18 EET

Status: **ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING**

Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games, shared game/mobile release evidence systems.

## Authoritative state recheck

Re-read current game candidate registry, latest games checkpoint and recent game commits before engineering. No source SHA or APK candidate SHA changed since V8, therefore no proven Godot 4.7.2 parser/import/headless, Android/API36/package, gameplay payload, avatar/MPFB/MakeHuman/UAL, locomotion/camera/touch, Terra/Rift sensor-landscape/expand, backend authority, anti-cheat, offline/local truth, installed-byte or V8 performance-provenance gates were repeated for identical SHAs.

Candidates remain: Terra `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`; Rift `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`; Spark `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`; Rush `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`; Learn Games `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`; Fitness Games `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`. Registry remains `final_or_play_ready=false`, `physical_device_status=PENDING`.

## New independent gap closed: crash-free claims were not byte-bound to logcat

Added Physical Device Evidence **V9**:
- `ReleaseOps/mobile/validate_game_device_evidence_v9.py`
- `ReleaseOps/mobile/test_validate_game_device_evidence_v9.py`
- `.github/workflows/thf-game-physical-device-evidence-tooling-v9.yml`

V9 layers on V8 and requires a non-empty hash-bound logcat evidence file from the same physical-device session and exact package. It requires an approved ADB logcat capture method, an interval inside the declared device session, the exact package identity inside captured bytes, `process_alive_after_core_gameplay=true`, and `crash_free=true`. It rejects SHA tampering, cross-session evidence, wrong package, package-absent logs and fatal markers including `FATAL EXCEPTION`, `AndroidRuntime`, `Fatal signal`, `ANR in`, `am_crash`, and `am_anr`.

The first CI run `34817072930` correctly failed because the positive fixture extended outside the declared device session. The fixture was corrected rather than weakening the validator. Final run `34817167353` completed **SUCCESS**: compilation PASS, V8 regressions PASS, V9 regressions PASS, release-truth preservation PASS.

Relevant commits:
- `90cae180bb4a2bf330ee9fe5ec5f521ff4f38a38` — V9 validator
- `1f8572d18490e1aa21a81746dc5bab23b5ef4353` — V9 regression suite
- `28b20bc67d8c52f3f8815a4915613a13eb08fb1f` — V9 CI workflow
- `cd7a6880046012157097bd382e5545d0777587aa` — fixture/session correction after fail-closed CI caught the invalid interval

## Preserved release truth

No APK was rebuilt because exact source/candidate SHAs did not change. No UI-only demo, engine/template APK, wrapper, placeholder endpoint, source/static/build-only PASS, fake online state or local substitute for server-authoritative online state was promoted.

All six remain **NOT_FINAL / PHYSICAL_DEVICE_PENDING**. Exact installed APK bytes still require one real physical-phone session proving install/cold launch, touch, orientation/safe area, same-PID background/resume, offline↔network transition, real core gameplay, hash-bound crash-free logcat, online-authority/local-mode truth and FPS/RAM/thermal. Terra/Rift additionally require avatar/player load, locomotion, camera and world/NPC interaction; Rift requires combat; Rush/Fitness require sensor motion and repetition counting; Spark/Learn require learning progression.

No production signing, Play publishing, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite or destructive cloud operation occurred. WAVE_MAWJA remained isolated.
