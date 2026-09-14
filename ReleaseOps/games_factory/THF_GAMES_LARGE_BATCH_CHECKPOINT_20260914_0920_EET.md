# THF Games Large-Batch Checkpoint — 2026-09-14 09:20 EET

Status: **ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING**

Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games, shared game/mobile release evidence systems.

## Authoritative state recheck

The current `THF_GAME_DEVICE_CANDIDATES_V1.json`, latest games checkpoint, and recent game commits were re-read from `main` before engineering work began. No source SHA or APK candidate SHA changed since the preceding V7 checkpoint, so previously proven Godot 4.7.2 parser/import/headless, Android/API36/package, gameplay payload, avatar/MPFB/MakeHuman/UAL, locomotion/camera/touch, Terra/Rift sensor-landscape/expand, asset provenance, backend authority, anti-cheat, offline/local truth, and installed-byte identity gates were not rerun for identical SHAs.

Exact candidates remain:
- Terra `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

Registry truth remains `final_or_play_ready=false` and `physical_device_status=PENDING`.

## New independent gap closed: typed performance claims were not value-bound to capture bytes

V6 required objective/performance evidence files to exist and be SHA-256 bound. V7 additionally proved installed APK bytes. A remaining evidence-integrity gap was that the typed `fps_observed`, `ram_mb_observed`, `thermal_status_observed`, and `observation_seconds` JSON values could still diverge from the hash-bound performance evidence file.

This batch introduced Physical Device Evidence **V8**:
- `ReleaseOps/mobile/validate_game_device_evidence_v8.py`
- `ReleaseOps/mobile/test_validate_game_device_evidence_v8.py`
- `.github/workflows/thf-game-physical-device-evidence-tooling-v8.yml`

V8 is layered on V7 and is fail-closed. It requires:
- performance provenance to bind to the exact objective evidence SHA-256;
- RAM provenance to use `dumpsys meminfo` TOTAL PSS and equal objective `total_pss_kb`;
- typed RAM MB to derive from the objective PSS value;
- FPS provenance to use an approved runtime source and bind the same objective framestats row count;
- thermal provenance to use `dumpsys thermalservice` with the objective thermal snapshot present;
- the provenance record to use the same physical-device session ID;
- the hash-bound performance file to contain one canonical machine-readable value for FPS, RAM MB, thermal status, observation seconds, objective evidence SHA and session ID;
- typed JSON FPS/RAM/thermal/duration values to match those hash-bound file values;
- duplicate canonical metrics, missing metrics, cross-session metrics, or an objective-SHA mismatch to fail.

This does not impose arbitrary performance thresholds; it strengthens provenance and truthfulness of observations.

## Regression evidence

Initial V8 CI Run `34812835320` completed SUCCESS. During review, the gate was strengthened further so that the values themselves, not only the declared sources, must match machine-readable metrics inside the hash-bound performance capture.

Final strengthened CI Run `34812938618` completed SUCCESS. The job passed:
- validator compilation;
- V7 installed-byte regressions;
- V8 performance-provenance regressions across all six products;
- release-truth preservation.

Negative regressions include missing provenance, wrong objective capture SHA, arbitrary RAM value, PSS-source mismatch, framestats-source mismatch, unapproved FPS method, missing thermal source, cross-session provenance, typed FPS mismatch against the hash-bound capture, typed thermal mismatch, performance-capture objective-SHA mismatch, and duplicate canonical metrics.

Relevant commits:
- `bb151f31cd7b4fde7a9b33eaffba028f4c16ce82` — V8 validator
- `e077fad603650af4ba894d80c4d253f3de7136c4` — initial V8 tests
- `2e01bf4a6265d630c371c24d2aefac5e0cfb7ac3` — V8 CI
- `686b211c8a7ad05a5121e995cd60e359dddfa130` — require machine-readable performance capture metrics
- `812ed833eb52de4a79321f300f78d8d83b81b89f` — strengthened V8 negative/positive regressions

## Preserved release truth / remaining exact gate

No APK was rebuilt because candidate/source SHAs did not change. No UI-only demo, wrapper, engine-only APK, placeholder endpoint, source/static-only PASS, fake online state, or local substitute for server-authoritative state was promoted.

All six candidates remain **NOT_FINAL / PHYSICAL_DEVICE_PENDING**. A real physical Android phone must still execute the exact registered installed bytes and produce one-session evidence for install/cold launch, installed-byte identity, touch, orientation/safe area, same-PID background/resume, offline↔network transition, core gameplay, crash-free behavior, online-authority/local-mode truth, and real FPS/RAM/thermal observations. Terra/Rift additionally require avatar/player load, movement, camera and world/NPC interaction; Rift requires combat; Rush/Fitness require sensor motion and repetition counting; Spark/Learn require learning progression.

No production signing, Play publishing, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite, or destructive cloud operation occurred. WAVE_MAWJA remained isolated.
