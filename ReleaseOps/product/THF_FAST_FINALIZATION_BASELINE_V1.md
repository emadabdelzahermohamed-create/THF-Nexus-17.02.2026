# THF Fast Finalization Baseline V1

Date: 2026-09-14

## Objective
Reach physically tested Android phone candidates as quickly as possible without repeating stale-source mistakes. Security hardening continues after the essential experience works, except blockers involving installability, authentication integrity, sensitive-data exposure, or destructive financial/admin actions.

## Non-regression rule
Before changing or building any product, resolve its newest authoritative source/version/SHA. Never replace a newer dedicated app/game runtime with an older Core/web fallback. Every candidate must record source SHA, app/game ID, versionCode/versionName, targetSdk, package ID, signing state, APK SHA and physical-device status.

## Shared identity foundation
All public apps and games use THF Identity / THF Pass as the common account layer.

Android sign-in priority:
1. Sign in with Google through Android Credential Manager.
2. Passkeys through Credential Manager.
3. Email + password or email one-time code as recovery/fallback.
4. Phone OTP where a supported SMS provider is configured.
5. Guest mode only for products where offline/guest use is meaningful; guest progress must be linkable to a real account.
6. Sign in with Apple on iOS/web when those targets enter the same release gate.

Requirements:
- one THF account across every app/game;
- provider account linking without duplicate THF identities;
- automatic sign-in for returning authorized accounts where platform policy permits;
- explicit logout/revoke flow;
- server-side session verification;
- admin/staff roles are never trusted from a client-only flag;
- consumer users never see operator controls.

## Fitness / health platform bridge
Do not build new Google Fit API dependencies. Use Android Health Connect as the primary Android data bridge because Google Fit APIs are on the 2026 retirement path.

Health Connect initial scope for THF Fitness and motion-aware games:
- steps;
- exercise sessions and routes;
- distance, speed, elevation;
- calories;
- heart rate and resting heart rate;
- sleep;
- weight/body composition where available;
- hydration/nutrition when the user enables them;
- planned exercise where supported.

Use Wear OS Health Services for live watch workout signals when a compatible watch is present.

Samsung path:
- use Samsung Health Data SDK, not the deprecated Samsung Health SDK for Android;
- keep this as an optional direct connector in addition to Health Connect when Samsung-specific data/behavior materially improves the experience;
- request only explicit user-approved data types;
- handle Samsung Health absence/version incompatibility gracefully.

Motion verification / AI coach:
- integrate MediaPipe Pose Landmarker or ML Kit Pose Detection behind one THF Motion interface;
- camera analysis is opt-in;
- rep counting and form guidance require confidence thresholds and temporal smoothing;
- do not award high-value competitive/economic proof from camera pose alone; combine with device/sensor/session signals and anti-cheat policy.

## Enhancement policy by product
- THF Hub: identity, SSO, deep links, notifications, unified account/profile and cross-app launch.
- THF Fitness: Health Connect, optional Samsung Health Data SDK, Wear OS Health Services, pose/motion analysis, animated human coach, workout plans and recovery guidance.
- THF Market: unified identity, memberships, orders, product/service entitlements and wallet handoff; no health permission requests unless required for a specific user-visible feature.
- THF Community: SSO, media/chat/calls, creator/community identity, safe moderation and profile links.
- THF Learn: SSO, progress sync, offline lessons, adaptive learning and game handoff.
- THF Wallet: SSO plus step-up authentication for sensitive operations; rewards/governance separated from raw health data.
- THF Publisher: private/internal publishing workflow only.
- THF Admin: private/internal control center only.
- THF World: latest native Terra stream, shared avatar identity, guest/offline visual/play mode, SSO when online, social/economy handoff.
- THF Arena: newest authoritative Rift source before any phone build, SSO, ranked identity, anti-cheat and local training mode.
- THF Learn Games: SSO/guest linking, real learning progression and parent/age-appropriate controls where applicable.
- THF Motion Games: Health Connect where useful, live motion/pose/sensor verification, real repetition/progression and offline fallback.

## Naming and icon rule
User-facing names come from `THF_PUBLIC_NAMES_AND_ACCESS_V1.json`. Engineering codenames and existing package IDs remain until a deliberate migration decision is made.

Every public product receives:
- one adaptive Android app icon;
- one monochrome/themed icon layer;
- one store icon;
- one wordmark lockup in Arabic and English;
- category-specific symbol while preserving the THF master brand;
- dark/light-safe variants.

No icon should rely on text alone at small sizes.

## Admin / control center access
Primary operator surfaces:
- THF Admin private Android app;
- private web control center.

Normal public apps/games do not expose an admin button. If an authorized staff member signs into a consumer product, an admin entry may appear only after the backend returns a valid staff role claim. A secret tap/gesture is never considered authorization.

THF Admin requires stronger auth than consumer use: passkey or MFA, server-side RBAC, short sessions for sensitive operations, audit logging, and re-authentication for financial/destructive actions.

## Fast-release sequence
For each product, execute this order and do not widen scope until the current gate passes:
1. newest authoritative source/version resolution;
2. essential feature completion;
3. clear bilingual display name/icon application;
4. shared THF Identity integration;
5. product-specific platform integrations;
6. APK package/signature/installability verification;
7. physical Android install/launch/navigation/RTL/permissions/offline/resume smoke;
8. real core-function test on device;
9. fix device-visible regressions;
10. user visual/design approval;
11. only then production signing, AAB/Play Internal and deeper hardening.

## Current source truth notes
- Terra authoritative source line: RC34 / 4.6.8-rc34.
- Rift newer authoritative source exists at RC41 / 4.7.5-rc41; older RC37 phone output must not be treated as newest-source finalization.
- Ordinary apps must follow the current authoritative lineage registry rather than filename age alone.

## Release truth
This document is an execution baseline, not a claim that the products are already FINAL/PLAY_READY. Physical-device acceptance remains mandatory.
