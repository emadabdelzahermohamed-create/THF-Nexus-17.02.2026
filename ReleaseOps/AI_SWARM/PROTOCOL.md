# Multi-AI Launch Protocol — 2026-10-06 → 2026-10-16

## Objective
Create a measurable release jump across the ecosystem without wasting compute or duplicating work. GitHub is the handoff bus between agents. GPT is the final reviewer/integrator; specialist agents implement bounded work and submit PRs.

## Priority order
1. **P0 Visual/Motion quality** — preserve the approved Fitness V2 image quality and make exercise motion automatic/continuous; raise game animation/camera/lighting quality.
2. **P0 Release blockers** — build, runtime, auth, Health Connect, Android API 36, signing, Play/Web deployment, physical-device evidence.
3. **P1 User-visible completeness** — real flows, working buttons, offline behavior, admin/control surfaces, Arabic RTL + English LTR.
4. **P1 Reliability/security** — tests, crash/error paths, secret isolation, rollback, observability.
5. **P2 Expansion** — only after release-critical paths are green.

## Scientific resource rule
For each candidate task estimate: `impact × launch-criticality × confidence / (cost + conflict-risk + repetition-risk)`. Execute the highest score first. Do not spend an expensive model on mechanical formatting, repeated audits, or a gate already proven PASS.

## Provider routing
- Use the strongest coding/reasoning agent for architecture, hard bugs, cross-module changes and review.
- Use a visual/multimodal-capable agent for motion/asset/runtime visual evaluation.
- Use cheaper/free coding agents for isolated implementation, tests, docs and repetitive migrations.
- Use local/open-source tooling for deterministic conversion/render/build tasks where model reasoning is unnecessary.
- A second model reviews only high-risk or high-impact changes; do not run every task through every model.

## Git workflow
1. Read `AGENTS.md`, this protocol, and `STATE.json`.
2. Pull the latest project-specific canonical branch.
3. Create `agent/<provider>/<lane>/<yyyymmdd>`.
4. Implement one bounded task to completion.
5. Test/build/render.
6. Commit with evidence.
7. Open a PR; never merge directly to production/release branches.
8. GPT Integrator reviews diff + evidence, requests fixes if needed, then merges only when gates pass.

## Project isolation / canonical starting points
- **Top Hero Fit Fitness V2:** `release/fitness-v2-rebuild-20261002`; accepted visual baseline; motion becomes automatic while retaining image quality.
- **THF platform/apps:** preserve existing canonical lineage and consume shared components only through reviewed merges.
- **RuinsCiv / EndCiv / THF games:** use project-specific branches/ReleaseOps paths; no WAVE secrets/assets.
- **WAVE_MAWJA:** standalone operational stream; never mix secrets/source/runtime into THF checkpoints.
- **Media / Arena Social / OnePublish / TokenOps:** keep product identity and release artifacts isolated even if coordination metadata lives in the central repo.

## Motion acceptance gates
### 2D exercise demonstrations
- same or better source image quality as approved baseline;
- automatically advances; no tap required;
- smooth deterministic loop with no visible jump that harms instruction clarity;
- anatomy/posture remains correct in every frame;
- preload/cache and offline availability;
- lifecycle-safe pause/resume;
- runtime evidence on Android and web where supported.

### 3D/game motion
- correct skeleton/clip mapping;
- idle/walk/run/action transitions blend cleanly;
- foot contact/IK or equivalent anti-sliding strategy where supported;
- camera/framing avoids clipping and preserves playability;
- lighting/shadows/materials remain coherent;
- representative Android performance evidence before release.

## 10-day phases
- **D1–D2:** lock baselines, connect agents, eliminate broken CI/no-job gates, ship Fitness auto-motion prototype and first game motion benchmark.
- **D3–D5:** parallel specialist implementation across Fitness/apps/games/WAVE with daily integrator merges.
- **D6–D7:** full build/runtime/device/web passes; fix only evidence-backed defects.
- **D8–D9:** release candidates, Play/Internal/web deployment, regression/security/rollback verification.
- **D10:** freeze feature expansion; only blocker fixes, exact-candidate verification, launch evidence and handoff.

## Merge policy
No PR is merged because an agent says it is complete. Merge requires evidence appropriate to the change. Any visual regression versus the accepted baseline is a failed gate even if automated tests pass.
