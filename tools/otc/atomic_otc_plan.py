#!/usr/bin/env python3
"""Offline fail-closed planner for a buyer-fee-paid atomic THF-for-SOL transaction.
Does not sign, broadcast, hold keys, or accept funds. Produces the exact instruction intent
that a later Solana SDK builder must serialize and simulate before owner/buyer signatures.
"""
from dataclasses import dataclass, asdict
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

def build(q:Quote):
    if q.thf_tokens<=0 or q.thf_tokens>MAX_AGGREGATE_TOKENS: raise ValueError('THF quantity outside approved design ceiling')
    if q.payment_lamports<=0: raise ValueError('payment must be positive')
    if q.buyer_fee_payer!=q.buyer_owner: raise ValueError('first-trade design requires buyer as fee payer')
    raw=q.thf_tokens*10**THF_DECIMALS
    return {'status':'UNSIGNED_OFFLINE_PLAN','mint':THF_MINT,'feePayer':q.buyer_fee_payer,'sellerSOLOutflowLamports':0,
      'requiredSigners':[q.seller_owner,q.buyer_owner],
      'instructions':[
       {'program':ATA_PROGRAM,'purpose':'create buyer THF ATA iff absent','payer':q.buyer_owner,'owner':q.buyer_owner,'mint':THF_MINT},
       {'program':TOKEN_PROGRAM,'type':'transferChecked','source':q.seller_token_account,'mint':THF_MINT,'destination':q.buyer_token_account,'authority':q.seller_owner,'amountRaw':str(raw),'decimals':THF_DECIMALS},
       {'program':SYSTEM_PROGRAM,'type':'transfer','from':q.buyer_owner,'to':q.seller_owner,'lamports':str(q.payment_lamports)}],
      'forbidden':['token-first','payment-first','approve','setAuthority','burn','mintTo','closeAccount','seller-fee-payment']}

def main():
 import argparse
 p=argparse.ArgumentParser(); p.add_argument('quote_json'); a=p.parse_args()
 q=Quote(**json.load(open(a.quote_json))); print(json.dumps(build(q),indent=2))
if __name__=='__main__': main()
