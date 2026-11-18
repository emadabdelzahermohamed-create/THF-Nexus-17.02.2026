# TopHeroFit Integrator Lease Registry — 2026-11-18

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`. This registry is canonical for TopHeroFit only.

## Release authority

Only the canonical branch `agent/codex/fitness-recovery/20261023` may write:
- release/version allocation and `RELEASE_CURRENT.json`;
- release workflows and signing configuration/secrets;
- Google Play upload, track, listing or promotion state.

Current application/source base: `7dc57dd9f6e647797cbbe2d1cfdb45773410a866`. Latest Internal readback: 51019 Completed. 51020 is not allocated. Owner Play write access and GCP Secret Manager signing access are not verified.

## Active file-level holds

| Files / surface | Owner | Current status and allowed work |
|---|---|---|
| `ActivityTrackingService.kt`, GPS policy/accumulator/checkpoint classes and GPS unit tests | PR #297 branch `agent/codex/gps-permission-downgrade-20261116-r1`, head `f741af0dccd48dbcf258f5ae5b1d23e0db58f3af` | Exact-head CI 44358671462 PASS; 304/304 Android tests; Draft until physical P0. No parallel native GPS writes. |
| `HealthConnectRepository.kt`, `HealthMetricEvidencePolicy.kt`, its tests | Canonical after PR #301 merge `7dc57dd9f6e647797cbbe2d1cfdb45773410a866` | Integrated; 14/14 new tests; no new permissions. Changes require new isolated PR and exact-head CI. |
| `app.js` Health metric summary formatter | PR #282 merged at `b248a3571d871c604dbc3a11af72858bbac74eb9` | Canonical; null/undefined/invalid => unavailable; genuine zero remains zero. |
| `app.js` active workout/session/resume UI | PR #216 | Draft/diverged. No whole-file overwrite. Only isolated line-range changes after lease check and combined-head CI. |
| `app.js` offline demo motion UI | PR #224 | Draft/diverged. Owns demo-motion hunks; no whole-file overwrite. |
| `app.js` GPS status/map/pause UI | PR #284 candidate only | Current PR head `274155eafdfff381009ef5814a621f32b225f1a8`, 19 ahead / 63 behind, no exact-head CI. It overlaps GPS/map and pause copy. A minimal “Location”/paused-status hunk is not yet assigned; do not edit until separate line-range lease and combined-head CI. |
| `MainActivity.kt`, `AndroidManifest.xml`, Health Services bridge | PR #93 | Draft/diverged; 19 requested permissions conflict with canonical five-scope allowlist. Blocked until reduced to five and exact-head tested. |
| Exercise catalog/program data | PR #160 / #213 | Draft/diverged; no exact-head native CI. Keep catalog and timed-RIR contracts separate. |
| Offline demo catalog/assets/runtime | PR #224 | Draft/diverged; validate asset/license/hash parity and native build before merge. |
| GPS route smoother helper | PR #248 | Draft, 4 ahead / 200 behind; not wired into service. Do not treat as active GPS path. |
| Route backup/sync | No implementation owner assigned | Design-only. No route endpoint or cloud upload. Must remain separate from workout/set sync and one-second local map refresh. |

## PR state against canonical source 7dc57dd9

| PR | Head | Ahead / behind | Exact-head CI | Decision |
|---|---|---:|---|---|
| #297 GPS | `f741af0d...` | 11 / 0 | 44358671462 SUCCESS | Draft; physical P0 required |
| #284 Maps | `274155ea...` | 19 / 63 | None on current head | Draft; stale/overlapping |
| #93 Health Services | `1cc08cef...` | 2 / 366 | None on current head | Draft; 19 vs 5 scopes |
| #216 Session Resume | `1ef91588...` | 201 / 221 | None on current head | Draft; shared app.js |
| #224 Offline Demos | `cc703baa...` | 153 / 221 | None on current head | Draft; shared app.js |
| #160 Catalog | `82e5ca5c...` | 53 / 221 | None on current head | Draft; no exact native CI |
| #213 Timed RIR | `f719214d...` | 190 / 221 | None on current head | Draft; no exact native CI |
| #248 GPS smoother | `67d3b438...` | 4 / 200 | None on current head | Draft; helper only |
| #301 Health metric guard | merged `7dc57dd9...` | — | 44315659269 SUCCESS | Integrated |
| #282 Metrics | merged `b248a357...` | — | 44138210115 SUCCESS | Integrated |
| #295 / #299 / #300 / #269 | merged | — | prior exact CI recorded | Existing canonical integrations |

PR #294 is closed unmerged and superseded by #297.

## Device and release gates

Desktop Commander localhost is OFFLINE; last seen about 31 hours before the 2026-11-18 19:29 Cairo check. Last known device is SM-A217F / Android 12. Current session state is unknown. Do not ADB, install, launch, force-stop, clear data, issue Stop, change location mode or read activity data until a safe connection is restored.

PR #297 is not merge-authorized until physical P0: measured outdoor routes, stationary drift, permission downgrade, screen-off/background, notification Pause/Resume/Finish and process-death restore. Anti-cheat remains incomplete because `ActivityEvidenceAnomalyPolicy.assessSegment()` is unwired. Competition scores remain `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED`, `rewardEligible=false`.

Route sync remains design-only. Existing `/api/v2/workouts/sync` and `/api/v2/workouts?limit=200` contain workout/set metadata only; no precise GPS route endpoint exists. No route upload by default.

No paid infrastructure or unrelated projects were used.
