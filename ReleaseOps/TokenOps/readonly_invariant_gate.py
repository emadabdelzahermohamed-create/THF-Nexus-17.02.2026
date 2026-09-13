#!/usr/bin/env python3
"""Assert canonical THF Mainnet invariants from readonly_audit.sh output.

Read-only validation only; holder concentration and signature enrichment remain optional.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any, Dict

NETWORK="solana-mainnet-beta"
MINT="HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
PROGRAM="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS=8
MAX_SUPPLY_RAW=10_000_000_000 * 10**DECIMALS
FLOOR_RAW=8_000_000_000 * 10**DECIMALS
SCHEMA="thf-tokenops-readonly-invariant-receipt/v1"

def _sha(v:Any)->str:
 return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def validate(audit:Dict[str,Any])->Dict[str,Any]:
 checks={
  "network":audit.get("network")==NETWORK,"mint":audit.get("mint")==MINT,
  "account_exists":audit.get("account_exists") is True,"program":audit.get("program_id")==PROGRAM,
  "decimals":audit.get("decimals")==DECIMALS,"mint_authority_absent":audit.get("mint_authority") is None,
  "freeze_authority_absent":audit.get("freeze_authority") is None,"readonly":audit.get("safety",{}).get("read_only") is True,
  "transaction_created_false":audit.get("safety",{}).get("transaction_created") is False,
  "transaction_signed_false":audit.get("safety",{}).get("transaction_signed") is False,
  "transaction_submitted_false":audit.get("safety",{}).get("transaction_submitted") is False,
  "private_key_used_false":audit.get("safety",{}).get("private_key_used") is False,
 }
 try: supply=int(audit.get("supply_raw"))
 except Exception: supply=None
 checks["supply_parseable"]=supply is not None
 checks["supply_not_above_original_10b"]=supply is not None and supply<=MAX_SUPPLY_RAW
 checks["supply_not_below_approved_8b_floor"]=supply is not None and supply>=FLOOR_RAW
 critical=[k for k,v in checks.items() if not v]
 degraded=[]
 if audit.get("largest_accounts_status")!="ok": degraded.append("holder_concentration_optional_query_unavailable")
 if audit.get("recent_signatures_status")!="ok": degraded.append("recent_signature_optional_query_unavailable")
 status="fail" if critical else ("degraded" if degraded else "pass")
 r={"schema":SCHEMA,"network":NETWORK,"mint":MINT,"audit_sha256":_sha(audit),"checks":checks,
    "critical_failures":critical,"degraded_conditions":degraded,"status":status,
    "financial_execution_authorized":False,"broadcast_allowed":False,"wave_mawja_untouched":True}
 r["receipt_sha256"]=_sha(r)
 return r

def main()->int:
 p=argparse.ArgumentParser();p.add_argument("audit");p.add_argument("--out",default="tokenops-audit/invariant-receipt.json")
 a=p.parse_args();audit=json.loads(Path(a.audit).read_text());r=validate(audit)
 Path(a.out).write_text(json.dumps(r,indent=2)+"\n")
 print(f"THF_TOKENOPS_INVARIANT_GATE={r['status'].upper()}");print(f"INVARIANT_RECEIPT_SHA256={r['receipt_sha256']}")
 return 1 if r["critical_failures"] else 0

if __name__=="__main__": raise SystemExit(main())
