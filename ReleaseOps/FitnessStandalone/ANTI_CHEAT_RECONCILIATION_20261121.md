# TopHeroFit — GPS anti-cheat policy reconciliation (2026-11-21)

Canonical application HEAD: `b097d6ef0025d615c261ee42e8d2246533224e70`.  
Native GPS integration: PR #303, exact tested source `26e90573ddda077ca2665ebdccd5600cc9316dd7`, run 44929317705.

**Decision: do not wire `ActivityEvidenceAnomalyPolicy.assessSegment()` as a second distance-credit gate in this checkpoint.** It is tested but its per-segment semantics overlap with the already-live `GpsFixGate` and `GpsDistanceAccumulator`; applying all three as independent gates would risk double filtering and undercounting real movement.

## 1. Current live service path

`ActivityTrackingService.handleLocationChanged()` currently:
1. Converts the raw Android `Location` to `GpsFix`, preserving provider label, monotonic elapsed time, accuracy and mock flag.
2. Records observed signal state separately from accepted metric evidence.
3. Applies `GpsFixGate.accepts()` before the accepted anchor advances.
4. Sends ACTIVE raw fixes to `GpsDistanceAccumulator.offer()`; ARMED fixes only seed the accumulator.
5. Adds distance only when the accumulator returns a multi-fix confirmed credit.
6. Stores raw accepted route points; no display-smoothed coordinates enter metrics.

## 2. Existing gate thresholds and semantics

| Policy | Existing behavior |
|---|---|
| `GpsFixGate` | Mock/invalid/stale/future/non-monotonic fixes rejected; max accuracy 25 m walk/run, 40 m cycle; speed ceiling 13/32/85 km/h; endpoint deadband based on the worse accuracy radius. |
| `GpsDistanceAccumulator` | Same-source requirement; max 120 s anchor gap; accuracy <=50 m; movement must exceed both endpoint uncertainty radii plus 3 m; at least 3 accepted fixes over 6 s; credited path bounded to 1.4x net displacement. |
| `ActivityEvidenceAnomalyPolicy` | Pairwise mock/source/coordinate/time/gap/accuracy/speed checks; max accuracy 50 m; per-pair uncertainty subtracts both radii; minimum per-pair creditable displacement 3 m; speed ceilings 4.5/12.5/45 m/s for walk/run/cycle. |

The anomaly policy's per-pair `MIN_CREDITABLE_DISTANCE_METERS=3` is not equivalent to the accumulator's multi-fix 3 m margin. A normal 1-second walking update can be individually below 3 m while contributing to a valid confirmed multi-fix movement window. Using `creditableDistanceMeters` as the distance increment would therefore discard valid short segments and break the existing path accumulator.

The existing `GpsFixGate` speed ceilings (13/32/85 km/h) also differ from the anomaly policy's per-sport ceilings. Adding both without calibrated device/outdoor traces could produce false exclusions, especially for cycling and downhill/fast running.

## 3. Safe integration direction

- Keep `GpsFixGate` as the accepted-fix admission boundary and `GpsDistanceAccumulator` as the sole distance-credit source until a calibrated unified policy is designed.
- Do not sum `ActivityGpsSegmentAssessment.creditableDistanceMeters` into activity totals.
- If the anomaly policy is retained, refactor toward one shared decision object consumed by the service and tests, rather than stacking duplicate filters. Separate hard-invalid evidence (mock, invalid coordinates, non-monotonic time, source discontinuity, impossible speed) from low-displacement observations that must remain available to the multi-fix accumulator.
- Add deterministic tests proving short valid fixes still accumulate, provider-switch callbacks cannot bridge distance, stale/long-gap fixes re-anchor, and all sports preserve plausible movement.
- If evidence diagnostics are added, store only bounded decision counts/status; never log raw coordinates, route polylines, tokens or user identifiers.
- Physical stationary drift and measured outdoor walk/run/cycle traces are required to calibrate thresholds before reward decisions.

## 4. Competition boundary

PR #269 is merged, but the current verified server metric is `strength_volume_kg_reps`. No GPS activity leaderboard or GPS reward path is enabled. `rewardEligible=false` remains the correct state for GPS activity.

Before any GPS competition/reward eligibility, require a separately designed server-verifiable evidence contract: authenticated source identity, anti-replay/session binding, bounded monotonic timestamps, provider-switch handling, server-side plausibility validation, rate limits and physical P0 evidence. This policy alone is not location attestation and must never be described as cheat-proof.

## 5. Decision

No anti-cheat code was changed in this checkpoint. This avoids adding a second stricter gate that could silently corrupt distance metrics. The next implementation should consolidate the decision path and add exact-head Android tests before merge; GPS rewards remain disabled.
