#!/usr/bin/env python3
"""THF canonical mint historical/recent activity classifier. Read-only RPC; never signs/broadcasts."""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,time,urllib.request
MINT='HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv'; RPC_DEFAULT='https://api.mainnet-beta.solana.com'
SUPPLY_TYPES={'mintTo','mintToChecked','burn','burnChecked'}; WATCH_TYPES=SUPPLY_TYPES|{'setAuthority','transfer','transferChecked','closeAccount'}
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rpc(method,params,retries=3):
 url=os.environ.get('SOLANA_RPC_URL',RPC_DEFAULT); body=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(); last=None
 for n in range(retries):
  try:
   req=urllib.request.Request(url,data=body,headers={'content-type':'application/json'}); out=json.load(urllib.request.urlopen(req,timeout=25))
   if 'error' in out: raise RuntimeError('rpc_error')
   return out.get('result')
  except Exception as e: last=e; time.sleep(1+n*2)
 raise RuntimeError(f'{method} failed after retries ({type(last).__name__})')
def utc(ts): return datetime.datetime.fromtimestamp(ts,datetime.timezone.utc).isoformat() if isinstance(ts,(int,float)) else None
def walk_instructions(tx):
 if not tx:return []
 groups=[(((tx.get('transaction') or {}).get('message') or {}).get('instructions') or [])]
 for inner in (tx.get('meta') or {}).get('innerInstructions') or []: groups.append(inner.get('instructions') or [])
 found=[]
 for ins in [i for g in groups for i in g]:
  parsed=ins.get('parsed') if isinstance(ins,dict) else None
  if not isinstance(parsed,dict):continue
  typ=parsed.get('type'); info=parsed.get('info') if isinstance(parsed.get('info'),dict) else {}; mint=info.get('mint')
  if typ in WATCH_TYPES and (mint==MINT or MINT in json.dumps(info,sort_keys=True)):
   found.append({'type':typ,'mint':mint,'source':info.get('source'),'destination':info.get('destination'),'authority':info.get('authority') or info.get('owner'),'authorityType':info.get('authorityType'),'newAuthority':info.get('newAuthority'),'amount':info.get('amount'),'tokenAmount':info.get('tokenAmount')})
 return found
def classify(limit=10):
 supply=rpc('getTokenSupply',[MINT,{'commitment':'finalized'}]) or {}; current=(supply.get('value') or {})
 sigs=rpc('getSignaturesForAddress',[MINT,{'limit':limit,'commitment':'finalized'}]) or []; rows=[]; counts={k:0 for k in sorted(WATCH_TYPES)}; unavailable=0
 for item in sigs:
  try:
   tx=rpc('getTransaction',[item.get('signature'),{'encoding':'jsonParsed','maxSupportedTransactionVersion':0,'commitment':'finalized'}]); events=walk_instructions(tx); status='classified'
   for ev in events: counts[ev['type']]=counts.get(ev['type'],0)+1
  except Exception: events=[];status='unavailable';unavailable+=1
  rows.append({'signature':item.get('signature'),'slot':item.get('slot'),'blockTime':item.get('blockTime'),'blockTimeUtc':utc(item.get('blockTime')),'err':item.get('err'),'classification_status':status,'canonical_mint_events':events})
 supply_events=sum(counts.get(k,0) for k in SUPPLY_TYPES)
 if unavailable: claim='inconclusive_sample_due_to_unavailable_transactions'
 elif supply_events: claim='historical_supply_instruction_observed_in_sample_current_supply_reported_separately'
 else: claim='no_supply_instruction_observed_in_classified_sample'
 out={'schema':'thf-tokenops-recent-activity/v2','network':'solana-mainnet-beta','mint':MINT,'current_supply_raw':current.get('amount'),'current_supply_ui':current.get('uiAmountString'),'current_supply_decimals':current.get('decimals'),'queried_signatures':len(sigs),'sample_newest_block_time_utc':utc(sigs[0].get('blockTime')) if sigs else None,'sample_oldest_block_time_utc':utc(sigs[-1].get('blockTime')) if sigs else None,'unavailable_transactions':unavailable,'event_counts':counts,'supply_instruction_count':supply_events,'claim':claim,'rows':rows,'read_only':True,'transaction_created':False,'transaction_signed':False,'transaction_submitted':False,'broadcast_allowed':False,'financial_effect':False}
 out['evidence_sha256']=sha(out);return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=10);ap.add_argument('--output',default='recent-activity.json');a=ap.parse_args();out=classify(max(1,min(a.limit,25)))
 with open(a.output,'w') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({k:out[k] for k in ('current_supply_ui','queried_signatures','sample_newest_block_time_utc','sample_oldest_block_time_utc','unavailable_transactions','event_counts','supply_instruction_count','claim','evidence_sha256')},sort_keys=True))
if __name__=='__main__':main()
