#!/usr/bin/env python3
import copy, hashlib, importlib.util, json
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location("v",HERE/"verifier.py"); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
H=lambda s: hashlib.sha256(s.encode()).hexdigest()
BASE={"spec_version":"0.1","session_id":"session-0000000001","challenge_nonce_hash":H("nonce-1"),"subject_pseudonym_hash":H("subject-1"),"activity_type":"squat","started_at":"2026-10-20T00:00:00Z","ended_at":"2026-10-20T00:05:00Z","evidence_digest":H("evidence-1"),"integrity_class":"VERIFIED_ACTIVITY","verification_score":910,"verifier_policy_version":"pow-v0.1","verifier_key_id":"dev-reference-key","issued_at":"2026-10-20T00:05:01Z","expires_at":"2026-10-20T01:05:01Z"}
def signed(x): x=copy.deepcopy(x); x["attestation_digest"]=v.canonical_digest(x); return x
NOW=datetime(2026,10,20,0,10,tzinfo=timezone.utc)
def run():
    used=set(); ok=signed(BASE); assert v.verify(ok,NOW,used)["accepted"]
    assert "nonce_reuse" in v.verify(ok,NOW,used)["reasons"]
    bad=copy.deepcopy(ok); bad["evidence_digest"]=H("tampered"); assert "digest_mismatch" in v.verify(bad,NOW,set())["reasons"]
    exp=copy.deepcopy(BASE); exp["expires_at"]="2026-10-20T00:06:00Z"; exp=signed(exp); assert "expired" in v.verify(exp,NOW,set())["reasons"]
    dur=copy.deepcopy(BASE); dur["ended_at"]="2026-10-21T00:00:00Z"; dur=signed(dur); assert "impossible_duration" in v.verify(dur,NOW,set())["reasons"]
    pol=copy.deepcopy(BASE); pol["verifier_policy_version"]="unknown"; pol=signed(pol); assert "unsupported_policy" in v.verify(pol,NOW,set())["reasons"]
    assert v.canonical_digest(signed(BASE))==v.canonical_digest(signed(BASE))
    print("PASS 7/7 Proof-of-Workout verifier fixtures")
if __name__=="__main__": run()
