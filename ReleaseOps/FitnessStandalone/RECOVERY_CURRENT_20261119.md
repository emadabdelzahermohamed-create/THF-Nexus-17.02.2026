# TopHeroFit canonical recovery checkpoint — 2026-11-19

Observed: 2026-11-19 17:58:00 UTC (19:58 Africa/Cairo). Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`. Scope: TopHeroFit only.

## Canonical source and tested integrations

- Canonical branch: `agent/codex/fitness-recovery/20261023`.
- Canonical application/source HEAD before this documentation-only checkpoint: `e28994ea76e67e0bed6eef3860f995b27388a002`.
- This checkpoint changes only ReleaseOps documentation and `RELEASE_CURRENT.json`; it does not change Android/WebView application source, workflows, signing or Play state.
- PR #304 Health source reconciliation merged at `e28994ea76e67e0bed6eef3860f995b27388a002`. Its exact PR head was `e5f23bbd592ce6c6c5a12a47a7cd5bb43079eb25`; exact-head run [44532209892](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44532209892) succeeded. Product 73/73, source-contract 34/34, backend 29/29, Android 287/287, zero failures/ignored; API 36, Kotlin, lint, assembleDebug and unsigned bundle validation passed. Artifact 14533717988 ZIP SHA-256 `a3ac105ac3f11c7459f65808a10c8e2eba33ff057c8aa7694d371139d6a7b404`; APK SHA-256 `9db12fcb515552505c722d97c88770d440f2d2af080cc103eb628bf289f53c69`; AAB SHA-256 `2a4266054a8528ebfb49c093b8de03d6d41965894ef749ca7d51e600a164e729`. ZIP/APK/AAB were independently rehashed. AAB is unsigned and QA/validation only.
- The three Health files in canonical merge `e28994ea...` were checked blob-for-blob against the tested PR #304 head. Exact mirrored metric intervals are deduplicated deterministically; overlapping verified intervals that cannot be apportioned are excluded from reward totals while source provenance is retained. No Health permission changed.
- PR #302 remains merged at `d2e4c6887fc3b94565536e5d985c193ab8ac1990` and provides truthful Location/paused UI. PR #301 remains merged at `7dc57dd9f6e647797cbbe2d1cfdb45773410a866` and adds fail-closed Health metric evidence checks. PR #282 remains merged at `b248a3571d871c604dbc3a11af72858bbac74eb9` and preserves null/undefined/invalid versus genuine zero.

## Selected GPS / Activity Engine candidate

- Current handoff: [PR #303](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/303), Draft / unmerged.
- Branch: `agent/codex/gps-activity-rebased-20261119-r1`.
- Current exact branch HEAD and tested source SHA: `6e73d988fe668c5b86f2ff4c053f2f43c2c4b6a8`.
- It is 1 commit ahead / 0 behind canonical and changes exactly 14 native GPS/Activity Engine source and unit-test files. It contains no app.js, index.html, MainActivity, Manifest, Health, catalog, release/version, workflow, signing or Play files.
- Exact-head run [44582044304](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44582044304) completed SUCCESS on exact SHA `6e73d988fe668c5b86f2ff4c053f2f43c2c4b6a8`.
- Product tests 73/73; source-contract 34/34; backend 29/29; Android unit tests 316/316; zero failures and zero ignored.
- Android API 36, Kotlin, lintDebug, assembleDebug and bundleRelease validation PASS. Gradle BUILD SUCCESSFUL in 3m 8s. Lint: zero errors, 12 warnings, 1 hint.
- Artifact 14560755289; GitHub digest and independently downloaded/recomputed ZIP SHA-256 `844d8cf09ede8ee9e7357d3461bfab6e557bce785bf4b1252a2aa470502af10b`; QA APK SHA-256 `ebeb5eb8725b8c265bc641f87046f80bb72e3150cb6018d825c35cb703c7917a`; release-validation AAB SHA-256 `62233609a6bb52f27a6905a028bcd5335f593c045e3ec60b5cb84cdd5a7c0fd9`. Artifact source marker is exact. AAB has no META-INF signing entries and is unsigned. Candidate metadata uses versionCode 51019 only for QA/validation; no release allocation.
- PR #297 is closed unmerged as superseded by #303. The old #297 source was transplanted into #303 and is not the active review target.

## GPS and session behavior in the selected source

- Fused Location Provider primary; permission-aware fallback to one eligible Android framework provider. Fine permission may select GPS; coarse-only uses Network. No GPS provider request without fine permission.
- Fine-to-coarse downgrade and provider changes clear the old source anchor. Distance is not bridged across providers.
- Mock, invalid, stale/future, out-of-order, poor-accuracy and implausible fixes are rejected.
- Distance accumulator applies endpoint-accuracy uncertainty deadband, multi-fix confirmation, long-gap re-anchoring and bounded path/net ratio. This is filtering, not proof against prolonged stationary multipath drift.
- V3 checkpoint preserves phase, wall/monotonic clocks, boot identity and bounded route. Restore does not credit process downtime.
- Foreground service, START_STICKY, ongoing notification, Pause/Resume/Finish actions and periodic local checkpoint writes are present in source. Screen-off/background and process-death behavior remain unverified on the handset.

## PR #284 historical reconciliation and current state

- Requested historical run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) succeeded on historical SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`. Artifact 13707718861 was downloaded and independently rehashed: ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`; embedded source marker matches that historical SHA. Its AAB SHA-256 was `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`, unsigned. This does not validate the current #284 head.
- Run [42694199295](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694199295) failed on historical SHA `4d0a9a2fea1ba71264b9f0aa7d3b957681a1571c` at source-contract test `test_android_main_activity_delegates_motion_to_engine` because `motionSnapshot` was absent from the then-truncated MainActivity. No candidate artifact was produced.
- Current PR #284 branch head: `274155eafdfff381009ef5814a621f32b225f1a8`; canonical compare: 19 ahead / 69 behind; 13 changed files; no exact-head CI. Current MainActivity at this exact head is 1,146 lines and contains `motionSnapshot`; blob `9d92bc47dfe317e1739b1d952f22ac00b10c00f6`.
- #284 overlaps #303 in native provider/service/presentation code and tests. It also changes shared app.js/index.html (overlaps #216/#224) and MainActivity/source-contract tests (overlaps #93). Keep #284 Draft and unmerged; only extract a map-only Leaflet/UI/assets handoff after explicit ownership separation and exact-head CI.

## Maps decision

- Selected no-billing map stack: Leaflet in WebView; attributed OpenStreetMap streets; OpenTopoMap terrain; EOX Sentinel-2 cloudless 2016 satellite and hybrid layers.
- Browser tile caching is not a guaranteed offline map package. No native Google basemap, traffic or transit overlay is present or claimed.
- Do not add archived Google Maps Rx, Maps SDK billing or a key for this selected stack. No paid infrastructure was provisioned.

## Health, anti-cheat and competitions

- Canonical Health Connect allowlist remains five scopes: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE and READ_ACTIVE_CALORIES_BURNED. No READ_HEART_RATE permission was added. PR #93 remains Draft and requests 19 scopes; do not merge without reducing to the canonical five and exact-head tests.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` is present and unit-tested but remains unwired in `ActivityTrackingService`. GPS filters are not full anti-cheat, cryptographic location attestation or proof of genuine activity.
- PR #269 is merged, but current competition support remains provisional `strength_volume_kg_reps`; no independently verified physical activity leaderboard or reward eligibility. `rewardEligible=false`; no THF payouts are authorized.

