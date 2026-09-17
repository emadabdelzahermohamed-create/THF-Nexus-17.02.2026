#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

ROOT = Path.cwd()
OVERLAY = Path(os.environ.get("THF_TERRA_SOCIAL_AUTH_OVERLAY", ""))


def die(msg: str):
    raise SystemExit(msg)


def replace_once(path: Path, old: str, new: str, label: str):
    text = path.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        die(f"{label}: insertion marker missing in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def insert_before(path: Path, marker: str, addition: str, label: str):
    text = path.read_text(encoding="utf-8")
    if addition.strip() in text:
        return False
    if marker not in text:
        die(f"{label}: marker missing in {path}")
    path.write_text(text.replace(marker, addition + marker, 1), encoding="utf-8")
    return True


def main() -> int:
    required = [ROOT / "app/main.py", ROOT / "app/db.py", ROOT / "web/templates/index.html", ROOT / "native/world/WorldMain.gd"]
    for p in required:
        if not p.is_file():
            die(f"required Terra source missing: {p}")
    source_module = OVERLAY / "app" / "auth_social.py"
    if not source_module.is_file():
        die(f"social auth overlay missing: {source_module}")
    shutil.copy2(source_module, ROOT / "app" / "auth_social.py")

    changed = ["app/auth_social.py"]

    dbp = ROOT / "app/db.py"
    db_old = """        CREATE TABLE IF NOT EXISTS inventory(\n"""
    db_new = """        CREATE TABLE IF NOT EXISTS social_account_links(\n          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, provider TEXT NOT NULL,\n          subject TEXT NOT NULL, email TEXT NOT NULL DEFAULT '', email_verified INTEGER NOT NULL DEFAULT 0,\n          display_name TEXT NOT NULL DEFAULT '', created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL,\n          UNIQUE(provider,subject), UNIQUE(user_id,provider),\n          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE\n        );\n        CREATE INDEX IF NOT EXISTS idx_social_links_user ON social_account_links(user_id,provider);\n        CREATE TABLE IF NOT EXISTS social_auth_attempts(\n          attempt_id TEXT PRIMARY KEY, provider TEXT NOT NULL, state TEXT UNIQUE NOT NULL,\n          pkce_verifier TEXT NOT NULL, client_kind TEXT NOT NULL DEFAULT 'web', link_user_id INTEGER,\n          status TEXT NOT NULL DEFAULT 'pending', resolved_user_id INTEGER, error TEXT NOT NULL DEFAULT '',\n          created_at INTEGER NOT NULL, expires_at INTEGER NOT NULL, consumed_at INTEGER,\n          FOREIGN KEY(link_user_id) REFERENCES users(id) ON DELETE CASCADE,\n          FOREIGN KEY(resolved_user_id) REFERENCES users(id) ON DELETE CASCADE\n        );\n        CREATE INDEX IF NOT EXISTS idx_social_attempt_state ON social_auth_attempts(provider,state);\n        CREATE TABLE IF NOT EXISTS inventory(\n"""
    if replace_once(dbp, db_old, db_new, "social tables"):
        changed.append("app/db.py")

    db_marker = "\ndef ensure_user_extensions(user_id:int, username:str|None=None):\n"
    db_funcs = r'''

def create_social_auth_attempt(attempt_id:str, provider:str, state:str, pkce_verifier:str, client_kind:str, link_user_id:int|None, ttl_seconds:int=600)->dict:
    now=int(time.time());expires=now+max(120,min(int(ttl_seconds),900))
    with db() as c:
        c.execute("DELETE FROM social_auth_attempts WHERE expires_at<? OR consumed_at IS NOT NULL",(now-60,))
        c.execute("INSERT INTO social_auth_attempts(attempt_id,provider,state,pkce_verifier,client_kind,link_user_id,created_at,expires_at) VALUES(?,?,?,?,?,?,?,?)",
                  (attempt_id,provider,state,pkce_verifier,client_kind,link_user_id,now,expires))
        return dict(c.execute("SELECT * FROM social_auth_attempts WHERE attempt_id=?",(attempt_id,)).fetchone())


def get_social_auth_attempt(attempt_id:str)->dict|None:
    with db() as c:
        r=c.execute("SELECT * FROM social_auth_attempts WHERE attempt_id=?",(attempt_id,)).fetchone()
        return dict(r) if r else None


def get_social_auth_attempt_by_state(provider:str,state:str)->dict|None:
    with db() as c:
        r=c.execute("SELECT * FROM social_auth_attempts WHERE provider=? AND state=?",(provider,state)).fetchone()
        return dict(r) if r else None


def complete_social_auth_attempt(attempt_id:str,user_id:int)->None:
    now=int(time.time())
    with db() as c:
        c.execute("UPDATE social_auth_attempts SET status='complete',resolved_user_id=?,error='' WHERE attempt_id=? AND expires_at>=? AND consumed_at IS NULL",
                  (user_id,attempt_id,now))
        if c.total_changes<1:raise ValueError("oauth_attempt_expired_or_consumed")


def fail_social_auth_attempt(attempt_id:str,error:str)->None:
    with db() as c:
        c.execute("UPDATE social_auth_attempts SET status='error',error=? WHERE attempt_id=? AND consumed_at IS NULL",(str(error)[:120],attempt_id))


def consume_social_auth_attempt(attempt_id:str)->dict|None:
    now=int(time.time())
    with db() as c:
        r=c.execute("SELECT * FROM social_auth_attempts WHERE attempt_id=?",(attempt_id,)).fetchone()
        if not r:return None
        row=dict(r)
        if row['status']!='complete' or row['consumed_at'] is not None or int(row['expires_at'])<now:return row
        c.execute("UPDATE social_auth_attempts SET consumed_at=? WHERE attempt_id=? AND consumed_at IS NULL",(now,attempt_id))
        row['consumed_at']=now
        row['_consumed_now']=True
        return row


def get_social_link(provider:str,subject:str)->dict|None:
    with db() as c:
        r=c.execute("SELECT * FROM social_account_links WHERE provider=? AND subject=?",(provider,subject)).fetchone()
        return dict(r) if r else None


def link_social_account(user_id:int,provider:str,subject:str,email:str='',email_verified:bool=False,display_name:str='')->dict:
    now=int(time.time())
    with db() as c:
        owner=c.execute("SELECT user_id FROM social_account_links WHERE provider=? AND subject=?",(provider,subject)).fetchone()
        if owner and int(owner['user_id'])!=int(user_id):raise ValueError("social_identity_already_linked")
        same_provider=c.execute("SELECT subject FROM social_account_links WHERE user_id=? AND provider=?",(user_id,provider)).fetchone()
        if same_provider and str(same_provider['subject'])!=str(subject):raise ValueError("provider_already_linked")
        c.execute("""INSERT INTO social_account_links(user_id,provider,subject,email,email_verified,display_name,created_at,updated_at)
                     VALUES(?,?,?,?,?,?,?,?)
                     ON CONFLICT(provider,subject) DO UPDATE SET email=excluded.email,email_verified=excluded.email_verified,display_name=excluded.display_name,updated_at=excluded.updated_at""",
                  (user_id,provider,subject,email,1 if email_verified else 0,display_name,now,now))
        r=c.execute("SELECT * FROM social_account_links WHERE provider=? AND subject=?",(provider,subject)).fetchone()
        return dict(r)


def social_links(user_id:int)->list[dict]:
    with db() as c:
        return [dict(r) for r in c.execute("SELECT provider,email,email_verified,display_name,created_at,updated_at FROM social_account_links WHERE user_id=? ORDER BY provider",(user_id,))]
'''
    if insert_before(dbp, db_marker, db_funcs, "social db functions"):
        if "app/db.py" not in changed: changed.append("app/db.py")

    mainp = ROOT / "app/main.py"
    if replace_once(mainp, "import math\n", "import math\nimport os\n", "main os import"):
        changed.append("app/main.py")
    import_marker = "from .game import hub\n"
    social_imports = """from .db import (\n    create_social_auth_attempt, get_social_auth_attempt, get_social_auth_attempt_by_state,\n    complete_social_auth_attempt, fail_social_auth_attempt, consume_social_auth_attempt,\n    get_social_link, link_social_account, social_links,\n)\nfrom .auth_social import enabled_providers, provider_enabled, authorization_url, exchange_identity, OAuthProviderError\n"""
    if insert_before(mainp, import_marker, social_imports, "social imports"):
        if "app/main.py" not in changed: changed.append("app/main.py")

    reg_marker = "async def register(request: Request):\n"
    helpers = r'''
def _provision_starter_user(uid:int)->None:
    add_item(uid,"rod","wood",1);add_item(uid,"furniture","chair_wood",2);add_item(uid,"furniture","table_wood",1);add_item(uid,"furniture","garden_lantern",2);add_item(uid,"consumable","pet_food",2);add_item(uid,"material","wood",4)
    starter=AVATAR_STUDIO.get("starter_outfit",{})
    for category,item in (("top",starter.get("top")),("bottom",starter.get("bottom")),("shoes",starter.get("shoes")),("accessory",starter.get("accessory")),("hand_item",starter.get("hand_item"))):
        if item and item!="none":add_item(uid,category,item,1)


def _public_base(request:Request)->str:
    configured=os.getenv("THF_PUBLIC_BASE_URL","").strip().rstrip("/")
    return configured or str(request.base_url).rstrip("/")


def _unique_social_username(provider:str,identity:dict)->str:
    raw=(str(identity.get("email","")).split("@",1)[0] or str(identity.get("display_name","")).strip() or provider)
    base=re.sub(r"[^A-Za-z0-9_\-]","",raw)[:18]
    if len(base)<3:base=(provider+"user")[:18]
    candidate=base
    for _ in range(40):
        if not get_user_by_name(candidate):return candidate
        candidate=(base[:15]+"_"+secrets.token_hex(2))[:24]
    return (provider+"_"+secrets.token_hex(7))[:24]


async def auth_providers(_request:Request):
    return JSONResponse({"providers":enabled_providers(),"local_password":True,"google_play_games":{"implemented":False,"note":"native Play Games account-linking requires the Android Play Games plugin/client configuration"}})


async def social_auth_start(request:Request):
    body=await json_body(request)
    provider=_string(body,"provider",min_len=2,max_len=32).lower()
    client_kind=_string(body,"client",default="web",max_len=16).lower()
    if client_kind not in {"web","native"}:raise _error(400,"invalid_oauth_client")
    if not provider_enabled(provider):raise _error(503,"provider_not_configured")
    link_user_id=None
    if _bool(body,"link",False):link_user_id=int(require_user(request)["id"])
    attempt_id=secrets.token_urlsafe(32);state=secrets.token_urlsafe(32);verifier=secrets.token_urlsafe(64)
    create_social_auth_attempt(attempt_id,provider,state,verifier,client_kind,link_user_id,600)
    redirect_uri=_public_base(request)+f"/api/auth/oauth/{provider}/callback"
    try:url=authorization_url(provider,state=state,redirect_uri=redirect_uri,verifier=verifier)
    except OAuthProviderError as e:
        fail_social_auth_attempt(attempt_id,str(e));raise _error(503,str(e))
    return JSONResponse({"attempt_id":attempt_id,"provider":provider,"authorization_url":url,"expires_seconds":600})


async def social_auth_callback(request:Request):
    provider=str(request.path_params["provider"]).lower();state=(request.query_params.get("state") or "")[:300];code=(request.query_params.get("code") or "")[:8000]
    attempt=get_social_auth_attempt_by_state(provider,state)
    if not attempt:return HTMLResponse("<h2>Invalid or expired sign-in request</h2>",status_code=400)
    if int(attempt.get("expires_at",0))<int(time.time()):
        fail_social_auth_attempt(attempt["attempt_id"],"oauth_attempt_expired");return HTMLResponse("<h2>Sign-in request expired</h2>",status_code=400)
    if not code:
        fail_social_auth_attempt(attempt["attempt_id"],"oauth_code_missing");return HTMLResponse("<h2>Sign-in cancelled</h2>",status_code=400)
    redirect_uri=_public_base(request)+f"/api/auth/oauth/{provider}/callback"
    try:
        identity=await exchange_identity(provider,code=code,redirect_uri=redirect_uri,verifier=str(attempt["pkce_verifier"]))
        existing=get_social_link(provider,str(identity["subject"]))
        if attempt.get("link_user_id"):
            uid=int(attempt["link_user_id"])
            if existing and int(existing["user_id"])!=uid:raise ValueError("social_identity_already_linked")
        elif existing:
            uid=int(existing["user_id"])
        else:
            username=_unique_social_username(provider,identity)
            uid=create_user(username,hash_password(secrets.token_urlsafe(48)),settings.default_lang)
            _provision_starter_user(uid)
        link_social_account(uid,provider,str(identity["subject"]),str(identity.get("email","")),bool(identity.get("email_verified",False)),str(identity.get("display_name","")))
        complete_social_auth_attempt(str(attempt["attempt_id"]),uid)
    except (OAuthProviderError,ValueError) as e:
        fail_social_auth_attempt(str(attempt["attempt_id"]),str(e));return HTMLResponse("<h2>Sign-in failed</h2><p>You can close this window and return to Terra.</p>",status_code=400)
    return HTMLResponse("<!doctype html><meta charset='utf-8'><title>Terra sign-in</title><body style='font-family:sans-serif;text-align:center;padding:3rem'><h2>✓ Terra sign-in complete</h2><p>يمكنك إغلاق هذه النافذة والعودة إلى اللعبة.</p><script>setTimeout(()=>window.close(),900)</script></body>")


async def social_auth_status(request:Request):
    attempt_id=str(request.path_params["attempt_id"])
    attempt=get_social_auth_attempt(attempt_id)
    if not attempt:raise _error(404,"oauth_attempt_not_found")
    if int(attempt.get("expires_at",0))<int(time.time()):raise _error(410,"oauth_attempt_expired")
    if attempt.get("status")=="error":raise _error(400,str(attempt.get("error") or "oauth_failed"))
    if attempt.get("status")!="complete":return JSONResponse({"status":"pending"},status_code=202)
    consumed=consume_social_auth_attempt(attempt_id)
    if not consumed or not consumed.get("_consumed_now"):raise _error(410,"oauth_attempt_consumed")
    uid=int(consumed["resolved_user_id"]);user=get_user(uid)
    if not user:raise _error(404,"user_not_found")
    return JSONResponse({"status":"complete","token":create_token(uid,user["username"]),"user":_user_payload(user),"next_step":"avatar_setup" if not get_avatar_identity(uid).get("setup_complete") else "world"})


async def account_links_get(request:Request):
    u=require_user(request);return JSONResponse({"links":social_links(int(u["id"])),"providers":enabled_providers()})

'''
    if insert_before(mainp, reg_marker, helpers, "social auth handlers"):
        if "app/main.py" not in changed: changed.append("app/main.py")

    reg_old = '''    add_item(uid,"rod","wood",1);add_item(uid,"furniture","chair_wood",2);add_item(uid,"furniture","table_wood",1);add_item(uid,"furniture","garden_lantern",2);add_item(uid,"consumable","pet_food",2);add_item(uid,"material","wood",4)\n    starter=AVATAR_STUDIO.get("starter_outfit",{})\n    for category,item in (("top",starter.get("top")),("bottom",starter.get("bottom")),("shoes",starter.get("shoes")),("accessory",starter.get("accessory")),("hand_item",starter.get("hand_item"))):\n        if item and item!="none":add_item(uid,category,item,1)\n'''
    reg_new = '    _provision_starter_user(uid)\n'
    text=mainp.read_text(encoding='utf-8')
    if reg_old in text:
        mainp.write_text(text.replace(reg_old,reg_new,1),encoding='utf-8')
        if "app/main.py" not in changed:changed.append("app/main.py")

    route_old = ' Route("/api/auth/register",register,methods=["POST"]),Route("/api/auth/login",login,methods=["POST"]),Route("/api/me",me,methods=["GET"]),'
    route_new = ' Route("/api/auth/register",register,methods=["POST"]),Route("/api/auth/login",login,methods=["POST"]),Route("/api/auth/providers",auth_providers,methods=["GET"]),Route("/api/auth/oauth/start",social_auth_start,methods=["POST"]),Route("/api/auth/oauth/{provider}/callback",social_auth_callback,methods=["GET"]),Route("/api/auth/oauth/status/{attempt_id}",social_auth_status,methods=["GET"]),Route("/api/account/links",account_links_get,methods=["GET"]),Route("/api/me",me,methods=["GET"]),'
    if replace_once(mainp, route_old, route_new, "social routes"):
        if "app/main.py" not in changed: changed.append("app/main.py")

    indexp=ROOT/"web/templates/index.html"
    html_old='      <div class="row"><button id="login" data-i18n="login">دخول</button><button id="register" data-i18n="register">إنشاء حساب</button></div>\n      <div id="authError" class="error"></div>'
    html_new='      <div class="row"><button id="login" data-i18n="login">دخول</button><button id="register" data-i18n="register">إنشاء حساب</button></div>\n      <div id="socialProviders" class="row social-providers" aria-label="Social sign in"></div>\n      <div id="authError" class="error"></div>'
    if replace_once(indexp,html_old,html_new,"web social buttons"):
        changed.append("web/templates/index.html")

    js_snippet = r'''async function loadSocialProviders(){try{const d=await api('/api/auth/providers'),host=$('#socialProviders');if(!host)return;host.innerHTML='';for(const p of d.providers||[]){const b=document.createElement('button');b.type='button';b.textContent=`${p.label}`;b.dataset.socialProvider=p.id;b.onclick=()=>socialAuth(p.id);host.appendChild(b)}}catch(e){console.warn('social providers',e)}}
async function socialAuth(provider){const err=$('#authError');try{err.textContent='';const d=await api('/api/auth/oauth/start',{method:'POST',body:JSON.stringify({provider,client:'web'})});const popup=window.open(d.authorization_url,'terra_oauth','popup,width=520,height=720');for(let i=0;i<180;i++){await new Promise(r=>setTimeout(r,1000));const s=await api('/api/auth/oauth/status/'+encodeURIComponent(d.attempt_id));if(s.status==='pending')continue;if(s.token){token=s.token;localStorage.setItem('thf_token',token);try{popup?.close()}catch{};$('#auth').style.display='none';await ensureAvatarSetupThenBoot();return}}throw new Error('oauth_timeout')}catch(e){err.textContent=e.message}}
setTimeout(loadSocialProviders,0);
'''
    for rel in ("web/static/game2d.js","web/static/game3d.js"):
        p=ROOT/rel;text=p.read_text(encoding='utf-8')
        marker="$('#login').onclick=()=>auth('login');$('#register').onclick=()=>auth('register');\n"
        if js_snippet.strip() not in text:
            if marker not in text:die(f"web auth marker missing in {rel}")
            p.write_text(text.replace(marker,marker+js_snippet,1),encoding='utf-8');changed.append(rel)

    worldp=ROOT/"native/world/WorldMain.gd"
    text=worldp.read_text(encoding='utf-8')
    field_marker='var auth_panel: PanelContainer\n'
    fields='var auth_panel: PanelContainer\nvar auth_box: VBoxContainer\nvar social_auth_attempt_id := ""\n'
    if 'var social_auth_attempt_id' not in text:
        if field_marker not in text:die('native auth field marker missing')
        text=text.replace(field_marker,fields,1)
    text=text.replace('    var auth_box := VBoxContainer.new()\n','    auth_box = VBoxContainer.new()\n',1)
    ready_old='''    api.configure(endpoint, token)\n    if token.is_empty():\n        _show_auth(true)'''
    ready_new='''    api.configure(endpoint, token)\n    _load_social_providers()\n    if token.is_empty():\n        _show_auth(true)'''
    if '_load_social_providers()' not in text:
        if ready_old not in text:die('native ready social marker missing')
        text=text.replace(ready_old,ready_new,1)
    native_marker='func _login_pressed() -> void:\n'
    native_funcs=r'''func _load_social_providers() -> void:
    var result: Dictionary = await api.request_json("/api/auth/providers")
    if not result.get("_ok", false):
        return
    for p in result.get("providers", []):
        if typeof(p) != TYPE_DICTIONARY:
            continue
        var provider := str(p.get("id", ""))
        if provider.is_empty():
            continue
        var button := Button.new()
        button.text = "Continue with " + str(p.get("label", provider.capitalize()))
        button.pressed.connect(_social_auth_pressed.bind(provider))
        auth_box.add_child(button)

func _social_auth_pressed(provider: String) -> void:
    status_label.text = "Opening " + provider + " sign-in…"
    var result: Dictionary = await api.request_json("/api/auth/oauth/start", HTTPClient.METHOD_POST, {"provider": provider, "client": "native"})
    if not result.get("_ok", false):
        status_label.text = "AUTH ERROR · " + str(result.get("detail", "unknown"))
        return
    social_auth_attempt_id = str(result.get("attempt_id", ""))
    var auth_url := str(result.get("authorization_url", ""))
    if social_auth_attempt_id.is_empty() or auth_url.is_empty():
        status_label.text = "AUTH ERROR · invalid_oauth_start"
        return
    OS.shell_open(auth_url)
    _poll_social_auth(social_auth_attempt_id)

func _poll_social_auth(attempt_id: String) -> void:
    for _i in range(180):
        if attempt_id != social_auth_attempt_id:
            return
        await get_tree().create_timer(1.0).timeout
        var result: Dictionary = await api.request_json("/api/auth/oauth/status/" + attempt_id.uri_encode())
        if result.get("status", "") == "pending":
            continue
        if not result.get("_ok", false):
            status_label.text = "AUTH ERROR · " + str(result.get("detail", "unknown"))
            social_auth_attempt_id = ""
            return
        var next_token := str(result.get("token", ""))
        if next_token.is_empty():
            continue
        token = next_token
        api.set_token(token)
        THFSessionStore.save_token(token)
        social_auth_attempt_id = ""
        _show_auth(false)
        await _bootstrap()
        return
    if attempt_id == social_auth_attempt_id:
        social_auth_attempt_id = ""
        status_label.text = "AUTH ERROR · oauth_timeout"

'''
    if 'func _social_auth_pressed(provider: String)' not in text:
        if native_marker not in text:die('native social function marker missing')
        text=text.replace(native_marker,native_funcs+native_marker,1)
    worldp.write_text(text,encoding='utf-8');changed.append('native/world/WorldMain.gd')

    report={"status":"PASS","feature":"terra_social_auth_v1","providers":["google","discord","facebook"],"google_play_games":"NOT_YET_IMPLEMENTED_NATIVE_LINK","changed":sorted(set(changed)),"secrets_in_source":False}
    (ROOT/"TERRA_SOCIAL_AUTH_V1_PATCH_RESULT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
