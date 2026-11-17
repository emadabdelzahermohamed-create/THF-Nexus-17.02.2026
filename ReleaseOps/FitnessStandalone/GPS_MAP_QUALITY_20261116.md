# TopHeroFit GPS / Maps quality checkpoint — 2026-11-16

Scope: TopHeroFit Activity Engine, GPS quality, Maps readiness, session persistence and safe QA only.
Canonical repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical base at exact-head validation: `fbb63025ef0d6dbfe22c7661b049a4b72da2b5a0`.

## Selected GPS handoff
- PR #297: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/297
- Branch: `agent/codex/gps-permission-downgrade-20261116-r1`.
- Exact PR HEAD after canonical rebase: `1c099845979a998dc0d374322f471c39400e566e`.
- Compare: 8 commits ahead / 0 behind; exactly eight GPS source/test files; no Health, app.js, MainActivity, manifest, workflow, release or signing files.
- Rebase used force-with-lease from old head `d572bae1baea0ea01fdca91d39cc089a30378e90` onto canonical `fbb63025ef0d6dbfe22c7661b049a4b72da2b5a0`.
- PR remains Draft; do not merge until physical P0 and release/privacy gates pass.

## Exact-head CI and artifacts
[Run 43923207674](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43923207674) completed SUCCESS on exact PR HEAD `1c099845979a998dc0d374322f471c39400e566e`.
- Product tests: 67/67.
- Source-contract tests: 34/34.
- Backend tests: 29/29.
- Android unit tests: 273/273; 0 failures; 0 ignored.
- Android API 36, Kotlin compilation, lintDebug, assembleDebug and unsigned bundleRelease validation: PASS.
- Lint: 0 errors, 16 warnings, 1 hint.

Artifact 14253604668 was downloaded and independently rehashed:
- ZIP SHA-256: `58c87c1a0ebf5d5a606375fee5a56aad2cf39ef2accd02f068ae8b8b199cc1aa`.
- QA APK SHA-256: `65cdf02aade50cb3916932e9af8187dd13ea5e21e38fe997ee795dcc3b283d98`.
- Validation AAB SHA-256: `6e9d73ecf9a50838e17a7c3551f41931d21684d3e1c2af7dc443f5412250dfdc`.
- `jarsigner -verify` reports `jar is unsigned`.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. Validation only; never promote.

## GPS/provider behavior
- Fused Location Provider remains primary, with one permission-eligible Android framework fallback provider.
- GPS_PROVIDER requires fine permission; coarse-only permission selects NETWORK_PROVIDER.
- If Android 12+ downgrades precise to approximate while GPS is active, the four-second watchdog switches to eligible NETWORK_PROVIDER immediately instead of waiting for the normal 12-second no-fix timeout.
- The fallback fails closed when coarse permission or NETWORK_PROVIDER is unavailable.
- Provider switches unregister the old provider and invalidate the previous source's live anchor/accumulator; no distance is bridged across providers.
- Bounded 8-second initial fallback, 12-second stale/no-fix fallback, retry backoff and generation guards prevent late Fused callbacks from reviving paused/stopped/replaced sessions.
- A live fix gap beyond 30 seconds clears the stale speed/distance anchor; activity and route history remain, but unobserved distance is not bridged.
- GPS presentation separates permission, device location switch, stale signal, filtered fix, accepted source, accuracy and paused state.

## Filtering and anti-cheat boundary
- GpsFixGate rejects mock/invalid coordinates, poor accuracy, stale/non-monotonic timestamps and sport-speed violations.
- GpsDistanceAccumulator enforces source continuity, re-anchors on provider change or long gap, uses endpoint-accuracy deadband, requires persistent threshold-crossing excursion and caps path inflation.
- `ActivityEvidenceAnomalyPolicy.assessSegment` exists and has tests but is not called by `ActivityTrackingService`. Do not claim full anti-cheat, cryptographic device/location attestation or reward eligibility.
- Passing source-level tests do not establish real GPS accuracy, genuine movement or physical device provenance.

## Session persistence/background boundary
- Source contains a Foreground Service, START_STICKY, local checkpoint every 10 seconds, ongoing notification and Pause/Resume/Finish controls.
- Restored route history is display/history only; only a fresh monotonic checkpoint may seed a live speed anchor. Stale anchors are cleared.
- Physical screen-off/background, notification controls, process-death restore and real movement tests remain BLOCKED_NOT_RUN.

## Maps stack
- Leaflet in Android WebView.
- OpenStreetMap street tiles, OpenTopoMap terrain and EOX Sentinel-2 cloudless 2016 imagery.
- WebView `LOAD_DEFAULT` is ordinary browser cache, not a guaranteed offline tile package.
- Tile providers have attribution and usage policies; free endpoints are not unlimited bulk/offline hosting.
- No Google Maps SDK, billing, API key, native traffic or transit overlay is used or claimed. Google directions is an optional external handoff.

## Separate route-sync gap
- Finished route history remains in WebView localStorage.
- Existing authenticated workout sync sends workout/set metadata only; no authenticated route endpoint or cloud route backup/restore exists.
- `ROUTE_SYNC_DESIGN_20261110.md` remains design-only with separate summary/precise-route consent, per-session opt-in, retention, deletion and revocation. No precise-location upload by default.

## Physical device and release gates
- Desktop Commander `localhost`: OFFLINE; last seen about 151 hours at the 2026-11-16 check.
- Last known handset: Samsung SM-A217F / Android 12. Current device/session state is unknown.
- No ADB, install, launch, Stop, settings or activity-data action was attempted.
- Physical P0 remains BLOCKED_NOT_RUN: stationary 60-second drift, measured walk/run/cycle, precise-to-approximate permission downgrade, first-fix latency, screen-off/background, notification Pause/Resume/Stop and process-death recovery.
- Latest read-only Play probe attempt 2 completed 2026-11-16 17:56:42Z: Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified. Upload and commit attempts were false. No Play mutation.
- VersionCode 51020 remains unallocated. No release signing, AAB upload, Play track mutation or Production promotion.

