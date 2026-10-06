# THF Multi-AI Launch Contract

## Mission
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
