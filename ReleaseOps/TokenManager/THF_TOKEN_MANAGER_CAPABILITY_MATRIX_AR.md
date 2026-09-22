# THF Token Manager — Capability Matrix

| المجال | الحالة الآن | المرحلة التنفيذية |
|---|---|---|
| Chain identity / supply / authorities | LIVE | Read-only |
| Wallet inspection | LIVE | Read-only |
| Holder concentration | LIVE-DEGRADED depending on RPC | Read-only |
| Incident / quarantine | موجود في TokenOps | ربط UI كامل |
| Evidence chain / hashes | موجود في TokenOps | ربط UI كامل |
| Treasury registry | Fail-Closed: no verified treasury accounts | إضافة عناوين عامة وإثبات الملكية/الرصيد |
| Multisig | غير مفعّل ماليًا | Squads v4 |
| Treasury transfers | Review-only | Multisig execution |
| 35% revenue distribution | Policy exists, budget derivation not approved | اعتماد value basis + caps + reserve |
| Anti-Sybil / activity evidence | Required by policy | ربط مصدر النشاط الموثق |
| Anti-whale caps | Required, values not approved | اعتماد per-user + epoch caps |
| Burn 10B -> floor 8B | Review-only | Burn reserve + 3 approvals + simulation |
| Vesting | Terms not approved | Streamflow adapter + approved schedules |
| Locking | Terms not approved | Lock contracts + reward source policy |
| Lock rewards | Terms not approved | Reward reserve; no new mint |
| Liquidity | Not configured | Treasury allocation + DEX/AMM policy |
| Jupiter swaps | Not enabled | Quote + slippage limits + multisig |
| DAO | Decision packets exist | SPL Governance/Realms adapter |
| Metadata | Needs authority inspection | Metaplex read/update if authorized |
| Alerts | Partial via TokenOps incidents | Wallet/RPC/treasury anomaly alerts |
| Reports | Evidence JSON exists | Arabic CSV/JSON/PDF reports |
| Android signing | Not enabled | Mobile Wallet Adapter |
| PWA / Web admin | LIVE safe-planning v2 (`1790082990998`) | Expand + auth/RBAC; authenticated E2E remains open |
| Secrets | Forbidden in source | external secret manager only |

## Safe-planning v2 release gate
- Amounts are parsed as exact 8-decimal integer base units; JavaScript floating-point is not used for financial quantities.
- Burn headroom is derived from the freshly observed current supply, not from the theoretical 10B ceiling.
- A plan is rejected if token program, decimals, authorities, supply bounds, slot, or UI/raw supply consistency fail.
- Plans carry a digest over the confirmed anchor, supply context, mint-account context, immutable identity, authorities and exact supply, with a 15-minute expiry.
- Plans remain review-only with `transactionBytesCreated=false`, `sign=false`, `signed=false`, `submitted=false`, and `broadcast=false`.
- Production source for the four runtime files matches merged SHA `ecc2a7c5fe11ef6a6eef7cf36f4fea0edcdadc6a`; deployment evidence is in `WEB_SAFE_PLANNING_V2_DEPLOY_20260922.md`.

## Required approvals before financial execution
- Reward epoch: minimum 2 approvals.
- Vesting settlement: minimum 2 approvals.
- Burn: minimum 3 approvals.
- Treasury transfer: minimum 3 approvals.
- Liquidity / DAO execution: keep at 3 until governance explicitly changes policy.

## Next implementation order
1. Register and verify treasury token accounts.
2. Create external Multisig and move operational treasury authority/control to it where appropriate.
3. Approve revenue-to-THF value basis and distribution caps.
4. Approve vesting/locking schedules and funding sources.
5. Enable signer handoff in the UI using wallet-standard/Mobile Wallet Adapter.
6. Add transaction simulation and human-readable instruction decoder.
7. Add post-transaction verification and evidence capture.
8. Add liquidity/DEX and DAO adapters after treasury governance is active.
