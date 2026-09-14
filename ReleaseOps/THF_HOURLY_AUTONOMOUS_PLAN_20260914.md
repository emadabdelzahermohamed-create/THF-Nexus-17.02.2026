# THF Hourly Autonomous Finalization Plan — 2026-09-14

## Goal
Reach the fastest truthful path to installable, phone-tested, design-approved THF applications and games while preserving latest authoritative sources and preventing regressions.

## Hourly lanes
- `:00` — Apps Factory: ordinary THF applications only.
- `:12` — Games Factory: Terra/Rift/Spark/Rush and shared game runtime only.
- `:24` — Integration Factory: shared Identity/Auth, Health, naming/icons, RBAC/admin, cross-app handoffs.
- `:36` — Release Factory: newest exact candidate packaging/installability/phone-QA preparation.
- `:50` — TokenOps Factory: non-blocking token/treasury work only; never blocks phone finalization.

WAVE MAWJA remains isolated and its factory stays disabled unless explicitly re-enabled.

## Non-negotiable source rule
Before any edit/build/package operation, resolve the newest authoritative product source/version/SHA. Fail closed on stale RCs, fallback wrappers, superseded APKs, old Core web shells used in place of Terra/Rift, or text-only fitness shells used in place of the real Motion Coach/MPFB/UAL runtime.

## Speed-first finalization priority
1. Latest real product payload.
2. Working onboarding/auth/session and reachable backend where required.
3. Google sign-in through Android Credential Manager and passkey-ready Identity layer; email/password or code fallback; guest linking where valid.
4. THF Fitness: Health Connect baseline, Samsung Health Data SDK adapter boundary, pose/motion verification, real animated-human exercise experience.
5. Clear user-facing bilingual names and product-specific icons/logos while package IDs remain stable.
6. THF Admin/Publisher private/internal access protected by server-authoritative RBAC; ordinary users never see or reach operator surfaces.
7. API 36 APK build with package/version/ABI/payload/signature/zipalign/installability validation.
8. Physical-phone install/launch/touch/layout/orientation/background-resume/offline-network/core-flow testing and design iteration.
9. Production signing/AAB/Play Internal after phone acceptance.
10. Broad security hardening/penetration work after the foundation is approved, except urgent auth/RBAC/data/secret/admin/financial blockers which are fixed immediately.

## Approved user-facing naming layer
Internal compatibility identifiers and package IDs remain unchanged.

Applications:
- Core -> THF Hub / مركز THF
- Pulse -> THF Fitness / لياقة THF
- Forge -> THF Market / سوق THF
- Echo -> THF Community / مجتمع THF
- Codex -> THF Learn / تعلّم THF
- Vault -> THF Wallet / محفظة THF
- Signal -> THF Publisher / ناشر THF (private/internal)
- Command -> THF Admin / إدارة THF (private/internal)
- Pass -> THF Identity / هوية THF (service/backend)

Games:
- Terra -> THF World / عالم THF
- Rift -> THF Arena / ساحة THF
- Spark -> THF Learn Games / ألعاب تعلم THF
- Rush -> THF Motion Games / ألعاب حركة THF

## Truth boundary
No task may call a product FINAL/PLAY_READY without exact-candidate physical-device evidence. CI/source/build success is not a substitute for phone evidence. Any APK that fails package-manager installation is immediately rejected and cannot be reused as a release baseline.

## Autonomous permission policy
Proceed without user interruption for all safe reversible source, CI, testing, packaging, documentation, naming, icon-resource, shared-library and QA-preparation work already authorized through connected tools. If OAuth console ownership, SMS provider activation, production signing, Play Console, billing, legal acceptance, physical-device action, signer/multisig or another non-delegable step is required, record the exact blocker and continue all independent work instead of stopping.
