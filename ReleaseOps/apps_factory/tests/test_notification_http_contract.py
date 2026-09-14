import importlib.util
import sqlite3
import sys
import time
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[1]
for name in ("notification_lifecycle", "notification_http_contract"):
    spec=importlib.util.spec_from_file_location(name,ROOT/f"{name}.py"); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod)
life=sys.modules["notification_lifecycle"]; http=sys.modules["notification_http_contract"]
class Vault:
    def __init__(self): self.data={}
    def put(self,k,v): self.data[k]=v
    def get(self,k): return self.data[k]
    def delete(self,k): self.data.pop(k,None)
def contract():
    v=Vault(); r=life.NotificationTokenRegistry(sqlite3.connect(":memory:"),v); return http.NotificationHttpContract(r),r,v
def principal(subject="u1", package="com.topherofit.thf.pulse", session_id="s1", authenticated=True, session_expires_at=None, revoked=False):
    return http.SessionPrincipal(subject,session_id,package,authenticated,session_expires_at,revoked)

def test_register_is_bound_to_authenticated_pass_session_and_hides_raw_token():
    c,r,v=contract(); body={"package":"com.topherofit.thf.pulse","provider":"fcm","provider_token":"provider-token-123456"}
    out=c.register(principal=principal(),body=body)
    assert out.status==201 and "provider_token" not in out.body
    reg=r.get(out.body["token_id"],subject="u1",session_id="s1")
    assert reg.session_id=="s1" and list(v.data.values())==["provider-token-123456"]

def test_second_session_cannot_rotate_or_revoke_first_session_token():
    c,r,_=contract(); p="com.topherofit.thf.pulse"; first=c.register(principal=principal(session_id="s1"),body={"package":p,"provider":"fcm","provider_token":"token-session-one"})
    tid=first.body["token_id"]
    with pytest.raises(PermissionError): c.rotate(principal=principal(session_id="s2"),body={"package":p,"provider":"fcm","old_token_id":tid,"provider_token":"token-session-two"})
    with pytest.raises(PermissionError): c.revoke(principal=principal(session_id="s2"),body={"token_id":tid})
    assert r.get(tid,subject="u1",session_id="s1").active

def test_logout_revokes_only_current_session_registration():
    c,r,_=contract(); p="com.topherofit.thf.codex"
    a=c.register(principal=principal(package=p,session_id="phone-a"),body={"package":p,"provider":"fcm","provider_token":"token-phone-a-123"})
    b=c.register(principal=principal(package=p,session_id="phone-b"),body={"package":p,"provider":"fcm","provider_token":"token-phone-b-123"})
    out=c.logout(principal=principal(package=p,session_id="phone-a"),body={"package":p})
    assert out.body["revoked"]==1
    assert not r.get(a.body["token_id"],subject="u1",session_id="phone-a").active
    assert r.get(b.body["token_id"],subject="u1",session_id="phone-b").active

def test_expired_revoked_and_cross_app_sessions_fail_closed():
    c,r,v=contract(); body={"package":"com.topherofit.thf.pulse","provider":"fcm","provider_token":"provider-token-123456"}
    for p in (principal(session_expires_at=time.time()-1),principal(revoked=True),principal(package="com.topherofit.thf.forge")):
        with pytest.raises(PermissionError): c.register(principal=p,body=body)
    assert r.db.execute("SELECT COUNT(*) FROM notification_tokens").fetchone()[0]==0 and v.data=={}

def test_query_credentials_and_missing_fields_fail_closed():
    c,_,_=contract(); body={"package":"com.topherofit.thf.pulse","provider":"fcm","provider_token":"provider-token-123456"}
    for key in ("token","access_token","Authorization","provider-token","secret"):
        with pytest.raises(PermissionError): c.register(principal=principal(),body=body,query={key:"leak"})
    with pytest.raises(ValueError): c.register(principal=principal(),body={"package":body["package"],"provider":"fcm"})
