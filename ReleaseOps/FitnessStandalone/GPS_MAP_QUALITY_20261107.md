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
- Exact-head Android CI, Node syntax check, Android Gradle/JUnit, lint, APK/AAB: pending after the candidate push; no PASS claimed yet.

## Google Maps owner gate

Latest recorded owner preflight remains 2026-11-03, run `41684077962`: Maps Android Backend and API Keys APIs enabled; key-inventory permission denied; no restricted Android key visible; no billing account linked. This prerequisite remains blocked. No billing, key, secret, or paid infrastructure was changed.

The in-app map remains the attributed free OSM street, OpenTopoMap terrain, and EOX 2016 satellite/hybrid stack. There is no native Google basemap, traffic, or transit layer in this candidate.

## Physical-device QA

Authorized Desktop Commander device `localhost` was offline at the 2026-11-07 recheck (last seen 115 hours earlier). No ADB, install, launch, Stop, or activity-session action was attempted. Phone/session state remains unknown. Physical GPS, stationary-drift, background, screen-off, process-death, and notification P0 are **BLOCKED_NOT_RUN**.

## Scope boundary

This candidate changes only Activity Engine/GPS presentation code, focused tests, the activity UI status text, and GPS/recovery evidence. It does not change Health/anti-cheat code, exercise catalog data, workflows, release version, signing, or Play.

Historical repository note: PR #267 was already merged on 2026-11-06. GitHub's merged-file list for that PR includes Health provenance files and `.github/workflows/fitness-sensor-candidate.yml`. Those are pre-existing canonical history, not changes in this run; this run does not edit them.
