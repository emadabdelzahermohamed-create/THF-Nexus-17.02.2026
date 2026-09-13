# THF Apps Factory checkpoint — 2026-09-13 23:15 EET

## Truth boundary

`FINAL_OR_PLAY_READY=FALSE`

Scope remains THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity, federation and cross-app handoffs. Dedicated native-game streams and token finance are excluded.

No production signing, public rollout, paid spend, owner identity verification, legal acceptance, treasury action or token signing was performed. WAVE was not modified.

## Same-SHA skip discipline

Core RC6 and the nine existing runtime-bound app APKs were not redundantly rebuilt. Their exact candidate/package/API36/runtime-binding evidence from the prior authoritative checkpoint remains unchanged because no regression evidence was found for those SHAs.

## Exact deployed auth-source snapshot

A new read-only source snapshot gate was added to bind lifecycle engineering to the exact currently deployed runtime implementation instead of inferred or stale source.

Workflow: `THF Pass Auth Candidate Source Snapshot V1`
Run: `34779491888`
Commit: `6e2aca91eec7b649675745157d93aa43f9242699`
Result: **SUCCESS**
Artifact: `THF-PASS-AUTH-CANDIDATE-SOURCE-SNAPSHOT-V1`
Artifact ID: `10324636220`
Artifact SHA-256: `5929bda9d81cbf7b0a268ca8164b87614bd2b7823ffb91334174f3669c8adaec`

The gate hashes and snapshots the deployed auth/router/database/runtime files and selected regression tests, verifies the local copy against the remote hashes, and asserts `MUTATION_PERFORMED=FALSE`, `WAVE_UNTOUCHED=TRUE`, `DEPLOYMENT_PERFORMED=FALSE`, `FINAL_OR_PLAY_READY=FALSE`.

## THF Pass lifecycle engineering candidate

The first two candidate attempts exposed only automation defects (`python` absent in favor of `python3`, then a generated-test quoting defect). Neither was treated as a product failure. Both were corrected automatically.

The corrected isolated candidate is `THF Pass Auth Lifecycle Candidate V2`.

Run: `34779846713`
Commit: `eefa9fb2f1de3a661d18bd2303c4dec21b6e4076`
Result: **SUCCESS**
Artifact: `THF-PASS-AUTH-LIFECYCLE-CANDIDATE-V2`
Artifact ID: `10325220782`
Artifact SHA-256: `0d8bb85d442dee0c686d701ec6ac9c4baa2830265daf8c779cc40a5821b6c20f`

Exact deployed source hashes used as the immutable baseline:
- `src/thf/app.py`: `471a8e0c6b67320386db6efcd32a3718265a645a30af3d7a9ea95060258058be`
- `src/thf/identity/service.py`: `8421a63db2e05bbd3b10b60da3edb0a3190ad7c2ea0498f4a1a704c3f7827b9f`

Disposable candidate hashes:
- candidate `app.py`: `d2eec7b71af0dfeadf7b2a7f7bdabff951174a8baa6b2b2f5baa718267be14bd`
- candidate `identity/service.py`: `97fe0a689681f1c0b578621f1df562cb616a18cb4d4f6273780a64558b30b6d5`

Candidate behavior proved in the disposable copy:
- bearer session refresh rotates the token and invalidates the old token;
- an old rotated token cannot be reused for another refresh;
- an expired session is rejected and cannot be refreshed;
- logout invalidates the current session;
- revoke-all invalidates concurrent sessions for the authenticated user;
- service-level and HTTP-level lifecycle tests pass;
- existing unified-runtime and security-boundary regressions remain green.

Test execution: **17 tests passed**.

This is engineering proof only. The deployed staging runtime was hash-checked after the test and remained unchanged. No lifecycle candidate was deployed. Consequently the live staging contract still does **not** claim refresh/logout/revoke/federation readiness.

## Exact-source notification contract inventory

A new exact-SHA notification inventory was run across Pulse, Forge, Echo, Codex, Spark, Rush, Vault, Signal and Command.

Workflow: `THF Apps Notification Contract Inventory V1`
Run: `34779880091`
Commit: `96e4100f4503ba0fb7bce4d9fca61997ea2bc7b9`
Result: **SUCCESS**
Artifact: `THF-APPS-NOTIFICATION-CONTRACT-INVENTORY-V1`
Artifact ID: `10325270137`
Artifact SHA-256: `977dbbc006354f923156a19fa58d0318d2417aa25abeb0b3748d10b4d8bacdff`

All nine exact authoritative source archives were SHA-verified and clean-extracted before scanning. The current sources show **no notification implementation evidence** for any of the nine apps: no `POST_NOTIFICATIONS` manifest permission, no Android notification API/channel implementation, no Firebase Messaging dependency/service/receiver, and no push-token registration implementation was detected. Every app is therefore truthfully classified `NONE` for notification source support in this inventory.

The inventory explicitly records `PROVIDER_DELIVERY_PROVEN=FALSE`, `PHYSICAL_DEVICE_PROVEN=FALSE`, `PUSH_READY=FALSE`, and `FINAL_OR_PLAY_READY=FALSE`.

This converts the previous generic notification blocker into an exact-source implementation gap. No app may be described as push-ready until a real notification contract is implemented where product requirements need it and provider delivery plus device behavior are proven.

## Current readiness / blockers

1. **THF Pass:** refresh/logout/revoke now have a tested reversible implementation candidate, but it has not been deployed to staging. Federation/cross-app handoff server semantics remain unimplemented/unproven. A later safe staging deployment must be candidate-hash-bound and rollback-protected before live auth claims change.
2. **Non-production credential-bound auth:** valid credential login/refresh/expiry/revocation against reachable staging is still not proven and requires a non-production test identity after lifecycle routes are deployed.
3. **Notifications:** all nine exact app sources currently lack notification implementation. Push readiness remains false.
4. **Spark/Rush testing:** real source unit-test debt remains; prior Gradle `NO-SOURCE` is not a unit-test PASS.
5. **Physical phone:** every exact runtime-bound APK SHA still requires install/launch/touch/responsive layout/orientation/accessibility/RTL/background-resume/offline-network/Data Saver/core-journey/crash-free acceptance.
6. Production signing, Play publication, legal acceptance and irreversible rollout remain owner-controlled later gates.

## Next autonomous executable block

- package the successful lifecycle implementation as a reproducible patch tied to the exact deployed source hashes, then run a reversible staging-candidate deployment rehearsal with explicit rollback without changing the current public endpoint;
- design and test federation/handoff semantics in the same disposable candidate boundary;
- add real Spark/Rush tests rather than accepting Gradle `NO-SOURCE`;
- define a shared notification interface and app-specific enablement policy before adding provider-specific push code, so apps that do not require push are not burdened with false functionality;
- preserve all current exact APK SHAs until source changes justify new candidates.
