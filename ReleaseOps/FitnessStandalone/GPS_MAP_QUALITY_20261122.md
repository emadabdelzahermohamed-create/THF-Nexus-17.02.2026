# TopHeroFit — GPS / Maps quality checkpoint (2026-11-22)

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical application merge: `0b2b52d204fc94944a077a383db7c5cb785c9147`.
Canonical branch tip before this documentation checkpoint: `6a5a9f470c4aa165733f86d958d7651f55e2aed7`.

## Status

- Canonical GPS engine PR #303 is merged.
- GPS source-arbitration PR #307 is Draft/open and unmerged.
- Legacy map/UI PR #284 remains stale/Draft; do not merge.
- Exact-head CI for corrected PR #307 head `45b27cc6a04b48931291e821efc85e76569965fe` passed in run 45052702946.
- Physical P0 remains BLOCKED_NOT_RUN. No phone/GPS accuracy/route/background-session PASS is claimed.

## Fused/framework arbitration correction

The previous #307 candidate registered the framework fallback and then incremented `locationRequestGeneration`, cleared `fusedLocationCallback`, and removed the Fused callback. That made its new Fused recovery branch unreachable while the fallback was active.

The corrected head keeps the Fused callback subscribed while a framework provider is active. The Fused callback is still gated by session mode, pause state, callback generation, `GpsFixGate`, freshness and the accuracy arbitration policy. It may take source ownership only when the candidate is valid and at least as accurate as a fresh framework fix, or when the framework fix is missing/stale. Promotion removes the current framework listener and resets only the live source anchor; it does not credit the source switch as distance. Pause, Stop and session replacement continue to invalidate the callback generation and remove the Fused callback in `unregisterActivitySources()`.

A new source-contract regression verifies:
- Successful framework fallback registration does not increment the Fused lifecycle generation.
- It does not clear or remove the active Fused callback.
- Lifecycle teardown still increments the generation and removes the callback.
- Existing promotion checks continue to remove the framework listener before Fused resumes metric ownership.

## Exact-head validation

Run: [45052702946](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45052702946) — SUCCESS on exact source SHA `45b27cc6a04b48931291e821efc85e76569965fe`.

| Suite | Result |
|---|---:|
| Product | 81/81 |
| Source contract | 37/37 |
| Backend | 29/29 |
| Android unit | 342/342 |
| Android failures / ignored | 0 / 0 |
| Android API 36 | PASS |
| Kotlin / Gradle | PASS |
| Lint | 0 errors, 11 warnings, 1 hint |

Gradle BUILD SUCCESSFUL in 2m42s.

Artifact 14766143584, downloaded and independently rehashed:
- ZIP SHA-256: `e7b8d49d38ab6f1389488396a2c3ba33819c0fb93122994d7ac0ce63543a18a3`
- QA APK SHA-256: `dc1bf863e2a88100de6f6a649672d4f3a0edfad2de547902bc534074fdcbb041`
- Unsigned validation AAB SHA-256: `74541210b5ed7775aad70c20948468e57da22e169906f237303fffad6780d6cc`
- QA package `com.topherofit.thf.pulse.qa`; versionCode 51019; versionName `5.0.0-v2-alpha19-debug`.
- `jarsigner` reports no manifest; the AAB is unsigned. It is not a release artifact and was not uploaded.

## Current map stack

The canonical map remains Leaflet with OpenStreetMap streets, OpenTopoMap terrain and EOX Sentinel-2 cloudless raster imagery. Current UI updates are local WebView state; map rendering/cache behavior does not prove offline map coverage. No Google Maps SDK, Rx wrapper, Billing configuration or Maps key was added.

## Physical P0 — BLOCKED_NOT_RUN

Latest Desktop Commander device-list check on 2026-11-22 returned localhost OFFLINE (last seen approximately 117 hours earlier). Last known handset: Samsung SM-A217F / Android 12. Current app and session state are unknown. No ADB command, install, launch, force-stop, notification action, location-setting change or activity-data read was attempted.

Required before merge/release:
1. Stationary drift with screen on/off for a measured 60-second interval.
2. Outdoor walk/run/cycle against a measured reference route.
3. Fine-to-coarse permission downgrade and source-switch behavior.
4. First-fix latency and truthful provider/accuracy display.
5. In-app navigation, background, screen-off and task-removal continuity.
6. Notification Pause/Resume/Finish actions.
7. Process-death restore without downtime credit.
8. Crash/ANR/logcat review.

## Separate route-sync gap

Completed GPS routes remain in WebView localStorage. The existing authenticated workout sync stores workout/set metadata; no authenticated route endpoint/table/upload path exists. The 1-second map refresh is local and is not route backup. Route sync remains design-only until explicit per-session precise-location consent, retention, revocation, deletion and account-deletion readback are implemented and tested. No precise location is uploaded by default.

## Release boundary

Latest read-only Play readback: 2026-11-22 17:56:05 UTC, run 43739661313 attempt 7. Internal 51019 Completed; Alpha 51007 Draft; Production not listed/not verified. No upload or commit attempted. VersionCode 51020 remains unallocated. Owner Play/API write access and GCP signing-key access remain unverified. No signed AAB or production promotion is authorized.
