# THF Account Deletion HTTP E2E V1

Status: **PASS-CANDIDATE / DISPOSABLE SERVER ONLY**

## Evidence
- GitHub Actions run: `34721620117`
- Workflow commit: `17c071882c47a47cca2236e3d473b977e5aabda1`
- Candidate tested: `THF_NEXUS_6_ACCOUNT_DELETE_ENDPOINT_CANDIDATE_V2_34721464414.zip`
- Candidate SHA-256 verified before test: `2b027ea4bfdbdbf29f3b3cb72201912b798aaf7c078415b738e9379c3515edd8`
- Test server: disposable `ThreadingHTTPServer` bound to `127.0.0.1` on an ephemeral port, using a disposable SQLite DB.
- GitHub OIDC/WIF -> GCP -> IAP: PASS

## HTTP results
- `POST /api/auth/register` -> `201`: PASS
- authenticated `GET /api/profile` before deletion -> `200`: PASS
- anonymous `DELETE /api/account` -> `403`: PASS
- authenticated `DELETE /api/account` -> `200`: PASS
- deleted response reports `ok=true`, `deleted=true`: PASS
- old bearer token on `GET /api/profile` after deletion -> `403`: PASS
- repeated `DELETE /api/account` with the revoked token -> `403`: PASS

Result: `HTTP_ACCOUNT_DELETION_E2E=PASS`.

This HTTP gate complements the V2 candidate filesystem/DB tests, which already prove owned-media/avatar cleanup, path-traversal fail-closed behavior, unrelated-file preservation, session invalidation, and clean foreign-key verification.

## Safety
- Production runtime mutation: FALSE
- Production DB mutation: FALSE
- Production signing: FALSE
- Google Play upload: FALSE
- Cloudflare production cutover: FALSE
- Solana/token financial action: FALSE
- THF/WAVE isolation: PASS
- WAVE_MAWJA mutation: FALSE

## Remaining account-deletion release work
The backend deletion path is now proven through HTTP on the reversible candidate. Remaining release work is primarily user-facing/compliance integration:
1. verify whether any THF web/native client already exposes an account-deletion control;
2. add/wire a client control if missing;
3. provide an independent public `/account-deletion` instructions/resource rather than SPA fallback;
4. complete independent Privacy, Terms and `/.well-known/security.txt` resources;
5. rerun policy/compliance and Android release-readiness gates on the consolidated versioned candidate.

No production deployment is authorized by this checkpoint.