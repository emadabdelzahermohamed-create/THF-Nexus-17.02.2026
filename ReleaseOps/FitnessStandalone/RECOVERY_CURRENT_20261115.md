# TopHeroFit canonical recovery — 2026-11-15

Scope: **TopHeroFit only**. Sole source of truth: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.

## Canonical source

- Starting canonical HEAD for this run: `73cdb2f5082f7631d4d6ce6459a6f6a89ba4db15`.
- Latest application merge: PR #296, squash merge `1e38da33ba16e9fa6a3276606a1130ff8f95a454`.
- Canonical branch now points to `1e38da33ba16e9fa6a3276606a1130ff8f95a454`.
- PR #296 was 3 ahead / 0 behind its exact canonical base; after merge, the canonical compare is 1 commit ahead / 0 behind.
- The three changed application/test files were independently re-fetched from canonical and their blobs match the tested PR tree:
  - `HealthConnectRepository.kt`: `d9e97dd12eb900c5101ba5569a90a73d2605a931`
  - `HealthRecordProvenancePresentationPolicy.kt`: `2803a7def252ebe645d33c800f8c9ef956a15a59`
  - `HealthRecordProvenancePresentationPolicyTest.kt`: `4dd3a9c095da7258c15136346d90dc26e894b2c8`
- Canonical Android manifest was re-fetched unchanged: `0969cdb2f18775f23e0870bf754612a04376895f`.

## PR #296 — Health Connect swimming presentation fail-closed

