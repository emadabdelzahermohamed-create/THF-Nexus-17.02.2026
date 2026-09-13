#!/usr/bin/env python3
"""Validate generated Android BuildConfig endpoint binding for THF candidates.

This validator is intentionally fail-closed for release promotion. It does not perform
network I/O and never prints credentials. It accepts only non-empty HTTPS/WSS endpoint
bindings in generated BuildConfig source. Runtime health/auth remains a separate gate.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
FIELD_RE=re.compile(r'public\s+static\s+final\s+String\s+(THF_(?:BASE|PASS)_URL)\s*=\s*"((?:\\.|[^"])*)"\s*;')
SAFE_SCHEMES=('https://','wss://')
BAD=re.compile(r'(?i)(localhost|127\.0\.0\.1|0\.0\.0\.0|example\.(?:com|org|net)|placeholder|changeme|your[-_.]?(?:api|host|url))')

def unescape_java(s:str)->str:
 return bytes(s,'utf-8').decode('unicode_escape')

def inspect(build_config:Path):
 text=build_config.read_text(errors='ignore')
 values={k:unescape_java(v) for k,v in FIELD_RE.findall(text)}
 out={}
 for name in ('THF_BASE_URL','THF_PASS_URL'):
  value=values.get(name,'').strip()
  out[name]={
   'present':name in values,
   'nonempty':bool(value),
   'secure_scheme':value.startswith(SAFE_SCHEMES) if value else False,
   'non_placeholder':not bool(BAD.search(value)) if value else False,
   'value_redacted': ('<bound:'+value.split('://',1)[0]+'>' if value else '<empty>'),
  }
  out[name]['pass']=all(out[name][k] for k in ('present','nonempty','secure_scheme','non_placeholder'))
 return {'schema':1,'build_config':str(build_config),'bindings':out,'binding_gate_pass':all(v['pass'] for v in out.values()),
 'truth_boundary':{'does_not_prove_reachability':True,'does_not_prove_auth':True,'does_not_prove_physical_device':True}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('build_config',type=Path);ap.add_argument('--json-out',type=Path);ap.add_argument('--require-pass',action='store_true');ns=ap.parse_args()
 d=inspect(ns.build_config);s=json.dumps(d,indent=2);print(s)
 if ns.json_out: ns.json_out.write_text(s+'\n')
 if ns.require_pass and not d['binding_gate_pass']: raise SystemExit(2)
if __name__=='__main__':main()
