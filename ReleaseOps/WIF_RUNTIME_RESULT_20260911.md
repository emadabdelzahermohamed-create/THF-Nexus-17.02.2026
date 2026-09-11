# THF GitHub → GCP WIF runtime result — 2026-09-11

## Result

- GitHub Actions OIDC issuance: **PASS**
- Workload Identity Federation authentication: **PASS**
- Service-account access token: **PASS**
- Authenticated service account: `thf-release-builder@project-b5e10d7e-8ce8-4aa4-a15.iam.gserviceaccount.com`
- `roles/compute.viewer` grant: **PASS (operator applied)**
- Compute builder metadata read: **PASS**
- Builder: `thf-wave-builder`
- Zone: `europe-west1-b`
- Builder state observed by GitHub Actions: **RUNNING**
- Workflow gate: **SUCCESS**

## Interpretation

The GitHub ↔ GCP federation path is operational end-to-end. GitHub Actions can mint a short-lived federated service-account token and read the prepared private builder without a persistent service-account key.

The previous `compute.instances.get` IAM blocker is closed.

## Next gate

Perform a read-only builder-access preflight for IAP/OS Login and network posture. Only after that passes should the automation lane receive the minimum SSH/IAP permissions needed to stage exact RC16 artifacts and execute the existing unsigned/test RC9/RC10 build chain.

## Safety boundary

No deployment, VM mutation, production signing, Google Play action, Cloudflare cutover, Solana action, or WAVE mutation was performed during this verification.
