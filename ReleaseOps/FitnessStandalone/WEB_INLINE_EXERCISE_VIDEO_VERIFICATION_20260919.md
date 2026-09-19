# THF Fitness — inline exercise video verification — 2026-09-19

Production: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/
AppDeploy snapshot: `1789822954470`
QA screenshot run: `1789822971776`

## Completed
- Exercise demonstration video is embedded 16:9 inside the active workout and exercise-detail surfaces; the normal flow no longer requires leaving THF to watch the demonstration.
- The schematic CSS stick-figure movement guide is no longer the primary movement reference.
- Canonical MPFB/MakeHuman Stage16A remains available as an enhanced 3D path; no legacy humanoid was introduced.
- Five existing catalog mappings were replaced with freshly web-verified exercise-specific YouTube demonstrations: Bodyweight Squat, Glute Bridge, Reverse Lunge, Hip Hinge, Bird Dog.
- Runtime deploy reached `ready` with 0 frontend, 0 backend and 0 network errors.

## Fresh verification sources
- Bodyweight Squat: YouTube video `IYOMod4X25Y` (title explicitly states proper Bodyweight Squat).
- Glute Bridge: OriGym exercise demo `3nQeWv5Tx1A`.
- Reverse Lunge: OriGym exercise demo `aoT5WAJot-U`.
- Hip Hinge: FITTR exercise video `gHASRYzwV1A`.
- Bird Dog: FITTR exercise video `GlOpvsoCzeU`.

## Fail-closed remainder
- The remaining embedded mappings must be individually verified for exercise identity/form and embeddability before they count as curated/certified media.
- Video matching is not biomechanical certification of Stage16A animation.
- Physical Android playback/GPU/audio acceptance remains open.
- Authenticated reference-screenshot visual acceptance remains open.
