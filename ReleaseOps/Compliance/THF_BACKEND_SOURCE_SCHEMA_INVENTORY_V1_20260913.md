# THF Backend Source + Schema Inventory V1

Status: **PASS / READ-ONLY**

## Evidence
- GitHub Actions run: `34717869392`
- Workflow commit: `cc5f30654f49be913aecfc72cf15b6b5a1a73fb9`
- Path inspected through GitHub OIDC/WIF -> GCP -> IAP: `~/thf-runtime-s1/runtime/THF_NEXUS_6_FINAL`
- Runtime source-set SHA-256 (`src` + `clients`, WAVE excluded): `7103363f195c29abe69e0d2284ab1ccc9f129235bacdc5946acbdd32043eaec7`
- Runtime database observed SHA-256: `56008a1256ed81a8e9d39d07fc232cdf10a8d48e192cbd192097306ae3333c38`
- `src/thf/__init__.py`: release `6.0.0`
- `src/thf/app.py`: server `THFNexus/6.0`, `/health` release `6.0.0`
- `pyproject.toml` still reports `5.0.0`; treat this as packaging metadata drift to correct in a versioned candidate, not proof of runtime mismatch.

## Account-deletion findings
The database enforces `PRAGMA foreign_keys=ON`. `sessions.user_id` and `profiles.user_id` use `ON DELETE CASCADE`, but many other user-linked tables use the SQLite default `NO ACTION`; some analytics/event tables use nullable `user_id`, and `domain_events.user_id` explicitly uses `ON DELETE SET NULL`.

Therefore a direct `DELETE FROM users WHERE id=?` is **not** a safe implementation for the current schema. The candidate must execute an authenticated transaction that:
1. derives the target user only from the validated session;
2. deletes mandatory user-owned rows that block the user delete;
3. nulls retained nullable attribution rows where retention is justified;
4. deletes the user row and invalidates all sessions;
5. verifies `PRAGMA foreign_key_check` and absence of the deleted identity;
6. separately handles user-owned media/avatar files before the feature can be release-ready.

## Isolation / safety
- THF/WAVE runtime isolation: PASS.
- WAVE_MAWJA: untouched.
- Canonical source mutation: FALSE.
- Production database mutation: FALSE.
- Destructive production test: FALSE.
- Production signing / Play upload / Cloudflare cutover / Solana financial action: FALSE.

## Next
Validate a metadata-driven deletion transaction against a **disposable copy/test DB only**, then implement the authenticated endpoint in a versioned THF source candidate if the transaction gate passes.