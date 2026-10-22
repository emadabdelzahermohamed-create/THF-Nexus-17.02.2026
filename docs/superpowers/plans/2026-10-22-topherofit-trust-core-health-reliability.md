# TopHeroFit Trust Core & Health Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the next TopHeroFit Android candidate with explicit activity provenance/integrity classes, reliable Health Connect sync states, stronger anti-cheat, and server-authoritative reward eligibility.

**Architecture:** Extend the existing 51007 Health Connect and motion foundation instead of replacing it. Android normalizes provider/sensor/manual evidence into one integrity model; Health UI exposes deterministic sync states; backend re-validates reward-bearing evidence and replay/idempotency. No client-local result can authorize a token/treasury transfer.

**Tech Stack:** Kotlin/Android API 36, AndroidX Health Connect, Android sensors, WebView asset UI, Python backend/unittest, GitHub Actions/Google Play Internal.

**Spec:** `docs/superpowers/specs/2026-10-22-topherofit-growth-platform-design.md`

## Global Constraints

- Canonical implementation base is `origin/release/fitness-51007-20261022` until superseded by a reviewed newer Fitness release branch.
- Package stays `com.topherofit.thf.pulse`; target SDK stays 36.
- Manual/self-authored/duplicated/replayed/implausible evidence is never reward-eligible.
- Health permissions are minimum-scope and revoked/missing permissions never render as successful sync.
- Internal Google Play upload follows every green candidate; Closed/Production remain policy/device gated.
- No secret, wallet key, signing material, OTP, password, or long-lived credential enters Git.

## Review Focus

- Samsung/Health Connect returns zero records after permission grant: UI must show `NO_RECORDS`, not a generic success or error.
- Permission is revoked between two reads: next read must become `PERMISSION_NEEDED`, and stale data must be visibly marked.
- Same provider record arrives twice or through two adapters: canonical identity must deduplicate it without collapsing unrelated sessions.
- Device sensor evidence has non-finite values or non-monotonic timestamps: classify/reject before it can influence verified totals.
- Reward claim is replayed or originates from THF's own Health write: backend must reject deterministically and idempotently.

---

### Task 1: Shared activity provenance and integrity model

**Files:**
- Create: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/ActivityIntegrity.kt`
- Create: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/ActivityIntegrityTest.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionModels.kt`

**Interfaces:**
- Produces: `enum class IntegrityClass { VERIFIED, SUPPORTED, MANUAL, REJECTED }`, `ActivityProvenance`, and `ActivityIntegrityClassifier.classify(...)`.
- Consumes: existing motion/session timestamps and source identities.

- [ ] **Step 1: Write failing integrity classification tests** for verified provider evidence, manual evidence, duplicate record, self-authored record, non-finite metrics, implausible speed/cadence, and non-monotonic sensor time.
- [ ] **Step 2: Run** `gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest --tests '*ActivityIntegrityTest'` and verify RED for missing classes/behavior.
- [ ] **Step 3: Implement minimal model/classifier** in `ActivityIntegrity.kt`; extend motion model only with the source fields required by the tests.
- [ ] **Step 4: Re-run the focused test and then** `gradle --no-daemon -p fitness-v2/android :app:testDebugUnitTest`; both must PASS.
- [ ] **Step 5: Commit** `feat(fitness): add unified activity integrity classification`.

### Task 2: Health Connect provenance and canonical deduplication

