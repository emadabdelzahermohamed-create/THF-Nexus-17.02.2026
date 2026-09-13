# THF Games Large-Batch Checkpoint — 2026-09-14 01:30 EET

Status: ACTIVE / NOT_FINAL / DEVICE EVIDENCE REQUIRED
Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games, shared game systems. WAVE_MAWJA remains technically isolated and was not modified.

## Safety / execution invariants
- Canonical source archives were never overwritten or deleted.
- WIF / short-lived GitHub OIDC credentials were used; no persistent cloud key was introduced.
- No production signing, Google Play publishing, Cloudflare production cutover, Solana/token financial action, destructive cloud mutation, or secret disclosure occurred.
- No source/static/build-only result was promoted to DEVICE PASS or FINAL/PLAY_READY.

## Authoritative source truth
- Terra / Nexus World: RC34 source SHA-256 `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68` — unchanged; previously proven Godot/mobile/package gates were not repeated.
- Rift / Nexus Arena: RC37 source SHA-256 `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914` — unchanged; previously proven Godot/mobile/package gates were not repeated.
- Spark authoritative source advanced from APPS RC3 to APPS RC4: SHA-256 `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`.
- Rush authoritative source advanced from APPS RC3 to APPS RC4: SHA-256 `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`.
- Learn Games and Fitness Games source/candidate bytes did not change; their already-proven build/package gates were not rerun.

## Critical RC4 regression caught — raw Spark/Rush are not game candidates
The existing `THF Spark Rush RC4 QA` path had previously passed package/signature/API36 checks, but packaged-payload inspection showed the raw RC4 APKs were only small WebView/offline shells (`assets/offline.html` + WebView/loadUrl markers) without the required packaged game loop.

Evidence:
- Raw RC4 source-contract run `34786350768`: fail-closed for both Spark and Rush on `timed_or_frame_loop_OR_render_or_motion`.
- Raw RC4 QA was strengthened with a packaged-payload gate. Run `34786573084` now fails intentionally with `THF_SPARK_RUSH_RC4_QA=REJECTED_WRAPPER_OR_MISSING_GAME_PAYLOAD`.
- Rejection artifact: `THF-SPARK-RUSH-RC4-QA-APKS`, ID `10327405066`, digest `sha256:cffc1c35cdee9f8ff159260cf6e6fe8ba12872e8abd22de0adb42fd6387c7d4d`.
- Therefore raw RC4 wrapper APKs are permanently ineligible for physical-device/Play readiness evidence.

## New fail-closed packaged-game APK gate
Added `ReleaseOps/validators/audit_game_apk_payload_v1.py` plus regression tests.
The gate rejects WebView/offline fallback wrappers unless the APK itself contains the required runtime signals:
- common game payload: frame loop + render + touch input,
- Spark/learning: learning state/progression,
- Rush/fitness: sensor runtime + fitness/repetition state.
It also exact-SHA locks the APK when requested and always leaves physical-device/final status pending.

Tooling regression run `34786503438`: SUCCESS after fixing a runner-only missing-pytest issue; gate semantics were not weakened.

## Spark/Rush RC4 real-game overlay — positive gate
The existing reversible real-game overlay was moved to the exact authoritative RC4 sources and rebuilt without modifying canonical archives.

Run `34786646013`: SUCCESS for both Spark and Rush, including:
- exact RC4 source SHA verification,
- clean ZIP extraction,
- real-game source contract,
- Android regression/lint tasks,
- release APK assembly,
- package identity,
- targetSdkVersion 36,
- APK ZIP integrity,
- new packaged-game-payload gate PASS,
- QA/non-production state retained.

Artifacts:
- Spark: ID `10326557577`, digest `sha256:4d86cb0245ce44da4dfbd3685e40109baadf98e9537665eda4bd2206a8709b28`.
- Rush: ID `10326522656`, digest `sha256:558c08392699a8f1257edbc26d7ea5ca189f1ddc26e328b1858d1221ba28ef37`.

Important byte-level reconciliation: authoritative RC4 + reversible real-game overlay reproduces the exact already-bound phone candidate bytes, so physical-device candidate SHAs remain unchanged:
- Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`.
- Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`.
This is a provenance correction/upgrade, not a new device candidate byte sequence.

## Current exact phone candidates
- Terra: `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`.
- Rift: `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`.
- Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`.
- Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`.
- Learn Games: `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`.
- Fitness Games: `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`.

## Backend-authority work
Existing read-only discovery run `34768073058` remains valid evidence that the THF runtime exposes game-related routes/symbols, with runtime-source SHA `6abec6481f40272f6a847e8da4ef6890243d55243e6d88d806cde6bfa97ac046`; it emitted no host values/secrets and read/changed no WAVE files.

A stronger static handler-authority audit was added to link sensitive mutation routes to auth/session/identity guard signals. The first two parser attempts correctly failed closed because the runtime's registration structure did not match decorator or `add_api_route(...)` assumptions. Latest run `34786785434` therefore remains a TOOLING/PARSER BLOCKER, not an application security PASS or FAIL. No authority claim is promoted from this incomplete static audit. Dynamic unauthorized-mutation rejection remains required before backend-authoritative readiness can be asserted comprehensively.

## ReleaseOps reconciliation
`ReleaseOps/ANDROID_QA_MATRIX_V1_20260913.md` was updated so Spark/Rush provenance points to authoritative RC4 sources while retaining the exact candidate APK SHAs above. It explicitly rejects raw RC4 wrapper APKs and requires packaged-game-payload inspection.

## Remaining hard gate
All six game/game-like candidates remain `PHYSICAL_DEVICE=PENDING` and `FINAL_STATUS=NOT_FINAL`.
Exact-SHA phone evidence is still mandatory:
- install + cold launch,
- touch / phone-safe layout / safe areas / orientation,
- background/resume,
- offline/network transition without fabricated online state,
- core gameplay and crash-free smoke,
- FPS/RAM/thermal observation,
- Terra: avatar/player load, movement, camera, world interaction/NPC where applicable,
- Rift: same plus real combat,
- Rush/Fitness Games: real sensor-driven movement/repetition behavior,
- Spark/Learn Games: real learning-game interaction/progression.

## Next safe work
1. Do not rebuild unchanged Terra/Rift/Learn/Fitness candidates solely to repeat PASS.
2. Continue backend-authority audit by adapting the parser to the actual route registration mechanism or use dynamic unauthorized-mutation tests; fail closed until resolved.
3. When a physical Android device is available, collect objective ADB evidence against only the exact candidate SHAs above, then complete the human-observed gameplay fields; do not fabricate device PASS.
