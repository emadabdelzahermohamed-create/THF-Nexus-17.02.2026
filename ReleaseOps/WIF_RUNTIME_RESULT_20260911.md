# THF GitHub → GCP WIF runtime result — 2026-09-11

## Result

- GitHub Actions OIDC issuance: **PASS**
- Workload Identity Federation authentication: **PASS**
- Service-account access token: **PASS**
- Authenticated service account: `thf-release-builder@project-b5e10d7e-8ce8-4aa4-a15.iam.gserviceaccount.com`
- Compute builder metadata read: **BLOCKED — IAM 403**
- Missing permission reported by Compute API: `compute.instances.get`
- Target resource: `projects/project-b5e10d7e-8ce8-4aa4-a15/zones/europe-west1-b/instances/thf-wave-builder`

## Interpretation

The GitHub ↔ GCP federation path is operational end-to-end. The remaining blocker is not WIF, GitHub, repository access, or a persistent credential. It is the GCP IAM policy attached to the federated service account.

## Minimal next change

Grant `roles/compute.viewer` to the release-builder service account at project scope, then rerun `THF GCP WIF Smoke`.

Prepared operator script: `ReleaseOps/01_grant_compute_viewer.sh`.

## Safety boundary

No deployment, VM mutation, production signing, Google Play action, Cloudflare cutover, Solana action, or WAVE mutation was performed during this verification.
