# THF + WAVE Large-Batch Release Checkpoint — 2026-09-14 10:38 EET

Status: **ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING**

## Start state
- Current main at start: `dc9b3e93c525eae7c4f329f5b983efe1c031614b`.
- Latest game checkpoint: Physical Device Evidence V9 SUCCESS, exact six game APK candidates unchanged, no physical-device promotion.
- Latest apps checkpoint: exact ten app candidates unchanged and `PENDING_PHYSICAL_PHONE`; runtime network evidence remains diagnostic-only until stable THF backend/Pass staging exists.
- WAVE remains isolated; no WAVE source, SSH/OS Login, Cloudflare or production deployment state was modified in this batch.

## New safe reversible repair — app crash-free evidence provenance
Found an evidence-policy asymmetry: game V9 already requires crash-free claims to be backed by a non-empty SHA-256-bound ADB logcat capture from the same device session/package, while app V3 only bound canonical check captures and could still accept a structured `crash_free` PASS without raw logcat provenance.

Added:
- `ReleaseOps/mobile/validate_app_device_evidence_v4.py`
- `ReleaseOps/mobile/test_validate_app_device_evidence_v4.py`
- `.github/workflows/thf-app-physical-device-evidence-tooling-v4.yml`

V4 layers on V3 and requires:
- `crash_observation` bound to the exact evidence session and package;
- approved ADB logcat method (`adb-logcat-epoch-package-filter` or `adb-logcat-pid-filter`);
- strict crash-observation interval wholly inside the declared phone session;
- non-empty evidence file with exact SHA-256 byte match;
- exact package identity present in captured bytes;
- `process_alive_after_core_journey=true`;
- `crash_free=true`;
- rejection of fatal markers including `FATAL EXCEPTION`, `AndroidRuntime`, `Fatal signal`, `ANR in`, `am_crash`, and `am_anr`;
- continued `final_or_play_ready=false` truth boundary.

Commits:
- `a41212ee9ce4fcd0983d87160c70e1c164fec748` — V4 validator.
- `ea132196877d976c1371d89418b7991efd88a484` — V4 regression suite.
- `a25a469afc195d605f8c43fe89f27e584f6b6fc4` — permanent V4 CI gate.

CI evidence:
- Workflow: `THF App Physical Device Evidence Tooling V4`.
- Run: `34818740502`.
- Conclusion: **SUCCESS**.
- Compile PASS; V2 installed-byte regressions PASS; V3 capture-content provenance regressions PASS; V4 crash-free logcat provenance regressions PASS; authoritative app registry remains ten unique candidates, all `PENDING_PHYSICAL_PHONE`, with `FINAL_OR_PLAY_READY=FALSE`.

## Preserved Mobile Real-Function Release Policy
No APK/AAB was rebuilt or signed because exact candidate/source SHAs did not change. No physical-device, GPU/FPS/RAM/thermal, Play approval, production endpoint, Cloudflare cutover or WAVE deployment claim was fabricated.

Remaining hard blockers:
- exact-candidate physical-phone evidence for every app/game;
- stable trusted THF production/staging HTTPS/WSS backend and explicit health/auth/session/federation proof;
- FCM/APNs provider delivery and on-device notification receive/tap/background-resume proof;
- production signing/signed AAB and Play Internal acceptance;
- user-only 2FA/ownership/billing/OAuth/legal acceptance where applicable;
- WAVE canonical-source release path remains isolated and must not be bypassed by weakening OS Login/SSH or substituting an older source.

Evidence body SHA-256: `94833d745f0dd7e0096162ae6ad38dfb09b20976d08db2928c42c888d7c0fb9c`
