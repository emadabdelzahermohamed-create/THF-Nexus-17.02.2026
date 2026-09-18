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

## P0 — Source authority + CI
- [x] Freeze exact source provenance for standalone Fitness branch (RC2 Drive ID + SHA pinned).
- [x] Add branch-native CI that fails closed on missing/wrong source or avatar.
- [ ] Produce test APK + unsigned/release-ready AAB evidence with SHA-256.
- [x] Store build manifest and reproducible source hash.

## P1 — Independent identity / login
- [x] Standalone login + registration UI.
- [ ] Google Sign-In / Google Identity production client configuration.
- [x] Additional provider adapter: Microsoft OIDC; provider secrets remain external.
- [x] Session revocation, one-time Android auth handoff and account deletion.
- [ ] Verify cross-device data sync against production backend.
- [ ] Preserve optional THF ecosystem identity bridge without making Fitness dependent on it.

## P2 — Production backend + web parity
- [ ] Stable HTTPS API endpoint; no temporary tunnels in production config.
- [ ] Fitness mobile sync endpoint and durable queue reconciliation verified against production.
- [ ] Publish responsive Web/PWA using the same API and account data as Android.
- [ ] Offline subset remains usable; ranked/economy-sensitive outcomes remain server-authoritative.

## P3 — Fitness functionality
- [ ] Exercise catalog, plans, timers, warm-up/cool-down, injury warnings and recovery flows: full regression.
- [ ] Motion Coach with real sensor/motion verification.
- [ ] Health Connect integration and production permission flow.
- [ ] Progress, XP, competitions/leaderboards and anti-cheat verification: production regression.
- [ ] Arabic/English RTL first, then retained localization framework.
- [ ] Accessibility: Reduce Motion, Data Saver, High Contrast and scalable text.

## P4 — Human avatar quality
- [x] Canonical identity avatar pinned to modern Stage16A; legacy humanoid references are CI-banned.
- [ ] Verify 137-joint skeleton + 195 clips on physical device/GPU.
- [ ] Improve exercise-to-animation mapping, transitions, foot contact, IK hooks and camera framing.
- [ ] Optimize LOD/update rate/shadows/face/hair for mobile without replacing the canonical human.
- [ ] GPU/device visual QA.

## P5 — Android release quality
- [ ] Remove debug suffix/debuggable state from production artifact.
- [x] Release version identity updated: package, targetSdk 36, versionCode/versionName.
- [ ] Release signing + Play App Signing compatible AAB.
- [ ] Install/launch/onboarding/RTL/workout/avatar/permissions/offline-online/resume regression on physical Android.
- [ ] Performance checks: startup, FPS, RAM and thermal behavior.

## P6 — Google Play
- [ ] Create/configure standalone Fitness Play app if not already present.
- [ ] Internal Testing upload only after Android gates pass.
- [ ] Data Safety, Health Apps declaration, App Access, content rating, target audience.
- [ ] Privacy policy + account deletion URL.
- [ ] Verify install from Play Internal and post-upload runtime.

## P7 — Web production
- [ ] Deploy production web service.
- [ ] Verify auth, workouts, avatar, sync, offline/online behavior and account deletion.
- [ ] Verify mobile-web parity against Android account data.
- [ ] Post-deploy smoke and rollback checkpoint.

## P8 — Security/release closure
- [x] Initial secret-like assignment scan + production user-scope/auth regression.
- [ ] Dependency review and network-security release audit.
- [ ] Play Integrity backend exchange for trusted activity/reward paths.
- [ ] Final release manifest, SHA-256, changelog and rollback instructions.
- [x] Git checkpoints created for completed development gates.
- [ ] After every publish: re-verify live Web and Play Internal artifact before advancing.

## Current verified checkpoint — V5 RC2
- Source SHA-256: `2290c5897eab827dd778204de03f6f70c49fd162a32d187e4844172ececf7b74`
- Local tests: 20/20 PASS.
- Canonical avatar SHA-256: `4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f` (137 joints / 195 clips).
- Previous CI blockers fixed: obsolete Android setup package; explicit current sdkmanager discovery.
- Next gate: obtain successful RC2 Android CI artifacts, then deploy a stable HTTPS backend before production OAuth/device/Play gates.

## Execution policy
Work top-to-bottom. Within each automation run, complete as many safe, independent tasks as possible rather than only one task. Do not mark a gate PASS without evidence. When a task is blocked only by an owner-only authorization or unavailable external credential, record the exact blocker and immediately continue with the next independent task.
