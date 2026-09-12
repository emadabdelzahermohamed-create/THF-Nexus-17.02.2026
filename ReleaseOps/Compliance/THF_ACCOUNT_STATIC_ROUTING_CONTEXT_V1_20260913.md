# THF Account Static Routing Context V1 — 2026-09-13

Status: PASS-CONTEXT
Scope: THF only. WAVE_MAWJA untouched.

## Verified execution

- GitHub Actions run: `34721961549` — SUCCESS.
- Access path: GitHub OIDC/WIF → GCP → IAP → `thf-wave-builder`.
- Input candidate: `THF_NEXUS_6_ACCOUNT_DELETE_ENDPOINT_CANDIDATE_V2_34721464414.zip`.
- Verified input SHA-256: `2b027ea4bfdbdbf29f3b3cb72201912b798aaf7c078415b738e9379c3515edd8`.
- Canonical source/archive was not mutated.

## Finding

The THF HTTP dispatcher sends non-API paths to `_static(path)`. Current `_static` behavior resolves requested files under `clients/web`, but if the requested file does not exist it falls back to `clients/web/index.html` and returns HTTP 200. Therefore `/account-deletion` cannot satisfy the public account-deletion information requirement until it is explicitly mapped to a real standalone resource or an equivalent distinct static file exists.

Relevant current behavior:

- `/api/*` and `/health` route to API handling.
- media/avatar files use explicit file handlers.
- other routes use `_static(path)`.
- `_static` falls back to `index.html` when the target is absent.

## Safe implementation decision

Build an isolated versioned candidate that:

1. Preserves the verified backend `DELETE /api/account` implementation.
2. Adds an authenticated Account UI with an explicit destructive confirmation phrase.
3. Calls `DELETE /api/account` using only the current authenticated session.
4. Clears client session state only after backend success.
5. Maps `/account-deletion` to a distinct standalone HTML resource rather than SPA fallback.
6. Tests deletion only against a disposable SQLite database and temporary extracted source tree.
7. Does not deploy, sign, publish, cut over Cloudflare, or mutate production runtime/database.

## Isolation / safety evidence

- THF candidate WAVE isolation: PASS.
- Production mutation: FALSE.
- WAVE mutation: FALSE.
- Production signing: FALSE.
- Play upload: FALSE.
- Cloudflare production cutover: FALSE.
- Solana financial action: FALSE.

## Next gate

`THF Account Client Candidate V1` is the next unblocked implementation gate. It must produce a new candidate archive without overwriting the input candidate, verify both input/output SHA-256 values, run parser/static checks, prove `/account-deletion` is not SPA fallback, and repeat authenticated deletion E2E against disposable test data.
