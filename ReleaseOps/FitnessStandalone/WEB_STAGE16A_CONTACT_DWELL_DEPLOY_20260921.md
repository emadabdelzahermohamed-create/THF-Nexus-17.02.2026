# THF Fitness / Pulse — Stage16A contact-dwell visual increment

Date: 2026-09-21
Scope: THF Fitness / Pulse standalone only.

## Production evidence
- AppDeploy snapshot: `1789984947600`
- Deployment: `ready`
- QA timestamp: `1789984964027`
- Web + mobile screenshots captured.
- Frontend errors: 0
- Backend errors: 0
- Network errors: 0

## Change
The canonical MPFB/MakeHuman Stage16A renderer keeps its velocity/height hysteresis and adds a short 45 ms stable-contact dwell before the planted-contact visual anchor engages. This suppresses single-frame/very-short near-floor contacts while retaining immediate release on lift or fast planar/vertical travel. The UI explicitly labels this as a time + velocity-qualified visual preview only; it is not IK, foot-lock, pressure sensing, force measurement, or biomechanical certification.

## Canonical contract
- MPFB/MakeHuman Stage16A only.
- 137-joint contract retained.
- 195-clip contract retained.
- Legacy humanoid fallback remains forbidden.

## Gates intentionally still open
Physical Android/GPU/Health Connect evidence, Web↔Android physical sync, true IK/foot-lock, Exercise→Animation biomechanical certification, first-install Android offline Stage16A packaging, Play tester runtime/compliance, and final screenshot-reference acceptance remain FAIL-CLOSED pending direct evidence.
