# Top Hero Fit Fitness — Sensor-First Verification Architecture

Date: 2026-10-21
Status: Design approved in chat; written specification pending user review
Base release SHA: `ba9a5bc3a318823ad8c967dae5ce4cbe9a880fec`
Target app: `com.topherofit.thf.pulse`

## 1. Objective

Make Top Hero Fit Fitness derive activity, workout progress, and reward eligibility primarily from verifiable device evidence instead of user-entered counters. Manual input remains available only when a fact cannot be measured reliably, and manual data must never be treated as equivalent to sensor-verified evidence.

The system must provide:

- real step counting from Android/Samsung hardware sensors;
- automatic motion/activity evidence for walking, running, and workout sessions;
- real Health Connect reads with provenance, not only a permission/"connected" label;
- anti-cheat and replay resistance proportional to the value of rewards;
- battery-aware sensing that does not keep high-rate sensors running all day;
- privacy-preserving verification, preferring on-device features over raw sensor upload;
- physical-phone QA on the Samsung SM-A217F that proves sensor and Health Connect behavior with observed changes.

## 2. Current State

The current Android app already has meaningful foundations:

- `ACTIVITY_RECOGNITION` permission;
- Samsung/Android `TYPE_STEP_COUNTER` registration;
- Health Connect permissions for steps, exercise, distance, and active calories;
- Health Connect read and exercise-session write paths;
- stable client record IDs and local version-aware upserts;
- pending Health Connect/backend queues and duplicate/stale handling.

However, the current implementation has important gaps:

- accelerometer and gyroscope are not part of workout verification;
- the step counter is used as an in-session delta only, without a broader motion evidence model;
- Health Connect `connected` currently means required permissions are present, not that real records were successfully read;
- recent health data is aggregated before the app can grade provenance quality;
- a UI-provided workout summary can be queued and written to Health Connect without independent sensor evidence;
- rewards do not yet distinguish manual, sensor-supported, Health Connect-supported, and integrity-attested evidence.

## 3. Source-of-Truth Policy

Every measured fact has an explicit source and confidence tier.

### 3.1 Default source priority

1. Local device sensors measured during the session.
2. Health Connect records from known automatic/active recording origins.
3. Cross-source fusion when both are available.
4. Manual input only for facts that cannot be measured safely or reliably.

Examples:

- steps: hardware Step Counter / Health Connect steps;
- movement cadence: Step Detector + accelerometer timing;
- running/walking classification: low-power activity classification plus local sensor features;
- session duration: monotonic app/session timestamps corroborated by activity evidence;
- dumbbell weight: manual, because phone sensors cannot infer it reliably;
- perceived exertion, pain, injury notes: manual by design;
- rep count: sensor/pose-derived where supported, otherwise manual but explicitly unverified.

### 3.2 Manual data policy

Manual data is never silently promoted to verified evidence. It must carry `source=MANUAL` and cannot independently unlock high-trust rewards, competitive leaderboard credit, or token issuance.

## 4. Architecture

The feature is split into isolated modules with narrow interfaces.

### 4.1 SensorCapabilityRegistry

Responsibilities:

- discover Step Counter, Step Detector, accelerometer, and gyroscope;
- expose permissions and sampling capabilities;
- expose device/sensor metadata needed for diagnostics;
- report capability state to UI and QA.

No reward logic belongs here.

### 4.2 MotionSessionEngine

Responsibilities:

- maintain workout/motion session lifecycle;
- use Step Counter and Step Detector for low-cost step evidence;
- temporarily enable accelerometer/gyroscope at higher sampling rates during active sessions or when a low-power trigger indicates meaningful motion;
- calculate compact features rather than permanently storing raw high-rate streams;
- emit a `MotionEvidence` object.

Proposed `MotionEvidence` fields:

- session ID;
- start/end monotonic timestamps and wall-clock timestamps;
- step delta;
- detector event count;
- cadence distribution;
- accelerometer magnitude mean/variance/peaks;
- gyroscope magnitude mean/variance;
- active-motion duration;
- stationary fraction;
- interruption/background intervals;
- sensor availability/accuracy flags;
- evidence digest/hash;
- local confidence score.

Raw samples are discarded after features are produced unless an explicit QA/debug mode is active.

### 4.3 ActivityClassifier

Responsibilities:

- classify coarse activity such as stationary, walking, running, cycling-like motion, and unknown;
- use Android activity transitions where available for low-power wake-up/classification;
- fuse transition confidence with local step/cadence/motion features;
- never claim a specific exercise type when evidence is insufficient.

The first production scope is walking/running/active-vs-stationary. More complex gym exercise classification is introduced incrementally after phone-validated data exists.

### 4.4 ExerciseVerificationEngine

Responsibilities:

