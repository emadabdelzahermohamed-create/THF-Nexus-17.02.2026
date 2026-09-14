# THF Apps Phone Fundamentals Source V1 — 2026-09-15

Status: **SOURCE_CANDIDATE_ONLY / NOT_FINAL / NO_GO**

Scope is Core/Hub, Forge/Market, Echo/Community, Codex/Learn, Vault/Wallet, private Signal/Publisher, private Command/Admin and shared Identity surfaces. Pulse, all game code and WAVE are excluded.

## Lineage
Latest exact app authority was resolved before edits. Core exact source was not available as editable exact bytes in this run, so Core is same-SHA skipped and remains unchanged. Forge/Echo/Codex/Vault/Signal/Command edits were made only after exact input ZIP SHA matched the authoritative source SHA. An initially found Echo/Codex RC4 Library file did not match authority and was rejected; exact RC3 bytes were then located and used.

## Completed source batch
- Approved visible names: THF Market, THF Community, THF Learn, THF Wallet, THF Publisher, THF Admin; package IDs unchanged.
- All six changed Android sources retain compileSdk/targetSdk 36 and exactly 20 `values*` string resource sets.
- Added adaptive launcher resources for API 26+, separate Android 13+ monochrome themed icon resources, and deterministic original 512x512 store-icon assets with provenance.
- Public apps keep launcher entries. Signal and Command remove MAIN/LAUNCHER and add signature-protected exported entry permission; this is an Android entry boundary in addition to the already-CI-proven server-authoritative THF Identity RBAC contract. It is not proof of private catalog/internal distribution or production signer parity.
- Existing reachable-backend/auth/offline behavior is preserved. No placeholder endpoint was introduced.

## Validation
- XML parse/static manifest/resource/package/API36 checks: PASS for six changed sources.
- Forge pytest: 1/1 PASS.
- Echo pytest: 4/4 PASS when an explicit ephemeral `ADMIN_KEY=test-admin` is supplied to the test process; empty ADMIN_KEY correctly fails closed at 403. No secret was written to source.
- Codex pytest: 6/6 PASS.
- Python compileall: PASS for Forge/Echo/Codex/Command.
- Deterministic source packaging: exact byte-for-byte rebuild PASS; ZIP integrity PASS.
- Clean-extract manifest/XML/targetSdk36 validation: PASS.
- Android APK/AAB build/package inspection: NOT RUN in this source batch because the connected remote builder/device is unavailable. Therefore previous APKs remain tied to previous source SHAs and are not eligible for the new sources.

## Candidate source SHAs
- forge: `d17477fd370fdc4b04562f7f1113e79942951f1d39444b498f18d82de983ed1f`
- echo: `0b9d6180b1701b239c1288fa76418e32086b9fc679995d1d2acdc0c7f098554c`
- codex: `255d8f24aec054bc4a42f8de845eeb895276b0938864b49166d89ff27377e4bd`
- vault: `2dc0f527b23bd9d6654cd611f94d8b6e4502f0e24184c846372cf4b9e007de2d`
- signal: `da0282314077bd55912629eecd599b64f292c958163a6bede6804894769460aa`
- command: `fb31bd2a4dba0344f37eed27ff36eb918b81d502c394f0d423bc2d97e61ca1e5`

## Remaining release gates
Reachable trusted THF backend/Identity role-claim deployment, provider push credentials, account deletion/logout/session persistence end-to-end proof, exact-source Android build and package inspection, private distribution/catalog enforcement, production signing and physical-phone install/launch/touch/layout/resume/offline/network/accessibility/core journey/crash-free evidence remain required.

`NETWORK_RELEASE_READY=FALSE`
`PUSH_READY=FALSE`
`PHYSICAL_DEVICE_PASS=FALSE`
`FINAL_OR_PLAY_READY=FALSE`
