# Fitness Sensor Evidence Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Fitness V2's session-step-only sensor path with a real, battery-aware native motion evidence pipeline that measures steps plus accelerometer/gyroscope activity, exposes evidence to the workout UI, and proves the behavior on the physical Samsung SM-A217F.

**Architecture:** Introduce a pure-Kotlin feature accumulator and session engine behind an Android sensor gateway. `MainActivity` becomes a lifecycle/bridge adapter instead of owning raw sensor logic. The web UI starts/stops native motion sessions and displays native evidence; reward semantics do not change in this phase. This plan implements Phase A of the approved sensor-first spec; Health Connect provenance, evidence fusion/anti-cheat, protected rewards, and exercise-specific verification remain separate follow-on plans.

**Tech Stack:** Kotlin/JVM 17, Android SensorManager, Android API 26–36, JUnit 4.13.2, existing WebView/PulseNative bridge, Gradle 8.11.1, ADB physical-phone QA.

**Spec:** `docs/superpowers/specs/2026-10-21-fitness-sensor-verification-design.md`

## Global Constraints

- Package remains `com.topherofit.thf.pulse`.
- `minSdk` remains 26 and `targetSdk` remains 36.
- Java/Kotlin target remains JVM 17.
- Step Counter/Step Detector are the preferred low-power signals.
- Accelerometer/gyroscope high-rate sampling must be active only during an explicit workout/motion session and stopped when no session is active.
- Production code must not persist continuous raw accelerometer/gyroscope streams; persist compact derived features/evidence only.
- Missing sensors or denied `ACTIVITY_RECOGNITION` must degrade to lower evidence, never fabricate verified motion.
- Manual workout fields remain usable, but Phase A must not promote them into sensor evidence.
- Reward/token/leaderboard trust behavior is unchanged in Phase A; later phases own reward gating.
- Physical gate device is Samsung SM-A217F; a build is not sensor-QA PASS until an observed real step increase and a stationary control are captured on the exact tested APK.

## Review Focus

1. **Step Counter reset/reboot/discontinuity:** a lower raw counter value starts a new segment and never produces a negative or giant step delta. Covered in Task 1 tests.
2. **Missing Step Detector / gyro / accelerometer:** engine reports capability accurately and still produces partial evidence from available sensors. Covered in Task 2 tests.
3. **App pause/resume during an active workout:** high-rate sensors stop while paused, interruption time is tracked, and the same session resumes without double-counting steps. Covered in Task 2 tests.
4. **Stationary false positives:** stationary accelerometer/gyro traces produce near-zero active-motion duration and low local confidence. Covered in Task 1 tests and Task 6 phone control.
5. **Out-of-order/duplicate sensor timestamps:** samples at or before the last accepted timestamp do not inflate duration, peaks, cadence, or detector counts. Covered in Task 1 tests.

---

## File Structure

**Create**

- `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionModels.kt` — immutable sensor capabilities, samples, session state, and `MotionEvidence` data contracts.
- `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionFeatureAccumulator.kt` — deterministic, Android-free feature extraction and evidence digest input.
- `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionSensorGateway.kt` — narrow sensor gateway + listener contract used by the engine.
- `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/AndroidMotionSensorGateway.kt` — `SensorManager` implementation and permission/capability discovery.
- `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionSessionEngine.kt` — session lifecycle, low-power vs active sampling, pause/resume handling, and snapshots.
- `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/MotionFeatureAccumulatorTest.kt` — deterministic feature/reset/stationary/timestamp tests.
- `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/MotionSessionEngineTest.kt` — fake-gateway lifecycle/capability/background tests.
- `fitness-v2/scripts/run_fitness_phone_candidate_51006.sh` — exact build 51006 phone QA launcher.

**Modify**

