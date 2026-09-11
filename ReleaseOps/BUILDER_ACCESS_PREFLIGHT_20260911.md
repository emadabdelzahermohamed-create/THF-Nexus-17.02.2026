# THF Builder Access Preflight — 2026-09-11

## Live GitHub Actions evidence

- Builder: `thf-wave-builder`
- Zone: `europe-west1-b`
- VM state: **RUNNING**
- Network: `default`
- Public/external IP: **none**
- OS Login: **TRUE**
- IAP SSH firewall candidate: `allow-iap-ssh` — **APPLIES**
- Additional broad SSH rule observed: `default-allow-ssh` — applies to the VM; no change performed in this gate.
- VM-attached service account: `1035420130588-compute@developer.gserviceaccount.com`
- Read-only preflight: **PASS**
- WAVE: **untouched**

## Minimum IAM required for the next SSH/IAP smoke test

Automation principal:
`thf-release-builder@project-b5e10d7e-8ce8-4aa4-a15.iam.gserviceaccount.com`

Grant:
1. `roles/compute.osLogin` on the project (non-admin OS Login).
2. `roles/iap.tunnelResourceAccessor` on the project for IAP TCP forwarding.
3. `roles/iam.serviceAccountUser` on the VM-attached service account only.

Prepared operator script: `ReleaseOps/02_grant_iap_oslogin.sh`.

No `roles/compute.instanceAdmin.v1` is added in this least-privilege lane because VM lifecycle or metadata mutation is not required for the next OS Login/IAP smoke test.
