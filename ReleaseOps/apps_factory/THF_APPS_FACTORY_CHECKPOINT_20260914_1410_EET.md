# THF Apps Factory Large-Batch Checkpoint — Durable Notification Vault Cleanup

## Authority and same-SHA skip
- Run-start `main`: `4b16957b10ac0fc78704ef0259c752977584b126`.
- The run-start tip belonged to the excluded token-finance stream and was not modified by this Apps Factory batch.
- Latest authoritative mobile evidence remains Apps Physical Device Evidence V10: validator `60fd52d4e80476c04385af748c0573cc92ff87cc`, regressions `b750c9c7c9de93f01d5cb5af38720a88f1d4da25`, CI gate `4bd6126a06e2f2d940003eab0d2a2c39ba6616db`, run `34833866209` SUCCESS.
- Exact app candidate bytes/source SHAs were not changed by this batch. The ten app candidates remain `PENDING_PHYSICAL_PHONE`; no unchanged APK/AAB was rebuilt or re-promoted.

## Material finding
Notification revoke/rotation made registrations inactive before deleting provider-token material from the secure vault. If vault deletion failed, delivery remained fail-closed because the DB registration was inactive, but raw provider-token material could remain orphaned with no durable cleanup/retry record.

## Repair
PR #15 added durable provider-token cleanup without persisting raw credentials:
- `cd9e95ec36b7d211a4eb2568e6d65587d17d06ae` — lifecycle implementation.
- `bfee3ba9b070a91d2f7ec9810c7c51762c864059` — regression coverage.
- Merge commit: `d5aa07d8cf48980dbccab9f77283f7a992b4a9bc`.

The lifecycle now:
- journals only opaque `token_id` plus bounded operational error metadata when vault deletion fails;
- retries cleanup through a bounded drain operation;
- never stores provider token material or token fingerprint in the cleanup journal;
- cancels stale cleanup before reactivating the same deterministic registration;
- refuses to delete vault material when a stale journal row points at an active registration;
- rejects rotation to an already-active destination without mutation;
- preserves session/package scoping and fail-closed delivery authority.

## Evidence
PR GitHub Actions run `34836471074`: SUCCESS.
Post-merge GitHub Actions run `34836585470` on exact merge commit `d5aa07d8cf48980dbccab9f77283f7a992b4a9bc`: SUCCESS.
- Python 3.12 compile: PASS.
- Notification lifecycle/HTTP/provider/dispatch/Pass bridge regression suite: `42 passed`.
- Release-truth step explicitly preserved:
  - `PUSH_READY=FALSE`
  - `PHYSICAL_DEVICE_PASS=FALSE`
  - `FINAL_OR_PLAY_READY=FALSE`

## Remaining non-substitutable gates
- Physical Android phone evidence remains required for each exact APK SHA: install, launch, touch, responsive layout/orientation/safe area, same-process background/resume, offline/network transition, accessibility, Data Saver, RTL/20-language behavior, core journey, crash-free, and notification receive/tap/deeplink where applicable.
- Stable trusted HTTPS/WSS THF backend/Pass endpoint and exact health/auth/session/federation evidence remain required for network release readiness; a temporary Quick Tunnel is not a production endpoint.
- Real FCM/APNs delivery still requires approved provider credentials behind a production KMS/secret boundary.
- Production signing/final AAB, Play App Signing/ownership/Internal-track acceptance, legal approval, and public production cutover are not claimed.
- `main` remains without enforced required-status branch protection; repository-admin governance action is still needed.

## Rollback
Revert merge commit `d5aa07d8cf48980dbccab9f77283f7a992b4a9bc` to restore the prior lifecycle. The cleanup table is additive and contains no raw provider secrets; leaving an unused table after rollback does not make an inactive registration deliverable.

## Isolation
No dedicated native game implementation, token-finance implementation, production signing, Play rollout, public deployment, or provider credential was modified in this batch.

Body SHA-256 (content above this line): `9eccc9c6fb6444b2cf753dbcaae058db1fb3199e9435206565946b63c7e95a1a`
