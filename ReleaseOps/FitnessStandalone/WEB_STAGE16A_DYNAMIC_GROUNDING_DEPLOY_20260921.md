# Stage16A dynamic grounding — production evidence (2026-09-21)

Scope: THF Fitness / Pulse standalone only. WAVE-MAWJA untouched.

## Implemented
- Preserved canonical MPFB/MakeHuman Stage16A renderer only (137 joints / 195 clips contract; zero legacy fallback).
- Replaced the visually static grounding ellipse with a bounded pelvis-reactive grounding shadow.
- Shadow follows lateral/depth pelvis translation with smoothing and tightens/fades as the body lifts, improving perceived floor contact without claiming force/pressure sensing or true IK.
- Increased mobile immersive Stage16A viewport height and adjusted overlay spacing/ground glow for clearer full-body framing.
- Updated runtime QA contract to explicitly cover the dynamic grounding behavior and truthful semantics.

## Production verification
- AppDeploy snapshot: `1789970498133`.
- Deployment status: `ready`.
- QA timestamp: `1789970515811`.
- Web screenshot and mobile screenshot captured by runtime QA.
- Frontend errors: 0.
- Backend errors: 0.
- Network errors: 0.
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`.

## Fail-closed boundaries
This evidence does **not** close physical Android/GPU, Health Connect, cross-device Web↔Android sync, true foot-lock/IK, pressure/force sensing, Exercise→Animation biomechanical certification, first-install Android offline Stage16A packaging, Play tester runtime/compliance, or final screenshot-reference acceptance.
