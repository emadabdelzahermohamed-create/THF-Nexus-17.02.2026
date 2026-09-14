# THF Applications Factory — private apps identity/RBAC checkpoint — 2026-09-14 23:00 EET

## Scope
This batch is restricted to THF Hub/Core, THF Market/Forge, THF Community/Echo, THF Learn/Codex, THF Wallet/Vault, private THF Publisher/Signal, private THF Admin/Command and THF Identity integration surfaces. THF Fitness/Pulse application work, all game code, token finance and WAVE are excluded.

## Authoritative lineage / same-SHA policy
- Run baseline was re-resolved to `main` commit `60d00c1c2b026fbd47036daa17b9670f460030c2` after concurrent release work moved the branch.
- Vault durable authority remained unchanged: package `com.topherofit.thf.vault`, targetSdk 36, source SHA-256 `052e2c55c6066c15eee63528218b8eab9711bec9de71335c67c7e1692a5b5432`, APK SHA-256 `7431987b0be9589f997d505cfe69c6d3e217deb7d2783c44f99e6f263693209e`.
- Signal durable authority remained unchanged: package `com.topherofit.thf.signal`, targetSdk 36, source SHA-256 `f78890c3bf036d80a568ec39baac4a665d6092b9bbc8c4f080f2651785c1a275`, APK SHA-256 `c7eb1044426423862687f93a875208a5ea8c5703d4978efb93eb4b54a1555d75`.
- Those exact candidate bytes were not rebuilt merely to create activity; prior payload and clean-extract integrity PASS remains preserved for the same SHAs.
- No newer authoritative candidate/source SHA for Core, Forge, Echo, Codex or Command was proven during this batch; existing validated evidence was preserved rather than replaced by source-only or template-only output.
- After the RBAC merge, concurrent phone-QA work advanced `main` to `77c12b4e44ab03c61db8b43db991a3cd0b09b462`, whose parent is the RBAC merge; no branch rewind or overwrite was performed.

## Release blocker found
The existing THF Pass federation receiver correctly enforced verified issuer, package audience, nonce replay, state, scope, route and session binding, but its verified handoff/session model carried no server-authoritative role claims. Therefore a private Signal/Command boundary could not prove publisher/admin authorization independently of hidden UI. This was treated as an auth/RBAC safety blocker.

## Engineering completed
PR #25 added fail-closed private-app RBAC to the THF Identity/Pass receiver:
- `VerifiedHandoff` now carries verifier-supplied role claims; caller/UI visibility is not authorization.
- Accepted role vocabulary is limited to `user`, `publisher`, `admin`; unknown role claims fail closed.
- Signal (`com.topherofit.thf.signal`) requires a verified `publisher` or `admin` role.
- Command (`com.topherofit.thf.command`) requires an explicit verified `admin` role.
- Both private applications require online authority; offline handoffs cannot establish private operator access.
- Federated sessions persist the verified role set and re-check private-app RBAC on authorization.
- Admin may satisfy publisher authorization for Signal, but publisher never satisfies Command admin authorization.
- Legacy V1 session databases migrate with an empty role set, so pre-RBAC sessions do not inherit private access.
- Call sites cannot invent an unknown required role.

Meaningful checkpoints:
- `c0b3ac86c588a7f896a55bf89f0740b77593ed9a` — role-aware Pass receiver/session persistence and fail-closed private RBAC.
- `807025315a3543f58f8efddea82e665319b88a7d` — private Signal/Command RBAC regression suite.
- `02393a0a21bab6325f8fccfdd47471f88dae74d2` — CI gate wiring.
- PR #25 merged as `9a7fea60d49ba9bb992f9698f7b7490c57a49a54`.

## Test evidence
PR workflow `THF Pass Handoff Receiver V1`, run `34890775394`, exact head `02393a0a21bab6325f8fccfdd47471f88dae74d2`: SUCCESS.
Passing stages: Python compile, existing handoff fail-closed regressions, new private Signal/Command RBAC regressions, cross-module federation/notification integration.

Post-merge evidence on exact merge SHA `9a7fea60d49ba9bb992f9698f7b7490c57a49a54`:
- `THF Pass Handoff Receiver V1` run `34890814022`: SUCCESS.
- `THF Apps Factory State Gate` run `34890814049`: SUCCESS.
- `THF No Arbitrary Artifact Size Cap V1` run `34890814149`: SUCCESS.

## Phone-source audit retained, not promoted
The current Vault/Signal native candidate generator already preserves package IDs, uses user-facing names `THF Wallet` and `THF Publisher`, marks Signal internal-only, supports RTL layout direction, Data Saver/network status, notification permission, Android Keystore/AES-GCM local storage, HTTPS-only backend health probing, and refuses fake THF Pass handoff when Pass is unavailable.

The following requested phone fundamentals are still NOT PROVEN for the authoritative candidate bytes and are not promoted by this batch:
- adaptive launcher icon resource set;
- Android 13+ monochrome themed icon;
- 512x512 store-icon asset bound to release provenance;
- complete Arabic/English resource localization and 20-language resource readiness (the current native QA surface still contains hard-coded English UI strings);
- deployed Android client binding to the new role-aware Pass session contract;
- ordinary-user invisibility of Signal/Command at the real distribution/catalog layer;
- reachable trusted production/staging backend proving health + cryptographic auth/session/federation + role claims;
- physical-phone install/launch/touch/layout/background-resume/offline/network/core-journey/crash-free/accessibility evidence.

These are deliberately recorded instead of being represented as UI-only/mock PASS.

## Release truth
- `PRIVATE_SIGNAL_COMMAND_RBAC_CONTRACT=PASS_CI_CANDIDATE`
- `PRIVATE_SIGNAL_COMMAND_RBAC_DEPLOYED_BACKEND=NOT_PROVEN`
- `PRIVATE_SIGNAL_COMMAND_DISTRIBUTION_INVISIBILITY=NOT_PROVEN`
- `ADAPTIVE_MONOCHROME_STORE_ICON_SET=NOT_PROVEN`
- `AR_EN_20_LANGUAGE_RESOURCE_READINESS=NOT_PROVEN`
- `NETWORK_RELEASE_READY=FALSE`
- `PUSH_READY=FALSE`
- `PHYSICAL_DEVICE_PASS=FALSE`
- `FINAL_OR_PLAY_READY=FALSE`

## External/user-only gates
A stable trusted-TLS THF Pass/backend deployment must cryptographically verify and issue the role claims consumed by this contract. Signal/Command must additionally be restricted by real internal distribution/catalog policy rather than launcher/UI hiding alone. Production signing/provider credentials must remain in approved secret/KMS boundaries, and exact-candidate physical-phone evidence remains mandatory before FINAL/PLAY_READY.

## Rollback
Revert merge commit `9a7fea60d49ba9bb992f9698f7b7490c57a49a54` to remove this RBAC batch. This rollback does not change the preserved Vault/Signal canonical candidate source or APK bytes.
