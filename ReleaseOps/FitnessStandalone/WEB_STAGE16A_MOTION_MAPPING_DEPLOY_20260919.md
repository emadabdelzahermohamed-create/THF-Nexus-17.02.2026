# THF Fitness Web Stage16A exercise-motion deployment — 2026-09-19

Production URL: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`
AppDeploy source snapshot: `1789820641840`
QA screenshot run: `1789820659833`

## Completed
- Active workout now passes the current exercise identity into the canonical MPFB/MakeHuman Stage16A renderer.
- Stage16A renderer selects an animation clip by exercise-name token when the canonical 195-clip asset contains a matching clip; otherwise it stays inside the canonical asset and uses an idle/breath/stand clip. No legacy humanoid fallback exists.
- Renderer restarts/crossfades motion when exercise intent changes and keeps the canonical GLB URL pinned.
- Active-session copy explicitly distinguishes demonstrated animation from sensed/verified form; no sensor verification is claimed without device evidence.
- Existing premium session composition, camera, ACES tone mapping, soft shadows and floor contact presentation remain enabled.
- Production QA contract now covers exercise-linked Stage16A motion, transition behavior and the honest sensor boundary.

## Runtime evidence
- Deployment reached terminal `ready`.
- Frontend errors: 0.
- Backend errors: 0.
- Network errors: 0.
- Desktop and mobile QA screenshots generated under run `1789820659833`.

## Fail-closed boundaries
- Token-based clip selection is an initial deterministic mapping hook, not certification that every exercise has a biomechanically correct animation.
- Foot IK/contact is not yet certified.
- Physical Android/GPU verification of 137 joints / all 195 clips remains open.
- Automated QA screenshots may land on signed-out surfaces; P0 authenticated reference-quality acceptance remains open until direct visual evidence is captured.
- Health Connect physical permission/runtime evidence and Web↔Android cross-device synchronization remain open.
- Google Play Internal versionCode `50001` is already committed; physical tester install/runtime remains separate and open.
