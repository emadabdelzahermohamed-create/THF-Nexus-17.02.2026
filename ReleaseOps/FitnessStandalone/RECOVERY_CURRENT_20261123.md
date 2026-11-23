# TopHeroFit — Canonical Recovery Checkpoint

**Observed:** 2026-11-23 19:51 Africa/Cairo (17:51:34 UTC)  
**Repository:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`  
**Canonical tip after integration:** `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`

## Source-of-truth boundary

The repository's `RELEASE_CURRENT.json` designates the recovery branch above as canonical. At application head `fe06...`, default `main` was 753 ahead / 180 behind; raw compare at `962660...` was 763 ahead / 180 behind. The ten additional commits are ReleaseOps-only checkpoints. Do not merge these histories automatically.

The canonical branch advanced from `a930448d01649a5bc1a5efba4f163da8c25f2285` through PR #309. Post-merge comparison against tested PR head `83cc98121bdd73a9d88705f9beb80fcfe420ea0e` shows one merge commit ahead and zero changed files.

## Integrated this run

### PR #309 — Health Connect other typed sessions

- Merged as `fe06b2bb98c6b8862fb4ab8493758a6fa3aa75af`.
- Tested PR head: `83cc98121bdd73a9d88705f9beb80fcfe420ea0e`.
- Exact-head workflow [45194352739](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45194352739): Product 83/83, Source Contract 35/35, Backend 29/29, Android Unit 341/341, zero failures and zero ignored.
- Artifact 14828150903 ZIP SHA-256: `9d6938b7fce88e93d59065e10b64ee435420e9d4dc5e311589d750f579305be0`.
- QA APK SHA-256: `c4a3d42418e82a6a23df301e800fd556d47c35979cb323bf4e5a0ada1d590b65`.
- Unsigned validation AAB SHA-256: `9d23056ae9abc9eb90cb8d69ef25717a51d997437109cd637b476eb7f6a180e5`.
- The change preserves raw Health Connect exercise types, deduplicates mirrored non-cardio sessions and quarantines conflicting same-window activity labels. No permissions, release version, signing or Play files changed.
- This is metadata reconciliation, not hardware attestation or proof of physical exercise.

## GPS and map status

### PR #307 — Fused/framework source arbitration

- Draft; branch `agent/codex/gps-fused-fallback-arbitration-20261122-r1`.
- PR head `5326bdef60c5e7e65ff6633767e43ade17675955`; application change `e788ea4b5ac6f539f503fbeb1d9c3f99a2438408`.
- Exact-head run [45132278712](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45132278712): Product 81/81, Source Contract 39/39, Backend 29/29, Android Unit 345/345, zero failures/ignored.
- Artifact 14797923310 ZIP SHA-256: `f3010f85b58670a7fada3de693aa4dd4a1e74f6d3fe8a0c1eed75102d1ce9c9d`.
- Unsigned validation AAB SHA-256: `97e790a850f404746a3c12f9107d1a18aaa2b3842c14a010c3d72b74bba52997`. Its bytes match the earlier e788 build; no new Play artifact was created or uploaded.
- At application head `fe06...`, compare was 9 ahead / 21 behind; raw compare at `962660...` was 9 ahead / 31 behind. The ten extra behind commits are ReleaseOps-only checkpoints, not GPS app changes. Rebase onto the latest canonical branch and rerun exact-head CI before merge.
- The branch-local recovery header still names `f6b124...`, while the PR and exact-head Actions evidence name `5326bdef...`; reconcile that stale checkpoint field.
- Physical P0 remains blocked.

### PR #284 — Open-source map/fallback handoff

- Draft; head `3fcbe6acbb4dc660284c74c8392818996e1de7ee`, original base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`.
- At application head `fe06...`, compare was 19 ahead / 129 behind; raw compare at `962660...` was 19 ahead / 139 behind. The ten extra behind commits are ReleaseOps-only checkpoints. The PR still changes 13 files.
- Historical exact-head run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) succeeded: Product 60/60, Source Contract 38/38, Backend 29/29, Android Unit 223/223, zero failures/ignored.
- Artifact 13707718861 ZIP SHA-256: `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`.
- Unsigned validation AAB SHA-256: `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`.
- The earlier 42694199295 run failed the source contract because the uploaded MainActivity input omitted `motionSnapshot`; the current PR branch tail contains `motionSnapshot` and `openLocationSettings`.
- Do not merge the branch as a whole: `ActivityTrackingService.kt` overlaps #307; `MainActivity.kt` is owned by #93; `app.js` and `index.html` overlap #216/#224. Only consider isolating the settings bridge after those owners release the files and a new exact-head/device test passes.
- Canonical MainActivity is 1,140 lines and does not yet contain `openLocationSettings`.

## Google Play and release

Latest independently rehashed readback remains run 43739661313, attempt 7, observed 2026-11-22 17:56:05 UTC. Artifact 14766395949 SHA-256 `7230b2fa82b21671d9710db75663c4ade78ce4a768974cb8a374301393774bc5`; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.

- Internal: 51019 — Completed.
- Alpha: 51007 — Draft.
- Production: not listed / not verified.
- No fresh readback was produced on 2026-11-23: the probe is workflow-dispatch-only, no dispatch action is exposed here, and Desktop Commander is offline.
- `uploadAttempted=false`; `commitAttempted=false`.
- Next versionCode 51020 remains **UNALLOCATED**. Owner Play/API write permission and GCP signing-key access remain unverified. No new signed AAB exists.

## Phone / physical P0

Desktop Commander `localhost` is offline (last seen 152 hours ago). Samsung SM-A217F is last known as Android 12; current app and session state are unknown. No ADB, install, force-stop, session action or device-wide setting change was attempted.

P0 still required: stationary drift, known-distance walk/run/cycle, precise/approximate transition, first-fix latency/accuracy, screen-off/background continuity, notification Pause/Resume/Finish, process-death recovery, daily-vs-session steps, Health grants/revoke/no-data/error, crash/ANR/logcat.

## Other priority gaps

- Route history remains WebView localStorage `pulse.v2.activities`; no authenticated route endpoint/table or precise-location upload exists. Route sync is design-only and separate from the 1-second local map refresh.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired. Keep `GpsFixGate` as admission and `GpsDistanceAccumulator` as the sole metric-credit path until a unified policy is tested.
- PR #269 competition backend is merged; current metric is `strength_volume_kg_reps`. GPS reward eligibility remains false; no THF payouts.
- Health Connect allowlist remains five scopes. No heart-rate permission or new scope was added.

## Next safe sequence

1. Restore authorized SM-A217F access without touching any existing session; run P0 and preserve raw evidence.
2. Rebase #307 on `fe06b2bb...`, run exact-head CI, then decide merge only after physical P0.
3. Keep #284 Draft; extract only the settings bridge after MainActivity/WebView owners release their files.
4. Continue Health permission/privacy and real-device grant/revoke/no-data verification.
5. Keep route sync opt-in design-only until consent, retention, deletion and authenticated API contracts are complete.
6. Allocate 51020 only after owner API/key prerequisites, exact-head Android CI and physical P0; Internal only after signed-AAB SHA verification and independent Play readback.
