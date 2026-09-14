# THF Apps Factory Large-Batch Checkpoint — 2026-09-14 05:05 EET

Status: NOT_FINAL / PHYSICAL_DEVICE_PENDING / PROVIDER_DELIVERY_PENDING / PRODUCTION_CUTOVER_PENDING

## Scope and same-SHA handling

This pass remained inside the THF Apps Factory scope: Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity, and cross-app handoff support. Dedicated native game streams and token-finance implementation were intentionally excluded and not modified.

The exact Android candidates in `THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json` remain unchanged and are still bound to their previously recorded APK/source SHA-256 values. Their already-proven same-SHA package/API36 gates were not rerun merely to manufacture activity. All ten candidates remain `PENDING_PHYSICAL_PHONE`; `final_or_play_ready` remains false.

## Material engineering changes

### Failure-safe notification registration and rotation

The provider-neutral token registry now protects the old working registration when a replacement cannot be safely committed.

- Registration stores the provider secret in the secure-vault boundary first, commits only the fingerprint/metadata to SQLite, and compensates the vault secret on DB failure.
- Rotation requires custody of the replacement token before changing the old registration.
- Old-inactive + new-active state is committed in one DB transaction.
- A DB failure rolls the old registration back to active and removes the uncommitted replacement secret.
- A vault-put failure leaves the old active registration and secret untouched.
- Rotating to the identical provider token is rejected without mutation.
- `SecureTokenVault` now exposes a server-side `get(token_id)` boundary so provider dispatch can retrieve the raw token without storing it in registry rows or client-visible delivery requests.

Relevant commits:
- `fc5fbc66523a07b4139d0248e0bd6661fdb380c0` — failure-safe rotation/registration
- `88e3a27ccf96e6ee362e8c1354799988072ecf38` — atomicity/compensation regressions
- `9c8ccc9618c6d3223049a104bd83cc3dc939fe40` — secure token retrieval boundary
- `ba0a129899d5f6064e009b063fc071b5defa9526` — retrieval-bound test fixture

### Provider contract hardening

The provider-neutral adapter contract now receives provider credentials only as the server-side `provider_token` argument. The public `DeliveryRequest` remains credential-free.

- Notification deeplinks are restricted to `thf://` or HTTPS.
- Sensitive query/fragment keys (`token`, `access_token`, `authorization`, `secret`, `credential`, `provider_token`) are rejected.
- Provider result semantics fail closed: accepted delivery requires a provider message ID; accepted cannot simultaneously be retryable/permanently failed; retryable and permanent failure are mutually exclusive.

Relevant commits:
- `a2c7cf2a6e643f7582e3d0ca0964d68896073b87`
- `7738419705b46bb766558d7c3cea0c1c17e7c918`

### Fail-closed dispatch coordinator

Added `notification_dispatch.py`, a provider-neutral server-side coordinator. It:

- resolves the registration under the authenticated subject scope;
- rejects inactive/cross-subject registrations;
- chooses the adapter from the provider stored in the authoritative registration;
- refuses missing or unconfigured adapters before any send attempt;
- obtains the raw provider token only from `SecureTokenVault`;
- validates provider response semantics;
- revokes a registration and deletes its vault token after a permanent provider-token failure;
- retains the registration on retryable failures;
- does not implement, emulate, or claim FCM/APNs network delivery.

Relevant commits:
- `e4399f165a26799d50875ee710a5d1c207f94f0a` — dispatch coordinator
- `72dfe94fb0e194931a1ae84cb20e56ad15017607` — dispatch regressions

## CI / regression evidence

The notification workflow trigger was corrected so lifecycle-test changes themselves run the gate:
- `4fba92ed617812d3192d4325af1ea6a682a4e124`

The workflow was then extended to compile and test lifecycle + Pass-bound HTTP + provider + dispatch together:
- `33986260623ce2d8eafcb1ba6b4e9db2b506b80c`
- Workflow: `THF Notification HTTP Provider Contract V1`
- Run: `34797845799`
- Conclusion: `SUCCESS`
- CPython: 3.12.14
- Regression result: `33 passed`
- Compile step: PASS
- Device-evidence fail-closed gate: PASS
- `PHYSICAL_DEVICE_PASS=FALSE`
- `PUSH_READY=FALSE`
- `FINAL_OR_PLAY_READY=FALSE`

## Truth boundary / remaining gates

This checkpoint does **not** prove or claim any of the following:

- FCM/APNs credentials, actual provider network delivery, notification receipt, tap, or background-resume on a physical phone;
- production `SecureTokenVault` backed by approved KMS/secret infrastructure;
- stable externally reachable non-public trusted-TLS THF Pass staging for lifecycle/federation runtime-live promotion;
- production signing, signed AAB, Play Internal acceptance, billing/legal/OAuth/2FA owner actions;
- exact-candidate install/launch/touch/layout/orientation/background-resume/offline↔network/core-journey/crash-free/accessibility/Data Saver/RTL/20-language physical-phone evidence.

The precise owner/external inputs still required when those gates are reached are: approved provider/KMS credentials and configuration for real push delivery; a reachable trusted-TLS non-public Pass staging target; and a physical Android device test against the exact APK SHA entries already recorded in the physical-device registry. None of those gates blocks continued independent contract/test hardening.

## Rollback and isolation

No production endpoint, signing material, Play listing, billing setting, OAuth consent, Cloudflare/WAVE configuration, dedicated native-game stream, or token-finance implementation was changed. This pass is Git-only ReleaseOps/contract/test work and can be rolled back by reverting the listed commits; the prior exact Android candidate artifacts remain unchanged.