## 2026-11-17 addendum — stale restore-anchor correction and partial physical QA

### New Activity Engine defect found and fixed
- Code review of the exact PR #297 source found that process-death recovery computed a saved route fix timestamp as `adjustedStartedAtElapsedMs(checkpoint, now) + point.elapsedMs`.
- `adjustedStartedAtElapsedMs` intentionally advances the session clock by the process downtime. Adding an old route-point offset to that adjusted start therefore advanced the old GPS fix by the same downtime and could make a stale checkpoint anchor appear fresh.
- Fixed in commit `349fcbb40ffbda9641e33ab68637b29c99bc960e`: `restorableLastFixElapsedMs` reconstructs the actual fix time from the checkpoint's persisted, pre-adjustment monotonic start; it refuses paused, non-active, missing/invalid-accuracy, missing-route, out-of-window and overflow cases.
- The service now seeds a live anchor only when that original timestamp is still within the 30-second freshness window. Route history remains available for display; an unobserved process-death gap is not bridged.
- Four regression tests cover stale downtime, fresh-window preservation, paused/missing-accuracy rejection, repeated restore without a new fix, and the new post-restore time base.

### Exact-head validation and artifact evidence
- PR #297 remains Draft / unmerged.
- Canonical base at validation: `a2000151de09adaf4344e8d2626b14cc0140aa0e`.
- Exact tested PR HEAD: `349fcbb40ffbda9641e33ab68637b29c99bc960e`; compare was 11 commits ahead / 0 behind, with exactly ten Activity Engine/GPS source and test files.
- [Android CI run 44038771808](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44038771808) completed SUCCESS on that exact HEAD.
- Product tests 67/67; source-contract tests 34/34; backend tests 29/29; Android unit tests 281/281, 0 failures, 0 ignored.
- Android API 36, Kotlin compilation, `lintDebug`, `assembleDebug`, and unsigned `bundleRelease` validation passed. Lint: 0 errors, 11 warnings, 1 hint.
- Artifact 14308053640 was downloaded. ZIP SHA-256 `04d8ce00108a16e1626b01776593539d7e05e4243b1e78206f843f8fb83731f6` matches GitHub's artifact digest. QA APK SHA-256 `60be32097cd943685d920140483f5d226e1b786ed977441ee383ddd4c605a5d4`; validation AAB SHA-256 `b20e592fb473b8227df58681aaf44aac11cddcd449bd32de1fb4412d8536ebeb`. `jarsigner -verify` reports `jar is unsigned`.
- QA identity remains `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is validation only, not a production package.

### Physical QA evidence — limited, not P0 PASS
- The 2026-11-16 PR #297 QA note records the exact earlier QA APK SHA `65cdf02aade50cb3916932e9af8187dd13ea5e21e38fe997ee795dcc3b283d98` installed under `com.topherofit.thf.pulse.qa`; the Play package `com.topherofit.thf.pulse` remained installed at 51019, with no overwrite or data clear. The QA package was removed after that test.
- Arabic RTL onboarding completed without an observed startup crash/ANR. Fine location and ACTIVITY_RECOGNITION were granted to the QA package. The native foreground ActivityTrackingService started and Android recorded a Fused high-accuracy location request.
- Stationary observation reported zero steps and zero distance; indoor fixes around ±400 m and later ±59 m were filtered, with no route point accepted. This is not an outdoor accuracy or 60-second drift P0 PASS.
- Native bridge Pause and Resume returned `paused=true` and `paused=false`; Pause unregistered sensor/location sources and Resume reacquired them. Notification action taps and the complete on-screen Pause/Resume interaction were not proven.
- The QA note identified a real UI defect: `renderActivity` does not map `gpsFixState === 'paused'` to localized paused copy, so the screen falls through to generic GPS-waiting text. `app.js` remains under shared ownership holds (#282, #216, #224); no shared UI file was changed in this run.
- Outdoor walk/run/cycle, route acceptance, screen-off/background, task removal, process-death restore, notification action taps and battery P0 remain unverified.

### Safe device recheck — 2026-11-17
- Desktop Commander `localhost` is Online, but its host is the Samsung SM-A217F itself (Android 12 / Termux app context), not a separate ADB workstation.
- `adb devices -l` returned an empty device list. The unprivileged Termux shell has no `dumpsys` binary; therefore the live tracking-service, lock-screen and UI state could not be inspected.
- `cmd package path com.topherofit.thf.pulse` confirms the Play package path exists, but does not establish its version or whether an activity session is active.
- No install, launch, force-stop, Stop, settings change, activity-data read, or device-wide location action was attempted. Preserve the installed Play app and unknown session until a shell-level ADB/device inspection is available. Physical P0 remains blocked.

### Maps and release boundary
- Maps remain Leaflet/WebView with attributed OpenStreetMap streets, OpenTopoMap terrain and EOX Sentinel-2 imagery. Browser cache is not a guaranteed offline tile package.
- The 2026-11-01 Maps preflight and latest 2026-11-16 report still show no owner-authorized key inventory, no package/SHA-restricted Android key and no linked billing account. No Google Maps SDK, native Google basemap, traffic or transit overlay is added or claimed.
- No Health/anti-cheat, exercise catalog, release version/workflow, signing, secret, billing or Play files/actions were changed. VersionCode 51020 remains unallocated; no AAB upload or Play mutation occurred.
