# Top Hero Fit — GPS quality checkpoint

Date: 2026-11-05 (Africa/Cairo)
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
Canonical recovery branch: `agent/codex/fitness-recovery/20261023`
Candidate branch: `agent/codex/activity-gps-distance-deadband-20261104-r1`
PR: [#265](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/265)
App/test source commit: `a09cb2098756440ecc9a799288823b4dda59de27`
Production blob: `552bb15816c2df6e78f11da14cb5aaa6e905d167`
Test blob: `63ba9f9d497e6acc383575c6cea4f95354d3a931`

## Baseline reviewed

- Read the requested `GPS_MAP_QUALITY_20261101.md` (blob `0e50b45f7be1e2a245753233f3e70343394b1115`) and the canonical `RECOVERY_20261023.md` (canonical branch blob `b2a471b149108ae173f49361f2c76b86a691f238`).
- Also reviewed the latest GPS candidate report `GPS_MAP_QUALITY_20261104.md` (blob `eaadb686ea06fe81b68480b7a6a6d082a1435208`) and the candidate branch's recovery checkpoint (blob `e11b93e8bf9a67508637b2a2b33857f118585a83`).
- The current source change is a focused follow-up to the GPS distance deadband work in PR #265. It does not modify the ActivityTrackingService wiring or the previously committed session lifecycle code.

## Material source delta — transient GPS excursion rejection

The prior accumulator could credit a single accepted fix as soon as net displacement cleared the accuracy deadband. A plausible cycling-speed GPS spike followed by a return could therefore be counted as distance, and its pending path could be included in later movement.

The accumulator now requires a threshold-crossing displacement to persist through the next accepted raw fix before crediting distance. If that candidate returns inside the deadband, it discards the unconfirmed excursion path and re-anchors at the returning fix. This reduces single-fix spike-and-return overcounting; it is not a spoof detector and cannot reject persistent stationary drift that remains plausible long enough.

The committed regression covers a 20 m / 2 s cycling-plausible excursion, return to the anchor, then later confirmed movement. Only the later 20 m path is credited. The 20 m / 2 s segment is 36 km/h, below the existing 85 km/h cycling plausibility ceiling; the regression exercises the accumulator after the existing raw-fix gate.

## Verification

- Python reference-model regression scenarios: **8/8 PASS** (small movement confirmation, turn-path retention, stationary jitter, poor intermediate accuracy, provider change, long-gap re-anchor, one-fix excursion/return followed by later movement, reset/mock isolation, and date-line distance).
- Exact fetched GitHub source/test blob contract checks: **5/5 PASS** (candidate state, reset behavior, excursion discard path, regression presence, and no-spike-credit assertions).
- The updated production and JUnit test files were re-fetched from the candidate branch; blob hashes match the values above.
- These are a Python reference-model and source-contract checks. Kotlin compilation, Android Gradle/JUnit, lint, APK/AAB, exact-head Android CI, and physical-device GPS QA were **not run**. No Android, GPS, phone, or Play PASS is claimed.

## Current blockers and release boundary

- The authorized Desktop Commander device `localhost` is **OFFLINE**, last seen **67 hours ago** on this check. No ADB, install, launch, Stop, or session action was attempted; the current phone/session state remains unknown and must be preserved.
- Latest recorded Maps preflight remains 2026-11-03: Maps Android Backend and API Keys APIs enabled, key-inventory permission denied, no key visible to the builder, and no billing account linked. The owner prerequisite was not met; no Cloud permission, billing, key, or paid infrastructure was changed. Native Google Maps SDK and traffic/transit layers remain blocked.
- The candidate branch has **zero combined status checks and zero associated PR workflow runs** at exact app/test commit `a09cb2098756440ecc9a799288823b4dda59de27`. The existing candidate workflow does not allowlist this branch, and no authorized dispatch route was available. No workflow was edited.
- No release version, signing, Play, Health/anti-cheat, or exercise-catalog files changed. No versionCode was allocated and no artifact was signed or uploaded. Keep PR #265 draft and 51020 unallocated.

## Next safe gate

Obtain an authorized exact-head Android CI route for the candidate; then run physical P0 only when the authorized device is online and the existing session is confirmed safely idle. Keep native Maps SDK blocked until the owner prerequisite is met and a package/SHA-restricted key can be provisioned.
