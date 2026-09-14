# THF Core Phone UI1 — REJECTED

Date: 2026-09-14

Status: **REJECTED / DO NOT PROMOTE / DO NOT USE AS VISUAL OR FUNCTIONAL BASELINE**

Rejected artifact:
- `THF-CORE-RC6-PHONE-UI1-LOCAL-QA.apk`

Reasons confirmed by physical-device screenshots:
1. Authentication/register/login is non-functional because the bundled UI is loaded from `file://` while its API calls are relative `/api/...` fetches.
2. The World surface is the old Core web/canvas presentation, not the latest THF Terra native Godot runtime.
3. The Fitness surface is the old form/card interface, not the agreed animated-human Motion Coach experience.
4. The candidate does not exercise the MakeHuman/MPFB + UAL avatar/motion asset stack that already exists in the Terra/Rift runtime.
5. It violates the no-regression rule: older RC6 presentation must not replace later cumulative game/fitness streams.

Required replacement gate:
- Core identity must use a reachable HTTP(S) backend or an explicitly embedded local API, never relative API calls from `file://`.
- World must bind to the latest accepted Terra native runtime and its MPFB/UAL assets.
- Fitness must show a real animated human/avatar performing the selected exercise; text-only exercise guidance is not acceptable.
- Build must prove the selected source/version is the newest accepted cumulative stream before producing a phone candidate.
- Physical-device acceptance is required before promotion.
