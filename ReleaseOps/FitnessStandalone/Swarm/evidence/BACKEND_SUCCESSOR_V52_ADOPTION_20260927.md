# Fitness Backend V52 successor adoption

Status: `PROGRESS` — source and local contract gates passed; GitHub CI and authenticated non-destructive environment E2E remain fail-closed.

## Immutable source provenance

- Drive file: `17De4XMcHKAENViMN4QZkNd7yqHf4lyt_`
- Name: `THF_FITNESS_STANDALONE_V5_RC2_BACKEND_V52_SOURCE.zip`
- Size: `20,157,248` bytes
- SHA-256: `babfbcb997e7b5347da1141e1455aa290e1e143bac8d00c48fa65a0f6d02d1f6`
- Parent folder: `0AE_eISTZ0j1lUk9PVA`
- Original canonical parent: Drive `1gcOkJ-EXnCEbCHMcBSUWAwVcQxj4j40-`, SHA-256 `2290c5897eab827dd778204de03f6f70c49fd162a32d187e4844172ececf7b74`
- V51 predecessor: Drive `161Hd1XE45dpKBIdl4CeCsIeZE9-MnAzG`, SHA-256 `bd9676075750beafcfba5e2262cb505eaf1920b2f42b1965b2dbae05bfe0b428`
- Manifest: `BACKEND_SUCCESSOR_V52.json`, schema `thf-fitness-backend-successor-v2`, scope `backend_only`

The uploaded Drive object was downloaded again after upload. Its byte size, ZIP integrity, and SHA-256 matched the local source exactly.

## Local exact-source validation

- Source tests: `25 passed`, `0 failed`, `1` upstream Starlette/httpx deprecation warning.
- Auditor regression tests: `10 passed`, `0 failed`.
- ZIP integrity: PASS.
- Static release contract: `PROGRESS`; all nine contract checks passed, including auth/session, user scope, sync/report, server authority, set sequencing, Health ingestion, and Health provenance/deduplication.
- Runtime OpenAPI contract: `PROGRESS`; 61 paths, 62 operations, 26 protected mutations, 26 secured protected mutations, no issues.
- Declared schemes: `sessionCookie`, `adminKey`.
- Public authentication boundaries: login and registration explicitly use public OpenAPI security overrides; protected mutations remain declared and secured.

## Implemented backend boundaries

- Production-session authentication boundary and explicit cookie/admin OpenAPI schemes.
- User-scoped snapshot/delta sync.
- Health record provenance and deterministic deduplication.
- Server-authoritative workout set order and idempotent events.
- Finish replay rejection.
- Competition submission requires server state and verified activity proof.
- Account deletion removes Health and sync records.

## Fail-closed remainder

- GitHub Actions must retrieve this exact Drive ID, verify this exact SHA-256, and reproduce the source tests and both contract reports.
- An authenticated, non-destructive environment E2E must prove login, scoped workout write, second-client sync, logout/session revocation, and account deletion.
- No production deploy, release PASS, or Android/phone evidence is claimed by this checkpoint.
