# Stage16A first-paint and framing runtime evidence — 2026-09-27

Lane: Motion/3D only  
Branch: `automation/fitness-swarm-motion-20260924`  
Live app: https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/

## Canonical asset provenance

- Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
- Source commit pinned by runtime: `6965062e0d438e865fb4b4bcb1cb97ed2dfdde38`
- Path: `public-assets/fitness/stage16a/thf_mpfb_stage16a_ual12_animated.glb`
- Git blob: `0ff06a17f4c3d1da96687e5b440ea910b2b989da`
- Size: 26,296,432 bytes
- Runtime contract: MPFB/MakeHuman Stage16A, 137 joints, 195 clips, zero legacy fallback.

## Changes completed

1. Removed the first-visit critical-path wait on `CacheStorage.put()`; the GLTF loader now starts directly from the pinned canonical URL.
2. Kept durable browser caching best-effort and asynchronous after the canonical model is decoded.
3. Added high-priority canonical-model preload and a truthful progress/error surface; errors explicitly state that no fallback model was substituted.
4. Added aspect-aware camera distance derived from model width, height, camera FOV, and live canvas aspect.
5. Reserved additional safe framing margin for the compact public preview.
6. Removed the duplicate internal motion readout from the compact preview so it no longer obscures the body.
7. Added regression coverage for direct streaming, cache warmup, truthful failure semantics, aspect-aware framing, and legacy fallback rejection.

## Deployment progression

- `1790482459656`: direct render path; canonical model became visibly rendered on both QA viewports.
- `1790482608410`: aspect-aware fit restored the head and hands to frame.
- `1790482730395`: compact safe margin plus duplicate-readout removal; final checked snapshot.

## Final QA evidence

- QA timestamp: `1790482744576`
- Mobile screenshot (390×844): https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790482769518/mobile.png
- Mobile SHA-256: `f167aac9e568d5edf057a33c6efef1b386df96069929de03267464ab984ff8aa`
- Web screenshot (1280×720): https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790482769518/web.png
- Web SHA-256: `4e47548bc44e3c25a8ec3d56fada8132a4c46219195bfa1a4e6b76335c7a584f`
- Frontend errors: 0
- Backend errors: 0
- Network errors: 0

Visual inspection confirms that the real canonical human is now rendered rather than a blank canvas on both viewports. The final desktop capture shows the head, hands, torso, and legs inside the stage; the compact preview has no duplicate internal readout over the body. The mobile first viewport shows the head, torso, and hands, with the remainder continuing below the viewport fold.

## Fail-closed boundaries

This evidence does **not** mark the Motion lane PASS:

- The captured route is the signed-out compact preview, not an authenticated workout.
- Exercise-specific animation, cross-fade transitions, replay, camera controls, muscle overlays, foot-contact hooks, and motion mapping are not visually proven by this capture.
- The external public-preview caption still intersects the extreme lower stage edge; its layout belongs to the Product surface.
- No physical-device, Android GPU, offline-first-install, phone, or Play result is claimed.
- Clip and joint metadata alone are not used as visual PASS evidence.

Result: **PROGRESS**.
