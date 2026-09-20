# THF Fitness Standalone — Unified Release Backlog

Date: 2026-09-18
Branch: `release/fitness-standalone-v1-20260918`
Product: THF Fitness / Pulse standalone
Rule: WAVE-MAWJA source and releases are out of scope and must remain untouched.

## Authority
- Start from the latest Pulse hybrid-modern lineage, not legacy textual Fitness or old humanoids.
- Canonical human avatar: MPFB/MakeHuman Stage16A lineage, 137 joints, 195 animation clips.
- Android applicationId target: `com.topherofit.thf.pulse`.
- Android targetSdk: 36.
- Web and Android must share the same production backend, account identity and synchronized user data.

## P0 — Final product scope / no-regression contract
- [ ] Treat `ReleaseOps/FitnessStandalone/FINAL_PRODUCT_SCOPE_20260918.md` as binding product scope for the next production candidate.
- [ ] No final release may regress to the simplified RC2 UX if agreed Fitness surfaces are absent.
- [ ] User-visible professional UX required across sports/training, 3D Motion Coach, health/wearables, trainers/gyms, nutrition, supplement safety, habit change, competitions, reports and settings.
- [ ] Scientific/safety source policy and license/provenance checks required for imported/open-source content.
- [ ] Backend-only capability does not satisfy completion.

### P0 — User-visible parity gate
- [ ] No backend-only release claims: every material Fitness capability must have a usable UI surface and UI acceptance evidence.
- [x] Production Web renders canonical Stage16A 3D directly inside the active workout/session flow. Physical Android/GPU evidence remains open.
- [x] Trainer workspace: clients/assignments/follow-up/bookings is visible and permission-gated in production Web.
- [x] Competition + leaderboard UI is visible; trusted score submission remains server-authoritative.
- [x] AI Coach has a user-facing explainable recommendation screen.
- [ ] Web/Android visible workflow parity against the same account/data backend.
- Evidence/audit: `UI_SURFACE_AUDIT_20260918.md`; `WEB_IMMERSIVE_STAGE16A_DEPLOY_20260919.md`; `WEB_VISUAL_DETAIL_DEPLOY_20260919.md`; `WEB_STAGE16A_MOTION_MAPPING_DEPLOY_20260919.md`; `WEB_STAGE16A_FOOT_CONTACT_HOOKS_DEPLOY_20260920.md`.

## P0 — Source authority + CI
- [x] Freeze exact source provenance for standalone Fitness branch (RC2 Drive ID + SHA pinned).
- [x] Add CI that fails closed on missing/wrong source or avatar; privileged WIF gate runs from short `main` ref and checks out this canonical Fitness branch.
- [x] Produce test APK + unsigned release AAB evidence with SHA-256.
- [x] Store build manifest and reproducible source hash.

## P1 — Independent identity / login
- [x] Standalone login + registration UI.
- [ ] Google Sign-In / Google Identity production client configuration.
- [x] Additional provider adapter: Microsoft OIDC; provider secrets remain external.
- [x] Session revocation, one-time Android auth handoff and account deletion.
- [ ] Verify cross-device data sync against production backend.
- [ ] Preserve optional THF ecosystem identity bridge without making Fitness dependent on it.

## P2 — Production backend + web parity
- [x] Stable HTTPS API endpoint established at `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`; no temporary tunnel.
- [ ] Fitness mobile sync endpoint and durable queue reconciliation verified against production.
- [ ] Publish responsive Web/PWA using the same API and account data as Android.
- [ ] Offline subset remains usable; ranked/economy-sensitive outcomes remain server-authoritative.

## P3 — Fitness functionality
- [ ] Exercise catalog, plans, timers, warm-up/cool-down, injury warnings and recovery flows: full regression. Production Web implementation is visible and usable; full cross-client regression remains open.
- [ ] Motion Coach with real sensor/motion verification. Canonical Stage16A visual demonstration is embedded in active sessions; sensed/verified movement remains fail-closed pending device evidence.
- [ ] Health Connect integration and production permission flow.
- [ ] Progress, XP, competitions/leaderboards and anti-cheat verification: production regression.
- [ ] Arabic/English RTL first, then retained localization framework.
- [ ] Accessibility: Reduce Motion, Data Saver, High Contrast and scalable text.

