#!/usr/bin/env python3
"""Audit a THF runtime OpenAPI document for the shared identity/federation lifecycle.

Diagnostic and fail-closed: route-name evidence is necessary but not sufficient. A PASS here
never substitutes for live auth/session tests, candidate binding, or physical-device evidence.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
METHODS={'get','post','put','patch','delete'}
GROUPS={
 'health': (r'(?i)(^|/)(health|ready|live)(/|$)', {'get'}),
 'login_or_token': (r'(?i)(^|/)(auth|login|token|session)(/|$)', {'post'}),
 'refresh': (r'(?i)(^|/)(refresh|renew)(/|$)|refresh[_-]?token', {'post'}),
 'logout': (r'(?i)(^|/)(logout|signout|sign-out)(/|$)', {'post','delete'}),
 'revoke': (r'(?i)(^|/)(revoke|invalidate)(/|$)', {'post','delete'}),
 'federation_or_handoff': (r'(?i)(federat|handoff|sso|exchange|pass)', {'get','post'}),
}

def audit(doc:dict)->dict:
 paths=doc.get('paths') or {}
 normalized=[]
 for p,v in paths.items():
  if not isinstance(v,dict): continue
  methods=sorted(k.lower() for k in v if k.lower() in METHODS)
  normalized.append({'path':p,'methods':methods})
 found={}
 evidence={}
 for name,(pat,expected_methods) in GROUPS.items():
  rx=re.compile(pat); ev=[]
  for item in normalized:
   if rx.search(item['path']) and expected_methods.intersection(item['methods']): ev.append(item)
  found[name]=bool(ev); evidence[name]=ev[:10]
 lifecycle=('login_or_token','refresh','logout','revoke')
 return {
  'schema':1,'openapi':doc.get('openapi'),'title':(doc.get('info') or {}).get('title'),
  'path_count':len(normalized),'capabilities':found,'evidence':evidence,
  'identity_lifecycle_surface_complete':all(found[x] for x in lifecycle),
  'shared_pass_surface_complete':all(found[x] for x in lifecycle+('federation_or_handoff',)),
  'health_surface':found['health'],
  'truth_boundary':{'route_surface_only':True,'does_not_prove_auth_success':True,'does_not_prove_revocation_semantics':True,'does_not_prove_candidate_binding':True,'final_or_play_ready':False},
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument('openapi_json',type=Path);ap.add_argument('--json-out',type=Path);ap.add_argument('--require-pass',action='store_true');ns=ap.parse_args()
 d=audit(json.loads(ns.openapi_json.read_text()));s=json.dumps(d,indent=2);print(s)
 if ns.json_out:ns.json_out.write_text(s+'\n')
 if ns.require_pass and not d['shared_pass_surface_complete']:raise SystemExit(2)
if __name__=='__main__':main()
