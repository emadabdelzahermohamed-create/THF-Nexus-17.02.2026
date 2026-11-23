# TopHeroFit — Canonical Recovery Checkpoint

**Observed:** 2026-11-23 20:33 Africa/Cairo (18:33:03 UTC)  
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
- Current exact PR head: `923a951a304d1c8b2210539be83f07c8accb4371`, directly based on canonical ReleaseOps tip `54d6266c3c8bc469a339a2e1db59734b0ecc8908`.
- Application scope is exactly four GPS-owned files: `ActivityLocationFallbackPolicy.kt`, `ActivityTrackingService.kt`, focused Kotlin tests and `test_source_contract.py`. The PR contains no stale ReleaseOps documents.
- Exact-head run [45238807995](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/45238807995): Product 83/83, Source Contract 39/39, Backend 29/29, Android Unit 347/347, zero failures/ignored; API 36, Kotlin/Gradle, lint and APK/AAB validation PASS.
- Lint: 0 errors, 11 warnings, 1 hint. Gradle BUILD SUCCESSFUL in 3m09s.
- Artifact 14851146115 independently downloaded/rehashed: ZIP SHA-256 `d8e716b24d085b65517354955483b0828c9eee1863b232129acc5a77e3389d8b`; embedded source marker exactly `923a951a304d1c8b2210539be83f07c8accb4371`; QA APK SHA-256 `b26f62bed569b6a27c1c9fd83a3afa85513b3a89ab42418e7fc0ee7e21384739`; unsigned validation AAB SHA-256 `8339981e7fc59f3bbab0ab5c8d4b0b659048a08b9cddd39389cedebc6e973ee0`. `jarsigner` confirms unsigned.
- The new arbitration passes both elapsed-realtime timestamps and rejects an older or equal Fused fix when the current framework fix is fresh. After promotion, older/equal points in a batched Fused result are discarded; only later accepted points are processed in monotonic order. Source transitions reset the live accumulator without crediting the transition.
- First rebased attempt `ecfe9adb...` failed only because the source-contract test still expected the old local variable name; it produced no artifact and did not reach Android build. The assertion was corrected in `923a951a...`; the exact-head run above passed.
- The PR is 2 commits ahead / 0 behind canonical tip `54d6266c...`, with no shared-file overlap. Physical P0 remains BLOCKED_NOT_RUN; keep Draft/unmerged. No signed release, version allocation or Play mutation.

### PR #284 — Open-source map/fallback handoff

- Draft; current head `274155eafdfff381009ef5814a621f32b225f1a8`; original base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`.
- Current comparison against canonical tip `54d6266c3c8bc469a339a2e1db59734b0ecc8908`: 19 ahead / 143 behind; 13 changed files. The supplied `3fcbe6ac...` is the historical head validated by the old run, not the current PR head.
- Historical exact-head run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) succeeded on `3fcbe6acbb4dc660284c74c8392818996e1de7ee`: Product 60/60, Source Contract 38/38, Backend 29/29, Android Unit 223/223, zero failures/ignored.
- Historical artifact 13707718861 was downloaded and independently rehashed: ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`; embedded source marker exactly `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; unsigned validation AAB SHA-256 `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`.
- Run 42694199295 failed the source contract because the uploaded MainActivity input was truncated and omitted `motionSnapshot`; it produced no artifact. The current PR head's MainActivity is 1,146 lines and contains both `motionSnapshot` and `openLocationSettings`. Canonical MainActivity is 1,140 lines, contains `motionSnapshot`, and does not yet contain `openLocationSettings`.
- No exact-head CI exists for current PR head `274155e...`. Do not merge the branch as a whole: `ActivityTrackingService.kt` overlaps #307; `MainActivity.kt` is owned by #93; `app.js` and `index.html` overlap #216/#224. The settings bridge is only a future isolated extraction after those owners release the files and exact-head/device validation passes.
- Keep Draft/unmerged. No Maps SDK, Billing, key, version, signing or Play changes.

## Google Play and release

Latest independently rehashed readback remains run 43739661313, attempt 7, observed 2026-11-22 17:56:05 UTC. Artifact 14766395949 SHA-256 `7230b2fa82b21671d9710db75663c4ade78ce4a768974cb8a374301393774bc5`; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.

- Internal: 51019 — Completed.
- Alpha: 51007 — Draft.
- Production: not listed / not verified.
- No fresh readback was produced on 2026-11-23: the probe is workflow-dispatch-only, no dispatch action is exposed here, and Desktop Commander is offline.
- `uploadAttempted=false`; `commitAttempted=false`.
- Next versionCode 51020 remains **UNALLOCATED**. Owner Play/API write permission and GCP signing-key access remain unverified. No new signed AAB exists.

## Phone / physical P0

Latest read-only Desktop Commander device-list check still reports `localhost` OFFLINE (last seen about 152 hours ago); current handset/app/session state is unknown. No ADB or session action was attempted. Samsung SM-A217F is last known as Android 12; current app and session state are unknown. No ADB, install, force-stop, session action or device-wide setting change was attempted.

P0 still required: stationary drift, known-distance walk/run/cycle, precise/approximate transition, first-fix latency/accuracy, screen-off/background continuity, notification Pause/Resume/Finish, process-death recovery, daily-vs-session steps, Health grants/revoke/no-data/error, crash/ANR/logcat.

## Other priority gaps

- Route history remains WebView localStorage `pulse.v2.activities`; no authenticated route endpoint/table or precise-location upload exists. Route sync is design-only and separate from the 1-second local map refresh.
- `ActivityEvidenceAnomalyPolicy.assessSegment()` remains tested but unwired. Keep `GpsFixGate` as admission and `GpsDistanceAccumulator` as the sole metric-credit path until a unified policy is tested.
- PR #269 competition backend is merged; current metric is `strength_volume_kg_reps`. GPS reward eligibility remains false; no THF payouts.
- Health Connect allowlist remains five scopes. No heart-rate permission or new scope was added.

## Next safe sequence

1. Restore authorized SM-A217F access without touching any existing session; run P0 and preserve raw evidence.
2. PR #307 is now rebased on canonical tip `54d6266c...` and exact-head CI passes; keep Draft until physical P0 is complete, then re-check the current base/head before any merge decision.
3. Keep #284 Draft; extract only the settings bridge after MainActivity/WebView owners release their files.
4. Continue Health permission/privacy and real-device grant/revoke/no-data verification.
5. Keep route sync opt-in design-only until consent, retention, deletion and authenticated API contracts are complete.
6. Allocate 51020 only after owner API/key prerequisites, exact-head Android CI and physical P0; Internal only after signed-AAB SHA verification and independent Play readback.
