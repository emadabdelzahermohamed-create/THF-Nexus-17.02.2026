#!/usr/bin/env python3
"""Credential-posture validator for THF TokenOps automation metadata only.

Never accepts credentials themselves. It verifies that automation/control-plane
descriptors prefer short-lived federation and prohibit persistent key material.
"""
from __future__ import annotations
import hashlib,json
from typing import Any,Dict,Mapping

SCHEMA="thf-tokenops-credential-posture/v1"
ALLOWED_AUTOMATION_AUTH={"wif_oidc","github_oidc_wif","gcp_workload_identity_federation"}
FORBIDDEN_KEYS={"private_key","private_key_data","service_account_key","access_token","refresh_token","seed","mnemonic","secret"}

def _sha(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()

def _scan(v:Any,p="$")->None:
    if isinstance(v,Mapping):
        for k,x in v.items():
            if str(k).lower().replace("-","_") in FORBIDDEN_KEYS:
                raise ValueError(f"credential material field forbidden at {p}.{k}")
            _scan(x,f"{p}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v): _scan(x,f"{p}[{i}]")

def validate_credential_posture(descriptor:Dict[str,Any])->Dict[str,Any]:
    _scan(descriptor)
    auth_mode=descriptor.get("automation_auth_mode")
    ttl=descriptor.get("credential_ttl_seconds")
    persistent=descriptor.get("persistent_service_account_key")
    signer=descriptor.get("financial_signer_location")
    blockers=[]
    if auth_mode not in ALLOWED_AUTOMATION_AUTH:
        blockers.append("automation_auth_not_short_lived_federation")
    if not isinstance(ttl,int) or ttl<=0 or ttl>3600:
        blockers.append("credential_ttl_not_bounded_to_1h")
    if persistent is not False:
        blockers.append("persistent_service_account_key_not_explicitly_forbidden")
    if signer not in {"external_multisig","user_controlled_external_signer"}:
        blockers.append("financial_signer_not_external_user_controlled")
    r={"schema":SCHEMA,"descriptor_sha256":_sha(descriptor),"blockers":sorted(blockers),
       "posture_ready":not blockers,"credentials_consumed":False,"financial_signing_enabled":False,
       "broadcast_enabled":False,"persistent_service_account_key_allowed":False}
    r["credential_posture_sha256"]=_sha(r)
    return r
