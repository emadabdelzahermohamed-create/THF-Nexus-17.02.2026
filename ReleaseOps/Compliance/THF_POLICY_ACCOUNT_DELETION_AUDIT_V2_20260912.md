# THF Policy + Account Deletion Audit V2 — 2026-09-12

Status: AUDIT-PASS / RELEASE-COMPLIANCE-BLOCKED
Scope: THF runtime only. WAVE_MAWJA excluded and untouched.

## Evidence

- GitHub Actions run: `34715148011` — SUCCESS
- Workflow commit: `779db165a2725a67dc206b2cab1a75d80b8a1f9d`
- Access path: GitHub OIDC/WIF -> GCP -> IAP/OS Login
- Persistent cloud key: NOT USED
- Runtime source-set SHA-256: `7103363f195c29abe69e0d2284ab1ccc9f129235bacdc5946acbdd32043eaec7`
- Live runtime endpoint inspected: `http://127.0.0.1:18080`
- Root SPA SHA-256: `8f2f118bf6890dc50babff369116523cb00fd6b1f1e343bb6d0cd43773c7b7ca`

## Live route findings

| Route | HTTP | Content-Type | Bytes | SHA-256 | Finding |
|---|---:|---|---:|---|---|
| `/health` | 200 | `application/json; charset=utf-8` | 212 | `a34c2c7eee18fdf6aaaa697e16e45be714939cf6159d6f9c59c4c6f0f9a74c00` | Distinct health response |
| `/privacy` | 200 | `text/html` | 15702 | `8f2f118bf6890dc50babff369116523cb00fd6b1f1e343bb6d0cd43773c7b7ca` | FAIL: SPA fallback, identical to root |
| `/terms` | 200 | `text/html` | 15702 | `8f2f118bf6890dc50babff369116523cb00fd6b1f1e343bb6d0cd43773c7b7ca` | FAIL: SPA fallback, identical to root |
| `/account-deletion` | 200 | `text/html` | 15702 | `8f2f118bf6890dc50babff369116523cb00fd6b1f1e343bb6d0cd43773c7b7ca` | FAIL: SPA fallback, identical to root |
| `/.well-known/security.txt` | 200 | `text/html` | 15702 | `8f2f118bf6890dc50babff369116523cb00fd6b1f1e343bb6d0cd43773c7b7ca` | FAIL: SPA fallback, wrong resource/content type |

## Source findings

- No independent file matching Privacy, Terms, account deletion, or `security.txt` was found in the inspected THF runtime source tree.
- No source route/reference for `/privacy`, `/terms`, account deletion, or `security.txt` was found by the audit patterns.
- Deletion-related implementation found at source level consists of session deletion and database foreign-key cleanup semantics (`ON DELETE CASCADE` / `ON DELETE SET NULL`).
- No authenticated end-user self-service account deletion endpoint/workflow was identified by this audit.

## Release interpretation

The HTTP 200 responses for the four compliance paths MUST NOT be treated as compliance PASS. They are routing fallback responses, not distinct policy/security/deletion resources.

### Blocking items before Play release-readiness can pass

1. Provide a reviewed Privacy Policy as a distinct public HTTPS resource and expose it in-app.
2. Provide reviewed Terms as a distinct resource where required by the product/legal policy.
3. Implement and verify an authenticated self-service account deletion flow, including deletion/retention semantics for user-linked data.
4. Provide a public account-deletion information URL suitable for Play Console requirements.
5. Add a real `/.well-known/security.txt` resource with an approved security-contact/expiry policy if retained as a release requirement.
6. Rerun this audit and require distinct content/hashes instead of SPA fallback.

Legal/business text and retention commitments were not invented by automation. Owner/legal approval remains required for the actual policy wording and retention commitments.

## Safety / isolation

- `THF_RUNTIME_WAVE_ISOLATION=PASS`
- `MUTATION_PERFORMED=FALSE`
- `PRODUCTION_SIGNING_PERFORMED=FALSE`
- `PLAY_UPLOAD_PERFORMED=FALSE`
- `CLOUDFLARE_PRODUCTION_CUTOVER_PERFORMED=FALSE`
- `SOLANA_FINANCIAL_ACTION_PERFORMED=FALSE`
- `WAVE_UNTOUCHED=TRUE`

## Next highest-priority unblocked work

Prepare a reversible technical contract/patch plan for account deletion and distinct policy routing without modifying canonical archives or production runtime; continue independent Play/store readiness work while legal text, production hostname, signing, and publishing authorizations remain blocked.
