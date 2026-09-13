# THF Godot Runtime Signing Recovery Checkpoint V1 — 2026-09-13

## Scope
THF Terra RC34 and Rift RC37 Android runtime-fixed release gates only. WAVE_MAWJA remains isolated and untouched.

## Verified failure
Terra runtime-fixed run `34748278235` reached canonical SHA verification, Godot 4.7.2 import, headless boot, Android template setup, and Android export, then failed at the *initial* `apksigner verify` because the isolated Godot HOME emitted an unsigned APK (`Missing META-INF/MANIFEST.MF`). This is a packaging/signing-stage failure, not a project-data/import/boot failure.

Canonical Terra source remained unchanged:
- `THF_Terra_v4.6.8_RC34_REMOTE_LOD_HYSTERESIS_CUMULATIVE_SOURCE.zip`
- SHA-256 `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`

## Root cause in ReleaseOps automation
The intended unsigned-APK recovery used `set +e`, but the global `ERR` trap still fired on the failed verification command before the recovery block could execute.

## Safe fix
Commit `138abd07ec81a91b51e357757d058ea92faa1598` changed the signature probe to an `if apksigner verify ...; then ... else ... fi` conditional. This suppresses the ERR trap only for the expected probe failure and then performs reversible QA-only recovery:
1. zipalign the unsigned APK;
2. generate an ephemeral QA keystore;
3. sign the disposable APK;
4. delete the temporary keystore;
5. re-run final signature, zipalign, package, targetSdk 36, Godot payload, and canonical-SHA guards.

No production signing key is used or accessed.

## Active validation runs
- Rift RC37 runtime-fixed: `34749952356` — triggered from fix commit and running through WIF/IAP.
- Terra RC34 runtime-fixed: `34749952370` — triggered from fix commit and running through WIF/IAP.

## Mandatory release gates preserved
- canonical source SHA-256 before and after build
- safe disposable extraction
- Godot import + headless boot
- Android export with project payload
- signature verification
- zipalign
- expected final package ID
- targetSdk 36
- no production signing
- no canonical archive mutation
- THF/WAVE isolation

## Safety / excluded actions
No Google Play publishing, Cloudflare production cutover, Solana/token financial action, destructive GCP mutation, production signing, canonical archive overwrite/delete, or WAVE/THF mixing was performed.

## Next step
Wait for runs `34749952356` and `34749952370`. If either fails, use its exact failing phase/log and fix only the disposable build/tooling path. If both pass, capture artifacts + SHA-256 and advance them to device install/runtime acceptance before calling either build final.