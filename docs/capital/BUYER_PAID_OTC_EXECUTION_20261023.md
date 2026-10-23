# THF buyer-paid OTC execution pack — 2026-10-23
Status: PREPARATION / REQUEST FOR INDICATIONS ONLY. No live sale, standing offer, reservation, payment request, price, executed trade, or buyer commitment.
Owner approved proceeding with direct buyer-funded network fees and parallel sponsorship; no owner cash available.

## Verified inventory
Solana mainnet mint HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv, legacy SPL, decimals8.
Finalized RPC evidence: Ei9gQahXJW4mynXzdr3xtqJBPEpevfNxGMNEUHnmnLrG -> 8,500,000,000 THF, token account63En8JJGwoyNmRg5Udfw3H2zWo2ky1EQMcW69N77Scvv slot460542707.
CnxP2aJ9YSsGDvpeFnuwRzxqvGV2WANqi9C7fYV4ZLBk ->1,500,000,000 THF, token account9FeEf5ThQrAihAtUviNjfzGQkXhn1H9ZdycFvzvhJywX slot460542720.
Both0SOL at slots460542699/460542713. Combined10bn. No delegate in parsed token accounts. This verifies balances, not signing control or absence of external agreements.

## Selected design
Direct co-signed atomic transaction using standard System/SPL/ATA instructions, no custom contract, escrow deposit, approvals/delegates, replacement mint, LP or platform listing fee.
Buyer is fee payer and pays any required associated-token-account rent. Prefer payment in native SOL for the first small financing trade, so seller needs no USDC ATA and receives SOL for later legitimate network costs. USDC alternative needs actual canonical mint verification, seller USDC ATA and buyer-paid creation as needed.
Exactly one transaction contains THF delivery to named buyer plus full agreed payment to named seller. Both buyer and seller sign the same immutable message. Either both transfers settle or neither does; failed transaction can still consume buyer network fees. Never send tokens first or request payment first.
This is a design; transaction construction, wallet compatibility and exact simulation remain to be implemented/tested once a real quote is known. No claim that a working settlement app exists.

## Bounded commercial scope
Initial aggregate financing design ceiling25,000,000 THF =0.25% supply; this is a proposed maximum for review, not token allocation or authorization to execute.
Invite nonbinding indications without inventing price or a market value. Record quote asset, total payment, THF quantity, quote validity, delivery/vesting, fee payer, account-rent payer, buyer public address, buyer eligibility and use of funds.
No guaranteed return, listing, resale, buyback, dividend, appreciation, or liquidity. Immediate delivery cannot be described as vested. No promised25USD minimum until quote asset/value and eligibility terms are settled.
Disclose holder concentration: the two reported treasury wallets hold100% of observed10bn supply; proposed allocation/vesting has not been executed onchain.
Operating financing is for app development, release, security and disclosed operating tools. Do not label this LP capital. Any LP tranche must have a separate budget and restrictions.

## Pre-sign review per quote
1. Verify current mint, decimals, authorities, source token-account ownership/state/delegate, balances, buyer address and payment asset.
2. Reconcile all pending trades against aggregate cap; one active seller authorization per inventory slice.
3. Calculate units with integer arithmetic, no float. Store raw THF and SOL/USDC amounts and human-readable equivalents.
4. Require buyer fee payer and buyer-paid rent; seller SOL outflow0. No close account, approve, setAuthority, burn, mint, arbitrary program, extra recipient or changed destination.
5. Set recent blockhash, simulate exact message with signature verification disabled only for unsigned diagnostic; verify both expected balance changes, programs, fees and account creations. Such simulation does not prove signatures/control.
6. Obtain owner review/signature on exact live trade and buyer signature. No keys/seed export. Reject altered message, stale blockhash or expired quote.
7. Confirm finalized signature and actual balances; book proceeds separately from operating revenue; report fees, restrictions and allocations. Raised money only after confirmed payment.

## Brand-only buyer interest text
Top Hero Fit is developing an Android fitness product, with planned learning and gaming integrations. We are seeking nonbinding indications for a small direct purchase of existing THF on Solana, with buyer-paid network/account costs and simultaneous token/payment settlement. Existing mint: HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv. Pricing and quantity are negotiated per quote; no public sale or guaranteed resale market is being offered through this message. Proceeds would fund disclosed development and operating costs, not a liquidity-pool promise. Interested eligible parties can contact TopHeroFit@gmail.com with desired THF quantity, payment asset/amount and willingness to cover fees. No funds should be sent in response to this inquiry. Allocation and vesting remain proposed, and the current supply is concentrated in two treasury-reported wallets. Founder public privacy is requested; any required private diligence is handled separately by the owner.

## Parallel sponsor inquiry
To verified protocol support/partnership contacts: ask whether their existing-SPL OTC flow allows an independent buyer/sponsor fee payer for ALL create/settlement/account-rent costs and requires no issuer upfront payment. Ask for complete fee schedule, existing THF compatibility, supported wallet co-signing and eligibility. Do not claim the venue supplies buyers, cash or approval.
Streamflow official support: support@streamflow.finance, verified at https://docs.streamflow.finance/en/articles/9339023-welcome-to-streamflow . Their published fee page includes service/network/rent charges; do not call Streamflow free.
Existing Impossible inquiry already sent; no duplicate until reply or materially new scope.

## Evidence and next action
Prepared packet only. No buyer identified/qualified; no outreach sent by creating this file; no sale or money raised.
Native brand Gmail required; connected Gmail profile is personal and must not be used for brand outreach. Public Site URL includes personal alias and stays private.
Next: verify native brand mailbox, send one technical sponsorship inquiry to official Streamflow support with actual send receipt; qualify buyers through suitable brand channels and keep an outreach ledger.
Sources: https://solana.com/docs/payments/send-payments/payment-processing/fee-abstraction ; https://solana.com/docs/core/transactions ; https://solana.com/developers/migrate-to-solana/eip2612 ; https://docs.streamflow.finance/en/articles/9338305-does-streamflow-charge-any-fees
