# THF Fitness / Pulse — Stage16A velocity-aware planted-contact production evidence

Date: 2026-09-21
Scope: THF Fitness / Pulse standalone only.

## Production result
- AppDeploy snapshot: `1789978884109`
- Deployment status: `ready`
- QA timestamp: `1789978900923`
- Web + mobile screenshots captured by QA.
- Frontend errors: 0
- Backend errors: 0
- Network errors: 0

## User-visible increment
The canonical MPFB/MakeHuman Stage16A renderer now conditions its planted-contact visual anchor on bounded foot-bone motion as well as near-ground height. A foot only enters the visual planted state when it is low and sufficiently still; the anchor releases on lift or fast planar/vertical travel. Anchor strength increases as planar motion settles, reducing the appearance of a floor marker sticking to a foot that is visibly travelling.

This is a visual/runtime quality improvement only. It is explicitly not inverse kinematics, true foot-lock, pressure/force sensing, or biomechanical Exercise→Animation certification.

## Avatar contract
- Canonical lineage: MPFB/MakeHuman Stage16A only.
- 137 joints / 195 clips contract retained.
- Legacy humanoid fallback remains forbidden.

## Gates deliberately left fail-closed
- Physical Android/GPU Stage16A evidence.
- Health Connect physical permission/data evidence.
- Web↔Android physical cross-device sync evidence.
- True IK/foot-lock.
- Exercise→Animation biomechanical certification.
- Android first-install offline Stage16A packaging.
- Play tester runtime/compliance and final screenshot-reference acceptance.
