#!/usr/bin/env python3
"""Candidate-only API36 compatibility migration for legacy THF MainActivity.

Fails closed unless the known legacy onBackPressed implementation and exactly one
onCreate method are present. The callback is injected immediately after the method
opens, independent of the local Bundle variable name. The disposable candidate
manifest is also made Play-compatible when CAMERA permission is present by declaring
camera hardware optional. Canonical archives stay untouched.
"""
from __future__ import annotations
import argparse, pathlib, hashlib, re, xml.etree.ElementTree as ET

ANDROID_NS='http://schemas.android.com/apk/res/android'
ET.register_namespace('android', ANDROID_NS)
LEGACY='@Override public void onBackPressed() { if (webView!=null && webView.canGoBack()) webView.goBack(); else super.onBackPressed(); }'
REPLACEMENT='''private void thfHandleBack() { if (webView!=null && webView.canGoBack()) webView.goBack(); else finish(); }
    @Override public boolean onKeyDown(int keyCode, android.view.KeyEvent event) {
        if (keyCode == android.view.KeyEvent.KEYCODE_BACK && android.os.Build.VERSION.SDK_INT < 33) { thfHandleBack(); return true; }
        return super.onKeyDown(keyCode, event);
    }'''
REGISTER='''
        if (android.os.Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,
                this::thfHandleBack);
        }'''
ONCREATE=re.compile(r'((?:@Override\s*)?(?:public|protected)\s+void\s+onCreate\s*\([^)]*\)\s*\{)',re.M)

def sha(p:pathlib.Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def patch_manifest(root:pathlib.Path)->pathlib.Path:
    manifest=root/'app/src/main/AndroidManifest.xml'
    if not manifest.is_file():raise SystemExit('AndroidManifest.xml missing')
    tree=ET.parse(manifest); manifest_root=tree.getroot(); app=manifest_root.find('application')
    if app is None:raise SystemExit('application element missing')
    app.set(f'{{{ANDROID_NS}}}enableOnBackInvokedCallback','true')
    name=f'{{{ANDROID_NS}}}name'; required=f'{{{ANDROID_NS}}}required'
    camera_permission=any(e.attrib.get(name)=='android.permission.CAMERA' for e in manifest_root.findall('uses-permission'))
    if camera_permission:
        features=[e for e in manifest_root.findall('uses-feature') if e.attrib.get(name)=='android.hardware.camera']
        if not features:
            e=ET.Element('uses-feature'); e.set(name,'android.hardware.camera'); e.set(required,'false'); manifest_root.insert(0,e)
        else:
            for e in features:e.set(required,'false')
    tree.write(manifest,encoding='utf-8',xml_declaration=True)
    check=ET.parse(manifest).getroot()
    check_app=check.find('application')
    if check_app is None or check_app.attrib.get(f'{{{ANDROID_NS}}}enableOnBackInvokedCallback')!='true':raise SystemExit('predictive-back manifest flag missing after write')
    if camera_permission:
        camera=[e for e in check.findall('uses-feature') if e.attrib.get(name)=='android.hardware.camera']
        if not camera or any(e.attrib.get(required)!='false' for e in camera):raise SystemExit('camera hardware optional contract failed')
    return manifest

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('root',type=pathlib.Path);ap.add_argument('--manifest-out',type=pathlib.Path,required=True);a=ap.parse_args()
    matches=list(a.root.rglob('MainActivity.java'))
    if len(matches)!=1:raise SystemExit(f'expected exactly one MainActivity.java, found {len(matches)}')
    p=matches[0];text=p.read_text(encoding='utf-8')
    if text.count(LEGACY)!=1:raise SystemExit('known legacy onBackPressed implementation not found exactly once')
    found=list(ONCREATE.finditer(text))
    if len(found)!=1:raise SystemExit(f'expected exactly one onCreate method, found {len(found)}')
    text=text.replace(LEGACY,REPLACEMENT,1)
    text,n=ONCREATE.subn(lambda m:m.group(1)+REGISTER,text,count=1)
    if n!=1:raise SystemExit('onCreate callback injection failed')
    if 'super.onBackPressed()' in text:raise SystemExit('legacy super.onBackPressed remains after migration')
    p.write_text(text,encoding='utf-8')
    manifest=patch_manifest(a.root)
    a.manifest_out.parent.mkdir(parents=True,exist_ok=True)
    a.manifest_out.write_text(f'{sha(p)}  {p.relative_to(a.root)}\n{sha(manifest)}  {manifest.relative_to(a.root)}\n',encoding='utf-8')
    print('PREDICTIVE_BACK_MIGRATION=APPLIED')
    print('ANDROID_API36_BACK_GESTURE=CALLBACK_REGISTERED')
    print('MANIFEST_ENABLE_ON_BACK_INVOKED_CALLBACK=TRUE')
    print('CAMERA_HARDWARE_OPTIONAL_IF_PERMISSION_PRESENT=PASS')
    print('LEGACY_PRE33_BACK=KEY_EVENT_FALLBACK')
    print('LINT_BASELINE_OR_SUPPRESSION=NO')
    return 0
if __name__=='__main__':raise SystemExit(main())
