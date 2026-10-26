# Fitness Release 51015 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate every safe post-51014 Fitness delta, fix false pre-movement counting and in-app session reset, then publish the exact verified candidate to Google Play Internal.

**Architecture:** Keep 51014 as rollback truth. Merge disjoint tested worker branches onto one isolated release branch, then add a small native truth-state layer so an activity is ARMED until measured movement activates it. Preserve ARMED/ACTIVE state through the existing process-death checkpoint and make repeated UI entry resume the live session instead of starting a new one.

**Tech Stack:** Kotlin/Android, WebView JavaScript/CSS, Python unittest product/source/backend gates, GitHub Actions, Android Publisher.

**Spec:** `ReleaseOps/FitnessStandalone/RECOVERY_20261023.md`

## Global Constraints

- Package remains `com.topherofit.thf.pulse`; targetSdk remains 36.
- New release must use versionCode greater than 51014.
- PR #98 broad Health expansion stays HOLD; no undeclared Health permissions enter this release.
- No Production claim without physical/runtime and policy gates; this plan targets Google Play Internal.
- No distance, calories, pace, session steps, or visible route before measured movement activates the session.
- An active activity session may not be reset by ordinary in-app navigation or re-entering the activity screen.
- TDD first for new behavior; all source/product/backend and Android build gates must pass before Play upload.

## Review Focus

- Stationary GPS drift must not create visible distance/calories/route before activation.
- Re-entering the same or another activity tile while a session is live must resume, not reset/switch it.
- ARMED and ACTIVE state must survive process-death checkpoint restore without inflating elapsed time.
- 51014 checkpoint compatibility must remain safe during in-place update.
- Held Health permissions must not leak from PR #98.

---

### Task 1: Integrate safe post-51014 worker deltas

**Files:** Merge PR branches #103-#113 except held #98; resolve only evidence-backed conflicts.

- [ ] Merge the clean worker branches into this isolated release branch.
- [ ] Run `python3 -m unittest discover -s fitness-v2/tests -v`.
- [ ] Run `python3 -m unittest discover -s fitness-v2/product/tests -v`.
- [ ] Run `python3 -m unittest discover -s fitness-v2/backend/tests -v`.
- [ ] Confirm the manifest has no new broad Health permissions from PR #98.

### Task 2: Make session start truthful and navigation-safe

**Files:**
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/ActivityTrackingService.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/ActivitySessionCheckpoint.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/ActivityMetrics.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.kt`
- Modify: `fitness-v2/android/app/src/main/assets/pulse/app.js`
- Test: Android unit tests plus product contract tests.

- [ ] Write failing tests proving ARMED snapshots expose zero elapsed/distance/steps/calories/pace/route while retaining GPS quality evidence.
- [ ] Run the focused tests and verify RED for missing ARMED behavior.
- [ ] Implement ARMED→ACTIVE integration using `ActivityActivationGate`; set activation timestamps only when measured motion qualifies.
- [ ] Write failing checkpoint tests for ARMED/ACTIVE round-trip and backward-compatible v1 restore.
- [ ] Implement checkpoint v2 with phase/activation timestamps and downtime adjustment.
- [ ] Write a failing product/native contract proving re-entering activity while a session is live resumes instead of calling a new start/reset.
- [ ] Implement the minimal resume guard in the WebView bridge/UI and native service.
- [ ] Run focused tests, then all source/product/backend suites.

### Task 3: Allocate and verify exact release candidate

**Files:** Release/version/workflow metadata only after Task 2 is green.

- [ ] Allocate unique versionCode 51015 and corresponding versionName.
- [ ] Run `git diff --check` and verify held Health scope remains excluded.
- [ ] Push the exact release branch and trigger/reuse the Fitness Sensor Candidate Build on that exact SHA.
- [ ] Require Android unit tests, lint, APK and AAB to pass; record run/artifact hashes.

### Task 4: Publish exact artifact to Google Play Internal

- [ ] Promote only the exact successful 51015 AAB using the existing signed promotion workflow.
- [ ] Independently read back Android Publisher Internal track and require versionCode 51015 with completed status.
- [ ] Update canonical recovery evidence with exact SHA/build/promotion/readback IDs.
- [ ] Keep Production fail-closed until physical phone and Health/policy gates pass.
