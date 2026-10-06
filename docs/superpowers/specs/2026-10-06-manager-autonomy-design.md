# Autonomous Manager + Multi-AI Design

## Intent
The user delegates product/technical management authority to improve the ecosystem automatically. Previously approved versions remain rollback references, not quality ceilings. The system may replace or redesign approved visuals, flows, architecture, animation, or tooling when the change has a measurable quality/release benefit.

## Non-negotiable safety rails
- GitHub remains the single source of truth for code and durable execution state.
- Every product keeps an isolated source/runtime/secrets boundary.
- Never commit credentials, signing keys, API secrets, private tokens, or production secrets.
- Any approved/stable candidate that may be superseded must remain recoverable by immutable SHA/tag/evidence.
- No destructive deletion of the last known-good candidate.
- Any change with release, payment, Play, production, signing, or security impact requires evidence appropriate to the risk.

## Manager autonomy policy
The manager may automatically:
- alter product architecture, UX, visual language, animation, implementation details, model/provider routing, schedules, and task ownership;
- replace a previously accepted design when a better result can be proven;
- reject agent output even if functionally correct when it regresses quality, performance, safety, maintainability, or release readiness;
- pause low-value work and redirect resources to higher-value release blockers;
- use specialist AI agents only for the work they are best suited for;
- create bounded experiments when uncertainty is high, provided production branches are not polluted.

The manager must preserve:
- a rollback SHA/reference for every superseded accepted baseline;
- project identity and isolation;
- verifiable release evidence;
- explicit blockers when an external owner-only action is truly required.

## Baseline-vs-candidate rule
Every material improvement is evaluated as `candidate` versus `baseline`.

A candidate can replace the baseline only when it wins overall on the dimensions relevant to that change:
1. user-visible quality and clarity;
2. functional correctness;
3. runtime/performance/battery/memory where applicable;
4. offline/reliability behavior where applicable;
5. maintainability and release risk;
6. accessibility/localization and device compatibility where applicable.

A visually better candidate may still fail if it harms correctness or performance. A faster candidate may fail if it visibly lowers the product standard. When evidence is mixed, keep the baseline and continue iteration.

## Animation policy
Animation remains a P0 differentiator across fitness and games.

For Fitness V2, the current high-quality exercise imagery is a rollback baseline only. The manager may improve or replace it when a candidate is demonstrably better. Preferred progression:
1. continuous automatic motion using the existing high-quality sequence when that preserves anatomy and clarity;
2. improve timing/interpolation/camera/composition when it raises perceived quality without distorting exercise technique;
3. replace the asset pipeline only if the new pipeline beats the baseline in realism, instructional clarity, offline behavior, performance, and consistency.

For games, prioritize high-quality locomotion/action blending, foot-contact/anti-sliding, camera/framing, lighting/shadows/material consistency, LOD, and mobile performance. Placeholder humanoids or low-quality animation are not acceptable merely to increase feature count.

## Agent routing
- Motion/Visual agent: animation, rendering, 2D/3D motion quality, cameras, lighting, visual evidence.
- App/Platform agent: Android/API36, Health Connect, auth/data/offline/build/release.
- Game agent: gameplay, world/avatar/motion/network/offline/mobile performance.
- Web/Admin agent: control surfaces, admin/publisher, monitoring, web deployment, media workflows where applicable.
- GPT Integrator: architecture review, task routing, conflict prevention, regression/security review, final candidate selection and official merges.

## Replit role
Replit is not a second source repository. Its first role is an operations/control surface that reads durable status from GitHub and helps expose:
- active lanes and owners;
- latest PR/checkpoint/build/deploy state;
- current blockers and owner-only actions;
- baseline and candidate SHAs;
- animation/visual quality gates;
- launch-window progress and next highest-value task.

Replit may also implement bounded web/admin work where it has clear ownership and no competing agent edits. Product source must still be checkpointed back through the canonical Git workflow before official adoption.

## 10-day operating principle
Maximize `release impact × quality gain × confidence / (resource cost + conflict risk + repetition risk)`.

Do not spend scarce model quota on deterministic tasks that local tooling/CI can perform. Do not have multiple expensive models solve the same low-risk task. Use a second-model review only for high-impact/high-risk changes.

## Completion standard
A feature is not complete because an agent says it is complete. It is complete only when the required user-visible/runtime/build/test/deployment evidence exists and the integrator accepts it against the current baseline.
