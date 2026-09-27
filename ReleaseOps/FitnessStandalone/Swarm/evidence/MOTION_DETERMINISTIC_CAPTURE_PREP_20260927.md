# Stage16A deterministic bilingual capture preparation

- Timestamp: 2026-09-27T19:10:50Z
- Lane: Motion/3D only
- Target branch: `automation/fitness-swarm-motion-20260924`
- Applied AppDeploy source version: `1790500694233`
- Canonical model source commit: `6965062e0d438e865fb4b4bcb1cb97ed2dfdde38`
- Canonical GLB SHA-256: `4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f`
- Prepared patch SHA-256: `d2d136e50ed418d8ecbd03b608ebd5ef892144d461810c32e57c8703bb9c063e`

## Completed

Prepared a Motion-only patch against the currently applied AppDeploy source. It:

1. Adds query-scoped deterministic capture phases at `motionQaPhase=0|25|50|75`.
2. Freezes the selected real GLB animation at the requested normalized phase.
3. Waits 45 rendered frames for camera and contact-overlay settlement before exposing `data-motion-qa-ready=true`.
4. Exposes machine-readable `data-motion-status`, `data-active-clip`, phase, and readiness attributes.
5. Adds a localized Arabic/English QA-ready badge.
6. Locks playback, replay, speed, camera, focus, and mirror controls while deterministic capture is active so the pose cannot drift after readiness is declared.
7. Stops displaying a fabricated `195` count before the GLB has actually loaded.
8. Adds a bilingual mobile visual-evidence test contract.

The capture mode does not authenticate, write server data, replace Stage16A, or certify proxy clips as biomechanically correct. Normal playback remains the default when the query parameter is absent.

## Validation

| Gate | Result | Evidence |
|---|---|---|
| Patch application | PASS | `git apply --check --directory=motion-baseline` exited 0 |
| JSON parse | PASS | `jq empty motion-prep/tests.json` exited 0 |
| Whitespace/error scan | PASS | `git diff --check --no-index` emitted no diagnostics for all three changed files |
| Static capture contract | PASS | Required phase/readiness/control-lock tokens found; test count 7 |
| Canonical GLB animation contract | PASS | Parsed GLB contains exactly 195 animations and all 7 referenced clip names |
| TypeScript build | NOT RUN | The local workspace has no TypeScript/Vite dependency set, and the AppDeploy build is unavailable while the host credit gate is active |
| Live runtime/screenshots/video | BLOCKED | The host currently returns `CREDITS_USAGE_LIMIT_REACHED`; retry is recorded for after `2026-09-28T00:00:00Z` |

## Fail-closed status

This is prepared source evidence only. It is not deployed and does not satisfy the visual release gate. Motion remains `PROGRESS`, not `PASS`.

## Next action

After the host reset:

1. Apply the patch to AppDeploy and run its build/e2e/runtime gates.
2. Capture `visualQa=workout-ar` and `visualQa=workout-en` at phases 0, 25, 50, and 75 on a 390 px viewport.
3. Require `data-motion-qa-ready=true` before every capture.
4. Record a short normal-playback video after removing `motionQaPhase`.
5. Verify framing, lighting, muscle overlay, transition behavior, and truthful foot-contact hooks before considering visual PASS.
