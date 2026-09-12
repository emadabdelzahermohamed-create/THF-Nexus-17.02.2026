# THF Account Client Candidate V1 — Evidence

Date: 2026-09-13
Status: PASS-CANDIDATE
Scope: THF only. WAVE_MAWJA remained isolated and untouched.

## Source and build

- Workflow: `THF Account Client Candidate V1`
- GitHub Actions run: `34723424879`
- Workflow source commit: `79bfa54c85a5c200f7e5e9b2fd361bd33c69bbbd`
- Input candidate: `THF_NEXUS_6_ACCOUNT_DELETE_ENDPOINT_CANDIDATE_V2_34721464414.zip`
- Input SHA-256 before and after: `2b027ea4bfdbdbf29f3b3cb72201912b798aaf7c078415b738e9379c3515edd8`
- Output candidate: `THF_NEXUS_6_ACCOUNT_CLIENT_CANDIDATE_V1_34723424879.zip`
- Output SHA-256: `8b0b892d1f32bdc7d5daa9867a442a349f6306969f29e9771dab2af3a9178784`
- Access path: GitHub OIDC/WIF -> GCP -> IAP/OS Login. No persistent cloud key used.

## Passed checks

- `ACCOUNT_DELETION_STATIC_RESOURCE=PASS`
- `ACCOUNT_DELETION_NOT_SPA_FALLBACK=PASS`
- `ACCOUNT_DELETE_HTTP_E2E=PASS`
- `OLD_SESSION_REVOKED=PASS`
- `CLIENT_STATIC_CONTRACT=PASS`
- `THF_CANDIDATE_WAVE_ISOLATION=PASS`

Disposable E2E sequence:

1. `/` returned HTTP 200.
2. `/account-deletion` returned HTTP 200 and content distinct from the SPA root.
3. Disposable user registration returned HTTP 201.
4. Authenticated `DELETE /api/account` returned HTTP 200 with `deleted=true`.
5. Reuse of the deleted account's old bearer session against `/api/profile` returned HTTP 403.

## Safety / mutation evidence

- `PRODUCTION_RUNTIME_MUTATION=FALSE`
- `PRODUCTION_DB_MUTATION=FALSE`
- `CANONICAL_ARCHIVE_OVERWRITE=FALSE`
- `PRODUCTION_SIGNING_PERFORMED=FALSE`
- `PLAY_UPLOAD_PERFORMED=FALSE`
- `CLOUDFLARE_PRODUCTION_CUTOVER_PERFORMED=FALSE`
- `SOLANA_FINANCIAL_ACTION_PERFORMED=FALSE`
- `WAVE_UNTOUCHED=TRUE`

## Release interpretation

The technical self-service account-deletion implementation is now a validated reversible candidate. It is not a production release approval. Retention wording and the final public account-deletion information copy still require policy/legal/owner review before release.

## Next highest-priority unblocked work

Prepare and test distinct static routing/resources for Privacy, Terms, and `/.well-known/security.txt` on an isolated candidate while explicitly marking policy/legal text as non-production draft pending approval. Do not modify the canonical archive or production runtime.
