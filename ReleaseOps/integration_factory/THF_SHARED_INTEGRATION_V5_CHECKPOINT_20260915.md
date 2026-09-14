# THF Shared Integration V5 checkpoint — 2026-09-15

## Baseline and scope
- Baseline: Shared Integration V4 runtime/contracts on `main`.
- V5 head at checkpoint creation: `0dc8395c2f1444553c5297b938c15a757757c3a5`.
- Scope only shared THF integration contracts/runtime. WAVE untouched.
- Package IDs remain unchanged; no production signing, store publishing, token/treasury mutation or irreversible action performed.

## V5 completed engineering
### Identity provider linking
- New provider links require an already-authenticated THF subject.
- New provider credentials must be server-verified before linking.
- Email equality is explicitly not linking authority.
- If a provider identity is already owned by another THF subject, linking fails closed into manual recovery; no silent account merge.
- Server-atomic link and audit event are required.

### Guest-to-account upgrade
- Guest progress can migrate only after server-side ownership verification.
- Migration is atomic and revokes the guest session after success.
- Client-side economy-balance merging and ranked-state merging are forbidden.
- Progress-reference count is bounded.

### Health provider negotiation
- Health Connect remains Android primary.
- Samsung Health Data SDK remains an optional adapter.
- Missing Samsung provider is nonfatal and does not block THF Fitness.
- Installed-but-unauthorized providers surface a permission requirement.
- Missing providers never fall back to manual health claims as trusted evidence.

### Health normalization and deduplication
- Every normalized health record requires provider, metric, source app identity and source-record identity.
- Deduplication key is deterministic and bound to provider + metric + source + record identity + time range + value fingerprint.
- Raw health payload logging is forbidden by contract.
- Normalized health records have no client reward authority.

### Shared accessibility/localization preferences
- Shared preference contract covers 20 language bases.
- RTL is derived for Arabic, Persian and Urdu and conflicting client RTL overrides fail closed.
- Data Saver, Reduce Motion and High Contrast can synchronize cross-app while product-specific visuals stay local.

### Operator recovery
- Recovery email must already be verified.
- Admin/Publisher operator recovery cannot rely on a single email channel alone.
- Server rate limiting and recovery audit events remain required.

## Validation added
- `ReleaseOps/integration_factory/test_shared_integration_runtime_v5.py`
- `.github/workflows/thf-shared-integration-v5.yml`
- V5 CI compiles V3/V4/V5 shared integration sources, runs cumulative V3/V4/V5 unit tests and validates fail-closed manifest truth.

## Truth boundary
The following remain external/runtime gates and are intentionally FALSE until evidenced:
- Google OAuth production console configured.
- Durable identity-link store bound.
- Durable guest migration store bound.
- Health Connect provider runtime bound and verified on a physical device.
- Samsung partner registration verified.
- Physical-device pass.
- FINAL/PLAY_READY.

V5 is a shared-integration engineering checkpoint, not a production or phone acceptance claim.
