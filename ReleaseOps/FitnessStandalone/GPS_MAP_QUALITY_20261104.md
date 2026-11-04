# Top Hero Fit — GPS quality checkpoint

Date: 2026-11-04
Canonical base: `agent/codex/fitness-recovery/20261023` at `f927d9fb3a80b581fd41966b91007c960577a6af`
Candidate branch: `agent/codex/activity-gps-distance-deadband-20261104-r1`
App/test source HEAD (before evidence-only documentation commits): `6aa40c03dbe214bc265c8124f99d9b442f244882`

## Source delta

- Added `GpsDistanceAccumulator` to separate measured distance from display-route points. It accumulates accepted path length behind a stable movement anchor and credits it only after net displacement exceeds both endpoint accuracy radii plus 3 m. This suppresses small stationary jitter while preserving accepted path length through turns.
- The deadband retains the worst reported accuracy across the pending window; provider changes, mock/invalid fixes, non-monotonic time, and gaps over 120 seconds reset or re-anchor rather than bridge evidence.
- Wired the accumulator to accepted raw fixes only. ARMED candidates seed but do not add distance; GPS activation seeds the final activation fix; step activation, start, pause/resume, and persisted-process restore reset the accumulator so paused/downtime movement is not added.
- Current speed is derived from the credited path segment and elapsed time, not the unfiltered Android speed field.
- Normalized longitude delta in `ActivityMetrics.distanceMetres` so legitimate routes crossing ±180° use the short arc.

This is a source-level measurement-filtering improvement, not a claim of physical GPS accuracy. A prolonged stationary drift can still exceed the deadband; GPS-only distance on small loops may be deferred until net displacement clears the threshold. Physical testing is required to assess those tradeoffs.

Evidence-only documentation commits follow the app/test source HEAD; no additional app source changed.
Draft PR #265 was opened at evidence HEAD `fd22c055af56a99acd2f7447b92a0b5faabceba8`; GitHub reports mergeable/clean, but the exact-head check-runs and statuses collections are empty. Subsequent commits are documentation-only.

## Exact-source checks

- Kotlin/JVM harness: **19/19 regression cases passed** using the exact committed production blobs for `GpsDistanceAccumulator.kt` (blob `697d73545683ecf934c382960101cac1f969792e`), `GpsFixGate.kt` (blob `28261ddcea4f2b5672573a2af854fbf75a1ecc35`), and `ActivityMetrics.kt` (blob `9f91c8722c323f4f97a088165890661f3791f59f`). The committed `GpsDistanceAccumulatorTest.kt` blob is `60c1c9fbfa3ae99bacda5bb6c4b644cb236c5f10`; existing `GpsFixGateTest.kt` blob is `fddb715072978aded2697b157fd1a575d0e9ff10`.
- Direct source-contract harness: **15/15 assertions passed** against the candidate service/helper/gate/metrics/source-test blobs. The added Python source-contract test snippet passed syntax compilation.
- These are local source/JVM checks. No Android Gradle/JUnit, lint, APK/AAB, or physical-device PASS is claimed.

## Blockers and release boundary

- The existing unsigned candidate workflow is branch-allowlisted and does not include this candidate branch. No authorized exact-head workflow-dispatch path was available; workflow files were not edited. Exact-head Android CI remains NOT RUN.
- Desktop Commander `localhost` is offline; current check reports last seen **43 hours ago**. No ADB, install, launch, Stop, or session action was attempted. Phone/session state is unknown; preserve it.
- Latest recorded Maps preflight remains 2026-11-03: Maps Android Backend and API Keys APIs enabled; key inventory permission denied; no Maps key visible and no billing account linked. No owner prerequisite was satisfied in this run; no billing, key, or paid infrastructure changed. Native Google Maps SDK and traffic/transit overlays remain blocked.
- No release version, workflow, signing, Play, Health/anti-cheat, or exercise-catalog files were changed. No versionCode was allocated and no artifact was signed or uploaded.

## Next safe gate

Obtain exact-head Android CI through an authorized existing route, then run physical P0 only when the authorized device is online and the existing session is confirmed safely idle. Continue the free attributed map stack until the owner Maps API/key/billing prerequisites are satisfied.
