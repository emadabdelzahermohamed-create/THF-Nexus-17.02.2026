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
FORM_BLOCK=re.compile(r'<form\b([^>]*)>(.*?)</form\s*>',re.I|re.S)
ATTR=lambda name: re.compile(r'\b'+name+r'\s*=\s*(["\'])(.*?)\1',re.I|re.S)
ID=ATTR('id'); HREF=ATTR('href'); ACTION=ATTR('action'); ONCLICK=ATTR('onclick'); TYPE=ATTR('type')
BACKEND_ROUTE=re.compile(r'@(?:app|router)\.(?:get|post|put|patch|delete)\(\s*["\']([^"\']+)["\']')
FETCH=re.compile(r'\bfetch\(\s*[`"\']([^`"\']+)[`"\']',re.I)
AXIOS=re.compile(r'\baxios\.(?:get|post|put|patch|delete)\(\s*[`"\']([^`"\']+)[`"\']',re.I)
EVENT_ID_TEMPLATES=(
 r"getElementById\(\s*['\"]{id}['\"]\s*\)\s*\??\.\s*onclick\s*=",
 r"getElementById\(\s*['\"]{id}['\"]\s*\)\s*\??\.\s*addEventListener\s*\(",
 r"querySelector\(\s*['\"]#{id}['\"]\s*\)\s*\??\.\s*(?:onclick|addEventListener)",
 r"\b{id}\s*\.\s*onclick\s*=",
 r"\b{id}\s*\.\s*addEventListener\s*\(",
)
BAD_HREF=re.compile(r'^\s*(?:#|javascript:|about:blank)?\s*$',re.I)

def text_files(root):
 for p in root.rglob('*'):
  if p.is_file() and p.suffix.lower() in TEXT_SUFFIX and not any(x in p.parts for x in ('.git','node_modules','build','.gradle')):
   yield p

def attr(rx,s):
 m=rx.search(s); return m.group(2).strip() if m else ''

def route_regex(route:str):
 esc=re.escape(route)
 esc=re.sub(r'\\\{[^}]+\\\}',r'[^/?#]+',esc)
 return re.compile(r'^'+esc+r'(?:[?#].*)?$')

def local_path(u:str):
 u=u.strip()
 if not u or u.startswith(('http://','https://','ws://','wss://','data:','blob:')): return None
 if '${' in u: return None
 return u if u.startswith('/') else None

def id_has_handler(fid:str,combined:str,event='click'):
 if not fid:return False
 if event=='click':
  return any(re.search(x.format(id=re.escape(fid)),combined,re.I) for x in EVENT_ID_TEMPLATES)
 esc=re.escape(fid)
 return bool(
  re.search(rf"getElementById\(\s*['\"]{esc}['\"]\s*\)\s*\??\.\s*(?:on{event}|addEventListener\s*\(\s*['\"]{event})",combined,re.I)
  or re.search(rf"\b{esc}\s*\.\s*(?:on{event}|addEventListener\s*\(\s*['\"]{event})",combined,re.I)
 )

def form_has_handler(fid:str,action:str,combined:str):
 if action and not BAD_HREF.match(action): return True
 if not fid:return False
 if id_has_handler(fid,combined,'submit'): return True
 # Common helper binding: postForm(formElement, '/api/...') or bindForm(formElement,...)
 return bool(re.search(rf"\b\w*(?:form|submit|bind)\w*\s*\(\s*{re.escape(fid)}\s*[,)]",combined,re.I))

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
  handled_form_button_spans=[]
  for fm in FORM_BLOCK.finditer(t):
   attrs,body=fm.group(1),fm.group(2); fid=attr(ID,attrs); action=attr(ACTION,attrs)
   handled=form_has_handler(fid,action,combined)
   if not handled: orphan_forms.append({'file':rel,'id':fid or None,'action':action or None})
   else:
    body_start=fm.start(2)
    for bm in BUTTON.finditer(body):
     typ=attr(TYPE,bm.group(1)).lower()
     if typ not in ('button','reset'):
      handled_form_button_spans.append((body_start+bm.start(),body_start+bm.end()))
  for bm in BUTTON.finditer(t):
   attrs=bm.group(1)
   if re.search(r'\bdisabled\b',attrs,re.I): continue
   if ONCLICK.search(attrs) or re.search(r'\bdata-[\w-]+\s*=',attrs,re.I): continue
   if any(a<=bm.start() and bm.end()<=b for a,b in handled_form_button_spans): continue
   bid=attr(ID,attrs)
   if not id_has_handler(bid,combined,'click'):
    orphan_buttons.append({'file':rel,'id':bid or None,'attrs':' '.join(attrs.split())[:240]})
  for attrs in ANCHOR.findall(t):
   href=attr(HREF,attrs)
   if ONCLICK.search(attrs): continue
   if BAD_HREF.match(href): bad_anchors.append({'file':rel,'href':href or None,'attrs':' '.join(attrs.split())[:240]})
 unmapped=[]
 for u in sorted(set(api_refs)):
  lp=local_path(u)
  if not lp: continue
  mapped=any(rx.match(lp) for rx in route_rx)
  # Prefix fetches such as '/api/handoff/' + target map to '/api/handoff/{target}'.
  if not mapped and lp.endswith('/'):
   mapped=any(r.startswith(lp+'{') for r in backend)
  if not mapped and not re.search(r'\.(?:js|css|png|jpg|jpeg|webp|svg|ico|json)(?:[?#].*)?$',lp,re.I):
   unmapped.append(u)
 return {
  'schema':2,'root':str(root),'html_documents':len(docs),'backend_routes':backend,'ui_api_references':sorted(set(api_refs)),
  'orphan_buttons':orphan_buttons,'bad_anchors':bad_anchors,'orphan_forms':orphan_forms,'unmapped_local_api_references':unmapped,
  'source_action_contract_complete':not(orphan_buttons or bad_anchors or orphan_forms or unmapped),
  'truth_boundary':{'source_only':True,'does_not_prove_touch':True,'does_not_prove_backend_success':True,'physical_phone_required':True}
 }

def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--json-out',type=Path);ns=ap.parse_args();d=audit(ns.root);s=json.dumps(d,indent=2,ensure_ascii=False);print(s)
 if ns.json_out:ns.json_out.write_text(s+'\n')
if __name__=='__main__':main()
