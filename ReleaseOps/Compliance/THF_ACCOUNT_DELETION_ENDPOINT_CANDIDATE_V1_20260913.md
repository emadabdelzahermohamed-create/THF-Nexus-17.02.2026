# THF Account Deletion Endpoint Candidate V1

Status: **PASS-CANDIDATE / NOT DEPLOYED**

## Provenance
- Successful GitHub Actions run: `34721247945`
- Workflow commit: `3d073c7cfcdda77dd49121f3b50f84160806aa02`
- Canonical input archive: `THF_NEXUS_6_FINAL_SOURCE_20260829.zip`
- Canonical input SHA-256 before and after: `8c060bdb7776ccf485b6294cda513a75b0fd3be28d43a416431d1368260a4884`
- Canonical archive mutation: FALSE
- Production runtime mutation: FALSE

## Candidate artifact
- Builder path class: `~/thf-runtime-s1/candidates/` (separate from runtime and canonical source)
- Candidate basename: `THF_NEXUS_6_ACCOUNT_DELETE_ENDPOINT_CANDIDATE_V1_34721247945.zip`
- Candidate SHA-256: `354155753ab5ec7630b14f0b8814eba024b8d03a19c879752a7dbc54b84c5d14`
- Size: `159743` bytes
- THF/WAVE isolation: PASS

## Implemented candidate contract
- Adds `DELETE /api/account`.
- Adds HTTP `do_DELETE` dispatch.
- Target user id is derived exclusively from `_need_user()['id']`, which resolves the validated bearer session. No request-body/path user-id selector is accepted.
- Adds `IdentityService.delete_account(uid)` using the schema-metadata deletion transaction validated in the previous DB gate.
- Mandatory user-owned `NO ACTION` rows are deleted; nullable attribution rows are anonymized; schema `CASCADE`/`SET NULL` actions are honored.
- `PRAGMA foreign_key_check` must be clean before commit.

## Tests
- Python parser/compile: PASS.
- Account creation on disposable DB: PASS.
- Authenticated-session identity binding contract: PASS.
- User deletion transaction: PASS.
- Session invalidation: PASS.
- Profile/user-owned chat removal: PASS.
- Post-delete `PRAGMA foreign_key_check`: PASS.
- Candidate packaging: PASS.

## Known remaining blocker
`FILESYSTEM_MEDIA_CLEANUP=NOT_YET_IMPLEMENTED`. Database identity deletion is not sufficient if avatar/media/object files owned by the account remain on local/object storage. This must be inventoried and tested before the candidate is eligible for release.

The endpoint also still needs an HTTP end-to-end gate and the independent public `/account-deletion` instructions/resource required for store compliance.

## Safety
- Production DB mutation: FALSE
- Production signing: FALSE
- Google Play upload: FALSE
- Cloudflare production cutover: FALSE
- Solana financial action: FALSE
- WAVE_MAWJA mutation: FALSE

## Next
Inventory the canonical source’s avatar/media storage ownership and deletion primitives, then extend this candidate with safe owned-file cleanup on a disposable filesystem fixture before HTTP end-to-end testing.