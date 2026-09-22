import { createHash } from 'node:crypto';

export const MINT = 'HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv';
const PROGRAM = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA';
const DECIMALS = 8;
const SCALE = 100_000_000n;
const FLOOR_RAW = 8_000_000_000n * SCALE;
const CEILING_RAW = 10_000_000_000n * SCALE;
const OBSERVATION_MAX_AGE_MS = 2 * 60 * 1000;
const OBSERVATION_FUTURE_SKEW_MS = 30 * 1000;
const PLAN_TTL_MS = 15 * 60 * 1000;
const BASE58 = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;

type ChainSafetySnapshot = {
  status: string;
  slot: number;
  contextSlots: {
    anchor: number;
    supply: number;
    mintAccount: number;
  };
  supplyRaw: string;
  supplyUi: string;
  decimals: number;
  programId: string;
  mintAuthority: string | null;
  freezeAuthority: string | null;
  observedAt: string;
  invariantFailures?: string[];
};

function configuredRpcUrl() {
  const configured = String(process.env.SOLANA_RPC_URL ?? '').trim();
  const value = configured || 'https://api.mainnet-beta.solana.com';
  const parsed = new URL(value);
  if (parsed.protocol !== 'https:' || parsed.username || parsed.password)
    throw new Error('rpc_url_must_be_https_without_credentials');
  return parsed.toString();
}

function parseUiAmount(value: unknown, decimals = DECIMALS) {
  const text = String(value ?? '').trim();
  const match = /^(0|[1-9]\d*)(?:\.(\d+))?$/.exec(text);
  if (!match || (match[2]?.length ?? 0) > decimals)
    throw new Error('invalid_decimal_amount');
  const fraction = (match[2] ?? '').padEnd(decimals, '0');
  return BigInt(match[1]) * 10n ** BigInt(decimals) + BigInt(fraction || '0');
}

function formatUiAmount(raw: bigint, decimals = DECIMALS) {
  const scale = 10n ** BigInt(decimals);
  const whole = raw / scale;
  const fraction = (raw % scale).toString().padStart(decimals, '0').replace(/0+$/, '');
  return fraction ? `${whole}.${fraction}` : whole.toString();
}

function assertFreshSnapshot(snapshot: ChainSafetySnapshot) {
  if (snapshot.status !== 'PASS') throw new Error('chain_invariants_failed');
  const observed = Date.parse(snapshot.observedAt);
  const age = Date.now() - observed;
  if (
    !Number.isFinite(observed) ||
    age > OBSERVATION_MAX_AGE_MS ||
    age < -OBSERVATION_FUTURE_SKEW_MS
  )
    throw new Error('chain_observation_stale');
  const supplyRaw = BigInt(snapshot.supplyRaw);
  if (supplyRaw < FLOOR_RAW || supplyRaw > CEILING_RAW)
    throw new Error('supply_outside_policy_bounds');
  return supplyRaw;
}

async function rpc(method: string, params: unknown[]) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12_000);
  try {
    const response = await fetch(configuredRpcUrl(), {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
      signal: controller.signal,
    });
    if (!response.ok) throw new Error('rpc_transport');
    const body = (await response.json()) as any;
    if (body.error) throw new Error('rpc_' + String(body.error.code ?? 'error'));
    return body.result;
  } finally {
    clearTimeout(timeout);
  }
}

