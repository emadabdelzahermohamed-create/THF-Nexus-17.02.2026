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
| PWA / Web admin | LIVE v1 | Expand + auth/RBAC |
| Secrets | Forbidden in source | external secret manager only |

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
