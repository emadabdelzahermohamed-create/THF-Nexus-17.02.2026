# TopHeroFit Fitness 51014 — Google Play Internal checkpoint — 2026-10-26

## Verified release state
- Package: `com.topherofit.thf.pulse`
- Version: `versionCode 51014`, `versionName 5.0.0-v2-alpha14`, `targetSdk 36`.
- Integrated release PR: `#102`, merged to `agent/codex/fitness-recovery/20261023` as `70263bb6965e794ec03dcf3811c3656dc6d46b54`.
- Exact built source/workflow SHA: `50188b65efe335955d0296b67ac34465e5477a85`.
- Deterministic Android build run: `40288559837` — SUCCESS.
- Build artifact: `fitness-activity-candidate-51014`, artifact ID `12635312914`, archive digest `sha256:bbd8f18a2882c6b978b523fd4413a5559266718d92e6b12da80f428af8f6aeaa`.
- Debug APK SHA-256: `39fc9ab633408d8559b0eef832a17a3dd87687bfdbd5656a82829e3ce545cfde`.
- Unsigned release AAB SHA-256: `49f04748f45436448f0d37bd4834af177be2fb941e74ab9882d1f5ddb223dfa4`.
- Signed Play-bound AAB SHA-256: `7b6a13bc8816278bede06a58da59a2792f25fb0d2ff9953cb54837d00b848621`.
- Play promotion workflow commit: `d674b56854099024cceb75bd4daa90623dcdbedc`.
- Play promotion run: `40289036989` — SUCCESS.
- Publisher result: `committed=true`, track=`internal`, versionCode=`51014`, source run=`40288559837`, source SHA=`50188b65efe335955d0296b67ac34465e5477a85`.
- Independent read-only publication probe: `40289183287` — SUCCESS.
- Independent Android Publisher readback: track=`internal`, release=`THF Fitness 51014 Internal`, status=`completed`, versionCodes=`[51014]`.
- Redundant canonical build run `40288969600` was cancelled because the merged canonical Fitness/build-workflow bytes were identical to the already-green exact source.

## Included material changes
1. **Activity process-death recovery** (PR #100 lineage): active walking/running/cycling session checkpoints persist measured mode/weight/start/distance/step baseline+delta/GPS route. Null-intent service recreation restores only recent same-boot state. Reboot-like elapsedRealtime reset fails closed. Restarts delayed more than two minutes fail closed, and accepted restart downtime is excluded from elapsed metrics so time/calorie estimates are not inflated. Explicit Stop/switch clears the checkpoint.
2. **Persistent bilingual voice guidance** (PR #101 lineage): automatic Arabic-Egypt / English-US exercise guidance using the existing native TTS bridge with browser fallback, with product/source/backend contract coverage.

## Verification before release
- Combined source tests: `40/40` PASS.
- Combined product tests: `38/38` PASS.
- Backend tests: `15/15` PASS.
- Voice JavaScript syntax checks: PASS.
- `git diff --check`: PASS.
- Android unit tests, lint, debug APK and release AAB: PASS in exact run `40288559837`.
- Upload-key certificate, jarsigner verification and bundletool identity validation: PASS in exact promotion run `40289036989`.

## Still fail-closed / not claimed
- **No public Production release is claimed.**
- Physical-phone 51014 propagation/runtime QA remains separate until the Play-installed phone actually reports versionCode 51014 and safe interactive tests are run.
- Process-death recovery is code/CI proven but requires exact-candidate physical process-death QA before a phone PASS claim.
- Broad Health Connect expansion in PR #93/#98 remains HOLD. Its extra Health data types must be reconciled with Google Play Health declarations/privacy and physically verified before a future release.
- Reboot recovery is not claimed; the activity checkpoint deliberately fails closed across reboot-like monotonic-clock reset.