export async function getOverview() {
  const anchorSlot = Number(await rpc('getSlot', [{ commitment: 'confirmed' }]));
  if (!Number.isSafeInteger(anchorSlot) || anchorSlot <= 0)
    throw new Error('rpc_anchor_slot_invalid');
  const [supply, account] = await Promise.all([
    rpc('getTokenSupply', [
      MINT,
      { commitment: 'confirmed', minContextSlot: anchorSlot },
    ]),
    rpc('getAccountInfo', [
      MINT,
      {
        encoding: 'jsonParsed',
        commitment: 'confirmed',
        minContextSlot: anchorSlot,
      },
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
  const supplyRaw = String(value.amount ?? '');
  const supplyContextSlot = Number((supply as any)?.context?.slot);
  const mintAccountContextSlot = Number((account as any)?.context?.slot);
  const invariantFailures: string[] = [];
  if (
    !Number.isSafeInteger(supplyContextSlot) ||
    supplyContextSlot < anchorSlot
  )
    invariantFailures.push('SUPPLY_CONTEXT_BEFORE_ANCHOR');
  if (
    !Number.isSafeInteger(mintAccountContextSlot) ||
    mintAccountContextSlot < anchorSlot
  )
    invariantFailures.push('MINT_CONTEXT_BEFORE_ANCHOR');
  if (programId !== PROGRAM) invariantFailures.push('TOKEN_PROGRAM_MISMATCH');
  if (Number(value.decimals) !== DECIMALS) invariantFailures.push('DECIMALS_MISMATCH');
  if (info.mintAuthority != null) invariantFailures.push('MINT_AUTHORITY_PRESENT');
  if (info.freezeAuthority != null) invariantFailures.push('FREEZE_AUTHORITY_PRESENT');
  try {
    const observedSupply = BigInt(supplyRaw);
    if (observedSupply < FLOOR_RAW || observedSupply > CEILING_RAW)
      invariantFailures.push('SUPPLY_OUTSIDE_POLICY_BOUNDS');
    if (parseUiAmount(value.uiAmountString) !== observedSupply)
      invariantFailures.push('SUPPLY_UI_RAW_MISMATCH');
  } catch {
    invariantFailures.push('SUPPLY_RAW_INVALID');
  }
  return {
    mint: MINT,
    network: 'solana-mainnet-beta',
    slot: anchorSlot,
    contextSlots: {
      anchor: anchorSlot,
      supply: supplyContextSlot,
      mintAccount: mintAccountContextSlot,
    },
    supplyUi: String(value.uiAmountString ?? ''),
    supplyRaw,
    decimals: Number(value.decimals),
    programId,
    mintAuthority: info.mintAuthority ?? null,
    freezeAuthority: info.freezeAuthority ?? null,
    recentCount,
    status: invariantFailures.length ? 'FAIL_CLOSED' : 'PASS',
    invariantFailures,
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
    const supplyRaw = BigInt(overview.supplyRaw);
    const amounts = values.map((x: any) => BigInt(String(x.amount || '0')));
    const bps = (v: bigint) =>
      supplyRaw > 0n ? Number((v * 10_000n) / supplyRaw) : null;
    return {
      status: 'ok',
      top1Bps: amounts.length ? bps(amounts[0]) : null,
      top5Bps: bps(
        amounts.slice(0, 5).reduce((a: bigint, b: bigint) => a + b, 0n)
      ),
      top20Bps: bps(
        amounts.slice(0, 20).reduce((a: bigint, b: bigint) => a + b, 0n)
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
    BigInt(String(x?.account?.data?.parsed?.info?.tokenAmount?.amount ?? '0'))
  );
  const totalRaw = amounts.reduce((a: bigint, b: bigint) => a + b, 0n);
  return {
    wallet,
    mint: MINT,
    totalUi: formatUiAmount(totalRaw),
    totalRaw: totalRaw.toString(),
    accountCount: values.length,
  };
}

function hash(input: unknown) {
  return createHash('sha256').update(JSON.stringify(input)).digest('hex');
}

export async function createOperationPlan(input: {
  kind?: string;
  amountUi?: string | number;
}) {
  const kind = String(input.kind ?? '');
  const amountRaw = parseUiAmount(input.amountUi);
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
  if (!cls || amountRaw <= 0n) throw new Error('invalid_plan');

  // Every review packet is bound to a fresh, fail-closed chain observation.
  // This still creates no transaction and never reaches a signing provider.
  const snapshot = await getOverview();
  const currentSupplyRaw = assertFreshSnapshot(snapshot);
  if (amountRaw > currentSupplyRaw) throw new Error('amount_exceeds_supply');
  if (kind === 'burn' && amountRaw > currentSupplyRaw - FLOOR_RAW)
    throw new Error('burn_exceeds_policy_headroom');
  const createdAt = new Date();
  const expiresAt = new Date(createdAt.getTime() + PLAN_TTL_MS);
  const chainSnapshot = {
    slot: snapshot.slot,
    contextSlots: snapshot.contextSlots,
    supplyRaw: snapshot.supplyRaw,
    supplyUi: snapshot.supplyUi,
    decimals: snapshot.decimals,
    programId: snapshot.programId,
    mintAuthority: snapshot.mintAuthority,
    freezeAuthority: snapshot.freezeAuthority,
    observedAt: snapshot.observedAt,
    digest: hash({
      mint: MINT,
      slot: snapshot.slot,
      contextSlots: snapshot.contextSlots,
      supplyRaw: snapshot.supplyRaw,
      decimals: snapshot.decimals,
      programId: snapshot.programId,
      mintAuthority: snapshot.mintAuthority,
      freezeAuthority: snapshot.freezeAuthority,
      observedAt: snapshot.observedAt,
    }),
  };
  const core = {
    schema: 'thf-token-manager-review-plan/v2',
    network: 'solana-mainnet-beta',
    mint: MINT,
    kind,
    amountUi: formatUiAmount(amountRaw),
    amountRaw: amountRaw.toString(),
    minimumApprovals: cls.approvals,
    executionAuthorized: false,
    transactionBytesCreated: false,
    simulationRequired: true,
    externalSignerRequired: true,
    signerBoundary: 'EXTERNAL_MULTISIG',
    sign: false,
    signed: false,
    submitted: false,
    broadcast: false,
    chainSnapshot,
    createdAt: createdAt.toISOString(),
    expiresAt: expiresAt.toISOString(),
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
