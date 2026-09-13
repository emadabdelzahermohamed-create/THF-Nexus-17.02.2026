# THF Godot Runtime Checkpoint V1 — 2026-09-13

## Scope
THF Android/Godot runtime release path only. WAVE_MAWJA remains isolated and untouched. No canonical source archive was overwritten or deleted.

## Rift RC37 — PASS
GitHub Actions run: `34749952356`
Result: `success`
Artifact: `THF-Rift-RC37-RUNTIME-FIXED-APK`
Artifact id: `10315238482`
Artifact archive digest: `sha256:0534f44094c8f7c5e9337a71072217b8a8d383992f5008dad2713d503ec722fb`
Canonical source SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
Runtime-fixed APK SHA-256: `f13d1904e122cb335c8ae55ff18a2a5fe8d899929cfbee1f630c0b310c8b6347`
Package: `com.topherofit.thf.rift`
Version: `4.7.1-rc37` / versionCode `42071`
Target SDK: `36`
Godot payload: PASS (`asset_count=450`)
Signing: ephemeral QA recovery only (`qa_sign_recovery=true`); production signing was not performed.
Canonical archive mutation: false.
WAVE mixing: false.

## Terra RC34 — build contents valid, gate bug identified
GitHub Actions run: `34749952370`
Canonical source SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`
Observed before gate failure:
- Godot 4.7.2 import: PASS
- headless boot: PASS
- Android template install: PASS
- Android export: PASS
- unsigned APK recovery: PASS
- final apksigner verification: PASS (v2/v3)
- zipalign: PASS
- package: `com.topherofit.thf.terra`
- version: `4.6.8-rc34` / versionCode `42068`
- targetSdk: `36`
- APK contains a large populated `assets/` tree.

The failure was a CI false negative in `godot_payload_guard`: under `set -o pipefail`, the `unzip -Z1 | grep` pipeline can return non-zero when `grep` exits after an early match and `unzip` receives SIGPIPE. This produced `phase=godot_payload_guard rc=1` despite valid assets.

## Safe fix
Commit `738a7d1bdbc97f5c7849e3ca07a8506af1c65c77` replaces the payload probe with Python `zipfile` enumeration. The gate now records `asset_count`, `pck_count`, and `project_binary_count` deterministically without a SIGPIPE-prone pipeline.

New Terra run: `34752636192` (triggered automatically by the shared gate change). This is the next authoritative Terra result.

## Existing Core checkpoint
Core RC6 runtime-configured staging remains PASS from run `34743356308` with APK SHA-256 `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`. It still requires physical-device acceptance before Final status.

## PR / financial safety
PR #2 remains open and draft for isolated TokenOps. No Solana transaction, signing, burn, transfer, or authority action was performed.

## Next step
1. Complete Terra run `34752636192` and capture APK SHA/evidence if PASS.
2. Move Rift and Terra to physical-device install/runtime acceptance; neither is Final until this passes.
3. Keep Core on runtime/device acceptance and continue remaining THF apps through the same classified runtime gates.
4. Continue WAVE independently only from its latest canonical source; do not substitute an older WAVE source.

## Forbidden actions not performed
No production signing, Google Play publishing, Cloudflare production cutover, destructive GCP mutation, persistent cloud key use, Solana/token financial action, or canonical archive overwrite/delete occurred in this checkpoint.
