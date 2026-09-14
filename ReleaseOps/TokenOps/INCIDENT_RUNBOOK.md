# THF TokenOps Incident / Quarantine Runbook

Scope: canonical THF mint on Solana Mainnet only. WAVE is out of scope.

## Automatic read-only quarantine triggers

Quarantine financial intents when any authoritative audit detects: canonical mint/network drift; token program drift; decimals drift; mint or freeze authority reappearing; supply below the approved 8B floor or above the 10B ceiling; evidence hash mismatch; treasury registry stale/future-slot evidence; Vault/Forge/Core contract violation.

## Automatic response

1. Block generation of review-ready reward, vesting, burn and treasury-transfer intents.
2. Preserve the read-only audit, invariant gate, policy hashes and evidence manifest.
3. Record the failing invariant and source SHA.
4. Continue independent read-only diagnostics where safe.
5. Require human-controlled multisig review before any recovery action.

## Forbidden automatic recovery

Never sign, submit, broadcast, transfer, burn, change authorities, migrate treasury, settle vesting/rewards, rotate financial signers, or execute DAO decisions automatically. Never request or retain seed phrases/private keys.

## Recovery gate

Recovery requires a fresh passing Mainnet invariant audit, verified treasury/public ownership evidence where relevant, exact evidence SHA-256, and the approval threshold defined by the authoritative treasury/governance policy. A passing recovery audit restores review capability only; it does not itself authorize execution.
