# TopHeroFit Growth Platform Design

Status: user-approved product direction, written specification pending final review
Date: 2026-10-22
Product: TopHeroFit / THF Fitness
Primary Android package: `com.topherofit.thf.pulse`

## 1. Objective

Build TopHeroFit into a production fitness platform that combines verified activity, adaptive training, high-quality offline exercise instruction, gym operations, social competition, coaching, and repeatable Google Play delivery. The product must create measurable user value and business value rather than expose placeholder labels or non-functional screens.

The competitive core is:

1. Verified Proof-of-Workout.
2. Adaptive Training.
3. Gym Operating System.
4. Verified Social Competitions.
5. High-quality offline exercise instruction.
6. Voice-guided training plus legally distributable workout music.

## 2. Binding priority order

Implementation order is binding unless a production blocker forces a temporary reordering:

1. Health Connect, phone sensors, provenance, integrity scoring and anti-cheat.
2. Reliable activity history, live tracking and clear sync/permission states.
3. Competitions, marathons and challenges built only on verified activity.
4. Exercise-library visual quality and library expansion.
5. Gym OS: occupancy, membership, bookings, coaches, programs and analytics.
6. Social, motivational, coaching and retention features.
7. Further monetization and partner integrations.

Every stable product jump must enter the Google Play release pipeline immediately. Internal testing is automatic for green candidates; Closed and Production promotion remain policy- and quality-gated.

## 3. Trust Core

### 3.1 Data sources

The Trust Core accepts activity from:

- Health Connect providers such as Samsung Health where permissioned.
- Phone step counter / accelerometer / gyroscope.
- GPS for supported outdoor sessions.
- Heart rate and other approved wearable data when available through Health Connect.
- Manual entries as unverified user records.

Every record stores provenance sufficient to distinguish provider, device/source class, recording method, timestamps and source record identifiers when the platform exposes them.

### 3.2 Integrity classes

Every activity is classified as one of:

- `VERIFIED`: sufficiently trustworthy for rewards and ranked competition.
- `SUPPORTED`: usable for personal analytics but not high-value rewards.
- `MANUAL`: user-authored; never silently treated as verified.
- `REJECTED`: impossible, duplicated, replayed, self-authored reward evidence or otherwise invalid.

The UI must show the class and explain why data is not reward-eligible.

### 3.3 Anti-cheat

The system rejects or down-ranks at minimum:

- duplicate Health records;
- self-authored Health records used as reward evidence;
- implausible speed, cadence, distance or time combinations;
- replayed challenge evidence;
- conflicting overlapping sessions;
- impossible sensor sequences;
- missing or revoked permissions presented as successful sync.

Reward eligibility is server-authoritative or policy-engine-authoritative. Client-local assertions cannot mint rewards or authorize treasury transfers.

## 4. Activity experience

Running, walking and supported workouts must provide a clear live experience comparable to mature fitness products: elapsed time, distance, pace/speed, cadence where available, route map, progress and recovery-safe controls.

Sync states must be explicit: connected, permission needed, provider unavailable, syncing, synced, partial data, no records, and error. The product must never collapse these distinct states into an ambiguous empty screen.

Activity history includes daily/weekly/monthly trends, personal records, streaks, verified totals and source badges.

## 5. Exercise Library and Offline Instruction

### 5.1 Quality target

The current two-frame demonstration baseline is transitional. Priority exercises must move to smooth multi-frame or skeletal/3D-equivalent offline motion that clearly demonstrates the full repetition without network access.

Each exercise must include:

- Arabic and English names and instructions;
- equipment and difficulty;
- target and secondary muscles;
- setup and execution cues;
- breathing and tempo guidance;
- common mistakes;
- regression and progression;
- substitute exercises;
- safety notes;
- offline demonstration assets with integrity hashes.

### 5.2 Expansion strategy

Expand in quality-controlled waves rather than raw count inflation:

- Wave A: core gym movements and popular bodyweight movements.
- Wave B: machines, cables and common free-weight variations.
- Wave C: sports conditioning, mobility, rehabilitation-safe low-risk drills and specialty training.

A catalog item cannot be marked production-ready until metadata, bilingual copy and demonstration media pass automated contract tests.

## 6. Adaptive Training

Programs adapt to user goal, experience, equipment, available days, recent performance, training volume and recovery signals. The system records set-level inputs before completion so a crash or navigation event does not discard workout state.

Initial supported goals include strength, hypertrophy, fat loss, general fitness, endurance and beginner onboarding. Recommendations must remain explainable and editable by the user.

## 7. Voice Coaching

Voice coaching is a first-class workout surface, not an accessibility afterthought.

The voice engine must support Arabic and English cues for:

- exercise start and transition;
- countdowns and interval timing;
- set/rep targets;
- rest countdowns;
- pace or cadence feedback when available;
- form/safety reminders that do not claim visual form detection unless actual validated pose analysis exists;
- motivational cues;
- milestone and personal-record announcements.

Users can independently control language, voice volume, cue density and whether motivational cues are enabled. Voice must duck music instead of abruptly stopping it. Essential timing cues must work offline.

## 8. Workout Music

TopHeroFit may bundle or stream workout music only when licensing is demonstrably compatible with commercial redistribution in the app.

Accepted sources are limited to tracks with a documented license that permits the intended use, such as CC0/public-domain or another license explicitly allowing commercial redistribution and modification when required. Attribution-required tracks need machine-readable attribution metadata and an in-app credits surface. NC (non-commercial), ND where edits/looping are required, unknown-license, ripped or merely 'royalty-free' tracks without redistribution rights are excluded.

