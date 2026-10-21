# THF Proof-of-Workout — Public Specification v0.1

Status: grant-safe draft. No token sale, reward entitlement, or financial transaction is created by this specification.

## Goal
Define a privacy-preserving, replay-resistant activity attestation that a Solana consumer application can verify without receiving raw workout video by default.

## Trust boundaries
1. Device captures motion locally and derives landmarks/metrics; raw camera frames remain local by default.
2. Verifier issues a short-lived session nonce before the activity starts.
3. Evidence binds the nonce, activity type, monotonic time window, device/app-integrity summary, sensor summary, model/version identifiers and a canonical evidence digest.
4. Server verification produces an attestation only after policy checks. Manual entries are never equivalent to verified evidence.
5. Solana receives only the minimum attestation commitment needed for audit/composability; sensitive biometric/video data must not be placed on-chain.

## Canonical attestation fields
- spec_version
- session_id (opaque random identifier)
- challenge_nonce_hash
- subject_pseudonym_hash (rotatable; not email/name)
- activity_type
- started_at / ended_at
- evidence_digest (SHA-256 over canonical evidence envelope)
- integrity_class
- verification_score (0..1000 integer)
- verifier_policy_version
- verifier_key_id
- issued_at / expires_at
- attestation_digest

## Verification classes
- REJECTED: evidence fails integrity/replay/plausibility policy.
- PERSONAL_LOG: accepted for private history but not competition/economic rewards.
- VERIFIED_ACTIVITY: passes current verification policy and may enter competition rules.
- HIGH_VALUE_REVIEW: technically valid but requires additional review before high-value rewards.

## Required anti-abuse checks
Replay/nonce reuse; timestamp monotonicity; impossible duration/speed; mock-location signals where GPS applies; emulator/device-farm indicators; app/device integrity; evidence duplication; sensor/pose consistency; policy-version binding.

## Privacy requirements
No raw camera frame, face template, email, legal name, precise GPS trail, private key or authentication secret is required in the public attestation. Applications should retain the minimum off-chain evidence needed for appeal/audit and apply deletion/retention controls.

## Solana commitment model
A reference implementation may commit `attestation_digest`, verifier identifier, policy version, activity class and coarse issuance time to devnet/mainnet. The full evidence envelope remains off-chain. Third parties can compare the canonical digest and verifier signature without receiving private raw media.

## Acceptance fixtures for M1
The reference verifier must deterministically test: valid fresh nonce; reused nonce; modified evidence digest; expired session; impossible duration; unsupported policy version; and valid attestation canonicalization.
