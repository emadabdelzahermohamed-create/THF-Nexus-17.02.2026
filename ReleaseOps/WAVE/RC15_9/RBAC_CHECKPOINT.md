# WAVE RC15.9 — Admin/RBAC checkpoint

Scope: WAVE_MAWJA only. Base: RC15.8 commit `086b430046ca1447b4722c88ff43a6b7217f4623`.

## Implemented
- Authenticated identity now reads `user_accounts.role` on password verification and session lookup.
- Roles are normalized to `viewer | publisher | admin`; unknown values fail closed to `viewer`.
- Public registration remains hard-coded to `viewer`, preventing privilege self-assignment.
- Added `hasWaveRole()` for route-level authorization guards.

## Security invariant
A session token does not embed privilege. Role is resolved from D1 on each authenticated lookup, so demotion/role changes take effect without waiting for session expiry.

## Remaining gate
Do not deploy this checkpoint by itself. Next step is to wire admin API/page guards, add negative/positive RBAC tests, then deploy WAVE and perform live smoke tests.
