# TopHeroFit — Canonical Recovery Checkpoint

**Observed:** 2026-11-26 17:59:45 UTC  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical application head:** `779df53146e23e76fe7b1faabffbc0e3540ee29a`  
**Latest read-only Play probe trigger:** `8905c6dc5e39dbd47c16a993225729e13cebe880`  
**Latest Play probe:** [45872277536](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45872277536)

## Source of truth and release ownership

- This repository and canonical branch are the only TopHeroFit source of truth.
- The default GitHub branch `main` is not the canonical release branch. Continue from `agent/codex/fitness-recovery/20261023`.
- `ReleaseOps/FitnessStandalone/RELEASE_CURRENT.json` is the release pointer.
- Only the canonical integrator writes release/version allocation, release/publication workflows, signing, Play upload/commit/promotion, and canonical recovery/lease evidence.
- No paid infrastructure and no unrelated projects.

## Canonical Health integration — PR #314

- PR [#314](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/314) merged 2026-11-26 17:57:25 UTC.
- Exact PR source SHA: `95f4996d0fefc3017401289d29278dda6740adec`.
- Squash merge / canonical application head: `779df53146e23e76fe7b1faabffbc0e3540ee29a`.
- Scope: only `HealthSportMapper.kt` and `HealthSportMapperTest.kt`; no manifest, permission, GPS, tracking, release, signing, or Play changes.
- Exact-head workflow [45830026710](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45830026710): Product 84/84, Source Contract 35/35, Backend 29/29, Android Unit 352/352; zero Android failures/ignored; Android API 36, Kotlin/Gradle and bundle validation PASS; lint 0 errors, 12 warnings, 1 hint.
- Artifact 15121128134, ZIP SHA-256 `5792eb77f98ec89e165350a6adcedcf4729c49b899e6a992b5f37971fd340e8d`, downloaded and independently rehashed.
- Embedded `SOURCE_SHA` is exactly `95f4996d0fefc3017401289d29278dda6740adec`.
- QA APK SHA-256 `fbd89742d804a4755fe9b45f2d1df84f23e306a1004292c5bc448f1b68665bec`.
- Validation AAB SHA-256 `477f52c66fa404ff294371a1a6e0b5bb9aaa5b5e2826f2f9a5f3c7bb3363bf2a`; `jarsigner` confirms unsigned. This is QA-only, versionCode 51019; no release version allocated and no Play write.
- Post-merge blob readback matches the exact PR-head blobs: mapper `a1446e1343045c9c14df3766e705930544576627`; test `ebd9e4bf58454fb88df538da34e71c9f6ef51064`.
- Push workflow [45872021666](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45872021666) completed success on merge SHA, but its deterministic-build job was skipped and it produced no artifact. Do not treat that run as a post-merge build.

The mapper now prioritizes reviewed exercise IDs over broad program labels, retains known sport fallback, allows OTHER_WORKOUT only for explicit generic labels, and rejects unknown/missing mappings instead of inventing a Health Connect exercise type. This did not add Health Connect permissions or create wearable/physical evidence.

## GPS handoff — PR #311

- PR [#311](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/311), Draft/unmerged.
- Branch head: `5eee7f80543d88420af011e36c4001660e75ee3b`; base SHA: `10d9794546e6ecd203bb8078ed458f25a23f056c`.
- Exact-head workflow [45566362328](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45566362328) succeeded on the exact PR head: Product 84/84, Source Contract 40/40, Backend 29/29, Android Unit 355/355; zero failures/ignored; API 36, Kotlin/Gradle, lint and APK/unsigned-AAB validation PASS (0 lint errors, 13 warnings, 1 hint).
- Artifact 14999518977 ZIP SHA-256 `01d30c100dece05428d6f3bb78b61468ebf8281c031f675e243d56d2e0bf50b0`; QA APK `154b76c9601db115a4b8484af8f051cce017abd10b5edf7a0e9b5e9e133ea301`; unsigned AAB `cd51118db39df8124448d1cc6856e3b5709334b2990111799537f7e807f42793`. Embedded source marker equals the exact PR head. QA package identity is `com.topherofit.thf.pulse.qa`, versionCode 51019.
- GPS behavior and limitations are detailed in `GPS_MAP_QUALITY_20261126.md`.
- Compared with the latest canonical branch head at the time of reconciliation, #311 is diverged (11 commits ahead / 26 behind) and GitHub reports it non-mergeable. Its two branch-local recovery/GPS checkpoint files duplicate canonical ReleaseOps paths. Keep Draft; no rebase/rebuild solely for docs/Health drift and no merge before physical P0.

## GPS map/settings handoff — PR #284

- PR [#284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284), Draft/unmerged.
- Current head: `274155eafdfff381009ef5814a621f32b225f1a8`; base SHA: `f596bcf722d5fac810538907ad6180999774bfc3`; 13 changed files; 19 ahead / 176 behind the current canonical line.
- No exact-head CI exists for the current PR head. Run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) validates only historical SHA `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; historical artifact 13707718861 is unavailable (404).
- Overlaps #311 (`ActivityTrackingService.kt`, GPS policy), #93 (`MainActivity.kt`/Manifest), and #216/#224 (shared WebView files). Do not merge wholesale or treat the initial 3fcbe6 head as current.
- Preserve the requested implementation intent—8s/12s Fused-to-framework fallback, one selected framework provider, stop Fused after fallback registration, truthful accuracy/pause UI, unique TopHeroFit User-Agent, OSM caching and explicit Android Location Settings bridge—but validate on a current, isolated head before integration.

## Other current PRs and ownership

| PR | Current state | Decision |
|---|---|---|
| #93 Health services | Draft; head `1cc08cef7dae7f432275fd23960f4390a49db14c`; 12 files; 19 declared scopes vs canonical five; non-mergeable | Hold; narrow scopes and reconcile privacy/Play declarations |
| #216 active-workout resume | Draft; head `1ef915886fdac62c8fe1d5e50505fd354d989ee3`; stacked on #215 | Hold; shared WebView ownership and no exact-head Actions validation |
| #224 active-workout offline demos | Draft; head `cc703baa3cc0e1866e50aafb9a8caad26583fc0a`; stacked on #223 | Hold; source/V8 harness is not native Node/WebView/device acceptance |
| #248 GPS display smoother | Draft; head `67d3b438815fe83ced301551aee43f5a6548c91d`; no production call site | Do not merge unused smoothing or let it change metric credit |
| #213 timed-program RIR | Open exercise handoff | Separate catalog/UI lane; not part of GPS/release integration |
| #160 bilingual cue cleanup | Open content handoff | Separate catalog/content lane; not part of GPS/release integration |

- #307 is closed, not merged, superseded by #311.
- #310 Health non-transitive session-window quarantine is merged at `fad03f360c1d9a474b62239025ff76fde7eeb087`.
- #312 Health unknown-exercise-type fail-closed handling is merged at `85fb3e96f90ca5f7a9eac9072d8301d7f31d55bb`.
- #269 competition backend is merged but provisional `strength_volume_kg_reps` only. No independently verified GPS leaderboard; GPS `rewardEligible=false`; no THF payouts.

## GPS, truthful metrics and anti-cheat boundaries

- Canonical map remains Leaflet in Android WebView with OpenStreetMap-derived raster layers; OpenTopoMap and EOX Sentinel-2 are optional.
- No Google Maps SDK/Rx, Google basemap, billing enablement or new Maps key is required or authorized for this stack.
- `GpsFixGate` is signal admission; `GpsDistanceAccumulator` is the sole distance-credit path. Display smoothing must not alter distance, pace, speed or rewards.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired. Do not add it as a second per-fix filter without a reviewed false-positive policy.
- Completed GPS route history remains in WebView localStorage. No authenticated route-sync endpoint/table or precise-location upload exists. Route backup/sync is a separate design-only gap after #284 validation; require explicit opt-in, retention/deletion semantics and no precise-location upload by default.

## Latest live Google Play readback — 2026-11-26

- Read-only probe [45872277536](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45872277536) completed SUCCESS at 2026-11-26 17:59:45 UTC.
- Artifact 15142793403 ZIP SHA-256 `7e51b333a5da1a8ad6390c4722bf1c49316e19b706e46975c5b283956a1b6e5d`, independently downloaded and rehashed.
- Embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`, independently rehashed.
- Package `com.topherofit.thf.pulse`; Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified.
- Arabic and English listings present; support email `TopHeroFit@gmail.com`.
- `uploadAttempted=false`, `commitAttempted=false`. Probe created and deleted a temporary empty edit; no listing, track, version, upload or commit mutation.
- This readback does not establish physical GPS/background behavior or a source-to-current-Play AAB identity for the newly merged #314 code. Store 51019 remains the previously released candidate.

## Phone and release gates

- Latest Desktop Commander device-list: localhost Offline (last seen about 224 hours before this observation); Samsung SM-A217F app/session state UNKNOWN.
- No ADB, install, launch, force-stop, notification, permission or location-setting action was performed.
- Physical P0 remains BLOCKED_NOT_RUN: stationary drift, measured walk/run/cycle routes, precise/approximate and revoke/regrant, first-fix latency/accuracy, screen-off/background, notification Pause/Resume/Finish, process-death restore without stopped-time credit, crash/ANR/Logcat.
- Owner Google Play/API write permission and GCP Secret Manager signing-key access remain NOT_VERIFIED.
- Next versionCode 51020 remains UNALLOCATED. No new signed AAB. Production remains blocked on physical P0, policy/privacy and release gates.


## PR #284 source-integrity recheck — 2026-11-26

The current PR head `274155eafdfff381009ef5814a621f32b225f1a8` contains a complete 1,146-line `MainActivity.kt`; it was fetched in two bounded ranges and `motionSnapshot()` is present in the final range. The current `app.js` contains the `openLocationSettings()` click bridge, and MainActivity contains the TopHeroFit User-Agent plus `WebSettings.LOAD_DEFAULT`. The allowlisted WebView tile policy covers OSM/OpenTopoMap/EOX HTTPS raster endpoints. This is source inspection only: #284 still has no exact-head CI and no phone P0, and remains Draft/unmerged.
