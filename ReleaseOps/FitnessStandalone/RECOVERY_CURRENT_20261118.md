# TopHeroFit canonical recovery candidate — 2026-11-18

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`. Scope: TopHeroFit Activity Engine, GPS/map quality and safe physical-device QA only.

## Authoritative starting points

- Historical starting GPS report: `GPS_MAP_QUALITY_20261101.md`, branch `agent/codex/gps-map-quality-20261030`, blob `0e50b45f7be1e2a245753233f3e70343394b1115`.
- Latest canonical GPS report before this run: `GPS_MAP_QUALITY_20261117.md`, blob `66a2ba33d7c3237f54c60453d05e668870ea0f3f`.
- Latest canonical recovery before this run: `RECOVERY_CURRENT_20261117.md`, blob `4ac6ebd10c91bf0fbf5fb16a8ddd100e29695cd8`.
- Canonical branch: `agent/codex/fitness-recovery/20261023`, documentation checkpoint HEAD `eb2e65780a7359ceb7da15edef9cdb03aad8591d`; canonical application/source head remains `b248a3571d871c604dbc3a11af72858bbac74eb9`.

## Current GPS candidate

- PR #297: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297
- Candidate branch: `agent/codex/gps-permission-downgrade-20261116-r1`.
- Exact tested application/source SHA: `16c5104a4f8af94f8b8c5bd71b4f52123e0caa4a`.
- The final source/test change adds a positive V1 route-checkpoint decode test. The prior commit fixes the test fixture newline so route parsing is actually reached. No production Kotlin source changed in these two final test-only commits.
- Current source diff is 14 GPS Activity Engine source/test files. No Health, anti-cheat, exercise catalog, `app.js`, MainActivity, manifest, workflow, release version, signing or Play file is part of the GPS source diff.
- New GPS report: `GPS_MAP_QUALITY_20261118.md`.

## Exact-head CI and artifacts

[Run 44257340423](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44257340423) completed SUCCESS on exact tested source SHA `16c5104a4f8af94f8b8c5bd71b4f52123e0caa4a`.

- Product tests 69/69.
- Source-contract tests 34/34.
- Backend tests 29/29.
- Android unit tests 290/290; 0 failures; 0 ignored.
- Android API 36, Kotlin compilation, lintDebug, assembleDebug and unsigned bundleRelease validation: PASS.
- Lint: 0 errors, 11 warnings, 1 hint.
- Artifact ID `14407185529`; GitHub ZIP digest and independent SHA-256 both `05abf94fc8c98de81bec6cacbf55e27a43bfcf0f7b4ce711d4012c9b01525ebd`.
- QA APK SHA-256 `07cba26c0f3250b3f174f9e78688cd262d5d4734d24497bbd9bf1c465d15167b`.
- Validation AAB SHA-256 `c02f9ee942ab67261e76720927aff48dcfa129e4100d49e92f20195c10dcf5fb`; jarsigner reports unsigned.
- QA identity only: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. No release signing or Play upload.

## Physical and owner-only blockers

- Latest Desktop Commander device list: `localhost` OFFLINE, last seen about 21 hours before the 2026-11-18 check. Last known handset Samsung SM-A217F / Android 12. No ADB device attached.
- No install, launch, force-stop, Stop action, settings/location-mode change or activity-data read was attempted. Preserve the installed Play package and unknown session.
- Prior 2026-11-16 limited QA is partial only: separate QA package, Play package 51019 preserved; stationary zero steps/distance; poor indoor fixes filtered; native bridge Pause/Resume toggled. No outdoor route, screen-off/background, notification tap or process-death physical PASS.
- Google Maps owner prerequisite remains unmet on last evidence (2026-11-03): Maps Android Backend and API Keys APIs enabled; key inventory permission denied; no package/SHA-restricted Android key; no linked billing account. No new Cloud access evidence, no billing, no key creation.
- Four real Leaflet base styles remain available: OSM street, OpenTopoMap terrain, EOX 2016 satellite and EOX hybrid. No native Google basemap, traffic or transit overlay.
- Shared `app.js` UI hold remains: ready state is labelled “GPS” even for Fused/Network, and paused state falls through to generic waiting text. `app.js` is owned/shared with #216/#224 and overlaps #284; do not edit until lease resolution and combined-head CI.

## Release and scope guard

- PR #297 remains Draft/unmerged until physical GPS/session P0 and shared UI/privacy gates pass.
- VersionCode 51020 remains unallocated.
- No release workflow/version/signing/secret/Play mutation; no signed AAB or Play PASS.
- No Health/anti-cheat or exercise-catalog changes. `ActivityEvidenceAnomalyPolicy.assessSegment()` remains unwired; no full anti-cheat or cryptographic location attestation is claimed.
- No route cloud upload/backup is implemented or claimed.
- The only changes after the exact tested source SHA are documentation checkpoint commits. Android CI evidence remains attached to the unchanged application/test source SHA `16c5104a4f8af94f8b8c5bd71b4f52123e0caa4a`.
