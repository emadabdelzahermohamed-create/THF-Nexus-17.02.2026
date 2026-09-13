# THF Apps Factory checkpoint — 2026-09-13 20:38 EET

## Truth boundary

This checkpoint is QA/release-preparation only. It does not declare FINAL or PLAY_READY. No production signing, Play publication, public cutover, paid spend, token-finance operation, or dedicated native-game work was performed. Physical-device acceptance remains mandatory and must be bound to the exact APK SHA.

## Exact-candidate state

Core RC6 was not rebuilt because the same exact candidate SHA was already proven through its current package/runtime gate and no regression evidence was found. Current exact Core APK SHA remains `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`, targetSdk 36, physical-device acceptance pending.

The general-app batch now has exact QA package inspection for all nine currently sourced apps. Pulse RC3 `d5dfe0198ab7d50589c612c796416e157bc689e6ef415164d268f090480dc4f0`; Forge RC3 `8079df0892bb692707f69efa4796ca6e43986f34c8c615a307d480a3b5f1bc44`; Echo RC4 `8a2821d4ebf38dd2d90563351487fe89f78829e91910527eceae0d97857e8d22`; Codex RC4 `3cc4260848eb0f9348a07badfc176440fed1cf6fa4bf1cf0df18ad250577088a`; Spark RC3 `87b5ed0c2b2e7485c71961f18f72bfa6f1498d9fc7a57397ad26d590e7fad5ef`; Rush RC3 `743eb8910b08b87ae9a72f72068c71c0cb96017c546b16d7b9bfadb06abe3cc1`; Command RC3 `fac87921bc4db9c69908be8686e3a6fe1f3377325ea2a4c87b4ad10dbcb9ab15`; Vault RC4-BF1 `87d9a657b0c0614f5c4acf9c0c7e5c690149d4e48e002678a163eed17b8f0345`; Signal RC4-BF1 `2a756ec0dad68fb4578e342172e7a7e55425ec8d8fb6c004e4ee9c0169f35cc8`. All nine inspected candidates preserve their locked package identity, targetSdk 36, QA signature validation and non-debuggable release packaging.

Vault and Signal RC3 had a real Gradle quoting defect and are superseded by corrected source-authoritative RC4-BF1 archives. The authoritative corrected source SHAs are Vault `dd6db86d7532f773a8d1d2662bf466bdcc0f1c64a863602ecdd1267c8f82fa33` and Signal `377044263fa0fc366afe67c6b42ccf4f3e2d1bc75769350f2ee885983f820ddf`. Their corrected RC4 workflow passed exact source SHA verification, source policy, pytest, Gradle release build, package identity, targetSdk 36, signing verification and non-debuggable inspection.

## Capability evidence inventory

A non-promotional source audit was run against the exact current source SHAs for Pulse, Forge, Echo, Codex, Spark, Rush, Vault, Signal and Command. Every source passed the existing Mobile Real-Function source policy. All nine expose 19 locale-specific Android resource directories in addition to the default resource set, which is consistent with 20-language resource readiness but is not runtime localization proof. All nine have source references for auth/session, THF Pass/federation-related wiring, local/offline handling, loading/error handling, RTL/locale handling, network-security configuration and accessibility-related behavior. Secure-storage evidence exists in every source, but source hits alone do not prove correct secret-at-rest behavior.

The same audit found no notification/push source hit in any of the nine exact source trees. This is recorded as a portfolio backlog gap rather than silently accepted. WebSocket evidence is present in Echo but absent from the other eight; that is not a defect unless their current product flow requires realtime transport. Data Saver/network-capability evidence is present across all nine, but exact-device metered-network behavior remains unproven.

A second audit restricted scanning to shipping runtime paths (`android/app/src/main`, `app`, `appsrc`) so documentation/test examples could not mask endpoint defects. Across all nine exact source SHAs it found zero placeholder runtime URLs and zero insecure HTTP/WS runtime URLs. Every app has at least one runtime auth/Pass-related source file and at least one runtime endpoint/build-config source reference. This clears a static runtime-endpoint hygiene gate only; it does not prove those configured HTTPS/WSS services are currently reachable or that auth/session handoff succeeds.

Spark RC3 and Rush RC3 still have no discovered pytest suite. Their compile/source-policy/package gates pass, but `NO_TESTS` is a release-preparation debt and is not equivalent to automated functional coverage.

## THF Pass / federation boundary

Cross-app sources contain THF Pass/federation references, but no authoritative standalone native THF Pass candidate/package was discovered in the current ReleaseOps source set. THF Pass therefore remains a shared identity/service discovery gate, not an inferred mobile-app PASS. Before promotion it needs an authoritative service/source manifest, reachable HTTPS health/auth/session evidence, cross-app handoff regression tests, secure session/token storage evidence, and logout/revocation/expired-session behavior.

## Required next executable work

1. Build regression tests for Spark and Rush real core journeys rather than accepting `NO_TESTS`.
2. Trace the THF Pass/federation contract from the exact source references into authoritative service endpoints; add health/auth/session/handoff tests without inventing a placeholder endpoint.
3. Decide per app whether notifications are product-required; where required, implement a real notification channel/provider path and permission/error behavior before release promotion.
4. Run candidate-bound reachable HTTPS/WSS backend health/auth tests for every network-required app and record endpoint provenance without exposing secrets.
5. Prepare the exact physical-phone evidence packs for install, launch, touch, responsive layout/orientation, background-resume, offline/network transitions, core journey and crash-free smoke. These remain user/device-only gates.
6. Production signing, Play publication, legal acceptance and irreversible rollout remain explicitly out of scope until owner-controlled approval.
