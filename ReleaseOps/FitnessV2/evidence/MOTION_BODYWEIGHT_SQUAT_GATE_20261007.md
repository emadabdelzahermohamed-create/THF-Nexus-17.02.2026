# Fitness V2 automatic motion pilot — bodyweight squat

- Task ID: `fitness-v2-smooth-exercise-motion-v1`
- Base SHA: `aee279c215cc21b355b039c37c3c55656e804ed0`
- Scope: replace the manual start/end image toggle in the active workout with an automatic offline motion player.
- Video: `fitness-v2/android/app/src/main/assets/pulse/media/motion/bodyweight-squat.webm`
- Video SHA-256: `39aa95865b5f45746fe17faca5693deb33b9b5bab4930b4c8dab897ef569cbe7`
- Encoding: VP9 WebM, 364×272, 8 fps, 2.0 seconds, 56,612 bytes, muted seamless loop.
- Source sequence: 16 reviewed chronological frames, standing → parallel squat → standing.
- Contact sheet: `FITNESS_V2_BODYWEIGHT_SQUAT_MOTION_CONTACT_20261007.jpg`
- Contact-sheet SHA-256: `3d6acfa9cac59e2a28d625e2516377dc256879c0323772f571c2783e42e2b398`

## Runtime contract

- Active workout uses `<video autoplay muted loop playsinline preload="auto">` when a verified motion asset exists.
- Manual “change position” control is removed.
- Playback pauses when the workout screen is left or the document becomes hidden, then resumes on return.
- Exercises without reviewed motion remain explicitly labelled as reference images; they are not falsely presented as smooth motion.
- All assets remain packaged locally for offline use.

## Verification

- JavaScript syntax: PASS (`node --check`).
- Product catalog suite: PASS (13 tests).
- Fitness V2 source contract suite: PASS (15 tests).
- Video decode/metadata: PASS (`ffprobe`, VP9 364×272 at 8 fps, duration 2.0 s).
- Frame-level visual review: PASS for this bodyweight-squat pilot, backed by the 16-frame contact sheet.
- Hosted browser runtime capture: NOT CLAIMED. The managed browser cannot reach the isolated local server (`ERR_CONNECTION_REFUSED`).
- Full catalog motion: NOT COMPLETE. Only the reviewed squat asset is enabled; every additional exercise requires its own verified sequence.
