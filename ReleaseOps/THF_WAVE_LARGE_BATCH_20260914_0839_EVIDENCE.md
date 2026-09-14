# THF + WAVE Large-Batch Release/QA Checkpoint — 2026-09-14 08:39 EET

Status: **ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING**

## Authoritative state read
- Current `main` before this batch already contained Game Physical Device Evidence V7 and checkpoint `ce783ec6672542d06db72ac34cdb90d4ac0f2332`.
- Game V7 run `34809088502` is SUCCESS and binds game evidence to the SHA-256 of the APK bytes actually installed on the phone.
- Latest THF Apps Factory checkpoint read: `ReleaseOps/apps_factory/THF_APPS_FACTORY_CHECKPOINT_20260914_0812_EET.md`; all ten app candidates remain `PENDING_PHYSICAL_PHONE`.
- WAVE remains isolated. Latest reviewed WAVE/program evidence continues to block RC14 on CI OS Login access to canonical `/root/workspace/wave-mawja`; WIF/GCP/IAP are operational. No SSH/OS Login weakening or older-source substitution was performed.

## Material gap found and repaired
The application physical-device registry bound acceptance to each exact candidate APK SHA, but the apps-side evidence tooling did not yet require cryptographic proof that the bytes installed on the physical phone were those exact registered bytes. This left apps weaker than the game V7 boundary.

Added:
- `ReleaseOps/mobile/validate_app_device_evidence_v2.py`
- `ReleaseOps/mobile/test_validate_app_device_evidence_v2.py`
- `.github/workflows/thf-app-physical-device-evidence-tooling-v2.yml`

Commits:
- `8130e2b506830ff5b663a59c75b032db7a27177b` — app installed-byte evidence validator
- `e72090ffb5d50bdee8b9e6e96d4ab91cf1c691f9` — negative/positive regressions
- `c9b22c921e6b0a2d5eee7a5c08c7648a44b13d9e` — permanent CI gate

The validator now fails closed unless:
- product/package/exact candidate SHA match the current authoritative app registry;
- the candidate remains `PENDING_PHYSICAL_PHONE`;
- the target is a real physical Android device, not an emulator;
- one device-session ID and bounded UTC interval are present;
- installed `base.apk` SHA-256 equals the exact candidate SHA;
- exactly one `/data/app/.../base.apk` code path is present;
- installed bytes were read by an approved ADB method;
- installed-byte proof belongs to the same session and timestamp window;
- a package dump exists;
- the objective capture and every required check reference a real non-empty evidence file whose SHA-256 matches;
- every registry-required physical check is PASS inside the same session window;
- the evidence bundle does not self-promote `FINAL_OR_PLAY_READY`.

## Verification
GitHub Actions run `34810279386` — `THF App Physical Device Evidence Tooling V2` — **SUCCESS**.

Successful stages:
- Python 3.12 compile;
- installed-byte physical evidence regression suite;
- authoritative registry truth preservation.

The workflow explicitly preserved:
- `APP_CANDIDATES=10`
- `PHYSICAL_DEVICE_STATUS=PENDING`
- `FINAL_OR_PLAY_READY=FALSE`

No physical-device result was fabricated and no candidate APK was rebuilt.

## Preserved blockers
- All exact app/game candidates still require physical-phone acceptance on the exact registered installed bytes.
- Production signing/signed AAB, Play Internal upload/acceptance, stable production HTTPS/WSS and production Cloudflare cutover remain unproven.
- Notification production delivery still requires approved provider credentials, KMS/secret boundary and real phone receive/tap/background-resume evidence.
- WAVE RC14 remains blocked on safe canonical-source access at `/root/workspace/wave-mawja`; no insecure workaround was applied.
- Owner/user-only signing keys, Play ownership, 2FA/OAuth, billing/legal acceptance and physical-device actions remain non-delegable.

No production deployment, Play approval, signed AAB, GPU/device QA or WAVE modification is claimed.
