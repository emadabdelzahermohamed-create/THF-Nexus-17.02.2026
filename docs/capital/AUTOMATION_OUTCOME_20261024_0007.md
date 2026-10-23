# THF funding execution checkpoint — 2026-10-24 00:07 Africa/Cairo

## Verified delta
Live branch head before this run: `8cc8b607f86ef4315fab6453544a435c2b70475e` (`funding: add fail-closed atomic OTC transaction planner tests`). The implementation now has an offline fail-closed atomic THF-for-SOL instruction-intent planner and four unit tests, but it is not yet a serialized Solana transaction and has not been RPC-simulated.

Current OTC pack confirms two finalized reported THF token accounts totaling 10bn THF and 0 SOL, while explicitly noting that balances do not prove signing control. The initial 25m THF ceiling is a proposed review ceiling only, not standing sale authority.

## Safety defect identified before serialization
The current planner accepts arbitrary `seller_owner`, `seller_token_account`, `buyer_owner`, and `buyer_token_account` strings and does not independently derive/validate ATAs or verify live account owner/mint/delegate/state. Therefore it must not be promoted directly to a serialized live transaction builder. A malicious or mistaken quote could otherwise encode an unintended destination/source while still passing the current local tests.

## Next executable engineering gate
Implement a quote validator/builder that, before serialization, obtains fresh RPC account data and fails closed unless: mint equals `HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv`; decimals=8; source token account is initialized, has this mint, is owned by the selected seller owner, has no delegate, and has sufficient balance; buyer THF destination is the canonical ATA derived from buyer owner + THF mint (create idempotently with buyer as payer when absent); buyer is fee payer; payment is positive native SOL to the same selected seller owner; only System, legacy SPL Token, Compute Budget if needed, and Associated Token Account programs are permitted; seller SOL outflow remains zero; no approve/setAuthority/burn/mint/close instructions are permitted.

Then serialize an unsigned message with a fresh blockhash and run `simulateTransaction` only as an unsigned diagnostic (`sigVerify=false`), checking program IDs, expected balance deltas, account creation/rent and errors. Do not request signatures or broadcast. Use a bounded synthetic quote for simulation until a real buyer/price/quantity exists; synthetic simulation is engineering evidence, not a sale or buyer commitment.

## Commercial state
No buyer/price/quantity has been verified in this run. No funds accepted, tokens sold, owner-funded fees, debt, listing, liquidity promise, or mainnet signature/broadcast. Existing Cyrene/Superteam outreach remains awaiting reply and must not be duplicated merely to create activity.

## Blocker after preparation
A real settlement still requires a qualified buyer with exact quote terms and buyer public address, plus separate owner review/signature of the exact immutable transaction. Signing control of the reported treasury inventory remains unproven and must be verified without exporting secrets before any live settlement.