## P4 — Human avatar quality
- [x] Canonical identity avatar pinned to modern Stage16A; legacy humanoid references are CI-banned.
- [ ] Verify 137-joint skeleton + 195 clips on physical device/GPU.
- [ ] Improve exercise-to-animation mapping, transitions, foot contact, IK hooks and camera framing. Web camera/framing, soft shadows, tone mapping and deterministic exercise-name mapping are live. Snapshot `1789873154525` adds foot-bone visual contact hooks when discoverable and explicit fail-closed IK status. This is visualization only: biomechanical mapping certification and true foot-lock/IK remain open.
- [ ] Optimize LOD/update rate/shadows/face/hair for mobile without replacing the canonical human.
- [ ] GPU/device visual QA.

## P5 — Android release quality
- [ ] Remove debug suffix/debuggable state from production artifact.
- [x] Release version identity updated: package, targetSdk 36, versionCode/versionName.
- [x] Release signing + Play App Signing compatible AAB. Verified signed build + Android Publisher upload in run `35434624698`; Internal edit committed with versionCode `50001`.
- [ ] Install/launch/onboarding/RTL/workout/avatar/permissions/offline-online/resume regression on physical Android.
- [ ] Performance checks: startup, FPS, RAM and thermal behavior.

## P6 — Google Play
- [x] Standalone Fitness Play application record verified for `com.topherofit.thf.pulse`.
- [x] Google Play Internal upload committed for signed versionCode `50001` in run `35434624698`; physical tester install/runtime remains a separate open gate.
- [ ] Data Safety, Health Apps declaration, App Access, content rating, target audience.
- [x] Privacy policy + account deletion URL published on the production HTTPS host.
- [ ] Verify install from Play Internal and post-upload runtime.

## P7 — Web production
- [x] Deploy production web service to AppDeploy HTTPS endpoint; deployment status `ready`.
- [ ] Verify auth, workouts, avatar, sync and offline/online behavior end-to-end.
- [ ] Verify mobile-web parity against Android account data.
- [x] Latest Stage16A foot-contact visual-hook gate: snapshot `1789873154525` reached `ready`; QA screenshot run `1789873172920` produced Web/mobile evidence with 0 frontend, 0 backend and 0 network errors. Authenticated reference-quality acceptance remains open.

## P8 — Security/release closure
- [x] Initial secret-like assignment scan + production user-scope/auth regression.
- [ ] Dependency review and network-security release audit. Fail-closed evidence contract recorded in `SECURITY_RELEASE_GATE.md`.
- [ ] Play Integrity backend exchange for trusted activity/reward paths; client-only checks do not satisfy release closure.
- [ ] Final release manifest, SHA-256, changelog and rollback instructions.
- [x] Git checkpoints created for completed development gates.
- [ ] After every publish: re-verify live Web and Play Internal artifact before advancing.

## Current verified checkpoint
- Source SHA-256 baseline: `2290c5897eab827dd778204de03f6f70c49fd162a32d187e4844172ececf7b74`.
- Canonical avatar SHA-256: `4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f` (137 joints / 195 clips).
- Google Play Internal: signed versionCode `50001`, run `35434624698`, committed true. Physical Play runtime remains open.
- Android production-backend emulator smoke PASS: run `35356916175`; physical sensor/GPU testing remains open.
- Production Web/backend: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`.
- Latest P0 Web visual increment: AppDeploy snapshot `1789873154525`; QA `1789873172920`; evidence `WEB_STAGE16A_FOOT_CONTACT_HOOKS_DEPLOY_20260920.md`.
- Next release blockers: physical-device install/sensor/GPU/Health Connect evidence, cross-device Web/Android sync verification, Play declarations/store-compliance completion, biomechanically certified Exercise→Animation mapping, true foot-lock/IK, first-install Android offline Stage16A packaging, and authenticated P0 visual-reference acceptance. Continue independent user-visible work while blocked.

## Verified blocker refresh — 2026-09-20
- Google Play Internal remains published for signed versionCode `50001`; publication does not imply physical-device success.
- Physical Android Stage16A/GPU/Health Connect and Web↔Android cross-device sync evidence remain open.
- Web Stage16A now has explicit foot-bone visual contact hooks where the canonical rig exposes discoverable foot bones, but true IK/foot locking remains FAIL-CLOSED.
- Visual quality remains FAIL-CLOSED against the approved screenshot/reference bar; functional presence does not close this gate.

## Execution policy
Work top-to-bottom. Within each automation run, complete as many safe tasks as possible rather than one task per run. Do not mark a gate PASS without evidence. When a task is blocked only by an owner-only authorization or unavailable external credential, record the exact blocker and immediately continue with the next independent task.
