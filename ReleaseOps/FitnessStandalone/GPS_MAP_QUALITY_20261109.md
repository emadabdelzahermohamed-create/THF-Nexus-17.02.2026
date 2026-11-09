# TopHeroFit — GPS accuracy presentation and Activity Engine checkpoint

Date: 2026-11-09 (Africa/Cairo)  
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
Canonical branch: `agent/codex/fitness-recovery/20261023`  
Canonical base at branch creation: `c105b6c10d4d784b64a9e8ff25e4656073434629`

## Source-of-truth review

- Re-read the requested historical `GPS_MAP_QUALITY_20261101.md` from `agent/codex/gps-map-quality-20261030`, blob `0e50b45f7be1e2a245753233f3e70343394b1115`. That path is not present on the current canonical branch.
- Re-read the newest canonical GPS report `GPS_MAP_QUALITY_20261108.md`, blob `44d1a3e751f193d7e95377ed1e9df526b95ba495`, and recovery checkpoint blob `578be4a435991324d3eb3263e5e7127f479ec569`.
- Canonical branch head remained `c105b6c10d4d784b64a9e8ff25e4656073434629`. Candidate base is exact; 0 commits behind canonical; commits after the exact app/test source HEAD are documentation-only.

## Defect and correction

The activity metric displayed `lastAccuracyMetres` regardless of `gpsFixState`. Stale/off/permission/filtered/acquiring states could therefore display an old accepted accuracy. JavaScript `Number(null)` could also turn a missing accuracy into a false `0 m`.

Paused sessions retained the previous ready accuracy; resume could reuse pre-pause observations; the map accuracy halo persisted around the last route point while GPS was not ready; and the pre-service process-death restore snapshot could briefly expose checkpoint accuracy.

Draft PR #283 corrects these paths:
- Accepted accuracy is visible only for `ready` plus a finite positive value.
- Paused snapshots and persistent notifications use an explicit `paused` GPS state and hide accepted/observed accuracy.
- Resume clears pre-pause observed and accepted fix state until a fresh post-resume fix.
- The map accuracy halo is hidden unless current GPS state is `ready`.
- Process-death pending snapshots report `paused` or `acquiring` and clear checkpoint accuracy until a fresh fix.
- Arabic/English paused copy and Kotlin/source-contract regressions are included.

This changes presentation/state only; it does not change raw fixes, provider settings, route history, distance, speed, pace, calories, permission scope or rewards.

## Exact Git evidence

- Candidate branch: `agent/codex/gps-accuracy-state-truth-20261109-r1`
- Current branch HEAD is the tip containing this evidence update; PR #283 carries the exact current SHA.
- Source/policy/test commit: `4571f59ee57438a979c759c864ac204e94008110`
- Map halo follow-up: `04893e88c8c2b9a37ce9dcf27ab64b286d847e94`
- Test discovery correction: `24fb52d8dccc9cb07f27ca2c2cfdefc315ffa30a`
- Process-death pending-snapshot fix; exact app/test source HEAD: `d3f051103054c73a08bc4faf8c57fd100e15932f`
- [PR #283](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/283): Draft, open, unmerged; 0 commits behind canonical; commits after the exact app/test source HEAD are documentation-only.
- Exactly five changed files: ActivityTrackingService, GpsFixPresentationPolicy, its tests, app.js, and the focused Python source-contract test.

## Verification

- Local exact-source audit: 12/12 checks passed, including JavaScript parse, policy contract, paused/resume/restore state, null handling, map halo gating and test discovery.
- Prior exact-head Android run [42572427384](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42572427384) on `24fb52d...` succeeded: product 60/60, source-contract 36/36, backend 29/29; Android unit-test, lint, Debug APK and validation AAB tasks succeeded.
- That prior-head QA APK SHA-256: `3ea328bbe4d223b08fd45d8dbab45e4317eab7027df27ee80c0a64b3957a8a7e`; validation AAB SHA-256: `77589134aff074df821cae94008df5bffb1cb0bb39ab1a213dec3b9a2e803955`. Package identity: QA `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. These artifacts are not from the final source HEAD and were not uploaded to Play.
- Exact final app/test source HEAD `d3f051103054c73a08bc4faf8c57fd100e15932f`: [run 42572575827](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42572575827) completed SUCCESS after one failed-job rerun for a transient Kotlin compiler HTTP 504. Product tests 60/60, source-contract tests 36/36, backend tests 29/29; Android API 36 install, `:app:testDebugUnitTest`, `:app:lintDebug`, `:app:assembleDebug`, and `:app:bundleRelease` all succeeded.
- Exact final-head QA APK SHA-256: `621aa86277c1126829991c39ed4b961207c4319e39d185f30e6c778bf9a8383b`; validation AAB SHA-256: `e1d54e331a9611ad54891c1449ad0c0ed7fea97df604fee6f3406744f1c750b3`; artifact `13654301552`. Package identity: QA `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. These are validation artifacts only; no Play upload or production release signing action occurred.
- Earlier run 42572223046 and the first attempt of 42572575827 hit external HTTP 504 responses while downloading Gradle/Kotlin dependencies. The single failed-job rerun for the final source succeeded; no retry loop was used.
- Earlier run 42572223046 also hit an external Gradle-distribution HTTP 504. Treat these as transient infrastructure, not source failures; do not retry-loop.

## Google Maps gate

Latest recorded owner preflight [41684077962](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/41684077962), 2026-11-03: Maps Android Backend and API Keys APIs enabled; key-inventory permission denied; no package/SHA-restricted Android key visible; no billing account linked. No permission retry, billing change, payment method, key, secret or paid infrastructure was attempted. Native Google basemap and supported traffic/transit remain owner-gated. Current map stack remains attributed OSM, OpenTopoMap and EOX 2016 plus Google directions handoff.

## Physical-device safety

Authorized Desktop Commander `localhost` is OFFLINE, last seen 19 hours before this check. No ADB, install, launch, stop or session action was attempted. Phone/session state is unknown and must be preserved. Physical GPS accuracy, stationary drift, background/screen-off, pause/resume/stop and process-death P0 remain `BLOCKED_NOT_RUN`.

## Release boundary and next gates

No Health/anti-cheat, exercise catalog, release version, workflow, signing, secrets, billing or Play files changed. VersionCode 51020 remains unallocated; no Play upload or Play PASS is claimed.

1. Complete the single failed-job rerun for `d3f05110...`; do not loop if the same external 504 recurs.
2. Keep PR #283 Draft until exact-head Android validation completes.
3. Resume physical P0 only when the authorized phone is online and the existing session is confirmed safely idle.
4. Implement native Google Maps only after the owner prerequisite and secure package/SHA key provisioning are available.
