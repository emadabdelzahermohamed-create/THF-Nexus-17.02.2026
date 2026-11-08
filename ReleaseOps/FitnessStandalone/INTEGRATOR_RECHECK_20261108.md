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


# Integrator recovery update — 2026-11-08 19:53 Cairo (evidence through 17:53Z)

## Canonical source and live Play readback
- Canonical branch: `agent/codex/fitness-recovery/20261023`. Current app-source SHA remains `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3` (merged #280/#281); subsequent integrator commits are evidence-only.
- Latest read-only Play probe: [run 42405709027, attempt 2](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42405709027), job 128802337041 succeeded. Artifact 13626008171 ZIP SHA-256 `0f73170f5da6c8e80efe883a7a60b015ae0bbeefc8f2f19534cc845bcb65dbea` was downloaded and independently recomputed; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`. Internal 51019 is completed; alpha 51007 remains draft; Production was not listed/verified. `uploadAttempted=false`, `commitAttempted=false`. No listing edit.
- Existing signed 51019 AAB remains `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5`. No new signed AAB, version allocation, signing, upload, or Production promotion.

## New exact-head Health UI candidate — PR #282
- [PR #282](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/282) changes only `app.js` plus `test_health_metric_truthfulness.py`. It fixes the partial-consent display bug: missing permission renders as an em dash; an allowed read with no records remains numeric zero for steps, sessions, distance, and active calories.
- Exact HEAD `3291e076510b5626dd8ee931dad84728ba01605d` passed [workflow run 42506335882](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42506335882). Product 62/62, source-contract 34/34, backend 29/29, Android unit 218/218 with zero failures; lint 0 errors, 16 warnings, 1 hint.
- Artifact 13627900908 ZIP SHA-256 `1e8df4de5bb45b146bedf4f780417655027c1dfed0a4cf39446fdd802b5fd4d6` independently recomputed. QA APK SHA-256 `566a64bee34a0ce6610bc7a36b6547795a9abd867884cf245b8de89bd11bfb05`; unsigned AAB SHA-256 `652c6cf16b4a67dddbeee3551cb069c2695fe0dbdb9fa9fdccbc48f1bb8e19df`. Package `com.topherofit.thf.pulse.qa`, validation identity 51019 only. Downloaded AAB has no JAR signing entries. No signing or Play upload.
- Keep #282 draft, not merged: open exercise UX PRs #224, #247, #249, #250, #253, #254, #256, and #258 also modify `app.js`. Resolve this shared ownership chain before any merge.

## PR cleanup and current handoffs
- Closed without merge: #279 (duplicate GPS permission UI, superseded by merged #281); #225 (ledger core already canonical, canonical test file newer; all-day observer/dashboard still missing); #98 (broad Health expansion with 14 extra read scopes and mixed workflow/Gradle/catalog changes; retained for reference only); #215 (stale mixed GPS/Maps branch, app code superseded by #264/#267; native Maps key/billing work remains owner-gated). No application or release code changed by these closures.
- #280 partial Health Connect consent and #281 GPS permission-state presentation are merged after exact-head CI. No new Health permissions were added.
- #93 Health Services reader, #188 permission guard, #263 GPS anomaly policy, #261 swimming eligibility, #266 heart-rate freshness, and #248 route smoothing remain open/held; exact-head CI, integration wiring, privacy/provenance and/or physical gates remain.
- DailyStepLedger core is present, but the all-day observer and dashboard are not wired. GPS anomaly, swimming and heart-rate policies remain policy/test-only, not end-to-end ingestion.
- Competition PR #269 remains merged source-only. Strength score is `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED`, `rewardEligible=false`; no event seed, owner admin key, or independently verified deployment. The 2026-11-06 competition follow-up branch has four ahead/20 behind commits, but all four changed backend file blobs exactly match canonical; no delta or new PR. The 2026-11-07 branch is an ancestor/no-delta.
- No explicit current lease registry found; do not assume shared resources are free.

## Maps, device and release boundary
- Maps preflight 41684077962 (2026-11-03): APIs enabled; key inventory permission denied; no restricted Android key visible; no billing account linked. Native Maps SDK remains blocked by owner API/key/billing prerequisites. No paid infrastructure.
- Authorized Desktop Commander device `localhost` is offline, last seen about seven hours before this check. Current phone/session state is unknown. No ADB, install, launch, Stop, session, or activity-data action was attempted; preserve the unknown session. Physical P0 remains `BLOCKED_NOT_RUN`.
- Keep versionCode 51020 unallocated. Next code must be greater than 51019 and allocated only after owner API/key prerequisites, exact-head Android CI and physical P0. Production remains unverified until policy/privacy and physical gates pass.
- A separate backend-only workflow optimization branch `agent/codex/workflow-backend-only-skip-20261108-r1` at `04281cbf549ae2b00fb088cf9f51056bcae7a4fc` is unmerged and has no retrievable exact-head CI evidence; do not integrate it yet.


# Integrator recheck — 2026-11-08 20:12 Cairo

- Canonical branch `agent/codex/fitness-recovery/20261023` was at `057184d4f89c3a9cdc152187dfd0312244f7f730` before this evidence-only refresh; app-source SHA remains `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`. The workflow-only update changed a comment in `.github/workflows/thf-fitness-publication-state-probe.yml` to trigger a fresh read-only probe. No application source, version, signing or Play workflow logic changed.
- Fresh live Play probe [42508799594](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42508799594) completed successfully; job 128817153188 succeeded. Artifact 13627803896 ZIP SHA-256 was independently recomputed as `dd0dea0844d11e8bef03caa35a59c4752b92862a839b163481d574ca1ccf0954`; embedded JSON SHA-256 is `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`. Internal 51019 completed, alpha 51007 draft, Production not listed/verified; uploadAttempted=false and commitAttempted=false.
- The #281 tested PR head `4507e757bec279ba0e5b596ee8822ef7aaff7f45` and canonical merge `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3` have identical Git tree SHA `2e656364ab80991919eaecfab94aaba5e33c47bc`. Exact-head Android CI run 42503748041 passed. The subsequent candidate workflow run 42504262580 on the merge SHA completed without an Android build/artifact (deterministic-build skipped); it is not a new build.
- PR #282 artifact 13627900908 was downloaded and rehashed: ZIP SHA-256 `1e8df4de5bb45b146bedf4f780417655027c1dfed0a4cf39446fdd802b5fd4d6`; QA APK `566a64bee34a0ce6610bc7a36b6547795a9abd867884cf245b8de89bd11bfb05`; unsigned AAB `652c6cf16b4a67dddbeee3551cb069c2695fe0dbdb9fa9fdccbc48f1bb8e19df`. The AAB has no JAR signature entries. #282 remains draft because of shared `app.js` ownership with #224/#247/#249/#250/#253/#254/#256/#258.
- Current open priority PRs are #93, #188, #248 and #282. #263/#261/#266 are closed unmerged; #215/#225/#279/#98 are closed unmerged. #280/#281/#269 remain merged. No explicit current lease registry exists; shared resources are not assumed free.
- AppDeploy read-only snapshot for `thf-fitness-pulse-ul26f1` is Ready but the stored snapshot is dated 2026-10-27; secret inventory is empty and no backend errors were reported. This does not establish a live competition deployment or admin key. Existing frontend logs include WebGL-context and remote Arabic-font load failures.
- Maps owner prerequisite remains blocked by preflight 41684077962: APIs enabled, key inventory permission denied, no restricted Android key visible, no billing account linked. Phone remains offline with unknown session; physical P0 remains BLOCKED_NOT_RUN.
- VersionCode 51020 remains unallocated; no new signed AAB, Play upload, listing edit or Production promotion. Production remains NOT_VERIFIED.
