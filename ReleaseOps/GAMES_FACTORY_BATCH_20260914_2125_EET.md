# THF Games Factory — 2026-09-14 21:25 EET

## Scope
Large-batch game engineering checkpoint for Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn/Fitness Games and shared avatar/animation systems.

## Authority / dedupe
- Latest Rift authority is **4.7.5-rc41**, not RC37.
- Exact RC41 cumulative-source SHA-256: `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`.
- RC41 deterministic/source validation already records focused 40/40 PASS, clean-extract 40/40 PASS, Python/JS PASS and exact deterministic ZIP integrity PASS; these source-only gates were not repeated as if they were Godot/device evidence.
- Terra RC34 Phone V4 and unchanged Spark/Rush/Learn/Fitness candidates were not rebuilt solely to repeat existing PASS evidence for unchanged SHAs.

## RC41 remote execution truth
- Authority-discovery run `34875925243` successfully authenticated through WIF/IAP and reached the private builder, but its actual evidence says `exact_rc41_builder_bytes=MISSING` and `next_gate=STAGE_EXACT_RC41_BYTES`.
- Fresh RC41 source-preflight run `34879987920` correctly failed closed with exit code `20` because the exact source bytes were not present on the builder. Its evidence artifact is `10361999891`, digest `sha256:ded6b7ff5e7982fb3b360631282ddf6704ce96af1bd9fa91c4acec58db38284e`.
- ChatGPT Library was searched for the exact RC41 archive and both recorded part names. Validation/handoff/state evidence is present, but the actual RC41 source archive/parts are not available as materializable Library files. No substitute older source was promoted.
- Therefore no fresh RC41 Godot 4.7.2 parser/import/headless or API36 AAB PASS is claimed in this checkpoint.

## Global artifact-size policy
User upload-era arbitrary size limits are retired globally across THF apps and games.

Policy now enforced:
- artifact size is telemetry/optimization, not an internal release rejection criterion;
- validated content must not be pruned solely to satisfy an arbitrary internal size cap;
- lossless optimization and real external platform constraints remain allowed;
- a real provider constraint must be documented explicitly as `EXTERNAL_PLATFORM_LIMIT` rather than silently converted into content pruning.

Added:
- `ReleaseOps/scripts/validate_no_arbitrary_artifact_size_caps_v1.py`
- `.github/workflows/thf-no-arbitrary-artifact-size-cap-v1.yml`

The diagnostic gate identified a real executable legacy offender:
`ReleaseOps/scripts/build_pulse_mpfb_motion_phone.sh`.

That Pulse build script was repaired at commit `bcc469c82b1db7d5961f1c0b1712a0dec1722907`:
- removed the `104857600` hard rejection;
- removed `under_100MiB` as an acceptance requirement;
- preserves `apk_size_bytes` as telemetry;
- records `artifact_size_policy=TELEMETRY_ONLY_NO_ARBITRARY_CAP`;
- records `validated_content_pruned_for_size=FALSE`.

The policy workflow remains fail-closed and will identify any next executable legacy offender rather than suppressing the check.

## Truth boundaries / safety
- `FINAL_OR_PLAY_READY=FALSE`.
- Physical Android device acceptance remains pending.
- No production signing.
- No Play production publish.
- No Cloudflare production cutover.
- No Solana/token financial mutation.
- No canonical source archive overwrite/delete.
- WAVE_MAWJA was not modified.

## Next non-duplicate gates
1. Continue global executable size-policy scan until PASS, repairing each genuine legacy hard cap without removing validated content.
2. Stage exact Rift RC41 bytes when a trustworthy exact source artifact becomes available; then run fresh Godot 4.7.2 clean parser/import/headless plus API36 package/payload build gates.
3. Keep all games `NOT_FINAL / PHYSICAL_DEVICE_PENDING` until exact-candidate physical-phone evidence is captured under the existing strict device-evidence chain.
