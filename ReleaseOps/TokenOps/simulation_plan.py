#!/usr/bin/env python3
import argparse, hashlib, json

ALLOWED={'reward_epoch','vesting_settlement','burn','treasury_transfer'}

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()

def build(manifest):
    if manifest.get('operation') not in ALLOWED:
        raise ValueError('unsupported operation')
    if manifest.get('transaction_created') is not False or manifest.get('transaction_signed') is not False or manifest.get('transaction_submitted') is not False:
        raise ValueError('manifest is not unsigned/non-executed')
    if manifest.get('broadcast_allowed') is not False:
        raise ValueError('broadcast must remain disabled')
    if manifest.get('external_signer_required') is not True:
        raise ValueError('external signer boundary missing')
    op=manifest['operation']
    payload=manifest.get('payload') or {}
    plan={
      'version':1,
      'network':manifest['network'],
      'mint':manifest['mint'],
      'operation':op,
      'manifest_sha256':manifest['manifest_sha256'],
      'solana_simulation':{
        'rpc_method':'simulateTransaction',
        'encoding':'base64',
        'sig_verify':False,
        'replace_recent_blockhash':True,
        'commitment':'confirmed',
        'serialized_transaction_present':False,
        'requires_external_transaction_compiler':True,
        'requires_external_signer_for_execution':True,
        'simulation_only':True,
        'broadcast_allowed':False
      },
      'instruction_intent':{
        'program':'spl-token',
        'kind':op,
        'payload':payload
      },
      'safety':{
        'private_key_required':False,
        'signature_required_for_plan':False,
        'transaction_created':False,
        'transaction_signed':False,
        'transaction_submitted':False,
        'financial_effect':False
      }
    }
    plan['simulation_plan_sha256']=hashlib.sha256(canonical(plan)).hexdigest()
    return plan

def main():
    p=argparse.ArgumentParser(); p.add_argument('manifest'); p.add_argument('output'); a=p.parse_args()
    out=build(json.load(open(a.manifest)))
    json.dump(out,open(a.output,'w'),indent=2); print(out['simulation_plan_sha256'])
if __name__=='__main__': main()
