# Gemini Agent Entry Point

Before any analysis or code change, read in this order:
1. `AGENTS.md`
2. `ReleaseOps/AI_SWARM/PROTOCOL.md`
3. `ReleaseOps/AI_SWARM/STATE.json`
4. `ReleaseOps/AI_SWARM/PROVIDER_MATRIX.md`
5. `ReleaseOps/AI_SWARM/FALLBACK_ROUTER.json`
6. `ReleaseOps/AI_SWARM/START_PROMPTS.md`
7. GitHub Launch Board issue #41 and the lane-specific issue/PR.
8. The project-specific current release/evidence state.

GitHub is the source of truth. Never redo a verified PASS for the same SHA and never duplicate an active task with the same `task_id + base_sha`. Work only on a dedicated `agent/gemini/<lane>/<yyyymmdd>` branch or a unique compatible derivative. Keep projects isolated and keep secrets/signing material/API keys out of Git. Never push directly to `main` or canonical release branches. Open a PR with tests/build/runtime evidence; GPT Integrator decides merge/release.

Provider/quota rule: a 429, exhausted quota, or provider outage is a routing event, not a project blocker. Record it once, stop tight retries, preserve the task acceptance criteria and base SHA, and let the router move the task to the next compatible provider. Never purchase, upgrade, enable billing/auto-top-up, or introduce a paid release dependency without explicit owner approval.

Approved baselines are rollback points, not ceilings. You may improve or replace an approved implementation only when evidence shows the candidate is equal-or-better overall. A/B comparison must include functionality, visual clarity, runtime quality, performance and regression risk.

P0 shared visual rule: preserve or improve the approved high-quality Fitness V2 exercise imagery and implement automatic continuous motion without requiring a tap. Prefer deterministic cached/offline frame-sequence or animated-image pipelines when they preserve anatomy/instruction quality better than a lower-quality 3D substitute. Require real runtime evidence, smooth loops, lifecycle-safe pause/resume and no visual regression.

For games, prioritize real gameplay, animation blending, locomotion, foot contact/IK or anti-sliding strategies where supported, camera/framing, lighting/shadows, mobile performance, Android API 36/arm64 packaging and runtime evidence.

Every meaningful completion must report base SHA, resulting SHA, scope/files changed, tests/build/runtime evidence, user-visible result, remaining risk/blocker and PR/checkpoint. Never claim phone, Health Connect, Play, deployment, animation, performance or visual PASS without concrete evidence.
