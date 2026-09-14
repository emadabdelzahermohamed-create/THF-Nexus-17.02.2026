# THF Games Large-Batch Checkpoint — 2026-09-14 06:10 EET

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING
Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games, shared source-lock and physical-device evidence systems.

## Authoritative state recheck

The current game candidate registry and preceding 05:10 checkpoint were re-read before engineering work. No APK candidate bytes changed, so previously proven Godot 4.7.2, parser/import/headless, Android/API36/package, payload, avatar/MPFB/MakeHuman/UAL, locomotion/camera/touch, sensor-landscape/expand, asset provenance, server-authority, anti-cheat and offline/local gates were not repeated for the same SHA.

Exact APK candidates remain:
- Terra: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games: `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games: `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

Registry truth remains `final_or_play_ready=false`, `physical_device_status=PENDING`.

## New authoritative-source lock

Added:
- `ReleaseOps/validators/validate_game_authoritative_source_lock_v1.py`
- `ReleaseOps/validators/test_validate_game_authoritative_source_lock_v1.py`
- `.github/workflows/thf-game-authoritative-source-lock-v1.yml`

Purpose: fail closed if the exact source bytes currently designated authoritative no longer match the source SHA recorded for any of the six current device candidates. The workflow is read-only, uses WIF/OIDC, Drive read-only for Spark/Rush RC4 and IAP to the isolated builder for Terra/Rift/Learn/Fitness, verifies ZIP integrity, preserves WAVE isolation, and explicitly cannot promote FINAL/PLAY_READY.

Observed authoritative source SHAs:
- Terra RC34: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`
- Rift RC37: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
- Spark RC4: `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`
- Rush RC4: `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`
- Learn Games outer source: `ce8547851c9573db02603ea6f11e020a1b7d346af0cac51e07947304f1a7c1f9`
- Fitness Games outer source: `cf5d73c3a03ab503dbd7c36a2d4db3ec1449ec8281304627b9463e2cb8732a25`

All six matched the current candidate registry and all six ZIP integrity checks passed.

Run `34801993923`: SUCCESS.
Artifact `THF-GAME-AUTHORITATIVE-SOURCE-LOCK-V1`:
- ID `10331118724`
- digest `sha256:6e91c294c8dfc0841eb21b01b73a0951931ca94ea8143a707fad7a87642a9a29`
- expires `2026-09-28T03:16:14Z`

Two earlier attempts in this batch failed only in new workflow parsing, not source validation: the first ingested SSH key-setup stdout into TSV, and the second used a `grep` tab expression that did not match a literal tab. The final implementation structurally filters TSV with `awk -F '\t'` and requires exactly the four builder records plus the two Drive records. No game/source bytes were changed to make the gate pass.

Relevant commits:
- `e660a2e3cc85b76c94731662dabad99264ba37ad` validator
- `0f0fb4685b1a7f7416132c90c976b0bc8cd95975` regression tests
- `8ced50064506f240ad2716fe3b04d71b090b27ee` initial workflow
- `d9ddb241ca2df6246418cd28d934d826361e47c8` SSH-output parser repair
- `606530ca5fc4c66c9541cb94dc1673cafdcc4d95` structural TSV parser / final successful run

## Physical-device evidence V4 hardening

Added:
- `ReleaseOps/mobile/validate_game_device_evidence_v4.py`
- `ReleaseOps/mobile/test_validate_game_device_evidence_v4.py`
- `.github/workflows/thf-game-physical-device-evidence-tooling-v4.yml`
- `ReleaseOps/games_factory/PHYSICAL_DEVICE_ACCEPTANCE_V4_20260914.md`

V4 keeps all V3 protections and closes a remaining evidence-integrity weakness. Manual PASS can no longer be satisfied by a plausible-looking `evidence_ref` string. Every required manual observation must now point to a safe relative path inside the evidence bundle; the file must exist, be non-empty and match its recorded SHA-256. Absolute paths and `..` traversal are rejected, as are missing files, empty files and evidence modified after capture.

V4 also requires concrete hash-bound device-session evidence for the authority boundary itself:
- `authority_observations.online_authority_behavior`
- `authority_observations.local_mode_truth`

Therefore the existing booleans `online_state_not_faked=true` and `local_mode_genuinely_local=true` are necessary but no longer sufficient for physical acceptance.

Latest V4 regression Run `34802054855`: SUCCESS. Coverage includes all six products plus missing-file, tampered-file, path-escape, empty-file, missing online-authority evidence and tampered local-truth evidence cases. The workflow also asserts the registry remains `PHYSICAL_DEVICE_PENDING` and `final_or_play_ready=false`.

Relevant commits:
- `db453b70206c3888f7ca98ce6cf6f525d8ded1b6` V4 validator
- `74e2a541f20a5ca972f41ffa7276dd4153a97c13` initial V4 tests
- `bce81b27e5419176ae9b1a475d119e38fb05358b` V4 CI
- `2c8797af1f96de87253ed86321d1b6aa11e70376` hash-bound online/local authority evidence
- `df3d634ee0f87237f7a183de83b430d81e21ca26` authority evidence regressions
- `99fd448f28a6b353361eea64aef04f130083c53e` V4 physical acceptance protocol

## Preserved release truth and remaining blocker

No candidate APK was rebuilt because neither its registered source SHA nor candidate APK SHA changed. No UI-only/template/fallback candidate was promoted.

All six candidates remain NOT_FINAL / PHYSICAL_DEVICE_PENDING. The remaining non-substitutable gate is a real physical Android phone running the exact registered APK bytes, with hash-bound V4 evidence for install/cold launch, touch, orientation/safe area, same-PID background/resume, offline/network transitions, gameplay, crash-free behavior, FPS/RAM/thermal observation and online/local authority behavior. Terra/Rift additionally require avatar/player load, locomotion, camera and world/NPC interaction; Rift requires combat; Rush/Fitness require real sensor motion and repetition counting; Spark/Learn require real learning progression.

No production signing, Play publishing, Cloudflare production cutover, Solana/token action, canonical archive overwrite or destructive cloud operation occurred. WAVE_MAWJA remained isolated.
