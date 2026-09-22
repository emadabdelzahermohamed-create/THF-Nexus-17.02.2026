# THF Fitness / Pulse — Stage16A dominant viewport + compact in-app video evidence

Date: 2026-09-21
Branch: `release/fitness-standalone-v1-20260918`
Scope: THF Fitness / Pulse standalone only. WAVE-MAWJA untouched.

## Implemented
- Re-composed the active training session so the canonical MPFB/MakeHuman Stage16A renderer remains the dominant visual coach surface.
- Retained the exercise YouTube embed inside the application as a compact picture-in-picture reference rather than a large block that displaces the 3D coach.
- Added responsive mobile sizing and logical `inset-inline-start` positioning so the composition works with Arabic RTL and English LTR.
- Removed obsolete CSS for the old synthetic demo-loop humanoid representation from the deployed session stylesheet. No legacy humanoid fallback is used.
- Preserved session controls, voice guidance, phase rail, prescription, Up Next, collapsible full session details, and canonical Stage16A lineage (137 joints / 195 clips).

## Runtime evidence
- AppDeploy app: `thf-fitness-pulse-ul26f1`
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`
- Snapshot: `1789989736929`
- Deployment status: `ready`
- QA timestamp: `1789989759014`
- QA screenshots: Web + mobile captured.
- Runtime errors: 0 frontend, 0 backend, 0 network.

## Acceptance boundaries
This closes only a visual-composition increment. It does NOT close the binding P0 screenshot-reference gate by itself. Physical Android/GPU/Health Connect evidence, cross-device Web↔Android sync, true IK/foot-lock, biomechanical Exercise→Animation certification, first-install Android offline Stage16A packaging, and Play tester runtime/compliance remain FAIL-CLOSED until direct evidence exists.
