# TopHeroFit canonical recovery — 2026-11-18

Observed: 2026-11-18 17:45:50 UTC. This checkpoint is TopHeroFit-only and supersedes time-sensitive November 17/earlier PR, lease, GPS and Play observations.

## Canonical source

- Repository: \`emadabdelzahermohamed-create/THF-Nexus-17.02.2026\`.
- Canonical branch: \`agent/codex/fitness-recovery/20261023\`.
- Canonical application HEAD after the tested UI merge: \`d2e4c6887fc3b94565536e5d985c193ab8ac1990\`.
- #301 Health metric anomaly guard merged at \`7dc57dd9f6e647797cbbe2d1cfdb45773410a866\`.
- #302 truthful GPS status UI merged at \`d2e4c6887fc3b94565536e5d985c193ab8ac1990\`.
- #282 truthful null/zero metric rendering merged at \`b248a3571d871c604dbc3a11af72858bbac74eb9\`.
- Release/version/workflow/signing/Play writes remain owned only by the canonical integrator.

## Newly integrated, disjoint handoff — PR #302

PR #302 is merged. Its source HEAD was \`45b57ceaf218e15e04d8c818a40caa4e1b6376f7\`, one commit ahead / zero behind canonical \`77c371334f6b5851981b35196b0a3a6f3f6ad715\` at merge time.

- Exact-head CI: [run 44361213445](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44361213445), SUCCESS.
- Product tests: 73; source-contract: 34; backend: 29.
- Android unit: 275/275; 0 failures, 0 ignored.
- API 36, Kotlin, lintDebug, assembleDebug and bundleRelease validation: PASS; Gradle BUILD SUCCESSFUL.
- Lint: 0 errors, 16 warnings, 1 hint.
- Artifact 14455031111 ZIP SHA-256: \`381473a829fc64ead55b27f1264a570ffd1ba7dab1c59b61cc6ac232f7e68095\`.
- QA APK SHA-256: \`d4a896e436ef185142721ba88ed6c56bd2df4e556f5fe22dd640cf6385af3667\`.
- Validation AAB SHA-256: \`0f968afa00f68c787bb0751caffbd8857ab56a92451f5fca1ed2d30fac216dfa\`; independently checked with \`jarsigner\`: unsigned.
- QA versionCode 51019 only. No install, signing, Play upload or track mutation.

The UI now labels accepted Fused/NETWORK fixes as “Location”, shows a distinct paused state, displays accepted accuracy only when finite and positive, and uses bilingual location labels. It changes only the status UI/header and a product regression test; it does not change native GPS service, route storage, Health scopes or release/signing files.

## GPS native candidate — PR #297

- Branch: \`agent/codex/gps-permission-downgrade-20261116-r1\`.
- Exact PR head: \`f741af0dccd48dbcf258f5ae5b1d23e0db58f3af\`.
- Current canonical comparison after #302: 11 ahead / 2 behind, diverged. The two behind commits are the documentation checkpoint and #302 UI merge; #297 does not contain the new UI fix.
- Current diff: 14 native GPS/session source/test files plus two checkpoint documents; no app.js, Health, MainActivity, Manifest, release, version, workflow, signing or Play changes.
- Exact-head CI: [run 44358671462](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44358671462), SUCCESS on exact HEAD \`f741af0dccd48dbcf258f5ae5b1d23e0db58f3af\`.
- Product 69/69; source-contract 34/34; backend 29/29; Android unit 304/304; 0 failures, 0 ignored; API 36, Kotlin, lint, assembleDebug and bundleRelease validation PASS.
- Artifact 14452564181 ZIP SHA-256: \`1fe20c29953a629f35d93413473345ae67ddc3414f8b071d335e25701d309609\`.
- QA APK SHA-256: \`d471438d8ce89454a24ab6cd8d8f802ae58c2e270c1ca93f3a01e7478d8cf77f\`.
- Release-validation AAB SHA-256: \`670d09313a87daf64ffa6dfe2dcd825fc6a7f8e9a7232c6eaf7f73eb93316082\`; independently downloaded and verified unsigned.
- Artifact records source SHA \`f741af0dccd48dbcf258f5ae5b1d23e0db58f3af\`, QA package \`com.topherofit.thf.pulse.qa\`, versionCode 51019. It is validation-only, not a release artifact.

Included source behavior: Fused primary with permission-aware single framework provider fallback; fine-to-coarse downgrade; provider re-anchoring; mock/stale/future/out-of-order/poor-accuracy/implausible-fix filtering; bounded V3 session checkpoint with phase, wall/monotonic clocks, boot identity and route; START_STICKY foreground service, persistent notification, Pause/Resume/Finish actions and periodic checkpointing.

**Keep #297 Draft/unmerged.** Physical P0 remains NOT RUN. For the eventual physical QA candidate, rebase/transplant the 14 native files onto current canonical so the APK includes #302's status UI, then run exact-head CI again. Do not rebuild the unchanged old source merely to refresh docs.

## Historical GPS PR #284

- Current head: \`274155eafdfff381009ef5814a621f32b225f1a8\`.
- Current compare: 19 ahead / 65 behind canonical; diverged; no exact-head CI.
- Historical run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) validates only historical SHA \`3fcbe6acbb4dc660284c74c8392818996e1de7ee\`.
- Historical MainActivity truncation failure 42694199295 was due the 1,000-line API read limit. Full 1,146-line MainActivity was restored and \`motionSnapshot\` verified on the historical checkpoint.
- #284 overlaps #297 native ActivityTrackingService/fallback policy, #93 MainActivity/Manifest, and #302's now-canonical renderActivity status/pause presentation. Keep Draft; never merge its current branch wholesale.
- If still needed after P0, isolate only Leaflet/OSM map-specific UI/settings from native GPS, Health/MainActivity and current status rendering; rebase and run exact-head CI.

## Maps decision

Current map architecture is Leaflet in WebView with attributed OpenStreetMap streets, OpenTopoMap terrain and EOX Sentinel-2 cloudless satellite/hybrid tiles. No Google Maps SDK, archived Rx wrapper, billing, key or paid infrastructure is required for this selected stack. Browser tile caching is not a complete offline map package. Google directions remains an optional external handoff.

## Health, metrics, anti-cheat and competitions

- #282: null/undefined/invalid metric values render unavailable; genuine zero remains zero.
- #301: fail-closed Health metric interval/value/rate checks; 14 deterministic tests. No Health permission expansion.
- Canonical Health allowlist remains exactly five scopes: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE, READ_ACTIVE_CALORIES_BURNED. READ_HEART_RATE remains absent.
- #93 remains Draft, 2 ahead / 368 behind, requests 19 scopes and overlaps MainActivity/Manifest. No permission expansion until reduced to the five approved scopes and retested.
- \`ActivityEvidenceAnomalyPolicy.assessSegment()\` is present and unit-tested but remains unwired in \`ActivityTrackingService\`. GpsFixGate and GpsDistanceAccumulator are filters/re-anchoring, not full anti-cheat or cryptographic location attestation. Do not claim anti-cheat PASS or reward eligibility.
- #269 is merged, but only provisional \`strength_volume_kg_reps\` is supported. Admin creation requires owner-managed \`THF_COMPETITION_ADMIN_KEY\` and independently verified production deployment; neither is verified. Scores remain \`SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED\`, \`rewardEligible=false\`; no THF rewards/payouts.

## Route backup / sync gap — separate from local map refresh

Completed route points are persisted in WebView localStorage. Existing authenticated \`/api/v2/workouts/sync\` and \`/api/v2/workouts?limit=200\` carry workout/set metadata only; no authenticated route endpoint/table exists. Route sync remains DESIGN ONLY. No route upload or cloud restore is implemented. After #284 map/native reconciliation and GPS validation, design opt-in finished-session route backup with separate precise-location consent, explicit retention/revocation/deletion and no precise-location upload by default. Do not conflate this with the 1-second local GPS-to-map refresh.

## Device / physical P0

- Desktop Commander localhost was OFFLINE at 2026-11-18 19:45 Cairo; last seen about 32 hours earlier.
- Last known handset: Samsung SM-A217F / Android 12. Current app/session state UNKNOWN; preserve.
- Last recorded device-wide \`location_mode=0\` is from 2026-11-09. No setting was changed.
- No ADB, install, launch, force-stop, Stop action, settings change or activity-data read was attempted in this recheck.
- Physical P0 remains BLOCKED_NOT_RUN: stationary drift, measured outdoor walk/run/cycle, fine-to-coarse downgrade, first-fix latency, screen-off/background, notification Pause/Resume/Finish, task removal and process-death restore.

## Google Play / release

Latest independent read-only Play probe: [run 43739661313, attempt 3](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43739661313), completed 2026-11-18 17:22:53Z.

- Internal: 51019 Completed.
- Alpha: 51007 Draft.
- Production: NOT_VERIFIED_NOT_LISTED_IN_READBACK.
- Upload attempted: false. Commit attempted: false.
- Artifact 14451997696 ZIP SHA-256: \`e7de6f3f00394c4888e0e3755f2259d072469733f9ebba14f1146a465096901e\`.
- Embedded JSON SHA-256: \`09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63\`.
- Downloaded artifact and embedded JSON were independently rehashed. The readback is fresh but read-only; it is not a Play upload or production proof.
- Owner Play write permission and GCP Secret Manager signing access remain unverified. Legacy promotion workflow is pinned to old source/certificate/versionCode 51019 and is not a 51020 workflow.
- Internal 51019 remains canonical. Next versionCode 51020 is **not allocated**. No signed release AAB, upload, listing edit, track mutation or Production promotion.
- Release gate: HOLD until owner API/key prerequisites, current exact-head Android CI, physical P0, policy/privacy and signed-AAB independent Play Internal readback are satisfied.

No paid infrastructure or other project was used.