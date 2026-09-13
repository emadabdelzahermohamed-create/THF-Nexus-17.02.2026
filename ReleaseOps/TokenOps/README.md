# THF TokenOps

This directory is the isolated operational control plane for the THF token on Solana Mainnet.

## Canonical mint

`HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv`

## Phase 1 — read-only audit

The first gate is strictly read-only. It queries Solana Mainnet JSON-RPC and records:

- mint account owner / token program
- decimals and current on-chain supply
- mint authority and freeze authority
- largest token accounts and their token-account owners when parsable
- recent signatures touching the mint
- current RPC slot
- machine-readable evidence plus SHA-256

No transaction is created, signed, simulated, submitted, or broadcast in this phase.

## Security boundary

- Never store a seed phrase or wallet private key in GitHub, GCP, ChatGPT, Drive, or repository files.
- Never create a persistent Solana hot-wallet key as part of ReleaseOps.
- Read-only RPC may run unattended.
- Future treasury automation must use a deliberately scoped signer / multisig / program authority and explicit limits.
- Production transfers, burns, authority changes, treasury migrations, vesting settlement, or DAO execution require a separate gated workflow and policy review.
- WAVE_MAWJA is outside TokenOps and must remain untouched.

## Current gate

Workflow: `.github/workflows/thf-token-readonly-audit.yml`

Script: `ReleaseOps/TokenOps/readonly_audit.sh`

Expected output is a GitHub Actions artifact containing `token-audit.json`, `largest-accounts.json`, `recent-signatures.json`, `rpc-slot.json`, `SUMMARY.txt`, and `SHA256SUMS.txt`.
