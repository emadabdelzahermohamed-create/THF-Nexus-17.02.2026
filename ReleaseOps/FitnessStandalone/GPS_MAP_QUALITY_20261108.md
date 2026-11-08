# TopHeroFit — GPS permission presentation checkpoint

Date: 2026-11-08 (Africa/Cairo)
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
Canonical branch: `agent/codex/fitness-recovery/20261023`
Canonical base SHA: `b06ae31c39d3d010258b0b0189c99f9ef7e49d4f`
Candidate branch: `agent/codex/gps-permission-status-20261108-r1`
Source commits:
- `dae0722df7de06585d50831f8a53c1fd36618e80` — activity UI permission state.
- `58c826c566a65c8a15212c1414520cfee089a817` — source-contract regression.

## Material Activity Engine/UI correction

The previously integrated `GpsFixPresentationPolicy` distinguishes `permission`, `off`, `acquiring`, `stale`, `filtered`, and `ready`. Code review found one remaining UI fall-through: when the policy returned `permission`, the activity status pill still displayed the generic “acquiring high-accuracy location” message.

The activity UI now maps `gpsFixState === "permission"` to the existing permission-needed copy (`activityPermissionNeeded`). A source-contract regression asserts that mapping. This does not request new permissions or change the GPS provider, accepted fixes, route, distance, speed, rewards, or observed accuracy.

The underlying policy/service correction already present on the canonical base remains unchanged: a fresh fix rejected by movement/quality filters is presented as `filtered`, not inaccurately described as weak horizontal accuracy. The notification continues to distinguish observed-but-not-accepted fixes.

## Prior exact-head Android evidence (baseline only)

GitHub Actions [run 42345994357](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42345994357) passed on the earlier GPS presentation candidate HEAD `7192d2cff4886bea908215039b47bc1cb8ff6784`, before the permission-pill follow-up in this branch:
- Product/source-contract/backend regression step succeeded.
- Android API 36 setup succeeded.
- Android unit report: **159 tests, 0 failures, 0 ignored (100%)**.
- Lint: **0 errors, 16 warnings**.
- Debug APK and validation AAB packaging succeeded; Gradle reported BUILD SUCCESSFUL, 99 actionable tasks, 2m 43s.
- Artifact `13563827022` archive SHA-256 independently verified: `0fa296bdeb8f83c35b5da8577d6ea4eda58e3e441919754cf10cdb517939201e`.
- QA debug APK SHA-256: `01b07b5dfc0439ba12f2062b964384993a157aa7aaea19cdac435fb996b9054f`.
- Validation AAB SHA-256: `1a5ac6a962dc61adc1deac706616d6ba28e44acdb69aa3cfee546bbb28ae9789`; no JAR signing block entries were present. This is unsigned validation output only.

That run is baseline evidence, **not** an exact-head PASS for the new permission-pill commits. Current branch exact-head Android CI is required before merge; no PASS is claimed for the new follow-up yet.

## Google Maps owner gate

Latest recorded preflight remains 2026-11-03, run `41684077962`: Maps Android Backend and API Keys APIs enabled; key-inventory permission denied; no package/SHA-restricted Android key visible; no billing account linked. No billing, key, secret, or paid infrastructure changed.

The native Google basemap, traffic and transit layers remain unavailable. The current in-app map remains the attributed free OSM street, OpenTopoMap terrain, and EOX 2016 satellite/hybrid stack with Google Maps directions handoff only.

## Physical-device QA

Authorized Desktop Commander `localhost` was OFFLINE at the 2026-11-08 08:47 Cairo check (last seen about 1 hour earlier). No ADB, install, launch, Stop, or activity-session action was attempted. Current phone/activity state remains unknown and must be preserved.

Physical GPS accuracy, stationary drift, navigation, background, screen-off, process-death recovery, persistent notification and pause/resume/stop P0 remain **BLOCKED_NOT_RUN**.

## Scope and release boundary

This follow-up changes only `fitness-v2/android/app/src/main/assets/pulse/app.js`, the GPS source-contract assertion in `fitness-v2/tests/test_source_contract.py`, and this GPS/recovery evidence. It does not change Health/anti-cheat implementation, exercise catalog data, workflows, release version, signing, or Play.

Validation identity remains 51019 only. VersionCode 51020 remains unallocated. No production signing, Play upload, track/listing change, or Play PASS occurred.
