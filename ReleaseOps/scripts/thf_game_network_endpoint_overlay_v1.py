#!/usr/bin/env python3
"""Replace localhost game endpoints on a disposable candidate tree with an explicitly supplied HTTPS/WSS staging endpoint.
Never use on canonical archives. Endpoint values are never emitted in evidence.
"""
from __future__ import annotations
import argparse, hashlib, pathlib, re, sys, urllib.parse

HTTP_RE=re.compile(r'https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?::\d+)?',re.I)
WS_RE=re.compile(r'wss?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0)(?::\d+)?',re.I)
EXT={'.gd','.godot','.cfg','.ini','.json','.tscn','.tres','.txt'}

def validate(url:str,scheme:str)->None:
    u=urllib.parse.urlsplit(url)
    if u.scheme!=scheme or not u.hostname or u.username or u.password or u.query or u.fragment:
        raise SystemExit(f'invalid {scheme} endpoint')
    if u.hostname.lower() in {'localhost','127.0.0.1','0.0.0.0','::1'} or u.hostname.endswith('.invalid'):
        raise SystemExit('non-reachable/placeholder host rejected')

def sha(p:pathlib.Path)->str:
    h=hashlib.sha256();
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('--https-url',required=True);ap.add_argument('--wss-url',required=True);ap.add_argument('--evidence-out',required=True);a=ap.parse_args()
    validate(a.https_url,'https');validate(a.wss_url,'wss');root=pathlib.Path(a.root).resolve();
    changed=[];http_count=0;ws_count=0
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in EXT or p.stat().st_size>2_000_000:continue
        try:s=p.read_text(errors='strict')
        except (UnicodeDecodeError,OSError):continue
        n1=len(HTTP_RE.findall(s));n2=len(WS_RE.findall(s))
        if not n1 and not n2:continue
        t=HTTP_RE.sub(a.https_url.rstrip('/'),s);t=WS_RE.sub(a.wss_url.rstrip('/'),t)
        p.write_text(t);changed.append(p.relative_to(root).as_posix());http_count+=n1;ws_count+=n2
    if http_count+ws_count==0:raise SystemExit('no localhost endpoint markers replaced')
    # Re-scan to guarantee localhost was removed, without printing any endpoint value.
    remain=0
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in EXT and p.stat().st_size<=2_000_000:
            try:s=p.read_text(errors='ignore')
            except OSError:continue
            remain+=len(HTTP_RE.findall(s))+len(WS_RE.findall(s))
    lines=['schema=thf-game-network-endpoint-overlay-v1',f'https_replacements={http_count}',f'wss_replacements={ws_count}',f'changed_file_count={len(changed)}','changed_files='+','.join(changed),'remaining_localhost_endpoint_markers='+str(remain),'endpoint_values_redacted=true','candidate_only=true','canonical_archive_mutated=false','production_cutover=false','device_status=PENDING','final_status=NOT_FINAL','']
    pathlib.Path(a.evidence_out).write_text('\n'.join(lines));print('\n'.join(lines));return 0 if remain==0 else 2
if __name__=='__main__':sys.exit(main())
