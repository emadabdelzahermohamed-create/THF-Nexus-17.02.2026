# TopHeroFit — canonical integrator recheck
Date: 2026-11-08 (Africa/Cairo)
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
Canonical branch: `agent/codex/fitness-recovery/20261023`
Canonical app-source SHA (last code change): `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`. Subsequent canonical commits in this checkpoint are evidence-only.

## Tested handoffs integrated

1. **PR #280 — partial Health Connect consent** merged as `06ca1b7891e72812f0a4514d90a7b97081a54b85`. Exact source head `63e80126d40c0a6ad253081a032807e38c4213aa`; exact-head Android CI run 42487820726 succeeded. The change is limited to `HealthConnectRepository.kt`, `HealthReadPermissionPolicy.kt`, and its test. Each metric is read only with its own grant. Missing permission is null; permitted/no-record is zero. No permissions were added. Validation archive SHA-256 `187a2fc435cb75546d56512c1a9149a5497adce13d91547e128352077690e1a3`; QA APK `96d71d6585c33fdb7b00190b7d924c5c36a6a5f6d10f7cffdd5b37ad3b63a4f9`; unsigned AAB `e0d6befbc8890c2ff8ae9dc88acb7115c5d6fc442bb4b075e5817c39bb27a30f`.
2. **PR #281 — GPS permission-state presentation** merged as `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`. Exact source head `4507e757bec279ba0e5b596ee8822ef7aaff7f45`; exact-head Android CI run 42503748041 succeeded. It changes only `app.js` and `test_source_contract.py`. Product 60/60, source-contract 34/34, backend 29/29, Android 218/218; lint 0 errors, 16 warnings, 1 hint. Archive 13626169449 SHA-256 `a962157d2a3e32146c66c1a75a8fb869d698cc4e2dab24fcc4ee050a9da3d41a`; QA APK `cd2e19b53e0192f9c418bc3e4bab33d32c7c29034bb115488e71fa25f7630208`; unsigned validation AAB `44a5d7c8f28c452686ee14dff3059102b097001e6a645b065993acd528b32828`.

The two handoffs were disjoint. The #281 merge tree differs from its tested base only in `app.js` and `test_source_contract.py`; no release, signing, version, workflow, or Play file changed. Both candidate AABs are unsigned validation outputs using QA identity/versionCode 51019. No versionCode was allocated and no bytes were signed or uploaded.

## GPS, Maps, sessions and truthful metrics

- Latest GPS checkpoint: [GPS_MAP_QUALITY_20261108.md](GPS_MAP_QUALITY_20261108.md).
- GPS status states distinguish permission/off/acquiring/stale/filtered/ready. Filtered observations are not mislabeled as weak accuracy. The current distance accumulator suppresses one-fix spikes, uses uncertainty deadband and bounded path/net distance, but does not prove spoof resistance or eliminate prolonged drift.
- Map implementation is Leaflet with attributed OSM/OpenTopoMap/EOX tiles, local fallback and a Google directions handoff. Native Google Maps SDK is still owner-gated: preflight run 41684077962 (2026-11-03) reported APIs enabled, key inventory permission denied, no restricted Android key visible, and no billing account linked. No paid infrastructure.
- Session checkpoint/persistence and foreground-service code remain in canonical source, but phone behavior is not physically revalidated. The authorized device is offline (last seen about 6 hours before the 2026-11-08 check); current session state is unknown. No ADB/session action was taken.
- DailyStepLedger core is present in canonical source, but it is not wired to an all-day observer/dashboard. Current ActivityTrackingService step observation is session-scoped; daily average/history is not yet established by continuous device evidence.
- Activity GPS anomaly, swimming eligibility and heart-rate evidence policy classes/tests exist, but are not wired end-to-end into raw GPS/Health ingestion. `HealthServicesReader.kt` is absent from canonical. The new partial-consent repository behavior is merged, but Health grant/revoke/no-data/error, wearable provenance and Play declaration/privacy gates remain open.

## Competition and anti-cheat

- PR #269 competition backend is merged as `ab29ddd333d39581ee6ed7a31a7fccd1ed7343c8`; exact backend CI run 42267621742 succeeded.
- Server derives provisional strength volume from stored workout sets; enrollment, event windows, capacity and idempotent submission protections are present. The score boundary remains `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED` and `rewardEligible=false`. No event is seeded, no deployment is independently verified, and the owner-managed `THF_COMPETITION_ADMIN_KEY` is not configured. No THF payout is authorized.
- No open competition-scoring PR or current competition lease was found. No current lease registry/file was found in the canonical FitnessStandalone release area or repository search; shared resources are not assumed free.

## Current open/held PRs

- #215 GPS map: open/draft, stale base; current canonical already contains Leaflet/tile/network-policy implementation. Its branch also changes Gradle, ActivityTrackingService/MainActivity, and cloud enablement/preflight workflows. Its observed run 41684088936 was only the artifact-size-cap workflow, not Android candidate CI. Do not merge wholesale.
- #248 route display smoothing: open/draft, old base, no exact-head CI on current head. Hold.
- #225 daily-step ledger: open/draft, old base. Its ledger core blob is already present in canonical; the missing work is the all-day observer, durable lifecycle ownership and dashboard. Do not duplicate the core.
- #93 Health services: open/draft; canonical HealthServicesReader is absent. Hold pending exact-head CI, minimal permissions, privacy/Play declaration review and physical QA.
- #98 broad Health expansion remains explicit HOLD. #188 permission-scope gate remains draft and does not authorize new permissions.
- #279 original GPS permission PR is superseded by merged #281 and is being closed. #280/#281 are merged. #263/#261/#266 are closed unmerged; policy classes/tests in canonical are not evidence of end-to-end ingestion or physical anti-cheat.

## Live Play and release evidence

- Latest independent readback: [run 42405709027, attempt 2](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42405709027), probe job 128802337041 succeeded.
- Artifact 13626008171 ZIP SHA-256 independently recomputed: `0f73170f5da6c8e80efe883a7a60b015ae0bbeefc8f2f19534cc845bcb65dbea`; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.
- Readback: Internal 51019 completed; alpha 51007 draft; Production not listed/verified; `uploadAttempted=false`, `commitAttempted=false`. Listing still claims GPS/background sessions and estimated metrics. No listing edit.
- Existing signed 51019 AAB remains SHA-256 `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5` from source lineage `76053bd9127c38d8065eb7ac250bdeb34ab67854`. There is no new signed AAB for current canonical source `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`.
- VersionCode 51020 remains unallocated. No rebuild/reupload of unchanged bytes, no signing, no Play write, and no Production promotion. Production remains NOT_VERIFIED until policy/privacy and physical gates pass.
