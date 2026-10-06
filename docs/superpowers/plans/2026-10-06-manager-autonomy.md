# Autonomous Manager + Multi-AI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Operate the ecosystem through a Git-centered autonomous manager that preserves rollback baselines, routes specialist agents efficiently, prioritizes animation/visual quality, and uses Replit as a control surface rather than a competing source repository.

**Architecture:** GitHub is the durable system of record. Specialist agents work in isolated lanes and submit evidence-backed changes; GPT integrates. Replit provides a lightweight operational dashboard and may later own bounded web/admin tasks, but official product changes still flow through canonical Git checkpoints.

**Tech Stack:** GitHub issues/PRs/actions, ChatGPT automations, Replit Agent/web app, existing Android/web/Godot/project toolchains.

**Spec:** `docs/superpowers/specs/2026-10-06-manager-autonomy-design.md`

## Global Constraints
- Preserve immutable rollback references for superseded accepted candidates.
- Never commit credentials, signing material, or production secrets.
- Keep WAVE and every independent product isolated from THF source/runtime/secrets.
- Animation/visual quality is P0, but visual gains cannot regress correctness/performance/offline behavior.
- Do not redo a PASS gate for the same exact SHA/candidate.
- Replit is not the canonical product repository.

## Review Focus
- Candidate looks better but increases memory/battery cost beyond acceptable mobile behavior.
- Two agents edit the same ownership area and produce conflicting PRs.
- A visually impressive motion candidate distorts exercise anatomy or technique.
- A new provider/tool silently bypasses project isolation or introduces secrets into logs/Git.
- Dashboard status drifts from GitHub truth and reports speculative completion.

---

### Task 1: Persist autonomous-manager policy

**Files:**
- Existing: `AGENTS.md`
- Existing: `ReleaseOps/AI_SWARM/PROTOCOL.md`
- Existing: `ReleaseOps/AI_SWARM/STATE.json`
- Create/maintain: manager-autonomy spec and plan

**Interfaces:**
- Consumes: existing AI Swarm protocol and launch board.
- Produces: explicit baseline-vs-candidate and rollback policy all agents can read.

- [ ] Update agent protocol so previously accepted versions are rollback baselines, not ceilings.
- [ ] Require candidate-vs-baseline evidence for material visual/animation changes.
- [ ] Record the current accepted Fitness V2 reference SHA before motion work supersedes it.
- [ ] Verify protocol/state remain valid JSON/Markdown and contain no secrets.
- [ ] Commit the policy checkpoint.

### Task 2: Replit operations dashboard

**Files:**
- Replit app only; no product source fork.

**Interfaces:**
- Consumes: public/canonical GitHub repository status, launch-board conventions, lane names and evidence vocabulary.
- Produces: one operational view of lanes, PRs/checkpoints, blockers, baselines/candidates and launch progress.

- [ ] Create a Replit web app named `THF AI Swarm Control`.
- [ ] Make the dashboard clearly treat GitHub as source of truth.
- [ ] Include lane cards for Integrator, Motion/Visual, Fitness+Apps, Games and Independent Products.
- [ ] Include baseline vs candidate status, evidence state, blocker state, next action and launch deadline.
- [ ] Include strong warnings against speculative PASS and cross-project secret/source mixing.
- [ ] Validate the preview works and shows empty/error states honestly if GitHub data cannot be fetched.

### Task 3: Resource-routing policy

**Files:**
- `ReleaseOps/AI_SWARM/PROTOCOL.md`
- `ReleaseOps/AI_SWARM/STATE.json`

**Interfaces:**
- Consumes: agent capabilities and current blocker state.
- Produces: deterministic task-selection rule and provider ownership map.

- [ ] Add impact/quality/confidence versus cost/conflict/repetition scoring as the routing rule.
- [ ] Reserve expensive second-model review for high-risk/high-impact tasks.
- [ ] Keep deterministic conversion/build/formatting work on local/CI/open-source tooling where practical.
- [ ] Verify no active automation duplicates another lane's ownership.
- [ ] Commit updated routing state.

### Task 4: Fitness motion baseline and upgrade gate

**Files:**
- Project-specific Fitness V2 motion/demo implementation and evidence paths determined from the canonical branch.

**Interfaces:**
- Consumes: `release/fitness-v2-rebuild-20261002` accepted visual reference and Motion issue #42.
- Produces: evidence-backed motion candidate and preserved rollback reference.

- [ ] Freeze the accepted baseline SHA/reference before changing the motion pipeline.
- [ ] Implement or accept the best continuous automatic-motion candidate available from the Motion specialist.
- [ ] Verify technique/anatomy, loop continuity, source quality, offline/cache, lifecycle and performance.
- [ ] Compare candidate against baseline; reject if the total product score is worse.
- [ ] Merge only after evidence-backed review.

### Task 5: Ecosystem-wide execution loop

**Files:**
- GitHub issues/PRs/state and project-specific release evidence.

**Interfaces:**
- Consumes: specialist PRs/checkpoints and current launch board.
- Produces: merged release improvements and updated next-task routing.

- [ ] Every integrator cycle, select the highest-impact unblocked task rather than the oldest task.
- [ ] Reject duplicate work, mixed-project changes, missing evidence and visual regressions.
- [ ] Preserve rollback reference before adopting a materially different candidate.
- [ ] Update launch-board/state after every accepted merge or hard blocker.
- [ ] Freeze feature expansion near launch and prioritize exact-candidate verification/release blockers.
