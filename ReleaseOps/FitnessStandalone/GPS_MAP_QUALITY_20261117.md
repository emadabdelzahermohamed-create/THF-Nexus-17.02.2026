# TopHeroFit GPS / Map Quality checkpoint — 2026-11-17

Observed: 2026-11-17T17:43:13Z (Africa/Cairo 19:43:13 +02:00). Scope: TopHeroFit only.

## Canonical and selected GPS handoff

- Canonical branch: `agent/codex/fitness-recovery/20261023`.
- Canonical application/source head before this documentation-only checkpoint: `b248a3571d871c604dbc3a11af72858bbac74eb9`.
- PR #297: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297
- Current exact tested PR head: `c340e330d8e634fab231976bac1b8f9ad44915cc`.
- Its first parent is the current canonical source head `b248a3571d871c604dbc3a11af72858bbac74eb9`; second parent is the previous tested GPS handoff `1bd1d4cb487bd9ce4eb1e263121e31a93b039028`.
- Compare against canonical at validation: 5 ahead / 0 behind; exactly 14 GPS Activity Engine source/test files. No app.js, Health, MainActivity, Manifest, ReleaseOps, signing or workflow files are in the GPS diff.
- PR remains Draft/open/unmerged. Physical P0 is still required.

## Exact-head CI and artifact evidence

[Android CI run 44139154404](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44139154404) completed SUCCESS on exact head `c340e330d8e634fab231976bac1b8f9ad44915cc`.

| Gate | Result |
|---|---:|
| Product tests | 69/69 |
| Source-contract tests | 34/34 |
| Backend tests | 29/29 |
| Android `:app:testDebugUnitTest` | PASS |
| Android `:app:lintDebug` | PASS |
| Android `:app:assembleDebug` | PASS |
| Android `:app:bundleRelease` | PASS_UNSIGNED |
| Gradle | BUILD SUCCESSFUL |
| Lint | 0 errors, 11 warnings, 1 hint |
| Competition backend job | Skipped; no competition files changed |

Artifact 14353801968 was downloaded and independently rehashed:
- ZIP SHA-256: `9634575de7c53d12a37470653ea610f37767df89b87a1a092117e6bbeee8249a` (matches GitHub artifact digest).
- QA APK SHA-256: `6cdc9a466da925cfd1293fdffbdf606be36a0ba64af99fa2027248ade3b9a8c7`.
- Validation AAB SHA-256: `486224f753a14a3f6bac9315273ba1bf862ce9d015023f63b84fa773a9f2334d`.
- `jarsigner -verify` confirms `jar is unsigned`.
- Candidate identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is QA-only, not a release allocation or Play package.

The final AAB differs from the earlier GPS-only validation AAB because this exact source tree includes the separately tested and merged #282 Health metric truthfulness fix. No unchanged bytes were intentionally rebuilt or reuploaded.

## GPS/provider and distance behavior in the tested source

- Fused Location Provider remains primary; one permission-eligible Android framework provider is used as fallback.
- Fine permission permits GPS_PROVIDER; coarse-only permission uses NETWORK_PROVIDER.
- Precise-to-approximate downgrade is detected by the watchdog and switches to the eligible network provider without waiting for the normal stale timeout.
- Fallback fails closed when coarse permission or NETWORK_PROVIDER is unavailable.
- Provider switches unregister the old provider and invalidate the prior source's live anchor; no distance is bridged across providers.
- Bounded initial/stale fallback, retry backoff and generation guards prevent late Fused callbacks from reviving paused/stopped/replaced sessions.
- A live fix gap beyond 30 seconds clears the stale speed/distance anchor. Route history remains displayable, but unobserved distance is not bridged.
- GPS UI distinguishes permission, device location switch, stale signal, filtered fix, accepted source, accuracy and paused state.

## Session persistence/background boundary

- ActivitySessionCheckpoint V3 records ARMED/ACTIVE phase, monotonic/wall clocks, boot identity and a bounded route.
- Lifecycle-critical checkpoint writes and deletion use synchronous commit; periodic sensor/location checkpoints may use apply.
- Restore rejects invalid/expired checkpoints; when boot identity is available the restore window is bounded to 24 hours, otherwise the legacy fallback is 120 seconds.
- Restored route points are historical display data. Only the original monotonic timestamp of a fresh fix (within the 30-second freshness gate) may seed a live anchor; process downtime is not added to an old fix.
- Foreground Service, START_STICKY, ongoing notification, Pause/Resume/Finish actions and 10-second checkpointing exist in source.
- Screen-off/background, task removal, notification action taps and process-death restore still require physical verification. Source CI is not physical acceptance.

