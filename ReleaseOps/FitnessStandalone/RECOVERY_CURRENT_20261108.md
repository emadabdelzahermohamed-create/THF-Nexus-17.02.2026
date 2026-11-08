# TopHeroFit canonical recovery — 2026-11-08 20:12 Cairo

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
Canonical release branch: `agent/codex/fitness-recovery/20261023`  
Branch head observed before this evidence-only recovery update: `057184d4f89c3a9cdc152187dfd0312244f7f730`  
Canonical Android app-source SHA: `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`

This file is the current recovery addendum. The historical `RECOVERY_20261023.md` remains preserved.

## Canonical source and tested handoffs

- PR #280 (partial Health Connect consent) merged as `06ca1b7891e72812f0a4514d90a7b97081a54b85`; exact tested source `63e80126d40c0a6ad253081a032807e38c4213aa`; Android CI run [42487820726](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42487820726) succeeded.
- PR #281 (truthful GPS permission state) merged as `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`; exact tested PR head `4507e757bec279ba0e5b596ee8822ef7aaff7f45`; Android CI run [42503748041](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42503748041) succeeded. The tested PR-head tree and canonical merge tree are exactly identical: `2e656364ab80991919eaecfab94aaba5e33c47bc`.
- The current Android app-source SHA remains `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`; later commits in this checkpoint are evidence/workflow-only.
- Candidate run [42504262580](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42504262580) on the merge SHA completed successfully as a workflow, but its Android deterministic-build job was skipped and it produced no artifacts. It is not a new Android build or artifact.

## Latest live Google Play readback

