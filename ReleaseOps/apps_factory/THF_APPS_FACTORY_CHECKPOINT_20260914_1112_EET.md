# THF Apps Factory Checkpoint — 2026-09-14 11:12 EET

## Scope and same-SHA skip
This batch covers THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass, shared identity/federation, cross-app handoffs and their release controls. Dedicated native game streams and token finance were excluded from implementation changes.

The authoritative exact-device registry remained `ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json`. Its ten current candidates and source/APK SHA bindings did not change in this batch. All remain `PENDING_PHYSICAL_PHONE`, so already-proven same-SHA package/API-36 gates were not rebuilt merely to create activity.

Current exact APK authority remains:
- Core: `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`
- Pulse: `e043b5555f793d4bd226b865c8a5a400068d05948f1104583f5e9f2e028607dc`
- Forge: `c93b26b2b59b0f09671ecf632bbc3304e27b52e7b0d07470ee284e5a565cd8b5`
- Echo: `ddc0c48ec0c149d2f6ab424f9b6576f64a0c7888f021771076ff32b3a9728d94`
- Codex: `cad4bed914e006c294ddbd37fcebbf9ef2f4c9baac161f852e7c6d2433d3884c`
- Spark: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Vault: `76e20915e4bc6dee23adf43fdfcca9705815cf990164ccb8649032118dd42ce0`
- Signal: `9d370142a251c2515fe19e7598a35213e8285fab4ed74f804d88ea6b5a21f05a`
- Command: `b556e1aaa622de044aa6de609c9911aff5def3d738146c57ae3b8a842777958c`

## Finding A — physical evidence V4 still allowed self-described check PASS
The registry requires 17 exact-phone checks: install, launch, touch, responsive layout, orientation, background resume, offline/network behavior, core journey, crash-free, accessibility, Data Saver, RTL, 20-language readiness and notification permission/channel/receive/tap-deeplink.

V2/V3/V4 already bound exact installed bytes, candidate/source/session/package provenance and crash-free logcat evidence. However, for the remaining checks the V3 canonical capture could still be a text file whose principal semantic assertion was `RESULT=PASS`. That is insufficient for Mobile Real-Function Release Policy acceptance.

Added `ReleaseOps/mobile/validate_app_device_evidence_v5.py`, its regression suite and `THF App Physical Device Evidence Tooling V5` CI. V5 layers V4 and additionally requires for every policy check except the separately hardened `crash_free` check:
- one approved check-specific probe method;
- a distinct raw probe capture, not the semantic manifest itself;
- SHA-256 binding for both semantic manifest and raw capture;
- same session/package/candidate/source/check/method/timestamp binding;
- check-specific structural markers in the raw capture;
- no missing or unregistered semantic checks;
- continued explicit `final_or_play_ready=false`.

Implementation commits:
- `59cbad9bb91d5009f5939e01dd74c621f3ecad25` — V5 validator.
- `b390071a91bc3d1503b476c2eb9b04c1083d77b4` — V5 regressions.
- `ea2d779bef4f573a33f940bf785d78de6fe1516a` — CI gate.

Evidence:
- workflow run `34820951440`: SUCCESS.
- Python 3.12 compile: PASS.
- V2 regressions: 11/11 PASS.
- V3 regressions: 14/14 PASS.
- V4 suite: 40/40 PASS.
- V5 suite (including inherited lower-layer regressions): 64/64 PASS.
- authoritative policy coverage: 16 semantic-probe checks plus the separate V4 crash-free logcat check.
- emitted truth: `SELF_DECLARED_CHECK_PASS_ACCEPTED=FALSE`, `RAW_PROBE_CAPTURE_SHA_REQUIRED=TRUE`, `PHYSICAL_DEVICE_STATUS=PENDING`, `FINAL_OR_PLAY_READY=FALSE`.

