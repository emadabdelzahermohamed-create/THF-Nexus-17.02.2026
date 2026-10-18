# Stage16A rig-attached anatomy visual gate — 2026-09-19

Production app: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/
AppDeploy snapshot: `1789833688742`
QA snapshot: `1789833706312`

## Completed
- Replaced world-space floating muscle capsules with overlays attached to matching Stage16A skeleton bones where the canonical rig exposes recognized aliases.
- Exercise-sensitive lower-body, upper-body and core overlays now inherit bone transforms and move with the animated Stage16A rig.
- UI reports ATTACHED vs UNAVAILABLE instead of claiming anatomy when a compatible bone was not found.
- Preserved canonical MPFB/MakeHuman Stage16A lineage and zero legacy humanoid fallback.
- Preserved fail-closed motion certification wording: name-matched clips are not called biomechanically certified.

## Runtime evidence
- Deployment reached `ready`.
- Frontend errors: 0.
- Backend errors: 0.
- Network errors: 0.
- Web and mobile QA screenshots generated under QA snapshot `1789833706312`.

## Still fail-closed
- These are rig-attached target overlays, not a medically exact segmented anatomical mesh.
- Per-exercise Exercise→Animation biomechanical certification remains open.
- Foot-lock/IK correction remains open beyond the current ground/shadow reference.
- First-install Android offline asset bundling and physical GPU/device evidence remain open.
- Google Play Internal remains blocked by the previously recorded verified upload-signing/physical-device gates.
