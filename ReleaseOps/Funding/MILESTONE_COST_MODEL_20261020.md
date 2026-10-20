# THF Proof-of-Workout — Milestone Cost Model

Date: 2026-10-20
Status: planning model; not an invoice, commitment, or request for funds.
Account routing: TopHeroFit@gmail.com

## Method
Use bottom-up work packages, not the maximum grant size. Before submission replace planning hours with repository/issue evidence and current market/vendor quotes where external services are unavoidable. Free/open-source/existing capacity is the default.

| Milestone | Work packages | Planning hours | Cash dependencies | Acceptance evidence |
|---|---|---:|---|---|
| M1 Verification spec/threat model | schema hardening; verifier; abuse fixtures; threat model; docs/CI | 80–140 | $0 preferred | tagged public component + deterministic tests |
| M2 Android evidence pipeline | pose/sensor fusion; signed nonce sessions; integrity hooks; four activity classifiers; privacy UX; device QA | 220–360 | $0 preferred; physical-device/cloud test spend only if free capacity fails | installable build + device/test report |
| M3 Solana devnet integration | attestation commitment; client/SDK example; devnet deploy; explorer evidence; CI | 100–180 | devnet only; no mainnet funding | explorer-verifiable devnet tx + reproducible tests |
| M4 Pilot/public measurements | consented pilot tooling; aggregate metrics; abuse remediation; docs/release | 140–240 | hosting/observability only after free tiers exhausted | public aggregate report + tagged release |

Planning total: 540–920 engineering/product hours. This range is for scope sizing; it is NOT a grant amount. Convert to a funding request only after choosing a defensible blended rate and documenting any unavoidable cash costs.

## Budget guardrails
1. Separate labor from third-party cash costs.
2. No token purchase, liquidity, exchange listing, paid influencer, or speculative treasury expense in this grant scope.
3. No raw-video storage budget by default; privacy architecture keeps frames on device.
4. Add a 10–15% contingency only to priced work packages with an explicit risk rationale; never use contingency to inflate the ask.
5. If Foundation guidance caps/reshapes a milestone, reduce scope before reducing acceptance quality.
6. Convertible funding is evaluated separately from the public-good grant and must not double-fund the same deliverable.

## Submission pricing gate
Before inserting a dollar amount, record: (a) hours by work package, (b) chosen blended rate and basis, (c) external quotes/free-tier exhaustion evidence, (d) contingency rationale, and (e) milestone payment mapping. Until all five exist, the request remains `TO BE COSTED`.
