#!/usr/bin/env python3
"""Fail-closed planner for a buyer-fee-paid atomic THF-for-SOL transaction.
No signing, broadcasting, key custody, or fund acceptance. Live serialization remains gated
on fresh RPC validation. Canonical buyer ATA is derived locally and must match the quote.
"""
from dataclasses import dataclass
import hashlib,json
THF_MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'
THF_DECIMALS=8
MAX_AGGREGATE_TOKENS=25_000_000
SYSTEM_PROGRAM='11111111111111111111111111111111'
TOKEN_PROGRAM='TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
ATA_PROGRAM='ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'
_B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
_P=2**255-19
_D=(-121665*pow(121666,_P-2,_P))%_P
_I=pow(2,(_P-1)//4,_P)

def _b58decode(s:str)->bytes:
    n=0
    for c in s:
        if c not in _B58: raise ValueError('invalid base58 public key')
        n=n*58+_B58.index(c)
    body=n.to_bytes((n.bit_length()+7)//8,'big') if n else b''
    return b'\0'*(len(s)-len(s.lstrip('1')))+body

def _b58encode(b:bytes)->str:
    n=int.from_bytes(b,'big'); out=''
    while n:
        n,r=divmod(n,58); out=_B58[r]+out
    zeros=len(b)-len(b.lstrip(b'\0'))
    return '1'*zeros+(out or ('' if zeros else '1'))

def _pubkey(s:str)->bytes:
    b=_b58decode(s)
    if len(b)!=32: raise ValueError('public key must decode to 32 bytes')
    return b

def _is_on_curve(compressed:bytes)->bool:
    if len(compressed)!=32: return False
    y=int.from_bytes(compressed,'little') & ((1<<255)-1)
    if y>=_P: return False
    y2=y*y%_P; u=(y2-1)%_P; v=(_D*y2+1)%_P
    x2=u*pow(v,_P-2,_P)%_P
    x=pow(x2,(_P+3)//8,_P)
    if (x*x-x2)%_P: x=x*_I%_P
    return (x*x-x2)%_P==0

def find_program_address(seeds:list[bytes],program_id:str)->tuple[str,int]:
    if any(len(s)>32 for s in seeds): raise ValueError('PDA seed too long')
    program=_pubkey(program_id)
    for bump in range(255,-1,-1):
        digest=hashlib.sha256(b''.join(seeds)+bytes([bump])+program+b'ProgramDerivedAddress').digest()
        if not _is_on_curve(digest): return _b58encode(digest),bump
    raise ValueError('unable to derive PDA')

def canonical_ata(owner:str,mint:str=THF_MINT)->str:
    ata,_=find_program_address([_pubkey(owner),_pubkey(TOKEN_PROGRAM),_pubkey(mint)],ATA_PROGRAM)
    return ata

@dataclass(frozen=True)
class Quote:
    seller_owner:str; seller_token_account:str; buyer_owner:str; buyer_token_account:str
    thf_tokens:int; payment_lamports:int; buyer_fee_payer:str

@dataclass(frozen=True)
class TokenAccountSnapshot:
    address:str; mint:str; owner:str; amount_raw:int; state:str='initialized'; delegate:str|None=None

def validate_quote(q:Quote):
    if q.thf_tokens<=0 or q.thf_tokens>MAX_AGGREGATE_TOKENS:
        raise ValueError('THF quantity outside approved design ceiling')
    if q.payment_lamports<=0: raise ValueError('payment must be positive')
    if q.buyer_fee_payer!=q.buyer_owner: raise ValueError('first-trade design requires buyer as fee payer')
    if not all((q.seller_owner,q.seller_token_account,q.buyer_owner,q.buyer_token_account)):
        raise ValueError('all public account fields are required')
    if q.buyer_token_account!=canonical_ata(q.buyer_owner):
        raise ValueError('buyer token account is not canonical THF ATA')
    return q.thf_tokens*10**THF_DECIMALS

def validate_source_snapshot(q:Quote, source:TokenAccountSnapshot):
    raw=validate_quote(q)
    if source.address!=q.seller_token_account: raise ValueError('RPC source address mismatch')
    if source.mint!=THF_MINT: raise ValueError('source mint mismatch')
    if source.owner!=q.seller_owner: raise ValueError('source owner mismatch')
    if source.state!='initialized': raise ValueError('source token account not initialized')
    if source.delegate is not None: raise ValueError('delegated source is not permitted')
    if source.amount_raw<raw: raise ValueError('insufficient verified THF source balance')
    return raw

def build(q:Quote, source:TokenAccountSnapshot|None=None):
    raw=validate_quote(q)
    if source is None: raise ValueError('fresh RPC source snapshot required before transaction planning')
    validate_source_snapshot(q,source)
    return {'status':'UNSIGNED_VALIDATED_PLAN','mint':THF_MINT,'feePayer':q.buyer_fee_payer,'sellerSOLOutflowLamports':0,
      'requiredSigners':[q.seller_owner,q.buyer_owner],'buyerAtaValidation':'CANONICAL_DERIVATION_VERIFIED',
      'instructions':[
       {'program':ATA_PROGRAM,'purpose':'create canonical buyer THF ATA iff absent','payer':q.buyer_owner,'owner':q.buyer_owner,'mint':THF_MINT,'address':q.buyer_token_account},
       {'program':TOKEN_PROGRAM,'type':'transferChecked','source':q.seller_token_account,'mint':THF_MINT,'destination':q.buyer_token_account,'authority':q.seller_owner,'amountRaw':str(raw),'decimals':THF_DECIMALS},
       {'program':SYSTEM_PROGRAM,'type':'transfer','from':q.buyer_owner,'to':q.seller_owner,'lamports':str(q.payment_lamports)}],
      'forbidden':['token-first','payment-first','approve','setAuthority','burn','mintTo','closeAccount','seller-fee-payment']}

def main():
 import argparse
 p=argparse.ArgumentParser(); p.add_argument('quote_json'); p.add_argument('source_snapshot_json'); a=p.parse_args()
 q=Quote(**json.load(open(a.quote_json))); source=TokenAccountSnapshot(**json.load(open(a.source_snapshot_json)))
 print(json.dumps(build(q,source),indent=2))
if __name__=='__main__': main()
