#!/usr/bin/env python3
"""Audit shipping-source evidence for THF identity/session and cross-app handoff contracts.

This is deliberately non-promotional. It detects whether a candidate source exposes the
minimum implementation surfaces that must later be proven against a reachable identity
service and a physical phone. It does not assert that authentication or handoffs work.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

TEXT_SUFFIXES={'.java','.kt','.kts','.xml','.gradle','.properties','.json','.py','.js','.ts','.tsx'}
RUNTIME_ROOTS=('android/app/src/main','app','appsrc')
PATTERNS={
 'auth_request': re.compile(r'(?i)(/auth\b|/login\b|login\s*\(|authenticate|Authorization\s*[:=]|Bearer)'),
 'session_read': re.compile(r'(?i)(session|access.?token|refresh.?token|currentUser|user.?session)'),
 'logout_revoke': re.compile(r'(?i)(logout|sign.?out|revoke|clear.?session|delete.?token)'),
 'expiry_refresh': re.compile(r'(?i)(refresh.?token|token.?refresh|expires?|401|unauthori[sz]ed)'),
 'secure_storage': re.compile(r'(?i)(EncryptedSharedPreferences|MasterKey|AndroidKeyStore|KeyStore|MODE_PRIVATE|secure.?stor)'),
 'pass_binding': re.compile(r'(?i)(THF_PASS_URL|THF_PASS|passUrl|pass_url|federat|sso|oauth|openid)'),
 'handoff_send': re.compile(r'(?i)(Intent\s*\(|startActivity|ACTION_VIEW|deep.?link|app.?link|handoff)'),
 'handoff_receive': re.compile(r'(?i)(getIntent\s*\(|intent\.data|getData\s*\(|onNewIntent|intent-filter|scheme=|host=)'),
}
SENSITIVE_QUERY=re.compile(r'(?i)(access[_-]?token|refresh[_-]?token|bearer|session|password|secret)=')
CLEAR_HTTP=re.compile(r'(?i)\b(?:http|ws)://(?!schemas\.android\.com)[^\s\"\'<>)]*')


def runtime_files(root: Path):
    seen=set()
    for rel in RUNTIME_ROOTS:
        base=root/rel
        if not base.exists(): continue
        for p in base.rglob('*'):
            if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES:
                rp=p.resolve()
                if rp not in seen:
                    seen.add(rp); yield p


def audit(root: Path):
    hits={k:0 for k in PATTERNS}; samples={k:[] for k in PATTERNS}
    sensitive_query=[]; clear_http=[]; files=0
    for p in runtime_files(root):
        files+=1; rel=p.relative_to(root).as_posix(); text=p.read_text(errors='ignore')
        for key,rx in PATTERNS.items():
            n=len(rx.findall(text)); hits[key]+=n
            if n and len(samples[key])<8: samples[key].append(rel)
        if SENSITIVE_QUERY.search(text): sensitive_query.append(rel)
        if CLEAR_HTTP.search(text): clear_http.append(rel)
    minimum={
      'session_lifecycle_surface': hits['session_read']>0 and hits['logout_revoke']>0 and hits['expiry_refresh']>0,
      'secure_storage_surface': hits['secure_storage']>0,
      'federation_binding_surface': hits['pass_binding']>0,
      'cross_app_handoff_surface': hits['handoff_send']>0 and hits['handoff_receive']>0,
      'no_sensitive_query_token_pattern': len(sensitive_query)==0,
      'no_cleartext_runtime_endpoint': len(clear_http)==0,
    }
    return {
      'schema':1,'root':str(root),'runtime_files_scanned':files,'hits':hits,'samples':samples,
      'minimum_contract_surfaces':minimum,
      'sensitive_query_token_files':sorted(set(sensitive_query)),
      'cleartext_runtime_endpoint_files':sorted(set(clear_http)),
      'contract_surface_complete':all(minimum.values()),
      'truth_boundary':{
        'source_contract_is_not_auth_success_proof':True,
        'source_contract_is_not_backend_reachability_proof':True,
        'source_contract_is_not_cross_app_runtime_proof':True,
        'physical_phone_handoff_evidence_required':True,
        'expired_session_logout_revocation_runtime_evidence_required':True,
      }
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); ap.add_argument('--json-out',type=Path)
    ns=ap.parse_args(); out=audit(ns.root); text=json.dumps(out,indent=2); print(text)
    if ns.json_out: ns.json_out.write_text(text+'\n')

if __name__=='__main__': main()
