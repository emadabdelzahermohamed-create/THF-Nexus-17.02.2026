# TopHeroFit — GPS and activity-map checkpoint
Date: 2026-11-08 (Africa/Cairo)
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
Canonical branch: `agent/codex/fitness-recovery/20261023`
Canonical app-source SHA after tested handoffs: `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`. Subsequent canonical commits are evidence-only.

## Current GPS behavior and truthful status

- GPS presentation is based on `GpsFixPresentationPolicy` states: `permission`, `off`, `acquiring`, `stale`, `filtered`, and `ready`.
- Fresh observations rejected by movement/quality filters are presented as observed-but-not-accepted (`filtered`), not falsely described as weak horizontal accuracy.
- PR #281 corrects the remaining permission-state fall-through: `permission` now displays the existing `activityPermissionNeeded` copy in the activity status pill. It adds no permission request and changes no provider, accepted fix, distance, speed, route, reward, or accuracy calculation.
- The current distance accumulator uses an uncertainty deadband, a 3 m minimum displacement margin, a 120 s maximum anchor gap, a 50 m maximum horizontal accuracy, a 1.4x path/net bound, and requires a second accepted fix to confirm a threshold-crossing excursion. A one-fix spike-and-return is discarded. This is conservative filtering, not proof against sustained stationary drift or spoofing.
- The current fused-location request rejects cached pre-Start fixes (`setMaxUpdateAgeMillis(0L)`) and waits for accurate location. Physical accuracy remains unverified.

## Map stack

- Canonical app already contains vendored Leaflet, attributed OpenStreetMap street tiles, OpenTopoMap terrain tiles, and EOX satellite/hybrid tiles, with a local SVG route fallback and a Google Maps directions handoff.
- WebView network policy limits external tile access to the approved HTTPS tile hosts.
- Native Google Maps SDK, native basemap, traffic, and transit are not enabled in the current canonical build.
- Latest owner preflight: run `41684077962` (2026-11-03), workflow `THF Google Maps Key Preflight`, success. Maps Android Backend and API Keys APIs were enabled, but the release builder lacked key-inventory permission; no package/SHA-restricted Android key was visible and no billing account was linked. Owner key/billing prerequisites remain blocked. No billing, payment method, key, secret, or paid infrastructure was created.

## Exact-head Android evidence

### PR #281 — GPS permission presentation
- Merged PR: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/281
- Exact tested source HEAD: `4507e757bec279ba0e5b596ee8822ef7aaff7f45`
- Canonical squash merge: `2b5d44668d33b9e9faac5d8ace9753e5f6032ad3`
- Exact-head Android candidate CI: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42503748041 — success.
- Product tests: 60/60; source-contract tests: 34/34; backend tests: 29/29; Android unit tests: 218/218.
- Lint: 0 errors, 16 warnings, 1 hint.
- Candidate archive artifact 13626169449 SHA-256: `a962157d2a3e32146c66c1a75a8fb869d698cc4e2dab24fcc4ee050a9da3d41a`.
- QA APK SHA-256: `cd2e19b53e0192f9c418bc3e4bab33d32c7c29034bb115488e71fa25f7630208`.
- Validation AAB SHA-256: `44a5d7c8f28c452686ee14dff3059102b097001e6a645b065993acd528b32828`.
- The AAB is unsigned validation output; candidate identity is QA package `com.topherofit.thf.pulse.qa`, versionCode 51019. No release signing or Play upload.

### PR #280 — partial Health Connect consent
- Merged PR: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/280
- Exact tested source HEAD: `63e80126d40c0a6ad253081a032807e38c4213aa`
- Canonical squash merge: `06ca1b7891e72812f0a4514d90a7b97081a54b85`
- Exact-head Android candidate CI: https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42487820726 — success.
- Changes only HealthConnectRepository plus a pure permission policy and unit tests. Each core metric is read only when its own permission is granted. Missing permission is `null`; an allowed read with no records is numeric zero. No permission was added or expanded.
- Candidate archive artifact 13620023894 SHA-256: `187a2fc435cb75546d56512c1a9149a5497adce13d91547e128352077690e1a3`.
- QA APK SHA-256: `96d71d6585c33fdb7b00190b7d924c5c36a6a5f6d10f7cffdd5b37ad3b63a4f9`.
- Validation AAB SHA-256: `e0d6befbc8890c2ff8ae9dc88acb7115c5d6fc442bb4b075e5817c39bb27a30f`; unsigned validation only.

## Physical P0 and release boundary

- Authorized Desktop Commander device `localhost` was offline at the 2026-11-08 device check (last seen about 6 hours earlier). The current phone/session state is unknown. Last phone observation remains 2026-11-01T21:24:32Z, with a foreground tracking service and an active/ambiguous session.
- No ADB command, install, launch, Stop, session action, or activity-data read was attempted. Preserve the unknown session.
- Physical GPS accuracy, stationary drift, background/screen-off continuity, process-death recovery, pause/resume/Stop, notification metrics, and Health grant/revoke/no-data/provenance P0 remain `BLOCKED_NOT_RUN`.
- VersionCode 51020 remains unallocated. Next code must be greater than 51019 and only allocated after owner API/key prerequisites, exact-head Android CI, and physical P0 pass. Production remains unverified pending policy/privacy and physical gates.
