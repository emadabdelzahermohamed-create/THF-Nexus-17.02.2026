# THF Apps Factory — Locked Source Inventory V1

Date: 2026-09-13
Scope: Core/Pulse/Forge/Echo/Codex/Spark/Rush/Vault/Signal/Command/Pass only. Terra/Rift native-game work, WAVE and token finance excluded.

## Authority used

The active apps stream remains `APPS-RC1` / `CHECKPOINT_PASSED_SOURCE_STATIC_ANDROID_BUILD_EXTERNAL`. The APPS-RC1 source artifacts are the authoritative package-locked inputs unless a newer stream record explicitly promotes another source. Stage16-N/O/Q and APPS-RC1 PASS gates are deduplicated and are not re-run as release gates for unchanged source.

Locked APPS-RC1 source hashes:

| App | Package | APPS-RC1 source SHA-256 |
|---|---|---|
| Pulse | `com.topherofit.thf.pulse` | `a13bdceed8c1ad08436f2b4114dbf6017459107fb3239545194304f344ab4954` |
| Forge | `com.topherofit.thf.forge` | `8092c8d1d06ee8409d13a704e2c8c834db832a3a823be43487353a2a4d9dd188` |
| Echo | `com.topherofit.thf.echo` | `cb38e9c7be53578e6dbdd3e2b818ee981a8d80032ce113df144c62637594febd` |
| Codex | `com.topherofit.thf.codex` | `47e4b8eb70b3dd4894f7bb4e24e77c8ae58e8d277ddf90afb01ff3f6803fbcd5` |
| Spark | `com.topherofit.thf.spark` | `2b7149b22b2c4d198e36e99aa41a10bf72b400c279f1b7302d1cbb6275e4d03d` |
| Rush | `com.topherofit.thf.rush` | `fbfffef5475ebb51d8c75b242c8ec7a32646c02021372a20a978149c6070b341` |
| Vault | `com.topherofit.thf.vault` | `b4fb8ae79bfc174cf0131c90c735e512b6220466b156290dcc6a4750bd4d2aac` |
| Signal | `com.topherofit.thf.signal` | `15e3494c655e40959a8a8b77278d1a50ddb04388d503cc36a12724235640a697` |
| Command | `com.topherofit.thf.command` | `a549104e3a87374379889d119485e81cf585eca3f53b68a165be6b094ab65f48` |

Core has a newer separately-proven RC6 runtime candidate and is not rebuilt here. THF Pass remains backend/SDK-only with package identity `com.topherofit.thf.pass`; no Android/Play listing is invented.

## Builder inventory result

GitHub Actions run `34764353989` (`THF Apps Factory Locked Source Inventory V1`) completed PASS as a read-only evidence collection run. It did **not** find an exact byte-for-byte copy of any of the nine locked APPS-RC1 source archives in the service-account-owned builder home. Therefore no stale or approximate source was promoted to an exact candidate.

A different Pulse archive exists on the builder:

- `THF_PULSE_V4.1.0_SOURCE.zip`
- observed SHA-256 `31116912623767ebc2edcd56ad55fb2358a4cf398d2765f5eb1de9d842a75ad2`

This does not equal the APPS-RC1 Pulse source hash. It is recorded as **SOURCE_DRIFT_NEEDS_PROVENANCE**, not automatically promoted or merged. This prevents accidental regression or cross-stream substitution.

## Release truth boundary

- No source-only/static-only PASS is promoted to FINAL/PLAY_READY.
- No template/wrapper-only candidate is accepted as a real-function release.
- No production signing, Play rollout, billing/spend or irreversible deployment occurred.
- Exact-candidate APK/package inspection and physical-device acceptance remain mandatory before FINAL/PLAY_READY.
- Network-required flows must demonstrate reachable HTTPS/WSS health/auth; fake offline economy/social/ranked state is prohibited.

## Next executable work

1. Discover current package-bound Android workspaces and source archives on the authorized builder without modifying canonical source.
2. Resolve source provenance: APPS-RC1 exact source vs any newer stream-promoted source; never infer promotion from filename/version alone.
3. For each provenance-resolved source, create disposable build workspaces, run existing unit/integration tests, build API-36 QA candidates, and inspect exact package/payload/SHA/endpoints.
4. Keep Signal/Command internal-only and Pass backend/SDK-only.
5. Bind every built candidate SHA to the physical-device acceptance manifest before any FINAL/PLAY_READY state.
