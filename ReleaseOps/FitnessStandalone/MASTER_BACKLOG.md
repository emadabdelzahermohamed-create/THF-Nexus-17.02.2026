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
- [ ] Freeze exact source provenance for standalone Fitness branch.
- [ ] Add branch-native CI that builds from this branch and fails closed on missing avatar/source.
- [ ] Produce test APK + unsigned/release-ready AAB evidence with SHA-256.
- [ ] Store build manifest and reproducible source hash.

## P1 — Independent identity / login
- [ ] Standalone login + registration UI.
- [ ] Google Sign-In / Google Identity production client configuration.
- [ ] Additional providers through OIDC/OAuth adapters (provider secrets external only).
- [ ] Session rotation/revocation, account deletion and cross-device sync.
- [ ] Ensure Fitness can run independently while preserving optional THF ecosystem identity bridge.

## P2 — Production backend + web parity
- [ ] Stable HTTPS API endpoint; no temporary tunnels in production config.
- [ ] Fitness mobile sync endpoint and durable queue reconciliation.
- [ ] Publish responsive Web/PWA using the same API and account data as Android.
- [ ] Offline subset remains usable; ranked/economy-sensitive outcomes remain server-authoritative.

## P3 — Fitness functionality
- [ ] Exercise catalog, plans, timers, warm-up/cool-down, injury warnings and recovery flows.
- [ ] Motion Coach with real sensor/motion verification.
- [ ] Health Connect integration and production permission flow.
- [ ] Progress, XP, competitions/leaderboards and anti-cheat verification.
- [ ] Arabic/English RTL first, then retained localization framework.
- [ ] Accessibility: Reduce Motion, Data Saver, High Contrast and scalable text.

## P4 — Human avatar quality
- [ ] Keep canonical modern human only; no legacy humanoid fallback.
- [ ] Verify 137-joint skeleton + 195 clips on device.
- [ ] Improve exercise-to-animation mapping, transitions, foot contact, IK hooks and camera framing.
- [ ] Optimize LOD/update rate/shadows/face/hair for mobile without replacing the canonical human.
- [ ] GPU/device visual QA.

## P5 — Android release quality
- [ ] Remove debug suffix/debuggable state.
- [ ] Production adaptive icon/splash/name/versionCode/versionName.
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
- [ ] Secret scan, dependency review, network security and auth/RBAC regression.
- [ ] Play Integrity backend exchange for trusted activity/reward paths.
- [ ] Final release manifest, SHA-256, changelog and rollback instructions.
- [ ] Git checkpoint after every passed gate.
- [ ] After every publish: re-verify live Web and Play Internal artifact before advancing.

## Execution policy
Work top-to-bottom. Within each automation run, complete as many safe tasks as possible rather than one task per run. Do not mark a gate PASS without evidence. When a task is blocked only by an owner-only authorization or unavailable external credential, record the exact blocker and immediately continue with the next independent task.
