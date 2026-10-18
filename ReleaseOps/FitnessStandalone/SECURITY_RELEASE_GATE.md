# THF Fitness / Pulse — Security & Dependency Release Gate

Date: 2026-09-18
Scope: Fitness standalone only. WAVE-MAWJA is explicitly excluded.
Canonical avatar: MPFB/MakeHuman Stage16A, 137 joints / 195 clips; legacy humanoids are prohibited.

## Purpose
This gate converts P8 security/release closure into reproducible, fail-closed checks that can run independently of the currently blocked production-hosting/signing work.

## Required checks
1. Python dependency audit: install the exact Fitness requirements and run `pip-audit`; any known vulnerable runtime dependency fails the gate unless an explicit reviewed exception is committed with CVE, rationale and expiry.
2. Android dependency inventory: run Gradle dependency resolution for release runtime and archive the report. Dynamic `+` versions and unpinned local binary substitutions are release blockers.
3. Secret scan: scan the checked-out Fitness release authority and ReleaseOps/FitnessStandalone only. Private keys, keystores, OAuth client secrets, service-account JSON, bearer tokens and committed production passwords fail the gate. Non-secret identifiers such as application IDs, OAuth client IDs, WIF provider resource names and service-account email addresses are allowed.
4. Android release security: release artifact must be non-debuggable, contain no debug applicationId suffix, use HTTPS production authorities, and must not enable cleartext traffic or permissive user-installed CA trust for production unless explicitly justified and tested.
5. Auth/RBAC: anonymous callers must not access another user's profile/workout/sync data; session revocation and account deletion must invalidate privileged access. Ranked/economy-sensitive writes remain server-authoritative.
6. Web security headers: production Web must be re-verified after deployment for HTTPS redirect/HSTS (where controlled), content-type protection, framing policy/CSP frame-ancestors, referrer policy and an explicit CSP appropriate to the actual app.
7. Play Integrity: reward/ranked trusted paths remain blocked from release closure until server-side Play Integrity token exchange and verdict handling are implemented and regression-tested. Client-only integrity checks do not satisfy this gate.

## Evidence to retain
- `pip-audit` output and resolved Python package versions.
- Gradle release dependency report.
- Secret-scan report with redaction (never archive discovered secret values).
- Merged/release manifest security attributes and network-security configuration evidence.
- Auth/RBAC automated test output.
- Post-deploy HTTPS/header probe output.
- Play Integrity backend test evidence.

## Current state
PARTIAL. Initial secret-like assignment scan and production user-scope/auth regression are already recorded PASS in the master backlog. Dependency audit, Android network-security audit and Play Integrity backend exchange remain open. This document is a gate definition, not evidence that those checks have passed.
