# THF + WAVE Release Factory Checkpoint — 2026-09-14 17:53 Africa/Cairo

Checkpoint body SHA-256 (all content below this line): `d84b21480983b2c3dadcaf10c32ee9fddfad2abbc04afda37929d0c120de2cc8`

## Authority reviewed
- Run-start authoritative state: `ReleaseOps/STATE_20260914_1647_RELEASE_FACTORY_FINAL.md` with body SHA-256 `c24ec611eef2f279041bf10b224d459014f8472dd10b34462da69f790441d642`.
- Existing release truth retained: exact-candidate physical-phone acceptance is still pending; no signed final AAB, Play approval, stable production HTTPS/WSS, Cloudflare production cutover, or production deployment is claimed.
- WAVE remains isolated with `CANONICAL_ROOT_OS_LOGIN_REQUIRED`; WIF/IAP reachability is available but the CI OS Login identity is not authorized for canonical `/root/workspace/wave-mawja`.

## Terra RC34 Android/Godot repair and hardened rebuild
- The original Terra RC34 compact-phone build failed before export because Godot 4.7.2 did not have valid Android SDK/JDK paths.
- The isolated SDK/JDK configuration repair landed on `main` and a prior rebuild proved the WIF -> GCP -> IAP -> Godot export path works.
- This batch then hardened `ReleaseOps/scripts/build_terra_rc34_compact_phone.sh` in commit `eca80080bfaf99ed1a8db1d6189a150a6cf21ecf` to fail unless Android API 36 exists and the exported APK itself reports the expected QA package and targetSdk 36 through `aapt dump badging`.
- The compact-build workflow was hardened to pinned Actions and `persist-credentials: false`; commit `5a6a43d2fdaab39395e3b54dd962a68149401d79` also serializes this build to avoid overlapping builder mutation.
- Verification run `34858271469` completed SUCCESS.
- Exported QA artifact facts from the APK/build evidence:
  - package: `com.topherofit.thf.terra.phoneqa`
  - version: `4.6.8-rc34-phonev2`
  - targetSdk: `36` proven from APK
  - Android API 36 installed: PASS
  - engine: Godot `4.7.2`
  - architecture: `arm64-v8a`
  - APK size: `49,656,414` bytes (<100 MiB)
  - APK SHA-256: `d1a9f6f3cf97dcd09680be0e381b5c13932090a4bc4169128a4f4f5ddeb5c3fc`
  - artifact ID: `10353771570`
  - artifact ZIP SHA-256: `4befefb9b86585e71b923ccdbdec05c4e89a7c21104814d11e89890c4961c882`
  - backend status: `EPHEMERAL_ENDPOINT_NOT_ACCEPTED_AS_FINAL`
  - physical device status: `PENDING`
  - final/play ready: `FALSE`
- This artifact is explicitly QA-only because its package identity is `.phoneqa`; it is not the production package and cannot satisfy exact-production-candidate device acceptance.

## Terra real-function source inspection
- Auth/spawn inspection run `34858182456` completed SUCCESS after checkout credential persistence was disabled in commit `097ecd2b85704c795cad3ba5dc7a0f47a88a8f57`.
- Fresh source inspection confirms touch-camera controls, Data Saver, accessibility/high-contrast/readable-text/reduced-motion controls and the MPFB avatar path exist.
- The same source still falls back to a `trycloudflare.com` Quick Tunnel when `THF_WORLD_API_URL` is absent. This remains a release blocker and is not accepted as a production HTTPS/WSS endpoint.
- Core avatar/gameplay startup is backend-gated: empty token shows auth; session resume requires `/api/me`; bootstrap requires successful `/api/world` and `/api/me`; `_spawn_local_avatar()` runs only after those backend checks. Therefore static/source inspection does not prove the required offline/local core-gameplay transition, and exact-device offline/network-transition acceptance remains blocked until a release-safe local/offline path is proven on the exact candidate.

## Apps Factory authority repair
- Active PR #20 authority run `34858122509` exposed a validator runtime defect: nullable unresolved SHA evidence caused `HEX64.fullmatch(None)` to throw `TypeError` instead of producing a fail-closed validation result.
- Branch `apps-factory-lineage-v3-20260914` was repaired in commit `8351440c0fead8cfe578f09ddd408ec4671c7366` with type-safe SHA validation; missing/non-string SHA evidence is now treated as invalid evidence, never as a validator crash.
- Follow-up authority run `34858481962` completed SUCCESS, including regression coverage and production-authority revalidation.
- This branch repair is not represented as merged to `main` by this checkpoint; release authority must continue to follow the actual merged state.

## Unchanged hard blockers
- Exact physical Android sessions remain required for every app/game: install, launch, touch, responsive layout/orientation/safe area, background/resume, offline/network transitions, core journey, and crash-free smoke. Games additionally require player/avatar load, movement/camera/gameplay interaction and FPS/RAM/thermal observation.
- Production signing keys / Play App Signing, Play Console ownership/legal acceptance, stable production endpoint ownership/DNS/Cloudflare cutover, and WAVE canonical-workspace authorization remain permission- or owner-gated.
- No physical-device/GPU evidence, signed AAB, Play approval, production deployment, token financial mutation, SSH/OS Login weakening, or WAVE source/runtime mutation was fabricated or performed.
