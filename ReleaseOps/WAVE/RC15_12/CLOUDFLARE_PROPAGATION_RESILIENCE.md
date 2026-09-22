# WAVE RC15.12 — Cloudflare propagation resilience

Recorded UTC: 2026-09-22T13:41:04Z

## Incident evidence

- Canonical commit: `b85da47d0e1afe74e9a832a4535aaa4785ceac6b`.
- Workflow run `35683881549` built and deployed successfully.
- Cloudflare reported version `8b71a48b-edde-4670-9162-305ddb2c9a85` at `https://wave-mawja.p-my.workers.dev`.
- The immediate live smoke passed `/admin`, then failed on `/publisher` without a diagnostic line.
- A later independent public-browser check reached the same guarded login URL from both aliases and displayed the Arabic WAVE Control login UI.

This is consistent with a short post-deploy propagation window. It is not evidence that the publisher route or its authorization boundary is missing.

## Change

- Preserve the exact `307|308 -> /control -> /admin-login?return_to=%2Fcontrol` contract.
- Retry only the two new aliases for at most 12 attempts, five seconds apart.
- Keep a hard failure (`exit 33`) when the exact redirect chain and guarded login UI do not converge.
- Emit the observed status, redirect target, and final URL on every retry so a future failure is diagnosable.
- Add deterministic tests for both transient recovery and persistent fail-closed behavior.

## Isolation and truth boundary

Only WAVE_MAWJA's Cloudflare smoke gate is changed. No Media, Arena Social, OnePublish, THF, Fitness, games, Android package, signing, OAuth, database, secret, or Play listing is changed. This checkpoint is not FINAL and does not claim a phone, Android, or Play pass.

## Local gates

- Transient-recovery and persistent-failure unit tests: 2/2 PASS.
- Shell parser: PASS.
- Workflow YAML and state JSON parsers: PASS.
- Git whitespace/error check: PASS.
- High-confidence secret signature scan: PASS with no match.
- SHA-256 workflow: `d6cf9d6520d5167a49ebc6ad85b5f21c37097f971a0f84472831fd06860590b4`.
- SHA-256 smoke script: `395ff6c2f07dfe1c17e06876588377dd816bc4bedcd4b4997be0bf81f8d92c33`.
- SHA-256 unit test: `710e74be63f8740c872aff56aedcbca370914715f677e05b4810efbf01e6e8f3`.
