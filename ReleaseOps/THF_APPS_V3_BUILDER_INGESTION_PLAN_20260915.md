# THF Apps V3 Builder Ingestion Plan — 2026-09-15

Scope is limited to Forge, Echo, Codex, Vault, Signal, Command and their Identity integration. Core remains same-SHA skip. Pulse, games, and WAVE are excluded.

## Lineage

- Parent main observed before this checkpoint: `cfc536de989f9f765f22d75ef3f45ae4edec8bb3`.
- That head only added a Pulse authority probe; it does not supersede THF Apps Phone Fundamentals V3 source authority.
- App authority remains `ReleaseOps/THF_APPS_PHONE_FUNDAMENTALS_SOURCE_V3_MANIFEST.json`.
- THF Identity integration authority remains V7 for runtime/security integration; no downgrade to the V3 manifest's historical V4 pointer is permitted.

## Exact source transport now available

Google Drive staging folder: `THF-Builder-Staging` (`1X0A6Up611K2moQZWewRx1ZICEmfMTVHS`).

Only the following exact source candidates are eligible for builder ingestion:

- Forge — `THF_Forge_PHONE_FUNDAMENTALS_SRC3.zip` — `75c3744af31f16273a174bdac53b9e812613e4d9ef8c2fa260521c7f7c40cbf8`
- Echo — `THF_Echo_PHONE_FUNDAMENTALS_SRC3.zip` — `3c90b53009d34e9c391bc8f977daf70195a041ba6c0098eca82709932b8734e9`
- Codex — `THF_Codex_PHONE_FUNDAMENTALS_SRC3.zip` — `44ff76cca12b6b13febc53e9e0b8748a01949eb07c40b020d76b82f45a094950`
- Vault — `THF_Vault_PHONE_FUNDAMENTALS_SRC3.zip` — `e33c7c7f1f6d7f913dfe6ca5d674aff2883f7a230c2a323724088c30c4497585`
- Signal — `THF_Signal_PHONE_FUNDAMENTALS_SRC3.zip` — `3b6ba96076decd62e31a90c60d91a101806d6a6e9be329a58baa55ece82227ef`
- Command — `THF_Command_PHONE_FUNDAMENTALS_SRC3.zip` — `314a89f33f62d754edc9cc369fcc35b019d6081c6be0dcfbffa0fe5801ce0ffc`

The Drive staging listing shows all six archives present. Previous authorized-builder discovery found all six missing on the builder, so discovery success must not be interpreted as source presence or Android build success.

## Next fail-closed builder operation

1. Transfer these six staged files to an isolated Apps V3 builder directory; do not search or copy Pulse/game/WAVE paths.
2. Recompute SHA-256 on the builder and require exact equality with the values above before extraction.
3. Run ZIP integrity and clean extraction.
4. Build only an archive whose SHA passes. Do not substitute an older APK or source tree.
5. Run compile/unit/integration/package inspection and record APK/AAB SHA, package ID, versionCode/versionName, targetSdk 36, launcher policy, adaptive/monochrome assets, and Signal/Command no-launcher/private boundaries.
6. Preserve `FINAL_OR_PLAY_READY=false` until physical-phone evidence exists.

## Current truth

`ANDROID_EXACT_BUILD=false`, `PHYSICAL_DEVICE_PASS=false`, `PRODUCTION_SIGNING=false`, `FINAL_OR_PLAY_READY=false`.
