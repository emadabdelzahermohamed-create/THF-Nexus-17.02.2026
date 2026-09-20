import { createHash } from 'node:crypto';

export const MINT = 'HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv';
const PROGRAM = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA';
const RPC = 'https://api.mainnet-beta.solana.com';
const DECIMALS = 8;
const FLOOR = 8_000_000_000;
const CEILING = 10_000_000_000;
const BASE58 = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;

async function rpc(method: string, params: unknown[]) {
  const response = await fetch(RPC, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
  });
  if (!response.ok) throw new Error('rpc_transport');
  const body = (await response.json()) as any;
  if (body.error) throw new Error('rpc_' + String(body.error.code ?? 'error'));
  return body.result;
}

export async function getOverview() {
  const [slot, supply, account] = await Promise.all([
    rpc('getSlot', [{ commitment: 'confirmed' }]),
    rpc('getTokenSupply', [MINT, { commitment: 'confirmed' }]),
    rpc('getAccountInfo', [
      MINT,
      { encoding: 'jsonParsed', commitment: 'confirmed' },
    ]),
  ]);
  let recentCount = 0;
  try {
    const recent = await rpc('getSignaturesForAddress', [
      MINT,
      { limit: 20, commitment: 'confirmed' },
    ]);
    recentCount = Array.isArray(recent) ? recent.length : 0;
  } catch {}
  const info = (account as any)?.value?.data?.parsed?.info ?? {};
  const programId = (account as any)?.value?.owner ?? '';
  const value = (supply as any)?.value ?? {};
  const invariantOk =
    programId === PROGRAM &&
    Number(value.decimals) === DECIMALS &&
    info.mintAuthority == null &&
    info.freezeAuthority == null;
  return {
    mint: MINT,
    network: 'solana-mainnet-beta',
    slot: Number(slot),
    supplyUi: String(value.uiAmountString ?? ''),
    decimals: Number(value.decimals),
    programId,
    mintAuthority: info.mintAuthority ?? null,
    freezeAuthority: info.freezeAuthority ?? null,
    recentCount,
    status: invariantOk ? 'PASS' : 'FAIL_CLOSED',
    observedAt: new Date().toISOString(),
  };
}

export async function getHolders() {
  try {
    const overview = await getOverview();
    const result = await rpc('getTokenLargestAccounts', [
      MINT,
      { commitment: 'confirmed' },
    ]);
    const values = Array.isArray((result as any)?.value)
      ? (result as any).value
      : [];
    const supplyRaw = Math.round(Number(overview.supplyUi) * 10 ** DECIMALS);
    const amounts = values.map((x: any) => Number(x.amount || 0));
    const bps = (v: number) =>
      supplyRaw > 0 ? Math.floor((v * 10000) / supplyRaw) : null;
    return {
      status: 'ok',
      top1Bps: amounts.length ? bps(amounts[0]) : null,
      top5Bps: bps(
        amounts.slice(0, 5).reduce((a: number, b: number) => a + b, 0)
      ),
      top20Bps: bps(
        amounts.slice(0, 20).reduce((a: number, b: number) => a + b, 0)
      ),
      accounts: values.map((x: any) => ({
        address: x.address,
        uiAmountString: x.uiAmountString ?? null,
      })),
    };
  } catch (e) {
    return { status: 'degraded', reason: 'holder_concentration_unavailable' };
  }
}

export async function inspectWallet(wallet: string) {
  if (!BASE58.test(wallet)) throw new Error('invalid_wallet');
  const result = await rpc('getTokenAccountsByOwner', [
    wallet,
    { mint: MINT },
    { encoding: 'jsonParsed', commitment: 'confirmed' },
  ]);
  const values = Array.isArray((result as any)?.value)
    ? (result as any).value
    : [];
  const amounts = values.map((x: any) =>
    Number(x?.account?.data?.parsed?.info?.tokenAmount?.uiAmountString ?? 0)
  );
  const total = amounts.reduce((a: number, b: number) => a + b, 0);
  return {
    wallet,
    mint: MINT,
    totalUi: total.toLocaleString('en-US', { maximumFractionDigits: 8 }),
    accountCount: values.length,
  };
}

function hash(input: unknown) {
  return createHash('sha256').update(JSON.stringify(input)).digest('hex');
}

export function createOperationPlan(input: {
  kind?: string;
  amountUi?: number;
}) {
  const kind = String(input.kind ?? '');
  const amountUi = Number(input.amountUi);
  const classes: Record<string, { approvals: number; note: string }> = {
    burn: { approvals: 3, note: 'الحرق دائم ويخفض إجمالي المعروض.' },
    treasury_transfer: {
      approvals: 3,
      note: 'يلزم إثبات ملكية حساب الخزينة والرصيد قبل التحويل.',
    },
    reward_epoch: {
      approvals: 2,
      note: 'توزيع 35% من الإيراد يحتاج أساس تقييم وسقف دورة ومستخدم معتمد.',
    },
    vesting_settlement: {
      approvals: 2,
      note: 'يلزم جدول Vesting معتمد واحتياطي مخصص.',
    },
    liquidity: {
      approvals: 3,
      note: 'تغيير السيولة يحتاج حدود انزلاق وسقف تعرض وسياسة خزينة.',
    },
    dao_execution: {
      approvals: 3,
      note: 'لا تنفيذ DAO قبل تحقق المقترح والتصويت والـtimelock.',
    },
  };
  const cls = classes[kind];
  if (!cls || !Number.isFinite(amountUi) || amountUi <= 0)
    throw new Error('invalid_plan');
  if (kind === 'burn' && amountUi > CEILING - FLOOR)
    throw new Error('burn_exceeds_policy_headroom');
  const core = {
    schema: 'thf-token-manager-review-plan/v1',
    network: 'solana-mainnet-beta',
    mint: MINT,
    kind,
    amountUi,
    minimumApprovals: cls.approvals,
    executionAuthorized: false,
    transactionBytesCreated: false,
    signed: false,
    submitted: false,
    broadcast: false,
    createdAt: new Date().toISOString(),
  };
  return {
    ...core,
    id: hash(core).slice(0, 16),
    status: 'REVIEW_REQUIRED',
    notes: [
      cls.note,
      'هذه الحزمة للمراجعة فقط ولا تحتوي أي مفتاح خاص أو توقيع.',
      'الخطوة التنفيذية المستقبلية يجب أن تمر عبر Multisig ومحاكاة قبل البث.',
    ],
  };
}