- Read-only probe [run 42508799594](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42508799594) completed successfully on workflow-only head `057184d4f89c3a9cdc152187dfd0312244f7f730`; job `128817153188` succeeded.
- Artifact `13627803896` was downloaded and its ZIP SHA-256 independently recomputed: `dd0dea0844d11e8bef03caa35a59c4752b92862a839b163481d574ca1ccf0954`.
- Embedded publication JSON SHA-256: `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.
- Readback: Internal 51019 = completed; alpha 51007 = draft; Production was not listed or verified.
- The artifact explicitly reports `uploadAttempted=false` and `commitAttempted=false`. No Play mutation occurred.
- The current Arabic and English listings still describe GPS sessions, background sessions, estimated metrics, offline exercise content and voice guidance. No listing edit was made; those runtime claims remain subject to physical P0 and policy/privacy review.

## Artifact lineage and release boundary

- The current canonical app source `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3` has exact-head Android validation through PR #281's tested tree. Its QA APK SHA-256 is `cd2e19b53e0192f9c418bc3e9ceacff3fda01e000213137f3b61ecf7162d0e47` only if separately verified; the recorded exact value for the #281 QA APK is `cd2e19b53e0192f9c418bc3e9ceacff3fda01e000213137f3b61ecf7162d0e47`. The unsigned validation AAB SHA-256 is `44a5d7c8f28c452686ee14dff3059102b097001e6a645b065993acd528b32828`.
- The exact #281 artifact is validation-only, package `com.topherofit.thf.pulse.qa`, validation versionCode 51019; it is unsigned. No release signing or Play upload occurred.
- The existing signed 51019 AAB remains SHA-256 `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5` from the older source lineage `76053bd9127c38d8065eb7ac250bdeb34ab67854`. It is not an artifact for the current app-source SHA.
- VersionCode 51020 remains unallocated. No new signed AAB, upload, listing edit, track change, or Production promotion occurred.

## GPS, maps, sessions and metrics

- GPS status distinguishes permission/off/acquiring/stale/filtered/ready. Fresh rejected observations are shown as filtered rather than mislabelled as weak accuracy.
- Distance uses an uncertainty deadband, minimum displacement margin, bounded anchor gap/accuracy and path/net limit; a one-fix spike-and-return is discarded. This is conservative filtering, not proof of spoof resistance, stationary-drift elimination or physical accuracy.
- Map stack remains Leaflet with attributed OSM/OpenTopoMap/EOX tiles, local SVG fallback and a Google Maps directions handoff. Native Google Maps SDK, native basemap, traffic and transit remain disabled.
- Latest recorded Maps preflight is run 41684077962 (2026-11-03): APIs enabled, release-builder key-inventory permission denied, no restricted Android key visible, no billing account linked. Owner API/key/billing prerequisites remain blocked. No paid infrastructure was created.
- Session persistence and foreground-service code are present in canonical source, but background/screen-off/process-death/pause-resume/Stop behavior is not physically revalidated. The current phone/session state is unknown; preserve it.
- DailyStepLedger core is present, but an all-day observer, durable day-boundary owner and dashboard are not wired. Current step observation is session-scoped; no continuous daily-average claim is established.

## Health and anti-cheat

- PR #280 reads each Health Connect metric only with its own grant: missing permission is null; an allowed read with no records is zero. No permissions were added.
- PR #282 fixes the UI distinction between unavailable (missing permission) and numeric zero. Exact head `3291e076510b5626dd8ee931dad84728ba01605d` passed run 42506335882: product 62/62, source-contract 34/34, backend 29/29, Android unit 218/218; lint 0 errors, 16 warnings, 1 hint. Artifact 13627900908 ZIP SHA-256 `1e8df4de5bb45b146bedf4f780417655027c1dfed0a4cf39446fdd802b5fd4d6`; QA APK `566a64bee34a0ce6610bc7a36b6547795a9abd867884cf245b8de89bd11bfb05`; unsigned AAB `652c6cf16b4a67dddbeee3551cb069c2695fe0dbdb9fa9fdccbc48f1bb8e19df`. The artifact was downloaded and independently rehashed; the AAB has no JAR signature entries.
- PR #282 remains draft and unmerged because it modifies `app.js`, also claimed by open exercise UX PRs #224/#247/#249/#250/#253/#254/#256/#258. Exact-head CI does not remove this shared-file conflict.
- PR #93 Health Services reader and #188 permission-scope guard remain open drafts without exact-head Android CI and without completed privacy/provenance/physical gates.
- PRs #263 (GPS anomaly), #261 (swimming eligibility) and #266 (heart-rate identity/freshness) are closed unmerged. Their policy/test code is not wired end-to-end to raw GPS or Health ingestion.

## Competitions

- PR #269 is merged source-only; backend CI run 42267621742 succeeded. It currently supports provisional strength volume only (`kg·reps`) derived from stored workout sets.
- Scores remain `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED`; `rewardEligible=false`. No event is seeded, no payout is authorized, and the owner-managed `THF_COMPETITION_ADMIN_KEY` is not configured.
- The 2026-11-07 competition branch is an ancestor/no-delta; no new competition handoff exists.
- Read-only AppDeploy check for existing TopHeroFit web app `thf-fitness-pulse-ul26f1`: status ready, stored snapshot version `1793087800913` (2026-10-27), secret-name inventory empty, backend error list empty. This is stale web-runtime evidence, not proof of current Android or competition deployment. Existing frontend error log contains WebGL-context and remote Noto Sans Arabic font-load failures. No deployment or secret was changed.

## PRs, leases and device

- Open priority PRs: #93, #188, #248, #282. #248 route smoothing is display-only and has local 11/11 harness evidence but no exact-head Android CI; it is not integrated. #282 has exact-head CI but remains held for `app.js` overlap.
- Merged: #280, #281, #269 (and existing source-only GPS/session integrations #264/#267).
- Closed unmerged: #215, #225, #279, #98, #263, #261, #266.
- Open exercise UX PRs #224/#247/#249/#250/#253/#254/#256/#258 still share `app.js` with #282.
- No explicit current lease registry/file was found in the canonical release tree. Shared resources are not assumed free.
- Desktop Commander `localhost` is offline (last seen about seven hours before the 2026-11-08 20:02 Cairo check). Last phone observation remains 2026-11-01T21:24:32Z with a foreground tracking service and an active/ambiguous session. Current state is unknown. No ADB, install, launch, Stop, session action or activity-data read was performed. Physical P0 remains `BLOCKED_NOT_RUN`.

## Release decision

**HOLD.** VersionCode 51020 remains unallocated. Next Android versionCode must be greater than 51019 and allocated only after owner API/key prerequisites, exact-head Android CI and physical P0 QA pass. Production remains unverified until policy/privacy and physical gates pass. No paid infrastructure, signing, Play write or Production action occurred.
