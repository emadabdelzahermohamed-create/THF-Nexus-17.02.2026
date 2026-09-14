# THF RELEASE / PHONE-QA checkpoint — 2026-09-14 23:45 EET

Status: **NOT_FINAL / NO_GO**

This checkpoint records the newest proven release authority and the safe/reversible repairs made in this batch. It does not claim physical-device QA, production signing, Play approval, or production deployment.

## Authority snapshot

- Terra / THF World: canonical package `com.topherofit.thf.terra`; exact source SHA-256 `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`; current QA APK SHA-256 `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`; physical phone `PENDING`.
- Rift / THF Arena: canonical package `com.topherofit.thf.rift`; latest authority `4.7.5-rc41`; exact source SHA-256 `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`; eligible APK `NONE`; physical phone `PENDING`. RC37 is superseded and is not an eligible build source.
- Spark / THF Learn Games: package `com.topherofit.thf.spark`; exact source SHA-256 `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`; current candidate APK SHA-256 `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`; physical phone `PENDING`.
- Rush / THF Motion Games: package `com.topherofit.thf.rush`; exact source SHA-256 `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`; current candidate APK SHA-256 `528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7`; physical phone `PENDING`.
- Pulse: product package `com.topherofit.thf.pulse`; newest reconciled product source SHA-256 `6b3a5ead0c8a57c53a9aaac01efa824bb020bddfe36eba1fb76ef156dea56427`; eligible exact candidate APK `NONE` in the newest lineage reconciliation. Older/debug overlay output is not promoted over this authority.
- Vault / THF Wallet: package `com.topherofit.thf.vault`; source SHA-256 `052e2c55c6066c15eee63528218b8eab9711bec9de71335c67c7e1692a5b5432`; QA APK SHA-256 `7431987b0be9589f997d505cfe69c6d3e217deb7d2783c44f99e6f263693209e`; production signing/network/physical-device release gates remain false.
- Signal / THF Publisher: package `com.topherofit.thf.signal`; source SHA-256 `f78890c3bf036d80a568ec39baac4a665d6092b9bbc8c4f080f2651785c1a275`; QA APK SHA-256 `c7eb1044426423862687f93a875208a5ea8c5703d4978efb93eb4b54a1555d75`; internal/private role gate retained; production signing/network/physical-device release gates remain false.
- Core/Forge/Echo/Codex/Command: no newer exact authoritative candidate was proven by the latest app-private checkpoint, therefore no stale or synthetic candidate was promoted. Command/Admin remains private/internal and role-gated.

## Shared integration authority

Shared integration V2 remains the newest integration checkpoint for Google/THF Identity hooks, passkey/password/email-code/guest state, cross-app handoff, Health Connect primary adapter hooks, optional Samsung Health adapter hooks, normalized motion evidence provenance, localization, Data Saver, Reduce Motion and High Contrast. Production OAuth verification, live passkey replay/challenge service, production handoff signer/replay store, Samsung partner access and physical-phone validation remain unproven and must remain fail-closed.

## Repairs completed in this batch

1. Retired the stale operational Rift RC37 path from `.github/workflows/thf-terra-rift-mobile-candidate-overlay-v1.yml`. Commit `8f249518443a2b79d8a18c00f8dfcfa39407867e`. The workflow is now Terra-only and explicitly asserts Rift `4.7.5-rc41`, no eligible Rift APK, WAVE untouched, production signing false, device pending and final false.
2. Retired the second stale operational Rift RC37 path from `.github/workflows/thf-terra-rift-runtime-binding-audit-v1.yml`. Commit `4ebb36f1f2ff48c7e79f5c97eec439867bb953b0`. The workflow is now Terra-only and latest-authority guarded.
3. After both repairs, `THF Games Latest Authority V1` run `34895081755` completed `SUCCESS`, proving that the latest-authority validator no longer sees an operational RC37 promotion path on `main`.
4. Repository code search for `RC37` under `.github/workflows` returned no remaining matches after the repairs.

## Hard blockers retained

- Exact-candidate physical-phone install/launch/touch/layout/orientation/background-resume/offline-network/core-journey/crash-free evidence is still required before any candidate can be `FINAL` or `PLAY_READY`.
- Games additionally still require exact-device avatar/player load, movement/camera/gameplay interaction and observed FPS/RAM/thermal behavior.
- Rift RC41 has no eligible exact APK yet; an RC37 binary must never substitute for it.
- Pulse newest product lineage has no eligible exact candidate APK yet; old/debug overlay output must not override the newest lineage.
- Production OAuth console, production signing, Play Console, legal acceptance and other user-only gates remain external/non-delegable where applicable.
- WAVE was not read, changed, rebuilt, deployed or mixed into this THF batch.

## Evidence payload

```text
state=NOT_FINAL_NO_GO
main_head_before_checkpoint=4ebb36f1f2ff48c7e79f5c97eec439867bb953b0
latest_game_authority_run=34895081755
latest_game_authority_run_conclusion=success
repair_mobile_overlay_commit=8f249518443a2b79d8a18c00f8dfcfa39407867e
repair_runtime_binding_commit=4ebb36f1f2ff48c7e79f5c97eec439867bb953b0
terra_source_sha256=eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68
terra_qa_apk_sha256=e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec
rift_source_sha256=29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d
rift_candidate_apk_sha256=NONE
spark_source_sha256=58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43
spark_candidate_apk_sha256=9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea
rush_source_sha256=766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c
rush_candidate_apk_sha256=528f7d1151e52efe35c5e441dca3635afceb47cae82c0209b0c914a0e8965ed7
pulse_source_sha256=6b3a5ead0c8a57c53a9aaac01efa824bb020bddfe36eba1fb76ef156dea56427
pulse_candidate_apk_sha256=NONE
vault_source_sha256=052e2c55c6066c15eee63528218b8eab9711bec9de71335c67c7e1692a5b5432
vault_candidate_apk_sha256=7431987b0be9589f997d505cfe69c6d3e217deb7d2783c44f99e6f263693209e
signal_source_sha256=f78890c3bf036d80a568ec39baac4a665d6092b9bbc8c4f080f2651785c1a275
signal_candidate_apk_sha256=c7eb1044426423862687f93a875208a5ea8c5703d4978efb93eb4b54a1555d75
physical_device_gate=PENDING
production_signing=false
play_ready=false
wave_touched=false
```

Evidence payload SHA-256: `5b58415474d6bfea3145d683e9e3f52cfc5c185fc3dcc7bbf57ac5cd5a5f3937`
