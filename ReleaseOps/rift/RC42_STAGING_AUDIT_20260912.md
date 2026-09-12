# Rift RC42 exact-staging audit — 2026-09-12

Scope: THF Rift only. Terra/Core/WAVE source untouched.

## Canonical state
- Latest GitHub ReleaseOps state: `RIFT-RC42-WEAPON-COMMAND-FAIL-CLOSED`.
- Version: `4.7.6-rc42`; versionCode `42076`.
- Expected canonical package: `THF_Rift_v4.7.6_RC42_WEAPON_COMMAND_FAIL_CLOSED_CUMULATIVE_SOURCE.zip`.
- Expected full SHA-256: `550c9d5b637d665b6cd835d4b85453a2430ef6b3f50d3d9a4008b248cb5cc95c`.
- Expected split part.00 SHA-256: `60689e0ee7ee92e753ab5d455e373b308c1950e496d2123fd10b3c89a59007a5`.
- Expected split part.01 SHA-256: `1488846af7b9c24a0bbf316612b3ced662e3b1bb2e52e2adc82ba0b1ad0efbac`.

## Existing source validation
- Focused tests: PASS 38/38.
- RC41 behavioral regression: PASS 40/40.
- Clean-extract gate: PASS 38/38.
- Python compileall: PASS.
- JavaScript syntax: PASS.
- ZIP integrity: PASS.
- Deterministic package: PASS exact SHA per RC42 ReleaseOps state.
- API36/AAB/arm64/unsigned policy metadata preserved.

## Exact-byte staging audit
The persistent Library was checked for the exact RC42 full archive and both exact split-part names. No RC42 byte artifact is currently addressable there. The newest addressable Rift package bytes are RC41 split parts:
- `THF_Rift_v4.7.5_RC41_SERVER_PICKUP_REACHABILITY_CUMULATIVE_SOURCE.zip.part.00`
- `THF_Rift_v4.7.5_RC41_SERVER_PICKUP_REACHABILITY_CUMULATIVE_SOURCE.zip.part.01`

Because RC42 is newer than the already-proven RC37 Android candidate, RC37 is not treated as current canonical for release readiness. RC42 is not reconstructed from older bytes or Git metadata; that would violate exact-source provenance.

## Blocker
Fresh Godot 4.7.2 parser/import/headless plus unsigned test-only Android API 36 AAB export for RC42 is blocked solely on availability of the exact RC42 canonical artifact bytes to the WIF/GCP staging path.

## Safety
- No canonical archive overwritten or deleted.
- No production signing.
- No Google Play upload/publish.
- No Cloudflare production cutover.
- No Solana transaction/financial action.
- WAVE_MAWJA untouched.

## Next
When exact RC42 bytes become addressable, verify split SHAs, reassemble and verify full SHA, then run fresh Godot 4.7.2 parser/import/headless and unsigned Android API 36 AAB export. Until then continue independent THF/WAVE gates rather than downgrading canonical Rift to RC41/RC37.
