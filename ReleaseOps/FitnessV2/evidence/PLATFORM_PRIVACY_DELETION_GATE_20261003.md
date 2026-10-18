# Fitness V2 platform privacy, deletion and Android package evidence — 2026-10-03

## Exact provenance

- Branch: `release/fitness-v2-rebuild-20261002`
- Backend deletion checkpoint: `d246e494ad2c0b1841449a0455e9fccd4ab3fc08`
- Exact Android/package candidate: `d79c9c621dab30748e0779bd5a5fc35e385593d5`
- Live AppDeploy app: `thf-fitness-pulse-ul26f1`
- Live snapshot: `v69` / `1790998671035` — ready, but older than both checkpoints
- API gateway: `https://api-v2.appdeploy.ai/app/thf-fitness-pulse-ul26f1/`
- Account origin: `https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/`

## Changes closed in source

Checkpoint `d246e494` reconciles the AppDeploy V2 route source with the robust hashed,
per-resource persistence model and adds bounded deletion for V2 workout history, record
indexes, Android tickets/sessions, idempotency records and competition submissions. The
README defines the authenticated `DELETE /api/account` integration point and explicitly
does not represent app-data deletion as deleting the external identity-provider account.

Checkpoint `22c11488` adds visible Arabic/English Profile actions for Privacy policy and
Delete account data. Native code validates the persistent HTTPS account base, allowlists
only `privacy.html` and `account-deletion.html`, and opens the system browser with a
browsable intent. Public source pages disclose on-device Health Connect processing,
optional HTTPS workout sync, retention/deletion scope and the external identity limit.

Candidate `d79c9c62` adds a pinned TypeScript 5.9.3 strict/no-emit gate using a local
contract snapshot derived from the connected AppDeploy SDK database/router reference. It
also aligns the single-record helper with the SDK's `Omit<T, 'id'> & { id: string }`
return type, so the deploy overlay is compiled rather than accepted by marker tests alone.

## Tests and CI

- Local Product read-only tests: `11/11 PASS`
- Local source contracts: `12/12 PASS`
- Local backend unit/security tests: `8/8 PASS`
- Python compile, JavaScript syntax, secret scan, runtime Stage16A scan and diff check: PASS
- Run 15 (`37127748766`) on `d246e494`: PASS
  - source/backend job `111216430196`
  - Android job `111216430064`
  - artifact `11275483016`, digest
    `sha256:694fad8cae6cbf537df3e1b3487b19b766f4390dd29adae79939473a3c454a9f`
- Run 16 (`37128008075`) on exact candidate `22c11488`: PASS
  - source/backend job `111217207660`
  - Android job `111217207808`
  - artifact `11276240179`, `fitness-v2-51003-package-gate`
  - digest `sha256:edf92f9885fcce43d0374126972243f618b5208c69720dc420726fb8da67f8c8`
  - expiry `2026-10-17T14:00:58Z`
- Run 17 (`37145448540`) on exact candidate `d79c9c62`: PASS
  - source/backend job `111268310806`, including TypeScript 5.9.3 strict/no-emit: PASS
  - Android job `111268310629`
  - artifact `11281913738`, `fitness-v2-51003-package-gate`
  - digest `sha256:96f96c53460e2bd52fbbf877f759f78a4d3362d0bc62873882b3f200201b90f0`
  - expiry `2026-10-17T18:49:00Z`
- Android unit tests: `7/7 PASS`
- Lint: `0 errors`, two dependency-update warnings

## Exact package evidence

- Debug APK: 14,787,102 bytes,
  SHA-256 `8fa3d49ba45201b6d8efee55f7ff4724756e9a3b2ce99e2287044226083aaa9b`
- Release AAB: 13,638,076 bytes,
  SHA-256 `e1a7df202581a4660edeef2e324cc608f85bdba595f2fb3f26b61e223656fff0`
- Package/version: `com.topherofit.thf.pulse` / `51003`
- compileSdk/targetSdk: 36/36; minSdk 26
- Architecture: bytecode-only, no native ABI payload
- Offline payload: 80 exercises, 26 programs, 160 demo images, zero Stage16A entries
- Health permissions: read steps/exercise/distance/active calories and write exercise;
  no heart-rate permission
- Production signing: `NOT_RUN_MISSING_ALL_FOUR_EXISTING_SECRETS`
- CI explicitly records physical phone, Health Connect, Samsung origin and Play Internal as
  `NOT_RUN`.

## Live checks and fail-closed limits

The existing live v69 API healthcheck is 200 and protected V2 routes reject missing or
invalid credentials. Earlier `browser-use:qa` inspection confirmed the public bilingual
Android account bridge and kept authenticated behavior fail-closed because no disposable
QA session completed the ticket/sync roundtrip.

The live `/.well-known/assetlinks.json` returns HTTP 403. Existing live privacy/deletion
pages return 200 but predate this candidate. The candidate source cannot be deployed until
the AppDeploy free quota resets at `2026-10-04T00:00:00Z`; therefore V2 deletion and the
updated disclosures are **not live-pass evidence**.

No `adb` or emulator binary is available in this executor, and no physical phone is
connected. There is no physical install, background/resume, offline workout, Health
Connect, Samsung-origin or Play Internal evidence.

## Next gate

After quota reset, deploy exact candidate `d79c9c62`, verify privacy/deletion and a full
disposable-account PKCE/sync/idempotency/history/progress/deletion roundtrip, then sign one
exact 51003 AAB with the existing upload key. Publish certificate-correct DAL, complete
the prepared Play declarations, and run physical Health Connect/Samsung-origin QA before
any Play upload.
