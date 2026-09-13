#!/usr/bin/env python3
import argparse, base64, hashlib, json, struct, urllib.request, urllib.error, time

MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'
TOKEN_PROGRAM='TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
SYSTEM_PROGRAM='11111111111111111111111111111111'
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def b58decode(s):
    n=0
    for ch in s:
        n=n*58+B58.index(ch)
    raw=n.to_bytes((n.bit_length()+7)//8,'big') if n else b''
    pad=len(s)-len(s.lstrip('1'))
    return b'\0'*pad+raw


def shortvec(n):
    out=bytearray()
    while True:
        elem=n & 0x7f; n >>= 7
        if n: elem |= 0x80
        out.append(elem)
        if not n: return bytes(out)


def rpc(url, method, params, attempts=5):
    body=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode()
    for attempt in range(1, attempts+1):
        req=urllib.request.Request(url,data=body,headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=30) as r:
                data=json.load(r)
            if 'error' not in data:
                return data['result']
            last=RuntimeError(f"RPC {method}: {data['error']}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last=e
        time.sleep(attempt*2)
    raise RuntimeError(str(last))


def find_public_fee_payer(url):
    sigs=rpc(url,'getSignaturesForAddress',[MINT,{'limit':10,'commitment':'confirmed'}])
    for row in sigs:
        sig=row.get('signature')
        if not sig: continue
        try:
            tx=rpc(url,'getTransaction',[sig,{'encoding':'jsonParsed','commitment':'confirmed','maxSupportedTransactionVersion':0}],attempts=2)
            keys=(((tx or {}).get('transaction') or {}).get('message') or {}).get('accountKeys') or []
            if not keys: continue
            first=keys[0]
            payer=first.get('pubkey') if isinstance(first,dict) else first
            if not payer: continue
            info=rpc(url,'getAccountInfo',[payer,{'encoding':'base64','commitment':'confirmed'}],attempts=2)
            value=(info or {}).get('value')
            if value and value.get('owner')==SYSTEM_PROGRAM and int(value.get('lamports',0))>=10000:
                return payer, sig
        except Exception:
            continue
    raise RuntimeError('no suitable public system-owned fee payer found from recent mint history')


def build_probe_transaction(payer):
    payer_b=b58decode(payer); mint_b=b58decode(MINT); program_b=b58decode(TOKEN_PROGRAM)
    if not all(len(x)==32 for x in (payer_b,mint_b,program_b)):
        raise ValueError('invalid public key length')
    # One required signer (fee payer), represented by a zero signature. sigVerify=false in simulation.
    header=bytes([1,0,2])
    keys=shortvec(3)+payer_b+mint_b+program_b
    recent_blockhash=b'\0'*32  # RPC replaces it atomically for simulation.
    # SPL Token GetAccountDataSize = opcode 21, accounts: [mint readonly].
    ix=bytes([2])+shortvec(1)+bytes([1])+shortvec(1)+bytes([21])
    message=header+keys+recent_blockhash+shortvec(1)+ix
    tx=shortvec(1)+(b'\0'*64)+message
    return base64.b64encode(tx).decode(), hashlib.sha256(tx).hexdigest()


def run(url):
    acct=rpc(url,'getAccountInfo',[MINT,{'encoding':'jsonParsed','commitment':'confirmed'}])['value']
    info=acct['data']['parsed']['info']
    if acct['owner'] != TOKEN_PROGRAM: raise RuntimeError('mint is not owned by classic SPL Token program')
    if int(info['decimals']) != 8: raise RuntimeError('unexpected decimals')
    if info.get('mintAuthority') is not None or info.get('freezeAuthority') is not None:
        raise RuntimeError('authority invariant changed')
    payer, source_sig=find_public_fee_payer(url)
    encoded, tx_sha=build_probe_transaction(payer)
    sim=rpc(url,'simulateTransaction',[encoded,{
        'encoding':'base64','sigVerify':False,'replaceRecentBlockhash':True,
        'commitment':'confirmed','innerInstructions':True
    }])
    value=sim.get('value') or {}
    logs=value.get('logs') or []
    token_invoked=any(TOKEN_PROGRAM in line for line in logs)
    success=value.get('err') is None and token_invoked
    out={
      'version':1,'network':'solana-mainnet-beta','mint':MINT,'program_id':TOKEN_PROGRAM,
      'decimals':8,'mint_authority':None,'freeze_authority':None,
      'probe_instruction':'GetAccountDataSize','probe_opcode':21,
      'fee_payer_source':'public_recent_confirmed_transaction','fee_payer_pubkey':payer,
      'source_signature':source_sig,'signature_material':'zero_placeholder_only',
      'sig_verify':False,'replace_recent_blockhash':True,
      'serialized_probe_sha256':tx_sha,'simulation_rpc_method':'simulateTransaction',
      'simulation_err':value.get('err'),'units_consumed':value.get('unitsConsumed'),
      'return_data':value.get('returnData'),'token_program_invoked':token_invoked,
      'simulation_pass':success,
      'safety':{
        'read_only_instruction':True,'private_key_used':False,'real_signature_used':False,
        'send_transaction_called':False,'transaction_broadcast':False,'financial_effect':False,
        'wave_untouched':True
      }
    }
    out['evidence_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return out


def main():
    p=argparse.ArgumentParser(); p.add_argument('--rpc',default='https://api.mainnet-beta.solana.com'); p.add_argument('--output',required=True); a=p.parse_args()
    out=run(a.rpc)
    with open(a.output,'w') as f: json.dump(out,f,indent=2,sort_keys=True)
    print('THF_TOKENOPS_MAINNET_SIMULATION=' + ('PASS' if out['simulation_pass'] else 'FAIL'))
    print('TOKEN_PROGRAM_INVOKED=' + str(out['token_program_invoked']).upper())
    print('PRIVATE_KEY_USED=FALSE')
    print('REAL_SIGNATURE_USED=FALSE')
    print('SEND_TRANSACTION_CALLED=FALSE')
    print('TRANSACTION_BROADCAST=FALSE')
    print('FINANCIAL_EFFECT=FALSE')
    print('WAVE_UNTOUCHED=TRUE')
    print('EVIDENCE_SHA256='+out['evidence_sha256'])
    if not out['simulation_pass']: raise SystemExit(2)

if __name__=='__main__': main()
