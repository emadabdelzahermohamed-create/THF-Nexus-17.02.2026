# TopHeroFit GPS / map quality checkpoint — 2026-11-09

Canonical branch: `agent/codex/fitness-recovery/20261023`  
Canonical app-source SHA: `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`  
Canonical branch base confirmed: `c105b6c10d4d784b64a9e8ff25e4656073434629`  
Latest GPS candidate: [PR #283](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/283)

## Current GPS defect class

The activity UI could expose a previously accepted accuracy after GPS transitioned to stale/off/permission/filtered/acquiring. A missing accuracy could become a false `0 m` through JavaScript numeric coercion. Paused sessions retained a ready-state accuracy; resume could reuse pre-pause fixes; the map halo could remain around the last route point while GPS was not ready; and a process-death pending snapshot could expose checkpoint accuracy before a new fix.

## Tested candidate correction

- Candidate branch: `agent/codex/gps-accuracy-state-truth-20261109-r1`.
- Exact PR HEAD: `645d11cc141e1b40be98e1a53ebb20f979441f70`.
- Exact app/test source SHA: `d3f051103054c73a08bc4faf8c57fd100e15932f`.
- Candidate: 8 commits ahead / 0 behind canonical.
- Four commits after app/test source SHA change only the GPS and historical recovery documentation.
- Changed source/test paths: `ActivityTrackingService.kt`, `GpsFixPresentationPolicy.kt`, `GpsFixPresentationPolicyTest.kt`, `app.js`, `test_source_contract.py`.

The candidate:
1. Displays accepted accuracy only when state is `ready` and value is finite and positive.
2. Uses explicit `paused` state in activity snapshots and persistent notification.
3. Hides accepted/observed accuracy while paused.
4. Clears pre-pause observed/accepted fix state on resume until a fresh post-resume fix.
5. Hides the map accuracy halo unless GPS state is `ready`.
6. Clears checkpoint accuracy from process-death pending snapshots and reports paused/acquiring until a fresh fix.

This is a truthfulness/presentation correction. It does not change raw GPS fixes, provider configuration, route history, distance/speed/pace/calories, permissions or rewards. It is not evidence of physically accurate GPS, stationary-drift elimination, anti-spoofing, or background reliability.

## Exact-head CI and artifacts

[Android candidate run 42573716669](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42573716669) completed successfully on exact PR HEAD `645d11cc141e1b40be98e1a53ebb20f979441f70`.

- Product 60/60.
- Source-contract 36/36.
- Backend 29/29.
- Android unit 220/220; 0 failures, 0 ignored.
- Android API 36; `:app:testDebugUnitTest`, `:app:lintDebug`, `:app:assembleDebug`, `:app:bundleRelease` succeeded.
- Lint: 0 errors, 16 warnings, 1 hint.

Artifact 13654725577 downloaded and independently verified:

- ZIP SHA-256: `a2c28279cfbe30a82b6b0fc77a45fbdc28ab2d40139971f4b350e4f5b64c5161`.
- QA APK SHA-256: `76bb278f83f7797ab7b840fa466186b32ce37d9eee619f1801c4718ff1edd85b`.
- Validation AAB SHA-256: `e1d54e331a9611ad54891c1449ad0c0ed7fea97df604fee6f3406744f1c750b3`.
- Package identity: `com.topherofit.thf.pulse.qa`, validation code 51019 only.
- AAB signature inspection reports `jar is unsigned`; no release signing.

The AAB digest is identical to the previous exact app/test source run 42572575827. The latest workflow rebuilt the same AAB bytes after documentation-only commits; do not sign/upload it or call it a new release artifact.

## Merge status

PR #283 is Draft/open/unmerged. It changes `app.js`, also modified by PR #282 (Health metric null-vs-zero UI) and open exercise UX handoffs. Keep it held until shared `app.js` ownership is resolved; no overlapping handoff was merged.

## Google Maps status

Latest owner preflight remains [run 41684077962](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/41684077962), 2026-11-03:

- Maps Android Backend and API Keys APIs enabled.
- Release-builder key-inventory permission denied.
- No package/SHA-restricted Android key visible.
- No billing account linked.

Native Google Maps SDK/native basemap and supported traffic/transit remain blocked by owner API/key/billing prerequisites. Current map stack remains attributed OSM/OpenTopoMap/EOX with Google directions handoff. No billing, payment method, key, secret or paid infrastructure was changed.

## Physical P0

Authorized Desktop Commander device `localhost` is offline, last seen about 31 hours before the Nov 9 check. Last phone observation remains 2026-11-01T21:24:32Z on Samsung SM-A217F with Play-installed 51019 and foreground ActivityTrackingService; session was active/ambiguous. Current phone/session state is unknown; preserve it. No ADB, install, launch, Stop, session or activity-data action was attempted.

Physical checks still required:
- Stationary walk/run/cycle false accumulation.
- Real movement, GPS jumps, multipath/drift and short-loop distance.
- Background, screen-off, Home/tab switch, reopen, pause/resume and explicit Stop.
- Process-death recovery and notification metric truthfulness.
- Daily-vs-session step totals and history.

Physical GPS/phone/Google Maps PASS is not claimed. VersionCode 51020 remains unallocated.
