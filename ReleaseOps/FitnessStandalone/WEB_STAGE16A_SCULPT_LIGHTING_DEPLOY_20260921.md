# Stage16A sculpt-lighting production evidence — 2026-09-21

Scope: THF Fitness / Pulse standalone only. WAVE-MAWJA untouched.

## Production result
- AppDeploy app: `thf-fitness-pulse-ul26f1`
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`
- Snapshot: `1789963257916`
- Deployment status: `ready`
- QA timestamp: `1789963275555`
- QA screenshots: Web + mobile produced.
- Runtime errors reported by AppDeploy QA: frontend `0`, backend `0`, network `0`.

## P0 visual increment
- Preserved canonical MPFB/MakeHuman Stage16A renderer and its 137-joint / 195-clip contract; no legacy humanoid fallback added.
- Tightened directional-light shadow frustum around the athlete to improve useful shadow resolution.
- Added a dedicated cool sculpt/key spotlight with soft penumbra and shadow casting to improve body-form readability.
- Added a soft elliptical grounding shadow under the athlete to improve perceived floor contact and depth without claiming pressure sensing or IK.
- Existing key/fill/rim lighting, ACES tone mapping, soft shadows, exercise-sensitive framing, pelvis-follow camera, rig-attached muscle visualization and fail-closed motion semantics remain intact.
- Updated the user-visible motion-coach QA contract to cover cinematic sculpt lighting and the grounding shadow.

## Acceptance boundary
This closes only a production visual increment. It does NOT close physical Android/GPU evidence, Health Connect, Web↔Android physical sync, true foot-lock/IK, biomechanical Exercise→Animation certification, first-install Android offline Stage16A packaging, Play tester runtime/compliance, or final screenshot-reference acceptance. Those remain FAIL-CLOSED pending direct evidence.