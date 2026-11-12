# Health permission release gate — 2026-11-12

## Canonical least-privilege baseline

- Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
- Canonical branch: `agent/codex/fitness-recovery/20261023`
- Canonical branch HEAD at refresh: `4c12cad9d1e73741d7449da57e3bd5b96871070b`
- Canonical Android manifest blob: `0969cdb2f18775f23e0870bf754612a04376895f`

The canonical manifest declares exactly five Health Connect permissions:

- `android.permission.health.READ_STEPS`
- `android.permission.health.READ_EXERCISE`
- `android.permission.health.WRITE_EXERCISE`
- `android.permission.health.READ_DISTANCE`
- `android.permission.health.READ_ACTIVE_CALORIES_BURNED`

`READ_HEART_RATE` remains absent. The existing exercise-session read scope is sufficient for swimming-session ingestion; no swimming-specific permission is needed.

## Held permission expansion

PR [#93](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93) remains open/draft at head `1cc08cef7dae7f432275fd23960f4390a49db14c`. Its current manifest blob is `a3b24f09e6b0c8a67b0fee3e7578317cfe979092` and declares 19 Health permissions: the five canonical permissions plus these 14 additional read scopes:

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

Do not merge the expansion wholesale. Each new data type requires a concrete user-visible feature, minimum-necessary rationale, service-level consent, Play Health declaration, privacy/Data Safety reconciliation, and physical grant/no-data/revoke/error validation. PR #98 was closed without merge and is not an integration candidate.

## Canonical Health implementation already integrated

- PR [#285](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/285) is merged. Its exact tested head `c8d464b86576db172d03a734ca9a119bd47631fb` passed Android candidate run [42827029570](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42827029570). It wires swimming eligibility into typed Health Connect exercise-session ingestion. Swimming requires a reviewed writer, compatible watch/band metadata, active/automatic recording, stable record ID, and valid interval. This is provider/device metadata, not cryptographic hardware attestation or physical watch proof.
- PR [#286](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/286) is merged as `3b65efa94709e3a60cc62113e19c92639e2a76b9`. Exact tested head `71a2863e51465ad587df8230269c1af4cbdf55d9` passed Android candidate run [43028123167](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43028123167). Record value, version and provenance now use the same latest source-scoped Health record version.
- PR [#282](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/282) remains draft. Its missing-permission-versus-zero UI correction passed an earlier exact-head workflow, but the shared `app.js` ownership chain and stale base remain unresolved. Do not claim physical Health UX acceptance.

## Required evidence before any Health-expanded release

| Gate | Required evidence | Current state |
|---|---|---|
| Play Health declaration | Exact declared data types and purpose tied to candidate source SHA, versionCode and AAB | NOT EVIDENCED |
| Privacy/Data Safety | Matching disclosure, purpose, retention and sharing | NOT EVIDENCED |
| Permission UX | Least-privilege rationale and truthful partial/no-data/revoked/error states | Source work exists; combined UI acceptance pending |
| Record provenance | Source package, stable identity, recording method, device class and trust reason per record | Stored in repository snapshot; complete UI serialization/physical review pending |
| Walking/running/cycling | Reconcile phone sensor/GPS and Health/watch evidence without double-counting; preserve distinct sessions | Cross-source policy exists; Health-reader integration and physical acceptance pending |
| Swimming | Compatible trusted Health wearable session; reject phone-only/manual/unknown records | Metadata gate integrated; physical watch verification NOT RUN |
| Heart rate | Optional user-visible feature, only when genuinely available from a permitted Health/watch source | Permission absent; feature/reader and physical tests not accepted |
| Physical Health Connect | Full/partial grants, no data, revoke and error cases with real source-labelled records | BLOCKED_NOT_RUN |

The repository's source provenance and device metadata must never be described as cryptographic sensor or wearable attestation. Imported/manual/unknown records remain distinguishable and must not receive verified rewards.

## Release boundary

The latest independently recorded Play readback is from 2026-11-10: Internal 51019 completed, Alpha 51007 draft, Production not verified. No newer successful Play readback is established here. VersionCode 51020 remains unallocated. This gate does not authorize signing, uploading, listing/track mutation or Production promotion.
