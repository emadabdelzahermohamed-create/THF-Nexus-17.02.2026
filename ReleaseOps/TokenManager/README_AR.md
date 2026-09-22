# THF Token Manager — Arabic-first control plane

## الهدف
تطبيق مستقل لإدارة THF على Solana Mainnet فوق طبقة `ReleaseOps/TokenOps` الحالية، مع واجهة عربية أولًا، وفصل كامل بين القراءة/التخطيط وبين التوقيع والتنفيذ المالي.

## الهوية الثابتة
- Network: Solana Mainnet Beta
- Mint: `HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv`
- Token Program: Classic SPL Token `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`
- Decimals: 8
- Current audited supply baseline: 10,000,000,000 THF
- Mint Authority: None
- Freeze Authority: None
- Approved burn floor: 8,000,000,000 THF
- Active-user revenue share policy: 35% of realized revenue, not automatic inflationary minting.

## النسخة الحية
- AppDeploy: https://thf-token-manager-yrh1nu.v2.appdeploy.ai/

## ما يعمل الآن
1. Live read-only token overview.
2. Verification of SPL program, decimals, mint authority and freeze authority.
3. Read-only wallet THF balance inspection from a public wallet address.
4. Largest-account / concentration probe when the selected RPC supports `getTokenLargestAccounts`.
5. Fail-closed UI if RPC data is unavailable.
6. Review-only operation plans for:
   - Burn
   - Treasury transfer
   - Reward epoch
   - Vesting settlement
   - Liquidity action
   - DAO execution
7. Enforced review metadata: minimum approvals, no transaction bytes, no signature, no submission, no broadcast.
8. Every review packet is bound to a fresh fail-closed Solana snapshot and expires after 15 minutes; supply and mint-account reads must both be at or after the same confirmed anchor slot.
9. All token amounts and concentration calculations use exact integer base units (`BigInt`) across 8 decimals.
10. Explicit external signer boundary: `sign=false`, `broadcast=false`, `EXTERNAL_MULTISIG` required.

## مبادئ أمان إلزامية
- ممنوع حفظ seed phrase / private key / raw signed transaction في المصدر أو قاعدة البيانات.
- لا توقيع تلقائي ولا broadcast تلقائي.
- كل عملية مالية مستقبلية: Simulation -> Review -> Multisig -> User-controlled signing -> Broadcast -> Post-chain verification.
- هذه النسخة تنتهي عند Review: لا تنشئ transaction bytes ولا تستدعي wallet ولا توقّع ولا تبث.
- أي اختلاف في mint/program/decimals/authorities يفعّل Fail-Closed.
- الحرق لا يسمح بخفض supply أسفل 8B وفق السياسة الحالية.
- تغيير السياسات المالية نفسها يحتاج Governance/Multisig ولا يتم من واجهة فردية مباشرة.

## البنية المقترحة
```
THF Token Manager
  ├── Arabic UI / PWA
  ├── Read-only RPC Gateway
  ├── TokenOps Safety Engine (existing)
  ├── Treasury Registry
  ├── Multisig Adapter
  ├── Distribution Engine
  ├── Vesting / Lock Adapter
  ├── Burn Controller
  ├── Liquidity / DEX Adapter
  ├── DAO / Governance Adapter
  ├── Metadata Inspector
  ├── Holder / Whale Analytics
  ├── Incident & Quarantine
  ├── Evidence / Audit Trail
  └── Export / Reporting
```

## ملاحظة تنفيذية
إلغاء Mint Authority وFreeze Authority لا يتم تغييره من هذا المشروع. أي أداة تظهر "Mint" أو "Freeze" لاحقًا يجب أن تكون للعرض/التحقق فقط بالنسبة لـTHF الحالي، وليست زر تنفيذ.
