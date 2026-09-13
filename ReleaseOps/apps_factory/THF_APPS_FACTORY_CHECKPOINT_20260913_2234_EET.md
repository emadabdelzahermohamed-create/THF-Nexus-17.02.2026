# THF Apps Factory checkpoint — 2026-09-13 22:34 EET

## Truth boundary

`FINAL_OR_PLAY_READY=FALSE`

Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity, federation and cross-app handoffs. Dedicated native-game streams and token finance remain excluded.

No production signing, public rollout, paid spend, owner identity verification, legal acceptance, treasury action or token signing was performed. WAVE was not modified.

## Same-SHA skip discipline

Core RC6 remained on exact APK SHA-256 `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`; its already-proven same-SHA gates were not rerun because no regression evidence was found.

The nine Apps source archives were also not redundantly rebuilt after their exact runtime-configured candidate gate had already passed on unchanged source SHAs.

## Authoritative runtime-bound candidate state

The authoritative factory state was advanced to schema 2 and now points to the runtime-configured exact staging candidates instead of the older endpoint-unbound QA APKs. The state retains each previous unbound SHA for regression comparison and requires that no runtime-bound candidate aliases it.

Current runtime-bound QA APK SHA-256 values:

| App | Source checkpoint | APK SHA-256 |
|---|---|---|
| Pulse | RC3 | `e043b5555f793d4bd226b865c8a5a400068d05948f1104583f5e9f2e028607dc` |
| Forge | RC3 | `c93b26b2b59b0f09671ecf632bbc3304e27b52e7b0d07470ee284e5a565cd8b5` |
| Echo | RC4 | `ddc0c48ec0c149d2f6ab424f9b6576f64a0c7888f021771076ff32b3a9728d94` |
| Codex | RC4 | `cad4bed914e006c294ddbd37fcebbf9ef2f4c9baac161f852e7c6d2433d3884c` |
| Spark | RC3 | `92bc7f913d560a185044af2df7b1955d3a0b29eca920034edf3cd9741bce0c23` |
| Rush | RC3 | `304164035cc4b82d23e2b2e6bf48abca3c466c46f5668a203cf0b4cfca223e99` |
| Vault | RC4-BF1 | `76e20915e4bc6dee23adf43fdfcca9705815cf990164ccb8649032118dd42ce0` |
| Signal | RC4-BF1 | `9d370142a251c2515fe19e7598a35213e8285fab4ed74f804d88ea6b5a21f05a` |
| Command | RC3 | `b556e1aaa622de044aa6de609c9911aff5def3d738146c57ae3b8a842777958c` |

These candidates retain package identity, targetSdk 36, QA signature/non-debuggable inspection and non-empty HTTPS runtime binding evidence from workflow run `34777489771`; shared staging health is PASS. They are not production-signed and are not physical-device accepted.

## Stronger ReleaseOps consistency gate

The factory-state validator was upgraded to fail closed on:

- schema regression away from runtime-bound candidate state;
- missing shared staging health or endpoint binding;
- false auth/THF Pass promotion;
- production cutover or WAVE-isolation drift;
- invalid evidence workflow/commit/artifact digest;
- current APK SHA aliasing the older endpoint-unbound QA SHA;
- package identity or API 36 drift;
- fabricated physical-device PASS.

Regression coverage was expanded for the new invariants. `THF Apps Factory State Gate` run `34777887082` completed SUCCESS: authoritative-state validation and regression tests both passed.

## Live THF Pass / shared identity semantics

A new fail-closed live probe and regression suite were added. It uses only safe malformed/anonymous requests, compares candidate paths with a randomized not-found control so SPA/static fallbacks cannot count as API evidence, and never uses or creates a real user identity.

The first CI attempt exposed only a Python dynamic-import/dataclass test-harness defect; it was fixed and not misreported as a product failure.

Corrected workflow run `34777926029` completed SUCCESS. Regression tests: `5 passed`.

Live reversible staging observations:

- `/health` JSON semantics: **PASS** (`ok=true`);
- distinct login/token-like route surface: **DETECTED**;
- refresh surface: **NOT DETECTED**;
- logout surface: **NOT DETECTED**;
- server-side revoke surface: **NOT DETECTED**;
- federation/handoff surface: **NOT DETECTED**;
- complete identity lifecycle surface: **FALSE**;
- valid credential login: **NOT PROVEN**;
- refresh/expiry semantics: **NOT PROVEN**;
- logout/revocation semantics: **NOT PROVEN**;
- cross-app federation success: **NOT PROVEN**.

Evidence artifact: `THF-PASS-LIVE-SEMANTICS-PROBE-V1`, artifact ID `10324232850`, SHA-256 `9bd6a61c6efaca5a15607537a8b2d4434f021c6bf139f370ac8b761fcd2eeb61`. A durable ReleaseOps evidence record was committed at `ReleaseOps/apps_factory/THF_PASS_LIVE_SEMANTICS_20260913_2232_EET.json`.

This converts the THF Pass blocker from an ambiguous “OpenAPI unavailable” condition into a specific runtime gap: health and a login-like surface exist, but the required refresh/logout/revoke/federation lifecycle is not present or not reachable at the currently bound staging paths.

## Existing evidence retained, not re-run without cause

Prior exact-source audits remain authoritative for unchanged source SHAs: no detected runtime placeholder or cleartext transport URLs, source evidence for local/offline and Data Saver/network handling, cross-app handoff wiring, and zero detected orphan visible actions after regression-protected source analysis. Those are source/wiring evidence only and do not replace physical touch or successful backend-flow evidence.

## Open engineering / release blockers

1. **THF Pass lifecycle:** implement or expose a reversible staging contract for refresh, logout, server-side revocation and federation/handoff; then add expiry/refresh/logout/revoke integration tests. Current login-like route detection alone is insufficient.
2. **Credential-bound auth test:** after the lifecycle exists, a non-production test identity/service credential is required to prove valid login, refresh, expiry and revocation. No production credential should be used.
3. **Spark/Rush test debt:** exact sources still have no real unit-test source suites; Gradle `NO-SOURCE` must never be reported as unit-test PASS.
4. **Notifications:** no app may claim push readiness until registration, permission/channel, receiver/service and provider-delivery behavior is proven where the product requires notifications.
5. **Physical-phone gate:** the exact runtime-bound APK SHA for each app must pass install, launch, touch, responsive layout/orientation, accessibility/RTL checks, background-resume, genuine offline↔network transitions, Data Saver behavior, core user journey and crash-free smoke. This remains a device-only action.
6. Production signing, Play Console publication, legal acceptance and irreversible rollout remain later owner-controlled gates.

## Next autonomous execution block

- inventory the staging/runtime implementation behind the detected login surface and locate the safest authoritative source for missing refresh/logout/revoke/federation routes;
- add fail-closed session lifecycle integration contracts before any auth readiness promotion;
- add real Spark/Rush unit-test sources or candidate-bound integration tests where source architecture supports them;
- build a notification contract inventory that separates local notification support from real provider push delivery;
- keep current exact candidate SHAs fixed until source/runtime changes justify a new candidate build.
