# THF Apps Factory — APPS-RC2 i18n / federation hardening

Date: 2026-09-13
Scope: Pulse, Forge, Echo, Codex, Spark, Rush, Vault, Signal, Command. Core RC6 is unchanged/proven; THF Pass remains backend/SDK-only. Native games, WAVE and token finance are excluded from this source batch.

## What changed

A new reversible source checkpoint was produced from the authoritative APPS-RC1 sources. Vault and Signal first received the missing Stage16-Q style Android hardening: emulator/placeholder Android defaults removed, `THF_BASE_URL` and `THF_PASS_URL` are build-injected and fail closed unless HTTPS, target-bound THF Pass handoff was added, cleartext remains disabled, API 36/package identities are preserved, and RTL manifest support was added. Vault backend regression test: 1/1 PASS. Signal backend regression tests: 2/2 PASS.

All nine ordinary Android hosts were then advanced with native-chrome localization resources for 20 languages: English, Arabic, Spanish, French, German, Portuguese, Russian, Simplified Chinese, Hindi, Korean, Turkish, Indonesian, Japanese, Italian, Dutch, Polish, Urdu, Bengali, Persian and Swahili. Native retry/error/settings strings are resource-backed rather than hard-coded English, `supportsRtl=true` is present, and the existing `THF_NATIVE_PREFS` locale bridge to the web product is preserved.

The backend/test trees were byte-hash compared before/after this localization-only stage and are unchanged for all nine apps, so already-proven backend gates are not re-run merely because Android resources changed. This obeys the same-SHA/same-payload dedup rule while still testing the two Vault/Signal backend checkpoints whose Android-host hardening was new.

## Source artifacts and SHA-256

| App | Package | APPS-RC2 source SHA-256 |
|---|---|---|
| Pulse | `com.topherofit.thf.pulse` | `ef4d82dc1e3fff0d0bcdf0b7b31b9820aa9c958d846e9b1fd8ee6a19430ab6f8` |
| Forge | `com.topherofit.thf.forge` | `8f6bf74b15146bc0a895912c40b9946ef5c3cc8df99fdcae39fa615ce4f03eed` |
| Echo | `com.topherofit.thf.echo` | `09773a4c3890fc43ee8e15b37267555f9db0e471fe8cbdcefa3886d2a2def73a` |
| Codex | `com.topherofit.thf.codex` | `d8cf35346e244c141c65d4a5ce10e07f7fb2d4d6b831a0a63dd0b517d3ae0b83` |
| Spark | `com.topherofit.thf.spark` | `6b74f8d75df8c0b7f74d8c2fee8be7e3517f3803cb42968735bc7a10939bc18c` |
| Rush | `com.topherofit.thf.rush` | `bb6ff035186b13cdde853145f42e66259c205889de2a7b368da34c9cb0582ba7` |
| Vault | `com.topherofit.thf.vault` | `e53d0cb62296581b1d8b52ce040b10ac896607adcc049b78f06a75bc8c28f6c7` |
| Signal | `com.topherofit.thf.signal` | `87e199ff2c174990b6e0e4e4ddd8accc0d585d2675343067395ccdf9490e9fb1` |
| Command | `com.topherofit.thf.command` | `7dc686a9ad78ef90eec7cb2f7e65495356b3d513d9fc152c7ee8e3d20f91e487` |

All nine source ZIP integrity checks PASS. The artifacts and machine-readable evidence were saved in the THF Nexus persistent workspace; no old APPS-RC1 source was overwritten.

## Cross-app identity / handoff audit

Against the active source set after the Vault/Signal hardening:

- compileSdk/targetSdk 36: PASS for all nine.
- locked package identities: preserved.
- `THF_BASE_URL` + `THF_PASS_URL` injection: PASS for all nine.
- HTTPS fail-closed host behavior: PASS for all nine.
- `topherofit://pass/handoff` manifest contract + target mismatch guard: PASS for all nine.
- Android release-host placeholder/loopback endpoint defaults: none in active source.
- cleartext disabled: PASS for all nine.
- Android permissions remain limited to `INTERNET` and `ACCESS_NETWORK_STATE` in this host layer.
- Data Saver / Reduce Motion / High Contrast / text zoom and explicit offline/retry behavior are preserved.

## Truth boundary

This is a **source engineering checkpoint**, not a release promotion. No exact APK/AAB candidate was compiled from these new APPS-RC2 source hashes in this execution environment, so no static package/runtime/device PASS is claimed for them. Full 20-language web/backend content and responsive layout must still be verified end-to-end; adding native resource sets is not enough to claim product-level localization completion.

`FINAL` / `PLAY_READY` remains prohibited until the exact compiled candidate has package/payload inspection, reachable HTTPS/WSS backend health/auth where required, and physical-phone install/launch/touch/layout/orientation/background-resume/offline-network/core-journey/crash-free evidence. Core RC6 remains unchanged and its already-proven same-SHA gates were not repeated.

## Additional release-policy guard

The portfolio validator was strengthened so a promoted mobile candidate now requires an evidence object bound to the exact APK SHA, including package/payload inspection, real backend health/auth over HTTPS/WSS, device install/launch, touch/layout/orientation, background resume, real offline/network transitions, core journey, crash-free smoke, localization/RTL, accessibility, Data Saver and rollback. Mobile games additionally require player/avatar load, movement/camera/gameplay, and FPS/RAM/thermal observation. Placeholder/loopback backend evidence is rejected. CI regression coverage for these conditions is PASS.

## Next executable block

1. Stage these exact APPS-RC2 source artifacts into an Android-SDK-enabled private build workspace without exposing them through the public repository.
2. Compile QA candidates with API 36 and injected non-secret HTTPS endpoints, then inspect exact APK package/payload/SHA and reject any wrapper-only or placeholder configuration.
3. Run reachable backend health/auth and Pass federation integration against each candidate.
4. Produce physical-device evidence manifests. Signal/Command remain private/internal; THF Pass remains backend/SDK-only.
5. Keep production signing, public Play rollout, legal acceptance and any paid spend outside autonomous execution.
