# THF APK-First Orchestration Policy

## Primary delivery objective
The immediate program goal is **real phone-testable APKs**, not endless RC churn.

Order of outcomes:
1. Produce a real installable APK for every public THF Android app/game from the latest coherent source.
2. Verify package/payload/API36/ABI/signature/installability and all automatable real-function gates.
3. Surface each APK to the owner immediately with SHA-256 and a short phone-test checklist. Do not wait for every other app or cosmetic enhancement.
4. Freeze that exact SHA as the `PHONE_TEST_TARGET` while device feedback is collected.
5. Fix only defects found against that target or critical release blockers, then issue the next test target deliberately.
6. After phone acceptance, build AAB/Play Internal candidate, finish Play declarations and controlled publishing preparation.
7. Continue iterative product/visual/game development after the baseline is proven on phones.

## Anti-stale / anti-version-churn rules
- Each product has exactly one release lane and one canonical target state.
- Development workers may advance `DEV_HEAD`, but **must not invalidate an existing PHONE_TEST_TARGET just because a newer source commit exists**.
- Release/QA works from the pinned candidate SHA, not from "whatever is newest" every time it runs.
- A new source version becomes a release candidate only when the owning stream publishes a coherent `CANDIDATE_READY` checkpoint with tests and SHA.
- Only the Release Factory may promote `CANDIDATE_READY` -> `APK_CANDIDATE` -> `PHONE_TEST_TARGET`.
- Once a PHONE_TEST_TARGET exists, continue its build/package/device gate to completion unless: (a) it cannot build/install, (b) a critical auth/data/admin/financial safety defect is found, or (c) the candidate is explicitly superseded by Release Factory for a documented reason.
- Never abandon a nearly completed build merely because another worker created a newer DEV_HEAD.
- Do not create a new version number for documentation-only, test-only, comment-only or non-user-impacting changes.
- Avoid parallel edits to the same product by different workers. Shared integration changes are proposed as reusable modules/contracts and consumed by the owning product stream.

## Product state machine
`DEV_HEAD -> CANDIDATE_READY -> APK_CANDIDATE -> PHONE_TEST_TARGET -> PHONE_PASS -> PLAY_CANDIDATE -> PLAY_INTERNAL -> RELEASE_READY`

Separate failure states: `BLOCKED_BUILD`, `BLOCKED_EXTERNAL`, `PHONE_FAIL`, `REGRESSION`.

## Required candidate manifest
Every product stream must maintain evidence containing at least:
- product name and package id
- source commit/SHA or source archive SHA-256
- versionCode/versionName
- targetSdk/minSdk and ABI(s)
- build system/engine version
- implemented core journeys
- tests executed and failures
- required backend endpoints and health status
- known external blockers
- `candidate_status`

## APK gate
A candidate APK is acceptable for owner phone testing only when:
- it is a real APK, not an engine/template shell;
- real product/game payload is present;
- package id and version metadata are correct;
- targetSdk 36 requirement is satisfied where applicable;
- required ABI is present (arm64-v8a for native game public candidates);
- install/signature/package checks pass;
- required production/staging test endpoint is reachable for network-required flows;
- obvious UI-only/nonfunctional route defects are blocked;
- game orientation/touch/runtime metadata are mobile-safe.

The APK may still be called **PHONE_TEST_CANDIDATE**, not FINAL. Physical-device evidence is still required for final acceptance.

## Owner handoff rule
As soon as a new APK reaches `PHONE_TEST_TARGET`, the Release Factory must surface it immediately to the owner with:
- APK artifact/download reference
- SHA-256
- product/version/package id
- what is expected to work
- exact 5-10 minute phone test checklist
- known limitations/blockers

Do not wait for all products to finish before surfacing an available APK.

## Work allocation
- **Apps Factory:** Core/Hub, Forge/Market, Echo/Community, Codex/Learn, Vault/Wallet, Signal/Publisher, Command/Admin, THF Pass and shared app integration. Produces CANDIDATE_READY; does not promote phone target.
- **Fitness Factory:** Pulse/Fitness only; real Motion Coach/health integrations/phone UX. Produces CANDIDATE_READY.
- **Games Factory:** Terra/World, Rift/Arena, Spark/Learn Games, Rush/Motion Games and shared avatar/game runtime. Produces CANDIDATE_READY.
- **Release Factory:** sole owner of candidate promotion, APK builds, package inspection, stale-candidate arbitration, APK handoff, phone-test tracking and Play candidate promotion.
- **TokenOps Factory:** token/treasury/governance infrastructure only. It must not create unrelated Android versions; Vault integration is coordinated through Apps Factory contracts.

## Throughput rule
Every hourly worker should execute the largest coherent batch possible. Prefer finishing a buildable user journey or release gate over generating many tiny version bumps. Checkpoint meaningful progress so another run can continue without restarting.
