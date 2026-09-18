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
- [x] Stable HTTPS API endpoint established at `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`; no temporary tunnel. Fail-closed contract recorded in `PRODUCTION_HOSTING_GATE.md`.
- [ ] Fitness mobile sync endpoint and durable queue reconciliation verified against production.
- [ ] Publish responsive Web/PWA using the same API and account data as Android.
- [ ] Offline subset remains usable; ranked/economy-sensitive outcomes remain server-authoritative.

## P3 — Fitness functionality
- [ ] Exercise catalog, plans, timers, warm-up/cool-down, injury warnings and recovery flows: full regression. Production Web implementation is now visible and usable; full cross-client regression remains open.
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
- [ ] Release signing + Play App Signing compatible AAB. Read-only probes found no upload-keystore candidate in connected Drive; GCP Secret Manager inventory is IAM-blocked for `thf-release-builder` (`secretmanager.secrets.list` denied).
- [ ] Install/launch/onboarding/RTL/workout/avatar/permissions/offline-online/resume regression on physical Android.
- [ ] Performance checks: startup, FPS, RAM and thermal behavior.

## P6 — Google Play
- [ ] Create/configure standalone Fitness Play app if not already present.
- [ ] Internal Testing upload only after Android gates pass. Fail-closed checklist recorded in `PLAY_RELEASE_GATE.md`; unsigned RC2 is explicitly non-publishable.
- [ ] Data Safety, Health Apps declaration, App Access, content rating, target audience.
- [x] Privacy policy + account deletion URL published on the production HTTPS host.
- [ ] Verify install from Play Internal and post-upload runtime.

## P7 — Web production
- [x] Deploy production web service to AppDeploy HTTPS endpoint; deployment status `ready` with no frontend/backend runtime errors.
- [ ] Verify auth, workouts, avatar, sync and offline/online behavior end-to-end. Account deletion endpoint/UI and public deletion instructions are deployed; full production regression remains open.
- [ ] Verify mobile-web parity against Android account data.
- [ ] Post-deploy smoke and rollback checkpoint.

## P8 — Security/release closure
- [x] Initial secret-like assignment scan + production user-scope/auth regression.
- [ ] Dependency review and network-security release audit. Fail-closed evidence contract recorded in `SECURITY_RELEASE_GATE.md` (`59cc26ce87a2c30631fac17db0005d6fea7dd6df`).
- [ ] Play Integrity backend exchange for trusted activity/reward paths; client-only checks do not satisfy release closure.
- [ ] Final release manifest, SHA-256, changelog and rollback instructions.
- [x] Git checkpoints created for completed development gates.
- [ ] After every publish: re-verify live Web and Play Internal artifact before advancing.

## Current verified checkpoint — V5 RC2 / P0 PASS
- Source SHA-256: `2290c5897eab827dd778204de03f6f70c49fd162a32d187e4844172ececf7b74`.
- Local tests: 20/20 PASS.
- Canonical avatar SHA-256: `4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f` (137 joints / 195 clips).
- Successful CI: `THF Fitness V5 Main Auth Gate`, run `35311644865`, commit `ffa24940dd8e1b8d560194232e521b55058bdd40`.
- Evidence artifact: `thf-fitness-v5-rc2-main-auth-gate`, artifact id `10533239127`, digest `sha256:c7f2a83497acc6e15b279e969ab927b01f8bef8398f766d1a31d7147407da281`.
- Debug APK SHA-256: `cfc5abb2b73cccdab338b3ec73205aad3bc6fb80557bf0f41a7a384e667e97d2`.
- Unsigned release AAB SHA-256: `ce8e8772665e4bc94f4c334a650079d93175ebf9b8ead053a62e0ee49988410a` — DO NOT publish this unsigned AAB.
- Previous base URL blocker is resolved: Web/backend deployed at `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`. Main Android gate commit `cd38292439eef0567776186d12e9b6d99825cca7` now injects this HTTPS URL as `THF_FITNESS_BASE_URL`. `THF_PASS_URL` and production signing remain unconfigured.
- Infrastructure re-probe 2026-09-18: connected DigitalOcean account still has zero droplets. Repository searches found no authoritative committed `THF_FITNESS_BASE_URL` or Fitness Cloud Run deployment contract. Creating new paid infrastructure remains owner-gated.
- Hosting acceptance/rollback requirements are checkpointed in `PRODUCTION_HOSTING_GATE.md` (`294a9bf221ece68dfb05c8e1c581bf327ba558e4`).
- Play pre/post-upload requirements are checkpointed in `PLAY_RELEASE_GATE.md` (`074d83480284667a5fda8c4a877080564e7e3e4a`).
- P8 dependency/network/auth/Play-Integrity evidence requirements are checkpointed in `SECURITY_RELEASE_GATE.md` (`59cc26ce87a2c30631fac17db0005d6fea7dd6df`).
- Production legal URLs: Privacy `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/privacy.html`; Account deletion `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/account-deletion.html`; Terms `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/terms.html`. Account deletion is authenticated and removes account-scoped goal/workout records in bounded requests before sign-out.
- Android signing source inspection: canonical RC2 `release` build has no production `signingConfig`. Fail-closed patch script `ReleaseOps/FitnessStandalone/apply_android_signing.py` and contract `ANDROID_SIGNING_CONTRACT.md` were added and locally text-tested PASS. Production upload key material remains external-only.
- Next priority: observe the Android rebuild against the live HTTPS backend, then configure production OAuth/signing, physical-device QA and Play Internal. Do not mark Android/Web cross-device sync PASS until the rebuilt Android artifact is exercised against the same production account/data.

- Web exercise UX defect fixed on production 2026-09-18: Arabic RTL tabs, 18-exercise library, 8 plans, warm-up/cool-down, instructions/warnings/recovery, workout logging, rest timer and progress persistence deployed at the production URL. Evidence: `WEB_EXERCISE_DEPLOY_20260918.md`. Full Android/physical-device regression remains open.

- Signing inventory evidence: GitHub Actions run `35356106595` PASSed as a read-only probe; artifact `10552265497` reports `secret_manager_list=BLOCKED` due IAM permission denial and explicitly confirms no secret values were read. Connected Google Drive metadata searches for THF/Fitness/Pulse upload key/keystore returned no candidates.

## Execution policy
Work top-to-bottom. Within each automation run, complete as many safe tasks as possible rather than one task per run. Do not mark a gate PASS without evidence. When a task is blocked only by an owner-only authorization or unavailable external credential, record the exact blocker and immediately continue with the next independent task.
