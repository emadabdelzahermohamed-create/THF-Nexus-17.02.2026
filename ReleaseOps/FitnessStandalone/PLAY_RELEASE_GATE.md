# THF Fitness / Pulse — Google Play Release Gate

Updated: 2026-09-20
Application ID: `com.topherofit.thf.pulse`
Target SDK: 36
Canonical avatar: MPFB/MakeHuman Stage16A, 137 joints / 195 clips. Legacy humanoid fallback is prohibited.

## Authority and artifact rule
This gate must be read with `MASTER_BACKLOG.md` and `PLAY_INTERNAL_COMMITTED_20260919.md`. Historical RC2 unsigned evidence is not the current publication state and must not be mistaken for the signed Play artifact.

Google Play Internal is already committed for the production-signed release `versionCode 50001`. Direct pipeline evidence is GitHub Actions run `35434624698`, job `105875090547`; the Android Publisher step returned package `com.topherofit.thf.pulse`, track `internal`, `committed=true`, `versionCode=50001`. Signed evidence artifact `thf-fitness-v5-rc2-signed-release`, artifact id `10581347670`, ZIP digest `sha256:6926a59d830f038d351b3b44d8b0f886cba87c9941efa0497d6f4441d4a765b2`.

## Closed publication prerequisites
- [x] Production HTTPS backend authority established and shared with Web/PWA.
- [x] Production signing materialized outside the repository; no keystore/password committed.
- [x] Signed API-36 release AAB accepted by the Play publication pipeline.
- [x] Internal-track edit committed for versionCode `50001`.
- [x] Public privacy policy and account-deletion URLs are available on the production HTTPS host.

## Fail-closed runtime/device gates
The following are **not** implied by successful Play upload and remain open until direct evidence exists:
- [ ] Install from the Google Play Internal tester track on a physical Android device.
- [ ] Launch/onboarding/login/Arabic RTL/English LTR/workout/resume regression on that installed Play artifact.
- [ ] Stage16A GPU rendering on physical Android, including canonical 137-joint / 195-clip lineage and absence of legacy fallback.
- [ ] Health Connect permission/data flow on physical Android for only the data types actually used.
- [ ] Physical sensor/motion verification and performance evidence (startup/FPS/RAM/thermal where applicable).
- [ ] Offline/online transition and first-install offline Stage16A asset availability.
- [ ] Web↔Android cross-device account/data synchronization using two real clients.
- [ ] Confirm the installed Play artifact resolves the same production backend/identity authority as Web.

## Play Console compliance gates
Do not guess these declarations; reconcile them against verified application behavior and owner-console state.
- [ ] Data Safety declaration.
- [ ] Health Apps declaration.
- [ ] App Access instructions/declaration.
- [ ] Content rating questionnaire/result.
- [ ] Target audience declaration.
- [ ] Ads declaration, matching actual behavior.

## Security/release closure
- [ ] Dependency review and network-security release audit PASS with evidence.
- [ ] Play Integrity server-side exchange for trusted activity/reward paths; client-only checks are insufficient.
- [ ] Final release manifest, artifact SHA-256 set, changelog and rollback/replacement procedure.
- [ ] Post-publish Play tester runtime re-verification after each Android release increment.

## Current state
**PUBLISHED TO GOOGLE PLAY INTERNAL, RUNTIME/COMPLIANCE NOT YET ACCEPTED.** Signed `versionCode 50001` is committed to `internal`. This is publication evidence only; physical-device Play runtime, Health Connect, Stage16A GPU verification, cross-device synchronization, Play declarations and final visual acceptance remain FAIL-CLOSED.

No WAVE-MAWJA source, release, deployment or configuration is in scope for this gate.
