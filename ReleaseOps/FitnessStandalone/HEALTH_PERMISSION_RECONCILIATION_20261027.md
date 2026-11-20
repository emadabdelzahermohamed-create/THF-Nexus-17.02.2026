# Health permission minimization checkpoint — 2026-10-27

## Exact baseline inspected
- Development branch: `agent/codex/fitness-recovery/20261023`
- Branch head at inspection: `85fbf46153818aeeb531c37c369a490f19aff093`
- Manifest blob SHA: `70585128750cdecced47f95fd8de011db2d8024a`
- Existing reconciliation blob SHA: `dadd70744b70577e72d05024425cc7549335b769`
- Current manifest contains exactly the five canonical Health Connect data permissions: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE, READ_ACTIVE_CALORIES_BURNED.

## Ownership / blocker
PR #93 remains an explicit active ownership claim over `AndroidManifest.xml`, `HealthServiceModels.kt`, `HealthConnectServiceSource.kt` / `HealthServicesReader.kt`, `HealthServicesActivity.kt`, Health service tests, native rationale resources and the narrow `MainActivity.kt` Health-settings bridge. This run did not modify any of those files.

PR #98 remains HOLD. Its broad 14-scope expansion is not a release candidate merely because an earlier Android build succeeded. The checked-in Play Health declaration draft is marked not submitted and does not establish Console acceptance or matching privacy disclosure.

## Narrow P0 decision
- Swimming sessions can use the already-declared READ_EXERCISE path, but a Health record alone is not enough to award VERIFIED swimming. Preserve record-level origin/source/device provenance and fail closed for phone-only, imported, manual or unknown-source swimming.
- Optional workout heart-rate samples justify at most the single additional READ_HEART_RATE scope, and only after the feature is visible, user-enabled and individually consented. READ_RESTING_HEART_RATE is not a substitute for workout samples.
- Keep the other 13 expansion scopes deferred until each has a concrete visible feature plus exact Play declaration/privacy and physical grant/no-data/revoke/error evidence.

## Material delta
Added `fitness-v2/tests/test_health_permission_minimization.py`. It guards the manifest against the broad PR #98 permission set, allows only the five canonical scopes plus the future narrow READ_HEART_RATE exception, and asserts that resting heart rate is not silently substituted for workout samples. The test is a policy/source guard; it does not claim that heart-rate ingestion has been implemented or that Play/physical Health gates passed.

## Remaining gates
1. Resolve the PR #93 ownership handoff before changing its claimed native files; do not cherry-pick its broad permission manifest.
2. Implement the narrow optional HR path on a disjoint owner-approved branch, with source-labelled records and explicit permission-denied/no-data/revoked/error states.
3. Obtain exact Google Play Health declaration and privacy reconciliation evidence.
4. Physically verify real watch/Health-origin samples, partial grants, revocation and absence of stale values on the exact candidate.

No activity-tracking, release version/workflow, signing or Play files were changed. No device interaction or Health/Play PASS is claimed.
