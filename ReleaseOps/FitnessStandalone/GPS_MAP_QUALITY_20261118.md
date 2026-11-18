# TopHeroFit GPS / Map Quality checkpoint — 2026-11-18

Scope: TopHeroFit only. Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.

## Canonical baseline and disjoint Health handoff

- Canonical branch: `agent/codex/fitness-recovery/20261023`.
- Canonical HEAD after exact-head-tested PR #301 merge: `7dc57dd9f6e647797cbbe2d1cfdb45773410a866`.
- PR #301 adds fail-closed Health Connect metric interval/value checks in three Health-only files. It does not change GPS, location permissions, map UI, release workflows, signing or Play.
- PR #301 exact-head run: [44315659269](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44315659269), source `853bd4e78b82d3b0db9203416a071bf360aa6a44`, SUCCESS. HealthMetricEvidencePolicyTest: 14/14; Product 69/69; Source contract 34/34; Backend 29/29; Android build/lint/bundle validation PASS.
- Artifact 14433350306 ZIP SHA-256 `afd8a019082ebc4341917ad753ad2be65d8f725bc21cc86cae870426c730b40d`; APK SHA-256 `9850fe1ec342cd1ba420546f7aa54c87cc0f82c1a5d6a9fc72f672fd5883185e`; unsigned validation AAB SHA-256 `914a0c6e5d40526a59152423ff72a3a575a882baf6cb3e43c582d110fdb711ae`. ZIP was downloaded and independently rehashed; AAB contains no signing entries. No release signing or Play upload.

## GPS candidate before canonical sync

- PR #297: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297
- Candidate branch: `agent/codex/gps-permission-downgrade-20261116-r1`; previous head `a007f62c6f7f088d60e9ed42c686c9cb45c5d407`.
- Exact-head CI run [44258464973](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44258464973) passed on exact branch head `a007f62c6f7f088d60e9ed42c686c9cb45c5d407`; Product 69/69, Source contract 34/34, Backend 29/29, Android unit 290/290, API 36, Kotlin, lint, assemble and unsigned bundle validation PASS. Zero Android test failures/ignored.
- Artifact 14407681576 ZIP SHA-256 `5483f5edfb08c2252ccc52132faf22287f13a36182dd15de253935239cc08c01`; APK SHA-256 `6c382e69f574bd9cf45748e4e15989f02bc76abbd2e4bf4bd670c2380e31959e`; unsigned AAB SHA-256 `c02f9ee942ab67261e76720927aff48dcfa129e4100d49e92f20195c10dcf5fb`.
- The AAB SHA is byte-identical to the prior exact-source run 44257340423; only the QA APK/ZIP packaging changed. Do not reupload or treat it as a new release artifact.
- Comparing canonical application base `b248a3571d871c604dbc3a11af72858bbac74eb9` with the GPS candidate shows 14 GPS Activity Engine source/test files only; no `app.js`, Health, MainActivity, Manifest, release, signing or workflow changes are part of the GPS source handoff.

## GPS implementation represented by the tested source

- Fused Location Provider is primary; a single permission-eligible framework provider is used for fallback.
- Fine permission permits GPS_PROVIDER; coarse-only permission selects NETWORK_PROVIDER.
- Android 12+ precise-to-approximate downgrade is detected by the watchdog; provider switches invalidate the old source anchor and distance accumulator.
- Bounded retry/backoff and generation guards prevent late Fused callbacks from reviving paused/stopped/replaced sessions.
- Fix gates reject mock, invalid, stale/future, out-of-order, poor-accuracy and implausible-speed/jump fixes.
- Stationary jitter uses the worse endpoint accuracy. Distance requires uncertainty-clearing displacement and multiple accepted fixes; prolonged stationary drift still needs physical proof.
- V3 session checkpoints preserve phase, wall/monotonic clocks, boot identity and bounded route; restore must not bridge process downtime.
- Foreground service, START_STICKY, ongoing notification, Pause/Resume/Finish actions and 10-second checkpoint writes exist in source. Screen-off/background, notification taps and process-death restore remain physical gates.

## Map and privacy boundaries

- Leaflet/WebView has OSM street, OpenTopoMap terrain, EOX Sentinel-2 cloudless 2016 satellite and EOX hybrid layers.
- Browser tile cache is not a guaranteed offline package. No native Google basemap, traffic/transit layer, Maps SDK, billing or API key is present or claimed.
- `persistFinishedActivity()` stores completed routes in WebView localStorage. No authenticated route upload/restore endpoint exists. Route sync remains design-only with separate opt-in precise-location consent, finished-session-only upload, retention, revocation and deletion requirements.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains unwired in `ActivityTrackingService`; no full anti-cheat or cryptographic location attestation is claimed.

## Physical P0

BLOCKED_NOT_RUN. Desktop Commander localhost is OFFLINE (last seen 31 hours before this check); last known handset SM-A217F / Android 12. Preserve the installed Play package and unknown session. No ADB, install, launch, Stop action, setting change or activity-data read was attempted. Outdoor measured routes, 60-second stationary drift, permission downgrade, first-fix latency, screen-off/background, notification taps, task removal and process-death restore remain unverified.

## Release boundary

PR #297 remains Draft/unmerged. VersionCode 51020 remains unallocated. No signed release AAB, Play upload, track mutation or Production promotion.
