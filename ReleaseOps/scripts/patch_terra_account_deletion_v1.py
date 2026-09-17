#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

ROOT = Path.cwd()
OVERLAY = Path(os.environ.get("THF_TERRA_ACCOUNT_DELETE_OVERLAY", ""))


def die(message: str) -> None:
    raise SystemExit(message)


def insert_before(path: Path, marker: str, addition: str, label: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if addition.strip() in text:
        return False
    if marker not in text:
        die(f"{label}: marker missing in {path}")
    path.write_text(text.replace(marker, addition + marker, 1), encoding="utf-8")
    return True


def replace_once(path: Path, old: str, new: str, label: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        die(f"{label}: marker missing in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def main() -> int:
    required = [
        ROOT / "app" / "db.py",
        ROOT / "app" / "main.py",
        ROOT / "web" / "static" / "game3d.js",
        ROOT / "native" / "world" / "WorldMain.gd",
    ]
    for path in required:
        if not path.is_file():
            die(f"required Terra source missing: {path}")

    delete_page = OVERLAY / "web" / "templates" / "account_delete.html"
    if not delete_page.is_file():
        die(f"account deletion page overlay missing: {delete_page}")
    (ROOT / "web" / "templates").mkdir(parents=True, exist_ok=True)
    shutil.copy2(delete_page, ROOT / "web" / "templates" / "account_delete.html")
    changed = ["web/templates/account_delete.html"]

    dbp = ROOT / "app" / "db.py"
    db_marker = "\ndef ensure_user_extensions(user_id:int, username:str|None=None):\n"
    db_addition = r'''

def delete_user_account(user_id:int, username:str)->dict:
    """Permanently delete an app account and its account-associated game data.

    Most Terra tables are protected by SQLite ON DELETE CASCADE. Three legacy
    tables predate those constraints, so they are explicitly purged before the
    user row is deleted. Audit rows owned by the deleted username are removed as
    well; global operational/security records that do not identify the user are
    untouched.
    """
    uid=int(user_id)
    with db() as c:
        existing=c.execute("SELECT id,username FROM users WHERE id=?",(uid,)).fetchone()
        if not existing:
            raise ValueError("user_not_found")
        actual_username=str(existing["username"])
        if actual_username!=str(username):
            raise ValueError("account_identity_mismatch")
        legacy_counts={}
        for table in ("card_draws","catches","payments"):
            before=c.execute(f"SELECT COUNT(*) AS n FROM {table} WHERE user_id=?",(uid,)).fetchone()["n"]
            c.execute(f"DELETE FROM {table} WHERE user_id=?",(uid,))
            legacy_counts[table]=int(before)
        c.execute("DELETE FROM audit_log WHERE actor=?",(actual_username,))
        c.execute("DELETE FROM users WHERE id=?",(uid,))
        if c.total_changes < 1:
            raise ValueError("account_delete_failed")
        return {"deleted_user_id":uid,"legacy_rows_deleted":legacy_counts}
'''
    if insert_before(dbp, db_marker, db_addition, "account delete db function"):
        changed.append("app/db.py")

    mainp = ROOT / "app" / "main.py"
    social_import_old = "    get_social_link, link_social_account, social_links,\n)\n"
    social_import_new = "    get_social_link, link_social_account, social_links, delete_user_account,\n)\n"
    if replace_once(mainp, social_import_old, social_import_new, "account delete db import"):
        changed.append("app/main.py")

    me_marker = "async def me(request:Request):return JSONResponse(_user_payload(require_user(request)))\n"
    handlers = r'''
async def account_delete_page(_request:Request):
    return FileResponse(ROOT/"web/templates/account_delete.html",media_type="text/html")


async def account_delete(request:Request):
    u=require_user(request);body=await json_body(request);expected=f"DELETE {u['username']}";confirm=str(body.get("confirm", ""))
    if not hmac.compare_digest(confirm,expected):
        raise _error(400,"account_delete_confirmation_required")
    try:
        result=delete_user_account(int(u["id"]),str(u["username"]))
    except ValueError as e:
        raise _error(400,str(e))
    return JSONResponse({"ok":True,"account_deleted":True,"user_id":result["deleted_user_id"]})


'''
    if insert_before(mainp, me_marker, handlers, "account delete handlers"):
        if "app/main.py" not in changed:
            changed.append("app/main.py")

    route_old = 'Route("/api/account/links",account_links_get,methods=["GET"]),Route("/api/me",me,methods=["GET"]),'
    route_new = 'Route("/api/account/links",account_links_get,methods=["GET"]),Route("/api/account/delete",account_delete,methods=["DELETE","POST"]),Route("/account-delete",account_delete_page,methods=["GET"]),Route("/api/me",me,methods=["GET"]),'
    if replace_once(mainp, route_old, route_new, "account delete routes"):
        if "app/main.py" not in changed:
            changed.append("app/main.py")

    for rel in ("web/static/game3d.js", "web/static/game2d.js"):
        p = ROOT / rel
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        if rel.endswith("game3d.js"):
            old = "<button id=\"saveProfile\">${tr('save','Save')}</button></div>"
            new = "<button id=\"saveProfile\">${tr('save','Save')}</button><button id=\"deleteAccount\" class=\"danger\">Delete account / حذف الحساب</button></div>"
            if new not in text:
                if old not in text:
                    die("web 3d profile deletion marker missing")
                text = text.replace(old, new, 1)
            hook = "$('#deleteAccount').onclick=()=>{window.location.href='/account-delete'};"
            save_hook = "$('#saveProfile').onclick=async()=>{"
            if hook not in text:
                idx = text.find(save_hook)
                if idx < 0:
                    die("web 3d save profile hook missing")
                end = text.find("}catch(e){toast(e.message)}}", idx)
                if end < 0:
                    die("web 3d profile handler end missing")
                end += len("}catch(e){toast(e.message)}}")
                text = text[:end] + ";" + hook + text[end:]
            p.write_text(text, encoding="utf-8")
            changed.append(rel)
        else:
            # game2d has the same account backend but may expose different panels;
            # make the external deletion resource discoverable without restructuring UI.
            if "window.THF_ACCOUNT_DELETE_URL" not in text:
                text = "window.THF_ACCOUNT_DELETE_URL='/account-delete';\n" + text
                p.write_text(text, encoding="utf-8")
                changed.append(rel)

    worldp = ROOT / "native" / "world" / "WorldMain.gd"
    text = worldp.read_text(encoding="utf-8")
    native_marker = '''    var close_button := Button.new()\n    close_button.text = "Done / تم"\n'''
    native_add = '''    var delete_account_button := Button.new()\n    delete_account_button.text = "Delete Account / حذف الحساب"\n    delete_account_button.pressed.connect(_open_account_delete_page)\n    box.add_child(delete_account_button)\n\n    var close_button := Button.new()\n    close_button.text = "Done / تم"\n'''
    if native_add not in text:
        if native_marker not in text:
            die("native settings deletion marker missing")
        text = text.replace(native_marker, native_add, 1)
    func_marker = "func _toggle_settings_panel() -> void:\n"
    func_add = '''func _open_account_delete_page() -> void:\n    var base := endpoint.trim_suffix("/")\n    OS.shell_open(base + "/account-delete")\n\n'''
    if func_add.strip() not in text:
        if func_marker not in text:
            die("native account delete function marker missing")
        text = text.replace(func_marker, func_add + func_marker, 1)
    worldp.write_text(text, encoding="utf-8")
    changed.append("native/world/WorldMain.gd")

    report = {
        "status":"PASS",
        "feature":"terra_account_deletion_v1",
        "api":"/api/account/delete",
        "external_web_resource":"/account-delete",
        "android_in_app_path":"settings -> external account deletion resource",
        "data_model":"users row cascade + explicit purge of pre-FK legacy tables + username audit rows",
        "changed":sorted(set(changed)),
    }
    (ROOT / "TERRA_ACCOUNT_DELETION_V1_PATCH_RESULT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
