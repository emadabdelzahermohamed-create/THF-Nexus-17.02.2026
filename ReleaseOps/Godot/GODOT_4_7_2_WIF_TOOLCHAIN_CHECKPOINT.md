# Godot 4.7.2 WIF Toolchain Checkpoint

Date: 2026-09-12
Status: PASS
Scope: THF release builder tooling only. WAVE_MAWJA source/runtime untouched.

## Verified upstream artifacts

- Godot editor release: `4.7.2-stable`
- Editor archive: `Godot_v4.7.2-stable_linux.x86_64.zip`
- Editor archive SHA-256: `cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4`
- Export templates archive: `Godot_v4.7.2-stable_export_templates.tpz`
- Export templates archive SHA-256: `f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011`

## Builder verification

GitHub Actions run: `34676204614`
Authentication: GitHub OIDC -> GCP Workload Identity Federation -> IAP/OS Login
Persistent cloud key: NOT USED

Godot reported version:
`4.7.2.stable.official.ed1daf0bf`

Installed paths for the WIF OS Login account:

- `$HOME/.local/bin/godot-4.7.2`
- `$HOME/.local/bin/godot` -> symlink to the verified editor
- `$HOME/thf-tools/godot/4.7.2-stable/godot` (compatibility path consumed by Terra/Rift release gates)
- `$HOME/.local/share/godot/export_templates/4.7.2.stable/`

Verified installed SHA-256 values:

- Godot editor binary: `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`
- `android_source.zip`: `a15416b528efb0a19a7d187e4d9f4e5336d0689144b111329fb4bd12c4447ad3`
- `android_debug.apk`: `59e0073f0fa59f552684a861d8f4266b0b34b488a140d6657eac7dd70d1a0a0d`
- `android_release.apk`: `6d1bb2cfa126a1b1c87e064a35b3cbd181bef0ec784dec1efd1d64dffa8be6cb`

Gate assertions:

- `GODOT_472_TOOLCHAIN_INSTALL=PASS`
- `TERRA_RIFT_GATE_PATH_COMPAT=PASS`
- `WAVE_UNTOUCHED=TRUE`

## Safety / reversibility

Templates are installed into the release-builder user's local Godot data directory. Existing template directories are moved to timestamped `.prev.*` paths before replacement. Canonical Terra/Rift archives are not modified. No production signing, Google Play publishing, Cloudflare production cutover, Solana/token financial action, or destructive cloud action is performed by this checkpoint.

## Next gate

Resume the latest canonical Terra RC34 and Rift RC37 deterministic Android API 36 test-AAB export gates. Preserve canonical source SHA verification and unsigned/test-only release policy. Any failure after this checkpoint is no longer attributable to a missing Godot 4.7.2 editor or export-template installation.