[PR #296](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/296) merged successfully.

- Tested PR head: `c2e3058c936b59e71f3c7e67cb854be516a6b4d9`.
- Merge commit: `1e38da33ba16e9fa6a3276606a1130ff8f95a454`.
- Exact-head Android candidate workflow [43721667918](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43721667918): SUCCESS.
- Product tests: 67/67.
- Source-contract tests: 34/34.
- Backend tests: 29/29.
- Android `:app:testDebugUnitTest`: 254 tests, 0 failures, 0 skipped.
- Android API 36, lint, `:app:assembleDebug` and `:app:bundleRelease`: PASS.
- Lint: 0 errors, 16 warnings, 1 hint.
- Gradle: BUILD SUCCESSFUL in 3m 1s.

Artifact 14164513840:
- ZIP SHA-256: `762540d8b291c1e7b7419130b2decd8c8c6b7c3b3a41183bbeb37f66c09c7659` (independently recomputed and matched).
- QA APK SHA-256: `e20af5bdcfe34c088bcb5ddba8ba1852b26d36b6281c3614654cd1b2a9b7456a`.
- Unsigned validation AAB SHA-256: `34998ff0a56b601aca328392e31d697d79ca02f7be3922e2ba00d27d6efe89ec`.
- `jarsigner` confirms the AAB is unsigned.
- QA identity: `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. This is not a release artifact.

Material behavior:
- Internal Health evidence now retains the actual exercise-session type and start/end instants from the Health Connect record.
- These fields are not added to the privacy-reduced UI summary.
- The presentation policy independently requires complete exercise-session metadata and valid positive session time.
- Swimming presentation reuses the canonical swimming eligibility policy: reviewed provider, compatible watch/fitness-band metadata, active/automatic recording, stable record ID and valid time range.
- Phone, ring and chest-strap swimming records fail closed even if upstream flags inconsistently claim VERIFIED.
- Missing exercise type/time and exercise metadata attached to a metric record fail closed.
- The reviewed-provider phone path for non-swimming running remains intact.
- This is a Health Connect metadata gate, not cryptographic hardware attestation. Physical wearable validation remains mandatory.

## Latest recovery and GPS handoff

Starting recovery document: [RECOVERY_CURRENT_20261114.md](RECOVERY_CURRENT_20261114.md), blob `57003b8fdd576f7ca6a11d95503e8a622fdd703c`.

Latest GPS report: [GPS_MAP_QUALITY_20261114.md](GPS_MAP_QUALITY_20261114.md), blob `b7436e3871ceae09188a66fe6b482c10ce5c674f`.

- Selected native GPS PR #294 remains open/Draft/unmerged.
- Current PR head: `a238aef70f5114fb845d7a55cdb59a1fc1bfd61e`; base remains `82ac0797f26ef142bee868ea6f8378066a961b1e`.
- Compare against current canonical: 4 ahead / 6 behind; current diff contains eight GPS source/test files.
- PR body still describes the earlier exact-tested source `7933a0eb0b6bedf8d00af49fee41ed24d88c264f` and six files; its metadata/body is stale relative to current head. The prior exact combined-head run [43625025348](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43625025348) passed that tested source, but does not establish current-head CI.
- Keep GPS ownership with #294. Do not edit or merge GPS native files in this lane.
- The canonical anomaly policy exists, but the selected GPS service still does not call `ActivityEvidenceAnomalyPolicy.assessSegment`. Live source-continuity, long-gap and uncertainty-adjusted segment checks remain outstanding.

## Current PR and file ownership audit

| PR | Current comparison / changed surface | Decision |
|---|---|---|
| #93 Health Services | 2 ahead / 349 behind; manifest, MainActivity, source-contract, reader/models/activity and rationale strings | Diverged; 19-scope manifest conflicts with canonical five-scope allowlist. Keep Draft. |
| #282 Health metric truthfulness | 2 ahead / 88 behind; shared `app.js` plus focused product test | Keep separate from #216 shared active-workout UI. |
| #160 bilingual catalog | 53 ahead / 204 behind; exercises JS/JSON, catalog manifest, builder and tests | Do not merge stacked branch; semantic and parity reconciliation required. |
| #213 timed program prescriptions | 190 ahead / 204 behind; `app.js`, programs JS/JSON, manifest, builder and tests | Do not merge stacked branch; reconcile with #204/#212/#214/#233/#234 and active workout UI. |
| #224 offline active demos | 153 ahead / 204 behind; active-workout demo module, `app.js`, `index.html`, test | Keep separate until shared UI ownership is reconciled. |
| #294 GPS | 4 ahead / 6 behind; eight GPS source/test files | GPS owner only; current PR body/head mismatch and physical P0 remain. |
| #296 swimming presentation gate | Merged at `1e38da33ba16e9fa6a3276606a1130ff8f95a454` | Canonical and exact-head tested. |

A current ownership/blocker note was added to [PR #93](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93): [comment 6895448461](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93#issuecomment-6895448461). It records the latest 2-ahead / 349-behind comparison, 19-vs-5 permission discrepancy and the disjoint #296 ownership boundary.

## Health permissions and evidence

Canonical manifest remains exactly five Health Connect scopes:
- `READ_STEPS`
- `READ_EXERCISE`
- `WRITE_EXERCISE`
- `READ_DISTANCE`
- `READ_ACTIVE_CALORIES_BURNED`

`READ_HEART_RATE` remains absent. No optional heart-rate permission or reader was added.

PR #93 still adds 14 extra declarations, including sleep, total calories, heart rate/resting heart rate, body measurements, oxygen saturation, VO2 max, speed, nutrition, blood pressure and glucose. These remain unauthorized until least-privilege feature, rationale, Play declaration and privacy gates are satisfied.

The live Health UI bridge still does not serialize `HealthSnapshot.recordProvenance`; PR #93 owns MainActivity and source-contract integration. Only privacy-reduced summaries may be bridged. Raw provider/client record IDs and device manufacturer/model must not be exposed.

## Exercise catalog, programs and offline motion audit

Current canonical data blobs:
- `exercises.json`: `425f0dab3fa1b0718cf84dd818a26d3585881718`
- `programs.json`: `013022b7cb647e17b66cd2c9f3aad20c39050062`
- `motion-manifest.json`: `16fb02e9f87e7930fa6b779f8f6440f11d8ae1ab`
- `video-licenses.json`: `e0b7c9e4bfc4afab643dc9c5b9d198c0d1f48887`

Fresh data audit:
- 112 exercises; 84 English/Arabic step-count mismatches.
- At least 23 Arabic step rows match known generic fallback phrases; semantic quality review remains necessary.
- 26 programs, 94 sessions, 470 exercise references, zero unknown exercise IDs.
- 232 timed references; all 232 currently carry RIR, including 226 whose catalog tracking disables RIR.
- Six timed Superman references still conflict with the catalog's repetition-based prescription.
- PR #160's parity candidate and PR #213's program candidate remain highly divergent and have shared-file ownership collisions; do not merge wholesale.

Offline motion manifest has seven entries: five licensed offline video assets and two reviewed 16-frame sequences. The other 105 catalog exercises remain reference-only two-frame demonstrations; do not describe them as full-motion videos. Merged PR #289's mapping/license/hash tests remain canonical.

The passing product suite on #296 also rechecked bilingual voice guidance, Health permission scope, forced-colors accessibility, keyboard focus, reduced motion, program progression and offline asset mappings.

## Physical, Play and release gates

- Desktop Commander `localhost` was checked on 2026-11-15 and remains OFFLINE (last seen 123 hours ago). Last known phone in the prior checkpoint: Samsung SM-A217F / Android 12. Current device/session state is unknown.
- No ADB, install, launch, Stop, settings or activity-data action was attempted.
- Physical Health Connect grant/partial-grant/revoke/no-data/error checks, actual compatible wearable validation, physical swimming, GPS stationary drift, measured routes, background/screen-off and process-death checks remain BLOCKED_NOT_RUN.
- The latest verified Play readback remains 2026-11-14 18:03:26 UTC: Internal 51019 completed; Alpha 51007 draft; Production not verified. No new Play readback was obtained in this run.
- VersionCode 51020 remains unallocated. No signing, release workflow, listing, upload or Production promotion occurred.
- Play Health declaration/privacy reconciliation remains a hard release gate. No new Health scopes were added.
- No paid service, Maps billing/key, unrelated project or external route upload was used.

## Next safe execution order

1. Keep PR #93 blocked until it rebases, restores the five-scope allowlist and integrates the privacy-reduced per-record provenance bridge with exact-head CI.
2. Connect phone-measured evidence to walking/running/cycling reconciliation without editing GPS acquisition.
3. Keep the live GPS anomaly-policy wiring with the #294 owner; require current-head CI and physical P0.
4. Consolidate bilingual catalog semantic fixes and timed-program RIR/dose corrections onto canonical without merging divergent stacks.
5. Expand genuinely licensed full-motion offline demonstrations with exact exercise mappings.
6. Keep heart rate optional and absent until a real supported data path and least-privilege declaration exist.
7. Preserve physical Health/wearable/GPS and Play privacy gates before any release decision.

No release version, signing configuration, workflow, Play state, GPS native file or tracking session was changed in this run.
