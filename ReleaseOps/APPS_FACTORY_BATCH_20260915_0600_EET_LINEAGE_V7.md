# THF Applications Factory — V7 lineage / no-regression checkpoint

Status: `NO_APP_SOURCE_EDIT / FAIL_CLOSED / NOT_FINAL / NO_GO`

## Scope
Included: THF Hub/Core, THF Market/Forge, THF Community/Echo, THF Learn/Codex, THF Wallet/Vault, private THF Publisher/Signal, private THF Admin/Command, and THF Identity integration surfaces.

Excluded and untouched: THF Fitness/Pulse, all game code, WAVE.

## Latest lineage proved before work
- Observed `main` head at intake: `62a694accf8b4688a5c078c7d82de6b7b7d3c5a8` (`ci(integration): gate shared integration V7`).
- Newest app-source authority remains `ReleaseOps/THF_APPS_PHONE_FUNDAMENTALS_SOURCE_V3_MANIFEST.json`; exact app bytes are unchanged from the prior V3 checkpoint, so same-SHA skip applies and no redundant source rewrite/build is authorized.
- Core/Hub remains same-SHA skipped at `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`.
- V3 exact sources remain Forge `75c3744af31f16273a174bdac53b9e812613e4d9ef8c2fa260521c7f7c40cbf8`, Echo `3c90b53009d34e9c391bc8f977daf70195a041ba6c0098eca82709932b8734e9`, Codex `44ff76cca12b6b13febc53e9e0b8748a01949eb07c40b020d76b82f45a094950`, Vault `e33c7c7f1f6d7f913dfe6ca5d674aff2883f7a230c2a323724088c30c4497585`, Signal `3b6ba96076decd62e31a90c60d91a101806d6a6e9be329a58baa55ece82227ef`, Command `314a89f33f62d754edc9cc369fcc35b019d6081c6be0dcfbffa0fe5801ce0ffc`.
- No old APK is eligible to be rebound to these source SHAs; exact Android build/package/device evidence remains required.

## Identity authority advanced to V7
The newest committed THF Identity/shared-integration authority is now `ReleaseOps/integration_factory/ANDROID_SHARED_INTEGRATION_V7.json`, extending V6 without package-ID changes. This checkpoint therefore supersedes the prior Apps Factory V6 lineage reference; no downgrade to V6/V4 is permitted.

V7 release-critical contracts used by in-scope applications:
- device-bound sessions and proof-of-possession are required;
- client-provided roles are never authoritative;
- private Publisher/Admin operator routes remain invisible to ordinary users;
- server role claims are authoritative, device proof is required, and step-up age is capped at 300 seconds;
- physical-device and FINAL/PLAY_READY remain false.

V7 also records external runtime activation truth as unverified for production Google OAuth, durable session storage and Android device-key runtime. Those items are not promoted by source-only or CI-only evidence.

## CI/no-regression evidence
At exact V7 gate SHA `62a694accf8b4688a5c078c7d82de6b7b7d3c5a8`, GitHub check `validate` completed SUCCESS. The V7 workflow compiles V4-V7 integration runtimes, executes V4-V7 regression tests, and validates package-ID preservation, device-bound identity, non-authoritative client roles, ordinary-user invisibility/server-authoritative operator routes, and fail-closed release truth. Artifact-size policy also completed SUCCESS on the same SHA.

Because app source SHAs did not change, previously proven V3 phone fundamentals are preserved by same-SHA skip: onboarding, real account/logout/delete call sites, trusted-HTTPS fail-closed behavior, validated-network requirement, Android Data Saver integration, offline/loading/error states, notification channel/runtime permission, RTL/accessibility, 20 locale resource sets, API36 source, approved visible names, adaptive icons, monochrome icons and 512x512 store icons.

## Release truth
- `APP_SOURCE_AUTHORITY=V3_EXACT_SHA_PRESERVED`
- `IDENTITY_INTEGRATION_AUTHORITY=V7`
- `IDENTITY_V7_CI=PASS`
- `ANDROID_EXACT_BUILD=FALSE`
- `NETWORK_RELEASE_READY=FALSE`
- `PUSH_PROVIDER_READY=FALSE`
- `PRIVATE_DISTRIBUTION_PROVEN=FALSE`
- `PHYSICAL_DEVICE_PASS=FALSE`
- `PRODUCTION_SIGNING=FALSE`
- `FINAL_OR_PLAY_READY=FALSE`

Remaining external/runtime gates: exact-source Android build/package inspection; production OAuth/JWK/session/logout/delete/role issuer and durable session store; push-provider delivery; private Publisher/Admin internal distribution and signer parity; exact-candidate physical-phone install/launch/touch/layout/background-resume/offline/network/accessibility/core-journey/crash-free evidence; production signing/legal/Play actions where applicable.