- `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.kt` — remove direct `SensorEventListener` ownership; integrate engine and bridge APIs.
- `fitness-v2/android/app/src/main/assets/pulse/app.js` — start/stop native sessions and render native motion evidence instead of relying on session-step-only status.
- `fitness-v2/android/app/src/main/assets/pulse/index.html` — add compact live sensor-evidence region to active workout UI.
- `fitness-v2/android/app/src/main/assets/pulse/styles.css` — style evidence chips/status without changing established visual system.
- `fitness-v2/android/app/build.gradle` — bump candidate to versionCode `51006`, versionName `5.0.0-v2-alpha6`.
- `.github/workflows/fitness-v2-android-health.yml` — gate and artifact names for 51006; retain existing unit/lint/APK/AAB/signing gates.
- `fitness-v2/scripts/fitness_phone_qa.sh` — add sensor capability/registration evidence and motion-specific fail-closed checks.

---

### Task 1: Pure Motion Evidence Model and Feature Accumulator

**Files:**
- Create: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionModels.kt`
- Create: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionFeatureAccumulator.kt`
- Test: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/MotionFeatureAccumulatorTest.kt`

**Interfaces:**
- Produces: `SensorCapabilities`, `MotionSensorType`, `MotionEvidence`, and `MotionFeatureAccumulator` for Task 2.
- `MotionFeatureAccumulator` public API:
  - `fun start(sessionId: String, startedAtWallMs: Long, startedAtElapsedNanos: Long, capabilities: SensorCapabilities)`
  - `fun acceptStepCounter(rawCount: Float, elapsedNanos: Long)`
  - `fun acceptStepDetector(elapsedNanos: Long)`
  - `fun acceptAccelerometer(x: Float, y: Float, z: Float, elapsedNanos: Long)`
  - `fun acceptGyroscope(x: Float, y: Float, z: Float, elapsedNanos: Long)`
  - `fun markInterrupted(startedAtElapsedNanos: Long)`
  - `fun markResumed(resumedAtElapsedNanos: Long)`
  - `fun snapshot(endedAtWallMs: Long, endedAtElapsedNanos: Long): MotionEvidence`
- `MotionEvidence` must contain at minimum: session ID, wall/elapsed duration, step delta, detector count, counter reset count, accelerometer/gyro sample counts, magnitude mean/variance/peak for both inertial sensors, active-motion milliseconds, stationary fraction, interruption milliseconds, capabilities, local confidence in `0.0..1.0`, and deterministic evidence digest.

- [ ] **Step 1: Write failing accumulator tests**

Add tests named:
- `stepCounterDeltaAccumulatesAcrossNormalSamples`
- `counterResetStartsNewSegmentWithoutNegativeSteps`
- `duplicateAndOutOfOrderTimestampsAreIgnored`
- `stationaryTraceProducesLowActivityConfidence`
- `movingTraceProducesNonZeroMotionFeatures`
- `interruptionTimeIsExcludedFromActiveDuration`

Key assertions:
- raw counter `100 -> 112` yields `stepDelta == 12`;
- raw counter `500 -> 510 -> 3 -> 8` yields `stepDelta == 15` and `counterResetCount == 1`;
- stationary `{ax=0, ay=0, az≈9.81, gyro≈0}` yields `activeMotionMs` near zero and `localConfidence < 0.25`;
- a deterministic moving trace yields non-zero accel/gyro variance and `localConfidence > stationary confidence`;
- re-sending the same timestamp does not change counts or digest input.

- [ ] **Step 2: Run focused test to verify RED**

Run:
```bash
gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest --tests '*MotionFeatureAccumulatorTest*'
```
Expected: FAIL because motion model/accumulator types do not exist.

- [ ] **Step 3: Implement the motion data contracts and accumulator**

Use double-precision online mean/variance accumulation (Welford-style) for magnitudes; do not retain raw sample arrays. Use `sqrt(x*x+y*y+z*z)` magnitude. Define a conservative first-pass active-motion threshold from acceleration deviation and/or gyro magnitude; keep thresholds constants in `MotionFeatureAccumulator` so tests pin them. Build digest from canonical evidence fields only, using SHA-256; do not include mutable UI/manual values.

- [ ] **Step 4: Run the focused tests to verify GREEN**

Run the same Gradle command.
Expected: all `MotionFeatureAccumulatorTest` tests PASS.

- [ ] **Step 5: Run all Android unit tests**

Run:
```bash
gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest
```
Expected: existing tests plus new accumulator tests PASS.

- [ ] **Step 6: Commit**

```bash
git add fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionModels.kt \
        fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionFeatureAccumulator.kt \
        fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/MotionFeatureAccumulatorTest.kt
