# TopHeroFit canonical recovery — 2026-11-09

Canonical repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
Canonical branch: `agent/codex/fitness-recovery/20261023`  
Canonical branch head before this evidence refresh: `c105b6c10d4d784b64a9e8ff25e4656073434629`  
Canonical Android app-source SHA: `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`

## Resume boundary

This file is an evidence/recovery snapshot only. It does not change app source, versionCode, signing, Play, billing or production state. Historical recovery `RECOVERY_20261023.md` is preserved. Latest full recheck: [INTEGRATOR_RECHECK_20261109.md](INTEGRATOR_RECHECK_20261109.md).

## Current tested GPS candidate

PR #283, branch `agent/codex/gps-accuracy-state-truth-20261109-r1`, is Draft/open/unmerged. Exact PR HEAD `645d11cc141e1b40be98e1a53ebb20f979441f70`; exact app/test source HEAD `d3f051103054c73a08bc4faf8c57fd100e15932f`. Candidate is 8 commits ahead and 0 behind canonical. The four commits after app/test source are documentation-only.

Exact-head Android CI run 42573716669 succeeded on PR HEAD 645d11c. Results: product 60/60, source-contract 36/36, backend 29/29, Android unit 220/220 (0 failures), lint 0 errors/16 warnings/1 hint; Android API 36, assembleDebug and bundleRelease succeeded. Artifact 13654725577 ZIP SHA-256 `a2c28279cfbe30a82b6b0fc77a45fbdc28ab2d40139971f4b350e4f5b64c5161` independently recomputed. QA APK SHA-256 `76bb278f83f7797ab7b840fa466186b32ce37d9eee619f1801c4718ff1edd85b`; validation AAB SHA-256 `e1d54e331a9611ad54891c1449ad0c0ed7fea97df604fee6f3406744f1c750b3`. AAB is unsigned and byte-identical to the earlier run 42572575827; it is not a new release artifact. No signing or Play upload.

PR #283 fixes stale/false GPS accuracy presentation and paused/process-death snapshots. It overlaps `app.js` with PR #282 and open exercise UX handoffs; keep unmerged until shared ownership is resolved. No physical GPS or device PASS is inferred.

## Release and Play

- Internal 51019 remains completed; alpha 51007 remains draft; Production was not listed/verified.
- Latest independent Play readback: run 42508799594, job 128817153188 succeeded, artifact 13627803896. ZIP SHA-256 `dd0dea0844d11e8bef03caa35a59c4752b92862a839b163481d574ca1ccf0954` re-downloaded and recomputed on 2026-11-09; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`. Readback date is 2026-11-08, not a new Nov 9 API observation. uploadAttempted=false, commitAttempted=false.
- Existing signed 51019 AAB SHA-256 `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5` belongs to older source lineage `76053bd9127c38d8065eb7ac250bdeb34ab67854`, not current canonical source.
- VersionCode 51020 remains unallocated. No new signed AAB, Play upload, listing edit or Production promotion.

## Owner/device gates

- Maps preflight 41684077962 (2026-11-03): APIs enabled; key inventory permission denied; no restricted Android key visible; no billing account linked. Native Maps SDK remains owner API/key/billing blocked. No paid infrastructure.
- Desktop Commander `localhost` offline, last seen about 31 hours before Nov 9 check. Last phone observation 2026-11-01T21:24:32Z had Play 51019 and foreground tracking service with an active/ambiguous session. Current session unknown; preserve. No ADB/install/launch/Stop/session action. Physical P0 blocked/not run.

## Remaining product work

- Session persistence/foreground service exists in source; screen-off/background/process-death/pause-resume/Stop and truthful notification metrics await physical P0.
- DailyStepLedger core exists; all-day observer/day-boundary owner/dashboard are not wired. Step observation remains session-scoped.
- Health Connect scopes remain READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE, READ_ACTIVE_CALORIES_BURNED. Partial consent is merged (#280); missing metric versus zero UI (#282) is tested but held due app.js overlap. Health Services reader (#93) and permission gate (#188) remain draft without exact-head CI. Imported Health summary stays on-device; provenance metadata is heuristic, not cryptographic attestation.
- GPS anomaly, swimming and heart-rate policies are not wired end-to-end. Physical Health grant/revoke/no-data/error and wearable checks remain blocked.
- Competition backend (#269) supports server-owned event/membership/capacity/submission/leaderboard logic for strength kg·reps. Scores remain SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED and rewardEligible=false; no event seed, admin key or independent deployment verification.
- Policy/privacy: historical Health declaration is versionCode 51003 and unsubmitted; AppDeploy snapshot is stale (2026-10-27); public privacy/deletion pages and Play URL not independently verified; explicit non-medical-device and professional-consultation disclosures need both locales.

## Leases

No explicit current lease registry/file found in the canonical FitnessStandalone area or repository search. Shared resources are not assumed free.

## Release gate

**HOLD.** Next Android versionCode must be greater than 51019 and may be allocated only after owner API/key prerequisites, exact-head Android CI and physical P0 QA pass. Production only after policy/privacy and physical gates. No paid infrastructure, signing or Play write.
