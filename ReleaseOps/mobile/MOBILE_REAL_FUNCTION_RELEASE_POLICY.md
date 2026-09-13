# THF Mobile Real-Function Release Policy / سياسة إصدار الهاتف الحقيقي

This policy is a release blocker for every THF Android app/game. A source/static PASS is not enough to label a build FINAL, PLAY_READY, or production-ready.

## Mandatory release sequence

1. **Exact source** — build only from the current canonical source SHA; no template-only or fallback-only candidate may be promoted.
2. **Android build** — compile/target SDK 36, correct final applicationId, arm64-v8a for public game candidates, no bundled production secrets.
3. **Real payload** — the APK/AAB must contain the product/game payload. A Godot engine/template APK with no exported project assets is an automatic FAIL.
4. **Phone layout** — games must use mobile-safe landscape behavior (`sensor_landscape` for Terra/Rift), expandable aspect handling, touch controls, and no desktop-window override that creates a 16:9 strip inside portrait. Apps must use responsive phone layouts with safe areas and RTL support where applicable.
5. **Functional behavior** — login/navigation/buttons must execute real behavior. Online-only actions require a reachable HTTPS/WSS backend. Offline mode is allowed only for features that genuinely work locally; economy/social/ranked state must never be faked.
6. **Physical-device acceptance** — install, launch, touch, rotation/orientation, background/resume, offline/network transition, and low/mid-tier phone smoke must PASS. Games additionally require avatar/model loading, movement, camera, gameplay interaction/combat where applicable, and FPS/RAM/thermal observation.
7. **Store gate** — only after device PASS may signing/Play Internal testing proceed. Production signing and irreversible store actions remain separate controlled gates.

## THF product rules retained

- targetSdk 36 and package identities stay locked.
- Arabic/English and the existing 20-locale contracts remain preserved where the product provides them.
- Data Saver / Reduce Motion / High Contrast / accessibility controls remain release requirements where already implemented.
- No pay-to-win in Arena/Rift; no purchase may falsify fitness evidence or learning mastery.
- WAVE MAWJA remains isolated from THF release mutations.

## Release-status rule

`FINAL` / `PLAY_READY` is forbidden unless all of the following evidence exists for the exact candidate SHA:

- build PASS;
- package/payload inspection PASS;
- backend health/auth PASS for network-required products;
- physical-device install/launch/touch PASS;
- orientation/responsive-layout PASS;
- core user journey PASS;
- crash-free smoke PASS;
- game FPS/RAM/thermal evidence when applicable.

If any item is missing, status must remain `QA_CANDIDATE` or `BLOCKED`, never `FINAL`.

## Current incident guard

The September 2026 Terra/Rift phone incident demonstrated two disallowed states: a landscape game configured with portrait orientation, and a Godot template APK without exported game payload. Both patterns are permanent automatic release blockers under this policy.
