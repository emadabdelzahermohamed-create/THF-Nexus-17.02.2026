# TopHeroFit canonical recovery — 2026-11-18

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`. Scope: TopHeroFit only. This repository is the sole source of truth.

## Canonical source

- Canonical branch: `agent/codex/fitness-recovery/20261023`.
- Application/source baseline at this checkpoint: `7dc57dd9f6e647797cbbe2d1cfdb45773410a866`.
- The documentation commit that publishes this recovery does not change Android application bytes.
- PR #301 was merged by squash at `7dc57dd9f6e647797cbbe2d1cfdb45773410a866`; it adds the fail-closed Health Connect metric guard and its 14 deterministic tests. Exact-head run [44315659269](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026) succeeded on source `853bd4e78b82d3b0db9203416a071bf360aa6a44`. HealthMetricEvidencePolicyTest 14/14; Product 69/69; source-contract 34/34; backend 29/29; Android build/lint/unsigned bundle validation PASS. Artifact 14433350306 ZIP SHA-256 `afd8a019082ebc4341917ad753ad2be65d8f725bc21cc86cae870426c730b40d`; APK SHA-256 `9850fe1ec342cd1ba420546f7aa54c87cc0f82c1a5d6a9fc72f672fd5883185e`; unsigned AAB SHA-256 `914a0c6e5d40526a59152423ff72a3a575a882baf6cb3e43c582d110fdb711ae`.
- PR #282 remains merged; null/undefined/invalid health metrics render unavailable, while a genuine zero remains zero. The Health Connect permission allowlist remains five scopes; no heart-rate permission was added.

## GPS / session candidate

- Selected handoff: [PR #297](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297).
- Candidate branch: `agent/codex/gps-permission-downgrade-20261116-r1`.
- Current candidate HEAD: `f741af0dccd48dbcf258f5ae5b1d23e0db58f3af`.
- It is synchronized with canonical PR #301 as a second merge parent. Against canonical application base `7dc57dd9f6e647797cbbe2d1cfdb45773410a866`, the PR is 11 commits ahead / 0 behind and changes exactly 14 GPS Activity Engine source/test files plus two candidate checkpoint documents. No shared `app.js`, Health, MainActivity, Manifest, release, version, workflow, signing or Play source is in the GPS diff.
- Exact-head run [44358671462](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44358671462) completed SUCCESS on exact HEAD `f741af0dccd48dbcf258f5ae5b1d23e0db58f3af`: Product 69/69; source-contract 34/34; backend 29/29; Android unit 304/304; zero failures/ignored; API 36, Kotlin, lint, assembleDebug and unsigned bundleRelease validation PASS. Lint: 0 errors, 11 warnings, 1 hint.
- Artifact 14452564181 ZIP SHA-256 `1fe20c29953a629f35d93413473345ae67ddc3414f8b071d335e25701d309609`; debug QA APK SHA-256 `d471438d8ce89454a24ab6cd8d8f802ae58c2e270c1ca93f3a01e7478d8cf77f`; unsigned release-validation AAB SHA-256 `670d09313a87daf64ffa6dfe2dcd825fc6a7f8e9a7232c6eaf7f73eb93316082`. The ZIP was downloaded and independently rehashed. The debug APK is isolated by `applicationIdSuffix '.qa'`; the release-validation AAB uses production package ID `com.topherofit.thf.pulse` and versionCode 51019 but has no signing entries and is unsigned. It is not installable, signable as-is, uploadable or a release.
- This AAB is different from the prior GPS-only AAB because it includes the now-canonical Health metric guard. No Play upload or release signing occurred.
- PR #297 remains Draft/unmerged until physical P0 passes.

## GPS and map implementation

- Fused Location Provider is primary; fallback chooses one eligible Android framework provider. Fine permission may use GPS_PROVIDER; coarse-only permission uses NETWORK_PROVIDER. Fine-to-coarse downgrade is detected and the previous source anchor is discarded.
- Source changes and long gaps re-anchor distance; stale, future, out-of-order, mock, invalid, poor-accuracy and implausible fixes are filtered.
- Distance accumulation uses endpoint uncertainty, a displacement deadband, persistence across multiple fixes and a path-to-net bound. This reduces stationary jitter but does not prove authenticity.
- V3 checkpoints preserve phase, wall/monotonic clocks, boot identity and bounded route. Foreground service, START_STICKY, ongoing notification, Pause/Resume/Finish actions and periodic local checkpoints exist in source.
- Map stack: Leaflet/WebView; OSM street, OpenTopoMap terrain, EOX Sentinel-2 cloudless 2016 satellite and EOX hybrid. Browser tile cache is not a guaranteed offline package. No native Google Maps SDK, billing, key, traffic or transit overlay is used or claimed.
- The shared WebView status still hardcodes “GPS” for any ready Fused/Network fix and does not explicitly show the paused state. Keep this as a separate minimal `app.js` hunk under an explicit lease; do not fold it into #297 or overwrite the shared file.

## Current PR and lease decisions

| PR | Current head / compare to canonical source | Decision |
|---|---|---|
| #297 GPS | `f741af0d...`; 11 ahead / 0 behind; 16 files; exact run 44358671462 PASS | Draft until physical P0 |
| #284 Maps | `274155ea...`; 19 ahead / 63 behind; 13 files; no exact-head CI | Draft; stale/overlapping |
| #93 Health Services | `1cc08cef...`; 2 ahead / 366 behind; 12 files; no exact-head CI | Draft; 19 requested scopes versus five allowed |
| #216 session resume | `1ef91588...`; 201 ahead / 221 behind | Draft; shared app.js |
| #224 offline demos | `cc703baa...`; 153 ahead / 221 behind | Draft; shared app.js/catalog |
| #160 exercise catalog | `82e5ca5c...`; 53 ahead / 221 behind | Draft; no exact-head native CI |
| #213 timed RIR | `f719214d...`; 190 ahead / 221 behind | Draft; no exact-head native CI |
| #248 GPS smoother | `67d3b438...`; 4 ahead / 200 behind | Draft; helper not service-integrated |
| #301 Health metric guard | merged at `7dc57dd9f6e647797cbbe2d1cfdb45773410a866` | Integrated after exact-head CI |
| #282 metrics | merged at `b248a357...` | Integrated |
| #295 / #299 / #300 / #269 | merged | Existing canonical integrations |
| #294 | closed unmerged | Superseded by #297 |

The current file-level ownership map is in [INTEGRATOR_LEASES_CURRENT_20261118.md](INTEGRATOR_LEASES_CURRENT_20261118.md). Release/version/workflow/signing/Google Play writes remain exclusively on the canonical branch.

## Fresh Google Play readback

- Existing read-only publication probe [43739661313, attempt 3](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43739661313) completed successfully at 2026-11-18T17:22:53Z. The workflow file blob at the run SHA and current canonical source is identical.
- Artifact 14451997696 ZIP SHA-256 `e7de6f3f00394c4888e0e3755f2259d072469733f9ebba14f1146a465096901e`, independently downloaded/rehashed. Embedded JSON SHA-256 `09e7a346e5e1c893d4323d20105d8f4d63`, independently recomputed.
- Package `com.topherofit.thf.pulse`: Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified. `uploadAttempted=false`, `commitAttempted=false`. The probe creates, reads and deletes a temporary edit; it does not mutate a published track or listing.
- Arabic and English store listings were read without mutation. No listing change was made.

## Physical P0 and owner-only gates

Desktop Commander `localhost` is OFFLINE; last seen about 31 hours before the 2026-11-18 19:29 Cairo check. Last known handset: Samsung SM-A217F / Android 12. Current app/session state is unknown. Preserve the installed Play package and unknown session. No ADB, install, launch, force-stop, Stop action, settings change or activity-data read was attempted. Last recorded `location_mode=0` is from 2026-11-09; no device-wide setting was changed.

Physical P0 remains BLOCKED_NOT_RUN for:
1. Measured outdoor walk/run/cycle route and distance reference.
2. Stationary 60-second drift and false step/distance accumulation.
3. Fine-to-approximate permission downgrade and provider re-anchor.
4. Screen-off/background tracking and ongoing notification.
5. Notification Pause/Resume/Finish and explicit Stop.
6. Task removal/process-death restore without crediting downtime.
7. Crash/ANR/logcat and Health permission/no-data/revoke checks.

## Anti-cheat, competitions and route sync

- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains unwired in `ActivityTrackingService`. GpsFixGate and GpsDistanceAccumulator filter and re-anchor, but they are not full anti-cheat and do not cryptographically attest location. No physical provenance PASS or reward eligibility is claimed.
- Competition PR #269 is merged, but the only provisional metric is `strength_volume_kg_reps`. Admin key/production authority is unverified; scores remain `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED`, `rewardEligible=false`; no rewards or payouts are authorized.
- Completed GPS routes remain in WebView localStorage. Existing authenticated `/api/v2/workouts/sync` and `/api/v2/workouts?limit=200` carry workout/set metadata only; the strict AppDeploy workout allowlist has no route fields or route table. The route backup design remains design-only: separate summary and precise-route consent, finished-session-only upload, retention, revocation, per-route/account deletion and privacy/security review. No route endpoint or cloud upload is implemented.

## Release decision

- Last independently read Internal versionCode: 51019.
- Next versionCode 51020: NOT ALLOCATED.
- No signed release AAB, signing, Play upload, track mutation or Production promotion.
- Play write permission and GCP Secret Manager signing access are not proven by the read-only probe. The legacy promotion workflow is pinned to older source/version/certificate and is not a 51020 workflow.
- Production remains HOLD pending exact-source CI, physical P0, owner API/signing prerequisites, privacy/Data Safety and policy review.

No paid infrastructure or unrelated projects were used.
