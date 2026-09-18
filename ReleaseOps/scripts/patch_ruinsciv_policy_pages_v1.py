#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil
from pathlib import Path

ROOT=Path.cwd()
OVERLAY=Path(os.environ.get("RUINSCIV_POLICY_OVERLAY",""))

def die(m): raise SystemExit(m)

def main():
    mainp=ROOT/"app"/"main.py"
    if not mainp.is_file(): die("app/main.py missing")
    for name in ("privacy.html","terms.html"):
        src=OVERLAY/"web"/"templates"/name
        if not src.is_file(): die(f"policy overlay missing: {src}")
        (ROOT/"web"/"templates").mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,ROOT/"web"/"templates"/name)

    text=mainp.read_text(encoding="utf-8")
    handlers='''async def ruinsciv_privacy_page(_request:Request):\n    return FileResponse(ROOT/"web/templates/privacy.html",media_type="text/html")\n\n\nasync def ruinsciv_terms_page(_request:Request):\n    return FileResponse(ROOT/"web/templates/terms.html",media_type="text/html")\n\n\n'''
    marker="async def account_delete_page(_request:Request):\n"
    if handlers.strip() not in text:
        if marker not in text: die("account deletion handler marker missing; apply deletion patch first")
        text=text.replace(marker,handlers+marker,1)

    old='Route("/api/account/delete",account_delete,methods=["DELETE","POST"]),Route("/account-delete",account_delete_page,methods=["GET"]),Route("/api/me",me,methods=["GET"]),'
    new='Route("/api/account/delete",account_delete,methods=["DELETE","POST"]),Route("/account-delete",account_delete_page,methods=["GET"]),Route("/privacy",ruinsciv_privacy_page,methods=["GET"]),Route("/terms",ruinsciv_terms_page,methods=["GET"]),Route("/api/me",me,methods=["GET"]),'
    if new not in text:
        if old not in text: die("policy route marker missing")
        text=text.replace(old,new,1)
    mainp.write_text(text,encoding="utf-8")

    idx=ROOT/"web"/"templates"/"index.html"
    if idx.is_file():
        it=idx.read_text(encoding="utf-8")
        footer='<div id="ruinscivLegalLinks" style="padding:12px;text-align:center;font-size:.9rem"><a href="/privacy">Privacy</a> · <a href="/terms">Terms</a> · <a href="/account-delete">Delete account</a></div>'
        if footer not in it:
            if "</body>" not in it: die("index body marker missing")
            it=it.replace("</body>",footer+"\n</body>",1)
            idx.write_text(it,encoding="utf-8")

    report={"status":"PASS","feature":"ruinsciv_policy_pages_v1","routes":["/privacy","/terms","/account-delete"],"production_legal_review_required":True}
    (ROOT/"RUINSCIV_POLICY_PAGES_V1_PATCH_RESULT.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
