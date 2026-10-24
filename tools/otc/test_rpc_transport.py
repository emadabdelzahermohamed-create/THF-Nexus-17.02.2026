#!/usr/bin/env python3
"""Deterministic HTTP-boundary tests for read-only OTC Solana RPC transport."""
import json
import unittest
from unittest.mock import patch

import rpc_transport as rpc


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.payload


class RpcTransportTests(unittest.TestCase):
    def test_rejects_non_https(self):
        with self.assertRaises(ValueError):
            rpc._rpc('http://example.invalid', 'getSlot', [])

    @patch('rpc_transport.urlopen')
    def test_get_slot_request_is_finalized(self, urlopen):
        urlopen.return_value = FakeResponse({'jsonrpc':'2.0','id':1,'result':123})
        self.assertEqual(rpc.get_finalized_slot('https://rpc.example'), 123)
        req = urlopen.call_args.args[0]
        body = json.loads(req.data)
        self.assertEqual(body['method'], 'getSlot')
        self.assertEqual(body['params'], [{'commitment':'finalized'}])

    @patch('rpc_transport.urlopen')
    def test_account_request_pins_finalized_and_min_context_slot(self, urlopen):
        urlopen.return_value = FakeResponse({'jsonrpc':'2.0','id':1,'result':{'context':{'slot':456},'value':None}})
        rpc.get_finalized_token_account('https://rpc.example', 'TokenAcct', min_context_slot=321)
        req = urlopen.call_args.args[0]
        body = json.loads(req.data)
        self.assertEqual(body['method'], 'getAccountInfo')
        self.assertEqual(body['params'][1]['commitment'], 'finalized')
        self.assertEqual(body['params'][1]['encoding'], 'jsonParsed')
        self.assertEqual(body['params'][1]['minContextSlot'], 321)

    @patch('rpc_transport.urlopen')
    def test_rpc_error_fails_closed(self, urlopen):
        urlopen.return_value = FakeResponse({'jsonrpc':'2.0','id':1,'error':{'code':-32000}})
        with self.assertRaises(ValueError):
            rpc.get_finalized_slot('https://rpc.example')

    @patch('rpc_transport.urlopen')
    def test_malformed_slot_fails_closed(self, urlopen):
        urlopen.return_value = FakeResponse({'jsonrpc':'2.0','id':1,'result':0})
        with self.assertRaises(ValueError):
            rpc.get_finalized_slot('https://rpc.example')

    def test_invalid_account_inputs_fail_before_network(self):
        with self.assertRaises(ValueError):
            rpc.get_finalized_token_account('https://rpc.example', '', min_context_slot=1)
        with self.assertRaises(ValueError):
            rpc.get_finalized_token_account('https://rpc.example', 'TokenAcct', min_context_slot=0)


if __name__ == '__main__':
    unittest.main()