git commit -m "feat(fitness): add deterministic motion evidence features"
```

### Task 2: Sensor Gateway and Battery-Aware Motion Session Engine

**Files:**
- Create: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionSensorGateway.kt`
- Create: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/AndroidMotionSensorGateway.kt`
- Create: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionSessionEngine.kt`
- Test: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/MotionSessionEngineTest.kt`

**Interfaces:**
- Consumes: Task 1 `MotionFeatureAccumulator`, `MotionEvidence`, `SensorCapabilities`.
- `MotionSensorGateway` must expose:
  - `fun capabilities(): SensorCapabilities`
  - `fun startLowPower(listener: MotionSensorListener)` — Step Counter + Step Detector only.
  - `fun startActive(listener: MotionSensorListener)` — accelerometer + gyroscope in addition to low-power sensors.
  - `fun stopActive()` — removes only active/high-rate sensor registrations.
  - `fun stopAll()`
- `MotionSessionEngine` must expose:
  - `fun onHostResume()`
  - `fun onHostPause()`
  - `fun startSession(sessionId: String): MotionSessionState`
  - `fun snapshot(): MotionEvidence?`
  - `fun stopSession(): MotionEvidence?`
  - `fun capabilities(): SensorCapabilities`
  - `fun currentState(): MotionSessionState`

- [ ] **Step 1: Write failing engine tests with a fake gateway and fake clock**

Tests:
- `resumeWithoutWorkoutStartsLowPowerOnly`
- `startSessionEnablesActiveSensors`
- `stopSessionReturnsEvidenceAndStopsHighRateSensors`
- `pauseDuringSessionStopsAllSensorsAndMarksInterruption`
- `resumeDuringSessionRestartsActiveSensorsWithoutNewSession`
- `missingGyroStillProducesPartialEvidence`
- `missingStepDetectorStillUsesStepCounter`
- `doubleStartSameSessionIsIdempotent`
- `startDifferentSessionWhileActiveIsRejected`

- [ ] **Step 2: Run engine tests to verify RED**

Run:
```bash
gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest --tests '*MotionSessionEngineTest*'
```
Expected: FAIL because gateway/engine types do not exist.

- [ ] **Step 3: Implement gateway contracts and pure engine lifecycle**

Keep Android `SensorManager` calls exclusively inside `AndroidMotionSensorGateway`. Register Step Counter/Detector with `SENSOR_DELAY_NORMAL`; register accelerometer/gyroscope only while `MotionSessionEngine` is active and host is resumed. The engine must not own an Android `Context` beyond what the gateway already owns.

- [ ] **Step 4: Implement Android sensor mapping and capability discovery**

Map `TYPE_STEP_COUNTER`, `TYPE_STEP_DETECTOR`, `TYPE_ACCELEROMETER`, and `TYPE_GYROSCOPE` into `MotionSensorListener` callbacks using `SensorEvent.timestamp`. Capability flags are true only when the corresponding `Sensor` exists; activity-recognition permission state is reported separately and does not pretend a sensor is absent.

- [ ] **Step 5: Run focused and full unit tests**

Run:
```bash
gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest --tests '*MotionSessionEngineTest*'
gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionSensorGateway.kt \
        fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/AndroidMotionSensorGateway.kt \
        fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionSessionEngine.kt \
        fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/MotionSessionEngineTest.kt
