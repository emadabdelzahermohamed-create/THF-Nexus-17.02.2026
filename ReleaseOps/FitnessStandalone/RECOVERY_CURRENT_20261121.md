# TopHeroFit — canonical recovery checkpoint (2026-11-21)

Observed: 2026-11-21 19:25 Africa/Cairo (17:25 UTC).  
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.  
Canonical branch: `agent/codex/fitness-recovery/20261023`.  
Canonical application merge: `b097d6ef0025d615c261ee42e8d2246533224e70`.  
Tested source SHA: `26e90573ddda077ca2665ebdccd5600cc9316dd7`.  
Both commits have the same Git tree `9fa0cea8f307c05483f336c409390727c1f7ebc4`; the squash merge preserves the exact tested application tree.

## 1. Canonical integration completed

PR [#303 — native GPS / Activity Engine](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/303) was merged at `b097d6ef0025d615c261ee42e8d2246533224e70`.

- Parent/base: `a87f86ef8d393772623ec34e5130610161bc365e`.
- Exact candidate HEAD: `26e90573ddda077ca2665ebdccd5600cc9316dd7`.
- Compare before merge: 1 commit ahead / 0 behind; exactly 15 changed files, all native Activity Engine/GPS source and tests.
- No WebView `app.js`, `index.html`, MainActivity, Manifest, Health repository, release/version, workflow, signing or Play files were changed.
- No unresolved review threads or submitted reviews were present.
- Post-merge branch readback points at the merge commit. Raw commit API confirms the merge tree is identical to the exact tested source tree.

## 2. Exact-head CI and artifact evidence

[Run 44929317705](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/44929317705) completed SUCCESS on exact source SHA `26e90573ddda077ca2665ebdccd5600cc9316dd7` on 2026-11-21.

| Suite | Result |
|---|---:|
| Product | 77/77 |
| Source contract | 35/35 |
| Backend | 29/29 |
| Android unit | 335/335 |
| Android failures / ignored | 0 / 0 |
| Android API 36 / Kotlin / Gradle | PASS |
| Lint / Debug APK / unsigned AAB validation | PASS |

Gradle BUILD SUCCESSFUL in 3m11s. Lint: 0 errors, 11 warnings, 1 hint.

Artifact 14715989999 (63,083,632 bytes), downloaded and independently rehashed:

- ZIP SHA-256: `d081932610a732a35df9e5eb37e641938566fe1cd15744760ae195f486a2268e`.
- Embedded source marker: `SOURCE_SHA=26e90573ddda077ca2665ebdccd5600cc9316dd7`.
- QA APK SHA-256: `39dc453eb4d5572f534ccd910882a17ccfb5b5c04849755897dcd6f73de2d9f5`.
- Validation AAB SHA-256: `4854e2585757383ce7d59e10b3bff48537a7bf4387dd2359c7918d339719d7d4`.
- `jarsigner -verify` reports `jar is unsigned`.

QA identity is `com.topherofit.thf.pulse.qa`, versionCode 51019, versionName `5.0.0-v2-alpha19-debug`. These are validation bytes only, not a signed release, version allocation or Play upload.

## 3. Native behavior now canonical

- Fused Location Provider primary with permission-level granularity; approximate-only users do not request GPS.
- 8-second first-fix and 12-second stale-fix fallback watchdog; only one eligible Android framework provider is active at a time.
- GPS-to-Network fallback is permission-aware; provider registrations have distinct listeners/generations, rejecting queued callbacks from replaced providers.
- Provider switches clear the prior distance anchor; distance is not bridged across providers.
- Invalid, mock, stale/future, out-of-order, poor-accuracy and implausible fixes are filtered.
- Distance accumulation uses uncertainty/deadband, multi-fix confirmation, long-gap re-anchoring and bounded path/net ratio. This reduces noise; it does not prove against prolonged stationary multipath drift.
- V3 local session checkpoint preserves phase, wall/monotonic clocks, boot identity and bounded route. Process downtime is excluded from active elapsed time.
- Foreground service, START_STICKY, ongoing notification, Pause/Resume/Finish actions and periodic local checkpoint writes are in source; physical continuity is not proven.

## 4. Legacy map handoff #284

[PR #284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284) remains open Draft.

- Head: `274155eafdfff381009ef5814a621f32b225f1a8`.
- Canonical comparison after #303 merge: 19 ahead / 80 behind; 13 changed files; diverged; no current-head CI.
- Historical run 42694452852 passed only on `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`.
- Historical run 42694199295 failed because the truncated MainActivity omitted `motionSnapshot`; no artifact was produced. Current #284 MainActivity is 1,146 lines and the symbol is present, but that is not CI or physical evidence.
- #284's native provider/service/presentation/test hunks are superseded by merged #303. Its remaining UI changes touch app.js, index.html and MainActivity and overlap shared-file leases (#93, #216, #224). The canonical Leaflet/OSM/OpenTopoMap/EOX stack is already present; no isolated map-tile change remains.
- Updated PR body records the reconciliation. Keep Draft; do not merge as-is.

## 5. Latest independent Google Play readback

[Read-only Publication State Probe 43739661313, attempt 6](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43739661313) completed successfully on 2026-11-21. Its probe job completed and artifact 14716559202 was downloaded and rehashed.

- ZIP SHA-256: `765481fc3a27a193bd483ad7f8bfb72459fd04b1fed8ee4f248ab0448278db92`.
- Embedded JSON SHA-256: `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.
- Package: `com.topherofit.thf.pulse`.
- Internal: 51019 Completed.
- Alpha: 51007 Draft.
- Production: not listed / not verified in this readback.
- `uploadAttempted=false`; `commitAttempted=false`.
- Listing remains unchanged and describes GPS sessions, background notification controls, offline-ready library and Arabic/English voice cues. These claims are not physical P0 evidence.

## 6. Phone and physical P0

Desktop Commander `localhost` is OFFLINE, last seen 103 hours before the 2026-11-21 check. Last known handset: Samsung SM-A217F / Android 12. Current device, app and session state are UNKNOWN.

No ADB, install, launch, force-stop, notification action, location-setting change or activity-data read was attempted. Preserve any possible active session.

Required physical P0 remains NOT RUN:
1. Stationary drift with screen on/off.
2. Measured outdoor walk/run/cycle against a reference route.
3. Fine-to-coarse permission downgrade and source-switch behavior.
4. First-fix latency and truthful provider/accuracy display.
5. In-app navigation, Home/background, screen-off and task removal continuity.
6. Notification Pause/Resume/Finish.
7. Process-death restore without downtime credit.
8. Crash/ANR/logcat review.

## 7. Health, anti-cheat and competitions

- Health PRs #282, #301, #304 and #305 remain merged. The canonical Health Connect allowlist remains five permissions: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE and READ_ACTIVE_CALORIES_BURNED. No Heart Rate or other additional permission was added.
- Health activity-session reconciliation is source/provenance metadata, not proof of physical exercise or GPS attestation.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired. A source review found its per-fix 3 m minimum overlaps with the live multi-fix accumulator and could discard valid short updates if stacked as a second gate. Keep `GpsFixGate` as admission and `GpsDistanceAccumulator` as the sole metric-credit path until a unified policy is designed. See [ANTI_CHEAT_RECONCILIATION_20261121.md](./ANTI_CHEAT_RECONCILIATION_20261121.md). Do not claim complete anti-cheat or GPS reward eligibility.
- Competition PR #269 is merged; current verified backend metric remains `strength_volume_kg_reps`. GPS reward eligibility remains false; no THF payouts are authorized.

## 8. Separate route-sync gap

- `persistFinishedActivity()` stores completed activity and route points in WebView localStorage (`pulse.v2.activities`, bounded to 100 history entries).
- The native active-session checkpoint is local Android preferences and is not a cloud queue.
- The one-second map/activity polling is local UI refresh, not a sync interval.
- Existing authenticated sync only covers workout/set metadata. No route endpoint, route table, route consent resource or precise-location upload path exists.
- Contract recheck and design-only constraints are in [ROUTE_SYNC_CONTRACT_RECHECK_20261121.md](./ROUTE_SYNC_CONTRACT_RECHECK_20261121.md) and [ROUTE_SYNC_DESIGN_20261110.md](./ROUTE_SYNC_DESIGN_20261110.md).
- Read-only AppDeploy inspection of snapshot `1794247542845` confirms authenticated `DELETE /api/account` calls `deleteFitnessV2UserData`; its V2 helper is byte-for-byte identical to canonical repository source. Runtime deletion on a non-privileged QA account and empty-history readback remain untested. Live privacy and account-deletion pages match canonical repository files and do not disclose precise-route backup.
- No route-sync implementation or cloud upload claim is made.

## 9. Release decision

- Last independently read Internal versionCode: 51019.
- Next versionCode 51020 remains UNALLOCATED.
- Owner Play/API write permission and GCP Secret Manager signing-key access remain NOT VERIFIED.
- No new signed AAB, version allocation, Play upload, track mutation or Production promotion.
- Release gate: HOLD until owner prerequisites, exact-head Android CI on the intended release source, physical P0, privacy/policy and signing/readback gates pass.
- No paid infrastructure and no other project was used.