## Finding B — Apps Factory state contradicted Runtime Network Evidence V2
The previous state file still represented shared runtime health as `PASS` / per-app `PASS_SHARED_STAGING`. That had become stale after Runtime Network Evidence V2 proved the reachable literal URLs were diagnostic/configuration references and could not establish THF backend health, auth, session or federation readiness.

Created reconciled state `ReleaseOps/apps_factory/THF_APPS_FACTORY_STATE_20260914_1115_EET.json` and hardened `validate_apps_factory_state.py` so the authoritative state now says:
- shared runtime `health=DIAGNOSTIC_REACHABILITY_ONLY`;
- endpoint binding `PASS_CONFIG_BINDING_ONLY`;
- `backend_health_auth_proof=false`;
- `network_release_ready=false`;
- Core runtime backend health `NOT_PROVEN_THF_BACKEND`;
- every app runtime health `NOT_PROVEN_THF_BACKEND`;
- all nine app endpoint bindings are configuration-only, not backend proof;
- all exact phone candidates remain pending.

Regression coverage explicitly rejects the old `PASS_SHARED_STAGING` label, shared `health=PASS`, backend-health/auth promotion, network-release promotion and Core runtime-health promotion.

Implementation commits:
- `b6872e2041a725b72e59b1f09c96ff8cb8e06244` — reconciled state.
- `53a594bcb2fd5a382952254d40ec8d064e3c0f3c` — fail-closed validator semantics.
- `d4c037da1cc65cfb32c8ccd872c877d7db5c8c67` — runtime-truth regressions.
- `f6618beb87d2ef8fd1bf6c008050e84c60fab0bb` — CI state gate update.

Evidence:
- Apps Factory State Gate run `34821359362`: SUCCESS.
- authoritative state validation: PASS, errors `[]`.
- exact package gates: 9/9.
- configuration bindings: 9/9.
- THF backend health/auth proven: 0/9.
- physical registry authority matches: 10/10.
- physical app acceptance: 9/9 PENDING plus Core PENDING.
- validator regressions: 19/19 PASS.
- emitted truth: `CONFIG_BINDING_ONLY=TRUE`, `BACKEND_HEALTH_AUTH_PROOF=FALSE`, `NETWORK_RELEASE_READY=FALSE`, `FINAL_OR_PLAY_READY=FALSE`.

## Current release truth / blockers
- `FINAL_OR_PLAY_READY=FALSE`.
- `PHYSICAL_DEVICE_PASS=FALSE`; all ten exact APK candidates still require real physical-phone execution and V5-grade evidence.
- `NETWORK_RELEASE_READY=FALSE`; a stable externally reachable trusted-TLS THF Pass/backend staging endpoint with real THF health/auth/session/federation evidence is still required.
- `PUSH_READY=FALSE`; FCM/APNs delivery plus approved KMS/secret boundary and exact-device permission/channel/receive/tap/deeplink proof remain required.
- Spark/Rush source history truth remains unchanged: no discovered native source unit-test suite; exact-source external regressions do not rewrite that fact.
- Production signing/AAB, Play Internal rollout, OAuth/legal/billing/2FA and device-only acceptance remain owner/device/external gates and were not fabricated or bypassed.

## Rollback
This batch changes release-control state/validators/tests/workflows only. It does not deploy a production backend, change a public endpoint, sign an APK/AAB, publish to Play, modify token finance or modify dedicated native game implementation. If the V5 evidence policy must be rolled back, revert `ea2d779bef4f573a33f940bf785d78de6fe1516a`, `b390071a91bc3d1503b476c2eb9b04c1083d77b4`, then `59cbad9bb91d5009f5939e01dd74c621f3ecad25`. If runtime-truth reconciliation regresses, revert `f6618beb87d2ef8fd1bf6c008050e84c60fab0bb`, `d4c037da1cc65cfb32c8ccd872c877d7db5c8c67`, `53a594bcb2fd5a382952254d40ec8d064e3c0f3c`, then remove/revert the new state commit `b6872e2041a725b72e59b1f09c96ff8cb8e06244`. Exact source/APK candidates are unaffected by either rollback path.
