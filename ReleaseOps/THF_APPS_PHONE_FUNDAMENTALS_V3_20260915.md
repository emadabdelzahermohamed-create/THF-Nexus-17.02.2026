# THF Apps Phone Fundamentals V3 — 2026-09-15

Status: SOURCE_CANDIDATE_ONLY / NOT_FINAL / NO_GO

## Authority
- App input authority: `THF_APPS_PHONE_FUNDAMENTALS_SOURCE_V2_MANIFEST.json`.
- Identity input authority: `thf.shared.integration.v4`; its CI run `34904946338` is PASS.
- Core/Hub is same-SHA skipped at `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`.
- Pulse, games and WAVE are excluded. No stale Batch11 V1 source is accepted as current authority.

## Completed V3 source batch
- Forge/Market, Echo/Community, Codex/Learn and Command/Admin now require validated Android Internet capability before treating network-required flows as online; captive/unvalidated connectivity fails into the existing offline/error state.
- Those WebView hosts now honor Android system Data Saver on metered networks in addition to the user Data Saver preference.
- All six changed sources declare notification runtime permission and create a real `thf_updates` NotificationChannel. Forge/Echo/Codex/Command expose permission through experience settings; Vault/Signal retain their native permission action and now create the channel.
- Provider push delivery is not claimed: FCM/APNs credentials and real subscription/delivery remain external gates.
- Existing onboarding, account/logout/delete routes, trusted HTTPS fail-closed behavior, RTL/accessibility preferences, 20 locale sets, API36 source, approved names, package IDs, adaptive icons, monochrome icons and 512x512 store icons are preserved.
- Publisher/Signal and Admin/Command remain private: no ordinary launcher, signature entry boundary, THF Pass handoff, authenticated server role claims. Publisher allows publisher/admin/owner; Admin only admin/owner.

## Validation
- All six V2 input ZIP SHAs matched authority before editing.
- XML/source assertions and Python compileall: PASS.
- Forge 1/1, Echo 4/4, Codex 6/6, Command 2/2: PASS.
- Deterministic ZIP rebuild, ZIP integrity and clean extraction: PASS for six V3 candidates.
- Authorized Android builder/device is disconnected, so APK/AAB build and physical-phone validation were not fabricated and no old APK was rebound.

## Exact V3 source candidates
- Forge / THF Market: `75c3744af31f16273a174bdac53b9e812613e4d9ef8c2fa260521c7f7c40cbf8` — 2.1.1-phone3 / 21102.
- Echo / THF Community: `3c90b53009d34e9c391bc8f977daf70195a041ba6c0098eca82709932b8734e9` — 2.1.1-phone3 / 21102.
- Codex / THF Learn: `44ff76cca12b6b13febc53e9e0b8748a01949eb07c40b020d76b82f45a094950` — 2.1.1-phone3 / 21102.
- Vault / THF Wallet: `e33c7c7f1f6d7f913dfe6ca5d674aff2883f7a230c2a323724088c30c4497585` — 1.2.0-apps-rc4 / 12002.
- Signal / THF Publisher: `3b6ba96076decd62e31a90c60d91a101806d6a6e9be329a58baa55ece82227ef` — 1.2.0-apps-rc4 / 12002.
- Command / THF Admin: `314a89f33f62d754edc9cc369fcc35b019d6081c6be0dcfbffa0fe5801ce0ffc` — 1.2.0-apps-rc4 / 12002.

## Persistent source storage
Exact V3 ZIPs, SHA list, manifest and clean-source checkpoint are stored under `/THF/ReleaseOps/Apps/2026-09-15/PhoneFundamentalsV3/` in Library.

## GitHub evidence
- PR #29 head `1ffcbf59987343febf75570270bc9425eabd156f`.
- PR authority run `34907427052`: SUCCESS.
- Merged main commit `541773ad0c73c019a303b887f8e5e4d3ed8b9e3d`.
- Post-merge `THF Apps Phone Authority V3` run `34907464011`: SUCCESS on exact merge SHA.
- Post-merge `THF No Arbitrary Artifact Size Cap V1` run `34907463960`: SUCCESS on exact merge SHA.

## Remaining hard gates
Exact-source API36 APK/AAB build/package inspection; deployed production OAuth/JWK/session/logout/delete/role issuer; provider push credentials and delivery proof; private internal distribution/signer parity; exact-candidate physical-phone acceptance.

`ANDROID_EXACT_BUILD=FALSE`
`NETWORK_RELEASE_READY=FALSE`
`PUSH_PROVIDER_READY=FALSE`
`PHYSICAL_DEVICE_PASS=FALSE`
`PRODUCTION_SIGNING=FALSE`
`FINAL_OR_PLAY_READY=FALSE`
