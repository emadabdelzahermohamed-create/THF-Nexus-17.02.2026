# THF GCP Production Inventory — 2026-09-12

Status: PASS-WITH-SECURITY-FINDING
Run: `34702891468`
Workflow fix commit: `9c885932751a5aa718b23bcb245c83be16a1dacb`
Mode: read-only via GitHub OIDC/WIF + IAP/OS Login

## Verified

- GCP project resolved correctly.
- VM `thf-wave-builder` is RUNNING in `europe-west1-b`, machine type `e2-standard-4`, internal IP only in instance inventory.
- Boot/data disk inventory shows a 200 GB `pd-balanced` disk in READY state.
- Runtime root `/home/sa_115575029018678177962/thf-runtime-s1/runtime/THF_NEXUS_6_FINAL` exists.
- Local runtime health: PASS.
- Runtime release: `6.0.0`.
- No forwarding rules were listed.
- One NAT auto address was listed; it is not treated as a fixed application endpoint.
- Cloud Run inventory was not available to this least-privilege service account (`run.services.list` denied). No permission escalation was attempted.

## Security finding

Current firewall inventory includes:

- `allow-iap-ssh`: TCP/22 from `35.235.240.0/20`.
- `default-allow-ssh`: TCP/22 from `0.0.0.0/0`.
- `default-allow-rdp`: TCP/3389 from `0.0.0.0/0`.
- `default-allow-icmp`: ICMP from `0.0.0.0/0`.
- `default-allow-internal`: internal network traffic.

`default-allow-ssh` and `default-allow-rdp` are broader than required for the established IAP path. They are recorded as a production-hardening blocker. They were NOT changed because firewall mutation is a consequential cloud change and no exact authorization for that class of action has been established.

## Safety

- `MUTATION_PERFORMED=FALSE`
- `PRODUCTION_CUTOVER_PERFORMED=FALSE`
- `WAVE_FILES_TOUCHED=FALSE`
- No persistent cloud key used.
- No production signing, Play upload, Cloudflare production cutover, Solana transaction, or destructive cloud action performed.

## Next

1. Keep IAP/WIF as the access path.
2. Obtain explicit authorization before firewall hardening; then remove/restrict public SSH/RDP only after verifying IAP access and preserving rollback.
3. Continue independent THF compliance/build/package gates while Cloudflare production hostname and signing remain authorization-blocked.
4. WAVE remains isolated and blocked on its missing full canonical runtime/source on the builder.