- convert motion evidence into exercise/workout confidence;
- optionally accept exercise-specific evidence providers;
- support future phone-placement-specific models;
- support optional on-device pose verification for exercises where camera verification materially improves rep/form confidence.

Optional pose verification may use MediaPipe Pose Landmarker. Camera verification is opt-in and must not be a requirement for ordinary local tracking.

### 4.5 HealthConnectProvenanceRepository

This replaces aggregate-only health interpretation with record-aware reads.

For each relevant Health Connect record, retain enough metadata to evaluate trust:

- record type;
- time range;
- data origin package;
- recording method when available;
- device metadata when available;
- client record ID/version when applicable;
- measured value needed for aggregation;
- ingestion/read timestamp.

The UI state must distinguish:

1. `PROVIDER_AVAILABLE`
2. `PERMISSIONS_GRANTED`
3. `DATA_READ_SUCCESS`
4. `VERIFIED_DATA_PRESENT`

A green "synced/verified" state requires a successful read. Permission grants alone are not sufficient.

### 4.6 EvidenceFusionEngine

Responsibilities:

- compare local sensor evidence with Health Connect evidence;
- detect agreement, missing data, and contradictions;
- produce a normalized `VerificationResult`.

Example checks:

- local step delta vs Health Connect step increase in overlapping periods;
- workout duration vs active-motion duration;
- claimed run distance vs plausible cadence/duration bounds;
- exercise session overlap conflicts;
- repeated or identical evidence digests;
- impossible simultaneous sessions;
- abrupt value jumps inconsistent with source cadence.

### 4.7 RewardTrustGate

Reward logic consumes `VerificationResult`; it does not read raw UI summaries directly.

Proposed trust tiers:

- `T0_MANUAL`: manual-only or unknown provenance; history allowed, no high-value rewards.
- `T1_SENSOR`: local sensor evidence passes plausibility checks.
- `T2_CORROBORATED`: local evidence agrees with trusted Health Connect evidence.
- `T3_ATTESTED`: T2 plus successful backend integrity checks for high-value operations.

Thresholds are configurable server-side so anti-cheat tuning does not require a new app build.

## 5. Anti-Cheat Design

Anti-cheat is layered and risk-based.

### 5.1 Local plausibility

Reject or downgrade evidence with:

- impossible step cadence or acceleration patterns;
- motion claimed while sensors are predominantly stationary;
- implausible distance/time combinations;
- negative or discontinuous counters not explained by reboot/session reset;
- workouts exceeding realistic duration limits;
- overlapping incompatible sessions.

### 5.2 Provenance grading

Health Connect records are scored by provenance. Manual/unknown recording methods are never equivalent to actively/automatically recorded data. Unknown third-party origins are allowed for user history but cannot automatically become high-trust reward evidence.

### 5.3 Replay and duplication resistance

Each workout uses:

- stable client record ID;
- monotonically increasing record version;
- session nonce generated at session start;
- evidence digest over canonicalized session facts;
- server-side idempotency/replay checks for reward claims.

### 5.4 App/device integrity

Play Integrity is used only for high-value backend actions such as token/reward issuance or protected leaderboard submissions. Ordinary local tracking remains functional when attestation is unavailable. Debug/QA builds use an explicit non-reward test mode rather than pretending production attestation passed.

### 5.5 No single-signal trust

No reward is based solely on:

- a user-entered value;
- a JavaScript summary;
- a single Health Connect aggregate;
- a Play Integrity verdict;
- a single sensor threshold.

The trust score requires coherent evidence.

## 6. Battery and Performance Policy

- Step Counter/Detector remain the preferred low-power continuous signals.
- Accelerometer/gyroscope high-rate sampling is disabled when no workout or meaningful motion trigger exists.
- Active-session rates are chosen to support classification while remaining practical on the Samsung A21s-class device.
- Feature extraction occurs on-device.
- Raw sample retention is disabled in production.
- Background behavior complies with Android lifecycle/foreground-service constraints; no hidden perpetual high-rate sampling.

Acceptance includes a battery sanity test over a representative workout and idle period.

## 7. Privacy and Data Minimization

- Store derived features and evidence digests instead of continuous raw inertial data by default.
- Camera/pose verification is explicit opt-in, processed on-device where practical, and disabled by default.
- Do not upload camera frames for ordinary verification.
- User-visible history can include manual records, but verification badges must make their trust level clear.
- Health Connect permissions remain least-privilege and purpose-specific.

## 8. UI/UX Requirements

The user should not need to type routine activity facts.

Dashboard/workout UX must show:

- live step count when sensor permission is granted;
- current detected activity when confidence is sufficient;
- workout auto-start suggestion or explicit start with automatic measurement after start;
- source badges: Sensor, Health Connect, Manual;
- verification state/confidence after session;
- Health Connect state with separate provider/permissions/data-read/verified indicators;
- manual fields only where technically necessary.

