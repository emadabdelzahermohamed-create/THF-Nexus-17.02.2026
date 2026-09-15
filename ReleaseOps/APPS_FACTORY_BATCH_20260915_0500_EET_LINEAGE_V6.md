# THF Applications Factory — lineage / no-regression checkpoint

Status: `NO_SOURCE_EDIT / FAIL_CLOSED / NOT_FINAL / NO_GO`

## Scope
Included: THF Hub/Core, THF Market/Forge, THF Community/Echo, THF Learn/Codex, THF Wallet/Vault, private THF Publisher/Signal, private THF Admin/Command, and THF Identity integration surfaces.

Excluded and untouched: THF Fitness/Pulse, all game code, WAVE.

## Latest repository lineage proved before work
- Observed `main` head at intake: `b3407eacc27123d4d6d62070f74b4ca92693d13b`.
- The newest app source authority remains `ReleaseOps/THF_APPS_PHONE_FUNDAMENTALS_SOURCE_V3_MANIFEST.json`.
- Core/Hub remains same-SHA skipped at `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`.
- Exact V3 app sources remain:
  - Forge/Market `75c3744af31f16273a174bdac53b9e812613e4d9ef8c2fa260521c7f7c40cbf8`
  - Echo/Community `3c90b53009d34e9c391bc8f977daf70195a041ba6c0098eca82709932b8734e9`
  - Codex/Learn `44ff76cca12b6b13febc53e9e0b8748a01949eb07c40b020d76b82f45a094950`
  - Vault/Wallet `e33c7c7f1f6d7f913dfe6ca5d674aff2883f7a230c2a323724088c30c4497585`
  - Signal/Publisher `3b6ba96076decd62e31a90c60d91a101806d6a6e9be329a58baa55ece82227ef`
  - Command/Admin `314a89f33f62d754edc9cc369fcc35b019d6081c6be0dcfbffa0fe5801ce0ffc`
- No old APK is eligible to be rebound to these source SHAs; the V3 manifest still records `NEEDS_EXACT_SOURCE_BUILD` and `eligible_apk_sha256=null`.

## Newer shared Identity authority discovered
Repository lineage has advanced beyond the V3 manifest's original `thf.shared.integration.v4` reference. The newest committed shared integration authority is `ReleaseOps/integration_factory/ANDROID_SHARED_INTEGRATION_V6.json` (commit `861b586dba63122884624f535099461c3db8858d`). V6 preserves package IDs and adds/retains these release-critical contracts:
- account deletion requires recent reauthentication, session revocation, handoff revocation, health-consent deletion and provider unlink; the client is not deletion authority;
- private Admin/Publisher operator access requires passkey user verification, a second factor and fresh role claims no older than 300 seconds;
- ordinary-user visibility for Admin/Publisher is false;
- preference sync is bounded to 20 locales, with RTL locales ar/fa/ur, and excludes identity/health/economy fields;
- physical-device/final readiness remains false.

This is treated as the current Identity integration authority. No downgrade to V4 is permitted.

## Same-SHA / no-regression decision
No app source bytes were edited in this batch because the exact V3 app source SHAs have not changed and their already-proven phone fundamentals remain authoritative: onboarding, explicit account/logout/delete routes, trusted-HTTPS fail-closed behavior, validated-network requirement, Android Data Saver integration, offline/loading/error states, notification channel/runtime permission, RTL/accessibility, 20 locale resource sets, API36, approved visible names, adaptive icons, monochrome icons and 512x512 store icons.

Signal/Publisher and Command/Admin remain private/internal with no ordinary MAIN/LAUNCHER exposure. V3's signature entry boundary and server role claim requirement are preserved; V6 strengthens the operator contract with passkey + second factor + <=300s fresh role claims. Hidden UI alone is not accepted as authorization.

## Builder discovery correction
The repository contains `.github/workflows/thf-apps-phone-v3-builder-discovery.yml`, which validates V3 authority and then searches the authorized GCP builder for the six exact source ZIPs by filename + SHA. Its push trigger is path-scoped to the workflow file itself. The observed push at commit `45074930701d6803e2d82bb39c720be6f52a9b7e` produced only the unrelated artifact-size-policy run in the accessible run set; therefore this checkpoint does **not** claim that builder discovery executed successfully and does not claim exact APK/AAB build evidence.

## Release truth
- `APP_SOURCE_AUTHORITY=V3_EXACT_SHA_PRESERVED`
- `IDENTITY_INTEGRATION_AUTHORITY=V6`
- `ANDROID_EXACT_BUILD=FALSE`
- `NETWORK_RELEASE_READY=FALSE`
- `PUSH_PROVIDER_READY=FALSE`
- `PRIVATE_DISTRIBUTION_PROVEN=FALSE`
- `PHYSICAL_DEVICE_PASS=FALSE`
- `PRODUCTION_SIGNING=FALSE`
- `FINAL_OR_PLAY_READY=FALSE`

Remaining external/runtime gates: execute exact-source builder discovery/build/package inspection; production OAuth/JWK/session/logout/delete/role issuer; provider push delivery; private internal distribution and signer parity for Publisher/Admin; exact-candidate physical-phone install/launch/touch/layout/background-resume/offline/network/accessibility/core-journey/crash-free evidence; production signing/legal/Play actions where applicable.
