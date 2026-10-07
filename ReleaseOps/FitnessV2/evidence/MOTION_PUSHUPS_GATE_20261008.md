# Fitness V2 automatic motion — push-ups

- Task ID: `fitness-v2-smooth-exercise-motion-v2`
- Base SHA: `238ab40bd51d8d5f24d6b857ef35f87b1feb9ba6`
- Scope: add a second reviewed automatic offline exercise cycle without changing the approved workout-player contract.
- Video: `fitness-v2/android/app/src/main/assets/pulse/media/motion/pushups.webm`
- Video SHA-256: `5b71b9a0d9f79f2fbff2f8b6b6e5bbe9610c82c0061a1636ea322f01e07eaad0`
- Encoding: VP9 WebM, 384×256, 8 fps, 2.0 seconds, 87,752 bytes, muted seamless loop.
- Source: the approved Unlicense free-exercise-db Pushups start/end photographs, expanded to a reviewed 16-frame top → bottom → top cycle.
- Contact sheet: `FITNESS_V2_PUSHUPS_MOTION_CONTACT_20261008.jpg`
- Contact-sheet SHA-256: `767e4aeb465008fb8091e62b4fb249e74024d0686f13e0ae8bc86c633aa0b528`

## Visual acceptance

- One athlete only; no duplicated or missing limbs.
- Hands and toes remain planted through the repetition.
- Elbows flex naturally while head, spine, hips, knees, and ankles preserve a controlled plank.
- Frames 1–8 provide the descent; the reviewed sequence mirrors the same poses for a deterministic ascent and seamless loop.
- Camera, crop, lighting, clothing, and gym background stay consistent with the approved references.

## Verification

- Frame count: PASS (16 decoded frames).
- Video decode/metadata: PASS (`ffprobe`: VP9, 384×256, 8 fps, 2.0 seconds).
- Frame-level visual review: PASS for this push-ups asset, backed by the committed contact sheet.
- Manifest contract: two verified automatic-motion exercises; every manifest asset is SHA-256 checked by the product test.
- Full catalog motion: NOT COMPLETE. This change raises reviewed coverage from 1/112 to 2/112 exercises.
- Physical Android runtime evidence: NOT CLAIMED; CI packaging is required after this commit.
