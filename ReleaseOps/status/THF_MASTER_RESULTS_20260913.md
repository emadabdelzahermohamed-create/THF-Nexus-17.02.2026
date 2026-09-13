# THF consolidated phone candidate status — 2026-09-13

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
- Core RC6: Android CI candidate exists; physical-device acceptance pending.
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

## Truth boundary
All APKs above are QA/test candidates, not production-signed Play releases. Production final requires physical-device acceptance, any resulting fixes, production signing, Play Internal validation/declarations, then rollout. Terra/Rift delivery also requires the agreed package-size strategy (AAB/Play Asset Delivery or separated assets); do not treat the ~197 MB staging APKs as the final <=100 MB delivery format.

WAVE-MAWJA remains a separate project and is not modified by these THF release operations.