## Route backup / sync — separate gap

- `persistFinishedActivity()` stores completed GPS route history in WebView localStorage.
- Existing authenticated `/api/v2/workouts/sync` and `/api/v2/workouts?limit=200` carry workout/set metadata only. No authenticated route endpoint/table or precise-location cloud upload was found.
- Route backup remains design-only. Any future implementation requires separate account-level and per-session precise-location consent, finished-session-only upload, retention, revocation, deletion and privacy/security review. Do not conflate it with the approximately one-second local map UI refresh.

## Current PR / lease snapshot

| PR | Current state | Compare to canonical | Decision |
|---|---|---:|---|
| #303 GPS | Draft; head `6e73d988...`; exact run 44582044304 PASS | 1 ahead / 0 behind; 14 native files | Physical P0 before merge |
| #284 Maps/GPS | Draft; head `274155ea...`; no exact-head CI | 19 ahead / 69 behind; 13 files | Stale/overlapping; map-only extraction |
| #304 Health reconciliation | Merged at `e28994ea...`; exact run 44532209892 PASS | 3 Health files | Integrated |
| #93 Health services | Draft | 2 ahead / 372 behind | 19 requested scopes versus five allowed |
| #216 session resume | Draft; noncanonical base | 201 ahead / 227 behind | Shared app.js; no merge |
| #224 offline demos | Draft; noncanonical base | 153 ahead / 227 behind | Shared app.js/assets; no merge |
| #248 GPS smoother | Draft | 4 ahead / 206 behind | Helper not wired into service |
| #160 Arabic exercise cues | Draft; noncanonical base | 53 ahead / 227 behind | Catalog ownership; no merge |
| #213 timed RIR | Draft; noncanonical base | 190 ahead / 227 behind | Program semantics; no merge |
| #258 equipment filter | Draft | 7 ahead / 204 behind | No exact-head evidence |
| #257 Arabic cues | Draft | 5 ahead / 206 behind | No exact-head evidence |
| #260 Arabic cues | Draft; noncanonical base | 15 ahead / 206 behind | No exact-head evidence |
| #297 | Closed unmerged | Superseded | Do not reopen as active target |
| #302 / #301 / #282 / #269 | Merged | Canonical | Preserve current behavior |

