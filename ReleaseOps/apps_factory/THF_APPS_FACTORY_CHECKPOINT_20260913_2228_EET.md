# THF Apps Factory checkpoint — 2026-09-13 22:28 EET

## Truth boundary

`FINAL_OR_PLAY_READY=FALSE`

Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity and cross-app handoffs. Dedicated native-game streams and token finance remain excluded.

No production signing, public rollout, paid spend, legal acceptance, owner identity verification, treasury action or token signing was performed.

## Same-SHA skip discipline

Core RC6 exact APK SHA-256 remains `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`. Its proven same-SHA gates were not rerun because no regression evidence was found.

## Major defect discovered and contained

A generated-BuildConfig audit proved that the prior exact QA candidates for all nine Apps streams were compiled with both `THF_BASE_URL` and `THF_PASS_URL` present but empty. Therefore previous package/API36/signature PASS evidence was **not** accepted as network-runtime readiness.

The diagnostic default-binding run was `34776966890`; all 9 rows had `binding_gate_pass=false`.

A fail-closed validator and regression suite now enforce non-empty secure HTTPS/WSS runtime endpoint bindings in generated Android `BuildConfig` while explicitly not claiming reachability/auth/device proof.

## Safe staging recovery

The existing THF runtime at the GCP builder was verified healthy locally and through its existing reversible Cloudflare Quick staging endpoint. The refresh gate `34777215659` returned:

- `status=PASS`
- `health=PASS`
- `endpoint_class=cloudflare_quick_staging`
- `endpoint_refreshed=false`
- `production_cutover=false`
- `wave_untouched=true`

Thus no production endpoint was changed and WAVE remained isolated.

Two CI-only defects in the staging candidate lane were fixed automatically: nested SSH quoting and treating a 200 non-JSON `/openapi.json` response as valid OpenAPI. Neither was misreported as an app/runtime failure.

## Runtime-configured exact staging candidates

Workflow `THF Apps Runtime Configured Staging V1`, run `34777489771`, commit `87fbff9faf5a5e8895192f647a84816ab75db2fc`, completed SUCCESS.

For every row the exact authoritative source archive SHA was verified before clean extraction, release assembly used the healthy HTTPS staging URL for both `-PTHF_BASE_URL` and `-PTHF_PASS_URL`, generated endpoint binding passed, APK was QA-signed, package identity matched, targetSdk 36 matched, APK was non-debuggable, and the staging binding was found in the payload.

| App | Source checkpoint | Runtime-staging APK SHA-256 |
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

Artifact digest: `sha256:f8f0f852bd82783ad8d57a021b64848bfa38d3f375c14173b870583931df1424`.

Runtime truth recorded by the gate:

- staging HTTPS health: PASS;
- candidate endpoint binding: PASS;
- auth flow: NOT PROVEN;
- THF Pass contract: NOT PROVEN;
- physical device: NOT PROVEN;
- production signing: false;
- public rollout: false.

The staging `/openapi.json` endpoint answered HTTP 200 but was not JSON, so identity lifecycle/OpenAPI capability is fail-closed rather than inferred.

## Source behavior audits retained

Exact-source runtime contract audit `34776549014` established across all nine Apps sources: no detected runtime placeholder URL, no cleartext HTTP/WS runtime transport, network/Data Saver and local/offline surfaces, and cross-app handoff surfaces. It also exposed incomplete refresh/logout/revocation lifecycle across the portfolio, weaker auth/session evidence in Pulse/Vault/Signal/Command, and no complete notification source contract in any of the nine sources.

Exact-source visible-action audit `34776819955` reached zero detected orphan buttons, dead anchors, orphan forms, or unmapped literal local API references after regression-protected handling of real DOM/helper idioms. This remains source-level wiring evidence only, not phone touch or backend-success evidence.

## THF Pass engineering control

Added `audit_openapi_identity_contract.py` with regression tests and CI run `34777458004` PASS. It requires route-surface evidence for login/token, refresh, logout, revoke and federation/handoff, but explicitly never promotes runtime readiness from route names alone.

## Remaining blockers / next executable work

1. Identify or deploy a real THF Pass/auth staging contract supporting refresh/logout/revoke/expiry and test live health/auth semantics. Current healthy staging endpoint is suitable for generic health/config binding but THF Pass/auth is not proven.
2. Add integration tests for expired-session, refresh, logout and server-side revocation before federation readiness can pass.
3. Implement/test notifications where product requirements require them; do not claim push without registration/channel/receiver/provider evidence.
4. Add actual Spark/Rush unit-test sources; previous Gradle unit-test tasks were `NO-SOURCE`.
5. Physical-phone evidence remains mandatory for these exact APK SHAs: install, launch, touch, responsive layout/orientation, background-resume, offline↔network, core journey and crash-free smoke.
6. Production signing, Play Console and legal/owner actions remain later owner-only gates.
