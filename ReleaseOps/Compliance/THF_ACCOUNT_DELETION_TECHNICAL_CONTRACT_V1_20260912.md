# THF Account Deletion Technical Contract V1 — 2026-09-12

Status: READY-FOR-IMPLEMENTATION-IN-VERSIONED-SOURCE
Scope: THF only. WAVE_MAWJA excluded.
Source evidence: `THF_POLICY_ACCOUNT_DELETION_AUDIT_V2_20260912.md`

## Objective

Add an end-user self-service account deletion capability and distinct public deletion-information route without changing any canonical source archive or production runtime directly. Implementation must occur first in a versioned release-source candidate and pass destructive-operation tests against disposable test data only.

## Required API contract

### Authenticated request

`DELETE /api/account`

Requirements:
- Requires a valid authenticated user session.
- Must reject missing/invalid credentials with `401`/`403`.
- Must never accept an arbitrary target `user_id` from the client.
- The target identity must be derived from the authenticated session.
- Must be idempotent from the user's perspective: repeated requests after successful deletion must not recreate data or expose prior account state.
- Must invalidate all active sessions as part of deletion.

### Recommended confirmation model

Use an explicit re-authentication or short-lived deletion confirmation challenge before destructive deletion. Do not rely on a UI-only confirmation dialog as the security boundary.

### Success response

Use a minimal response such as HTTP `204`, or a non-sensitive JSON confirmation. Do not return deleted personal data.

## Data-deletion semantics

Before implementation, enumerate every table/object keyed directly or indirectly to the authenticated user. Classify each as one of:

- DELETE: user-owned data removed immediately.
- ANONYMIZE: data retained only after irreversible removal of user linkage where legitimate retention applies.
- RETAIN: only where a documented legal/security/accounting obligation requires retention, with a defined retention period.

Current audit evidence already shows database foreign keys using `ON DELETE CASCADE` and `ON DELETE SET NULL`, but those constraints alone are not sufficient proof of complete account deletion. The final gate must verify actual post-delete state across every user-linked table and external provider activated in the final production configuration.

## Minimum deletion coverage

The implementation/test inventory must explicitly cover, where present in the final schema/configuration:

- user/account identity and profile
- sessions/authentication records
- fitness/workout/activity records
- readiness/health-related inputs
- uploaded avatar/media references and owned media
- chat/messages and social interactions subject to the approved retention policy
- ad/view interaction records subject to the approved retention/anonymization policy
- wallet/economy references without performing any blockchain transaction
- audit/security events according to the approved retention policy
- external provider objects only when a provider is actually enabled in production

## Public information route

`GET /account-deletion`

Must return a distinct, non-SPA-fallback HTTPS page explaining:
- how a user initiates deletion in the app;
- what categories are deleted;
- what categories, if any, are retained and for how long;
- how to contact support for deletion issues.

Actual legal/retention wording requires owner/legal approval and is intentionally not invented in this contract.

## Policy routes

The following must be explicit resources and must not resolve to the generic SPA root:

- `GET /privacy`
- `GET /terms` where retained as a release requirement
- `GET /account-deletion`
- `GET /.well-known/security.txt` where retained as a release requirement

## Verification gates

1. Source/parser tests pass.
2. Existing native/API-36 build gates remain green.
3. Unauthenticated `DELETE /api/account` fails closed.
4. Authenticated deletion is tested only with disposable test identity/data.
5. All sessions for the deleted test identity become invalid.
6. Post-delete database queries confirm required DELETE/ANONYMIZE outcomes.
7. `/privacy`, `/terms`, `/account-deletion`, and `security.txt` are distinct from SPA root by content and SHA-256.
8. THF/WAVE isolation remains PASS.
9. Canonical archive SHA-256 is identical before and after candidate construction/tests.
10. No production signing, Play upload, Cloudflare production cutover, Solana transaction, or destructive cloud mutation occurs during this gate.

## Rollback

The change must be carried only in a versioned release-source candidate/commit. Production runtime remains unchanged until the candidate passes all tests and receives the required deployment authorization. Rollback is therefore the removal/reversion of the candidate commit; canonical source archives remain untouched.

## Current blockers outside engineering

- Approved Privacy/Terms wording and retention commitments.
- Public production hostname/cutover authorization.
- Production signing authorization and Play App Signing/user-only steps.
- Explicit Play upload/publishing authorization.

## Next engineering step

Locate the exact canonical/versioned THF backend source used for the current `6.0.0` runtime and create a reversible candidate patch implementing this contract. Before any destructive test, create disposable test fixtures and verify the complete user-linked schema inventory.
