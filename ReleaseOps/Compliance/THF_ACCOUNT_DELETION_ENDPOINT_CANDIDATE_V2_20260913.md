# THF Account Deletion Endpoint Candidate V2

Status: **PASS-CANDIDATE / NOT DEPLOYED**

## Evidence
- GitHub Actions run: `34721464414`
- Workflow commit: `18bfbfeabaf730f2349ffe5c86033ef6841d317c`
- Canonical input: `THF_NEXUS_6_FINAL_SOURCE_20260829.zip`
- Canonical SHA-256 before/after: `8c060bdb7776ccf485b6294cda513a75b0fd3be28d43a416431d1368260a4884`
- Candidate artifact: `THF_NEXUS_6_ACCOUNT_DELETE_ENDPOINT_CANDIDATE_V2_34721464414.zip`
- Candidate SHA-256: `2b027ea4bfdbdbf29f3b3cb72201912b798aaf7c078415b738e9379c3515edd8`
- Candidate size: `159630` bytes
- Candidate location class: `~/thf-runtime-s1/candidates/` (separate from canonical source and production runtime)

## Candidate behavior
`DELETE /api/account` remains identity-bound exclusively to the validated bearer session through `_need_user()['id']`.

V2 adds constrained local-file cleanup coordinated by `Runtime.delete_account(uid)`:
- local Media files accepted only from `/media/file/<basename>` references with exact `<uid>_...` ownership prefix;
- stale `.upload-<uid>-*.tmp` files are included;
- Avatar photo and GLB are derived/validated against the account's trusted `avatar_id` and exact canonical `runtime/uploads/<avatar_id>.img` / `runtime/avatars/<avatar_id>.glb` paths;
- every local target is resolved and constrained to the expected storage root;
- owned files are same-filesystem renamed into a per-account staging directory before the DB transaction;
- on DB failure, staged files are restored;
- after successful DB commit, the stage is removed;
- arbitrary DB paths are never blindly unlinked.

## Tests passed on disposable source + DB + filesystem
- canonical archive SHA verification: PASS
- unsafe/path-traversal reference rejected before deletion: PASS
- rejected account remains in DB: PASS
- rejected account's real media remains present: PASS
- unrelated sentinel file preserved: PASS
- service-generated local media cleanup: PASS
- service-generated Avatar likeness image cleanup: PASS
- generated Avatar GLB cleanup: PASS
- stale account upload temp cleanup: PASS
- session invalidation after successful account deletion: PASS
- user/media/avatar DB removal: PASS
- `PRAGMA foreign_key_check`: PASS
- Python compile/parser: PASS
- HTTP route-to-session binding contract: PASS
- THF/WAVE isolation: PASS

## Safety
- Canonical archive mutation: FALSE
- Production runtime mutation: FALSE
- Production DB mutation: FALSE
- Production signing: FALSE
- Google Play upload: FALSE
- Cloudflare production cutover: FALSE
- Solana/token financial action: FALSE
- WAVE_MAWJA mutation: FALSE

## Remaining release gates
1. Run an HTTP end-to-end test against a disposable server instance using real register/auth + `DELETE /api/account`, and verify the old token fails afterward.
2. Add an independent public `/account-deletion` instructions/resource; the current production route is still SPA fallback.
3. Add independent Privacy, Terms, and `/.well-known/security.txt` resources and rerun Compliance V2.
4. If external object storage becomes active, add provider-specific owned-object cleanup and rerun this gate.
5. Keep production deployment/signing/publishing behind the existing explicit authorization gates.

WAVE_MAWJA remains technically isolated and unchanged.