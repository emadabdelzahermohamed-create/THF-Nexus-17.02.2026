# THF TokenOps Incident / Quarantine Runbook

Scope: canonical THF mint on Solana Mainnet only. WAVE is out of scope.

## Deterministic operating modes

- `NORMAL_READ_ONLY`: core invariant and evidence-chain controls pass; known financial-readiness blockers remain fail-closed and do not by themselves constitute an incident.
- `READ_ONLY_DEGRADED`: core controls pass, but optional observability such as holder concentration is unavailable. Continue independent read-only diagnostics; do not weaken any financial gate.
- `FAIL_CLOSED_CRITICAL`: a canonical invariant, evidence-chain, scope/provenance, treasury reconciliation, or execution-safety condition fails. Pause generation of review-ready financial intents and require a fresh core audit plus human-controlled governance review.

## Automatic read-only quarantine triggers

Quarantine financial intents when any authoritative audit detects: canonical mint/network drift; token program drift; decimals drift; mint or freeze authority reappearing; supply below the approved 8B floor or above the 10B ceiling; evidence hash/freshness mismatch; treasury ownership/balance/hash reconciliation mismatch; Vault/Forge/Core contract violation; WAVE entering TokenOps provenance; or any unexpected claim that autonomous financial execution is authorized.

Optional RPC/holder-concentration unavailability alone is degraded observability, not a core incident, provided the canonical invariant and evidence chain remain valid.

## Automatic response

1. Block generation of review-ready reward, vesting, burn and treasury-transfer intents for critical incidents.
2. Preserve the read-only audit, invariant gate, policy hashes, source provenance and evidence manifest.
3. Record deterministic critical/degraded reasons and source SHA-256 bindings.
4. Continue independent read-only diagnostics where safe.
5. Require human-controlled multisig/governance review before any recovery action that could have financial effect.

## Rollback semantics

Repository/control-plane rollback may be recommended to a previously verified checkpoint when a critical software/evidence regression is proven. This is a recommendation only and must preserve evidence lineage. There is no automatic or implied on-chain rollback.

## Forbidden automatic recovery

Never sign, submit, broadcast, transfer, burn, change authorities, migrate treasury, settle vesting/rewards, rotate financial signers, execute DAO decisions, or construct executable transaction/instruction bytes automatically. Never request or retain seed phrases/private keys.

## Recovery gate

Recovery requires a fresh passing Mainnet invariant audit, a fresh passing evidence chain, verified treasury/public ownership evidence where relevant, exact SHA-256 evidence, and the approval threshold defined by the authoritative treasury/governance policy. A passing recovery audit restores review capability only; it does not itself authorize execution.
