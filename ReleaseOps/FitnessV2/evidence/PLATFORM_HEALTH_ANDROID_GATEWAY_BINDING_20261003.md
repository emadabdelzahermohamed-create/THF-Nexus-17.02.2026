# Fitness V2 platform, Health and Android gateway evidence — 2026-10-03

## Scope and provenance

- Branch: `release/fitness-v2-rebuild-20261002`
- Exact candidate: `89937707206d5beebcfe7c6230290775c6cfa0a8`
- Live AppDeploy app: `thf-fitness-pulse-ul26f1`
- Applied AppDeploy version: `v69` / `1790998671035`
- Branded account origin: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`
- Native API gateway: `https://api-v2.appdeploy.ai/app/thf-fitness-pulse-ul26f1/`

The account origin and API gateway are intentionally separate. Direct `/api/*` requests to
the branded static origin return the SPA; the credential-free AppDeploy gateway is the
native HTTPS endpoint. Candidate `89937707` makes this distinction explicit in Gradle and
in the CI build binding.

## Live contract probes

Observed on 2026-10-03 between 13:35 and 13:37 UTC:

| Probe | Result |
|---|---|
| Account connection URL with valid-shaped S256 challenge | Arabic Android connection explanation and explicit sign-in button rendered |
| `GET /api/_healthcheck` on API gateway | `200 application/json`, `ok=true` |
| `GET /api/v2/workouts` without token | `401 {"error":"unauthorized"}` |
| `GET /api/v2/progress/summary` without token | `401 {"error":"unauthorized"}` |
| `POST /api/v2/auth/android/tickets` without browser auth | `401 {"error":"Unauthorized"}` |
| `POST /api/v2/auth/android/sessions` with invalid ticket/verifier | `400 {"error":"invalid_android_auth_exchange"}` |
| `POST /api/v2/workouts/sync` without token | `401 {"error":"unauthorized"}` |
| `/.well-known/assetlinks.json` on branded origin | `403 application/xml`; DAL remains open |
| `/privacy.html` and `/account-deletion.html` | `200 text/html` |

The `browser-use:qa` review scored the tested public connection surface **4/5**: the
bilingual, explicit, privacy-preserving bridge is reachable and the API fails closed, but
the authenticated sign-in/ticket/sync path was not completed without a disposable QA
identity and therefore is not marked PASS.

## Source and CI gates

- Local read-only Product tests: `11/11 PASS`
- Local Android/source contract tests: `10/10 PASS`
- Local backend tests: `8/8 PASS`
- Python compile, JavaScript syntax, secret scan, Stage16A scan and `git diff --check`: PASS
- GitHub Actions run: `37126932766` (`Fitness V2 Android Health Gate`, run 14)
- Source/backend job: `111214013531` — PASS
- Android job: `111214013405` — PASS
- Android unit tests represented by seven `@Test` contracts: PASS through the Gradle job
- Lint: `0 errors, 2 dependency-update warnings`

The unrelated monorepo workflow run `37126932012` failed before creating any jobs. It is
not used as Fitness V2 release evidence; the scoped Fitness V2 workflow above is green.

## Exact package evidence

- Artifact: `11274802669`, `fitness-v2-51003-package-gate`
- Artifact digest: `sha256:49a244b2640897e752083d48fbf02010ee84a49b75c71693068256c4d07e9e3d`
- Expiry: 2026-10-17 13:42:28 UTC
- Debug APK SHA-256: `6abb60bb8f2b50096ab933e7db24dd3bb15d93f05a5d981f42e8b909a813a705`
- Release AAB SHA-256: `d45c6486bd45e0de988864c2b996db488ed0a911add63c9ae1aaf20f5d484b3d`
- Package/version: `com.topherofit.thf.pulse`, `51003`, `5.0.0-v2-alpha3`
- compileSdk/targetSdk: 36/36; minSdk 26
- Architecture: bytecode-only; no native ABI payload
- Offline payload: 80 exercises, 26 programs, 160 demonstration images
- Stage16A entries: 0
- Embedded API gateway string in DEX: PASS
- Health permissions: steps, exercise read/write, distance and active calories only; no heart rate
- Production signing: `NOT_RUN_MISSING_ALL_FOUR_EXISTING_SECRETS`

## Gates deliberately left open

- No authenticated QA account ticket exchange or persisted workout sync/history/progress probe.
- No signed AAB, release certificate fingerprint or valid Digital Asset Links document.
- No emulator or physical-phone install/launch/background-resume/offline workout evidence.
- No Health Connect or Samsung Health-originated physical-device evidence.
- No Play Data Safety/Health apps declaration evidence and no Play Internal upload for 51003.

## Next release action

Complete one non-privileged authenticated PKCE and workout-sync roundtrip, then make the
existing four upload-signing secrets available to the protected workflow. Publish DAL
for the resulting certificate, rebuild exactly candidate `89937707`, and run the signed
artifact on a physical Android phone before any Play action.
