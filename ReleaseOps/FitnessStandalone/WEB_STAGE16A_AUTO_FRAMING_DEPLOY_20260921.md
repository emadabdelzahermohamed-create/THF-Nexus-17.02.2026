# Stage16A automatic exercise-sensitive framing — production evidence

Date: 2026-09-21
Scope: THF Fitness / Pulse standalone only.

## Change
Production Stage16A renderer now computes an opening camera target from the loaded canonical model bounds and exercise-sensitive target zone. Lower-body, upper-body, core and full-body flows receive different initial vertical framing and distance while retaining movement context. Existing smooth camera interpolation, four manual model-aware views and explicit Muscle Focus remain available.

Canonical lineage is unchanged: MPFB/MakeHuman Stage16A only, 137 joints / 195 clips; no legacy humanoid fallback was introduced. This change does not claim biomechanical certification, true IK/foot-lock, physical-device/GPU success or Android offline-first-install readiness.

## Production evidence
- AppDeploy snapshot: `1789956035373`
- Deployment terminal status: `ready`
- QA timestamp: `1789956053743`
- QA screenshots: Web and mobile produced.
- Runtime errors: 0 frontend, 0 backend, 0 network.
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`

## Gate status
This is a P0 visual-quality increment and runtime evidence, not final screenshot-reference acceptance. Physical Android/GPU, Health Connect, Web↔Android sync, biomechanical Exercise→Animation certification, true IK/foot-lock and first-install Android offline Stage16A remain FAIL-CLOSED.