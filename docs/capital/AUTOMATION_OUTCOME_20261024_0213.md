# THF funding execution checkpoint — 2026-10-24 02:13 Africa/Cairo

## Completed delta
Live branch/checkpoint was read first. The prior checkpoint required canonical buyer ATA derivation before any serialization.

Implemented that gate in `tools/otc/atomic_otc_plan.py` without adding a paid dependency or touching keys. The planner now derives the SPL Associated Token Account deterministically from buyer owner + legacy Token Program + THF mint using the Associated Token Program PDA rules, validates all public keys as 32-byte base58 values, and refuses a quote whose supplied buyer token account is not the canonical THF ATA. The generated plan records `CANONICAL_DERIVATION_VERIFIED` rather than the previous unresolved marker.

Added tests for: (1) a public mainnet WSOL ATA vector independently visible on Solana Explorer, (2) THF ATA derivation for the same public owner, and (3) rejection of a non-canonical buyer token account, while retaining the previous source-snapshot and buyer-paid-fee gates.

Implementation commits: `7d9282d97de0e19e681aa786a723a08fba0a3d3b` and `9b0a44fa34d67bf133e1d2d137df7011dfa5a0aa`.

Independent derivation check performed before commit: owner `GG5jCGt6Kzp9StPepZeJf6BeujyMa4TmMEYNEbF1G4Lp` + WSOL mint derives `8yDNe4ctQKtZZTFLuXaL51fVW6S2qaUGvmu7rYCTjLEV`, matching the public Solana Explorer token-account record. The same algorithm derives THF ATA `HokdYvghHusxtWPTKfEEaPm1cmcv4FSsBr35aKDwqN84` for that synthetic public test owner. No treasury/private identity is exposed by these test vectors.

## Next executable step
Add the read-only finalized RPC adapter that constructs `TokenAccountSnapshot` from parsed SPL account data and rejects stale/wrong-program/malformed responses. Then build an unsigned synthetic transaction and run `simulateTransaction(sigVerify=false)` only. No signatures or broadcast.

## Commercial state / blocker
Zero funds raised and zero THF sold. Live settlement remains blocked on a qualified buyer with exact quantity, price and public address plus owner review/signature of the final immutable transaction. Verified balances still do not establish treasury signing control. No owner-funded fee or paid infrastructure was used.