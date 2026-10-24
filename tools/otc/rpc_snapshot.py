#!/usr/bin/env python3
"""Read-only parser/validator for finalized SPL getAccountInfo responses.
No signing, broadcasting, keys, or transactions. Network transport is deliberately separate.
"""
from dataclasses import dataclass
from atomic_otc_plan import TokenAccountSnapshot, TOKEN_PROGRAM

@dataclass(frozen=True)
class RpcSnapshotEvidence:
    snapshot: TokenAccountSnapshot
    context_slot: int
    commitment: str = 'finalized'


def parse_finalized_token_account(address: str, response: dict, *, min_context_slot: int) -> RpcSnapshotEvidence:
    """Convert a jsonParsed getAccountInfo result into a fail-closed snapshot.

    Caller must request commitment=finalized and encoding=jsonParsed. min_context_slot must come
    from the immediately preceding finalized chain read/checkpoint; stale responses are rejected.
    """
    if not isinstance(min_context_slot, int) or min_context_slot <= 0:
        raise ValueError('positive min_context_slot required')
    if not isinstance(response, dict) or response.get('error') is not None:
        raise ValueError('RPC error or malformed response')
    result = response.get('result')
    if not isinstance(result, dict):
        raise ValueError('missing RPC result')
    context = result.get('context')
    if not isinstance(context, dict) or not isinstance(context.get('slot'), int):
        raise ValueError('missing RPC context slot')
    slot = context['slot']
    if slot < min_context_slot:
        raise ValueError('stale RPC context slot')
    value = result.get('value')
    if not isinstance(value, dict):
        raise ValueError('token account does not exist')
    if value.get('owner') != TOKEN_PROGRAM:
        raise ValueError('account is not owned by legacy SPL Token Program')
    data = value.get('data')
    if not isinstance(data, dict) or data.get('program') != 'spl-token':
        raise ValueError('expected jsonParsed spl-token account data')
    parsed = data.get('parsed')
    if not isinstance(parsed, dict) or parsed.get('type') != 'account':
        raise ValueError('expected parsed SPL token account')
    info = parsed.get('info')
    if not isinstance(info, dict):
        raise ValueError('missing parsed token account info')
    token_amount = info.get('tokenAmount')
    if not isinstance(token_amount, dict) or not isinstance(token_amount.get('amount'), str):
        raise ValueError('missing raw token amount')
    try:
        amount_raw = int(token_amount['amount'])
    except ValueError as exc:
        raise ValueError('invalid raw token amount') from exc
    if amount_raw < 0:
        raise ValueError('negative raw token amount')
    mint = info.get('mint'); owner = info.get('owner'); state = info.get('state')
    if not all(isinstance(x, str) and x for x in (mint, owner, state)):
        raise ValueError('missing mint/owner/state')
    delegate = info.get('delegate')
    if delegate is not None and not isinstance(delegate, str):
        raise ValueError('malformed delegate')
    return RpcSnapshotEvidence(
        snapshot=TokenAccountSnapshot(address=address, mint=mint, owner=owner,
                                     amount_raw=amount_raw, state=state, delegate=delegate),
        context_slot=slot,
    )
