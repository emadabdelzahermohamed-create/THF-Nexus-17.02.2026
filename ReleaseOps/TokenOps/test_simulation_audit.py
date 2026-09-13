#!/usr/bin/env python3
import json, tempfile
from pathlib import Path
import simulation_plan, audit_export

MANIFEST={
 'version':1,'network':'solana-mainnet-beta','mint':'HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv',
 'operation':'reward_epoch','payload':{'epoch':'test','amount_raw':'0'},'approvals':[],
 'approval_count':0,'required_approvals':2,'approval_gate_pass':False,'execution_backend':'external_multisig',
 'transaction_created':False,'transaction_signed':False,'transaction_submitted':False,
 'broadcast_allowed':False,'external_signer_required':True,'manifest_sha256':'abc123'
}
plan=simulation_plan.build(MANIFEST)
assert plan['solana_simulation']['rpc_method']=='simulateTransaction'
assert plan['solana_simulation']['serialized_transaction_present'] is False
assert plan['solana_simulation']['simulation_only'] is True
assert plan['solana_simulation']['broadcast_allowed'] is False
assert plan['safety']['financial_effect'] is False

bad=dict(MANIFEST); bad['transaction_signed']=True
try:
    simulation_plan.build(bad)
    raise AssertionError('signed manifest accepted')
except ValueError: pass

with tempfile.TemporaryDirectory() as d:
    ledger=Path(d)/'audit.jsonl'
    e1={'kind':'simulation_plan','sha256':plan['simulation_plan_sha256'],'status':'PASS'}
    e2={'kind':'holder_concentration','status':'RPC_RATE_LIMITED','non_blocking':True}
    a=audit_export.append_entry(e1,ledger,created_at=1)
    b=audit_export.append_entry(e2,ledger,created_at=2)
    result=audit_export.verify(ledger)
    assert result['verified'] is True and result['entries']==2 and result['head_hash']==b['entry_hash']
    assert b['previous_hash']==a['entry_hash']
    tampered=ledger.read_text().replace('RPC_RATE_LIMITED','PASS')
    ledger.write_text(tampered)
    try:
        audit_export.verify(ledger)
        raise AssertionError('tampered audit chain accepted')
    except ValueError: pass

print('THF_TOKENOPS_SIMULATION_GATE=PASS')
print('THF_TOKENOPS_APPEND_ONLY_AUDIT_GATE=PASS')
print('TRANSACTION_CREATED=FALSE')
print('TRANSACTION_SIGNED=FALSE')
print('TRANSACTION_SUBMITTED=FALSE')
print('FINANCIAL_EFFECT=FALSE')
