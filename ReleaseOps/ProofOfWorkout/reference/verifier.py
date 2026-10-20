#!/usr/bin/env python3
"""Deterministic grant-safe reference verifier for THF Proof-of-Workout v0.1.
No secrets, biometrics, token transfers, or network calls.
"""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

SUPPORTED={"walk","run","squat","push_up","plank"}
POLICY="pow-v0.1"

def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z","+00:00"))

def canonical_digest(obj):
    clean={k:v for k,v in obj.items() if k not in {"attestation_digest"}}
    blob=json.dumps(clean,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()

def verify(e, now=None, used_nonces=None):
    now=now or datetime.now(timezone.utc); used_nonces=used_nonces if used_nonces is not None else set()
    reasons=[]
    if e.get("spec_version")!="0.1": reasons.append("unsupported_spec")
    if e.get("verifier_policy_version")!=POLICY: reasons.append("unsupported_policy")
    if e.get("activity_type") not in SUPPORTED: reasons.append("unsupported_activity")
    try:
        start,end,issued,expires=map(parse_ts,[e["started_at"],e["ended_at"],e["issued_at"],e["expires_at"]])
        duration=(end-start).total_seconds()
        if duration <= 0 or duration > 21600: reasons.append("impossible_duration")
        if expires <= issued or now > expires: reasons.append("expired")
    except Exception: reasons.append("invalid_time")
    nonce=e.get("challenge_nonce_hash","")
    if nonce in used_nonces: reasons.append("nonce_reuse")
    if e.get("attestation_digest") != canonical_digest(e): reasons.append("digest_mismatch")
    if not reasons: used_nonces.add(nonce)
    return {"accepted":not reasons,"reasons":reasons,"integrity_class":e.get("integrity_class") if not reasons else "REJECTED"}

def main():
    import sys
    obj=json.load(open(sys.argv[1],encoding="utf-8"))
    print(json.dumps(verify(obj),sort_keys=True))
if __name__=="__main__": main()
