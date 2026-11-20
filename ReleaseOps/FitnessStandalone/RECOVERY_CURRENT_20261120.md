# TopHeroFit — canonical recovery checkpoint (2026-11-20)

Observed: 2026-11-20 14:01:23 UTC.
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical application HEAD before this documentation commit: `d8e315376de6785ec93a792342618737866ae121`.

## Canonical change merged today

PR [#305](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/305) is merged.

- Tested PR head: `4a732579eb90b9e97a8dca2339a1a7c6b8d8c194`.
- Merge commit / canonical HEAD: `d8e315376de6785ec93a792342618737866ae121`.
- Exact-head workflow: [44748990073](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44748990073) — SUCCESS.
- Product tests: 77/77.
- Source-contract tests: 34/34.
- Backend tests: 29/29.
- Android API 36: setup passed; `:app:testDebugUnitTest`, `:app:lintDebug`, `:app:assembleDebug`, and unsigned `:app:bundleRelease` validation passed.
- Android unit tests: 298/298; 0 failures; 0 ignored.
- Lint: 0 errors, 16 warnings, 1 hint.
- Gradle: BUILD SUCCESSFUL in 2m20s.
- QA package identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is validation identity only; no version allocation or Play action.

Artifact ID `14634457804`, 63,063,341 bytes. GitHub artifact ZIP SHA-256 `85f85fc59fc7b4fb6ff9df5684cd3e3c1787b8c6a521d86541e501ea9d824f6c`; the downloaded ZIP was independently rehashed and matched. APK SHA-256 `7052c5a79215a3b245148dfb2e0cc169b8ec9a005357eec2d1b35b83d57bcff7`. Unsigned validation AAB SHA-256 `bb9760d9a21eeb4d0c4d8a76009ce8e654b1a0d4da3fb9be06e6240819b15f3a`.

### Health Connect activity-session reconciliation

The change is restricted to four files:

- `HealthConnectRepository.kt` — canonical blob `a040318e8ebd77b1783f05b5f2b29e14792a4f9d`.
- `HealthExerciseSessionReconciliationPolicy.kt` — `23082cb85971f6e5f46fe837b2532b187918f4f8`.
- `HealthExerciseSessionReconciliationPolicyTest.kt` — `2d09bcefa35883e23a6e805b19ee7747c2f33542`.
- `test_health_activity_session_reconciliation.py` — `e74124fcb9b5f35ccfbf319258f3eea53571c0e6`.

Behavior:
- Applies only to reviewed Health Connect walking, running, and cycling exercise sessions after provider/type/record-ID version selection.
- Normalizes treadmill running to running and stationary biking to cycling.
- Near-identical same-sport sessions retain one deterministic winner; compatible watch/fitness-band metadata outranks phone, then newest provider modification and stable source/record identity break ties.
- Near-identical sessions with conflicting walking/running/cycling labels are all excluded from reward-verified session counts as `CONFLICTING_ACTIVITY_TYPE_AMBIGUOUS`; the app does not guess which source is correct.
- Duplicate sessions retain source provenance with `DUPLICATE_ACTIVITY_SESSION`; duplicate count includes these exclusions.
- Missing source/record identity, invalid intervals, missing observation time and future sessions fail closed.
- Unverified/manual/unknown records do not poison verified candidates.
- Only reconciled verified sessions contribute to exercise-session count and latest-session summary.

This is Health Connect metadata reconciliation, not GPS attestation, proof of physical exercise, or proof that a watch is genuine. Physical-device acceptance remains separate.

## Health permission and provenance baseline

Canonical manifest SHA remains `0969cdb2f18775f23e0870bf754612a04376895f`. Exactly five Health Connect permissions remain:

- `READ_STEPS`
- `READ_EXERCISE`
- `WRITE_EXERCISE`
- `READ_DISTANCE`
- `READ_ACTIVE_CALORIES_BURNED`

No heart-rate permission. Optional heart rate remains unavailable unless separately approved, granted and backed by actual data. Existing swimming eligibility remains restricted to reviewed provider records with compatible watch/fitness-band metadata, valid exercise-session identity/time and active/automatic recording. No swimming or wearable evidence was created in this run.

PR #93 still declares 19 Health permissions (14 more than canonical), including heart rate and clinical/wellness scopes. It owns the Health Services bridge, manifest and MainActivity; it remains Draft and must be reconciled before integration.

## Canonical content audit (read-only)

- Exercises: 112 unique IDs.
- English/Arabic step-array length mismatches: 84.
- Programs: 26; sessions: 94; exercise references: 470.
- Timed references: 232; all 232 still carry RIR; six timed Superman references have inappropriate RIR.
- Latest canonical offline-motion inventory from the November 19 checkpoint: 5 licensed video clips, 2 reviewed 16-frame sequences and 105 reference-only exercises. This run did not add or fabricate motion assets.

The bilingual catalog, timed-program and offline-demo PRs remain diverged; see `INTEGRATOR_LEASES_CURRENT_20261120.md`.

## GPS and physical acceptance

Latest GPS candidate is PR [#303](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/303), head `a3289482f93e500e2e0146e8f9b2d838a2390cb3`. It has exact-head CI success on run 44689978734, but after the Health merge it compares 3 ahead / 2 behind canonical and must be rebased by its native owner. Keep Draft until physical P0 passes.

Desktop Commander localhost is OFFLINE; last seen 76 hours ago. Last known handset: Samsung SM-A217F / Android 12; current installed app and session state are unknown. No ADB, installation, launch, notification action, location-setting change or activity-data read was attempted. See `GPS_MAP_QUALITY_20261120.md`.

## Google Play and release gates

Latest canonical readback is from 2026-11-19:
- Internal 51019: completed.
- Alpha 51007: draft.
- Production: not verified in the readback.
- Next versionCode 51020 remains unallocated.

No fresh Play readback was obtained on November 20. Health declaration/privacy reconciliation, data-safety consistency, physical Health Connect grant/revocation, wearable validation and GPS P0 remain hard release gates. No signing, release workflow, version, listing, track, upload or Play state was changed.

No paid service or unrelated project was used.
