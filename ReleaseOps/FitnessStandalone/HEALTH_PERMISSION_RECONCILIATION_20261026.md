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

## Release decision
HOLD PR #98 unchanged. Do not merge/release the broad permission set until each added data type has all of the following evidence:
1. A concrete user-visible Fitness feature that actually needs the type.
2. Matching Google Play Health-app/data-type declaration evidence for the exact release candidate.
3. Matching privacy disclosure/data-handling evidence.
4. Physical-device tests for grant, partial grant, no-data, revoke/error and record-level origin/provenance where applicable.
5. No stale sensitive values after revoke/background and no fabricated zero for absent data.

## Permission-minimization recommendation
Prefer a narrow follow-up rather than shipping all 14 additions together. Keep an added permission only when its corresponding optional service is user-visible, tested, declaration-reconciled and privacy-reconciled. Defer clinical/sensitive scopes (blood glucose, blood pressure, oxygen saturation) and nutrition/sleep/body-composition scopes unless a concrete Fitness feature and declaration need is demonstrated. This is a release-scope recommendation, not a claim that any particular type is prohibited.

## Integrator handoff
- PR #98 exact held head observed: 2483367811abcf68af740f24b2f55e0f04f211b3.
- Build proof already recorded by PR #98: run 40284169005 at source 9b9a7310501712ae152c96ec5afc0f85defb6bde.
- Do not reuse its historical 51013 version.
- Next Health worker action: create an isolated permission-minimized implementation/test PR, preserving optional-service partial-grant/no-data/revoke/provenance behavior; do not edit release/version/workflows/Play.
- Integrator may consider a future Health-expanded release only after policy/privacy + physical gates are direct evidence, with versionCode >51014.
