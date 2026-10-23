#!/usr/bin/env python3
"""Fail-closed planner for a buyer-fee-paid atomic THF-for-SOL transaction.
No signing, broadcasting, key custody, or fund acceptance. Live serialization remains gated
on fresh RPC validation and canonical ATA derivation.
"""
from dataclasses import dataclass
import json
THF_MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'
THF_DECIMALS=8
MAX_AGGREGATE_TOKENS=25_000_000
SYSTEM_PROGRAM='11111111111111111111111111111111'
TOKEN_PROGRAM='TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
ATA_PROGRAM='ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'

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
    if source is None:
        raise ValueError('fresh RPC source snapshot required before transaction planning')
    validate_source_snapshot(q,source)
    return {'status':'UNSIGNED_VALIDATED_PLAN','mint':THF_MINT,'feePayer':q.buyer_fee_payer,'sellerSOLOutflowLamports':0,
      'requiredSigners':[q.seller_owner,q.buyer_owner],
      'buyerAtaValidation':'REQUIRED_CANONICAL_DERIVATION_BEFORE_SERIALIZATION',
      'instructions':[
       {'program':ATA_PROGRAM,'purpose':'create canonical buyer THF ATA iff absent','payer':q.buyer_owner,'owner':q.buyer_owner,'mint':THF_MINT},
       {'program':TOKEN_PROGRAM,'type':'transferChecked','source':q.seller_token_account,'mint':THF_MINT,'destination':q.buyer_token_account,'authority':q.seller_owner,'amountRaw':str(raw),'decimals':THF_DECIMALS},
       {'program':SYSTEM_PROGRAM,'type':'transfer','from':q.buyer_owner,'to':q.seller_owner,'lamports':str(q.payment_lamports)}],
      'forbidden':['token-first','payment-first','approve','setAuthority','burn','mintTo','closeAccount','seller-fee-payment']}

def main():
 import argparse
 p=argparse.ArgumentParser(); p.add_argument('quote_json'); p.add_argument('source_snapshot_json'); a=p.parse_args()
 q=Quote(**json.load(open(a.quote_json))); source=TokenAccountSnapshot(**json.load(open(a.source_snapshot_json)))
 print(json.dumps(build(q,source),indent=2))
if __name__=='__main__': main()
