# Fitness Trust Core + Health UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Fitness 51008 a green, evidence-carrying Trust Core candidate before any new Google Play upload.

**Architecture:** Keep raw Health Connect provenance in the Android repository, classify each record with one pure policy, aggregate only eligible evidence, expose an explicit health-sync state to the WebView, and keep the Play 51007 gate pinned until 51008 passes CI + phone QA. Competition/reward logic consumes verified evidence only.

**Tech Stack:** Kotlin/AndroidX Health Connect, JUnit, Python source/backend contracts, GitHub Actions, existing HMAC partner-claim backend.

**Spec:** `docs/superpowers/specs/2026-10-22-topherofit-growth-platform-design.md` on `spec/fitness-next-architecture-20261022` (approved 2026-10-23).

## Global Constraints
- Trust Core and anti-cheat precede competitions, rewards, gym features and visual expansion.
- Do not upload 51008 to Google Play until source/backend/unit/lint/build gates and physical phone QA are green.
- Read permissions are required for sync; write permission is optional and must not block read-only Health Connect use.
- Manual/unknown/self-authored evidence must never become verified reward evidence.
- Raw health/precise-location evidence remains off-chain.
- Existing 51007 Play Internal workflow stays pinned to 51007 until an explicit 51008 promotion task is green.

## Review Focus
- Same Health record appearing twice must not double-count rewards.
- Self-authored THF Health records must be excluded from verified rewards.
- Manual/unknown recording method must remain unverified even if the origin package is external.
- Connected Health with zero records must be distinguishable from permission failure and from unverified-only records.
- Revoked permission or stale evidence must fail closed for competitions/rewards.

---

### Task 1: Align 51008 candidate contract without accidentally promoting Play

**Files:**
- Modify: `fitness-v2/tests/test_source_contract.py`
- Test: `fitness-v2/tests/test_source_contract.py`

**Interfaces:**
- Consumes: current `versionCode 51008`, `fitness-sensor-candidate.yml`, pinned 51007 Play workflows.
- Produces: source contract proving 51008 is a build candidate while Play promotion remains 51007-only.

- [ ] Replace the stale test that requires `build.gradle` to remain 51007 with assertions that build candidate is 51008 and Play gate remains explicitly 51007.
- [ ] Run `python fitness-v2/tests/test_source_contract.py`; expected PASS.
- [ ] Commit source-contract correction.

### Task 2: Implement Health record identity + authoritative provenance policy

**Files:**
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/WorkoutIdentity.kt`
- Create: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/HealthRecordEvidencePolicy.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/HealthConnectRepository.kt`
- Modify: `fitness-v2/tests/test_source_contract.py`
- Test: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/HealthConnectProvenanceTest.kt`

**Interfaces:**
- Produces: `WorkoutIdentity.stableHealthRecordKey(...)`; `HealthRecordEvidencePolicy.assess(...) -> ActivityIntegrityResult`.

- [ ] Add source-contract assertions for the missing production policy symbols and run to observe RED.
- [ ] Implement stable deterministic Health record key from origin/record/client/version/time.
- [ ] Implement pure policy: self-authored => REJECTED; manual/unknown => MANUAL; external active/automatic => VERIFIED; external unresolved => SUPPORTED/MANUAL according to recording method.
- [ ] Refactor `HealthConnectRepository` to use the single policy for `verifiedForRewards/reason` and stable dedup key.
- [ ] Run Python source contract; expected PASS. Android JUnit is verified in CI.
- [ ] Commit provenance implementation.

### Task 3: Separate read permission from optional write permission

**Files:**
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/HealthConnectRepository.kt`
- Modify/Test: `fitness-v2/tests/test_source_contract.py`

**Interfaces:**
- Produces: default connect/sync path requests `READ_PERMISSIONS`; save-to-Health action requests `WRITE_PERMISSIONS` only when needed.

- [ ] Write failing source-contract assertions for read-only default connect path.
- [ ] Implement separate launchers/permission checks without weakening write-before-save guard.
- [ ] Run source contract; expected PASS.
- [ ] Commit permission separation.

### Task 4: Add explicit Health UX state classifier and provenance summary

**Files:**
- Create: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/HealthUxState.kt`
- Create: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/HealthUxStateTest.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.kt`
- Modify: `fitness-v2/android/app/src/main/assets/pulse/app.js`
- Modify: `fitness-v2/android/app/src/main/assets/pulse/index.html`

**Interfaces:**
- Produces states: `UNAVAILABLE`, `PROVIDER_UPDATE_REQUIRED`, `PERMISSION_REQUIRED`, `READY_UNSYNCED`, `SYNCING`, `SYNCED_VERIFIED`, `SYNCED_NO_RECORDS`, `SYNCED_UNVERIFIED_ONLY`, `RATE_LIMITED`, `ERROR`.

- [ ] Write Kotlin unit tests for state transitions.
- [ ] Implement pure classifier and include state + verified/excluded/dedup counts in native payload.
- [ ] Render clear Arabic/English connected/no-data/unverified/verified messages; never show “no data” for a permission/error state.
- [ ] Run source contracts and CI unit tests.
- [ ] Commit UX state implementation.

### Task 5: Strengthen reward/competition evidence gate

**Files:**
- Modify: `fitness-v2/backend/reward_connector.py`
- Modify: `fitness-v2/backend/tests/test_reward_connector.py`

**Interfaces:**
- Consumes: verified provenance score/status.
- Produces: fail-closed reward eligibility with replay/idempotency guard.

- [ ] Add failing tests for stale/replayed/non-verified evidence.
- [ ] Implement minimum verified evidence + nonce/replay validation without coupling game currency to THF Token.
- [ ] Run backend tests; expected PASS.
- [ ] Commit reward gate.

### Task 6: CI + physical phone gate + Play decision

**Files:**
- Modify only if needed: `.github/workflows/fitness-sensor-candidate.yml`, phone QA scripts.

**Interfaces:**
- Consumes: Tasks 1–5.
- Produces: CI run URL/SHA, physical phone evidence, explicit publish/no-publish decision.

- [ ] Push branch and require `Fitness Sensor Candidate Build` green at exact SHA.
- [ ] Run phone QA with motion sensors + Health Connect + Samsung Health origin evidence.
- [ ] If both green, create/promote an exact 51008 package gate and upload to Play Internal; otherwise keep 51007 as latest published Internal and record blocker.
