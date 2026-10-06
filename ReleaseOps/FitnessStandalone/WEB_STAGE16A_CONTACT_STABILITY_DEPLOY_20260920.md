# THF Fitness — Stage16A Contact Stability Production Evidence

Date: 2026-09-20
Scope: THF Fitness / Pulse standalone only.

## Change
- Preserved canonical MPFB/MakeHuman Stage16A lineage only (137 joints / 195 clips); no legacy humanoid fallback.
- Replaced threshold-sensitive foot proximity presentation with hysteresis-stabilized near-ground state: enter <= 0.055 world Y, leave >= 0.085 world Y.
- Foot marker opacity/scale now ease toward target values instead of snapping each frame.
- Session exposes a truthful live near-ground count (0..2) when both foot-bone hooks are discoverable.
- Replay reset now re-enables the existing canonical animation action and fades it in without a pre-reset fade-out cut.
- This is visual contact stabilization only. It is NOT pressure sensing, biomechanical certification, true foot-lock, or IK.

## Production evidence
- AppDeploy app: `thf-fitness-pulse-ul26f1`
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`
- Snapshot: `1789901923645`
- QA timestamp: `1789901939723` (screenshots run path `1789901941224`)
- Deployment terminal state: `ready`
- QA: 0 frontend errors, 0 backend errors, 0 network errors.
- Web and mobile QA screenshots produced by the production QA run.

## Gate status
- P0 perceived contact/motion quality: improved, still OPEN against final visual-reference acceptance.
- Exercise→Animation biomechanical certification: OPEN / FAIL-CLOSED.
- True foot-lock / IK: OPEN / FAIL-CLOSED.
- Physical Android/GPU runtime: OPEN / FAIL-CLOSED.
- First-install Android offline Stage16A: OPEN / FAIL-CLOSED.
