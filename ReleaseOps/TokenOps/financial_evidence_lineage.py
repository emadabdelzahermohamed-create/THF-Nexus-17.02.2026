#!/usr/bin/env python3
"""Immutable hash-only lineage receipt for TokenOps financial evidence reconciliation."""
from __future__ import annotations
import hashlib,json,re
from typing import Any,Dict
HEX64=re.compile(r"^[0-9a-f]{64}$")
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
def build_lineage(reconciliation:Dict[str,Any], source_commit_sha:str)->Dict[str,Any]:
    if not isinstance(source_commit_sha,str) or not re.fullmatch(r"[0-9a-f]{40}",source_commit_sha): raise ValueError("invalid source commit sha")
    rsha=reconciliation.get("reconciliation_sha256")
    if not isinstance(rsha,str) or not HEX64.match(rsha): raise ValueError("missing reconciliation sha")
    expected=sha({k:v for k,v in reconciliation.items() if k!="reconciliation_sha256"})
    if rsha!=expected: raise ValueError("reconciliation hash mismatch")
    r={"schema":"thf-tokenops-financial-evidence-lineage/v1","network":reconciliation.get("network"),"mint":reconciliation.get("mint"),
       "source_commit_sha":source_commit_sha,"reconciliation_sha256":rsha,"input_hashes":reconciliation.get("inputs",{}),
       "readiness":reconciliation.get("readiness"),"binding_blockers":reconciliation.get("binding_blockers",[]),
       "execution_authorized":False,"broadcast_allowed":False,"financial_effect":False,"wave_mawja_untouched":True}
    r["lineage_sha256"]=sha(r);return r
