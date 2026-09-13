# THF + WAVE Large-Batch Release/Platform/QA Checkpoint — 2026-09-14 00:30 EEST

## Release truth
This checkpoint records only evidence established in this pass. It does not claim physical-device/GPU QA, production signing, signed AAB, Play approval, or production deployment.

## Core MobileFix1 resolution
- Authoritative Core source remained `THF_Core_RC6_ANDROID_NATIVE_I18N_RELEASE_CUMULATIVE_SOURCE.zip`.
- Source SHA-256: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`.
- WIF/OIDC -> GCP -> IAP remained operational.
- Dedicated Core runtime on port `18181` passed local health.
- The earlier Live QA gate failure was isolated to verification/tooling behavior, not source integrity, WIF/GCP access, or runtime startup.
- `THF Core MobileFix1 Resume V2` run `34784243935` completed PASS.
- Head commit: `e1a73b6956ff1dedc5249a7aaf7af746465dfa9c`.
- Package: `com.topherofit.thf.core.debug`.
- VersionCode: `62201`.
- VersionName: `6.2.2-rc6-mobilefix1-debug`.
- targetSdk: `36`.
- Staging HTTPS health: PASS.
- Home HTTP: PASS.
- Endpoint injection in generated BuildConfig: PASS.
- Endpoint presence across `classes*.dex`: PASS.
- APK SHA-256: `507c47676445bfe0e7b54bc4005369315df365967f83e2717b055db268c58f8e`.
- Uploaded artifact ZIP SHA-256: `2a5d8f052fb87249c1c3495f597b9851c591d065a2ddfa5b201a0c5cc2b98d4c`.
- Artifact ID: `10325617728`.
- Production signing: NO.
- Play upload: NO.
- Physical-device acceptance: PENDING.
- FINAL: NO.
- PLAY_READY: NO.

## Diagnostic hardening
A post-completion failure evidence workflow was added in commit `cf234f0daa895a13c5268bd4c220d79be1a97dc7` so future Core MobileFix1 failures are inspected only after the target workflow has completed, preventing the previous race where diagnostics read half-written remote evidence.

## Mobile Real-Function boundary
The Core candidate above clears build/package/runtime-binding evidence only. It remains blocked from FINAL until the exact APK SHA receives physical-device evidence for install, launch, touch, responsive layout/orientation, background/resume, offline/network transitions, core user journey, and crash-free smoke.

## Learn/Fitness
No regression was established relative to the prior checkpoint:
- Learn exact QA APK SHA-256: `04134c48df8f8b771a09ace6db4843bc66f46f2e13e6fbba993b092b80fe38ba`.
- Fitness exact QA APK SHA-256: `41b52e0273d062f98595f476bdcbc46802007663ba2729ada37f49c52aeacdef`.
Both remain physical-device PENDING and not FINAL/PLAY_READY.

## WAVE RC14
No material resolution was established in this pass. WIF/GCP/IAP remain operational, while CI OS Login still cannot read canonical `/root/workspace/wave-mawja`. Do not weaken OS Login/SSH or grant broad Owner access. Preferred remediation remains a builder-owned release workspace cryptographically tied to the canonical checkout, or narrowly approved OS Login admin access.

## Stable production / security / Play blockers
- Current verified Core endpoint is Cloudflare Quick Tunnel staging, not a stable production hostname.
- GCP production inventory still records public default SSH/RDP firewall rules as a hardening blocker; no consequential firewall mutation was performed.
- Production signing key use, signed AAB generation, Play Internal upload/approval, legal/store acceptance, stable production HTTPS/WSS cutover, and exact-candidate physical-device testing remain outstanding/non-delegable.
