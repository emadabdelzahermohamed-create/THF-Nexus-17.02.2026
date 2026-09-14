# THF Shared Integration V2 — checkpoint — 2026-09-14

## Scope completed
This batch advances the reusable THF integration layer without touching WAVE or performing production/store/financial mutations.

### Identity/session
- Added explicit shared session states: anonymous, guest, authenticated, reauth_required and revoked.
- Added shared auth-method registry for Google, passkey, password, email-code and guest.
- Operator roles are fail-closed unless the session is authenticated.
- Authenticated sessions require a concrete identity subject.
- Shared contract marks refresh-token persistence as secure-storage-only and logout as server-session revocation.

### Passkeys
- Added RP-ID validation, user-ID requirement and minimum challenge-length policy.
- Passkey registration contract requires a server-grade challenge and validates attestation mode.
- Production server challenge-store/replay binding remains intentionally unclaimed.

### Cross-app handoff
- Added one reusable THF cross-app handoff contract.
- Handoff is limited to known THF products, different source/target, explicit subject and nonce.
- Lifetime is fail-closed to <=300 seconds.
- Server signature and single-use semantics are mandatory.
- Roles and secrets are explicitly never carried inside handoff payloads.
- Production server signer/replay-store binding remains unclaimed.

### Health / motion evidence
- Health Connect remains primary Android semantic health bridge; Samsung Health Data SDK remains optional provider adapter.
- Existing provider provenance/deduplication and consent-first permissions are preserved.
- Added normalized motion-evidence contract for camera pose, wearable sensor, device sensor or combined evidence.
- Repetition count, monotonic clock and confidence are validated.
- Client motion evidence is never reward authority; backend verification remains mandatory.

### Shared preferences
- Added reusable locale/Data Saver/Reduce Motion/High Contrast preference contract.
- Arabic, Persian, Hebrew and Urdu resolve to RTL; other supported language tags resolve to LTR.
- This contract is suitable for synchronized cross-app preference handoff while preserving product-local UI behavior.

## Exact files updated
- `ReleaseOps/integration_factory/shared_integration_contracts.py`
- `ReleaseOps/integration_factory/test_shared_integration_contracts.py`
- `ReleaseOps/integration_factory/ANDROID_SHARED_INTEGRATION_V1.json` (schema promoted to `thf.android.shared.integration.v2`; legacy filename preserved for compatibility)
- `.github/workflows/thf-shared-integration-v1.yml` (workflow display/gates promoted to V2; legacy filename preserved for compatibility)

## Validation
- Python compile PASS on the V2 contracts/tests.
- Shared regression suite PASS after V2 additions.
- Machine-readable Android V2 manifest gate PASS on the preceding exact V2 manifest commit.
- A stricter V2 workflow was added to gate passkey/session/handoff/motion truth boundaries on subsequent commits.

## Release truth
Still FALSE / externally unproven:
- Google OAuth production console/consent/client activation.
- Production backend Google signature-verifier binding.
- Passkey production challenge/replay store binding.
- Cross-app handoff production server signer/replay binding.
- Samsung Health production partner registration/access.
- Physical Health Connect/Samsung integration validation.
- Physical phone acceptance.
- FINAL / PLAY_READY.

Next work should bind these contracts into concrete Android/backend clients, starting with THF Fitness and THF Hub, while reusing rather than duplicating policy logic.