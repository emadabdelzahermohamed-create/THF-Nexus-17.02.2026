# Health Connect services — native, optional, read-only wellness hub

## Intent and scope
Implement the user's 25 October request for actual services behind Health Connect permissions, not a visual copy of Android's settings. Existing four-type activity sync and exercise-only writes stay unchanged. Each additional service is optional and has an explicit purpose before Android's own consent dialog. Build on Kotlin / Health Connect 1.1.0, minSdk 26, targetSdk 36. No paid service or new account.

## Approach (implementation choice under autonomous execution)
Use a native HealthServicesActivity reached from Health → Manage permissions. It contains separate permission actions and real on-demand reads per service, plus a direct link to Android Health Connect settings. A combined mandatory permission bundle would break partial consent. Editing the existing web UI would overlap open PRs #88/#89/#91, so defer web copy reconciliation to integration; the native hub explicitly distinguishes its optional services from the basic activity consent flow.

## Functional contract
- Activity totals (today): steps, distance, active calories, total calories; use Health Connect aggregates, never sum overlapping sources or add active to total calories.
- Exercise sessions and sleep duration (7 days); sleep aggregate respects provider semantics.
- Latest available weight, height, body fat, BMR, resting heart rate, oxygen saturation, VO2 max, blood pressure, blood glucose (last 28 days, no history permission). Average heart rate and maximum recorded speed are today's platform aggregates, explicitly not live measurements.
- Nutrition: energy and macros from the latest record, not a sum of potentially duplicated cross-app meals, guessed food database or diet prescription.
- Every metric has independent permission / empty / ready / error status. A denied or revoked category must not block another category or expose its previous cached values. Permission rechecked before and after each operation; foreground-only, memory-only, cleared on background.
- Show time window or observation time, units, source packages, and recording method when reading an individual record. Do not call a measurement sensor-verified or reward-eligible. No health data is logged, sent to a server, used for ads, or put in Git.
- No data fabrication, auto-grants, medical diagnosis, health-based rewards, extra writes, background reads, history permission, active-session interruption, device operations, release version/workflow edits, or Play mutation.

## Files and ownership
Create HealthServiceModels.kt, HealthConnectServiceSource.kt, HealthServicesActivity.kt and focused tests. Modify AndroidManifest.xml, MainActivity.kt's openHealthSettings bridge, native health rationale resources and the previous five-scope source contract. These are disjoint from open experience PRs. Canonical branch is integrator-only.

## Release gates
Tests + Android compile/lint must pass before this is ready for review. Integrator must reconcile basic web rationale, public privacy policy, Health apps / Data Safety declarations for new read scopes before a signed release. No phone/Internal/Production PASS from unit tests or permission declarations. QA must prove Android consent, partial allow/deny/revoke, real Samsung origin/time/value, no-data state, Arabic/English, and active-workout preservation on the exact new candidate.