## Physical QA status

<badge>BLOCKED — device offline</badge>

- Latest Desktop Commander device list at 2026-11-17T17:43:13Z: localhost OFFLINE, last seen about 8 hours earlier.
- Last known handset: Samsung SM-A217F / Android 12. The last recorded device-wide `location_mode=0` is from 2026-11-09; no current value is available.
- A prior limited QA note recorded Arabic RTL onboarding, QA package fine-location and ACTIVITY_RECOGNITION grants, native foreground service start, a Fused high-accuracy request, stationary zero steps/distance and indoor poor fixes filtered with no accepted route point. Native bridge Pause/Resume toggled expected state.
- That evidence does not prove outdoor route accuracy, a 60-second stationary drift P0, full UI/notification actions, screen-off/background, process-death restore or battery behavior.
- No ADB, install, launch, Stop, setting change or activity-data action was performed in this recheck. Preserve the installed Play package and unknown session.

## Maps stack

- Android WebView + Leaflet.
- Attributed OpenStreetMap-derived street tiles, OpenTopoMap terrain and EOX Sentinel-2 cloudless 2016 imagery.
- Browser cache is not a guaranteed offline tile package; no unlimited tile hosting is implied.
- No Google Maps SDK, billing, key, native Google basemap, traffic or transit overlay is added or claimed. Do not add archived Google Maps Rx.

## Separate authenticated route-sync gap

- `persistFinishedActivity()` stores completed route history in WebView localStorage.
- Existing `BackendSyncRepository` sends workout/set metadata only; no authenticated route endpoint or route upload/restore exists in the inspected Android/AppDeploy contract.
- `ROUTE_SYNC_DESIGN_20261110.md` remains design-only. It already specifies separate default-off summary and precise-route consent, per-session opt-in, finished-session-only uploads, bearer auth, idempotency, server-derived account identity, retention/deletion/revocation, account-deletion integration and privacy/security tests.
- The one-second map/UI refresh is local presentation only. No GPS route upload or cloud backup is implemented or claimed.

## Anti-cheat boundary

- `ActivityEvidenceAnomalyPolicy.assessSegment()` exists and has policy tests.
- A direct source inspection of this exact GPS branch found zero calls to `assessSegment` in `ActivityTrackingService.kt`.
- `GpsFixGate` and `GpsDistanceAccumulator` provide mock/accuracy/time/speed/source-continuity filtering and re-anchoring, but this is not full anti-cheat, cryptographic device/location attestation or reward eligibility.
- Wire the segment policy into the live service only as a separately tested follow-on handoff after the current GPS ownership/P0 gate is resolved.

## Historical #284

- Historical run 42694452852 passed only for old head `3fcbe6acbb4dc660284c74c8392818996e1de7ee`.
- Current #284 head remains `274155eafdfff381009ef5814a621f32b225f1a8`; compare to current canonical: 19 ahead / 61 behind, diverged, no current-head CI.
- #284 overlaps #297 native GPS files, #93 MainActivity/Manifest/Health bridge and #282/#216/#224 app.js. Keep Draft; do not merge wholesale.
- Unique map-only work, if still required after P0, must be isolated from shared files and tested against current canonical.

## Play / release boundary

Latest available independent read-only Play probe remains [run 43739661313, attempt 2](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43739661313), completed 2026-11-16 17:56:42Z:
- Internal: 51019 Completed.
- Alpha: 51007 Draft.
- Production: not listed / not verified.
- Upload and commit attempts: false.
- Probe ZIP SHA-256: `c3634fa8a1c4c462deecf4ad6582db0c395481a7b8758051b709374d55e7a025`.
- Embedded JSON SHA-256: `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.
No newer Play probe was found in the latest 100 workflow runs; no fresh 2026-11-17 Play readback is claimed.

VersionCode 51020 remains unallocated. Owner Play write permission and signing/Secret Manager prerequisites remain unverified. No signing, AAB upload, track mutation, listing change or Production promotion occurred.
