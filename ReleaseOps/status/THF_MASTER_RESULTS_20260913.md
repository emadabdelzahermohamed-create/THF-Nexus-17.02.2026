# THF consolidated phone candidate status — 2026-09-14

## Product separation

### Apps
- THF Core — `com.topherofit.thf.core`
- THF Pulse — `com.topherofit.thf.pulse`
- THF Forge — `com.topherofit.thf.forge`
- THF Echo — `com.topherofit.thf.echo`
- THF Codex — `com.topherofit.thf.codex`
- THF Vault — `com.topherofit.thf.vault`
- THF Signal — `com.topherofit.thf.signal` — private/internal recommended
- THF Command — `com.topherofit.thf.command` — private/internal only
- THF Pass — backend/SDK only; no Play listing

### Games
- THF Terra / Nexus World — `com.topherofit.thf.terra`
- THF Rift / Nexus Arena — `com.topherofit.thf.rift`
- THF Spark — `com.topherofit.thf.spark`
- THF Rush — `com.topherofit.thf.rush`

## Current phone QA candidates
- Core RC6 OLD candidate: **SUPERSEDED** after physical phone test. It installed and native Experience Settings worked, but the main product failed closed because `THF_BASE_URL` / `THF_PASS_URL` were not injected.
- Core RC6 MobileFix1 LIVE QA: **SUPERSEDED FOR PHONE/DESIGN QA** after the physical phone test showed the account-less `trycloudflare.com` Quick Tunnel hostname expired/unresolved (`ERR_NAME_NOT_RESOLVED`). The APK itself installed and ran; the blocker was the temporary endpoint lifecycle.
- Core RC6 Phone UI1 Local QA: **CURRENT PHYSICAL PHONE/DESIGN CANDIDATE**. Build/test gate PASS in run `34838408684`; versionCode `62203`, versionName `6.2.2-rc6-phoneui1-debug`, package `com.topherofit.thf.core.debug`, targetSdk `36`, SHA-256 `465faa1a04a276c648ef851f758b79640eddff0c2b3bf382a7cf8021cc6aca71`, APK size `95,799` bytes. The real Core web UI, i18n and World3D assets are bundled inside the APK, so temporary external endpoint availability cannot block UI/touch/RTL/design/device QA. Backend-dependent features are intentionally not accepted by this candidate and will be tested after the phone/design pass using a persistent endpoint.
- Pulse RC3: QA APK build/inspect PASS.
- Forge RC3: QA APK build/inspect PASS.
- Echo RC4: QA APK build/inspect PASS.
- Codex RC4: QA APK build/inspect PASS.
- Vault RC4-BF1: corrected Gradle escaping; source tests + QA APK build/inspect PASS in run `34771821808`.
- Signal RC4-BF1: corrected Gradle escaping; source tests + QA APK build/inspect PASS in run `34771821808`.
- Command RC3: QA APK build/inspect PASS.
- Spark RC4: source tests + QA APK build/inspect PASS in run `34772013340`.
- Rush RC4: source tests + QA APK build/inspect PASS in run `34772013340`.
- Terra: staging QA APK exists at targetSdk 36; current confirmed stream source is RC34. Physical GPU/touch/perf acceptance remains pending.
- Rift: staging QA APK exists from an older source line. Current authoritative source state found in Library is RC41 (`4.7.5-rc41`, versionCode `42075`, targetSdk 36, SHA `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`). RC41 still requires exact artifact staging to WIF/GCP for fresh Godot parser/import/headless + Android candidate export before it can supersede the older phone APK.

## Current execution priority
Phone/device/design acceptance comes first. For each app/game: latest source -> installable APK -> physical phone launch -> UI/RTL/touch/navigation/performance review -> fix -> repeat until design/device acceptance. Persistent backend integration, production signing, Play Internal and final security hardening follow after the phone/design candidate is accepted, except blockers that prevent safe installation or execution.

## Truth boundary
All APKs above are QA/test candidates, not production-signed Play releases. Core Phone UI1 is deliberately self-contained for physical design/compatibility QA; it is not evidence that backend-dependent flows are complete. Production final requires persistent backend endpoints, physical-device functional acceptance, production signing, Play Internal validation/declarations, then rollout. Terra/Rift delivery also requires the agreed package-size strategy (AAB/Play Asset Delivery or separated assets); do not treat the ~197 MB staging APKs as the final <=100 MB delivery format.

WAVE-MAWJA remains a separate project and is not modified by these THF release operations.
