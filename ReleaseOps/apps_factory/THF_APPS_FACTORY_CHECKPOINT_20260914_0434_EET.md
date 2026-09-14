# THF + WAVE Large-Batch Release Checkpoint — 2026-09-14 04:34 EET

Status: NOT_FINAL / PHYSICAL_DEVICE_PENDING / PRODUCTION_CUTOVER_PENDING

## Material change this pass

Notification provider-token mutations are now bound to a live THF Pass session principal in the isolated HTTP contract.

- Source commit: 7cf2406bfcf7467c01e0984660062204ee5208c0
- Regression commit: 43cd0e3cfb408837f16d012c75840bcaeddc69ee
- Workflow: THF Notification HTTP Provider Contract V1
- Run: 34796197771
- Conclusion: SUCCESS
- Run head: 43cd0e3cfb408837f16d012c75840bcaeddc69ee
- No uploaded artifact was produced by this workflow.

The contract now fails closed when the bound Pass session is revoked or expired before register, rotate, revoke, or logout mutations. Package/audience binding, subject scoping, and query-string credential rejection remain enforced. Regression coverage confirms blocked expired/revoked mutations leave the token registry and vault unchanged.

## Release-policy interpretation

This closes an isolated contract/security gap only. It does NOT prove:
- FCM/APNs provider delivery
- notification receipt/tap/background-resume on a physical phone
- production signing or signed AAB
- Play Internal acceptance
- stable production HTTPS/WSS
- production deployment

Exact-candidate physical-device evidence remains mandatory under Mobile Real-Function Release Policy.

## WAVE isolation

No WAVE source, runtime, SSH/OS Login policy, Cloudflare configuration, or canonical workspace was modified in this pass. The previously recorded canonical-source access blocker remains unresolved unless a newer authoritative WAVE gate proves otherwise; older WAVE sources must not substitute for the canonical candidate.

## Safety

No signing keys, OAuth credentials, billing/ownership settings, 2FA, production endpoints, Play submissions, or physical-device/GPU evidence were fabricated or changed.

Body SHA-256 (content above this line): cecb83ef348002e58b1526a02ea4a8b17cd43eb5be1fac872a5d6ab528e1afd3
