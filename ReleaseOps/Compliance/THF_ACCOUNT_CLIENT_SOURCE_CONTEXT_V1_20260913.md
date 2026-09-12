# THF Account Client Source Context V1

Status: **PASS / IMPLEMENTATION CONTEXT VERIFIED**

## Evidence
- GitHub Actions run: `34721877851`
- Workflow commit: `4150e748baeeeedf3ec226afa07f6477546114eb`
- Parent candidate: `THF_NEXUS_6_ACCOUNT_DELETE_ENDPOINT_CANDIDATE_V2_34721464414.zip`
- Parent candidate SHA-256: `2b027ea4bfdbdbf29f3b3cb72201912b798aaf7c078415b738e9379c3515edd8`
- GitHub OIDC/WIF -> GCP -> IAP: PASS
- THF/WAVE isolation: PASS

## Verified client structure
- Main account header currently exposes sign-in/services only; no account-management/deletion control.
- `#auth` currently contains registration and login forms only.
- The web client uses a single in-memory `state.token` and generic authenticated `api()` helper.
- No user-facing logout/delete handler exists in `clients/web/app.js`.

## Verified backend candidate structure
- HTTP DELETE is wired through `do_DELETE()`.
- Authenticated `DELETE /api/account` resolves the user from the bearer session and invokes the tested account-deletion routine.
- The deletion routine handles user-linked foreign keys by schema action, explicit delete, or anonymization as appropriate, verifies `PRAGMA foreign_key_check`, and restores staged owned files on failure.

## Implementation decision
The next reversible candidate may add the account-management UI without changing authentication architecture:
1. add a static account view and deletion control;
2. require authenticated state and an explicit destructive confirmation in the client;
3. call only `DELETE /api/account` with the current bearer session;
4. clear local in-memory account state only after the backend returns a confirmed deletion result;
5. expose an independent `/account-deletion` instructions page instead of SPA fallback.

Privacy, Terms, and `/.well-known/security.txt` remain separate compliance blockers and must not be fabricated as legal-final content.

## Safety
- Canonical source mutation: FALSE
- Production runtime/DB mutation: FALSE
- Production signing: FALSE
- Google Play upload: FALSE
- Cloudflare production cutover: FALSE
- Solana/token financial action: FALSE
- WAVE_MAWJA mutation: FALSE