Manual editing must never overwrite original sensor evidence; edits create a separate manual annotation layer.

## 9. Data Model

A `WorkoutEvidenceEnvelope` is the canonical input to backend/reward processing.

Required logical fields:

- schema version;
- workout/session ID;
- record version;
- start/end time;
- exercise/activity type and confidence;
- local sensor feature summary;
- Health Connect provenance summary;
- manual annotations separated from measured facts;
- local plausibility flags;
- fusion result;
- trust tier;
- evidence digest;
- integrity token/reference only when required for protected actions.

The existing UI workout summary becomes a presentation/input object, not the authoritative evidence object.

## 10. Error Handling

- Missing sensor: degrade gracefully and report capability; do not fabricate zero-evidence verification.
- Permission denied: local history/manual fallback remains usable, reward trust is reduced.
- Health Connect unavailable: local sensor pipeline continues.
- Health Connect permissions granted but no records: display `NO_DATA`, not `SYNCED`.
- Rate limiting: preserve last successful data state and retry with backoff.
- Sensor reset/reboot: detect Step Counter discontinuity and start a new baseline segment.
- Integrity unavailable: ordinary workout saved locally; protected reward claim remains pending/unverified.
- Conflicting sources: preserve history, flag conflict, and downgrade reward trust instead of deleting data.

## 11. Physical Phone QA Acceptance Criteria

The Samsung SM-A217F is the primary device gate for this phase.

A build does not pass sensor QA unless evidence shows:

1. ACTIVITY_RECOGNITION granted to the installed exact build.
2. Step Counter/Detector capability detected.
3. A controlled walking sample produces an observed step increase.
4. A stationary control period does not generate a comparable false increase.
5. An active workout produces non-zero accelerometer/gyroscope-derived motion features when those sensors are enabled for the session.
6. Health Connect provider availability and permissions are reported separately.
7. Health Connect read returns either concrete records with origins/provenance or an explicit `NO_DATA`; a permission-only state is not called synced.
8. Manual workout data is labeled manual and receives lower trust than sensor evidence.
9. Duplicate/replayed reward submission is idempotently rejected or downgraded.
10. The exact tested APK/AAB SHA, app version, source SHA, and evidence artifact are recorded.

## 12. Implementation Phases

### Phase A — Sensor evidence foundation

- split sensor handling out of `MainActivity`;
- add Step Detector plus accelerometer/gyroscope session sampling;
- define `MotionEvidence` and deterministic feature extraction;
- expose evidence to UI without reward changes initially;
- physical phone QA.

### Phase B — Health Connect provenance

- record-level reads;
- recording method/origin/device grading;
- provider/permission/read/verified state machine;
- phone QA against Samsung Health/Health Connect.

### Phase C — Evidence fusion and anti-cheat

- plausibility rules;
- cross-source consistency;
- replay-resistant evidence envelope;
- trust tiers and backend validation.

### Phase D — Protected rewards

- Play Integrity integration for protected claims;
- server-side idempotency/integrity verification;
- pending/retry behavior;
- no production reward success claimed without real backend evidence.

### Phase E — Exercise-specific verification

- expand supported exercise evidence models;
- optional MediaPipe pose path for appropriate movements;
- validate model accuracy before using it for high-value rewards.

## 13. Testing Strategy

Unit tests:

- feature extraction from deterministic sensor traces;
- counter reset handling;
- cadence/plausibility bounds;
- provenance grading;
- fusion outcomes;
- replay/idempotency logic;
- trust-tier assignment.

Instrumentation/device tests:

- permission flows;
- sensor capability detection;
- session lifecycle/background transitions;
- Health Connect read/no-data/error states;
- queue persistence and process restart.

Physical QA:

- controlled walk;
- stationary control;
- short run/walk transition;
- representative bodyweight workout;
- Health Connect sync with source evidence;
- battery sanity run.

CI artifacts must include machine-readable summaries so a successful build cannot be confused with successful physical-sensor verification.

## 14. Non-Goals for the First Delivery

The first delivery will not attempt to perfectly identify every gym exercise from a phone in arbitrary placement. It will establish trustworthy motion/session evidence, real Health Connect provenance, and anti-cheat foundations first. Exercise-specific models are added only when they can be validated with real device data.

## 15. Release Gate

The sensor-first feature is release-eligible only when:

- source SHA is merged to the Fitness release line;
- Android CI succeeds;
- physical Samsung QA passes the acceptance criteria for the implemented phase;
- Health Connect status semantics are proven accurate;
- manual-only records cannot obtain the same trust/reward path as verified evidence;
- no claim of anti-cheat/Health Connect success is made without attached evidence.