File-level ownership and release authority are recorded in [INTEGRATOR_LEASES_CURRENT_20261119.md](INTEGRATOR_LEASES_CURRENT_20261119.md).

## Fresh Google Play readback — 2026-11-19

- Read-only publication probe [43739661313, attempt 4](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43739661313) completed successfully at 2026-11-19T17:55:08Z.
- Probe workflow blob SHA `33cf9e555e68e00b7990545720bd7e0403a96716` is identical at the run SHA and current canonical branch. It creates a temporary edit, reads details/listings/tracks, then deletes the edit; it does not write a published track or listing.
- Artifact 14558144305 ZIP SHA-256 `1b4b9eab4cbf550be74a0f191e477c895f736b0d718719ecdf019743ecd3ebed`, independently downloaded/rehashed. Embedded JSON SHA-256 `09e7a346e5e1c893d4323d20105d8f4d63`, independently recomputed.
- Package `com.topherofit.thf.pulse`: Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified. `uploadAttempted=false`, `commitAttempted=false`. Arabic and English listing titles/descriptions were read; no listing edit occurred.

## Device and release gates

- Latest Desktop Commander inventory on 2026-11-19: localhost OFFLINE, last seen 56 hours ago. Last known handset: Samsung SM-A217F / Android 12. Current installed app/session state is UNKNOWN; preserve it.
- No ADB, install, launch, force-stop, notification action, location-setting change or activity-data read was attempted. Last recorded device-wide `location_mode=0` remains historical only; no setting was changed.
- Physical P0 remains BLOCKED_NOT_RUN: stationary drift; measured outdoor walk/run/cycle; fine-to-coarse downgrade; first-fix latency/accuracy honesty; app navigation, screen-off/background/task removal; notification Pause/Resume/Finish; process-death restore without downtime credit; crash/ANR review.
- Owner Play write permission and GCP Secret Manager signing-key access remain NOT_VERIFIED.
- Internal 51019 remains the latest independently read release. Next Android versionCode 51020 is UNALLOCATED. No new signed AAB, Play upload, track mutation or Production promotion. Production remains NOT_VERIFIED.
- No paid infrastructure or unrelated project was used.
