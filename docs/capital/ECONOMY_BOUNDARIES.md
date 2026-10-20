# THF Economy Boundaries

Status: binding architecture/compliance rule
Updated: 2026-10-20
Business/funding account identity where provider permits: TopHeroFit@gmail.com

## 1. Independent economic domains

THF Token is an independent economic layer. RuinsCiv, EndCiv, and future partner games retain their own authoritative backend and game-specific economies. Skins, characters, weapons, passes, diamonds, points, or other game rewards are not THF Token and must not be represented, accounted for, or silently converted as THF Token.

No implicit exchange rate, redemption promise, bridge, peg, swap, or convertibility exists between THF Token and any game currency/reward.

## 2. Fitness-to-game reward protocol

Fitness challenge rewards for games use a claim-based integration rather than token conversion:

1. Fitness verifies eligible human activity under the Proof-of-Workout policy.
2. Fitness produces a short-lived, signed eligibility claim containing only the minimum required fields (challenge ID, subject/pseudonymous account binding, partner/game ID, reward entitlement ID, issued/expiry timestamps, nonce, policy/version and integrity digest).
3. The game backend validates issuer, signature, audience, expiry, nonce/replay status, challenge/reward mapping and account binding server-side.
4. The authoritative game backend grants its own game reward.
5. The claim is marked consumed/idempotent so retries cannot duplicate rewards.

The claim conveys eligibility only. It is not money, a THF-token transfer instruction, or proof that an on-chain payment occurred.

## 3. Optional future THF-token adapter

A game may integrate THF Token only through an explicit, separately reviewed adapter. The adapter must never reuse a game-currency balance as a THF-token balance or infer convertibility.

If THF Token is proposed as an additional Fitness challenge reward, it is a separate reward rail and requires all of the following before activation:

- qualified legal/compliance clearance for the target jurisdiction and user cohort;
- KYC/AML/sanctions controls where legally required;
- anti-fraud and server-authoritative eligibility validation;
- replay/idempotency protection and allocation/campaign caps;
- treasury policy and auditable allocation ledger;
- explicit user-facing distinction between game rewards and THF Token;
- owner confirmation immediately before any irreversible on-chain transfer/broadcast.

Egypt retail crypto issuance, trading, promotion, liquidity, and retail token solicitation remain fail-closed pending qualified legal clearance.

## 4. Accounting and APIs

Maintain separate ledgers/namespaces:

- `fitness_eligibility_claims`: signed entitlement claims; no monetary balance.
- `game_rewards`: partner/game-owned reward identifiers and fulfillment status.
- `thf_token_allocations`: legally cleared THF allocations only; never game diamonds/currency.
- `treasury_transactions`: on-chain THF treasury activity after required approvals.

Cross-domain reporting may reference a common campaign ID for attribution, but must not net, merge, or convert balances.

## 5. Capital-formation disclosures

Investor, grant, tokenomics and community materials must preserve this separation. Do not count partner-game rewards as THF token distribution, circulating supply, token revenue, liquidity, or token traction. Do not describe game diamonds or virtual goods as token-backed unless a future legally reviewed architecture explicitly makes that true.

Proof-of-Workout remains suitable for the Solana public-good pitch independently of game rewards: reusable verification can attest eligible human activity, while downstream applications decide what non-token or legally cleared token benefit to grant.

## 6. Security and secrets

Never commit passwords, OTPs, recovery codes, wallet seeds, private keys, signing keys or long-lived secrets. Production claim-signing keys and treasury signing authority must remain outside Git and be independently scoped/rotatable.