git commit -m "feat(fitness): add battery-aware motion session engine"
```

### Task 3: Replace MainActivity Raw Sensor Ownership with Motion Engine

**Files:**
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.kt`
- Test: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/MotionSessionEngineTest.kt`

**Interfaces:**
- Consumes: Task 2 `MotionSessionEngine`.
- Produces JS bridge methods:
  - `beginMotionSession(sessionId: String): String`
  - `motionSnapshot(): String`
  - `endMotionSession(): String`
- `PulseNative.status()` adds `motionCapabilities` and `motionSession` JSON objects.
- Compatibility methods `beginStepSession()` and `sessionSteps()` remain for one release, but delegate to the engine rather than directly reading `SensorEvent` state.

- [ ] **Step 1: Add a failing source-contract assertion that MainActivity no longer implements SensorEventListener**

Modify `fitness-v2/tests/test_source_contract.py` to assert:
- `MainActivity` does not declare `SensorEventListener`;
- the old fields `absoluteSteps`, `sessionBaseline`, `stepSensor`, and direct `sensorManager.registerListener` calls are absent;
- bridge methods `beginMotionSession`, `motionSnapshot`, and `endMotionSession` exist.

- [ ] **Step 2: Run source contract to verify RED**

Run:
```bash
python fitness-v2/tests/test_source_contract.py
```
Expected: FAIL on the new motion-engine contract.

- [ ] **Step 3: Integrate MotionSessionEngine into MainActivity lifecycle**

Instantiate `AndroidMotionSensorGateway` + `MotionSessionEngine` in `onCreate`. Route `onResume`/`onPause` to engine lifecycle. Keep `ACTIVITY_RECOGNITION` permission request behavior; after grant, call `motionEngine.onHostResume()` so low-power sensors become available immediately.

- [ ] **Step 4: Add JSON serialization helpers for capabilities/evidence/session state**

Serialize only derived fields. Do not expose raw sensor samples. `motionSnapshot()` returns `{available:false}` when no active session rather than a fabricated zero-evidence workout.

- [ ] **Step 5: Make native saveSummary attach native evidence, never trust UI-provided motion evidence**

When `saveSummary` receives JSON, remove any inbound `motionEvidence`/`verification` fields first. If the summary `clientRecordId` matches the most recently ended native session, attach the native `MotionEvidence` JSON and set `measurementSource="SENSOR"`; otherwise set `measurementSource="MANUAL_OR_UNVERIFIED"`. Do not change reward behavior in this task.

- [ ] **Step 6: Run source contract and Android unit tests**

Run:
```bash
python fitness-v2/tests/test_source_contract.py
gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest
```
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.kt \
        fitness-v2/tests/test_source_contract.py
git commit -m "refactor(fitness): route native tracking through motion engine"
```

### Task 4: Start/Stop Native Evidence from Workout UI and Show Live Sensor Status

**Files:**
- Modify: `fitness-v2/android/app/src/main/assets/pulse/app.js`
- Modify: `fitness-v2/android/app/src/main/assets/pulse/index.html`
- Modify: `fitness-v2/android/app/src/main/assets/pulse/styles.css`
- Modify/Test: `fitness-v2/tests/test_source_contract.py`

**Interfaces:**
- Consumes: Task 3 bridge methods.
- UI behavior:
  - workout start calls `beginMotionSession(clientRecordId)`;
  - active workout periodically reads `motionSnapshot()` at a low UI cadence (1 Hz maximum);
  - finish calls `endMotionSession()` before `saveSummary()`;
  - local history displays `Sensor` when native evidence exists, otherwise `Manual / unverified`;
  - displayed live values include steps, detector events, motion state/intensity, and local confidence; no raw vectors are shown.

- [ ] **Step 1: Add failing source-contract checks for bridge usage and evidence labels**

