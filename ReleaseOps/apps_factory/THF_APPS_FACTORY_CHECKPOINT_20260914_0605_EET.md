# THF Apps Factory Large-Batch Checkpoint — 2026-09-14 06:05 EET

Status: NOT_FINAL / PHYSICAL_DEVICE_PENDING / PUSH_PROVIDER_PENDING / PASS_STABLE_STAGING_PENDING

## Scope and same-SHA handling

This pass stayed inside THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity, notifications, and cross-app handoff support. Dedicated native game streams and token-finance implementation were not modified.

Core RC6 and the existing runtime-bound Android app candidates retain their previously recorded exact APK/source SHA values. Previously proven same-SHA package/API36/runtime-binding gates were intentionally skipped rather than rerun for activity. No candidate is FINAL/PLAY_READY; physical-phone acceptance remains SHA-bound and pending.

## Cross-stream authority blocker discovered at run start

The latest cross-stream truth checkpoint reports conflicting exact APK SHA-256 values for the same Android package identities in the apps and games registries:

- `com.topherofit.thf.spark`: apps `92bc7f913d560a185044af2df7b1955d3a0b29eca920034edf3cd9741bce0c23`, games `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- `com.topherofit.thf.rush`: apps `304164035cc4b82d23e2b2e6bf48abca3c466c46f5668a203cf0b4cfca223e99`, games `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`

This pass did not touch the dedicated game streams and did not arbitrarily select either lineage. Spark/Rush promotion therefore remains fail-closed until one combined-function exact candidate proves preservation of the required app + game behavior and the alternate evidence is explicitly superseded/rejected. Unrelated app candidates continue independently.

## Material engineering change: live Pass session -> notifications

Added `ReleaseOps/apps_factory/pass_notification_bridge.py` to close the stale-principal gap between an earlier authentication decision and later notification actions.

Every notification register/rotate/revoke/dispatch operation now has an integration boundary that re-resolves the current THF Pass session and rejects:

- unknown sessions;
- server-revoked sessions even when the client's cached principal still appears valid;
- expired sessions using authoritative expiry;
- subject mismatch;
- package/audience mismatch;
- cross-package delivery using a registration from another THF application.

Dispatch audience is derived from the authoritative notification registration rather than trusting client payload metadata. Provider tokens remain server-side in the SecureTokenVault boundary.

Logout is fail-secure: the Pass session is revoked first, then package-scoped notification registrations are removed. If notification cleanup fails, the Pass session remains revoked so the stale session cannot authorize another mutation or dispatch.

Engineering commits:
- `0b97abf7a213f5594a9b9ec0d84700f6eb74f342` — initial live-session bridge
- `c5a6e06374911ac11ac2585aba84bd15a4834cac` — authoritative registration audience enforcement
- `cf90c45c5e257e86d97d4518c61fe7e058f7bb1b` — bridge regression suite
- `5cfc47f0bfb1b0a6f6ee084ca4128b188eb4dc16` — CI integration
- `85f6396c59b580db78d108f1ab979bc4648b78bf` — deterministic test-clock repair

## CI evidence

Workflow: `THF Notification HTTP Provider Contract V1`

The first expanded run `34801254890` compiled successfully but failed regressions because the deterministic bridge fixture supplied an epoch-relative expiry to `SessionPrincipal`, whose legacy local guard uses wall-clock time. This was a test-fixture clock-domain bug, not converted into a PASS.

The fixture was repaired by keeping the already-verified local principal structurally valid while the injected live Pass authority owns the deterministic clock. Corrected run:

- Run: `34801310972`
- Head SHA: `85f6396c59b580db78d108f1ab979bc4648b78bf`
- Job: `contract`
- Compile candidates: SUCCESS
- Notification + live Pass session regressions: SUCCESS
- Device-evidence fail-closed template: SUCCESS
- Overall conclusion: SUCCESS

The CI gate still deliberately reports/retains the truth boundary: `PHYSICAL_DEVICE_PASS=FALSE`, `PUSH_READY=FALSE`, `FINAL_OR_PLAY_READY=FALSE` until provider delivery and exact-device evidence exist.

## Remaining gates

This checkpoint does not claim:

- stable externally reachable non-public trusted-TLS THF Pass staging wired to this bridge;
- FCM/APNs production credentials or actual provider network delivery;
- approved production KMS/secret storage backing SecureTokenVault;
- exact-device notification permission/channel/receive/tap/deeplink/background-resume behavior;
- exact APK install/launch/touch/layout/orientation/background-resume/offline↔network/core journey/crash-free/accessibility/Data Saver/RTL/20-language acceptance;
- production signing, signed AAB, Play Internal acceptance, billing, legal acceptance, OAuth/2FA owner actions;
- Spark/Rush release-lineage reconciliation.

No production endpoint, signing material, Play listing, WAVE configuration, dedicated native-game implementation, or token-finance implementation was changed. Rollback is Git-only by reverting the listed Apps Factory commits; existing exact APK artifacts remain unchanged.
