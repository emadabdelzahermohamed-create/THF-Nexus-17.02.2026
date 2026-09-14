# THF Apps Factory checkpoint — 2026-09-14 04:05 EET

`FINAL_OR_PLAY_READY=FALSE`

Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault UX, Signal, Command, THF Pass/shared identity/federation/handoffs. Dedicated native game streams and token finance were not mutated.

## Same-SHA preservation
- Core RC6 and all nine runtime-bound Android candidates retain their previously proven exact package/API36/runtime-binding evidence.
- No exact Android candidate was redundantly rebuilt because no regression evidence changed its source/APK SHA.
- Physical-phone acceptance remains PENDING for all ten exact APKs (Core + nine app candidates).

## Notification HTTP contract block
Added `ReleaseOps/apps_factory/notification_http_contract.py` as a framework-neutral candidate behind an already-verified THF Pass session. It supports register, rotate, revoke and logout-scoped notification token lifecycle operations without parsing credentials itself or exposing raw provider tokens in responses.

Security properties regression-protected:
- verified Pass session required;
- provider tokens/authorization/credentials/secrets forbidden in query strings;
- locked THF package allowlist remains enforced by the registry;
- Pass session is bound to one package audience, preventing a valid session for app A from registering/revoking tokens for app B;
- revoke remains subject + package scoped;
- raw provider token custody remains behind `SecureTokenVault`.

Tests: `ReleaseOps/apps_factory/tests/test_notification_http_contract.py`.

## Provider-adapter contract block
Added `ReleaseOps/apps_factory/notification_provider_contract.py` and regressions. This defines configuration and send interfaces without shipping provider credentials or pretending delivery has occurred. Delivery requests require localization resource keys and locale, carry explicit Data Saver state, and reject credential-bearing deeplinks.

No FCM/APNs production adapter or live send was added; `PUSH_READY=FALSE` remains mandatory.

## Physical-device evidence preparation
Added `THF_NOTIFICATION_DEVICE_EVIDENCE_TEMPLATE_V1.json` with all observations PENDING and an exact-SHA requirement for physical notification permission/channel/receive/tap/deeplink/background-resume/RTL/localization/accessibility/Data Saver/offline-truth/crash-free evidence.

Added `THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json`, pre-binding Core plus the nine authoritative app candidates to their exact APK SHA-256 and source SHA-256 values from `THF_APPS_FACTORY_STATE_20260913_2035_EET.json`. Every candidate remains `PENDING_PHYSICAL_PHONE`.

Added `.github/workflows/thf-apps-physical-evidence-registry-v1.yml` to fail closed on SHA/package drift, candidate count drift, missing required phone checks or premature promotion.

## CI evidence
- `THF Notification HTTP Provider Contract V1` run `34794517839`: SUCCESS before package-audience hardening.
- Package-audience hardening commit `7d4fc89f3f398588922c861512cc8c2ffd8782ca` plus regression commit `a8fa43c9640a36afe49cb378764ba77509a526bb`.
- Hardened notification run `34794565970`: SUCCESS, including compile, lifecycle + HTTP + provider regressions and fail-closed device template validation.
- `THF Apps Physical Evidence Registry V1` run `34794606131`: SUCCESS. The gate proves exact Core + nine app package/APK/source binding and requires all physical acceptance states to remain PENDING until real phone evidence exists.

## Truth boundary / blockers
1. THF Pass isolated lifecycle/federation rehearsals exist, but a stable externally reachable non-public trusted-TLS staging endpoint is still not proven; do not report Pass as staging-live.
2. Notification lifecycle/HTTP/provider contracts are tested candidates only. No production provider credentials, provider delivery, reachable production registration endpoint, or physical notification delivery is proven.
3. Production-grade encrypted `SecureTokenVault` still requires an approved runtime secret/KMS boundary.
4. Every exact Android APK still requires physical-phone install/launch/touch/responsive-layout/orientation/background-resume/offline-network/core-journey/crash-free/accessibility/Data Saver/RTL/localization acceptance; notification-capable apps additionally require permission/channel/receive/tap/deeplink evidence.
5. Production signing, AAB/Play Internal, OAuth/legal/2FA and irreversible rollout remain untouched owner-controlled gates.

## Next executable block
Integrate the package-bound notification HTTP candidate into the isolated THF Pass rehearsal without changing the public endpoint. Continue fail-closed contract work around Pass session expiry/revocation linkage so an expired/revoked session cannot register/rotate/revoke provider tokens. Then prepare an adapter-specific FCM/APNs implementation only after an approved credential/KMS boundary exists. Do not promote PUSH_READY or FINAL/PLAY_READY until live reachable runtime and exact physical-phone evidence exist.
