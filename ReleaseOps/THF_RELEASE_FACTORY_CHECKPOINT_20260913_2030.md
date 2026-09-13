# THF / WAVE Release Factory Checkpoint — 2026-09-13 20:30 EEST

Status: **NO-GO for final/public rollout; Vault/Signal RC4 engineering blocker resolved**

This checkpoint records reversible release/tooling/QA work only. No production signing, Play upload/approval, Cloudflare production cutover, physical-device result, legal acceptance, billing action, financial transaction, or destructive cloud mutation is claimed.

## Material change: Vault + Signal RC4 exact candidates

The first `THF Vault Signal RC4 Build Fix` attempt (`34771821808`) failed in exact-source staging without sufficient diagnostics. The failure was not attributed to Gradle, Android, WIF, or package compilation.

A reversible fail-closed evidence repair was committed as:
- commit `51ec7dfda852391e7ca7742b98e5d4a718d21d8c`
- workflow `.github/workflows/thf-vault-signal-rc4-buildfix.yml`

The repaired stage now records HTTP result, expected/actual source SHA-256, ZIP integrity and per-source PASS/FAIL before build, then records exact candidate APK SHA-256.

Verification run `34771909287` completed PASS end-to-end.

### Exact source evidence
- Vault RC4-BF1 source SHA-256 expected/actual: `dd6db86d7532f773a8d1d2662bf466bdcc0f1c64a863602ecdd1267c8f82fa33` — HTTP 200 — ZIP PASS.
- Signal RC4-BF1 source SHA-256 expected/actual: `377044263fa0fc366afe67c6b42ccf4f3e2d1bc75769350f2ee885983f820ddf` — HTTP 200 — ZIP PASS.
- `source-stage.tsv` SHA-256: `24a3125642d1b3026955176c05cc65bf9b625cd8ff985fb7c1d18789ffe22240`.

### Exact QA APK evidence
- Vault package `com.topherofit.thf.vault`
  - versionCode `12001`
  - versionName `1.2.1-apps-rc4-buildfix1`
  - targetSdk 36
  - QA signature verifies
  - non-debuggable
  - APK SHA-256 `ee4d86b0a6b2d1a0c526929bc97baa9acf97c5c72dce6df910e9e69744f6d2b5`
- Signal package `com.topherofit.thf.signal`
  - versionCode `12001`
  - versionName `1.2.1-apps-rc4-buildfix1`
  - targetSdk 36
  - QA signature verifies
  - non-debuggable
  - APK SHA-256 `15699461b80d3d65e4da8e435b15e6cf3317684de7d3e25904b11319ec2857b7`

Both source policy gates passed. Vault tests: 1 passed. Signal tests: 2 passed. Both Gradle `assembleRelease` executions completed successfully.

Evidence artifact:
- name `THF-VAULT-SIGNAL-RC4-BF1-QA-APKS`
- artifact ID `10321794443`
- uploaded artifact ZIP SHA-256 `fbed0ea80bee7aa7be9750e9753000525348b2ec5bcc187d07de12f354ec33e5`

This closes the prior Vault/Signal exact-source/build/package/API36 QA blocker. It does **not** establish production signing or final mobile readiness.

## WAVE RC14

No material resolution in this batch. WIF/GCP/IAP remains distinct from the WAVE source-access blocker. WAVE remains NO-GO because the CI OS Login identity cannot read canonical `/root/workspace/wave-mawja`.

Allowed safe closure remains:
1. narrowly scoped owner/admin-approved OS Login access; or
2. preferred: service-account-owned release workspace cryptographically bound to the canonical checkout.

Do not disable OS Login, weaken SSH, grant broad Owner, or substitute older WAVE source.

## Existing hard blockers retained

- Core RC6, Terra RC34 and Rift RC37 remain blocked on exact-hash physical-device acceptance.
- Vault RC4-BF1 and Signal RC4-BF1 now also require exact-candidate physical-device acceptance before FINAL/PLAY_READY.
- Any networked core journey must still prove reachable production/stable HTTPS/WSS health/auth; staging/Quick Tunnel is not production.
- Production signing key / Play App Signing, Play Internal ownership actions, legal/store declarations and final publishing remain user-controlled gates.
- No stable production hostname/cutover is claimed.

Physical-device acceptance must cover install, cold launch, touch, responsive layout/orientation, background/resume, offline/network transition, core journey and crash-free smoke; games additionally require player/avatar load, movement/camera/gameplay and FPS/RAM/thermal observation.

## Tooling debt observed, not a current release blocker

GitHub Actions reports Node 20 action-runtime deprecation warnings and `actions/setup-java@v4` deprecation while forcing compatible Node 24 execution. Current run passed, so this is maintenance debt rather than a blocker; migrate pinned action SHAs to Node-24-capable/current major revisions in a separately verified tooling change.

## Safety

THF and WAVE remained isolated. No canonical source was overwritten. No production signing, Play upload, production deployment/cutover, destructive IAM/firewall mutation, financial action, or fabricated physical-device/GPU evidence was performed.
