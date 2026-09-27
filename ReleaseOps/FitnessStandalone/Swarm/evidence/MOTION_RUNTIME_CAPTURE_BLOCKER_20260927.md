# Motion runtime capture blocker evidence — 2026-09-27

## Scope

This checkpoint resumed the active `P0_STAGE16A_MOTION_VISUAL_QUALITY_CLOSURE` task without using owner credentials. It audited the currently applied Stage16A source, retried the existing non-privileged workout fixtures, visually inspected the resulting runtime screenshots, and restored the production source version before ending.

No password, cookie, session token, private credential, protected API call, or server write was used.

## Source truth audited

Applied production source version `1790500694233` (v63) was inspected directly:

- Canonical GLB URL remains pinned to repository commit `6965062e0d438e865fb4b4bcb1cb97ed2dfdde38`.
- Renderer uses Three.js GLTF loading, ACES tone mapping, soft shadows, hemisphere/key/rim/fill/sculpt lighting, aspect-aware full-body framing, eased model-aware camera movement, and exercise-sensitive target-zone focus.
- The renderer exposes the real selected clip and keeps `name-match`, conservative `reference-proxy`, and `unmapped` states explicitly uncertified.
- The exercise target overlay is attached to resolved rig bones when available.
- Foot markers use foot-bone world positions, ground proximity, velocity thresholds, hysteresis, short dwell, and visual planted anchors.
- These contact hooks are visual feedback only. The runtime correctly states they are **not** pressure sensing and **not** certified IK; Motion PASS therefore remains fail-closed.
- The contract shown in source remains 137 joints / 195 clips / 0 legacy fallbacks.

## Runtime capture attempts

### Arabic workout fixture

- Applied source version: `1790500055575` (v58)
- Hard-coded fixture: `workout-ar`
- Deployment result: `ready`
- Frontend errors: 0
- Backend errors: 0
- QA result: `qa_snapshot: null` after an additional wait
- Interpretation: no screenshot or interaction evidence was emitted; no visual PASS claimed.

### English workout fixture

- Applied source version: `1790500635667` (v62)
- Hard-coded fixture: `workout-en`
- Deployment result: `ready`
- QA timestamp: `1790517902477`
- Mobile screenshot: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790517905893/mobile.png
- Mobile SHA-256: `dc997592207b1f028c97777eaf3f5a684df8bf5f0d79b69356159433eed5dec8`
- Web screenshot: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790517905893/web.png
- Web SHA-256: `739f20adbb43f5fe07f05a4e49bcbfecaa8cf37c0c4b71e8a903e99632b8fe2f`
- Visual inspection: the host-level `This app is paused — This app has reached its credit limit` overlay obscures the page. The captured page underneath is not a usable active-workout evidence frame. This screenshot proves the hosting blocker, not Stage16A motion quality.

## Production restore

The live app was restored to production source version `1790500694233` (v63) before this checkpoint ended.

- Deployment result: `ready`
- QA timestamp: `1790517964024`
- Mobile screenshot: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790517990315/mobile.png
- Mobile SHA-256: `6f0f8344f80d8176a45054d0cfefe85c9c000f0ba2804a1d964b9977f14f1f41`
- Web screenshot: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790517990315/web.png
- Web SHA-256: `5a3cf3249a65e1c3dab81525b8ace8648aae6ad8a39254f3f63eb2f40463e49e`
- Frontend errors: 0
- Backend errors: 0
- Network errors: 0
- Visual inspection: canonical Stage16A remains visible underneath the host pause overlay, but the overlay blocks normal public interaction and invalidates this screenshot as visual release proof.

## Tool boundary

No approved host-managed interactive browser capability was exposed in this run. A direct public-URL read through the available web retrieval tool rejected both `?visualQa=workout-ar` and `?visualQa=workout-en` as inaccessible. The existing AppDeploy QA pipeline was therefore the only authorized runtime capture mechanism used.

## Fail-closed decision and next action

Motion remains `PROGRESS`, not PASS. The blocker is now evidence-backed and narrower than an authentication gap: AppDeploy is serving a host-level credit-limit pause overlay, while the Arabic fixture emits no QA snapshot and the English fixture screenshot is obscured.

After the documented AppDeploy reset time `2026-09-28T00:00:00.000Z`:

1. Verify the host pause overlay is gone on v63.
2. Capture `workout-ar` and `workout-en` through the query-scoped, non-privileged fixture.
3. Record sequential frames or video for one complete Stage16A exercise path, including clip label, camera/framing, lighting/materials, transition state, rig-attached muscle context, and foot-contact indicators.
4. Restore and re-verify v63 if any temporary fixture version is applied.
5. Keep IK and biomechanical certification fail-closed unless supported by separate real evidence.
