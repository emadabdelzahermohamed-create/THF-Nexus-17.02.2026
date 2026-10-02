# Fitness V2 Platform, Health Connect and Android evidence — 2026-10-02

## Exact candidate

- Branch: `release/fitness-v2-rebuild-20261002`
- Candidate SHA: `0aa8336c18e09037457d6e30745fedaffa47d581`
- Backend source checkpoint included in candidate: `ea99b454a8ebefd0ca6cd1d34c16c05ac2bfd21d`
- Android hardening checkpoint included in candidate: `82ec187eb0fe1ce03a0cafffaa9c9259387cb3b5`
- Package: `com.topherofit.thf.pulse`
- Version: `51002` / debug name `5.0.0-v2-alpha2-debug`

## Backend/data contract

The candidate adds an HTTPS-only WSGI boundary around a per-account SQLite workout store. Tokens are issuer/audience-bound, short-lived HS256 credentials selected through a runtime key id; no development key is accepted. The API validates stable client record IDs and versions, idempotency, provenance, timestamps, set values and account isolation. It persists sets/reps/load/rest/RPE/RIR and derives workout history, volume, personal records and competition comparisons from server-stored facts.

Evidence:

- Local backend tests: 8/8 PASS.
- Python compile gate: PASS.
- Secret/private-key/placeholder-cleartext scan: no findings.
- GitHub source-and-backend job: `110981592612`, PASS.
- Live deployment: NOT RUN. The existing AppDeploy origin returned `text/html` SPA content for V2 paths rather than the required authenticated JSON API.
- AppDeploy deployment preparation was attempted once and returned `CREDITS_USAGE_LIMIT_REACHED`; its reported daily reset is `2026-10-03T00:00:00Z`. No paid upgrade was started.
- Account integration: NOT RUN. Android exposes `setBackendAccessToken` as a memory-only bridge, but the packaged V2 Product JavaScript does not acquire a production access token or call that bridge. The live AppDeploy account runtime is still the earlier product and is not evidence of a V2 Web/Android account model.

## Android/Health source and package gates

Health Connect is discoverable in the packaged navigation and includes connection status, pre-permission rationale, last-sync/pending/error/empty states, permission refresh on resume, settings/revoke handling and stable versioned write IDs. Requested Health permissions are limited to steps, exercise sessions, distance, active calories and writing completed exercise sessions. Heart rate, sleep, weight and body-fat permissions are absent.

Automated results:

- Local Android/source contract tests: 8/8 PASS.
- Android/JUnit tests in the exact CI artifact: 4/4 PASS, 0 failures, 0 ignored.
- Workflow: `Fitness V2 Android Health Gate` run `37050254091`, run number 9, PASS.
- Source/backend job: `110981592612`, PASS.
- Android build job: `110981592351`, PASS.
- Lint: 0 errors, 2 `GradleDependency` update notices. The previous backup/orientation/i18n/KTX findings were removed.
- Manifest/package: API 36 compile/target, minSdk 26, cleartext disabled, localized Arabic/English label and Health rationale, backup/device-transfer data excluded.
- Architecture: bytecode-only; no native `.so` and therefore no native ABI split to omit arm64.

## Exact artifact

- Artifact id: `11246003209`
- Name: `fitness-v2-51002-package-gate`
- Artifact digest: `sha256:2f789efae1bd7fecbb79ee3b7bf4def5193e8d673ca861377aff7769ca008fda`
- Size: 28,195,657 bytes
- Expires: `2026-10-16T18:53:53Z`
- Debug APK: 14,772,846 bytes; SHA-256 `168f4e269176fbfe07c4e13bb7aad0e394face57776ec6f6e5c06e712b5d74da`
- Release AAB: 13,629,532 bytes; SHA-256 `86d7a54e4d3ba358f6a38fa82a2b3d8e82afc091d0e1a229257cac67ca8696d7`
- Payload: 80 exercises, 26 programs and 160 offline demonstration images.
- Stage16A payload entries: 0.

## Fail-closed boundary

This is progress, not release closure. The AAB is unsigned because all four existing upload-signing secrets were unavailable to the workflow. `THF_FITNESS_V2_BASE_URL` was not configured, no production V2 endpoint has been validated, and no production account-token acquisition/handoff path is reachable from the packaged client. No emulator or physical phone was available, so install/launch, background/resume, offline workout, real Health Connect permission/read/write, Samsung Health-originated activity and exact-candidate Play Internal are all NOT RUN. None is claimed PASS.

## Next task

After the authorized free deployment quota resets, deploy the authenticated V2 API to a persistent HTTPS runtime, validate the JSON contracts using a non-privileged test account, complete a secure account-token handoff into the memory-only Android bridge, bind that URL, produce one signed versionCode 51002 AAB using the existing protected upload key, and run exact-artifact physical phone and Health Connect/Samsung-origin QA before Play Internal.
