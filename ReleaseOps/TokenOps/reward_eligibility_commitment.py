#!/usr/bin/env python3
"""Deterministic privacy-preserving input commitment for THF reward epochs.

TokenOps consumes eligibility scores produced by Core/fitness/learning systems; it does not
invent activity or device data. This module commits only pseudonymous subject IDs and
normalized integer weights for treasury planning. It never signs or broadcasts transactions.
"""
from __future__ import annotations
import hashlib, json

SCHEMA="thf-tokenops-reward-eligibility/v1"

def _canon(v): return json.dumps(v, sort_keys=True, separators=(",",":"))
def digest(v): return hashlib.sha256(_canon(v).encode()).hexdigest()

def build(*, epoch_id:str, source_sha256:str, rows:list[dict], policy_sha256:str)->dict:
    if not epoch_id or len(source_sha256)!=64 or len(policy_sha256)!=64:
        raise ValueError("epoch/source/policy evidence required")
    seen=set(); normalized=[]; blockers=[]; total_weight=0
    for row in rows:
        subject=str(row.get("subject_id","")).strip()
        weight=int(row.get("weight",-1))
        provenance=str(row.get("provenance","")).strip()
        if not subject or weight < 0 or not provenance:
            blockers.append("INVALID_ELIGIBILITY_ROW"); continue
        if subject in seen: blockers.append("DUPLICATE_SUBJECT")
        seen.add(subject); total_weight += weight
        normalized.append({"subject_id":subject,"weight":weight,"provenance":provenance})
    normalized.sort(key=lambda x:x["subject_id"])
    out={"schema":SCHEMA,"epoch_id":epoch_id,"source_sha256":source_sha256,
         "policy_sha256":policy_sha256,"rows":normalized,"subject_count":len(seen),
         "total_weight":total_weight,"blockers":sorted(set(blockers)),
         "fabricated_activity_allowed":False,"contains_private_keys":False,
         "sign":False,"broadcast":False,"financial_execution":False,
         "status":"BLOCKED" if blockers else "COMMITTED_FOR_TREASURY_PLANNING"}
    out["eligibility_commitment_sha256"]=digest(out)
    return out
