# THF Apps Factory Checkpoint — 2026-09-13 21:20 EET

## Truth boundary

Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, shared THF Pass/federation and cross-app handoffs. Dedicated native game streams and token finance are excluded.

`FINAL_OR_PLAY_READY=FALSE`

No production signing, public rollout, paid spend, legal acceptance, token/treasury signing or native-game change was performed. Exact-candidate physical-phone acceptance remains mandatory before FINAL/PLAY_READY.

## Authoritative release state preserved

Core RC6 remains unchanged at APK SHA-256 `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`; its same-SHA package/runtime gates were not rerun because no regression evidence exists.

The nine non-Core authoritative source checkpoints remain:

- Pulse RC3 — `71a16804e7c138535bb373263ae4374d8a5eef410ffe83b165472c684b6c8b10`
- Forge RC3 — `0f7a416a9e14af9dbb3cdcb26bfb891e0c680d4a33a73d60601eda215e697e51`
- Echo RC4 — `87c6a532fc56870b9a4c1039ac1f44b43e1a2f4c5c4518caf0d6537c61704226`
- Codex RC4 — `c5108b257b5e9af6849c43df7b7aa671e586bb4a9c91964566c85b1a6329e83d`
- Spark RC3 — `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0`
- Rush RC3 — `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b`
- Vault RC4-BF1 — `dd6db86d7532f773a8d1d2662bf466bdcc0f1c64a863602ecdd1267c8f82fa33`
- Signal RC4-BF1 — `377044263fa0fc366afe67c6b42ccf4f3e2d1bc75769350f2ee885983f820ddf`
- Command RC3 — `f7da9039041b8142d795e96934b95f00b83ac8fb5e3d6f5d9bfbff0aeb2eb408`

## Block A — exact-source backend transport audit

Workflow `THF Apps Backend Reachability V1`, run `34773438267`, completed SUCCESS after re-hashing the exact authoritative archives.

Literal shipping-source HTTPS origins that were discoverable all responded at the transport layer: WHO, PubMed and esm.sh for Pulse; Solscan for Vault and Command; Telegram API for Signal. `UNREACHABLE_LITERAL_ORIGIN_COUNT=0`.

This is not THF backend auth proof. Forge, Echo, Codex, Spark and Rush emitted no literal HTTPS origin from the runtime URL scanner, indicating their effective service configuration may be injected through BuildConfig/configuration rather than source literals. Candidate-bound THF health/auth/session remains unresolved for those paths. HTTP 401/403/404-class responses count only as transport reachability, not user-flow success.

## Block B — Spark/Rush regression execution

The exact-source Spark/Rush lane was repaired safely to provision Gradle 8.13 and detect module-qualified tasks. Final remediation commit: `02b30e7405fb5d7364cc7010f30b542b125d4b81`.

Run `34773691664` completed SUCCESS for both Spark RC3 and Rush RC3. For each exact source, the lane executed:

- `app:testReleaseUnitTest`
- `app:testDebugUnitTest`
- `app:lintRelease`
- `app:lintDebug`
- `app:assembleRelease`

The two unit-test tasks complete as `NO-SOURCE`; therefore this run proves Android compile/lint/release-assembly regression coverage, but it does **not** prove real unit-test coverage. The prior `NO_TESTS` debt remains truthful until real test sources are added. Spark also emits deprecated-API warnings in `MainActivity.java`, and the Android build reports Gradle features that will require cleanup before Gradle 9 migration. These are tracked engineering debt, not grounds for readiness promotion.

Artifacts:

- Spark regression artifact id `10322956989`, ZIP digest `sha256:e892d9a0cd648eac4744f59d1a6919ae08fa556b6fc5209c6b95ccff5f560470`
- Rush regression artifact id `10322627891`, ZIP digest `sha256:8be740da37e01d671c8a17961b850bc9e72ad1a3ddbe347bd7f6bad79bf6867c`

## Block C — identity, session and cross-app handoff audit

Added a fail-closed shipping-source auditor plus regression tests and fixed a false-positive detector so normal in-memory token assignments are not confused with URL query leakage. Final auditor commit: `44953e908c3583cb61d7623cedba30028e01a59b`.

Workflow run `34773752897` completed SUCCESS, including validator regression tests, exact Drive source SHA verification, nine-app audit, and evidence artifact upload.

Across all nine exact authoritative sources, the audit found source surfaces for secure storage, THF Pass/federation binding, cross-app handoff send/receive behavior, no sensitive token/session query-string transport pattern, and no cleartext HTTP/WS runtime endpoint pattern.

However, **all nine fail the complete session-lifecycle source contract** because no logout/revocation implementation evidence was detected. Additional gaps are more severe in several apps:

- Command, Vault and Signal show no meaningful auth/session/expiry source surface in the audited shipping runtime.
- Pulse has extensive session-related state but no complete auth/expiry/logout-revocation lifecycle surface.
- Forge, Echo, Codex, Spark and Rush expose partial auth/session/refresh-related surfaces but still lack logout/revocation evidence.

Therefore THF Pass/shared identity/federation is **not complete and must not be promoted**. A source contract is also not proof that a live identity backend accepts authentication or that a physical cross-app handoff works.

Identity audit artifact id `10322338825`, ZIP digest `sha256:321842fea8a721e15bea8ae66fc0150a287fbba6d6c1fe1bc8bff331b02874ed`.

## Current blockers and next executable work

1. Add regression-protected logout/revocation/expired-session behavior to the app identity contract before shared federation can be considered functionally complete; preserve secure-storage and handoff behavior already present.
2. Resolve effective candidate-bound `THF_BASE_URL` / `THF_PASS_URL` or equivalent generated configuration and prove reachable HTTPS health/auth/session against the actual service, not public reference/provider URLs.
3. Add real Spark/Rush unit or integration test sources; current Gradle unit-test tasks are `NO-SOURCE` even though lint and assembly pass.
4. Audit and then implement/repair notification/push behavior where absent, without introducing fake notification state.
5. Exact physical-phone evidence is still required for install, launch, touch, responsive layout/orientation, background-resume, genuine offline/network transition, core journey and crash-free smoke for each exact APK SHA.
6. Production signing, Play release, legal acceptance and any irreversible rollout remain owner-controlled gates.

All new work is isolated in reversible Git commits and does not mutate validated source archives or production infrastructure.
