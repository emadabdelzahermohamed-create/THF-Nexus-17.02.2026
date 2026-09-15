# THF Apps V3 Builder Discovery Truth — 2026-09-15

Scope: THF Core/Forge/Echo/Codex/Vault/Signal/Command and THF Identity surfaces only. Pulse, games and WAVE excluded.

- Authoritative app source remains Phone Fundamentals V3; no app source bytes were changed in this checkpoint.
- Exact V3 source ZIPs were independently recovered from the persistent ReleaseOps Library and their SHA-256 values match the V3 manifest for Forge/Echo/Codex/Vault/Signal/Command.
- ZIP integrity was rechecked before staging.
- GitHub Actions run 34927051970 successfully proved WIF/IAP access to the authorized GCP builder, but the discovery payload classified all six exact V3 source archives as MISSING on the builder. Workflow success therefore proves the inspection path, not source availability or an Android build.
- The six exact V3 archives were staged to the connected Google Drive folder `/THF-Builder-Staging` as a transport source for a subsequent authorized builder ingestion step. No Pulse/game/WAVE artifact was staged.
- No APK/AAB is rebound to V3. ANDROID_EXACT_BUILD remains FALSE.
- Physical-phone evidence is still absent. PHYSICAL_DEVICE_PASS remains FALSE and FINAL_OR_PLAY_READY remains FALSE.

Exact V3 SHAs:
- Forge: 75c3744af31f16273a174bdac53b9e812613e4d9ef8c2fa260521c7f7c40cbf8
- Echo: 3c90b53009d34e9c391bc8f977daf70195a041ba6c0098eca82709932b8734e9
- Codex: 44ff76cca12b6b13febc53e9e0b8748a01949eb07c40b020d76b82f45a094950
- Vault: e33c7c7f1f6d7f913dfe6ca5d674aff2883f7a230c2a323724088c30c4497585
- Signal: 3b6ba96076decd62e31a90c60d91a101806d6a6e9be329a58baa55ece82227ef
- Command: 314a89f33f62d754edc9cc369fcc35b019d6081c6be0dcfbffa0fe5801ce0ffc
