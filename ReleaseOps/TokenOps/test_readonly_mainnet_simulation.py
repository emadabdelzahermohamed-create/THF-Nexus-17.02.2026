#!/usr/bin/env python3
import base64
import readonly_mainnet_simulation as m

payer='11111111111111111111111111111111'
# Structural test uses a valid 32-byte base58 key only; it is never submitted.
encoded, digest=m.build_probe_transaction(payer)
raw=base64.b64decode(encoded)
assert len(raw)>100
assert raw[0]==1                      # one signature entry
assert raw[1:65]==b'\0'*64           # zero placeholder, never a real signature
assert bytes([21]) in raw             # GetAccountDataSize opcode
assert len(digest)==64
assert len(m.b58decode(m.MINT))==32
assert len(m.b58decode(m.TOKEN_PROGRAM))==32
print('READONLY_PROBE_COMPILER=PASS')
print('REAL_SIGNATURE_USED=FALSE')
print('SEND_TRANSACTION_CALLED=FALSE')
print('TRANSACTION_BROADCAST=FALSE')
print('FINANCIAL_EFFECT=FALSE')
