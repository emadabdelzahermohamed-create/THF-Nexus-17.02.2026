# Fitness 51012 candidate identity and phone-QA gate — 2026-10-25

## Scope

Physical-phone QA lane for `com.topherofit.thf.pulse`. This checkpoint records a newly built exact candidate and the current device gate. It does not claim phone, Google Play Internal promotion, or Production acceptance.

## Exact candidate

- Canonical source branch: `agent/codex/fitness-recovery/20261023`
- Source SHA: `cb425fef23b8541499acb02cecd8b86312b0eb34`
- Source change: merge of PR #87 (keyboard focus visibility)
- Workflow: Fitness Activity Candidate Build
- Run: `40163572486` — completed / success
- Artifact: `12586864799`
- Artifact name: `fitness-activity-candidate-51012`
- Artifact archive size: `37506227` bytes
- Artifact archive SHA-256: `ac0adffe4f56787da049e69b4deae30269e59a0e68a8c2bc82b11edbac624279`
- Version code recorded by the artifact: `51012`
- Debug APK SHA-256: `a8d6a6b2b987134eae80da7f43081117b1f519a3bb9505f757e0547c58ab6c40`
- Release AAB SHA-256: `eae15bec8d0b38d63c23531a3aa6113db9e4896be5d6da9e192a405f34bb6479`

The workflow log ends with `BUILD SUCCESSFUL in 2m 2s` and includes unit tests, lint, debug APK assembly, and release bundle generation. These are build gates only.

## Device observation

A single bounded read-only ADB check returned:

```text
List of devices attached

error: no devices/emulators found
```

No reconnect loop, install, launch, data clearing, or interaction was attempted. The user's workout state and phone data were not touched.

## Release truth

- The earlier signed 51012 Play Internal artifact remains separately evidenced from source `29bfe57d58b84a5391e201120888d053f54ed055`, build run `40125830819`, artifact `12572602451`, promotion run `40126227388`, signed AAB SHA-256 `c5ae818b45d9775b1850dae9fb36f8c211ac6b9141c4117f17d85da54e56a374`.
- This newer source candidate `cb425fef...` has not been installed on the phone and has not been promoted to Play.
- No Phone PASS and no Production PASS.

## Remaining physical gates

When ADB becomes available and this exact APK remains the newest candidate:

1. Confirm package/version and installed artifact identity.
2. Install/upgrade without clearing user data.
3. Verify collapsed and expanded ongoing notification metrics plus Stop.
4. Verify Home and screen-off continuity without interrupting an active workout.
5. Verify Health Connect provenance and voice where feasible.
6. Capture logcat/crash/ANR and screenshots only where useful.

If a newer source/artifact exists first, supersede this candidate and do not spend a run testing stale bytes.


## Bounded physical recheck — 2026-10-25 15:11 Cairo

A single read-only probe found the physical Samsung SM-A217F connected at `192.168.8.6:37319`, awake and not keyguard-restricted. The canonical branch still resolves to `cb425fef23b8541499acb02cecd8b86312b0eb34`.

The phone still has the Play-installed older candidate:

- package: `com.topherofit.thf.pulse`
- versionCode: `51010`
- versionName: `5.0.0-v2-alpha10`
- targetSdk: `36`
- installer: `com.android.vending`

A real `ActivityTrackingService` session was active: `isForeground=true`, `startRequested=true`, with an ongoing low-importance notification and one visible `إيقاف` action. The notification text was the older generic tracking copy, not the newer 51012 metric layout. Another non-THF app was foreground, which establishes active owner use while tracking continues.

Because a real workout/tracking session was in progress, QA deliberately did not install/upgrade, launch THF, expand/tap the notification, press Stop, change permissions, turn the screen off, clear data, or collect screenshots. This preserves the owner's live session. The observation is not a defect against the uninstalled `cb425fef...` candidate and does not close any 51012 physical gate.

### Next safe action

After the existing tracking service is no longer active, first re-confirm that `cb425fef...` and artifact `12586864799` remain the newest exact candidate. Only then perform the in-place upgrade and the smallest pending notification/Stop/Home/screen-off regression. Do not interrupt the current session and do not claim Phone PASS before that evidence.

## Safe preflight checkpoint — 2026-10-25 20:53 Cairo

The authorized remote Termux host was online and contained ADB, but one bounded `adb devices -l` inventory returned an empty device list. No reconnect, stale IP/port reuse, install, launch, force-stop, wake/unlock, permission change, notification action, or data operation followed. The phone candidate therefore remains physically unverified.

Canonical remains `agent/codex/fitness-recovery/20261023` at `17e84b6b16a99fbb624edd79792bbef95e7c5415`. The newest exact standalone APK candidate recorded for phone QA remains source `cb425fef23b8541499acb02cecd8b86312b0eb34`, run `40163572486`, artifact `12586864799`, version code `51012`. It is not installed or phone-tested. Separately, the earlier signed 51012 artifact from source `29bfe57d...` remains verified committed to Play Internal; this observation does not change that release truth or prove Play propagation.

### Reusable safety gate

`fitness-v2/scripts/fitness_phone_preflight.sh` now defines a read-only gate for future device windows. It performs exactly one inventory call and exits successfully only with `qa_state=READY_FOR_MANUAL_QA`. It fails closed for:

- no authorized device or multiple devices;
- a requested serial that is unavailable;
- a non-interactive or keyguard-locked device;
- a missing Fitness package;
- an active `ActivityTrackingService` session.

The gate never reconnects, pairs, wakes, unlocks, installs, launches, stops, taps, changes permissions, or clears data. A ready result permits only a separate deliberate QA action; it does not claim Phone PASS.

Verification: `python3 -m unittest discover -s fitness-v2/tests -v` passed 37 tests, including eight fake-ADB preflight cases. `bash -n fitness-v2/scripts/fitness_phone_preflight.sh` and `git diff --check` passed. ShellCheck was not installed in the execution environment.

## Fail-closed parser repair — 2026-10-25 21:18 Cairo

A synthetic read-only reproduction showed that a successful but empty `dumpsys window` response could previously reach `READY_FOR_MANUAL_QA`. The preflight now requires a recognized explicit unlocked indicator after rejecting every recognized locked indicator. Empty or unrecognized window output returns `DEVICE_LOCK_STATE_UNKNOWN` before package/service queries.

The same boundary was applied to tracking-service inspection: an empty successful response returns `SERVICE_STATE_UNKNOWN`; only a recognized Activity Manager services response without active flags can proceed. These are QA-harness safety results, not physical-device or app-candidate results. No phone operation occurred.

TDD evidence: both new regressions failed against the prior script by returning exit `0`; after the minimal parser repair, all 10 preflight cases pass. The complete Fitness Python suite now passes 39 tests; `bash -n` and `git diff --check` pass.
