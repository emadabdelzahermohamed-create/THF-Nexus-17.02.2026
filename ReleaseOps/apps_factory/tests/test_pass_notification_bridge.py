import importlib.util
import sqlite3
import sys
from dataclasses import replace
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[1]
for name in ("notification_lifecycle","notification_http_contract","notification_provider_contract","notification_dispatch","pass_notification_bridge"):
    p=ROOT/f"{name}.py"
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)

life=sys.modules["notification_lifecycle"]
http=sys.modules["notification_http_contract"]
provider=sys.modules["notification_provider_contract"]
dispatch=sys.modules["notification_dispatch"]
bridge_mod=sys.modules["pass_notification_bridge"]

class Vault:
    def __init__(self): self.data={}
    def put(self,k,v): self.data[k]=v
    def get(self,k): return self.data.get(k)
    def delete(self,k): self.data.pop(k,None)

class Authority:
    def __init__(self, sessions): self.sessions={x.session_id:x for x in sessions}
    def resolve(self, sid): return self.sessions.get(sid)
    def revoke_session(self, sid):
        s=self.sessions[sid]
        self.sessions[sid]=replace(s,revoked=True)

class Adapter:
    provider_name="test"
    def __init__(self): self.calls=[]
    def validate_configuration(self): return True
    def send(self,*,provider_token,request):
        self.calls.append((provider_token,request.token_id))
        return provider.DeliveryResult(True,"msg-1")

def setup(now=1000.0, package="com.topherofit.thf.pulse"):
    vault=Vault(); registry=life.NotificationTokenRegistry(sqlite3.connect(":memory:"),vault)
    session=bridge_mod.LiveSession("u1","s1",package,now+60,False)
    authority=Authority([session]); adapter=Adapter()
    h=http.NotificationHttpContract(registry)
    d=dispatch.NotificationDispatcher(registry,{"test":adapter})
    b=bridge_mod.PassNotificationBridge(authority=authority,http_contract=h,dispatcher=d,clock=lambda:now)
    # The bridge authority owns the deterministic test clock; keep the already-verified
    # principal structurally valid without coupling this fixture to wall-clock time.
    principal=http.SessionPrincipal("u1","s1",package,True,None,False)
    return b,authority,registry,vault,adapter,principal

def body(package="com.topherofit.thf.pulse", token="provider-token-123456"):
    return {"package":package,"provider":"test","provider_token":token}

def test_live_authority_rejects_stale_locally_valid_principal_after_revoke():
    b,a,r,v,adapter,p=setup()
    created=b.register(principal=p,body=body())
    a.revoke_session("s1")
    with pytest.raises(PermissionError): b.rotate(principal=p,body={**body(token="provider-token-654321"),"old_token_id":created.body["token_id"]})
    with pytest.raises(PermissionError): b.revoke(principal=p,body={"token_id":created.body["token_id"]})
    assert r.get(created.body["token_id"],subject="u1").active is True

def test_live_authority_rejects_expired_unknown_subject_and_audience_mismatch():
    b,a,_,_,_,p=setup()
    a.sessions["s1"]=replace(a.sessions["s1"],expires_at=999.0)
    with pytest.raises(PermissionError): b.register(principal=p,body=body())
    a.sessions["s1"]=replace(a.sessions["s1"],expires_at=1060.0,subject="other")
    with pytest.raises(PermissionError): b.register(principal=p,body=body())
    a.sessions["s1"]=replace(a.sessions["s1"],subject="u1",package_id="com.topherofit.thf.forge")
    with pytest.raises(PermissionError): b.register(principal=p,body=body())
    a.sessions.clear()
    with pytest.raises(PermissionError): b.register(principal=p,body=body())

def test_dispatch_rechecks_live_session_and_package_before_provider_send():
    b,a,r,v,adapter,p=setup()
    created=b.register(principal=p,body=body())
    req=provider.DeliveryRequest(created.body["token_id"],"title.key","body.key","en","thf://pulse/home",False)
    out=b.dispatch(principal=p,request=req)
    assert out.accepted and adapter.calls==[("provider-token-123456",created.body["token_id"])]
    a.revoke_session("s1")
    with pytest.raises(PermissionError): b.dispatch(principal=p,request=req)
    assert len(adapter.calls)==1

def test_dispatch_rejects_registration_from_different_package_even_same_subject():
    b,a,r,v,adapter,p=setup()
    forge=r.register(subject="u1",package="com.topherofit.thf.forge",provider="test",raw_token="forge-provider-token")
    req=provider.DeliveryRequest(forge.token_id,"title.key","body.key","en","https://thf.example/forge",True)
    with pytest.raises(PermissionError): b.dispatch(principal=p,request=req)
    assert adapter.calls==[]

def test_logout_revokes_pass_first_and_package_notification_tokens():
    b,a,r,v,adapter,p=setup()
    created=b.register(principal=p,body=body())
    out=b.logout(principal=p)
    assert out.status==200 and out.body=={"session_revoked":True,"notification_tokens_revoked":1}
    assert a.resolve("s1").revoked is True
    assert r.get(created.body["token_id"],subject="u1").active is False
    assert created.body["token_id"] not in v.data
    with pytest.raises(PermissionError): b.register(principal=p,body=body(token="another-provider-token"))

def test_logout_is_fail_secure_if_notification_cleanup_fails():
    b,a,r,v,adapter,p=setup(); b.register(principal=p,body=body())
    original=r.revoke_logout
    def fail(**kwargs): raise RuntimeError("simulated registry failure")
    r.revoke_logout=fail
    with pytest.raises(RuntimeError): b.logout(principal=p)
    assert a.resolve("s1").revoked is True
    r.revoke_logout=original
