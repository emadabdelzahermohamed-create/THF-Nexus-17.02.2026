# Fitness 51015 build checkpoint — 26 October 2026

- Package: `com.topherofit.thf.pulse`
- versionCode: `51015`
- versionName: `5.0.0-v2-alpha15`
- targetSdk: `36`
- Exact source/workflow SHA: `a49114530b250595dcdc2efd73e0fcc8756ea126`
- Deterministic Android build run: `40378739276` — SUCCESS
- Artifact: `fitness-activity-candidate-51015`
- Artifact ID: `12678120736`
- Debug APK SHA256: `22be537c5095f3dc118b28a82211a11b8ab4c0e0bdaa85b76f414098c598df83`
- Unsigned release AAB SHA256: `8a081af622517ff68a24fc4cca6756a006460012a23177304adafad86f028c55`
- Local gates before final build: source `43/43`, product `55/55`, backend `15/15`, `git diff --check` PASS.
- Android gate: `:app:testDebugUnitTest`, `:app:lintDebug`, `:app:assembleDebug`, `:app:bundleRelease` PASS on the exact SHA above.

## Integrated post-51014 deltas

Safe worker changes from PRs #103 through #113 were integrated, while broad Health expansion PR #98 remains intentionally excluded/HOLD. This candidate includes process-safe rest timing, saved reduced-motion behavior, finite activity metrics, sport-specific program progression, corrected exercise metadata, physical P0 snapshot tooling, stricter GPS accuracy gates, smoother accessible offline motion phases, wearable provenance/anti-cheat policy, and an integrated ARMED→ACTIVE activity truth state.

The activity service now withholds elapsed time, distance, session steps, calories, pace/speed and public route until measured movement activates the session. Re-entering activity UI resumes an existing live session rather than resetting it. ARMED/ACTIVE state persists in checkpoint v2 while v1 checkpoints from 51014 remain backward-compatible.

## Release boundary

This checkpoint proves source/build identity only. Google Play Internal signing/upload/readback and physical-phone 51015 runtime evidence are separate gates. Public Production remains fail-closed until physical/runtime and Health/policy/privacy gates pass.
