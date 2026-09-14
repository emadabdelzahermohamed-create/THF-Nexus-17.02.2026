# THF Games Large-Batch Checkpoint — 2026-09-14 08:20 EET

Status: **ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING**

Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games, shared mobile/device evidence and release integrity systems.

## Authoritative state recheck

At the beginning and end of this batch, the current game candidate registry and latest game ReleaseOps checkpoints were read from `main`. No registered game source SHA or candidate APK SHA changed during this batch. Therefore previously proven Godot 4.7.2 parser/import/headless, Android/API36/package, game-payload, avatar/MPFB/MakeHuman/UAL, locomotion/camera/touch, sensor-landscape/expand, asset provenance, backend-authority, anti-cheat and offline/local gates were not repeated for the same SHA.

Exact candidate APKs remain:
- Terra: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games: `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games: `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

Registry truth remains `final_or_play_ready=false` and `physical_device_status=PENDING`.

## New gap found: pre-install SHA did not prove installed phone bytes

The existing physical-device collector correctly hashes the candidate APK before installation and binds evidence to the registered candidate. That still left one release-evidence gap: a pre-install hash alone does not cryptographically prove that the package bytes actually installed on the phone are those exact bytes.

This batch added Physical Device Evidence **V7**, extending V6 capture integrity and V5 single-session integrity with post-install APK byte identity.

Added:
- `ReleaseOps/mobile/validate_game_device_evidence_v7.py`
- `ReleaseOps/mobile/test_validate_game_device_evidence_v7.py`
- `ReleaseOps/mobile/capture_installed_apk_identity_v1.py`
- `ReleaseOps/mobile/test_capture_installed_apk_identity_v1.py`
- `.github/workflows/thf-game-physical-device-evidence-tooling-v7.yml`
- `ReleaseOps/games_factory/PHYSICAL_DEVICE_ACCEPTANCE_V7_20260914.md`

V7 now requires, fail-closed:
- the SHA-256 of the installed phone APK bytes equals `exact_candidate_sha256`;
- `pm path` resolves exactly one installed `/data/app/.../base.apk` rather than a split/multi-code-path candidate;
- the installed bytes are read through an approved byte-read path (`adb exec-out cat` or `adb pull`);
- the installed APK identity proof belongs to the same device session ID as the rest of the evidence;
- its observation timestamp is inside the declared physical-device session interval;
- the package dump exists as corroborating package-registration evidence;
- all V6 objective/performance capture-file hashes, V5 one-session checks, V4 evidence-file integrity checks, and earlier product-specific requirements continue to apply.

The capture helper additionally rechecks the connected physical phone fingerprint against the evidence bundle, rejects emulators, resolves the installed code path, streams `base.apk` bytes from the phone, hashes them, rejects a mismatch, appends an identity transcript to the objective evidence capture and updates that capture's SHA-256. It cannot promote readiness.

## Regression result

GitHub Actions Run `34809088502` — `THF Game Physical Device Evidence Tooling V7` — completed **SUCCESS**.

Successful steps included:
- validator/capture-helper compilation;
- V6 capture-integrity regression;
- V7 installed-byte regression across all six game products;
- installed-identity capture-helper regression;
- release-truth assertion that `PHYSICAL_DEVICE_STATUS=PENDING` and `FINAL_OR_PLAY_READY=FALSE` remain unchanged.

Negative regressions cover installed-SHA mismatch, false verification flag, split/multiple code paths, non-`/data/app` path, unapproved hash method, missing package dump, cross-session installed identity, installed-identity timestamp outside session, wrong connected phone fingerprint and installed-byte mismatch.

Relevant commits in this batch:
- `3e28be489dbddcdfe51bdb6ccf3d380bd0f0e8df` — initial V7 validator
- `d9a66dbd9f175ff7afb8933796087d65084fa712` — initial V7 regressions
- `e8ab08b2aee0ae3a97d969ad3236230783ce5ac3` — V7 CI
- `c48998739ffa0f7853c9cf1af5be01c174aacf80` — installed APK identity capture helper
- `3cce34cd373e5a2894c9bb6763131fd6ed5350ee` — capture-helper regressions
- `60b60a6603bafee08775c867f1641c96e9e91c04` — same-session binding for installed identity
- `58dc3b01d4ac80e922c6f5f108e326cba1295c6c` — same-session negative regressions
- `6a13d20a6b48f2d5be0105fc372c618b52957e8d` — CI exercises capture helper
- `3d0646df3f7926895e499434207e54448367c92b` — V7 physical acceptance protocol

## Preserved release truth / exact blocker

No game APK was rebuilt because neither registered source SHAs nor candidate APK SHAs changed. No UI-only/template/wrapper candidate was accepted.

All six candidates remain **NOT_FINAL / PHYSICAL_DEVICE_PENDING**. A real physical Android phone must still run the exact registered APK bytes and produce one-session, hash-bound evidence for install/cold launch, installed-byte identity, touch, orientation/safe area, same-PID background/resume, offline/network transitions, core gameplay, crash-free behavior, online-authority/local-mode truth, and FPS/RAM/thermal observations. Terra/Rift additionally require real avatar/player load, locomotion, camera and world/NPC interaction; Rift requires combat; Rush/Fitness require real sensor motion and repetition counting; Spark/Learn require real learning progression.

No production signing, Play publishing, Cloudflare production cutover, Solana/token action, canonical archive overwrite or destructive cloud operation occurred. WAVE_MAWJA remained isolated.
