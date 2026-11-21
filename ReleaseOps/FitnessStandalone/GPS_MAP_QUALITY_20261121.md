# TopHeroFit — GPS / Activity Engine checkpoint (2026-11-21)

Observed: 2026-11-21 06:48 UTC (exact-head candidate workflow completion).
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical application HEAD: `d8e315376de6785ec93a792342618737866ae121`.
Current canonical branch tip observed by compare: `38976e3f55d38bbe3ed624d2c776c1a34ad0eebf`.

## Source-of-truth recovery

The requested `GPS_MAP_QUALITY_20261101.md` path is not present in the current canonical `ReleaseOps/FitnessStandalone` directory. The newest available canonical GPS checkpoint is `GPS_MAP_QUALITY_20261120.md`; the newest canonical recovery checkpoint is `RECOVERY_CURRENT_20261120.md`. This candidate checkpoint extends those records without modifying the canonical branch directly.

## Current GPS candidate

PR [#303](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/303) remains Draft and unmerged.

- Branch: `agent/codex/gps-activity-rebased-20261119-r1`.
- Exact tested application/source SHA: `ff082baf9a579766d4babab96c79480d68e2aa9a`.
- At application SHA `ff082baf9a579766d4babab96c79480d68e2aa9a`, the source/test comparison was 19 ahead / 4 behind across 15 application/test files. After adding and refreshing both candidate checkpoint documents, the final PR branch comparison is 23 ahead / 4 behind with 17 changed files; the four behind commits are canonical documentation/checkpoint changes and do not overlap the 15 application/test paths.
- The four behind commits are canonical checkpoint/documentation changes and do not overlap the 15 GPS application/test paths.
- The candidate still excludes `app.js`, `index.html`, `MainActivity`, Manifest, Health, anti-cheat, exercise catalog, release/version, workflow, signing and Play files.

## Material GPS fix — late callbacks after provider replacement

The framework fallback previously registered the service itself as the `LocationListener` for both GPS and Network. After `removeUpdates()` and a provider switch, an already queued callback could still arrive on that same listener. It could then be treated as a current fix even though its source belonged to the provider that had just been replaced.

The candidate now:

- Creates a distinct `LocationListener` instance for each legacy-provider registration.
- Captures the expected provider and a monotonically increasing registration generation in that listener.
- Accepts a callback only when both the generation and provider label still match.
- Invalidates the generation before removing the exact listener during provider switch, source cleanup, pause/stop and session teardown.
- Keeps Fused callbacks on the shared location handler; framework callbacks enter that handler only after the provider/generation guard.
- Prevents a queued GPS callback from contaminating a Network stream, and vice versa, after a provider transition.

New unit test: `legacyProviderCallbacksMustMatchTheCurrentProviderAndRegistrationGeneration`. It covers matching GPS and Network callbacks, provider mismatch, stale generation, null provider and a Fused label on a legacy registration.

The first CI attempt on intermediate SHA `f8602818a7a6a85239192fbf56c4a0a3f473bcb5` exposed a source-contract delimiter that still expected the old service override. The source-contract test was corrected to target `private fun handleLocationChanged`; the final exact-head run below passed.

## Exact-head CI evidence

- [Run 44877063092](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44877063092) — SUCCESS on exact application SHA `ff082baf9a579766d4babab96c79480d68e2aa9a`.
- Product tests: 77/77.
- Source-contract tests: 35/35.
- Backend tests: 29/29.
- Android API 36; Android unit tests: 331/331, 0 failures, 0 ignored.
- Kotlin/Gradle compilation, `:app:lintDebug`, `:app:assembleDebug` and `:app:bundleRelease` validation all passed.
- Gradle: BUILD SUCCESSFUL in 2m22s.
- Lint: 0 errors, 11 warnings, 1 hint.

Artifact ID `14697075475`, 63,082,733 bytes. GitHub ZIP SHA-256 `9168becad8e9ee58c8261bb5fc7d77f0734065f9dc0d51342bc90c740f6f0a98`; downloaded and independently rehashed to the same digest.

- Embedded source marker: `SOURCE_SHA=ff082baf9a579766d4babab96c79480d68e2aa9a`.
- QA APK SHA-256: `0ef23a772689c0b6e9f54087f8b3d35af87b1c0fceed318c9b492196744ae217`.
- Validation AAB SHA-256: `ed3f2717b74bbdd0e804faede7ebc59d4134c495523703716df037082b44c523`.
- ZIP, APK and AAB digests were independently recomputed from the downloaded artifact.
- `jarsigner -verify` reports `jar is unsigned` for the validation AAB.

QA identity only: package `com.topherofit.thf.pulse.qa`, versionCode `51019`, versionName `5.0.0-v2-alpha19-debug`. This is not a production package or release artifact; no version allocation or Play action occurred.

## Google Maps / cloud prerequisite

The canonical 2026-11-20 checkpoint records Maps Android Backend API and API Keys API enabled, but owner key-management permission unavailable, no Android package/SHA-restricted key, and no Billing account linked. No owner-only Cloud permission or key prerequisite became available in this run.

The app remains on Leaflet/WebView with attributed OpenStreetMap streets, OpenTopoMap terrain and EOX Sentinel-2 imagery. No native Google basemap, Traffic or Transit layer is integrated or claimed. No billing, paid service or API key was introduced.

## Physical device QA — BLOCKED_NOT_RUN

A single Desktop Commander device-list read on 2026-11-21 reported `localhost` OFFLINE, last seen 92 hours earlier. Last known handset: Samsung SM-A217F / Android 12; current device, app and activity-session state are unknown.

No ADB command, APK install, app launch, force-stop, notification action, location-setting change or activity-data read was attempted.

Still required on the physical handset:
1. Stationary drift with screen on/off and a measured 60-second stationary interval.
2. Outdoor walk/run/cycle against a measured reference route.
3. Fine-to-coarse permission downgrade and provider-switch callback behavior.
4. First-fix latency and honest reported accuracy.
5. In-app navigation, background, screen-off and task-removal continuity.
6. Notification Pause/Resume/Finish behavior.
7. Process-death restore without downtime credit, plus crash/ANR review.

No GPS, route, notification, physical exercise or handset QA PASS is claimed.

## Release gate

Keep PR #303 Draft/unmerged until physical P0, privacy/policy and release gates pass. No version allocation, signing, AAB upload, track mutation or Production promotion. VersionCode 51020 remains unallocated.
