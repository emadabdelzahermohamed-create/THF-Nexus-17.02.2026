# THF Latest-Only / No-Regression Release Policy

Effective: 2026-09-14

This policy is mandatory for every THF Android app and game candidate before it is sent for physical-device testing or promoted toward Google Play.

## 1. Latest authoritative source only

A candidate MUST be built from the newest authoritative lineage for that product, not from an older UI shell, fallback, copied RC directory, or convenient previous APK.

Before build, record:
- product name
- authoritative source path / source archive
- exact source SHA-256 or Git commit SHA
- semantic/app version
- versionCode
- targetSdk
- engine/toolchain version
- required cumulative feature/assets lineage

If the newest authority cannot be proven, the build is FAIL-CLOSED and must not be sent to the user.

## 2. No-regression gate

A newer package MUST NOT lose a capability, asset family, animation system, runtime, screen, backend contract, or game system already accepted in a later cumulative stream.

For Terra/Rift/Pulse in particular, old Core web/canvas fallbacks are not valid substitutes for their native/current runtimes.

A candidate is rejected if its visible or functional baseline is older than the latest accepted lineage even if the APK itself builds successfully.

## 3. Android package-installability gate

Every APK sent to a phone MUST pass all of the following before delivery:
- non-empty file and valid ZIP/APK structure
- AndroidManifest.xml present and parseable
- package id is the expected THF package
- versionCode/versionName are the intended current values
- targetSdk is 36 unless a documented platform exception exists
- ABI contains the intended device architecture (arm64-v8a for current phone QA)
- `apksigner verify --verbose --print-certs` PASS
- `aapt2 dump badging` or equivalent manifest identity PASS
- signature scheme accepted by the target Android version
- installability smoke test using `adb install -r` on a compatible Android device/emulator when available
- SHA-256 captured after the final signing step, not before it

If any installability check is absent or fails, the artifact is NOT DELIVERABLE.

## 4. Physical-device truth

A build that has not installed and launched on the target device is QA CANDIDATE only. It must never be described as final, production-ready, or Play-ready.

Screenshots/errors from the physical device override optimistic CI assumptions. A package-invalid message is an immediate hard rejection.

## 5. Network/auth truth

Authentication, registration, multiplayer, sync, economy, cloud saves, media, or APIs must use a reachable stable endpoint for any release that claims those functions work. `file://` relative fetches and ephemeral `trycloudflare.com` endpoints are not release authority.

Offline visual QA may exist only when clearly labeled and must not be presented as proof of live backend functionality.

## 6. Asset/runtime provenance

For games and animated fitness experiences, the candidate must prove that required current assets are actually referenced by the runtime, not merely stored somewhere in an archive.

Examples include MPFB/MakeHuman avatar assets, UAL animation libraries, IK/rig/facial runtimes, exercise motion runtimes, environment packs, and other accepted cumulative assets.

## 7. Delivery rule

Do not send a new APK/AAB until the evidence bundle contains:
- authoritative latest-source proof
- no-regression proof
- structural/package identity proof
- signature verification proof
- architecture/SDK proof
- final artifact SHA-256
- physical-device install/launch evidence when available

Any uncertainty = FAIL-CLOSED. No downgrade to an older build is allowed merely to make a build or installation pass.
