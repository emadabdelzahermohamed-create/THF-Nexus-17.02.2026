# THF Fitness / Pulse — Set sequence guard deployment evidence

Date: 2026-09-22
Scope: THF Fitness / Pulse standalone Web/backend only.
Canonical Git branch at implementation start: `release/fitness-standalone-v1-20260918`
Canonical Git head at implementation start: `236d7cf4a2850018f94df0aa0a6594f917eb5784`

## Production deployment
- AppDeploy app: `thf-fitness-pulse-ul26f1`.
- Production snapshot: `1790082588730`.
- Deployment terminal state: `ready`.
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`.
- QA timestamp: `1790082607869`.
- QA screenshots: Web and mobile produced.
- Runtime error summary: frontend `0`, backend `0`, network `0`.

## User-visible/session change
- The active-session set button becomes disabled and exposes an Arabic/English saving state while a set write is in flight.
- The client sends the expected one-based set number with each set log.
- The backend accepts only the first incomplete exercise in the prescribed plan order.
- The backend rejects stale set numbers, later-exercise submissions, off-plan exercises, and writes after all prescribed sets are complete.
- The accepted set number is returned in the backend response for an explicit server-authoritative boundary.

## Source and test verification
The applied snapshot was re-read after deployment and verified to contain:
- `loggingSet`, disabled/`aria-busy` set action, and `expectedSet` in `src/App.tsx`.
- `exercise_out_of_order`, `stale_set_sequence`, and `acceptedSet` in `backend/index.ts`.
- QA coverage labels for duplicate submission, server-enforced exercise order, and expected-set validation in `tests/tests.json`.

AppDeploy build/validation and post-deploy Web/mobile QA completed without reported frontend, backend, or network errors. The automated E2E field was not returned for this deployment, so authenticated end-to-end behavior remains fail-closed pending direct signed-in execution evidence.

## Preserved boundaries
- Canonical MPFB/MakeHuman Stage16A remains unchanged: 137 joints / 195 clips.
- No WAVE-MAWJA, RuinsCiv, or other project source/deployment/configuration was touched.
- No Android artifact was created or uploaded in this checkpoint.
- No claim of physical-device, GPU, Health Connect, FINAL, or Play runtime PASS is made.

