#!/usr/bin/env python3
"""Fail-closed source audit for visible web controls and local API route wiring.

This is source evidence only. It cannot prove touch behavior or a successful journey on a phone.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
HTML_SUFFIX={'.html','.htm'}
TEXT_SUFFIX={'.html','.htm','.js','.ts','.tsx','.py'}
BUTTON=re.compile(r'<button\b([^>]*)>',re.I|re.S)
ANCHOR=re.compile(r'<a\b([^>]*)>',re.I|re.S)
FORM=re.compile(r'<form\b([^>]*)>',re.I|re.S)
ATTR=lambda name: re.compile(r'\b'+name+r'\s*=\s*(["\'])(.*?)\1',re.I|re.S)
ID=ATTR('id'); HREF=ATTR('href'); ACTION=ATTR('action'); ONCLICK=ATTR('onclick')
BACKEND_ROUTE=re.compile(r'@(?:app|router)\.(?:get|post|put|patch|delete)\(\s*["\']([^"\']+)["\']')
FETCH=re.compile(r'\bfetch\(\s*[`"\']([^`"\']+)[`"\']',re.I)
AXIOS=re.compile(r'\baxios\.(?:get|post|put|patch|delete)\(\s*[`"\']([^`"\']+)[`"\']',re.I)
EVENT_ID_TEMPLATES=(
 r"getElementById\(\s*['\"]{id}['\"]\s*\)\s*\.\s*onclick\s*=",
 r"getElementById\(\s*['\"]{id}['\"]\s*\)\s*\.\s*addEventListener\s*\(",
 r"querySelector\(\s*['\"]#{id}['\"]\s*\)\s*\.\s*(?:onclick|addEventListener)",
)
BAD_HREF=re.compile(r'^\s*(?:#|javascript:|about:blank)?\s*$',re.I)

def text_files(root):
 for p in root.rglob('*'):
  if p.is_file() and p.suffix.lower() in TEXT_SUFFIX and not any(x in p.parts for x in ('.git','node_modules','build','.gradle')):
   yield p

def attr(rx,s):
 m=rx.search(s); return m.group(2).strip() if m else ''

def route_regex(route:str):
 # FastAPI /x/{id} => /x/anything, while preserving optional query strings.
 esc=re.escape(route)
 esc=re.sub(r'\\\{[^}]+\\\}',r'[^/?#]+',esc)
 return re.compile(r'^'+esc+r'(?:[?#].*)?$')

def local_path(u:str):
 u=u.strip()
 if not u or u.startswith(('http://','https://','ws://','wss://','data:','blob:')): return None
 if '${' in u or '{' in u and '}' in u: return None
 return u if u.startswith('/') else None

def audit(root:Path):
 docs=[]; combined=''; backend=[]; api_refs=[]
 for p in text_files(root):
  t=p.read_text(errors='ignore'); combined+='\n'+t
  if p.suffix.lower() in HTML_SUFFIX: docs.append((p,t))
  backend.extend(BACKEND_ROUTE.findall(t))
  api_refs.extend(FETCH.findall(t)); api_refs.extend(AXIOS.findall(t))
 backend=sorted(set(backend)); route_rx=[route_regex(r) for r in backend]
 orphan_buttons=[]; bad_anchors=[]; orphan_forms=[]
 for p,t in docs:
  rel=p.relative_to(root).as_posix()
  for attrs in BUTTON.findall(t):
   if re.search(r'\bdisabled\b',attrs,re.I): continue
   if ONCLICK.search(attrs) or re.search(r'\bdata-[\w-]+\s*=',attrs,re.I): continue
   bid=attr(ID,attrs)
   handled=False
   if bid:
    handled=any(re.search(x.format(id=re.escape(bid)),combined,re.I) for x in EVENT_ID_TEMPLATES)
   if not handled: orphan_buttons.append({'file':rel,'id':bid or None,'attrs':' '.join(attrs.split())[:240]})
  for attrs in ANCHOR.findall(t):
   href=attr(HREF,attrs)
   if ONCLICK.search(attrs): continue
   if BAD_HREF.match(href): bad_anchors.append({'file':rel,'href':href or None,'attrs':' '.join(attrs.split())[:240]})
  for attrs in FORM.findall(t):
   action=attr(ACTION,attrs)
   fid=attr(ID,attrs)
   handled=bool(action and not BAD_HREF.match(action))
   if not handled and fid:
    handled=bool(re.search(rf"getElementById\(\s*['\"]{re.escape(fid)}['\"]\s*\).*?(?:submit|addEventListener)",combined,re.I|re.S))
   if not handled: orphan_forms.append({'file':rel,'id':fid or None,'action':action or None})
 unmapped=[]
 for u in sorted(set(api_refs)):
  lp=local_path(u)
  if lp and not any(rx.match(lp) for rx in route_rx):
   # Static assets are not backend actions.
   if not re.search(r'\.(?:js|css|png|jpg|jpeg|webp|svg|ico|json)(?:[?#].*)?$',lp,re.I): unmapped.append(u)
 return {
  'schema':1,'root':str(root),'html_documents':len(docs),'backend_routes':backend,'ui_api_references':sorted(set(api_refs)),
  'orphan_buttons':orphan_buttons,'bad_anchors':bad_anchors,'orphan_forms':orphan_forms,'unmapped_local_api_references':unmapped,
  'source_action_contract_complete':not(orphan_buttons or bad_anchors or orphan_forms or unmapped),
  'truth_boundary':{'source_only':True,'does_not_prove_touch':True,'does_not_prove_backend_success':True,'physical_phone_required':True}
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--json-out',type=Path);ns=ap.parse_args();d=audit(ns.root);s=json.dumps(d,indent=2,ensure_ascii=False);print(s)
 if ns.json_out:ns.json_out.write_text(s+'\n')
if __name__=='__main__':main()
