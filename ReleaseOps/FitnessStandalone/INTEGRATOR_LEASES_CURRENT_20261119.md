# TopHeroFit Integrator Lease Registry — 2026-11-19

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`. This registry is canonical for TopHeroFit only.

## Sole release authority

Only `agent/codex/fitness-recovery/20261023` may write:
- Android version allocation and `ReleaseOps/FitnessStandalone/RELEASE_CURRENT.json`;
- release workflows, signing configuration and signing secrets;
- Google Play upload, track, listing, commit or promotion state.

Canonical application source base at this checkpoint: `e28994ea76e67e0bed6eef3860f995b27388a002`. Next versionCode 51020 is unallocated. Owner Play write access and GCP Secret Manager signing access are NOT_VERIFIED. No release/Play write occurred in this checkpoint.

## Active file-level ownership

| Files / surface | Owner | Allowed work / hold |
|---|---|---|
| `ActivityTrackingService.kt`, GPS fallback/fix/distance/snapshot/checkpoint classes and native GPS tests | PR #303, branch `agent/codex/gps-activity-rebased-20261119-r1`, head `6e73d988...` | Exact-head CI 44582044304 PASS; 316/316 Android tests. Draft until physical P0. No parallel native GPS edits. |
| `HealthConnectRepository.kt`, `HealthMetricSourceReconciliationPolicy.kt`, its tests | Canonical after PR #304 merge `e28994ea...` | Integrated after exact-head CI 44532209892. Changes require a new isolated PR and exact-head CI. |
| `HealthMetricEvidencePolicy.kt` and Health evidence tests | Canonical after PR #301 | Fail-closed interval/value/rate checks; five-scope allowlist unchanged. No additional permission without owner/privacy review. |
| `app.js` metric formatting | Canonical after PR #282 | null/undefined/invalid => unavailable; genuine zero remains zero. |
| `app.js` active workout/session/resume UI | PR #216, Draft/diverged | Shared file. No whole-file overwrite; line-range lease and combined-head CI only. |
| `app.js` offline demo motion UI/assets | PR #224, Draft/diverged | Shared file/assets. No whole-file overwrite; validate offline asset hashes/licensing and combined-head CI. |
| `app.js` / `index.html` map UI | PR #284 candidate only, current head `274155ea...`, 19 ahead / 69 behind | Draft, no exact-head CI, overlaps #216/#224. Only map-only extraction after ownership reconciliation. |
| `MainActivity.kt`, `AndroidManifest.xml`, Health bridge and source-contract tests | PR #93, Draft, 2 ahead / 372 behind | 19 requested scopes conflict with canonical five-scope Health allowlist. Reduce to five, then exact-head CI. #284 also touches MainActivity/tests. |
| GPS route smoother helper | PR #248, Draft, 4 ahead / 206 behind | Not wired into ActivityTrackingService; do not treat as active GPS path. |
| Exercise catalog / Arabic cues | PR #160, Draft, 53 ahead / 227 behind; PR #257, Draft, 5 ahead / 206 behind; PR #260, Draft/noncanonical base, 15 ahead / 206 behind | Separate content ownership. No merge without current canonical base and exact tests. |
| Timed RIR / program semantics | PR #213, Draft/noncanonical base, 190 ahead / 227 behind | No merge without canonical rebase and exact tests. |
| Equipment filter | PR #258, Draft, 7 ahead / 204 behind | No exact-head evidence; lower priority than GPS/session. |
| Competition backend | PR #269 merged | Provisional `strength_volume_kg_reps` only; no verified activity leaderboard or reward eligibility. `rewardEligible=false`. |
| Route backup/sync | No implementation owner | Design-only; no route API/table/upload. Must remain separate from workout/set sync and one-second map UI refresh. |

## PR state against canonical application base `e28994ea...`

| PR | State / head | Ahead / behind | Exact-head CI | Decision |
|---|---|---:|---|---|
| #303 GPS | Draft, `6e73d988...` | 1 / 0; 14 native files | 44582044304 SUCCESS | Physical P0 required |
| #284 Maps/GPS | Draft, `274155ea...` | 19 / 69; 13 files | None on current head | Stale/overlapping; map-only extraction |
| #304 Health reconciliation | Merged `e28994ea...` | — | 44532209892 SUCCESS | Integrated |
| #93 Health services | Draft | 2 / 372 | None | 19 scopes vs five |
| #216 session resume | Draft/noncanonical base | 201 / 227 | None | Shared app.js |
| #224 offline demos | Draft/noncanonical base | 153 / 227 | None | Shared app.js/assets |
| #248 GPS smoother | Draft | 4 / 206 | None | Helper only |
| #160 Arabic exercise cues | Draft/noncanonical base | 53 / 227 | None | Catalog |
| #213 timed RIR | Draft/noncanonical base | 190 / 227 | None | Program semantics |
| #258 equipment filter | Draft | 7 / 204 | None | Lower priority |
| #257 Arabic cues | Draft | 5 / 206 | None | Lower priority |
| #260 Arabic cues | Draft/noncanonical base | 15 / 206 | None | Lower priority |
| #297 | Closed unmerged | — | Superseded by #303 | Do not reopen |
| #302 / #301 / #282 / #269 | Merged | — | Exact-head evidence recorded | Preserve canonical integrations |

## Physical-device boundary

Latest Desktop Commander inventory 2026-11-19: localhost OFFLINE, last seen 56h ago. Last known handset SM-A217F / Android 12; current session unknown. Preserve. No ADB, install, launch, force-stop, notification action, settings change or activity-data read until a safe connection is restored.

Physical P0 remains mandatory before #303 merge: measured outdoor routes, stationary drift, permission downgrade, first-fix latency, screen-off/background, notification Pause/Resume/Finish and process-death restore without downtime credit.

## Security / privacy / release boundaries

- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired. No full anti-cheat, cryptographic location attestation or activity reward eligibility is claimed.
- Existing workout endpoints carry set/workout metadata only. Route cloud sync is design-only and must default OFF with separate precise-location consent, retention, revocation and deletion.
- Health Connect allowlist remains five scopes; no heart-rate permission added.
- Google Play latest readback 2026-11-19: Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified; upload/commit false.
- No signing, version allocation, Play upload or Production promotion until owner API/key prerequisites, exact-source CI, physical P0 and policy/privacy gates pass.
- No paid infrastructure or unrelated projects.
