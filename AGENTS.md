# THF Multi-AI Launch Contract

## Current execution priority — 2026-10-24
This section supersedes historical October 6–16 deadlines and old canonical pointers below. Active work is ONLY Fitness (four isolated lanes) and zero-upfront funding (one lane), through the user's next two-day sprint. Games/WAVE/Creator stay paused.

- Fitness canonical development branch: `agent/codex/fitness-recovery/20261023`. Read its live `ReleaseOps/FitnessStandalone/EXECUTION_20261024.md` and `RECOVERY_20261023.md` before any work. This branch is a development truth, not evidence of public release.
- Source notification candidate: PR82 / `agent/codex/live-notification/20261024`,51012; includes GPS PR81 and newer provenance fixes. Read current CI and merge state; never assume it shipped.
- Funding: `agent/codex/token-funding/20261023` receipts and `agent/codex/sponsorship/20261024` sponsorship draft. No verified revenue at this checkpoint.
- Only integrator changes canonical/release/version/Play; sensors, exercise experience, and phone QA have separate file/resource ownership. Check current ownership before shared operations; schedule staggering alone is not a lock.
- Save exact SHA/run/artifact/version/gate/next action before waiting. Optional auth must never stop independent app work. Unattended runs must not initiate interactive browser login. Record unavailable/declined auth once and move to executable work; don't retry it or bypass it.
- A tool timeout did not bound a prior auth handoff (~18min). Do not promise a guaranteed timeout or fix to ChatGPT's UI. Poll CI briefly and preserve durable checkpoints.
- Publish meaningful passing candidates through the existing Google Play Internal pipeline and verify committed track/version. Public Production additionally requires actual release gates; never call a build a Play release.
- Delete obsolete material only after references/dependencies and standalone replacement have been verified. Record reversible deletion manifest; preserve historical evidence, licenses, signing material and unrelated projects. No force push/history purge.

## Historical mission
Ship the THF ecosystem to the highest practical production quality within the 10-day launch window ending 2026-10-16 (Africa/Cairo). Git is the single source of truth. Never redo a gate already proven PASS for the same exact SHA/candidate.

## Mandatory startup
Before changing code, read:
1. `ReleaseOps/AI_SWARM/PROTOCOL.md`
2. `ReleaseOps/AI_SWARM/STATE.json`
3. The lane/project-specific current state, backlog, release evidence, and latest passing SHA.

## Global rules
- Keep projects isolated. Never mix WAVE secrets/source/runtime with THF or other projects.
- Never commit secrets, credentials, signing material, tokens, or private keys.
- Work on a dedicated branch: `agent/<provider>/<lane>/<yyyymmdd>`.
- One agent owns one bounded lane at a time. Do not edit another lane unless an explicit dependency requires a small compatible change.
- Every meaningful change must include tests/runtime evidence where applicable and a Git checkpoint.
- Do not claim visual, phone, Health Connect, Play, deployment, animation, or performance PASS without concrete evidence.
- Prefer existing code, approved assets, open/permissive sources, and already-authorized infrastructure. Avoid rebuilding integrations that already work.
- If blocked, record the blocker once and continue the next independent release-critical task instead of looping.

## Visual and animation priority
Animation is a P0 differentiator across fitness apps and games.

### Fitness baseline
The approved high-quality exercise imagery in `release/fitness-v2-rebuild-20261002` is the visual baseline. Preserve its image quality and exercise clarity.

### Motion requirement
For exercise demonstrations, motion must appear continuous and automatic without requiring the user to tap to advance frames. Prefer the lowest-risk implementation that preserves the approved artwork:
- timed frame sequences / animated image packages when the source is image-based;
- smooth looping with deterministic cadence;
- preloading/caching for offline operation;
- optional interpolation/cross-fade only when it improves continuity without distorting anatomy;
- no quality downgrade just to obtain movement;
- pause/resume with app lifecycle and battery-aware behavior;
- verify real runtime motion on representative screens.

For games/3D, preserve each project's approved modern avatar/world lineage and use proper animation blending, locomotion transitions, foot contact/IK where available, camera/framing, lighting, shadows, LOD and performance budgets. Do not substitute low-quality placeholder humanoids.

## Agent specialization
- **Motion/Visual agent**: animation loops, 2D/3D motion pipeline, render quality, cameras, lighting, runtime visual evidence, asset optimization.
- **App/Platform agent**: Android API 36, Health Connect, backend/data sync, offline, auth, build/sign/release gates.
- **Game agent**: Godot gameplay, world/avatar/motion, networking/offline/LAN, Android packaging, runtime/performance gates.
- **Web/Media agent**: web/admin/publisher/media pipelines, live endpoints, transcoding/HLS, deployment and reliability.
- **Reviewer/Integrator (GPT)**: architecture review, regression/security review, PR conflict resolution, release candidate selection, final merge and launch verification.

## Pull request contract
Every PR must state:
- lane and project;
- base SHA and resulting SHA;
- exact files/scope changed;
- tests/build/runtime evidence;
- user-visible improvement;
- remaining blocker/risk;
- whether it changes secrets, signing, payments, Play or production deployment (normally NO unless explicitly authorized).

The Integrator may reject or split PRs that mix unrelated projects, duplicate completed work, reduce visual quality, or lack evidence.
