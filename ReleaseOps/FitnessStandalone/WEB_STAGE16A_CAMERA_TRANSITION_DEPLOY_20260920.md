# THF Fitness / Pulse — Stage16A camera + transition P0 evidence

Date: 2026-09-20
Scope: THF Fitness / Pulse standalone only. WAVE-MAWJA untouched.

## Production evidence
- AppDeploy snapshot: `1789878130424`
- Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`
- Deployment state: `ready`
- QA screenshot run: `1789878148320`
- QA runtime: 0 frontend errors, 0 backend errors, 0 network errors.
- Web and mobile screenshots were produced by QA.

## P0 increment
- Preserved canonical MPFB/MakeHuman Stage16A lineage only; no legacy humanoid fallback.
- Replay now uses an explicit fade-out/fade-in transition instead of a hard reset/play visual cut.
- The four camera views now derive framing from the loaded Stage16A model bounding box/center/height rather than only fixed absolute framing, improving robustness across the canonical asset's rendered pose envelope.
- Existing soft shadows, ACES tone mapping, rig-attached muscle visualization, ground reference, foot-bone visual hooks, truthful cache/network provenance, and fail-closed animation certification remain intact.

## Tests / acceptance
- AppDeploy build/deploy validation passed.
- Production runtime reached `ready`.
- QA returned zero frontend/backend/network errors and generated Web/mobile screenshots.
- Updated runtime test contract covers smooth replay transition and four model-aware camera views.

## Gates intentionally still FAIL-CLOSED
- Exercise→Animation biomechanical certification.
- True foot-lock/IK (visual hooks are not IK).
- Physical Android/GPU install/runtime evidence.
- First-install Android offline Stage16A packaging.
- Health Connect physical evidence.
- Web↔Android cross-device synchronization evidence.
- Authenticated visual-reference acceptance against the approved screenshots.
