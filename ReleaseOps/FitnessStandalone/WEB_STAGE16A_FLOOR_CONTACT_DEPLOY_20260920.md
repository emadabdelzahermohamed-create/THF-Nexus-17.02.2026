# THF Fitness / Pulse — Stage16A Floor Contact Visual Evidence

Date: 2026-09-20
Scope: THF Fitness / Pulse standalone only

## Production change
- Canonical MPFB/MakeHuman Stage16A remains the only human renderer (137 joints / 195 clips contract).
- Added soft floor-projected contact discs driven by each detected Stage16A foot bone world position.
- Disc opacity/scale eases from foot-to-ground proximity and hysteresis-stabilized grounded state.
- Improved directional shadow bias/normalBias/radius to reduce contact-shadow acne while retaining soft grounding.
- Semantics remain fail-closed: this is visual proximity/contact context only, not pressure sensing, biomechanical certification, foot-lock or IK.
- No legacy humanoid fallback introduced.

## Production verification
- AppDeploy snapshot: `1789906905579`.
- Deployment status: `ready`.
- QA timestamp: `1789906923327`.
- Web screenshot captured.
- Mobile screenshot captured.
- Frontend errors: 0.
- Backend errors: 0.
- Network errors: 0.

## Gates intentionally left open
- True foot-lock / IK.
- Exercise→Animation biomechanical certification.
- Physical Android/GPU Stage16A runtime.
- Physical Health Connect evidence.
- First-install Android offline Stage16A packaging.
- Physical Web↔Android cross-device sync.
- Play tester install/runtime.
- Final authenticated P0 visual-reference acceptance.
