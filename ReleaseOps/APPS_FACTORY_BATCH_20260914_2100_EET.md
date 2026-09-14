# THF Apps Factory — large-batch checkpoint — 2026-09-14 21:00 EET

## Scope
THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault UX, Signal, Command, THF Pass, shared identity/federation and cross-app handoffs. Dedicated native game streams and token finance are excluded.

## Authority / same-SHA policy
- Started from `main` at `a5b1bf27fd8bdae6e3e0d6d9cd4aa34aa3a80373`.
- Preserved the latest Apps durable candidate authority from PR #24; no candidate APK/source bytes were rebuilt merely to create activity.
- Existing candidate/package/API-36 evidence for unchanged SHAs remains preserved; physical/network/final truth is not promoted.

## Engineering completed
- Added `ReleaseOps/apps_factory/pass_handoff_receiver.py`.
- Added cryptographic verifier boundary: receiver cannot accept caller-declared verified truth; deployment must supply a verifier implementation.
- Enforced trusted issuer, exact installed-package audience, known THF package allowlist, cross-app source/target separation, constant-time state comparison, nonce replay prevention, short-lived handoff TTL, clock-skew bounds, per-target scope allowlists, and target-bound `thf://<app>/...` return routes.
- Added SQLite-backed one-time replay journal and package-bound federated session store with revocation/expiry/binding enforcement.
- Offline handoff contract cannot establish economy/social/ranked/tournament write truth; those scopes are not part of any app handoff allowlist.
- The shared package map covers Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault, Signal and Command.

## Cross-module integration completed
- Added integration coverage proving a THF Pass federated session can authorize notification registration/dispatch through the existing Pass notification bridge.
- Proved revoking the Pass federated session blocks background dispatch even while the notification registration still exists.
- Proved a Pulse handoff session cannot be replayed as a Forge principal.

## Commits
- `e778794651c5163d6ec041f630b54958bc12268d` — receiver/session/replay implementation.
- `73adba39c14bfbbf52383a155f7742b10fb63e27` — fail-closed receiver regressions.
- `1b2568013e39424ded4f1ac3d0b7381f087fbce3` — notification/federation integration regressions.
- `9d8ad712332c199301f3de313a06509efd7c3973` — CI gate.

## CI evidence
Workflow: `THF Pass Handoff Receiver V1`
Run: `34878360606`
Exact head SHA: `9d8ad712332c199301f3de313a06509efd7c3973`
Result: **SUCCESS**.
Steps passing: compile, handoff receiver fail-closed regressions, cross-module federation integration.

## Release truth after this batch
- `THF_PASS_HANDOFF_RECEIVER_CONTRACT=PASS_CI_CANDIDATE`
- `THF_PASS_CRYPTOGRAPHIC_DEPLOYED_VERIFIER=NOT_PROVEN`
- `THF_PASS_REACHABLE_HTTPS_WSS_BACKEND=NOT_PROVEN`
- `NETWORK_RELEASE_READY=FALSE`
- `PUSH_READY=FALSE`
- `PHYSICAL_DEVICE_PASS=FALSE`
- `FINAL_OR_PLAY_READY=FALSE`

## Remaining external / user-only gates
A stable trusted-TLS THF Pass/backend endpoint with real health/auth/session/federation must deploy the verifier boundary; FCM/APNs credentials must remain inside the approved KMS/secret boundary; every exact production candidate still requires physical-phone install/launch/touch/layout/background-resume/offline-network/core-journey/crash-free/accessibility/Data Saver/RTL/20-language evidence before FINAL/PLAY_READY; production signing, Play Console declarations/legal acceptance and rollout remain user-controlled gates.

## Rollback
Revert commits `9d8ad712332c199301f3de313a06509efd7c3973`, `1b2568013e39424ded4f1ac3d0b7381f087fbce3`, `73adba39c14bfbbf52383a155f7742b10fb63e27`, and `e778794651c5163d6ec041f630b54958bc12268d` in reverse order. No application candidate APK/source bytes are affected by this rollback.
