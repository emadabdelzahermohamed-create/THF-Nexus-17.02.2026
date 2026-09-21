#!/usr/bin/env python3
"""Remove the exact seeded THF Echo demo ad from an exact-source candidate.

Fail closed if the known authoritative anchor drifts. This does not invent a replacement
endpoint. With no real campaigns configured, /api/ads/next already returns {'ad': None}.
"""
from pathlib import Path
import argparse

OLD='''        if c.execute("SELECT COUNT(*) FROM ad_campaigns").fetchone()[0]==0:\n            c.execute("INSERT INTO ad_campaigns(name,placement,cpm,cpc,creative_text,landing_url) VALUES(?,?,?,?,?,?)",("THF Native Demo","feed_native",2.0,.08,"إعلان تجريبي أصلي غير مزعج","https://example.com"))\n'''
NEW='''        # No synthetic/default ad campaign is inserted. Campaign inventory must come from\n        # a real authorized control-plane write. An empty inventory is a valid no-ad state.\n'''

def apply(root: Path) -> Path:
    matches=list(root.rglob('app/main.py'))
    if len(matches)!=1:
        raise SystemExit(f'expected exactly one app/main.py, found {len(matches)}')
    p=matches[0]
    text=p.read_text(encoding='utf-8')
    if text.count(OLD)!=1:
        raise SystemExit('Echo seeded-demo anchor drift')
    text=text.replace(OLD,NEW)
    if 'https://example.com' in text or 'THF Native Demo' in text:
        raise SystemExit('placeholder demo survived patch')
    p.write_text(text,encoding='utf-8',newline='\n')
    return p

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); ns=ap.parse_args()
    print(apply(ns.root.resolve()))
