#!/usr/bin/env python3
"""Candidate-only predictive-back migration for legacy THF MainActivity.

Fails closed unless the known legacy onBackPressed implementation and one onCreate
super call are present. Canonical archives remain untouched.
"""
from __future__ import annotations
import argparse, pathlib, hashlib

LEGACY='@Override public void onBackPressed() { if (webView!=null && webView.canGoBack()) webView.goBack(); else super.onBackPressed(); }'
REPLACEMENT='''private void thfHandleBack() { if (webView!=null && webView.canGoBack()) webView.goBack(); else finish(); }
    @Override public boolean onKeyDown(int keyCode, android.view.KeyEvent event) {
        if (keyCode == android.view.KeyEvent.KEYCODE_BACK && android.os.Build.VERSION.SDK_INT < 33) { thfHandleBack(); return true; }
        return super.onKeyDown(keyCode, event);
    }'''
REGISTER='''super.onCreate(savedInstanceState);
        if (android.os.Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,
                this::thfHandleBack);
        }'''

def sha(p:pathlib.Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('root',type=pathlib.Path);ap.add_argument('--manifest-out',type=pathlib.Path,required=True);a=ap.parse_args()
    matches=list(a.root.rglob('MainActivity.java'))
    if len(matches)!=1:raise SystemExit(f'expected exactly one MainActivity.java, found {len(matches)}')
    p=matches[0];text=p.read_text(encoding='utf-8')
    if text.count(LEGACY)!=1:raise SystemExit('known legacy onBackPressed implementation not found exactly once')
    if text.count('super.onCreate(savedInstanceState);')!=1:raise SystemExit('super.onCreate(savedInstanceState) not found exactly once')
    text=text.replace(LEGACY,REPLACEMENT,1)
    text=text.replace('super.onCreate(savedInstanceState);',REGISTER,1)
    p.write_text(text,encoding='utf-8')
    a.manifest_out.parent.mkdir(parents=True,exist_ok=True)
    a.manifest_out.write_text(f'{sha(p)}  {p.relative_to(a.root)}\n',encoding='utf-8')
    print('PREDICTIVE_BACK_MIGRATION=APPLIED')
    print('ANDROID_API36_BACK_GESTURE=CALLBACK_REGISTERED')
    print('LEGACY_PRE33_BACK=KEY_EVENT_FALLBACK')
    print('LINT_BASELINE_OR_SUPPRESSION=NO')
    return 0
if __name__=='__main__':raise SystemExit(main())
