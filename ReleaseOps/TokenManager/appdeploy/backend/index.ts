import { router, json, error } from '@appdeploy/sdk';
import {
  createOperationPlan,
  getHolders,
  getOverview,
  inspectWallet,
} from './tokenService';

export const handler = router({
  'GET /api/_healthcheck': [async () => json({ message: 'Success' })],
  'GET /api/token/overview': [
    async () => {
      try {
        return json(await getOverview());
      } catch (e) {
        console.error(e);
        return error('solana_rpc_unavailable', 503);
      }
    },
  ],
  'GET /api/token/holders': [async () => json(await getHolders())],
  'POST /api/wallet/inspect': [
    async ({ body }) => {
      try {
        const wallet = String(
          (body as { wallet?: string } | null)?.wallet ?? ''
        );
        return json(await inspectWallet(wallet));
      } catch (e) {
        return error('invalid_or_unavailable_wallet', 400);
      }
    },
  ],
  'POST /api/operations/plan': [
    async ({ body }) => {
      try {
        return json(
          createOperationPlan(
            (body ?? {}) as { kind?: string; amountUi?: number }
          )
        );
      } catch (e) {
        return error('invalid_operation_plan', 400);
      }
    },
  ],
});
