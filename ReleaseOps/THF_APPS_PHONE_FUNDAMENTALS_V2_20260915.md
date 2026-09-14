# THF Apps Phone Fundamentals V2 — 2026-09-15

Status: SOURCE_CANDIDATE_ONLY / NOT_FINAL / NO_GO

## Authority and scope
- Base `main`: `ea8e99a2c4f08669913d8822650e5b8ac0cc2468`.
- The six V1 source ZIPs were independently SHA-256 matched to the latest authoritative Phone Fundamentals V1 manifest before editing.
- Core/Hub remains same-SHA skipped because editable exact bytes matching its authoritative source are unavailable; no replacement/fork was fabricated.
- Pulse, all game code, and WAVE were not modified.

## Completed phone-fundamentals batch
- THF Market/Forge, Community/Echo, Learn/Codex, Wallet/Vault, Publisher/Signal and Admin/Command now include first-run onboarding.
- All six now expose explicit account, logout and account-deletion call sites through separately injected `THF_ACCOUNT_URL`, `THF_LOGOUT_URL`, and `THF_DELETE_ACCOUNT_URL`. Missing, non-HTTPS or offline endpoints fail closed. No placeholder endpoint was introduced.
- Wallet and Publisher native UI controls use Android string resources with Arabic + English copy; all six preserve exactly 20 locale resource sets and RTL support.
- Package IDs are unchanged. API 36, Data Saver hooks, adaptive launcher assets, Android 13+ monochrome icons and 512x512 store icons are preserved.
- Publisher remains private: no MAIN/LAUNCHER, signature-protected entry, and now a target-bound THF Pass HTTPS handoff must return `state=authenticated`, a non-empty subject and role `publisher|admin|owner` before its functional UI is built.
- Admin remains private: no MAIN/LAUNCHER, signature-protected entry, and its target-bound handoff requires `admin|owner`. A publisher-only claim cannot open Admin.
- These are fail-closed client call sites enforcing server-returned claims; they are not a claim that production THF Pass, OAuth providers, signer parity, or private distribution is deployed.

## Exact V2 source candidates
- Forge / THF Market: `c19e0b9feab81f72d07a07cb3b13960caf34c5f62eb73789bd9e0893c4dd4eac` — v2.1.1-phone2 (21101).
- Echo / THF Community: `2b0c7097096d14fa257d6ba66e4a9dbb3c729d73ab710fb88316006b0ee191a5` — v2.1.1-phone2 (21101).
- Codex / THF Learn: `06a79845ffb4901cbc054d38e7b32a37098012068e1977d2f3e64fc8e4e00e36` — v2.1.1-phone2 (21101).
- Vault / THF Wallet: `5bcea1b79a8a37e1d3777aa2af7890fa1e0d83d83b0012aab1bcf74491080fb0` — v1.2.0-apps-rc3 (12001).
- Signal / THF Publisher: `6a62afe8f00a6b48a9f369b145b1915e4aa3d089e625f95bd612296b02114dbe` — v1.2.0-apps-rc3 (12001).
- Command / THF Admin: `b41ae40be2b944874686098ab8438343d4fd438b6029bffa175d10a970055798` — v1.2.0-apps-rc3 (12001).

## Verification
- Deterministic source ZIP rebuild: PASS for all six.
- ZIP integrity + clean extract: PASS for all six.
- Package/API36/version/XML/20-locale/onboarding/account-routes/HTTPS-fail-closed/RTL/icon/launcher-policy assertions: PASS for all six.
- Private Signal/Command signature-boundary + server-role-gate assertions: PASS.
- Clean-extract backend tests: Forge 1/1 PASS; Echo 4/4 PASS with an ephemeral test-only `ADMIN_KEY`; Codex 6/6 PASS; Command 2/2 PASS. Python compileall PASS for these backend trees.
- PR #28 head `d95ee7333ed04fbded3ac83cd6af41f987492265`: `THF Apps Phone Fundamentals V2` run `34902698519` PASS; `THF No Arbitrary Artifact Size Cap V1` run `34902698442` PASS.
- PR #28 merged into `main` at `fff7f2a24ffa3e09ffcb8a0a6191f18d31330b48`.
- Exact Android APK/AAB compile/package inspection: NOT RUN. The authorized remote Desktop Commander builder/device is currently unavailable and the local execution container has no Android SDK/Gradle toolchain. No previous APK was rebound to a new source SHA.

## Persistent artifacts
The six exact V2 source ZIPs, SHA list, manifest, and clean-extract validation are stored under `/THF/ReleaseOps/Apps/2026-09-15/PhoneFundamentalsV2/` in the persistent THF Library.

## Remaining release gates
1. Build these exact source SHAs on an authorized API36 Android builder; inspect package/version/payload/icons/zipalign/signature and preserve SHA authority.
2. Bind reachable trusted THF Identity/Pass account/session/logout/delete endpoints and private role-claim handoff; external OAuth/provider consent remains a gate.
3. Bind provider push credentials and prove a real subscription/delivery path where notifications are required; no fake notification state was added.
4. Prove private/internal catalog distribution and production signer parity for Publisher/Admin.
5. Obtain exact-candidate physical-phone install/launch/touch/layout/background-resume/offline/network/accessibility/core-journey/crash-free evidence.

`ANDROID_EXACT_BUILD=FALSE`
`NETWORK_RELEASE_READY=FALSE`
`PHYSICAL_DEVICE_PASS=FALSE`
`PRODUCTION_SIGNING=FALSE`
`FINAL_OR_PLAY_READY=FALSE`
`PULSE_TOUCHED=FALSE`
`GAMES_TOUCHED=FALSE`
`WAVE_TOUCHED=FALSE`
