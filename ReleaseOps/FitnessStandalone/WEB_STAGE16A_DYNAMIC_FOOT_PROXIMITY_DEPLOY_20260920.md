# THF Fitness — Stage16A dynamic foot-proximity visual gate

Date: 2026-09-20
Scope: THF Fitness / Pulse standalone only. WAVE-MAWJA untouched.

## Production change
- AppDeploy snapshot: `1789894747889`
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`
- Canonical human remains MPFB/MakeHuman Stage16A only (137 joints / 195 clips); no legacy humanoid fallback added.
- Existing foot-bone markers now react visually to each foot bone's world-space proximity to the ground: opacity and scale strengthen near the ground and soften away from it.
- UI copy explicitly states that these are proximity indicators, **not** certified IK, pressure sensing, or biomechanical certification.
- Existing model-aware camera interpolation, Muscle Focus framing, lighting/shadows, rig-attached muscle visualization and fail-closed animation mapping are retained.

## Runtime evidence
QA snapshot timestamp: `1789894761164`.
- Web screenshot captured.
- Mobile screenshot captured.
- Frontend errors: 0.
- Backend errors: 0.
- Network errors: 0.
- Deployment status: `ready`.

## Fail-closed gates retained
This visual increment does not close true foot-lock/IK, Exercise→Animation biomechanical certification, physical Android/GPU/Health Connect evidence, first-install Android offline Stage16A packaging, Web↔Android cross-device synchronization, Play tester runtime, or final reference-quality acceptance.
