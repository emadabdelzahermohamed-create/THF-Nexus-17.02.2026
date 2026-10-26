# Health Connect permission reconciliation — 2026-10-26

## Scope and truth boundary
Policy/declaration evidence only for the held Health expansion in PR #98. This does not claim Google Play declaration acceptance, physical Health Connect PASS, merge/release approval, or Production readiness. Canonical release/version/workflows and activity tracking are untouched.

Verified release baseline from canonical recovery: Google Play Internal versionCode 51014; phone still Play-installed 51012. Any future Health-expanded candidate must use a unique versionCode >51014 and remains integrator-owned.

## Exact manifest delta versus canonical
Canonical Health permissions:
- READ_STEPS
- READ_EXERCISE
- WRITE_EXERCISE
- READ_DISTANCE
- READ_ACTIVE_CALORIES_BURNED

PR #98 adds these 14 read permissions:
- READ_TOTAL_CALORIES_BURNED
- READ_SLEEP
- READ_HEART_RATE
- READ_RESTING_HEART_RATE
- READ_WEIGHT
- READ_HEIGHT
- READ_BODY_FAT
- READ_BASAL_METABOLIC_RATE
- READ_OXYGEN_SATURATION
- READ_VO2_MAX
- READ_SPEED
- READ_NUTRITION
- READ_BLOOD_PRESSURE
- READ_BLOOD_GLUCOSE

It also adds HealthServicesActivity. The manifest comment describes the added services as optional and individually requested after rationale, but manifest declaration itself still expands the app's declared Health data surface.

## P0 wearable/sport permission decision
The current P0 does **not** justify the 14-scope expansion.

- Swimming import/eligibility can be represented by `ExerciseSessionRecord` using `EXERCISE_TYPE_SWIMMING_POOL` or `EXERCISE_TYPE_SWIMMING_OPEN_WATER`; canonical already declares `READ_EXERCISE`. Do not add a swimming-specific permission and do not infer verified swimming from phone GPS/sensors.
- Optional watch/Health heart-rate display is the only newly stated P0 feature that directly requires one of PR #98's new data types: `READ_HEART_RATE`. Request/read it only after the user enables the visible heart-rate feature and preserve explicit unavailable/no-data/revoked states.
- `READ_RESTING_HEART_RATE` is not required for workout heart-rate samples and remains deferred unless a separate visible feature is approved and reconciled.
- `READ_SPEED` is not required merely to deduplicate imported walking/running/cycling sessions; canonical exercise/distance plus existing phone-owned tracking evidence must be reconciled first. Do not broaden permissions just to make dedup easier.
- The remaining 11 broad scopes (total calories, sleep, weight, height, body fat, BMR, oxygen saturation, VO2 max, nutrition, blood pressure, blood glucose) have no newly stated P0 requirement and remain deferred.

For swimming competition evidence, a Health exercise record is necessary but not sufficient for `verified`: preserve record-level origin/source/device metadata and classify fail-closed when provenance cannot establish a compatible wearable/Health source. Imported/manual/unknown-source swimming must not receive verified swimming progress. Open-water route presence alone must never upgrade trust; pool sessions may legitimately have no GPS route.

For walking/running/cycling, deduplicate phone + GPS + Health/watch evidence by overlapping session identity/time window and preserved origin before aggregation. Never count both an imported Health session and its corresponding phone-measured session as separate verified progress merely because they arrived through different sources.

## Release decision
HOLD PR #98 unchanged. Do not merge/release the broad permission set until each added data type has all of the following evidence:
1. A concrete user-visible Fitness feature that actually needs the type.
2. Matching Google Play Health-app/data-type declaration evidence for the exact release candidate.
3. Matching privacy disclosure/data-handling evidence.
4. Physical-device tests for grant, partial grant, no-data, revoke/error and record-level origin/provenance where applicable.
5. No stale sensitive values after revoke/background and no fabricated zero for absent data.

## Permission-minimization recommendation
Prefer a narrow follow-up rather than shipping all 14 additions together. For the current P0, the candidate permission delta should be **READ_HEART_RATE only**, while swimming continues through existing READ_EXERCISE. Keep any later added permission only when its corresponding optional service is user-visible, tested, declaration-reconciled and privacy-reconciled. Defer clinical/sensitive scopes (blood glucose, blood pressure, oxygen saturation) and nutrition/sleep/body-composition scopes unless a concrete Fitness feature and declaration need is demonstrated. This is a release-scope recommendation, not a claim that any particular type is prohibited.

## Direct policy/API evidence checked 2026-10-26
- Android Health Connect workout guidance identifies `ExerciseSessionRecord` as the central workout record and supports associated `HeartRateRecord` data.
- Android Health Connect data types include pool/open-water swimming exercise types and define `READ_HEART_RATE` separately from `READ_EXERCISE`.
- Google Play Health policy requires minimum-necessary Health Connect access, Health apps declaration, privacy disclosure, and removal of unused permissions.

These references establish the permission-minimization direction only; they do not prove the app's Play declaration has been accepted.

## Integrator handoff
- PR #98 exact held head observed: 2483367811abcf68af740f24b2f55e0f04f211b3.
- Build proof already recorded by PR #98: run 40284169005 at source 9b9a7310501712ae152c96ec5afc0f85defb6bde.
- Do not reuse its historical 51013 version.
- Next Health worker action: create an isolated implementation/test PR from current canonical whose only newly declared Health data permission is READ_HEART_RATE; preserve optional-service partial-grant/no-data/revoke/provenance behavior and wearable-only verified-swimming eligibility. Do not edit release/version/workflows/Play or activity-tracking-owned files.
- Integrator may consider a future Health-expanded release only after policy/privacy + physical gates are direct evidence, with versionCode >51014.
