# THF Apps Factory Checkpoint — 2026-09-14 10:15 EET

## Scope
THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass, shared identity/federation and cross-app handoff release controls. Dedicated native game streams and token finance are excluded from this Apps Factory batch. Game-stream files were read only where required to establish Spark/Rush source provenance; no dedicated game implementation was modified.

## Start state and same-SHA skip
- Run-start repository baseline observed: `8d6bab5bbab4bb2b31277e69b94ef85470564d67`.
- Latest previously recorded Apps Factory checkpoint observed: `bf2d9d2d1254573a4748243ac38c05808013ab80`.
- `ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json` remained the authority for exact candidate source/APK SHA bindings.
- Core plus the nine app candidates remained `PENDING_PHYSICAL_PHONE`; no candidate source/APK SHA changed in this batch.
- Therefore already-proven same-SHA compile/package/API-36 work was not repeated. This batch concentrated on a newly discovered release-evidence regression.

## Finding A — stale backend-evidence lineage for Spark/Rush
The backend reachability workflow still used superseded Spark/Rush RC3 archives, even though the authoritative current candidates are the RC4 combined-function sources.

Corrected exact source lineage:
- Spark: `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`, Drive source `1bwvy2huHjkpof3ZcH1QEJK23ep7SKKEm`.
- Rush: `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`, Drive source `1P4Z1r6l08rbCLuDsXX1YRjWo0seC8yQz`.

Added:
- `ReleaseOps/validators/validate_app_backend_reachability_lineage_v1.py`
- `ReleaseOps/tests/test_validate_app_backend_reachability_lineage_v1.py`
- workflow enforcement that compares every app row to the current physical-device candidate registry, rejects superseded SHAs, rejects missing/duplicate apps, rejects source drift, and cannot promote a candidate out of `PENDING_PHYSICAL_PHONE`.

The first PR run (`34816479326`) failed before any network probe because the test harness was invoked in a way that did not guarantee the repository import path. It was not treated as PASS. The harness was corrected to module-based unittest execution.

Evidence after correction:
- PR #12 head: `b1041311dcaf998423f2c64bd92e3237ab2757a2`.
- PR run `34816556875`: SUCCESS.
- Merge commit: `286461264cdd5f35c00c8321c49c87370f148ac7`.
- Main post-merge run `34816615237`: SUCCESS.

## Finding B — literal external URL response was not THF backend proof
Inspection of the corrected evidence showed the reachable literal URLs were third-party/service references such as WHO, PubMed, esm.sh, Solscan and Telegram. A successful response from those origins cannot establish THF backend health, authentication, session or federation readiness.

Added:
- `ReleaseOps/validators/evaluate_runtime_network_truth_v2.py`
- `ReleaseOps/tests/test_evaluate_runtime_network_truth_v2.py`
- `THF Apps Runtime Network Evidence V2` semantics in `.github/workflows/thf-apps-backend-reachability-v1.yml`.

The new gate:
- verifies exact current source lineage before inspecting network references;
- fails closed on placeholder or insecure runtime URLs;
- classifies literal HTTPS/WSS probes as diagnostics only;
- does not infer backend health/auth from third-party reachability;
- emits an explicit non-promotional truth boundary for every exact current app source.

Evidence:
- PR #13 head: `38ae80ef60340b87665b96144049d530981fe69b`.
- PR run `34816866903`: SUCCESS.
- PR artifact digest: `sha256:fbcf87ccf1772ac749fbce50a8d9ee2761c6024e66fef346d9692af8a31ddefd`.
- Merge commit: `2355e61da4be533aad81fbe9b3b49fd3eb78070c`.
- Main post-merge run `34816920898`: SUCCESS.
- Main post-merge artifact ID: `10336941427`.
- Main post-merge artifact digest: `sha256:d1b3701da051ef0ffa2040720d8e3eb728b08f835157a2a32ab99bc17b3a3a1e`.

The resulting release truth is intentionally:
- `EXACT_CURRENT_SOURCE_LINEAGE=PASS`
- `SUPERSEDED_SOURCE_REJECTED=TRUE`
- `LITERAL_RUNTIME_REFERENCE_PROBE_IS_DIAGNOSTIC_ONLY=TRUE`
- `THIRD_PARTY_ORIGIN_RESPONSE_IS_BACKEND_PROOF=FALSE`
- `BACKEND_HEALTH_AUTH_PROOF=FALSE`
- `NETWORK_RELEASE_READY=FALSE`
- `PHYSICAL_DEVICE_PROOF_REQUIRED=TRUE`
- `FINAL_OR_PLAY_READY=FALSE`

## Current blockers / user-only or external gates
- A stable externally reachable trusted-TLS THF Pass/backend staging endpoint plus an explicit health/auth/session/federation contract is still required before network-dependent app flows can receive source-bound runtime proof.
- FCM/APNs provider delivery and production secret/KMS boundary remain unproven; `PUSH_READY=FALSE` remains unchanged.
- Every exact APK candidate still requires physical-phone evidence for install, launch, touch, responsive layout, orientation, background resume, offline↔network behavior, core user journey, crash-free behavior, accessibility, Data Saver, RTL and 20-language readiness. Notification-capable candidates additionally require permission/channel/receive/tap/deeplink evidence.
- Production signing/AAB, Play Internal rollout, OAuth/legal/billing/2FA gates were not performed in this batch.

## Rollback
This batch changed ReleaseOps validators/tests/workflow semantics only; it did not deploy a production backend, change public endpoints, sign production packages, or roll out to Play. If these release-control changes regress, revert merge commit `2355e61da4be533aad81fbe9b3b49fd3eb78070c`, then `286461264cdd5f35c00c8321c49c87370f148ac7`. Existing exact app candidates remain unchanged and auditable.
