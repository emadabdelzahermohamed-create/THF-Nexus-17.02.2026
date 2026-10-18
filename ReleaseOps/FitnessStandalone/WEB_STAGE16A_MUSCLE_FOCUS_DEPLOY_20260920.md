# THF Fitness / Pulse — Stage16A target-zone muscle-focus P0 evidence

Date: 2026-09-20
Scope: THF Fitness / Pulse standalone only. WAVE-MAWJA untouched.

## Production evidence
- AppDeploy snapshot: `1789885576486`.
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`.
- Deployment state: `ready`.
- QA screenshot run: `1789885593768`.
- QA runtime: 0 frontend errors, 0 backend errors, 0 network errors.
- Web and mobile screenshots were produced by QA.

## P0 increment
- Canonical MPFB/MakeHuman Stage16A remains the only human renderer; no legacy humanoid fallback.
- Added a user-visible `Muscle focus` / `تركيز العضلات` control inside the live Stage16A training surface.
- The focus control derives a camera target from the current exercise-sensitive target zone (lower body, upper body, core, or full body) and the loaded canonical model bounds.
- Camera movement uses the existing smooth interpolation path, so target-zone reframing does not hard-cut.
- Existing four-view camera, rig-attached muscle visualization, lighting/shadows, ground/foot visual hooks, replay transition, speed/mirror controls, and truthful cache/network provenance remain intact.
- Runtime test contract now explicitly covers exercise-sensitive target-zone camera focus.

## Acceptance boundary
This is a visual/framing aid, not biomechanical certification and not true IK/foot locking. Physical Android/GPU, first-install Android offline Stage16A, Health Connect and cross-device sync remain FAIL-CLOSED.