Assert `app.js` references `beginMotionSession`, `motionSnapshot`, `endMotionSession`, `measurementSource`, and does not start a workout using only `beginStepSession`.

- [ ] **Step 2: Run source contract to verify RED**

Run:
```bash
python fitness-v2/tests/test_source_contract.py
```
Expected: FAIL.

- [ ] **Step 3: Wire workout start/finish to the new bridge**

Use the existing `clientRecordId` as native session ID. On finish, parse the returned native evidence and use its `stepDelta` for display/history when present; never replace native measured steps with a user-entered value.

- [ ] **Step 4: Add live evidence UI**

Add one compact region inside the active workout screen with IDs stable enough for ADB UI-dump QA. Use explicit text labels for `Sensor`, current step delta, motion confidence, and capability degradation. Update at most once per second and stop polling when the active workout ends or leaves the screen.

- [ ] **Step 5: Preserve manual-only fields as annotations**

Keep load, RPE/RIR, pain/notes, and unsupported rep entry usable. Do not label those values sensor-verified. History should preserve both measured evidence and manual annotations separately.

- [ ] **Step 6: Run source/product tests**

Run:
```bash
python fitness-v2/tests/test_source_contract.py
python -m unittest discover -s fitness-v2/product/tests -v
gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest
```
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add fitness-v2/android/app/src/main/assets/pulse/app.js \
        fitness-v2/android/app/src/main/assets/pulse/index.html \
        fitness-v2/android/app/src/main/assets/pulse/styles.css \
        fitness-v2/tests/test_source_contract.py
git commit -m "feat(fitness): surface live sensor evidence in workouts"
```

### Task 5: Build 51006 and Strengthen Sensor Phone-QA Harness

**Files:**
- Modify: `fitness-v2/android/app/build.gradle`
- Modify: `.github/workflows/fitness-v2-android-health.yml`
- Modify: `fitness-v2/scripts/fitness_phone_qa.sh`
- Create: `fitness-v2/scripts/run_fitness_phone_candidate_51006.sh`

**Interfaces:**
- Candidate identity: versionCode `51006`, versionName `5.0.0-v2-alpha6`.
- CI artifact name: `fitness-v2-51006-package-gate`.
- Phone QA harness adds `--require-motion-sensors` and writes `sensor_capabilities.txt`, `sensor_registration_before.txt`, and `sensor_registration_active.txt`.

- [ ] **Step 1: Add fail-closed QA checks before changing version/build files**

Extend `fitness_phone_qa.sh` so `--require-motion-sensors` requires physical presence of Step Counter, Step Detector, accelerometer, and gyroscope in `dumpsys sensorservice`, and requires the Fitness package to appear registered for Step Counter while resumed. During an active workout capture, require Fitness package registration for accelerometer and gyroscope as well.

- [ ] **Step 2: Add candidate 51006 runner**

Clone the 51005 runner pattern but require versionCode `51006` and pass `--require-motion-sensors --require-health-connect` to the QA harness.

- [ ] **Step 3: Bump Android version and workflow gate**

Set `versionCode 51006`, `versionName '5.0.0-v2-alpha6'`; update workflow badging assertion and uploaded artifact name to 51006. Keep API 36, signing key SHA-1, lint, unit, offline payload, and AAB signing checks unchanged.

- [ ] **Step 4: Run local verification**

Run:
```bash
bash -n fitness-v2/scripts/fitness_phone_qa.sh
bash -n fitness-v2/scripts/run_fitness_phone_candidate_51006.sh
python fitness-v2/tests/test_source_contract.py
gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
```
Expected: PASS and `app-debug.apk` produced.

- [ ] **Step 5: Commit**

```bash
git add fitness-v2/android/app/build.gradle \
        .github/workflows/fitness-v2-android-health.yml \
        fitness-v2/scripts/fitness_phone_qa.sh \
        fitness-v2/scripts/run_fitness_phone_candidate_51006.sh
