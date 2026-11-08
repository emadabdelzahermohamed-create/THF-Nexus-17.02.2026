# TopHeroFit — GPS fix presentation checkpoint

Date: 2026-11-07 (Africa/Cairo)
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
Canonical branch: `agent/codex/fitness-recovery/20261023`
Canonical base SHA: `bb57fc7b697a4df040e9b3fd094d23c59781ef58`
Candidate branch: `agent/codex/gps-path-inflation-guard-20261106-r1`
App-source commit: `a91b11658b72739c1f40d4465ee2b8359f8919e3`

## Material Activity Engine change

The Activity Engine previously classified every fresh observed fix newer than the last accepted fix as `weak`. That included accurate fixes intentionally rejected by the movement deadband or other acceptance filters. The user-facing text then claimed weak accuracy even when the reported horizontal accuracy was good.

Added `GpsFixPresentationPolicy` and wired it into `ActivityTrackingService`:

- `permission`: location permission is absent.
- `off`: GPS and network location providers are disabled.
- `acquiring`: no valid observation has arrived.
- `stale`: the latest valid observation is older than 30 seconds or has a future elapsed timestamp.
- `filtered`: a fresh observation exists but is not yet accepted for route/distance metrics.
- `ready`: the accepted fix is at least as recent as the latest valid observation.

The activity screen and foreground-notification status now say that a location was observed but not accepted for distance, and still display the reported accuracy. They no longer describe this case as weak accuracy. The policy uses Android elapsed-realtime timestamps, not wall-clock time.

This is a truthful UI/state-classification correction. It does not change accepted GPS fixes, distance, speed, route points, reward evidence, or GPS accuracy itself.

## Tests and evidence

- Local Kotlin/JVM harness for the exact policy logic: **9/9 PASS**.
- Added Android JUnit regression coverage for permission, provider-off, no observation, stale/future observation, filtered fix, and ready fix.
- Added repository source-contract coverage for the service-to-policy and UI state wiring.
- Exact-head Android CI run 42345994357 passed on candidate HEAD `7192d2cff4886bea908215039b47bc1cb8ff6784`: 159/159 Android unit tests, lint with 0 errors and 16 warnings, debug APK and unsigned validation AAB packaging. Artifact and binary hashes are recorded below.

## Google Maps owner gate

Latest recorded owner preflight remains 2026-11-03, run `41684077962`: Maps Android Backend and API Keys APIs enabled; key-inventory permission denied; no restricted Android key visible; no billing account linked. This prerequisite remains blocked. No billing, key, secret, or paid infrastructure was changed.

The in-app map remains the attributed free OSM street, OpenTopoMap terrain, and EOX 2016 satellite/hybrid stack. There is no native Google basemap, traffic, or transit layer in this candidate.

## Physical-device QA

Authorized Desktop Commander device `localhost` remained offline at the 2026-11-08 08:47 Cairo recheck (last seen about 1 hour earlier). No ADB, install, launch, Stop, or activity-session action was attempted. Phone/session state remains unknown. Physical GPS, stationary-drift, background, screen-off, process-death, and notification P0 are **BLOCKED_NOT_RUN**.

## Scope boundary

This candidate changes only Activity Engine/GPS presentation code, focused tests, the activity UI status text, and GPS/recovery evidence. It does not change Health/anti-cheat code, exercise catalog data, workflows, release version, signing, or Play.

Historical repository note: PR #267 was already merged on 2026-11-06. GitHub's merged-file list for that PR includes Health provenance files and `.github/workflows/fitness-sensor-candidate.yml`. Those are pre-existing canonical history, not changes in this run; this run does not edit them.


## Exact-head Android CI follow-up — 2026-11-08 (Africa/Cairo)

The previously pending validation has now completed on the exact candidate branch HEAD `7192d2cff4886bea908215039b47bc1cb8ff6784` (app-source commit `a91b11658b72739c1f40d4465ee2b8359f8919e3`).

- GitHub Actions run [42345994357](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42345994357): `changed-app` succeeded; `deterministic-build` succeeded; competition-backend was skipped as unrelated.
- The product/source-contract/backend regression step succeeded; Android API 36 setup succeeded.
- Android unit report: **159 tests, 0 failures, 0 ignored (100%)**.
- Android lint: **0 errors, 16 warnings**.
- Debug APK and validation AAB packaging completed; build log reports **BUILD SUCCESSFUL**, 99 actionable Gradle tasks, 2m 43s.
- Workflow artifact ID: `13563827022`; downloaded archive SHA-256 independently recomputed as `0fa296bdeb8f83c35b5da8577d6ea4eda58e3e441919754cf10cdb517939201e`.
- QA debug APK SHA-256: `01b07b5dfc0439ba12f2062b964384993a157aa7aaea19cdac435fb996b9054f`.
- Validation AAB SHA-256: `1a5ac6a962dc61adc1deac706616d6ba28e44acdb69aa3cfee546bbb28ae9789`. The AAB contains no JAR signing block entries; it is an unsigned validation bundle, not a production-signed artifact.
- Candidate build metadata remains validation identity `versionCode=51019`, `versionName=5.0.0-v2-alpha19-debug`. No version allocation, production signing, Play upload, track change, or release PASS occurred.

This is exact-head Android build/unit/lint evidence only. It is **not** physical GPS, Google Maps, background/screen-off/process-death device QA, or Play acceptance.
