# THF Fitness V2 Rebuild — Closure Scope

Date: 2026-10-02
Branch: release/fitness-v2-rebuild-20261002
Status: ACTIVE / single-project focus

## Product decision

The current Stage16A avatar is removed from the production acceptance path. No release is accepted because an avatar exists; exercise clarity is the requirement.

## Current baseline truth

- Live catalog currently exposes 18 exercises and 8 plans.
- Sport-specific coverage is insufficient; football is the only clearly distinct sport-conditioning plan.
- Gym coverage is not a real equipment/muscle/program library.
- Android package contains Health Connect code/permissions, but V2 requires a complete user-facing connection and sync flow with physical-device evidence.

## V2 information architecture

Primary navigation:
1. Today
2. Train
3. Progress
4. Health
5. Profile

Train:
- Programs
- Exercise library
- Gym
- Home
- Running & walking
- Cycling
- Football
- Swimming
- Yoga & Pilates
- Calisthenics & gymnastics
- Boxing & martial arts
- Mobility & stretching
- HIIT & cardio
- Racket/team sports
- Recovery & breathing

## Exercise contract

Every exercise accepted into production must include:
- Arabic + English name
- sport/category
- primary + secondary muscles
- equipment
- level
- setup
- step-by-step execution
- breathing cue
- tempo or duration
- sets/reps/rest defaults where relevant
- common mistakes
- regression + progression
- safety warning
- demonstration media
- offline availability state
- source + license metadata

## Open content lanes

1. free-exercise-db
   - public-domain exercise dataset
   - 800+ exercises
   - local JSON + images are suitable for an offline baseline

2. wger
   - open-source workout/exercise ecosystem
   - ingest only content whose per-entry license is acceptable
   - preserve attribution/license metadata

3. THF-owned motion lane
   - use permissively licensed/open motion-capture tooling for motions that need animation
   - no dependency on the rejected Stage16A avatar
   - demonstrations may use licensed images, local video, or 3D motion; clarity wins over using a single character

## Gym acceptance

Gym is a first-class section, not a filter.
Required filters:
- body part
- muscle
- equipment
- movement pattern
- difficulty
- goal

Required equipment families:
- barbells
- dumbbells
- benches
- cables
- selectorized machines
- plate-loaded machines
- smith machine
- racks
- kettlebells
- resistance bands
- bodyweight

Tracking:
- sets
- reps
- load
- rest
- RPE/RIR
- warm-up sets
- working sets
- personal records
- history
- estimated volume

## Health Connect acceptance

A build is NOT Health-Connect-complete merely because permissions/classes exist.

Required user-visible flow:
- Health screen with connection status
- explanation before permission request
- request only used permissions
- read steps
- read exercise sessions
- read distance where supported
- read active calories where supported
- optional heart-rate read only when used in UI
- write completed THF exercise sessions
- deduplicate with stable client record IDs
- sync status + last sync timestamp
- permission change/revoke handling
- empty/error states
- physical Android device evidence

Samsung Health:
- use Health Connect as the primary interoperability path
- document the Samsung Health <-> Health Connect user setup
- verify Samsung-originated steps/exercise data on a physical device when available

## Health Connect exercise mapping

Map THF sports to official Health Connect ExerciseSessionRecord types where available, including:
- strength training / weightlifting
- running / treadmill
- walking / hiking
- biking / stationary biking
- soccer
- swimming pool / open water
- yoga / Pilates
- gymnastics
- HIIT
- boxing / martial arts
- rowing
- tennis / table tennis / squash / badminton
- volleyball / basketball / handball
- stretching
- guided breathing

## UX acceptance

No release until:
- onboarding selects goal, level, schedule and available equipment
- Today shows one clear next action
- Train is browsable and searchable
- exercise detail has a clear demo above the fold
- active workout is usable one-handed
- progress is understandable without opening raw logs
- Health integration is discoverable from primary navigation
- RTL Arabic is first-class
- no dead buttons
- no placeholder sport sections

## Release gate

V2 closes only after:
1. Web visual/functional pass
2. Android build pass
3. Physical-device workout pass
4. Health Connect physical-device sync pass
5. Offline exercise demo pass
6. Play internal pass
7. User acceptance