git commit -m "build(fitness): gate sensor-first candidate 51006"
```

### Task 6: Physical Samsung SM-A217F Sensor Acceptance

**Files:**
- Create after QA: `fitness-v2/evidence/phone-motion-51006-summary.txt`
- No product-code changes unless QA exposes a defect; defects return to the owning task and receive a fix + new test first.

**Interfaces:**
- Consumes exact debug APK SHA-256 produced by Task 5/CI.
- Produces a text evidence summary with exact APK SHA-256, source SHA, package/version, permission state, detected sensors, stationary control result, walking result, active-session inertial registration, and evidence screenshots/video directory hash.

- [ ] **Step 1: Install the exact 51006 APK and capture identity**

Run the candidate runner against the authorized Samsung SM-A217F ADB serial. Record package, versionCode `51006`, versionName, APK SHA-256, targetSdk 36, and `ACTIVITY_RECOGNITION` grant state.

- [ ] **Step 2: Capture stationary control**

Start a native workout session and leave the phone stationary for at least 30 seconds. Expected: step delta remains 0 or negligible, active-motion fraction remains low, and confidence remains below the moving sample.

- [ ] **Step 3: Capture real walking sample**

With the same exact build, physically carry the phone through a controlled walking sample of at least 20 real steps. This is the only inherently physical action in the gate; if no one is available to move the phone, mark the gate BLOCKED rather than simulating steps. Expected: native `stepDelta` increases materially, Step Detector events are non-zero when the hardware reports them, and local confidence exceeds the stationary control.

- [ ] **Step 4: Prove high-rate sensors are session-scoped**

Capture `dumpsys sensorservice` while the workout is active and after it ends. Expected: Fitness is registered to accelerometer/gyroscope during the active session and is not registered to those high-rate sensors after session end; low-power step sensors may remain registered while the app is resumed.

- [ ] **Step 5: Run crash/ANR and lifecycle resume checks**

Background and resume the app during the session once. Expected: no crash/ANR, session ID remains stable, interruption time increases, no double-counted step jump occurs.

- [ ] **Step 6: Write and commit the evidence summary**

The summary must explicitly state PASS/BLOCKED/FAIL for each acceptance item and link/hash the local evidence bundle. Do not claim `PHYSICAL_SENSOR_QA=PASS` unless the real walking sample passed.

```bash
git add fitness-v2/evidence/phone-motion-51006-summary.txt
git commit -m "test(fitness): record 51006 physical sensor evidence"
```

### Task 7: Phase A Branch Verification and Handoff to Health Provenance Plan

**Files:**
- No new product file required.
- Update plan checkboxes/PR description only if the execution workflow tracks them in git.

**Interfaces:**
- Produces a Phase A result suitable for merge/review and the input state for Phase B Health Connect provenance planning.

- [ ] **Step 1: Run the complete software gate**

Run:
```bash
python -m unittest discover -s fitness-v2/product/tests -v
python fitness-v2/tests/test_source_contract.py
python -m unittest discover -s fitness-v2/backend/tests -v
gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest :app:lintDebug :app:assembleDebug :app:bundleRelease
```
Expected: PASS.

- [ ] **Step 2: Verify GitHub Actions on the exact branch head**

Expected: `Fitness V2 Android Health Gate` succeeds and uploads `fitness-v2-51006-package-gate` for that exact SHA.

- [ ] **Step 3: Verify evidence gate**

Expected: `phone-motion-51006-summary.txt` proves physical walking + stationary control. If physical movement was unavailable, keep the PR explicitly BLOCKED on phone motion rather than merging as sensor-complete.

- [ ] **Step 4: Request whole-branch review**

Review focus: lifecycle leaks, sensor battery behavior, false evidence promotion, timestamp/counter discontinuities, and bridge trust boundary.

- [ ] **Step 5: Merge only after review + CI + physical sensor evidence**

After merge, Phase B gets its own implementation plan for Health Connect record-level provenance and truthful provider/permissions/read/verified states.
