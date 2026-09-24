# Fitness Release Swarm Protocol — 2026-09-24

Priority 1: Top Hero Fit standalone. Priority 2 after closure: WAVE_MAWJA.

## Write isolation
- Product lane writes only branch automation/fitness-swarm-product-20260924.
- Motion lane writes only branch automation/fitness-swarm-motion-20260924.
- Backend lane writes only branch automation/fitness-swarm-backend-20260924.
- Android lane writes only branch automation/fitness-swarm-android-20260924.
- Release lane writes only branch automation/fitness-swarm-release-20260924 and is the sole integration/merge owner.
- No worker may push directly to release/fitness-standalone-v1-20260918 or another worker branch.

## Ownership boundaries
- product: Web/app UX, onboarding, workout/session presentation, RTL/LTR, accessibility. It must not edit Android build/signing files, backend/service code, or 3D asset/animation source.
- motion: Stage16A renderer, exercise-animation mapping, camera/framing, lighting, transitions, IK/foot-contact hooks, offline 3D assets. It must not edit product routing/auth, backend services, or Android packaging.
- backend: API/auth/data sync/reports/Health data server contracts/anti-cheat services. It must not edit UI, 3D assets, or Android build/signing.
- android: manifest/Gradle/package/signing/AAB/APK/DAL/device/runtime packaging only. Shared UI/business source is read-only; defects there are reported to the owning lane.
- release: read/test/integrate only; no product feature development.

## Completion protocol
Each worker owns exactly one active task until PASS or a true external blocker. It records task, acceptance criteria, exact commit SHA, tests and blockers only in its lane state file. It opens/updates a PR to the release integration branch only after PASS. Release lane validates the PR against the current integrated candidate, checks changed-file ownership, runs integration gates, then merges sequentially. Conflicting or out-of-scope changes are never merged.

## Dependency protocol
Workers never wait idle for another lane. When an upstream dependency is missing, record the dependency and continue acceptance work that does not require it on the SAME task. If nothing remains executable, mark BLOCKED with exact dependency and stop mutating that task until the release state changes. Release lane never assumes current-hour workers completed; it validates only submitted PASS commits.

## Promotion
Fitness is closed only after live Web verification, exact Android candidate integrity, Play Internal availability, required declarations, and physical-device gates where required. After closure, release state changes phase to WAVE_MAWJA; workers switch only after reading that canonical phase marker.
