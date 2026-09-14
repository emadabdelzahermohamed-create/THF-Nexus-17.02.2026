import importlib.util
import sqlite3
import sys
from dataclasses import replace
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[1]
for name in ("notification_lifecycle","notification_http_contract","notification_provider_contract","notification_dispatch","pass_notification_bridge"):
    spec=importlib.util.spec_from_file_location(name,ROOT/f"{name}.py"); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod)
life=sys.modules["notification_lifecycle"]; http=sys.modules["notification_http_contract"]; provider=sys.modules["notification_provider_contract"]; dispatch=sys.modules["notification_dispatch"]; bridge_mod=sys.modules["pass_notification_bridge"]

class Vault:
    def __init__(self): self.data={}
    def put(self,k,v): self.data[k]=v
    def get(self,k): return self.data.get(k)
    def delete(self,k): self.data.pop(k,None)
class Authority:
    def __init__(self,sessions): self.sessions={x.session_id:x for x in sessions}
    def resolve(self,sid): return self.sessions.get(sid)
    def revoke_session(self,sid): self.sessions[sid]=replace(self.sessions[sid],revoked=True)
class Adapter:
    provider_name="test"
    def __init__(self): self.calls=[]
    def validate_configuration(self): return True
    def send(self,*,provider_token,request): self.calls.append((provider_token,request.token_id)); return provider.DeliveryResult(True,"msg-1")

def setup(now=1000.0, package="com.topherofit.thf.pulse"):
    vault=Vault(); registry=life.NotificationTokenRegistry(sqlite3.connect(":memory:"),vault)
    sessions=[bridge_mod.LiveSession("u1","s1",package,now+60,False),bridge_mod.LiveSession("u1","s2",package,now+60,False)]
    authority=Authority(sessions); adapter=Adapter(); h=http.NotificationHttpContract(registry); d=dispatch.NotificationDispatcher(registry,{"test":adapter})
    b=bridge_mod.PassNotificationBridge(authority=authority,http_contract=h,dispatcher=d,clock=lambda:now)
    p1=http.SessionPrincipal("u1","s1",package,True,None,False); p2=http.SessionPrincipal("u1","s2",package,True,None,False)
    return b,authority,registry,vault,adapter,p1,p2

def body(token, package="com.topherofit.thf.pulse"): return {"package":package,"provider":"test","provider_token":token}

def test_live_authority_rejects_stale_session_before_mutation_or_dispatch():
    b,a,r,v,adapter,p1,p2=setup(); created=b.register(principal=p1,body=body("provider-token-s1")); tid=created.body["token_id"]
    a.revoke_session("s1")
    with pytest.raises(PermissionError): b.rotate(principal=p1,body={**body("provider-token-new"),"old_token_id":tid})
    req=provider.DeliveryRequest(tid,"title.key","body.key","en","thf://pulse/home",False)
    with pytest.raises(PermissionError): b.dispatch(principal=p1,request=req)
    assert r.get(tid,subject="u1",session_id="s1").active and adapter.calls==[]

def test_parallel_sessions_cannot_mutate_or_dispatch_each_others_registration():
    b,a,r,v,adapter,p1,p2=setup(); one=b.register(principal=p1,body=body("provider-token-s1")); two=b.register(principal=p2,body=body("provider-token-s2"))
    t1=one.body["token_id"]; t2=two.body["token_id"]
    with pytest.raises(PermissionError): b.revoke(principal=p2,body={"token_id":t1})
    with pytest.raises(PermissionError): b.rotate(principal=p2,body={**body("provider-token-new"),"old_token_id":t1})
    req=provider.DeliveryRequest(t1,"title.key","body.key","en","thf://pulse/home",False)
    with pytest.raises(PermissionError): b.dispatch(principal=p2,request=req)
    assert r.get(t1,subject="u1",session_id="s1").active and r.get(t2,subject="u1",session_id="s2").active

def test_logout_revokes_only_current_pass_session_and_notification_registration():
    b,a,r,v,adapter,p1,p2=setup(); one=b.register(principal=p1,body=body("provider-token-s1")); two=b.register(principal=p2,body=body("provider-token-s2"))
    out=b.logout(principal=p1)
    assert out.body=={"session_revoked":True,"notification_tokens_revoked":1}
    assert a.resolve("s1").revoked is True and a.resolve("s2").revoked is False
    assert not r.get(one.body["token_id"],subject="u1",session_id="s1").active
    assert r.get(two.body["token_id"],subject="u1",session_id="s2").active
    req=provider.DeliveryRequest(two.body["token_id"],"title.key","body.key","en","thf://pulse/home",False)
    assert b.dispatch(principal=p2,request=req).accepted

def test_logout_remains_fail_secure_when_notification_cleanup_fails():
    b,a,r,v,adapter,p1,p2=setup(); b.register(principal=p1,body=body("provider-token-s1"))
    original=r.revoke_logout
    def fail(**kwargs): raise RuntimeError("simulated registry failure")
    r.revoke_logout=fail
    with pytest.raises(RuntimeError): b.logout(principal=p1)
    assert a.resolve("s1").revoked is True
    r.revoke_logout=original

def test_expired_subject_and_audience_mismatch_fail_closed():
    b,a,r,v,adapter,p1,p2=setup()
    a.sessions["s1"]=replace(a.sessions["s1"],expires_at=999.0)
    with pytest.raises(PermissionError): b.register(principal=p1,body=body("provider-token-s1"))
    a.sessions["s1"]=replace(a.sessions["s1"],expires_at=1060.0,subject="other")
    with pytest.raises(PermissionError): b.register(principal=p1,body=body("provider-token-s1"))
    a.sessions["s1"]=replace(a.sessions["s1"],subject="u1",package_id="com.topherofit.thf.forge")
    with pytest.raises(PermissionError): b.register(principal=p1,body=body("provider-token-s1"))
