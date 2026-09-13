# THF Apps — APPS-RC3 Real-Function Hardening checkpoint

Date: 2026-09-13
Scope: THF Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command. Core RC6 is not rebuilt here because its same-SHA exact-candidate gate is already proven; THF Pass remains backend/SDK-only and is covered as a federation dependency. Dedicated game streams and token finance are excluded.

## Authoritative baseline read before work

The current APPS-RC2 i18n/federation sources were recovered by exact SHA, clean-extracted, and treated as the only inputs for this hardening batch. Source identities:

| App | APPS-RC2 source SHA-256 | Locked Android package |
|---|---|---|
| Pulse | ef4d82dc1e3fff0d0bcdf0b7b31b9820aa9c958d846e9b1fd8ee6a19430ab6f8 | com.topherofit.thf.pulse |
| Forge | 8f6bf74b15146bc0a895912c40b9946ef5c3cc8df99fdcae39fa615ce4f03eed | com.topherofit.thf.forge |
| Echo | 09773a4c3890fc43ee8e15b37267555f9db0e471fe8cbdcefa3886d2a2def73a | com.topherofit.thf.echo |
| Codex | d8cf35346e244c141c65d4a5ce10e07f7fb2d4d6b831a0a63dd0b517d3ae0b83 | com.topherofit.thf.codex |
| Spark | 6b74f8d75df8c0b7f74d8c2fee8be7e3517f3803cb42968735bc7a10939bc18c | com.topherofit.thf.spark |
| Rush | bb6ff035186b13cdde853145f42e66259c205889de2a7b368da34c9cb0582ba7 | com.topherofit.thf.rush |
| Vault | e53d0cb62296581b1d8b52ce040b10ac896607adcc049b78f06a75bc8c28f6c7 | com.topherofit.thf.vault |
| Signal | 87e199ff2c174990b6e0e4e4ddd8accc0d585d2675343067395ccdf9490e9fb1 | com.topherofit.thf.signal |
| Command | 7dc686a9ad78ef90eec7cb2f7e65495356b3d513d9fc152c7ee8e3d20f91e487 | com.topherofit.thf.command |

RC2 already preserved API 36, 20 native locale resource sets and RTL. Those gates were not repeated as independent release claims; they were preserved while changing only the hardening delta below.

## Real-function policy findings closed in source

The RC2 wrappers/backends still contained policy hazards that prevented truthful release promotion even if an APK compiled. APPS-RC3 closes these source-level hazards:

- Android WebView third-party cookies are explicitly disabled.
- Data Saver no longer uses `LOAD_CACHE_ELSE_NETWORK` for authoritative network state. The WebView uses normal freshness semantics while image loading remains reduced under Data Saver.
- Android endpoint validation parses URI scheme/host, requires HTTPS, and rejects malformed/user-info endpoints instead of relying on a string prefix only.
- THF Pass federation and cross-app network handoffs fail closed when required endpoints are absent or not HTTPS.
- Loopback development addresses are removed as runtime defaults for network-required product flows. Missing configuration does not masquerade as a reachable service.
- Shipped `change-admin-key` / `change-*-secret` defaults are removed. Admin and economy secrets must be explicitly configured.
- Admin endpoints fail closed when the admin key is not configured.
- Economy submission requires both a configured HTTPS economy endpoint and explicit service secret. Otherwise the event remains locally pending/outboxed; no fake remote success is reported.
- Visible external handoff controls that depend on an absent service URL are suppressed/failed closed rather than sending the user to a placeholder target.

## Regression evidence

After the delta, all nine source trees pass Python compile/compileall and the security static gate. Seven applications contain packaged pytest suites and all seven pass with explicit test-only credentials. Spark and Rush do not currently contain pytest suites; this is recorded as `NO_TESTS`, not PASS-by-inference. Existing backend/product source is preserved.

## APPS-RC3 cumulative source artifacts

| App | APPS-RC3 source SHA-256 |
|---|---|
| Pulse | 71a16804e7c138535bb373263ae4374d8a5eef410ffe83b165472c684b6c8b10 |
| Forge | 0f7a416a9e14af9dbb3cdcb26bfb891e0c680d4a33a73d60601eda215e697e51 |
| Echo | 40a197b60563e560cab93ba0a64c859d9b650da222fdaec933993977d63902ab |
| Codex | 3d60cc550732468c89fe120f552def53ac798646d065e94efa153f8979e15b1e |
| Spark | dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0 |
| Rush | bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b |
| Vault | 7a2ba4236a0c42d2521fa2eb2c2d7108ceba0d2929ebdf68959a6eacbce4a793 |
| Signal | 51d7ce44fed24f7490973bcc7e019a8430157c4d5bfa1541e7cb590b0b7957c0 |
| Command | f7da9039041b8142d795e96934b95f00b83ac8fb5e3d6f5d9bfbff0aeb2eb408 |

The cumulative RC3 archives, summary JSON and regression TSV were stored in the THF Nexus Overnight workspace. This is a reversible source checkpoint; no canonical runtime was replaced.

## Exact-candidate lane

A separate QA-only GitHub Actions lane now stages exact sources through private Drive/WIF, uses an isolated GCP builder, builds `assembleRelease` so locked package IDs are not changed by a debug suffix, zipaligns, signs only with a disposable QA key, and checks exact package ID, targetSdk 36, APK signature, non-debuggable state and SHA-256. It explicitly refuses to equate package inspection with final readiness.

The RC2 candidate run is retained as diagnostic/package evidence only. RC2 is not eligible for FINAL because the real-function policy regressions above were discovered after its source checkpoint. The next candidate must be built from the exact RC3 SHA for each app.

## Truthful readiness

- Core RC6: prior exact-candidate package/runtime evidence preserved; physical-device acceptance still required.
- Pulse/Forge/Echo/Codex/Spark/Rush/Vault/Signal/Command: `APPS_RC3_SOURCE_HARDENED_NOT_FINAL` until an exact RC3 APK candidate is built/inspected, reachable backend health/auth is demonstrated where required, and physical-device acceptance is recorded.
- Signal and Command remain internal/private distribution surfaces; no public Play promotion is implied.
- THF Pass remains backend/SDK/federation-only; no standalone Play listing is implied.
- No production signing, Play public rollout, paid spend, owner identity action, Cloudflare production cutover, treasury/token transaction or irreversible operation occurred.

## Remaining release gates

1. Stage the exact nine APPS-RC3 SHA artifacts into the isolated builder and build exact-package API36 QA candidates.
2. Inspect candidate payload/package/version/signature/manifest and bind every result to its APK SHA.
3. Configure or identify real reachable HTTPS/WSS staging endpoints, then prove health/auth and each network-required core journey. No localhost/placeholder substitutes are acceptable.
4. Execute physical-phone evidence per exact APK SHA: install, launch, touch, responsive layout/orientation, background/resume, offline/network transitions, core user journey and crash-free smoke.
5. Only after those gates: Play Internal Testing evidence for public apps. No FINAL/PLAY_READY promotion before all required evidence exists.
