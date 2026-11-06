# Top Hero Fit — GPS quality checkpoint

Date: 2026-11-06 (Africa/Cairo)
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
Canonical recovery branch: `agent/codex/fitness-recovery/20261023`
Canonical base SHA: `7dca1b9a83dc55752e96625e8ff18a58c9843cc7`
Candidate branch: `agent/codex/gps-path-inflation-guard-20261106-r1`
PR: [#267](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/267)
Source commit: `d3c644e802cfa229c2adfa71c89c9f6e623af97d`

## Material GPS defect and correction

The pending distance accumulator previously added every accepted segment while waiting for net displacement to clear the reported-accuracy deadband. Oscillating accepted fixes could inflate the path length substantially even though the final displacement remained small.

Reproduced through the existing `GpsFixGate` using 2 m reported accuracy and 5-second cycling updates:

- Accepted positions: `0, 4, 0, 4, 0, 4, 0, 8, 12 m`
- Net displacement: `12.0 m`
- Previous credited path: `36.0 m` (3x net displacement)
- New maximum credited path: `16.8 m` (1.4x net displacement)

The accumulator now bounds credited path to `min(pendingPathDistance, netDisplacement × 1.4)`. This preserves ordinary corner length where it fits within the envelope. It reduces oscillation-driven overcount but does not prove that a stationary phone cannot experience persistent plausible drift.

## Source and tests

- Source commit: `d3c644e802cfa229c2adfa71c89c9f6e623af97d`
- Base: `7dca1b9a83dc55752e96625e8ff18a58c9843cc7`
- Production helper blob: `7ab7213e5d96e12d019f0589f08cf2c5dbc71baf`
- JUnit test blob: `07450a99d07ede401459307274e888c96507e1f9`
- Source-contract blob: `d44cb4cb0e8b9ced8a14d7a8b5c194194f37b0cd`
- Exact production helper compilation and committed test-method execution via Kotlin/JVM 21 with a local assertion shim: **9/9 PASS**.
- Exact-head combined GitHub statuses: **0**; associated PR workflow runs: **0**.
- Android Gradle/JUnit runner, service compilation, lint, APK/AAB, and physical GPS QA: **NOT RUN**.

The candidate reapplies the prior GPS date-line normalization, provider identity, accepted-fix distance integration, pause guards, and accumulator lifecycle resets on the current canonical base. PR #267 changes only Activity Engine/GPS source and focused tests.

## Google Maps state

The latest recorded read-only preflight is run `41684077962` (2026-11-03): Maps Android Backend and API Keys APIs are enabled; key inventory permission is denied; no key is visible to the builder; no billing account is linked. No billing, payment method, key, or paid infrastructure was changed.

Native Google Maps SDK rendering and native traffic/transit layers remain owner-prerequisite blocked. The current free map stack remains OSM street, OpenTopoMap terrain, and EOX 2016 satellite/hybrid with attribution; the Google directions handoff is not an in-app Google basemap. No Google Maps integration PASS is claimed.

## Physical-device and release gates

- Authorized Desktop Commander `localhost`: OFFLINE, last seen 92 hours ago. No ADB, install, launch, Stop, or session action was attempted. Current phone/session state is unknown and must be preserved.
- Physical GPS, stationary drift, route accuracy, background/screen-off, process-death, and notification-control P0: **BLOCKED_NOT_RUN**.
- PR #264 session integration is merged source-only and passed exact Android CI run `41681713383` on source SHA `5ce141340282319723a218deafbd1f24eee2b04a`; physical P0 remains unrun.
- Stale PR #265 was closed as superseded by PR #267. PR #267 remains Draft; keep it unmerged pending exact-head Android CI and safe physical P0.
- VersionCode 51020 remains unallocated. No release/workflow/signing/Play files changed; no artifact signed or uploaded; no Play state changed.

## Next safe gate

Obtain exact-head Android CI through an authorized existing route. Run physical P0 only after the authorized device is online and the current session is confirmed idle. Provision native Google Maps only after the owner prerequisite is met and the key can be restricted to the exact Android package and signing SHA plus required APIs.
