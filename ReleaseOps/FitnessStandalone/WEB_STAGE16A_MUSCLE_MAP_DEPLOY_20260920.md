# THF Fitness / Pulse — Stage16A Exercise-sensitive Muscle Map Production Evidence

Date: 2026-09-20
Scope: THF Fitness / Pulse standalone only
Branch: `release/fitness-standalone-v1-20260918`

## Implemented
- Exercise detail muscle visualization now changes its highlighted body region from the exercise target classification (lower body / upper body / core / full body) instead of using one fixed target pulse.
- Added primary-focus/support legend and bilingual explanatory copy.
- Safety semantics remain explicit: the map is illustrative only, not a diagnosis and not a measurement of muscle activation.
- Canonical MPFB/MakeHuman Stage16A remains the exercise-detail renderer; no legacy humanoid fallback was introduced.
- Exercise→Animation biomechanical certification remains fail-closed.

## Production runtime evidence
- AppDeploy production snapshot: `1789905543370`.
- Deployment status: `ready`.
- QA timestamp: `1789905563125`.
- QA screenshots captured for Web and mobile.
- Runtime errors after deploy: frontend 0, backend 0, network 0.
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`.

## Acceptance boundaries
This increment does **not** close final screenshot-reference visual acceptance, Exercise→Animation biomechanical certification, true foot-lock/IK, physical Android/GPU/Health Connect, first-install Android offline Stage16A, cross-device Web↔Android sync, or Play tester runtime. Those gates remain FAIL-CLOSED pending direct evidence.
