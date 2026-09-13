#!/usr/bin/env python3
"""Audit endpoint/federation references only in shipping runtime source paths.

No readiness promotion is performed. The output is intended to distinguish runtime
configuration from docs/tests/examples so placeholder evidence cannot be hidden by
non-runtime exception markers.
"""
import argparse, json, re
from pathlib import Path

URL_RE = re.compile(r"(?i)\b(?:https|wss|http|ws)://[^\s\"'<> )]+")
RUNTIME_ROOTS = [
    "android/app/src/main",
    "app",
    "appsrc",
]
TEXT_SUFFIXES={'.java','.kt','.kts','.xml','.gradle','.properties','.json','.py','.js','.ts','.tsx','.html','.css'}
PLACEHOLDER_HOSTS=("example.com","example.invalid",".invalid","localhost","127.0.0.1","0.0.0.0")
PASS_RE=re.compile(r'(?i)(THF_PASS_URL|passUrl|pass_url|/auth|/session|logout|refresh.?token|Bearer)')
BUILD_CONFIG_RE=re.compile(r'(?i)(BuildConfig\.(?:THF_BASE_URL|THF_PASS_URL)|THF_BASE_URL|THF_PASS_URL)')


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


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); ap.add_argument('--json-out',type=Path)
    ns=ap.parse_args(); root=ns.root
    urls=[]; placeholder=[]; insecure=[]; pass_files=[]; config_files=[]; files=0
    for p in runtime_files(root):
        files += 1
        rel=p.relative_to(root).as_posix()
        text=p.read_text(errors='ignore')
        if PASS_RE.search(text): pass_files.append(rel)
        if BUILD_CONFIG_RE.search(text): config_files.append(rel)
        for u in URL_RE.findall(text):
            item={'url':u,'file':rel}
            if item not in urls: urls.append(item)
            low=u.lower()
            if any(h in low for h in PLACEHOLDER_HOSTS): placeholder.append(item)
            if low.startswith(('http://','ws://')) and 'schemas.android.com' not in low: insecure.append(item)
    out={
      'schema':1,'root':str(root),'runtime_files_scanned':files,
      'runtime_urls':urls,'runtime_placeholder_urls':placeholder,'runtime_insecure_urls':insecure,
      'pass_or_auth_runtime_files':sorted(set(pass_files)),
      'build_config_endpoint_runtime_files':sorted(set(config_files)),
      'truth_boundary':{
        'audit_is_not_backend_reachability_proof':True,
        'audit_is_not_physical_device_proof':True,
        'placeholder_runtime_url_requires_resolution_before_release':True,
        'insecure_runtime_url_requires_resolution_or_strict_local_only_proof':True
      }
    }
    text=json.dumps(out,indent=2); print(text)
    if ns.json_out: ns.json_out.write_text(text+'\n')

if __name__=='__main__': main()
