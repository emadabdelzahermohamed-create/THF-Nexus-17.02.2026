# THF Apps Factory checkpoint — 2026-09-14 03:10 EET

`FINAL_OR_PLAY_READY=FALSE`

Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault UX, Signal, Command, THF Pass/shared identity/federation/handoffs. Dedicated native game streams and token finance were not mutated.

## Same-SHA preservation
- Core RC6 and all nine runtime-bound Android candidates retain their previously proven package/API36/runtime-binding evidence; no redundant rebuild was performed.
- Exact source/APK identities remain those recorded in `THF_APPS_FACTORY_STATE_20260913_2035_EET.json`.
- Physical-phone acceptance remains PENDING for every exact APK candidate.

## Notification lifecycle engineering block
Implemented a provider-neutral server-side registration lifecycle candidate at `ReleaseOps/apps_factory/notification_lifecycle.py` and bound it to all nine exact authoritative source SHA-256 values in `THF_NOTIFICATION_LIFECYCLE_CANDIDATE_20260914.json`.

Implemented semantics:
- authenticated subject required;
- locked THF package allowlist;
- provider token registration;
- token rotation with old-token revocation and generation increment;
- logout-scoped revocation;
- cross-subject access fails closed;
- raw provider tokens are not stored in the registry database;
- token custody is delegated to an opaque `SecureTokenVault` boundary so no home-grown crypto or committed credential is introduced.

Truth boundary:
- provider delivery is intentionally NOT implemented;
- `PUSH_READY=FALSE`;
- physical receive/tap/background-resume is NOT proven;
- this candidate does not change the existing exact APK candidates.

Regression suite: `ReleaseOps/apps_factory/tests/test_notification_lifecycle.py` covers registry-vs-vault custody, locked package/auth enforcement, rotation, cross-subject isolation, logout scoping and explicit absence of fake provider delivery.

CI: `.github/workflows/thf-notification-lifecycle-candidate-v1.yml` compiles the candidate, executes regressions and enforces `PUSH_READY=FALSE`/`FINAL_OR_PLAY_READY=FALSE` plus nine-app API36 binding.

The first CI execution (`34791629282`) failed in the test loader before product assertions because Python 3.12 `dataclass` requires the dynamically loaded module to be present in `sys.modules`. This harness defect was diagnosed from job logs and fixed in commit `ca9b2bd6f3685fe4fe1c58d740599b17ffd1fd4c`; the corrected run `34791684762` was queued at checkpoint time. This is tracked as CI/tooling state, not a product PASS.

## Checkpoint commits
- `4114f863529294bd8392cb882024d0c033330f15` — provider-neutral lifecycle candidate.
- `56e250bd67964302e4baa20bcfa75bd187ba6ade` — lifecycle regression suite.
- `42820041ae14218434ff6280b8bd961a414cb4fc` — CI gate.
- `fc1abcc193938f809b3960a24f4b75c547a03cce` — exact-source/API36 lifecycle registry.
- `ca9b2bd6f3685fe4fe1c58d740599b17ffd1fd4c` — Python 3.12 test-loader repair.

## Remaining truthful blockers
1. THF Pass has isolated HTTPS lifecycle/federation rehearsal evidence, but stable externally reachable non-public trusted-TLS staging remains unproven and must not be reported staging-live.
2. Notification provider adapter/configuration and authenticated reachable registration endpoints are not yet wired to authoritative app candidates; provider delivery remains unproven.
3. A production-grade encrypted `SecureTokenVault` implementation needs an approved runtime secret/KMS boundary; no secret or credential is committed here.
4. Physical-phone evidence remains mandatory for install/launch/touch/layout/orientation/background-resume/offline-network/Data Saver/accessibility/RTL/core journey/crash-free, and for notification receive/tap behavior.
5. Production signing, AAB/Play Internal, legal/OAuth/2FA and irreversible rollout remain outside this checkpoint.

## Next executable block
After the corrected lifecycle CI is green, wire a credential-free HTTP contract around the registry for authenticated Pass sessions in an isolated rehearsal, add provider-adapter interface conformance tests without sending real notifications, and extend device-evidence manifests to capture notification permission/channel/deeplink/background-resume truth for exact APK SHAs. Stable trusted external Pass staging remains dependent on an approved non-public runtime target and TLS boundary.
