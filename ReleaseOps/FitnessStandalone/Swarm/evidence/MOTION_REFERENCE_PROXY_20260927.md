# Stage16A reference-motion mapping evidence — 2026-09-27

## Canonical asset inspection

The pinned GLB `public-assets/fitness/stage16a/thf_mpfb_stage16a_ual12_animated.glb` was parsed directly from its binary JSON chunk.

- Source commit: `6965062e0d438e865fb4b4bcb1cb97ed2dfdde38`
- Blob SHA: `0ff06a17f4c3d1da96687e5b440ea910b2b989da`
- SHA-256: `4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f`
- Bytes: `26296432`
- Contract: 137 joints / 195 clips / 0 legacy fallback
- Parsed result: exactly 195 named clips, including `UAL1_Crouch_Idle_Loop`, `UAL1_Crouch_Fwd_Loop`, `UAL1_Push_Loop`, `UAL1_Jump_Loop`, `UAL1_Jog_Fwd_Loop`, `UAL2_Slide_Loop`, and `breathe`.

## Implemented mapping

AppDeploy source version `1790500307224` (v60) replaced broad token-only matching with a conservative three-state mapping contract:

- `name-match`: a clip name contains an exercise token; still explicitly uncertified.
- `reference-proxy`: a small allowlist maps an exercise to the closest available Stage16A rhythm reference.
- `unmapped`: the renderer falls back to a neutral idle/reference stance and does not claim instruction.

Allowlisted reference proxies:

- Bodyweight squat / wall sit → `UAL1_Crouch_Idle_Loop`
- Reverse lunge / mountain climber → `UAL1_Crouch_Fwd_Loop`
- Incline push-up / shoulder tap → `UAL1_Push_Loop`
- Jumping jacks → `UAL1_Jump_Loop`
- High knees → `UAL1_Jog_Fwd_Loop`
- Lateral shuffle → `UAL2_Slide_Loop`
- Box breathing → `breathe`

The runtime copy names the actual clip and states that the proxy shows rhythm only and is not certified biomechanical instruction. Unmapped exercises remain fail-closed.

## Deployment and regression proof

- Mapping build: `1790500307224` (v60), ready, frontend/backend errors 0.
- Deterministic fixture build with external embed suppression: `1790500635667` (v62), ready, frontend/backend errors 0.
- Final production build containing the mapping with normal auth restored: `1790500694233` (v63), ready.
- Final public mobile screenshot: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790500731642/mobile.png
- Mobile SHA-256: `3b1ac322eb9f4026d833fae8fa268561fb6e8fec1cd5afdd5cce1ed96598817c`
- Final public web screenshot: https://appdeployai-v2-qa-screenshots.s3.us-east-1.amazonaws.com/thf-fitness-pulse-ul26f1/1790500731642/web.png
- Web SHA-256: `ba19c001464503006ba6fee5c56dfa92d7ad5bcf7df7ce46560ddc7e1abf5c8e`
- Final QA timestamp: `1790500707991`; frontend/network errors 0; backend errors 0.
- Visual regression result: the canonical human is visible on the restored production root.

## Fail-closed boundary

AppDeploy returned no QA screenshot for the temporary `workout-ar` / `workout-en` fixture versions, including a second application attempt of v60. No approved host-managed interactive browser was available. Therefore the reference clip, blend, camera controls, muscle overlay, and foot-contact hooks are not visually proven in an active workout in this checkpoint. Motion remains `PROGRESS`, not PASS.
