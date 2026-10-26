# Top Hero Fit Fitness V2 backend core

This directory contains the authenticated workout-history, progress and competition
verification boundary used by Web and Android.

The WSGI entry point is `api.create_app_from_environment`. It deliberately has no
development credential fallback. Deployment must provide:

- `THF_WORKOUT_DB`: durable SQLite path for this recovery implementation;
- `THF_AUTH_ISSUER` and `THF_AUTH_AUDIENCE`: exact shared-account token scope;
- `THF_AUTH_KEYS_JSON`: rotated `{kid: base64url-secret}` verification key ring.

Ingress must terminate TLS and forward `wsgi.url_scheme=https`. The API rejects
non-HTTPS requests, missing/expired/revoked sessions, client-supplied account identity,
ambiguous stable record versions and idempotency-key reuse with a different body.

Run the contract suite with:

```sh
python -m unittest discover -s fitness-v2/backend/tests -v
python fitness-v2/tests/test_source_contract.py
```

This source checkpoint is not a deployment claim. A production database migration,
issuer/key configuration, HTTPS deployment and live authenticated probes remain separate
release gates.
