#!/usr/bin/env python3
from __future__ import annotations
import hashlib, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

EXPECTED_INPUT_SHA = "2b027ea4bfdbdbf29f3b3cb72201912b798aaf7c078415b738e9379c3515edd8"
ROOT_NAME = "THF_NEXUS_6_FINAL"

def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, got {text.count(old)}")
    return text.replace(old,new,1)

def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: builder.py INPUT.zip OUTPUT.zip")
    src=Path(sys.argv[1]).resolve(); out=Path(sys.argv[2]).resolve()
    if not src.is_file(): raise SystemExit("input candidate missing")
    got=sha256(src); print(f"INPUT_SHA256={got}")
    if got != EXPECTED_INPUT_SHA: raise SystemExit("input SHA mismatch")
    if out.exists(): raise SystemExit("refusing to overwrite existing output")
    with tempfile.TemporaryDirectory(prefix="thf-account-client-v1-") as td:
        t=Path(td)
        with zipfile.ZipFile(src) as z: z.extractall(t)
        root=t/ROOT_NAME
        if not root.is_dir(): raise SystemExit("candidate root missing")
        if any("wave-mawja" in str(p).lower() or "wave_mawja" in str(p).lower() for p in root.rglob('*')):
            raise SystemExit("THF/WAVE isolation failure")
        web=root/'clients'/'web'; index=web/'index.html'; appjs=web/'app.js'; apppy=root/'src'/'thf'/'app.py'
        html=index.read_text(encoding='utf-8'); js=appjs.read_text(encoding='utf-8'); py=apppy.read_text(encoding='utf-8')
        account_section='''\n<section id="account" class="view"><div class="page-head"><h2>ACCOUNT & PRIVACY</h2><p>إدارة الحساب والبيانات المرتبطة به.</p></div><div class="card"><h3>حذف الحساب نهائيًا</h3><p>سيتم حذف الحساب وإبطال جميع جلساته. بعض السجلات قد تُحذف أو تُفصل عن الهوية حسب علاقات قاعدة البيانات وسياسة الاحتفاظ القانونية المنشورة.</p><label>للتأكيد اكتب DELETE ACCOUNT<input id="deleteAccountConfirm" autocomplete="off" placeholder="DELETE ACCOUNT"></label><button id="deleteAccountBtn">حذف الحساب</button><div id="deleteAccountOut" class="result"></div><p><a href="/account-deletion">تعليمات حذف الحساب</a></p></div></section>\n'''
        html=replace_once(html,'</main>',account_section+'</main>','index account section')
        html=replace_once(html,'<button data-open="services">⌘<span>SERVICES</span></button>','<button data-open="services">⌘<span>SERVICES</span></button><button data-open="account">⚙<span>ACCOUNT</span></button>','account nav')
        html=replace_once(html,'<footer class="site-footer"><span>THF Nexus User Experience</span><a href="/admin.html" rel="nofollow">Staff Console</a></footer>','<footer class="site-footer"><span>THF Nexus User Experience</span><a href="/account-deletion">Account deletion</a><a href="/admin.html" rel="nofollow">Staff Console</a></footer>','footer deletion link')
        js_insert='''\n// Account deletion ------------------------------------------------------------\n$('#deleteAccountBtn').addEventListener('click',async()=>{\n  try{\n    needAuth();\n    if($('#deleteAccountConfirm').value.trim()!=='DELETE ACCOUNT')throw new Error('اكتب DELETE ACCOUNT للتأكيد');\n    const d=await api('/api/account',{method:'DELETE'});\n    state.token='';state.user=null;\n    $('#accountName').textContent='زائر';$('#authToggle').textContent='تسجيل / دخول';$('#deleteAccountConfirm').value='';\n    out('#deleteAccountOut',{deleted:true,result:d});\n    openView('auth');\n  }catch(e){out('#deleteAccountOut',e.message)}\n});\n'''
        js=replace_once(js,'// Services -------------------------------------------------------------------',js_insert+'\n// Services -------------------------------------------------------------------','account js')
        static_old="web=(self.runtime.root/'clients'/'web').resolve();target=web/'index.html' if path in {'','/'} else (web/path.lstrip('/')).resolve()"
        static_new="web=(self.runtime.root/'clients'/'web').resolve();target=(web/'account-deletion.html') if path=='/account-deletion' else (web/'index.html' if path in {'','/'} else (web/path.lstrip('/')).resolve())"
        py=replace_once(py,static_old,static_new,'static route')
        deletion='''<!doctype html>\n<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>حذف حساب THF Nexus</title><link rel="stylesheet" href="/styles.css"></head><body><main><section class="card"><h1>حذف حساب THF Nexus</h1><p>يمكن للمستخدم المسجّل حذف حسابه من داخل التطبيق: ACCOUNT → حذف الحساب، ثم كتابة DELETE ACCOUNT للتأكيد.</p><p>عند نجاح الطلب إلى DELETE /api/account يتم حذف الحساب وإبطال الجلسات الحالية. قد تخضع بعض البيانات لسياسة احتفاظ قانونية منشورة قبل الإصدار العام.</p><p><a href="/#account">فتح إدارة الحساب</a></p></section></main></body></html>\n'''
        index.write_text(html,encoding='utf-8'); appjs.write_text(js,encoding='utf-8'); apppy.write_text(py,encoding='utf-8'); (web/'account-deletion.html').write_text(deletion,encoding='utf-8')
        subprocess.run([sys.executable,'-m','py_compile',str(apppy)],check=True)
        node=shutil.which('node')
        if node: subprocess.run([node,'--check',str(appjs)],check=True)
        if "DELETE /api/account" not in deletion or "DELETE ACCOUNT" not in html or "method:'DELETE'" not in js: raise SystemExit('client contract validation failed')
        out.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(root.rglob('*')):
                if p.is_file(): z.write(p,Path(ROOT_NAME)/p.relative_to(root))
    print(f"OUTPUT={out}")
    print(f"OUTPUT_SHA256={sha256(out)}")
    print("THF_WAVE_ISOLATION=PASS")
    print("CANONICAL_SOURCE_MUTATED=FALSE")

if __name__=='__main__': main()
