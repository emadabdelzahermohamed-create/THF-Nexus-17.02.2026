# THF Fitness Motion — Stage16A exercise-blend runtime checkpoint (2026-10-02)

## Scope

Motion/3D only. This checkpoint does not claim visual, GPU, phone, Health Connect, or release PASS.

## Published runtime

- AppDeploy application: `thf-fitness-pulse-ul26f1`
- Production snapshot: `1790910310382` (`v67`)
- Public URL: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/
- Deployment result: `ready`
- Frontend errors: `0`
- Backend errors: `0`
- Network errors in production QA snapshot: `0`
- Post-restore QA capture IDs: `1790910512577/mobile.png` and `1790910512577/web.png`
- Immutable source baseline: `1790568670855` (`v66`)
- Exact deployed source delta: `MOTION_EXERCISE_BLEND_PATCH_20261002.patch`
- Patch checkpoint commit: `153e62163e253e5dd8b02d5d50e7e374c4f63cf2`

## What changed

The bodyweight-squat path no longer reuses `UAL1_Crouch_Idle_Loop` as a rhythm-only proxy. It now:

1. selects the canonical `idle` and `UAL1_Crouch_Idle_Loop` clips from the real Stage16A GLB;
2. freezes both source clips at a stable representative pose;
3. blends their weights through a four-second upright → descent → bottom → ascent curve;
4. maps deterministic QA phases 0/25/50/75 to weights 0/0.5/1/0.5;
5. exposes `data-motion-status=exercise-blend` and both source clip names after the GLB is ready;
6. keeps controls locked during deterministic capture and leaves the ordinary playback path unchanged;
7. keeps biomechanical approval fail-closed pending real GPU runtime inspection.

## Canonical-asset CPU evidence

Because the authorized cloud browser exposes no WebGL context, a deterministic open-source CPU evidence route was added:

- Tool: `ReleaseOps/FitnessStandalone/Swarm/tools/stage16a_cpu_preview.py`
- Tool commit: `821a9879cc12d153dfce79f2884b1e47ad8b91fb`
- Tool SHA-256: `c5e62bbf25e29d9bc0ffbaf4153727b5496f6064191029ba0f0a2daadd97a5ca`
- Source asset: `public-assets/fitness/stage16a/thf_mpfb_stage16a_ual12_animated.glb`
- Source asset SHA-256: `4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f`
- Source bytes: `26,296,432`
- Parsed joints: `137`
- Parsed animation clips: `195`
- Skinned vertices per frame: `19,166`
- Rasterized triangles per frame: `35,492`
- Contract result: `CPU_PREVIEW_CONTRACT_PASS`
- Manifest SHA-256: `ba2dc0556ecfc9fe7a1869b3578432a6eaa941c26a836a6da8d15c207ef86f5f`

| Phase | Blend | Rendered stature | PNG SHA-256 |
|---|---:|---:|---|
| 0% | 0.0 | 1.660018 | `127ae5086ef6524ee401bed3a36a9ffc0e2e67c36375f8ed0f54245db9f6d2b2` |
| 25% | 0.5 | 1.485955 | `b41732aec599b57eed764365f17aa6b0bd8993debc0f6169ade27c414d7bc123` |
| 50% | 1.0 | 0.949534 | `3b148a5df4bf1497dfe58b45c9a4ed3d772feb091bac6258a56db49b75c0dba7` |
| 75% | 0.5 | 1.485955 | `d81b3a29f6281037a4b892ccb2dece179330e57a7f89d69b5019b6ea7750b5f6` |

The inspected CPU frames show the real textured human progressing from upright stance through controlled descent to a deep crouch and back through the matching ascent phase. This validates the asset, skin, source poses, and blend geometry without pretending it is browser/GPU proof.

## Bilingual active-workout runtime

Read-only public fixture checks were run after `v67`:

- Arabic: `?visualQa=workout-ar&motionQaPhase=25`; the active session, Bodyweight Squat, set 1/3, 40 s work, 45 s rest, next movement, technique/muscle control, and RTL document direction rendered.
- English: `?visualQa=workout-en&motionQaPhase=50`; the same active-session journey rendered with `lang=en` and `dir=ltr`.
- Both fixtures remained non-privileged and in-memory.
- The cloud browser returned no WebGL context. The new guarded renderer showed the localized canonical-render-unavailable state inside the workout instead of blanking the page, and no fallback humanoid was substituted.

## Fallback record

1. AppDeploy build/runtime provider: succeeded for `v67`.
2. AppDeploy route-specific temporary capture `1790910393702`: built and became ready, but emitted no route-specific QA snapshot; production was immediately restored to `v67`.
3. Authorized cloud browser: exercised both active-workout routes, but its GL vendor is disabled and therefore cannot provide Stage16A GPU frames.
4. Local open-source CPU renderer: succeeded and produced deterministic real-asset pose evidence.
5. The required local gateway file `/home/gamalammulazim_gmail_com/AUTH_FALLBACK_GATEWAYS.md` was absent; a workspace/repository filename search also returned no copy. No paid provider or new secret was used.

## Gate

`PROGRESS`, not `PASS`.

Open evidence remains:

- GPU-capable Arabic RTL and English LTR active-workout frames at 0/25/50/75;
- ordinary-playback video showing the full squat cycle and transitions;
- visual inspection of camera framing, materials, foot contact, and contact-anchor behavior on the published `v67` code;
- confirmation that `data-motion-status=exercise-blend` appears after successful GLB load.

Next action: run the two public fixture URLs in an authorized GPU/WebGL-capable runtime, capture phases 0/25/50/75 and normal playback, inspect foot contact and framing, then update this gate without re-running the already-passed source/build/CPU checks.
