#!/usr/bin/env python3
"""Minimal read-only Solana JSON-RPC transport for OTC validation.
No signing, broadcasting, keys, transaction submission, or paid endpoint assumptions.
"""
import json
from urllib.request import Request, urlopen


def _rpc(endpoint: str, method: str, params: list, *, timeout: float = 10.0) -> dict:
    if not isinstance(endpoint, str) or not endpoint.startswith('https://'):
        raise ValueError('https RPC endpoint required')
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    req = Request(endpoint, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    with urlopen(req, timeout=timeout) as response:
        body = response.read()
    parsed = json.loads(body)
    if not isinstance(parsed, dict) or parsed.get('error') is not None:
        raise ValueError('RPC error or malformed response')
    return parsed


def get_finalized_slot(endpoint: str, *, timeout: float = 10.0) -> int:
    response = _rpc(endpoint, 'getSlot', [{'commitment': 'finalized'}], timeout=timeout)
    slot = response.get('result')
    if not isinstance(slot, int) or slot <= 0:
        raise ValueError('invalid finalized slot')
    return slot


def get_finalized_token_account(endpoint: str, address: str, *, min_context_slot: int,
                                timeout: float = 10.0) -> dict:
    if not isinstance(address, str) or not address:
        raise ValueError('token account address required')
    if not isinstance(min_context_slot, int) or min_context_slot <= 0:
        raise ValueError('positive min_context_slot required')
    return _rpc(endpoint, 'getAccountInfo', [address, {
        'commitment': 'finalized',
        'encoding': 'jsonParsed',
        'minContextSlot': min_context_slot,
    }], timeout=timeout)