**Files:**
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/HealthConnectRepository.kt`
- Create: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/HealthConnectProvenanceTest.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/WorkoutIdentity.kt`
- Modify: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/WorkoutIdentityTest.kt`

**Interfaces:**
- Consumes: `ActivityProvenance` and `IntegrityClass` from Task 1.
- Produces: stable canonical provider record keys and normalized Health evidence that distinguishes THF-authored writes from external providers.

- [ ] **Step 1: Write failing tests** proving stable identity for the same provider record, separation of unrelated records, and self-authored THF records being non-reward-eligible.
- [ ] **Step 2: Run focused tests** and verify RED from missing provenance/dedupe behavior.
- [ ] **Step 3: Implement provider/device/record identity extraction and canonical key generation** without requesting new Health permissions.
- [ ] **Step 4: Run focused + full Android unit suite** and verify PASS.
- [ ] **Step 5: Commit** `feat(fitness): preserve Health Connect record provenance`.

### Task 3: Explicit Health sync state machine and user-facing states

**Files:**
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/HealthSyncGate.kt`
- Modify: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/HealthSyncGateTest.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.kt`
- Modify: `fitness-v2/android/app/src/main/assets/pulse/app.js`
- Modify: `fitness-v2/tests/test_source_contract.py`

**Interfaces:**
- Produces: deterministic states `CONNECTED`, `PERMISSION_NEEDED`, `PROVIDER_UNAVAILABLE`, `SYNCING`, `SYNCED`, `PARTIAL`, `NO_RECORDS`, `ERROR`, including freshness timestamp when cached/stale data is shown.
- Consumes: normalized results from Task 2.

- [ ] **Step 1: Extend `HealthSyncGateTest` and source contract tests** for permission revoked, provider unavailable, zero records, partial read, and stale cached data.
- [ ] **Step 2: Run Android and source-contract focused tests** and verify RED.
- [ ] **Step 3: Implement the state machine and bridge/UI rendering** with Arabic/English labels; never map zero-record success to error.
- [ ] **Step 4: Re-run focused tests and full source/backend/Android unit gates** and verify PASS.
- [ ] **Step 5: Commit** `feat(fitness): expose reliable Health sync states`.

### Task 4: Sensor/Health fusion and reward eligibility boundary

**Files:**
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionSessionEngine.kt`
- Modify: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/MotionSessionEngineTest.kt`
- Modify: `fitness-v2/android/app/src/main/java/com/topherofit/thf/pulse/MotionFeatureAccumulator.kt`
- Modify: `fitness-v2/android/app/src/test/java/com/topherofit/thf/pulse/MotionFeatureAccumulatorTest.kt`

**Interfaces:**
- Consumes: Task 1 integrity classifier and Task 2 Health provenance.
- Produces: a session evidence summary whose highest integrity class is computed from actual accepted evidence, never from a client flag.

- [ ] **Step 1: Add failing tests** for overlapping sessions, impossible sensor sequence, rejected sensor samples not affecting totals, and Health/sensor corroboration increasing confidence without bypassing rejection rules.
- [ ] **Step 2: Run focused tests** and verify RED.
- [ ] **Step 3: Implement minimal evidence fusion** using existing motion engine lifecycle and monotonic hardware timestamps.
- [ ] **Step 4: Run full Android tests** and verify PASS.
- [ ] **Step 5: Commit** `feat(fitness): fuse trusted motion and Health evidence`.

### Task 5: Backend replay/idempotency and authoritative eligibility

**Files:**
- Modify: `fitness-v2/backend/workout_store.py`
- Modify: `fitness-v2/backend/reward_connector.py`
- Modify: `fitness-v2/backend/tests/test_workout_store.py`
- Modify: `fitness-v2/backend/tests/test_reward_connector.py`
- Modify: `fitness-v2/backend/tests/test_api.py`

**Interfaces:**
- Consumes: client evidence envelope containing provenance/integrity inputs; does not trust the client-computed class alone.
- Produces: deterministic server-side eligibility result and idempotent/replay-safe claim status.

- [ ] **Step 1: Write failing backend tests** for duplicate submission, nonce replay, stale evidence, self-authored Health source, manual evidence, and implausible metrics.
- [ ] **Step 2: Run** `python -m unittest discover -s fitness-v2/backend/tests -v` and verify RED on the new cases.
- [ ] **Step 3: Implement minimal backend validation/idempotency** while preserving existing API compatibility where possible.
- [ ] **Step 4: Re-run backend tests** and verify PASS.
- [ ] **Step 5: Commit** `feat(fitness): make reward eligibility server authoritative`.

### Task 6: 51008 release candidate and Google Play Internal evidence

**Files:**
- Modify: `fitness-v2/android/app/build.gradle`
- Modify: `.github/workflows/fitness-v2-android-health.yml`
- Modify: `.github/workflows/thf-fitness-play-probe.yml`
- Modify: `fitness-v2/tests/test_source_contract.py` if version assertions exist.

**Interfaces:**
- Consumes: all green Tasks 1–5.
- Produces: unique `versionCode 51008`, release-quality version name, signed AAB, CI evidence, and Play Internal upload/probe evidence.

- [ ] **Step 1: Add/adjust failing version contract** expecting versionCode `51008` and a non-debug release versionName.
- [ ] **Step 2: Run source contract and package/version tests** and verify RED while still on 51007.
- [ ] **Step 3: Bump candidate version and update exact-package workflow assertions**; do not weaken signing/permission gates.
- [ ] **Step 4: Run local source/backend/Android gates**; then push the candidate branch and require green GitHub Actions build/sign/package evidence.
- [ ] **Step 5: Upload only the exact green signed 51008 AAB to Google Play Internal and run an independent Play track probe**; retain SHA/run/track evidence. Closed promotion waits for physical-phone Health/sensor smoke evidence.
- [ ] **Step 6: Commit** `release(fitness): prepare verified trust-core 51008 candidate`.
