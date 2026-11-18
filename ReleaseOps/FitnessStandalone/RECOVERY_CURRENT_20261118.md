# TopHeroFit canonical recovery candidate — 2026-11-18

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`. Scope: TopHeroFit only. The repository is the sole source of truth.

## Canonical source and completed handoffs

- Canonical branch: `agent/codex/fitness-recovery/20261023`.
- Current canonical HEAD at checkpoint creation: `7dc57dd9f6e647797cbbe2d1cfdb45773410a866`.
- PR #301 merged by squash as `7dc57dd9f6e647797cbbe2d1cfdb45773410a866`. It adds `HealthMetricEvidencePolicy` and validates Health Connect metric intervals/values only after the existing source trust assessment. It rejects negative/non-finite values, invalid/pre-epoch/reversed/future intervals and extreme rates; genuine zero remains zero. No permissions were added; the five-scope Health Connect baseline remains unchanged.
- PR #301 exact-head CI: [44315659269](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44315659269), source `853bd4e78b82d3b0db9203416a071bf360aa6a44`, SUCCESS; 14/14 metric-policy tests, Product 69/69, Source 34/34, Backend 29/29, Android build/lint/unsigned bundle PASS.
- PR #282 remains merged: null/undefined/invalid health metrics display unavailable; genuine zero remains zero.
- PRs #295, #299 and #300 remain merged; Health future-session observation-time rejection and sport/source provenance remain canonical.

## GPS / session candidate

- PR #297 is the selected GPS/native Activity Engine handoff; branch `agent/codex/gps-permission-downgrade-20261116-r1`.
- Prior exact tested head `a007f62c6f7f088d60e9ed42c686c9cb45c5d407`; exact-head run [44258464973](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44258464973) SUCCESS with Product 69/69, Source 34/34, Backend 29/29 and Android 290/290.
- The exact candidate artifact 14407681576 was downloaded and ZIP-rehashed: `5483f5edfb08c2252ccc52132faf22287f13a36182dd15de253935239cc08c01`. APK SHA `6c382e69f574bd9cf45748e4e15989f02bc76abbd2e4bf4bd670c2380e31959e`; unsigned AAB SHA `c02f9ee942ab67261e76720927aff48dcfa129e4100d49e92f20195c10dcf5fb`. This AAB is identical to the earlier 16c5104 artifact; no reupload.
- The GPS candidate has now been synchronized with canonical PR #301 and the November 17 release/recovery evidence. A new combined-head Android CI is required before it can be considered merge-ready. Keep Draft until that CI and physical P0 pass.
- PR #284 remains a separate historical Maps/GPS handoff. Its old requested run 42694452852 validates only historical head `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; current PR #284 head is not validated on exact head and overlaps GPS, MainActivity/Manifest and shared app.js ownership. Keep Draft; do not merge wholesale.

## Current Play evidence

- Read-only publication probe run [43739661313, attempt 3](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43739661313) completed successfully at 2026-11-18T17:22:53Z.
- Artifact 14451997696 ZIP SHA-256 `e7de6f3f00394c4888e0e3755f2259d072469733f9ebba14f1146a465096901e`, independently downloaded/rehashed. Embedded JSON SHA-256 `09e7a346e5e1c893d4323d20105d8f4d63`, independently recomputed.
- Google Play package `com.topherofit.thf.pulse`: Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified. `uploadAttempted=false`, `commitAttempted=false`. The probe created/read/deleted a temporary edit; it did not change a published track.
- This is a fresh read-only Play readback; no new AAB was uploaded.

## Active PR / lease status

- #297 owns native GPS/session files; no parallel native GPS edits.
- #284 remains stale/overlapping and untested on its current head.
- #93 remains blocked: it requests 19 Health permissions while canonical allowlist is five; rebase and remove 14 extra scopes before exact CI.
- #216/#224 retain shared `app.js` workout/demo ownership; no whole-file overwrite.
- #160/#213 remain divergent catalog/program stacks without exact-head native CI.
- #248 remains a standalone smoother helper not wired into the service and without Android Gradle/JUnit exact-head CI.
- #301 is merged. #282, #295, #299, #300 and #269 remain merged.
- Competition backend remains provisional `strength_volume_kg_reps`; no owner admin key or production authority verified; `rewardEligible=false` until evidence gates pass.

## Physical-device boundary

Desktop Commander localhost is OFFLINE (last seen about 31 hours before this check). Last known handset SM-A217F / Android 12. Current session unknown. Do not force-stop, install, launch, clear data, change device-wide location mode or read activity history until a safe connection is restored. Physical P0 remains NOT RUN for outdoor measured routes, stationary drift, precise-to-approximate downgrade, screen-off/background, notification actions and process-death restore.

## Separate route-sync gap

Completed GPS route history remains in WebView localStorage. No authenticated route-sync endpoint or cloud route upload/restore is implemented. The one-second local map refresh is not cloud sync. Keep route backup opt-in with separate precise-location consent, retention/deletion/revocation and no precise upload by default.

## Release gate

- Last Internal versionCode: 51019.
- Next versionCode 51020 remains unallocated.
- Owner Play write permission and GCP Secret Manager signing access remain unverified.
- No signed release AAB, signing, upload, track mutation or Production promotion.
- Production requires physical P0 plus privacy/policy and owner signing/API gates.

No paid infrastructure or unrelated projects were used.
