# THF Fitness / Pulse — Google Play Release Gate

Date: 2026-09-18
Application ID: `com.topherofit.thf.pulse`
Target SDK: 36
Canonical avatar: MPFB/MakeHuman Stage16A, 137 joints / 195 clips. Legacy humanoid fallback is prohibited.

## Artifact rule
The current RC2 AAB is unsigned release evidence only. It MUST NOT be uploaded to Google Play. Play Internal upload is permitted only after a Play App Signing-compatible production AAB is generated and the physical-device/runtime gates pass.

## Pre-upload evidence required
- Production HTTPS backend and identity URLs embedded/configured and identical in authority to Web/PWA.
- Production signing configured without committing keystore material or passwords.
- Release build is non-debuggable and has no debug applicationId suffix.
- Install/launch/onboarding/login/RTL/workout/avatar/permissions/offline-online/resume regression on physical Android.
- Stage16A avatar renders on device and reports the canonical 137-joint / 195-clip lineage; no legacy fallback.
- Health Connect permission flow tested for only the data types actually used.
- Account deletion works in-app and a public deletion URL is available.
- Privacy policy URL is public and matches actual data handling.
- Data Safety and Health Apps declarations are prepared from verified behavior, not guessed.
- App Access, content rating, target audience and ads declarations are complete.
- Secret scan/dependency/network-security/auth regression passes.

## Post-upload evidence required
- Record Play Internal versionCode/versionName and AAB SHA-256.
- Install from the Internal Testing track, not a locally sideloaded substitute.
- Re-run launch/login/sync/workout/avatar/Health Connect/offline-online/resume/account-deletion smoke tests.
- Confirm the installed Play artifact points to the same production backend/identity used by Web.
- Record rollback/replacement procedure before advancing the release gate.

## Current state
BLOCKED before upload: production hosting/identity authority, production signing, and physical-device QA remain open. The unsigned RC2 AAB is evidence only and is not publishable.
