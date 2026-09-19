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
- [x] Production Web renders canonical Stage16A 3D directly inside the active workout/session flow; deployed snapshot `1789798972531`. Physical Android/GPU evidence remains open.
- [x] Trainer workspace: clients/assignments/follow-up/bookings is visible and permission-gated in production Web.
- [x] Competition + leaderboard UI is visible; trusted score submission remains server-authoritative.
- [x] AI Coach has a user-facing explainable recommendation screen.
- [ ] Web/Android visible workflow parity against the same account/data backend.
- Evidence/audit: `ReleaseOps/FitnessStandalone/UI_SURFACE_AUDIT_20260918.md`; latest Stage16A session evidence: `WEB_IMMERSIVE_STAGE16A_DEPLOY_20260919.md`; exercise-detail visual upgrade: `WEB_VISUAL_DETAIL_DEPLOY_20260919.md`.

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
- [ ] Exercise catalog, plans, timers, warm-up/cool-down, injury warnings and recovery flows: full regression. Production Web implementation is visible and usable; search/filter by text, level and equipment deployed 2026-09-19. Exercise-detail target-muscle visualization and prescription metrics deployed in snapshot `1789804866458`. Full cross-client regression remains open.
- [ ] Motion Coach with real sensor/motion verification. Canonical Stage16A visual demonstration is now embedded in production active sessions; sensed/verified movement remains fail-closed pending device evidence.
- [ ] Health Connect integration and production permission flow.
- [ ] Progress, XP, competitions/leaderboards and anti-cheat verification: production regression.
- [ ] Arabic/English RTL first, then retained localization framework.
- [ ] Accessibility: Reduce Motion, Data Saver, High Contrast and scalable text.

## P4 — Human avatar quality
- [x] Canonical identity avatar pinned to modern Stage16A; legacy humanoid references are CI-banned.
- [ ] Verify 137-joint skeleton + 195 clips on physical device/GPU.
- [ ] Improve exercise-to-animation mapping, transitions, foot contact, IK hooks and camera framing. Web camera/framing, soft shadows and tone mapping improved in snapshot `1789798972531`; exercise-specific animation certification/IK remains open.
- [ ] Optimize LOD/update rate/shadows/face/hair for mobile without replacing the canonical human.
- [ ] GPU/device visual QA.

## P5 — Android release quality
- [ ] Remove debug suffix/debuggable state from production artifact.
- [x] Release version identity updated: package, targetSdk 36, versionCode/versionName.
- [ ] Release signing + Play App Signing compatible AAB. A dedicated THF Fitness upload keystore was generated on the authorized remote builder and its four components were stored as separate GCP Secret Manager secrets on 2026-09-19; CI retrieval/signing and Play certificate acceptance still require evidence before PASS.
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
- [x] Post-deploy browser/runtime smoke for latest visual-detail gate: snapshot `1789804866458` reached `ready`; AppDeploy reported 0 frontend, 0 backend and 0 network errors. Automated QA screenshots were generated, but they show the signed-out surface and therefore do not close authenticated visual-reference acceptance.

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
- Production Web/backend: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`. Android gate commit `cd38292439eef0567776186d12e9b6d99825cca7` injects it as `THF_FITNESS_BASE_URL`. `THF_PASS_URL` and production signing remain unconfigured.
- Hosting acceptance/rollback requirements: `PRODUCTION_HOSTING_GATE.md` (`294a9bf221ece68dfb05c8e1c581bf327ba558e4`).
- Play pre/post-upload requirements: `PLAY_RELEASE_GATE.md` (`074d83480284667a5fda8c4a877080564e7e3e4a`).
- P8 evidence requirements: `SECURITY_RELEASE_GATE.md` (`59cc26ce87a2c30631fac17db0005d6fea7dd6df`).
- Production legal URLs: Privacy `/privacy.html`; Account deletion `/account-deletion.html`; Terms `/terms.html` on the production host.
- Android signing source inspection: canonical RC2 release build has no production `signingConfig`; `apply_android_signing.py` + `ANDROID_SIGNING_CONTRACT.md` are fail-closed. Production upload key remains external-only.
- Google Play state probe run `35357059466` PASS: application record exists, four standard tracks readable, zero releases; no Play edit committed.
- Android production-backend emulator smoke PASS: run `35356916175`, artifact `10552152173`, APK SHA-256 `aede65b003659b4b3ba46555b51744f365a9824e462029a5f0e6a3f1bd20f567`; install/cold-launch/ar-EG UI/no-fatal-crash/screenshot/UI-dump PASS. Physical sensor/GPU testing remains open.
- Production Web sports/wellness expansion deployed 2026-09-19; evidence `WEB_SPORTS_WELLNESS_DEPLOY_20260919.md`, Git checkpoint `05a3616990adfcd94989fb406b067708acb1aaaf`.
- Production Web exercise discovery search/filter deployed 2026-09-19; AppDeploy snapshot `1789795331179`, evidence `WEB_EXERCISE_DISCOVERY_DEPLOY_20260919.md`, Git evidence commit `fa6b09cbd6e2b3977c2d1045924b0779427bbed7`.
- Production Web immersive Stage16A active-session upgrade deployed 2026-09-19; AppDeploy snapshot `1789798972531`, evidence `WEB_IMMERSIVE_STAGE16A_DEPLOY_20260919.md`, initial evidence commit `2aefcb16a17e19031a5f9687e9bdb10f46bb9990`.
- Production Web exercise-detail visual upgrade deployed 2026-09-19; AppDeploy snapshot `1789804866458`, QA screenshot run `1789804885030`, evidence commit `aedaf00a587426fb248e1e5a2f2aad5bcb656f4f`.
- Next release blockers remain CI signing retrieval/Play certificate acceptance, physical-device sensor/GPU/Health Connect evidence, and cross-device Web/Android sync verification. Continue independent user-visible work while blocked.

## Verified blocker refresh — 2026-09-19
- Google Play probe evidence currently shows zero releases, including Internal; publication is NOT complete.
- Current recorded release AAB is unsigned and explicitly non-publishable.
- A dedicated upload key now exists in GCP Secret Manager, but signed-AAB generation, Play acceptance, and Internal upload remain fail-closed until directly evidenced.
- Physical Android Stage16A/GPU/Health Connect and Web↔Android cross-device sync evidence remain open.
- Visual quality remains FAIL-CLOSED against the approved screenshot/reference bar; functional presence does not close this gate.

## Execution policy
Work top-to-bottom. Within each automation run, complete as many safe tasks as possible rather than one task per run. Do not mark a gate PASS without evidence. When a task is blocked only by an owner-only authorization or unavailable external credential, record the exact blocker and immediately continue with the next independent task.
