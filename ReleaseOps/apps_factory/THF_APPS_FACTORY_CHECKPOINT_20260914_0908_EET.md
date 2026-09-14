# THF Apps Factory Checkpoint — 2026-09-14 09:08 EET

## Scope and authoritative baseline

Scope remained limited to THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass, shared identity/federation and cross-app handoffs. Dedicated native game streams and token finance were not modified.

Authoritative predecessor: `ReleaseOps/apps_factory/THF_APPS_FACTORY_CHECKPOINT_20260914_0812_EET.md`.

The run started from current `main` `1e41ead175700317cc5474ed486205b63986aa8d`, after reading the latest Apps Factory checkpoint and current ReleaseOps/mobile state. Same-SHA skip remained active: Core RC6 and the nine runtime-bound app candidates were not rebuilt because the checkpointed authoritative source/APK SHAs and their prior package/API36 gates did not change. All ten candidates remain `PENDING_PHYSICAL_PHONE`.

The newer apps-side installed-byte evidence hardening was also preserved: `ReleaseOps/THF_WAVE_LARGE_BATCH_20260914_0839_EVIDENCE.md` records successful run `34810279386` and requires the APK bytes actually installed on a physical phone to hash exactly to the registered candidate SHA before device promotion.

## Material gap found

The interactive `PassNotificationBridge` revalidated THF Pass before dispatch, but `NotificationDispatcher` itself only required an active notification registration. An internal/background producer capable of calling the dispatcher directly could therefore attempt delivery using a registration whose Pass session had since been revoked or expired, especially in the already-documented fail-secure case where Pass logout succeeded but notification-registry cleanup failed.

That gap meant session revocation was not an invariant of every provider-send path.

## Completed batch

Merged PR `#11` closes the bypass at the dispatcher boundary.

Implementation commits on the batch branch:

- `e2f41a8d25df77411788ea24b7d75c714e08cba9` — make a live session delivery guard mandatory inside `NotificationDispatcher` and invoke it before vault access/provider send.
- `e2db8d9e8952897eaba468bc895a1781693f9b37` — add `PassSessionDeliveryGuard`, validating live subject/session/package/expiry/revocation for background delivery.
- `71fbe5ae5a2afa5fab60c54843754d56c09e546d` — dispatcher regressions: guard required; authority rejection occurs before secure-token vault reads or adapter sends.
- `4bf99404a9ce97e6129fffdd1593b2b8df8d2a5f` — Pass bridge/background regressions proving revoked, expired and audience-mismatched sessions cannot deliver, including the cleanup-failure case where the registry row remains active.

PR `#11` merged to `main` as `dff1ca3bfdcc751452f8e17293c49bb5f6c3b742`.

## Verified behavior

PR workflow run `34811965125` — `THF Notification Session Scope Gate V1` — **SUCCESS**.

The job compiled the notification candidate and ran the complete lifecycle/HTTP/provider/dispatch/Pass bridge suite: **36 passed**.

Post-merge exact-commit checks on `dff1ca3bfdcc751452f8e17293c49bb5f6c3b742` are all **SUCCESS**:

- `notification-session-scope` — run `34812010492`;
- notification HTTP/provider `contract` — run `34812010494`;
- Apps Factory `validate` — run `34812010704`.

The dispatcher now fails closed unless the exact registration's Pass session is currently known, unrevoked, unexpired and bound to the same subject/package. This authorization happens before reading the provider token from `SecureTokenVault` and before invoking the provider adapter. Thus a failed logout cleanup can leave an inactive-cleanup task to reconcile later without allowing continued push delivery from that revoked session.

## Release truth

No FCM/APNs credential, KMS secret, public/staging endpoint, production signing material or Play rollout was introduced. No physical-device evidence was fabricated.

State remains:

- `PUSH_READY=FALSE`
- `PHYSICAL_DEVICE_PASS=FALSE`
- `FINAL_OR_PLAY_READY=FALSE`
- exact app candidates: `10`, all `PENDING_PHYSICAL_PHONE`

Remaining privileged/user-only gates remain unchanged: stable externally reachable trusted-TLS THF Pass staging; production FCM/APNs + real KMS/secret boundary; production signing/Play ownership/OAuth/2FA/billing/legal acceptance; and physical-phone install/launch/touch/layout/orientation/background-resume/offline-network/Data Saver/accessibility/RTL/20-language/core-journey/crash-free evidence for every exact APK SHA, plus notification permission/channel/receive/tap/deeplink evidence where applicable.

No dedicated native game stream or token-finance code was changed in this batch.
