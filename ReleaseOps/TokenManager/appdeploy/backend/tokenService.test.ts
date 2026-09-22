import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';

import {
  MINT,
  createOperationPlan,
  getHolders,
  getOverview,
  inspectWallet,
} from './tokenService.ts';

const PROGRAM = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA';
const originalFetch = globalThis.fetch;
const originalRpc = process.env.SOLANA_RPC_URL;

function response(result: unknown) {
  return new Response(JSON.stringify({ jsonrpc: '2.0', id: 1, result }), {
    status: 200,
    headers: { 'content-type': 'application/json' },
  });
}

function installRpcMock(options?: {
  supplyRaw?: string;
  programId?: string;
  supplyContextSlot?: number;
  mintAccountContextSlot?: number;
  walletAmounts?: string[];
  largestAmounts?: string[];
}) {
  const supplyRaw = options?.supplyRaw ?? '1000000000000000000';
  globalThis.fetch = async (_input, init) => {
    const payload = JSON.parse(String(init?.body ?? '{}')) as {
      method?: string;
      params?: Array<Record<string, unknown> | string>;
    };
    switch (payload.method) {
      case 'getSlot':
        return response(321_654_987);
      case 'getTokenSupply':
        assert.equal(
          (payload.params?.[1] as Record<string, unknown>)?.minContextSlot,
          321_654_987
        );
        return response({
          context: { slot: options?.supplyContextSlot ?? 321_654_988 },
          value: {
            amount: supplyRaw,
            decimals: 8,
            uiAmountString:
              supplyRaw === '1000000000000000000'
                ? '10000000000'
                : '8500000000',
          },
        });
      case 'getAccountInfo':
        assert.equal(
          (payload.params?.[1] as Record<string, unknown>)?.minContextSlot,
          321_654_987
        );
        return response({
          context: { slot: options?.mintAccountContextSlot ?? 321_654_989 },
          value: {
            owner: options?.programId ?? PROGRAM,
            data: {
              parsed: {
                info: { mintAuthority: null, freezeAuthority: null },
              },
            },
          },
        });
      case 'getSignaturesForAddress':
        return response([]);
      case 'getTokenLargestAccounts':
        return response({
          value: (options?.largestAmounts ?? []).map((amount, index) => ({
            address: `holder${index}`,
            amount,
            uiAmountString: amount,
          })),
        });
      case 'getTokenAccountsByOwner':
        return response({
          value: (options?.walletAmounts ?? []).map(amount => ({
            account: {
              data: { parsed: { info: { tokenAmount: { amount } } } },
            },
          })),
        });
      default:
        throw new Error(`unexpected_rpc_method:${payload.method}`);
    }
  };
}

afterEach(() => {
  globalThis.fetch = originalFetch;
  if (originalRpc === undefined) delete process.env.SOLANA_RPC_URL;
  else process.env.SOLANA_RPC_URL = originalRpc;
});

test('overview verifies immutable THF identity and exact supply', async () => {
  installRpcMock();
  const overview = await getOverview();
  assert.equal(overview.status, 'PASS');
  assert.equal(overview.supplyRaw, '1000000000000000000');
  assert.deepEqual(overview.contextSlots, {
    anchor: 321_654_987,
    supply: 321_654_988,
    mintAccount: 321_654_989,
  });
  assert.deepEqual(overview.invariantFailures, []);
});

test('review plan is snapshot-bound and cannot sign or broadcast', async () => {
  installRpcMock();
  const plan = await createOperationPlan({ kind: 'burn', amountUi: '1.25' });
  assert.equal(plan.amountRaw, '125000000');
  assert.equal(plan.amountUi, '1.25');
  assert.equal(plan.sign, false);
  assert.equal(plan.signed, false);
  assert.equal(plan.broadcast, false);
  assert.equal(plan.externalSignerRequired, true);
  assert.equal(plan.signerBoundary, 'EXTERNAL_MULTISIG');
  assert.equal(plan.chainSnapshot.supplyRaw, '1000000000000000000');
  assert.equal(plan.chainSnapshot.contextSlots.anchor, 321_654_987);
  assert.equal(plan.chainSnapshot.contextSlots.supply, 321_654_988);
  assert.equal(plan.chainSnapshot.contextSlots.mintAccount, 321_654_989);
});

test('burn headroom uses current supply rather than the theoretical ceiling', async () => {
  installRpcMock({ supplyRaw: '850000000000000000' });
  await assert.rejects(
    createOperationPlan({ kind: 'burn', amountUi: '500000000.00000001' }),
    /burn_exceeds_policy_headroom/
  );
});

test('operation planning fails closed on a token-program mismatch', async () => {
  installRpcMock({ programId: '11111111111111111111111111111111' });
  await assert.rejects(
    createOperationPlan({ kind: 'reward_epoch', amountUi: '10' }),
    /chain_invariants_failed/
  );
});

test('operation planning fails closed when an RPC context predates its anchor', async () => {
  installRpcMock({ mintAccountContextSlot: 321_654_986 });
  await assert.rejects(
    createOperationPlan({ kind: 'reward_epoch', amountUi: '10' }),
    /chain_invariants_failed/
  );
});

test('wallet totals retain all eight decimal places without Number rounding', async () => {
  installRpcMock({ walletAmounts: ['9007199254740993', '7'] });
  const wallet = await inspectWallet(MINT);
  assert.equal(wallet.totalRaw, '9007199254741000');
  assert.equal(wallet.totalUi, '90071992.54741');
});

test('holder concentration uses integer basis-point math', async () => {
  installRpcMock({ largestAmounts: ['100000000000000001', '99999999999999999'] });
  const holders = await getHolders();
  assert.equal(holders.status, 'ok');
  assert.equal(holders.top1Bps, 1000);
  assert.equal(holders.top5Bps, 2000);
});

test('non-HTTPS RPC configuration is rejected before transport', async () => {
  process.env.SOLANA_RPC_URL = 'http://rpc.example.test';
  let called = false;
  globalThis.fetch = async () => {
    called = true;
    throw new Error('must_not_fetch');
  };
  await assert.rejects(getOverview(), /rpc_url_must_be_https_without_credentials/);
  assert.equal(called, false);
});
