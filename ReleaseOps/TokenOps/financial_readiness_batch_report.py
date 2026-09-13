#!/usr/bin/env python3
"""Generate deterministic TokenOps fail-closed readiness evidence from a read-only audit."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from policy_blocker_registry import build_registry
from treasury_risk_envelope import build_risk_envelope
from financial_readiness_attestation import build_attestation

def load(p): return json.loads(Path(p).read_text())
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--policy",required=True); ap.add_argument("--treasury-policy",required=True); ap.add_argument("--audit",required=True); ap.add_argument("--output-dir",required=True)
    a=ap.parse_args(); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    policy=load(a.policy); treasury=load(a.treasury_policy); audit=load(a.audit)
    registry=build_registry(policy,treasury,audit); risk=build_risk_envelope(policy,treasury,audit); att=build_attestation(policy,treasury,audit,registry,risk)
    for name,obj in (("policy-blockers.json",registry),("treasury-risk-envelope.json",risk),("financial-readiness-attestation.json",att)):
        (out/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print(f"READINESS_STATUS={att['readiness_status']}"); print(f"BLOCKER_COUNT={att['blocker_count']}"); print(f"EXACT_REMAINING_SIGNER_ACTION={att['exact_remaining_signer_action']}")
    print("EXECUTION_AUTHORIZED=FALSE"); print("BROADCAST_ALLOWED=FALSE"); print("FINANCIAL_EFFECT=FALSE"); print("WAVE_UNTOUCHED=TRUE")
if __name__=="__main__": main()
