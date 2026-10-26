# TopHeroFit Fitness 51013 — Google Play Internal checkpoint — 2026-10-26

## Canonical release delta
- Package: `com.topherofit.thf.pulse`
- Candidate: `versionCode 51013`, `versionName 5.0.0-v2-alpha13`, `targetSdk 36`.
- Play-safe integration PR: `#99`, merged to `agent/codex/fitness-recovery/20261023` as `0d8de1056a1946b746c10edb3785ab5f1e13d1f6`.
- Exact built source SHA: `56e67762f8753526fb62bb0063033fdc1f136103`.
- Deterministic Android build run: `40284690599` — SUCCESS.
- Candidate artifact: `fitness-activity-candidate-51013`, artifact ID `12632764313`, archive digest `sha256:69b9c9877b24acea4ee9ffdd53e472f3728ae406ac931a076f998a07c3256149`.
- Debug APK SHA-256: `c3f12818a55afbfa3d259657a10191a9d0dcf9e8ae9de41150b1ccd351aa54ca`.
- Unsigned release AAB SHA-256: `0f8805c4e669cc98a131ca1f1d05dcb9f7df364a03e867dc69df6e2054c14a21`.
- Signed release AAB SHA-256: `680a01d87560abaa1905360dad0e94ee0686a7cd84a86e501c8e55edd765741e`.
- Play promotion run: `40285259055` — SUCCESS.
- Promotion source binding: run `40284690599`, source SHA `56e67762f8753526fb62bb0063033fdc1f136103`, versionCode `51013`.
- Publisher result: `committed=true`, track=`internal`, versionCode=`51013`.
- Independent read-only publication probe: run `40285416323` — SUCCESS.
- Independent Play readback: track=`internal`, release=`THF Fitness 51013 Internal`, status=`completed`, versionCodes=`[51013]`.
- Duplicate canonical rebuild `40285102974` was cancelled after proving no `fitness-v2`/candidate-workflow byte difference from the already-green exact source.

## Included release changes
- Reduced-motion preference persistence.
- Health status screen-reader semantics.
- Forced-colors accessibility preservation.
- Explicit motion preference override.
- Invalid calorie-input hardening.
- Bilingual guidance diversity gate.
- Fail-closed physical-phone preflight tooling from PR #90.

## Verification before build
- Fitness source/preflight tests: `39/39` PASS.
- Product tests: `36/36` PASS.
- Backend tests: `15/15` PASS.
- Preflight shell syntax: PASS.
- `git diff --check`: PASS.
- GitHub Android job passed unit tests, lint, debug APK and release AAB generation.

## Deliberately not released in 51013
PR #93 broad Health Connect service/data-type expansion is source/build proven separately by run `40284169005` at SHA `9b9a7310501712ae152c96ec5afc0f85defb6bde`, but its additional Health Connect data types are not included in the Play-safe 51013 release. Google Play declaration/privacy reconciliation is required before those broader permissions are shipped.

## Physical-device truth boundary
The authorized SM-A217F remains connected through ADB, but the fail-closed preflight returned `DEVICE_NOT_INTERACTIVE` during this release cycle. No forced wake/unlock, data erase, reinstall, or active-workout interruption was performed. Therefore 51013 is **BUILT + SIGNED + PLAY INTERNAL COMMITTED + INDEPENDENTLY READ BACK**, but **PHONE 51013 remains PENDING**. Production remains blocked on actual physical/runtime and policy gates.
