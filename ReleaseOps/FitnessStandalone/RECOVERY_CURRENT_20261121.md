# TopHeroFit — candidate recovery checkpoint (2026-11-21)

Observed: 2026-11-21 06:48 UTC.
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical application HEAD: `d8e315376de6785ec93a792342618737866ae121`.
Canonical branch tip observed by compare: `38976e3f55d38bbe3ed624d2c776c1a34ad0eebf`.

This is a candidate-branch checkpoint pending PR #303 integration. The canonical branch's latest recovery file remains `RECOVERY_CURRENT_20261120.md`; its latest GPS file remains `GPS_MAP_QUALITY_20261120.md`. The requested 2026-11-01 GPS path is not present in the current canonical directory inventory.

## GPS owner handoff

PR [#303](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/303) remains OPEN, Draft and unmerged.

- Branch: `agent/codex/gps-activity-rebased-20261119-r1`.
- Exact tested application SHA: `ff082baf9a579766d4babab96c79480d68e2aa9a`.
- Current compare: 19 ahead / 4 behind canonical; 15 changed files.
- The four behind commits are documentation/checkpoint changes and do not overlap the GPS application/test paths.
- PR was mergeable at the latest PR readback; no merge was attempted.

### New source change

The Activity Engine now creates a distinct framework `LocationListener` per provider registration. Each listener captures its expected GPS/Network provider and generation. Queued callbacks from a replaced listener are rejected after a provider switch or teardown. The new policy unit test covers matching, mismatched, stale-generation and unknown-provider callbacks.

Commits added to the candidate branch:
- `8c4f8053db47f8bb2c0e4dd6719786fdcd4957b2` — provider/generation acceptance policy.
- `e9c62899d3abf8ed5b63fde0c2904244202d9efb` — listener instance and generation guard in ActivityTrackingService.
- `f8602818a7a6a85239192fbf56c4a0a3f473bcb5` — targeted GPS policy unit test.
- `ff082baf9a579766d4babab96c79480d68e2aa9a` — source-contract test updated for the extracted handler.

## Exact-head test and build receipt

[Workflow 44877063092](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44877063092) completed SUCCESS on exact source SHA `ff082baf9a579766d4babab96c79480d68e2aa9a`.

- Product: 77/77.
- Source-contract: 35/35.
- Backend: 29/29.
- Android API 36.
- Android unit tests: 331/331, 0 failures, 0 ignored.
- Kotlin/Gradle compile, lint, debug APK and unsigned AAB validation: PASS.
- Gradle BUILD SUCCESSFUL in 2m22s.
- Lint: 0 errors, 11 warnings, 1 hint.

Artifact `14697075475`, ZIP SHA-256 `9168becad8e9ee58c8261bb5fc7d77f0734065f9dc0d51342bc90c740f6f0a98`, independently rehashed. APK SHA-256 `0ef23a772689c0b6e9f54087f8b3d35af87b1c0fceed318c9b492196744ae217`. Validation AAB SHA-256 `ed3f2717b74bbdd0e804faede7ebc59d4134c495523703716df037082b44c523`; `jarsigner -verify` confirms the AAB is unsigned.

QA package: `com.topherofit.thf.pulse.qa`, versionCode `51019`, versionName `5.0.0-v2-alpha19-debug`. No version allocation, signing or Play action.

The immediately preceding run 44876802803 failed one source-contract assertion because it still used the old `override fun onLocationChanged` delimiter. The test was corrected and the final run 44877063092 passed. The failed intermediate run did not produce a build artifact.

## Physical device and cloud blockers

- Desktop Commander `localhost`: OFFLINE, last seen 92 hours before the 2026-11-21 check. Last known handset Samsung SM-A217F / Android 12; current state unknown.
- No ADB, install, launch, force-stop, notification interaction, location-setting change or activity-data read was attempted.
- Google Maps owner prerequisite remains unavailable: no owner key-management permission, no package/SHA-restricted Android key, and no linked Billing account in the latest canonical record.
- Existing map stack remains Leaflet, OpenStreetMap, OpenTopoMap and EOX Sentinel-2. No Google basemap, Traffic or Transit integration is claimed.

## Scope and exclusions

Changed files remain limited to the GPS/Activity Engine policy, service and tests, plus the GPS source-contract test and these candidate ReleaseOps checkpoints. No Health/anti-cheat or exercise catalog files, app.js, index.html, MainActivity, Manifest, release version/workflow/signing or Play files were edited.

## Next actions

1. Keep PR #303 Draft/unmerged until physical P0 is completed.
2. On reconnect, inspect the handset and any active activity before any install or interaction.
3. Run stationary drift, measured outdoor route, provider downgrade/switch, navigation/background/screen-off, notification actions and process-death restore.
4. Keep Google Maps SDK/key work blocked until the owner prerequisite is available; do not create billing or keys without authorization.
5. Do not allocate versionCode 51020 or publish until all hard gates pass.
