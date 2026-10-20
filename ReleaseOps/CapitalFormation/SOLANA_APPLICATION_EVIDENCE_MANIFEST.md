# THF — Solana Application Evidence Manifest

Updated: 2026-10-20
Account identity for THF applications: TopHeroFit@gmail.com

## Purpose
Single source of truth for evidence required before submitting the THF Proof-of-Workout / verifiable-human-activity funding application. This file contains no credentials, private keys, seeds, OTPs, recovery codes, or long-lived secrets.

## Product thesis
THF Proof-of-Workout is a reusable verification primitive for human sports/activity evidence. The commercial Top Hero Fit application consumes the primitive; the grant-facing component should remain independently inspectable and reusable. Solana is used for low-cost, timestamped commitments/receipts and interoperable reward/competition state; raw video, biometrics, precise location and other sensitive evidence must remain off-chain.

## Submission fields and evidence gates

| Field | Required evidence | State |
|---|---|---|
| Company/project | Canonical Top Hero Fit naming in repo/site | VERIFY |
| Website | Public HTTPS product/demo URL with THF identity | BLOCKED until verified |
| Country | Truthful applicant/entity jurisdiction | OWNER/LEGAL FACT — do not infer |
| Applicant email | TopHeroFit@gmail.com wherever provider permits | READY |
| Applicant name | Verified legal applicant identity | VERIFY |
| Solana addresses | Public non-secret project/treasury addresses with role labels | BLOCKED until ownership/role verified |
| Funding amount | Bottom-up milestone budget + rate basis + external costs | BLOCKED until evidence complete |
| Category | Public good / developer infrastructure / consumer activity verification as form permits | VERIFY against live form |
| Why You | Working demo, open-source verifier, Android integration, measurable milestones | BLOCKED until evidence links are complete |

## Technical evidence packet

### E1 — Public specification
Required: canonical Proof-of-Workout v0.1 specification and privacy/trust-boundary description.
Acceptance: public immutable Git commit or release URL; no sensitive user evidence committed.

### E2 — Reference verifier
Required: deterministic verifier plus abuse fixtures.
Acceptance: reproducible test command; PASS output captured in CI; negative cases include replay/nonce reuse, stale evidence, digest tamper, expired session and policy mismatch.

### E3 — Solana devnet proof
Required: devnet-only commitment/receipt transaction generated from non-sensitive test evidence.
Acceptance: transaction signature + explorer link + input commitment hash + code commit SHA. Never publish seed/private key. No mainnet broadcast is required for grant evidence.

### E4 — Android integration
Required: THF Fitness build demonstrates evidence creation -> local verification -> devnet commitment flow.
Acceptance: build/version identifier, test log, short demo capture, and exact source commit.

### E5 — Milestones / use of funds
Required: M1–M4 work packages, hours, defensible blended-rate basis, free-tier assumptions, external costs and contingency.
Acceptance: every requested dollar maps to a milestone deliverable; no token liquidity, speculative marketing or personal-wallet funding included.

### E6 — Public-good reuse
Required: document how third-party sports/learning apps can create/verify the same evidence envelope without adopting THF token economics.
Acceptance: minimal integration example + permissive licensing decision verified before publication.

## Capital / legal gates
- Egypt retail crypto issuance/trading/promotion/liquidity: FAIL-CLOSED pending qualified legal/licensing clearance.
- Grant application may describe technical token utility factually; do not solicit Egyptian retail token purchases.
- No fabricated traction, guaranteed returns, listing promises or liquidity dates.
- No investor funds to a personal wallet.
- Accepting investment funds, signing investment contracts, token sale/transfer, liquidity funding, or irreversible on-chain mainnet broadcast requires the applicable legal gate and explicit final owner confirmation.

## Current execution order
1. Locate/canonicalize E1 and E2 public commit paths.
2. Add CI evidence for verifier/abuse fixtures.
3. Produce E3 devnet proof using test-only credentials/funds and retain exact explorer evidence.
4. Produce E4 Android evidence.
5. Close E5 rate-basis/external-cost assumptions and select requested amount.
6. Verify live application fields and submit early once evidence is sufficient.

## Funding-watch snapshot — 2026-10-20
- Solana Foundation grants/funding remains the canonical funding route; monitor milestone grants, convertible grants and current RFPs.
- Current Multi-Validator Staking UI RFP is not a product fit for THF; do not divert scope merely to chase it.
- Colosseum Crypto World's Fair submission window (Sep 14–Oct 12, 2026) is closed; do not fabricate eligibility or back-date a submission.
- Continue monitoring Colosseum for the next eligible competition/Eternal state and Superteam for global/Africa/Egypt grants, bounties and Instagrants.

## Account routing
All THF/token/ecosystem/business/funding/investor-relations/Solana/community/platform assets use TopHeroFit@gmail.com wherever the provider allows. Personal owner identity is used only where technically or legally required; THF assets remain identified/owned by the THF account wherever possible.