Music capabilities:

- offline starter packs;
- BPM/intensity playlists;
- user-selectable workout genres;
- shuffle and favorites;
- music/voice ducking;
- no network dependency for downloaded packs;
- license/source manifest shipped with every pack.

User-owned local music or external provider integrations are separate adapters and must respect provider terms.

## 9. Gym Operating System

### 9.1 Gym entity

A gym has branches, capacity, opening hours, equipment, coaches, memberships, classes, programs, challenges and operational analytics.

### 9.2 Occupancy

Initial occupancy estimation combines verified check-ins, active in-gym sessions, configured capacity and historical patterns. Display simple user-facing bands such as quiet, moderate and busy plus predicted quieter windows.

Later adapters may ingest turnstile, BLE or partner API data. Predictions must expose freshness and confidence; estimated occupancy must never be labeled as exact live headcount unless it is exact.

### 9.3 Membership and booking

Supported flows include:

- browse gym/branch;
- membership products;
- class/session booking;
- QR check-in;
- coach booking where offered;
- renewal reminders;
- gym-specific programs and challenges.

Physical gym services are accounted separately from digital in-app goods. Payment implementation must follow Google Play policy and local payment requirements.

### 9.4 Owner and coach tools

Gym owners/coaches can create and assign programs by goal and level, manage classes, publish challenges, review attendance/engagement analytics and communicate with opted-in members.

Role-based access separates owner, manager, coach and staff permissions. Audit logs cover material administrative changes.

## 10. Competitions and Marathons

Challenge creators may be individuals, friends, coaches or gyms. Supported formats include steps, verified distance, streaks, verified workout completion, attendance and validated strength/volume metrics.

Competition tiers:

- free social challenges;
- sponsor-funded fixed-prize challenges;
- gym-funded rewards and benefits;
- game-reward entitlement challenges through signed eligibility claims;
- legally cleared future THF-token reward rail, disabled by default.

No stake-based token or cash competition is enabled without explicit legal and store-policy clearance. Entry fees that create a chance to win real-world value are fail-closed.

Leaderboards must handle ties, late sync, revoked records, fraud reclassification and challenge cutoff time deterministically.

## 11. Social and Motivation

The product supports friends, private groups, gym groups, shareable workout cards, personal records, leaderboards and opt-in social activity.

Notifications are contextual rather than spam-driven. Examples include goal proximity, recovery-safe reminders, a challenge nearing completion, a friend overtaking the user, a scheduled session and a verified quieter gym window.

Every notification class is individually configurable and subject to frequency caps and quiet hours.

## 12. Economic and Token Boundaries

THF Token remains economically separate from game currencies and ordinary fitness points. Existing `docs/capital/ECONOMY_BOUNDARIES.md` remains binding.

Fitness may produce signed eligibility claims for downstream rewards. A future THF-token adapter is disabled until legal, anti-fraud, treasury and store-policy gates are satisfied.

No client workout result directly authorizes a token transfer. No implicit exchange rate exists between fitness points, game rewards and THF Token.

## 13. Monetization

Near-term non-token revenue surfaces may include:

- gym SaaS subscriptions;
- membership/booking commission where lawful;
- coach tools and premium programming;
- consumer premium features;
- sponsor-funded challenges;
- B2B wellness programs;
- grants, accelerator funding and equity/convertible investment.

Token fundraising is treated as a separately reviewed capital-markets activity, not an in-app shortcut to operating cash.

## 14. Release and Evidence Pipeline

Every candidate receives a unique increasing versionCode and reproducible source SHA.

Required gates before Google Play Internal upload:

- source contract tests;
- backend/unit tests;
- Android build and signing checks;
- package/version verification;
- health permission and manifest checks;
- no known critical crash.

Internal upload occurs immediately after a green candidate. Closed promotion adds device smoke, Health Connect integration, sync integrity and policy checks. Production promotion additionally requires store metadata/policy readiness and a release-quality versionName without debug/alpha labeling unless intentionally shipping a public beta.

Evidence retained per release includes source SHA, build run, Play upload result, track state, device evidence and known limitations.

## 15. Error and Offline Behavior

Critical workout and timing functions must degrade gracefully offline. Health sync queues retryable work without fabricating success. Music/voice downloaded assets remain usable offline. Gym bookings and authoritative remote mutations clearly show pending/failed state when network access is absent.

No feature may silently substitute stale remote data without a freshness indicator when freshness affects user decisions.

## 16. Privacy and Permissions

Request the minimum Health Connect and Android permissions required for the active feature. Explain the purpose at the moment of use. Revocation must be respected immediately for future reads/writes.

Gym occupancy and social features use aggregated or permissioned data; users are not exposed as a live location roster by default.

## 17. Testing Strategy

Automated contracts cover catalog integrity, Health provenance, anti-cheat, challenge scoring, voice cue sequencing, music license manifests, gym roles and release versioning.

Device tests cover Samsung/Health Connect permission flows, provider-empty states, live sensor tracking, offline workout continuity, voice/music mixing, and upgrade/install behavior.

High-value reward paths require negative tests for duplicate, replayed, manual, self-authored and implausible activity.

## 18. Delivery decomposition

This specification is intentionally architectural and must be implemented as separate plans, in this order:

1. Trust Core completion and Health UX reliability.
2. Competition foundation on verified evidence.
3. Exercise media quality pipeline plus voice/music engine.
4. Gym OS foundation and occupancy.
5. Gym booking/membership/coach tools.
6. Social motivation and adaptive coaching expansion.

Each plan must ship a working, testable increment and push its stable candidate through the established Google Play pipeline.
