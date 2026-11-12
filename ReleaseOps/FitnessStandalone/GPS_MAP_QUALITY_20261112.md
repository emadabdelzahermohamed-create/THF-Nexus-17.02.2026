# TopHeroFit — GPS and Activity Engine quality report

Date: 2026-11-12 (Africa/Cairo)  
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
Canonical branch: `agent/codex/fitness-recovery/20261023`  
Candidate PR: [#284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284)  
Candidate branch: `agent/codex/gps-open-source-stack-20261109`  
Exact candidate HEAD after this report/checkpoint commit: documented in the commit response; application source SHA is `68894a585e78df0a8d7b40cc68fa4f29acf10c9c`.

## Source-of-truth review

- Re-read the requested historical `GPS_MAP_QUALITY_20261101.md` from `agent/codex/gps-map-quality-20261030`, blob `0e50b45f7be1e2a245753233f3e70343394b1115`.
- Re-read the latest prior GPS report `GPS_MAP_QUALITY_20261111.md` on the canonical recovery branch, blob `2a36f80f297f562320eec4b4244491205a3c0659`.
- Re-read the canonical recovery checkpoint and the candidate's synchronized copy before adding this checkpoint.
- The canonical map decision remains the free Leaflet/WebView stack: attributed OpenStreetMap streets, OpenTopoMap terrain and EOX Sentinel-2 cloudless 2016 satellite/hybrid. Native Google Maps is not required for that chosen stack.

## Material Activity Engine correction

### Defect found

The framework fallback selected a single provider. When fine permission was granted and GPS_PROVIDER was enabled, the service could keep a registered but silent GPS provider indefinitely even when coarse permission and an enabled NETWORK_PROVIDER were available. The existing permission-aware selection handled approximate-only permission, but did not provide a bounded fallback from an enabled-yet-silent GPS provider.

### Implemented behavior

Source commit `e1b05b6a34fcc0427cb6fac0f625581455b3b70b` adds a pure fallback policy and service integration:

- Fine permission + enabled GPS: start with GPS_PROVIDER.
- Coarse-only permission: select NETWORK_PROVIDER.
- Never request NETWORK_PROVIDER without coarse permission.
- If GPS registration itself fails, switch to NETWORK_PROVIDER immediately when coarse permission and the network provider are available.
- If GPS registration succeeds but no fresh accepted fix arrives, allow a 12-second bounded interval, then switch only when the accepted fix is absent or stale.
- Do not switch from NETWORK back to GPS within the same fallback cycle.
- Preserve one active framework provider at a time. This avoids alternating GPS/network source labels resetting the distance accumulator on every fix.

Follow-up source commit `68894a585e78df0a8d7b40cc68fa4f29acf10c9c` resets the old accepted/observed fix, accuracy, speed and distance accumulator when the framework provider changes. This prevents a first fix from the new provider from being rejected against a stale anchor from the previous provider or bridging distance across different provider streams.

Exact source blobs:
- `ActivityLocationFallbackPolicy.kt`: `b07bf335cfb5dbf6e921a72aac98cd2af7ad4cca`
- `ActivityTrackingService.kt`: `dc4576ef005f64aafda9cf52ac36f45697a2e480`
- `ActivityLocationFallbackPolicyTest.kt`: `3b9b38258a8f749879f972c2dfa75ed47ff8fcb6`

## Verification

- Exact policy blob was compiled with the local Kotlin compiler: PASS.
- Deterministic Kotlin policy harness: 18/18 assertions PASS (fine/coarse permission selection, no-permission fail-closed, GPS no-fix timeout, fresh/stale/future accepted-fix cases, immediate registration-failure fallback, network-provider availability, pause/replacement protection).
- Re-fetched source-contract audit: 10/10 PASS (exact blobs, service wiring, provider-switch guard, old-anchor reset, permission gating, and both regression tests).
- Git compare from prior candidate head `be95a73bce584043eaffe17df1c1a99a81251488` to source head `68894a585e78df0a8d7b40cc68fa4f29acf10c9c`: 2 commits ahead, 0 behind; exactly three files changed (ActivityTrackingService, ActivityLocationFallbackPolicy and its JUnit test).
- Exact-head GitHub Actions lookup for `68894a585e78df0a8d7b40cc68fa4f29acf10c9c`: zero workflow runs; combined status list empty. Android Gradle/JUnit, Lint, APK/AAB and CI PASS are NOT claimed for this delta.
- The repository's last prior Android CI PASS remains run [42976730277](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42976730277) on the earlier source SHA `fdbdd0588222ba366e56767e3b21de66c3f0d829`; it does not validate today's provider-switch changes.

## Physical-device QA

- Authorized Desktop Commander `localhost` is OFFLINE, last seen 44 hours before this check.
- No ADB device is attached.
- Current phone/session state is unknown. No install, launch, Stop, pause/resume, settings change or activity-data read was attempted.
- Physical approximate-permission fallback, silent-GPS-to-network transition, stationary drift, measured route, screen-off/background, notification and process-death P0 remain BLOCKED_NOT_RUN.

## Google Maps and owner prerequisite

- Historical preflight `41684077962` (2026-11-03) records Maps Android Backend and API Keys APIs enabled, but key-inventory permission denied, no package/SHA-restricted Android key visible, and no billing account linked.
- No permission retry, billing, payment method, key, secret or paid infrastructure change.
- Keep the canonical Leaflet/OSM/OpenTopoMap/EOX 2016 stack. No native Google basemap, traffic or transit overlay is present or claimed. Revisit only after the owner prerequisite and an explicit repository decision to change the map-stack choice.

## PR, release and scope boundary

- PR #284 remains Draft and unmerged. Existing shared-file ownership holds (#282/#216 on `app.js`; #93 on `MainActivity.kt` and source-contract tests) remain unresolved. No rebase or merge was performed.
- No Health/anti-cheat or exercise-catalog files, release version, workflows, signing, secrets or Play files changed.
- VersionCode 51020 remains unallocated. No APK was installed; no AAB was signed or uploaded; no Play PASS.
