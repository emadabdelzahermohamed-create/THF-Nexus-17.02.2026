# THF Apps Factory Checkpoint — 2026-09-14 08:12 EET

## Scope and authoritative baseline

This batch is limited to THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass, shared identity/federation and cross-app handoffs. Dedicated native game streams and token finance were not touched.

Authoritative predecessor: `ReleaseOps/apps_factory/THF_APPS_FACTORY_CHECKPOINT_20260914_0715_EET.md`.

Same-SHA skip remained active. Core RC6 and the nine runtime-bound application candidates were not rebuilt because their authoritative source/APK SHAs and previously proven package/API36 gates did not change. All ten candidates remain `PENDING_PHYSICAL_PHONE`.

## Completed batch

A correctness/security gap was closed in the provider-neutral notification candidate: notification registrations were previously scoped by subject + package but not by the exact THF Pass session. That could make logout from one live session revoke registrations belonging to another live device/session of the same subject/package.

The merged implementation now:

- binds registration IDs and ownership to `subject + session_id + package + provider + fingerprint`;
- requires exact session ownership for register/rotate/revoke/dispatch/logout;
- keeps parallel Pass sessions isolated even for the same user/package/provider token;
- preserves live Pass re-validation before every notification mutation or dispatch;
- preserves Pass-first fail-secure logout, but token cleanup now affects only the logging-out session;
- keeps raw provider tokens outside the registry DB behind `SecureTokenVault`;
- retains provider delivery as non-production candidate behavior only; no FCM/APNs credential was introduced.

## Migration hardening

The previous SQLite schema had `UNIQUE(subject, package, provider, fingerprint)`. A simple `ALTER TABLE ADD session_id` would have left that old uniqueness constraint in force and broken same-token registration across two Pass sessions.

The migration now rebuilds the table atomically with `UNIQUE(subject, session_id, package, provider, fingerprint)`. Existing rows are retained under `__legacy_unbound__` and therefore remain fail-closed until explicitly re-registered by an authenticated live session. Regression coverage proves the legacy row is inaccessible and that two new sessions can subsequently register the same provider token independently.

## Regression and CI evidence

Permanent workflow added: `.github/workflows/thf-notification-session-scope-gate-v1.yml`.

CI infrastructure bootstrap on main: commit `626d33eaffc22f36c397ead824478973f6fccf63`; run `34808642670` = SUCCESS.

PR `#10` head `0deb3c9e8911c0e2228edf54b8b8e3ae04918a44`; run `34808691421` = SUCCESS. Python 3.12 compile PASS; notification lifecycle/HTTP/provider/dispatch/Pass-bridge suite = `32 passed`.

PR `#10` merged to main as `d8f9064eb2e9c4b3e5c4f4df2373d6016da93288`.

Post-merge run `34808719153` = SUCCESS. Python 3.12 compile PASS; same suite = `32 passed`.

The gate explicitly emits:

- `PUSH_READY=FALSE`
- `PHYSICAL_DEVICE_PASS=FALSE`
- `FINAL_OR_PLAY_READY=FALSE`

## Release truth / blockers unchanged

This batch does not establish FCM/APNs production delivery, a production `SecureTokenVault` KMS boundary, stable externally reachable trusted-TLS THF Pass staging, production signing, Play Internal rollout, or physical-phone acceptance.

Remaining user/privileged gates are exact and unchanged:

1. A physical Android device must test each exact APK SHA for install/launch/touch/responsive layout/orientation/background-resume/offline↔network/Data Saver/accessibility/RTL/20-language core journeys/crash-free evidence; notification-capable candidates additionally require permission/channel/receive/tap/deeplink evidence.
2. THF Pass still needs a stable externally reachable non-public HTTPS staging endpoint with trusted TLS and deployment credentials before lifecycle/federation can be called staging-live.
3. Production push requires approved FCM/APNs credentials plus a real KMS/secret boundary and reachable authenticated provider registration/delivery infrastructure.
4. Production signing, Play Internal, OAuth/2FA, billing and legal acceptance remain owner/user-only gates when promotion is attempted.

No public endpoint was changed, no production rollout was performed, and no dedicated native game stream or token-finance code was modified.
