# Health permission release gate — 2026-10-29

## Scope and decision

This is a Lane B policy/test handoff only. It does not change the Android manifest, Health services, activity tracking, release version/workflows, signing, Play state, or any active Health implementation lease.

**Decision: keep PRs #93 and #98 on HOLD.** A green build alone is not evidence that the expanded Health data surface is declared, disclosed, or physically verified.

## Exact source evidence

- Canonical branch: `agent/codex/fitness-recovery/20261023`
- Canonical head observed before this handoff: `adce7e5f1a54525d4603a4f26098e91d0d457a56`
- Canonical manifest blob: `0969cdb2f18775f23e0870bf754612a04376895f`
- PR #93 head: `1cc08cef7dae7f432275fd23960f4390a49db14c`
- PR #98 held head: `2483367811abcf68af740f24b2f55e0f04f211b3`
- The manifest blob on both #93 and #98 heads was `a3b24f09e6b0c8a67b0fee3e7578317cfe979092`; it declares the same 14 additional Health read permissions listed below.
- The latest recovery record identifies Play Internal versionCode **51019** as the current verified release. The 51014 value in the older Free continuity note is historical and must not be used as the current release baseline.
- Physical acceptance remains blocked/not run: the last known phone installation is 51018 and the authorized device preflight reported no attached device. No Play Console declaration evidence or physical Health Connect result is attached to this handoff.

## Canonical permission allowlist

The current canonical manifest declares exactly these five Health permissions:

- `android.permission.health.READ_STEPS`
- `android.permission.health.READ_EXERCISE`
- `android.permission.health.WRITE_EXERCISE`
- `android.permission.health.READ_DISTANCE`
- `android.permission.health.READ_ACTIVE_CALORIES_BURNED`

## Held candidate expansion

PRs #93 and #98 add all 14 of these read permissions in their manifest:

- `READ_TOTAL_CALORIES_BURNED`
- `READ_SLEEP`
- `READ_HEART_RATE`
- `READ_RESTING_HEART_RATE`
- `READ_WEIGHT`
- `READ_HEIGHT`
- `READ_BODY_FAT`
- `READ_BASAL_METABOLIC_RATE`
- `READ_OXYGEN_SATURATION`
- `READ_VO2_MAX`
- `READ_SPEED`
- `READ_NUTRITION`
- `READ_BLOOD_PRESSURE`
- `READ_BLOOD_GLUCOSE`

An “optional” source comment does not reduce the declared permission surface. The new regression gate requires the canonical manifest to remain on its reviewed allowlist until a specific permission has passed its own integration gate.

## P0 decisions

1. **Swimming:** use the existing exercise-session permission path. Do not add a swimming-specific permission or infer verified swimming from phone GPS/sensors. An exercise session alone is not enough to grant `VERIFIED`; retain record-level origin, source package, recording method, and compatible wearable/device evidence. Unknown, manual, or unsupported source evidence must fail closed.
2. **Optional heart rate:** `READ_HEART_RATE` is the only newly requested P0 data type with a direct user-visible rationale, but it remains deferred in the canonical manifest until its dedicated implementation is connected, the exact data use is reconciled with Play/privacy, and physical grant/no-data/revoke/error/source-label tests pass. Do not substitute resting heart rate for workout samples.
3. **Walking/running/cycling:** reconcile phone sensor/GPS and Health/watch records before aggregation. Preserve origin and stable record identity; do not broaden permissions with `READ_SPEED` merely to make deduplication easier.
4. **Other 12 expansion types:** no new P0 requirement is recorded here. Keep them deferred until each has a concrete user-visible feature, minimum-necessary rationale, and its own evidence.

## Required evidence before any Health-expanded release

| Gate | Required artifact | Current status |
|---|---|---|
| Play Health declaration | Exact Play Console declaration/data-type evidence tied to the candidate source SHA, versionCode, and AAB | NOT EVIDENCED |
| Privacy disclosure | Exact policy/disclosure text matching each declared type, purpose, retention, and sharing | NOT EVIDENCED |
| Permission UX | Visible opt-in/rationale and clear unavailable, no-data, partial-grant, revoked, and error states | Source exists in held work; exact candidate not accepted |
| Record provenance | Per-record origin, source package, recording method/device, stable identity, and trust tier | Incomplete across active handoffs |
| Swimming eligibility | Real compatible wearable/Health evidence; manual/unknown/GPS-only rejected | Physical verification NOT RUN |
| Heart-rate UX | Optional, source-labelled samples; no stale values after revoke; no data is not fabricated as zero | Physical verification NOT RUN |
| Dedup/anomaly | Cross-source dedup without collapsing two same-source sessions; spoof/time/speed plausibility checks | Exact integrated candidate NOT VERIFIED |
| Physical Health Connect | Grant/partial grant/no-data/revoke/error with real source data on authorized device | BLOCKED_NOT_RUN |

No Play declaration acceptance or physical Health/Watch PASS is claimed by this document.

## Regression gate

`fitness-v2/product/tests/test_health_permission_scope_gate.py` checks the exact canonical Health allowlist, confirms existing exercise-session permission remains present, and fails if the deferred heart-rate or broad wellness/clinical expansion is silently added. The gate must be deliberately updated only alongside the exact permission's declaration/privacy and physical evidence; do not weaken it merely to make #93/#98 green.

## Integrator handoff

- Keep #93 and #98 HOLD.
- Keep the active service, provenance, and heart-rate implementation files with their current PR owners; this handoff adds only a separate product test and this new policy document.
- Any future candidate must allocate a unique versionCode greater than the then-current verified baseline (currently 51019), only after meaningful exact-SHA tests and policy/privacy/physical gates. Version allocation, workflows, signing, and Play remain Integrator-owned.
