# THF Fitness / Pulse — Production Hosting Gate

Date: 2026-09-18
Branch: `release/fitness-standalone-v1-20260918`
Scope: THF Fitness / Pulse standalone only. WAVE-MAWJA is explicitly excluded.

## Required invariant
Android and Web MUST use the same stable HTTPS backend, account identity, and synchronized durable data. Temporary tunnels and unrelated project hosts are not acceptable production authority.

## Verified infrastructure state
- P0 CI/build is PASS; production build evidence reports `base_url_configured=no` and `pass_url_configured=no`.
- Connected DigitalOcean account has zero droplets as of 2026-09-18; there is no existing Fitness host there that can be reused without provisioning billable infrastructure.
- Repository search did not reveal a committed authoritative value for `THF_FITNESS_BASE_URL` or an existing Fitness Cloud Run deployment contract.
- No unrelated THF service and no WAVE-MAWJA deployment may be repurposed by assumption.

## Fail-closed deployment contract
Before P2/P7 may be marked PASS, evidence MUST record all of:
1. Stable HTTPS Fitness origin URL.
2. Stable HTTPS THF Pass/identity URL (may be the same origin if served by the same backend).
3. Durable production data store and migration/rollback plan.
4. Android `THF_FITNESS_BASE_URL` exactly matches the Web/PWA API authority.
5. Android `THF_PASS_URL` matches the Web identity authority.
6. OAuth redirect URIs are bound to the production origin, with provider secrets external to source control.
7. Live smoke test covers registration/login, workout/progress write, second-client read/sync, logout/session revocation, and account deletion.
8. Ranked/economy-sensitive writes remain server-authoritative; offline queue reconciliation cannot mint trusted outcomes locally.
9. Post-deploy rollback checkpoint and live re-verification are recorded.

## Current blocker
A stable production host/domain and corresponding deploy authorization are not presently available through the connected infrastructure. Creating a new paid host is intentionally not performed without owner authorization. This blocks production OAuth, Web publication, cross-device production sync verification, production-bound Android rebuild, and downstream Play Internal publication.

## Independent work allowed while blocked
Security/dependency audit, Android release hardening, policy/declaration preparation, avatar/mobile optimization review, offline/server-authority tests, and release documentation may proceed as long as they do not claim production-host PASS.
